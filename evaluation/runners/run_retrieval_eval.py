"""Benchmark retrieval source coverage using Recall@K and Precision@K.

Runs each question through the actual LangGraph nodes /api/chat uses
(analyze_query -> build_metadata_filter -> retrieve), not the raw
PineconeRetriever directly. Earlier versions of this script called the
retriever alone, which meant a graph-level fix (e.g. the dual-corpus
retrieval in backend/graph/nodes/retrieval.py, see KNOWN_ISSUES.md) had no
way to show up here — the benchmark could report a query as failing long
after it had actually been fixed. Chained through the graph, this reflects
what a live chat request really does: intent classification, the
intent-driven document_type filter, and (for general/history intent) the
dual per-corpus search included.
"""

import argparse
import json
from pathlib import Path
import sys
import time
from typing import Any, Optional

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from backend.config import PINECONE_NAMESPACE, RERANK_ENABLED
from backend.graph.nodes.analyzer import analyze_query
from backend.graph.nodes.metadata import build_metadata_filter
from backend.graph.nodes.retrieval import retrieve
from backend.rag.retriever import PineconeRetriever, create_retriever


PROJECT_ROOT = Path(__file__).resolve().parents[2]
QUESTIONS_PATH = PROJECT_ROOT / "evaluation" / "datasets" / "retrieval_questions.json"
METADATA_PATH = PROJECT_ROOT / "data" / "processed" / "metadata"


class FixtureEmbeddings:
	"""Deterministic embeddings used only by the local benchmark fixture."""

	def embed_query(self, query: str) -> list[float]:
		return [float(len(query))]


class LocalMetadataService:
	"""PineconeService-shaped fixture backed by processed metadata JSONL."""

	def __init__(self):
		self.records = []
		for path in sorted(METADATA_PATH.rglob("*.jsonl")):
			for line in path.read_text(encoding="utf-8").splitlines():
				metadata = json.loads(line)
				article = metadata.get("article")
				case_id = metadata.get("case_id")
				if article:
					self.records.append({
						"id": f"article_{article}:chunk_{metadata['chunk_id']}",
						"metadata": metadata,
					})
				elif case_id:
					self.records.append({
						"id": f"{case_id}:chunk_{metadata['chunk_id']}",
						"metadata": metadata,
					})

	def search_text(self, text: str, top_k: int, filter: Optional[dict], namespace: str, rerank: Optional[dict] = None) -> dict:
		matches = self.records
		if filter:
			for field, condition in filter.items():
				matches = [
					match for match in matches
					if match["metadata"].get(field) == condition.get("$eq")
				]
		return {"matches": matches[:top_k]}


def load_questions() -> list[dict]:
	return json.loads(QUESTIONS_PATH.read_text(encoding="utf-8"))


def source_ids_from_hits(hits: list[dict]) -> set[str]:
	"""Extract source_ids from a graph retrieval node's `retrieved_documents`
	(already-normalized hit dicts), not a raw Pinecone response."""
	result = set()
	for hit in hits or []:
		metadata = hit.get("metadata") or hit.get("fields", {})
		article = metadata.get("article")
		if article:
			result.add(f"article_{article}")
		case_id = metadata.get("case_id")
		if case_id:
			result.add(str(case_id))
	return result


def run_benchmark(retriever: PineconeRetriever, questions: list[dict], top_k: int) -> tuple[float, float, float, float]:
	recall_values = []
	precision_values = []
	latency_values = []
	rerank_latency_values = []
	for item in questions:
		started = time.perf_counter()
		# The same node chain /api/chat runs: classify intent + extract any
		# explicit article/clause reference, layer on the intent-driven
		# document_type filter, then retrieve (dual per-corpus search when
		# there's no document_type constraint at all).
		state = analyze_query({"query": item["question"]})
		state = build_metadata_filter(state)
		state = retrieve(state, retriever=retriever)
		latency_values.append((time.perf_counter() - started) * 1000)
		rerank_latency_values.append(retriever.last_rerank_latency_ms)
		retrieved = source_ids_from_hits(state["retrieved_documents"])
		expected = set(item["expected_source_ids"])
		hits = retrieved & expected
		recall = len(hits) / len(expected) if expected else 1.0
		precision = len(hits) / len(retrieved) if retrieved else 0.0
		recall_values.append(recall)
		precision_values.append(precision)
		print(
			f"{item['id']} Recall@{top_k}={recall:.2%} "
			f"Precision@{top_k}={precision:.2%} "
			f"intent={state.get('intent')} "
			f"expected={sorted(expected)} retrieved={sorted(retrieved)}"
		)
	return (
		sum(recall_values) / len(recall_values),
		sum(precision_values) / len(precision_values),
		sum(latency_values) / len(latency_values),
		sum(rerank_latency_values) / len(rerank_latency_values),
	)


def run_grouped_benchmark(
	retriever: PineconeRetriever, questions: list[dict], top_k: int
) -> None:
	"""Run and report metrics separately for each labeled question group."""
	for category in ("explicit-article", "conceptual", "case-law"):
		group = [item for item in questions if item["category"] == category]
		recall, precision, latency, rerank_latency = run_benchmark(retriever, group, top_k)
		print(f"{category} questions: {len(group)}")
		print(f"{category} Mean Recall@{top_k}: {recall:.2%}")
		print(f"{category} Mean Precision@{top_k}: {precision:.2%}")
		print(f"{category} Mean retrieval latency: {latency:.2f} ms")
		print(f"{category} Mean rerank request latency: {rerank_latency:.2f} ms")


def main() -> None:
	parser = argparse.ArgumentParser(description=__doc__)
	parser.add_argument("--top-k", type=int, default=10)
	parser.add_argument("--live", action="store_true", help="query configured Pinecone instead of the local fixture")
	parser.add_argument("--namespace", default=PINECONE_NAMESPACE)
	parser.add_argument("--no-rerank", action="store_true", help="disable hosted reranking")
	args = parser.parse_args()
	if args.top_k <= 0:
		raise ValueError("--top-k must be positive")

	if args.live:
		retriever = create_retriever(
			top_k=args.top_k,
			namespace=args.namespace,
			use_reranker=RERANK_ENABLED and not args.no_rerank,
		)
		mode = "live Pinecone, through the LangGraph retrieval node"
	else:
		retriever = PineconeRetriever(
			pinecone_service=LocalMetadataService(),
			top_k=args.top_k,
			namespace=args.namespace,
			use_reranker=RERANK_ENABLED and not args.no_rerank,
		)
		mode = "local metadata fixture, through the LangGraph retrieval node"

	questions = load_questions()
	print(f"Mode: {mode}")
	print(f"Questions: {len(questions)}")
	run_grouped_benchmark(retriever, questions, args.top_k)


if __name__ == "__main__":
	main()
