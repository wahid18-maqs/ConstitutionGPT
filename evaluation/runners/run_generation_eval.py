"""Generation-quality eval: runs each question through the real chat
pipeline (backend.graph.workflow.run -- same function /api/chat calls)
and scores the actual answer with DeepEval's FaithfulnessMetric,
HallucinationMetric, and this project's own CitationAccuracyMetric.

Field mapping (approved): state["query"] -> input, state["answer"] ->
actual_output, state["retrieved_documents"] -> retrieval_context/context.

Live by design -- every question makes a real Gemini generation call, a
real Pinecone retrieval call, and real Gemini judge-model calls per
metric. Not a fixture/mocked eval like run_retrieval_eval.py's default
mode.
"""

import argparse
import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

import json  # noqa: E402

from deepeval.metrics import FaithfulnessMetric, HallucinationMetric  # noqa: E402
from deepeval.test_case import LLMTestCase  # noqa: E402

from backend.graph.nodes.citations import citation_for  # noqa: E402
from backend.graph.workflow import run as run_chat_graph  # noqa: E402
from evaluation.metrics.citation_accuracy import CitationAccuracyMetric  # noqa: E402
from evaluation.metrics.gemini_judge import GeminiJudgeModel  # noqa: E402

QUESTIONS_PATH = PROJECT_ROOT / "evaluation" / "datasets" / "generation_questions.json"


def load_questions() -> list[dict]:
	return json.loads(QUESTIONS_PATH.read_text(encoding="utf-8"))


def retrieved_source_ids(retrieved_documents: list[dict]) -> set[str]:
	ids = set()
	for hit in retrieved_documents or []:
		citation = citation_for(hit.get("fields", {}))
		if citation:
			ids.add(citation["source_id"])
	return ids


class _CitationTestCase:
	"""Not a real LLMTestCase -- CitationAccuracyMetric is only ever
	called directly in this runner (never through DeepEval's evaluate()
	batch API), so it doesn't need to satisfy LLMTestCase's schema."""

	def __init__(self, cited_source_ids: list[str], available_source_ids: set[str]):
		self.cited_source_ids = cited_source_ids
		self.available_source_ids = available_source_ids


def run_one(item: dict, judge_model: GeminiJudgeModel) -> dict:
	result = run_chat_graph(item["question"], language="en")
	retrieved_texts = [hit.get("fields", {}).get("text", "") for hit in result["context"]]
	available_ids = retrieved_source_ids(result["context"])
	cited_ids = [c["source_id"] for c in result["citations"]]

	test_case = LLMTestCase(
		input=item["question"],
		actual_output=result["answer"],
		retrieval_context=retrieved_texts,
		context=retrieved_texts,
	)

	faithfulness = FaithfulnessMetric(model=judge_model)
	faithfulness.measure(test_case)

	hallucination = HallucinationMetric(model=judge_model)
	hallucination.measure(test_case)

	citation_accuracy = CitationAccuracyMetric()
	citation_accuracy.measure(_CitationTestCase(cited_ids, available_ids))

	return {
		"id": item["id"],
		"category": item["category"],
		"question": item["question"],
		"answer": result["answer"],
		"cited_source_ids": cited_ids,
		"expected_source_ids": item["expected_source_ids"],
		"faithfulness_score": faithfulness.score,
		"faithfulness_reason": faithfulness.reason,
		"hallucination_score": hallucination.score,
		"hallucination_reason": hallucination.reason,
		"citation_accuracy_score": citation_accuracy.score,
		"citation_accuracy_reason": citation_accuracy.reason,
	}


def main() -> None:
	parser = argparse.ArgumentParser(description=__doc__)
	parser.add_argument("--limit", type=int, default=None, help="only run the first N questions")
	args = parser.parse_args()

	questions = load_questions()
	if args.limit:
		questions = questions[: args.limit]

	judge_model = GeminiJudgeModel()
	results = []
	for index, item in enumerate(questions):
		if index > 0:
			time.sleep(20)  # free-tier Gemini quota is 5 req/min; pace between questions
		print(f"Running {item['id']} ({item['category']}): {item['question']}")
		record = run_one(item, judge_model)
		results.append(record)
		print(
			f"  faithfulness={record['faithfulness_score']:.2f} "
			f"hallucination={record['hallucination_score']:.2f} "
			f"citation_accuracy={record['citation_accuracy_score']:.2f}"
		)

	def mean(key: str) -> float:
		return sum(r[key] for r in results) / len(results)

	print(f"\nQuestions: {len(results)}")
	print(f"Mean Faithfulness: {mean('faithfulness_score'):.2%}")
	print(f"Mean Hallucination (lower is better): {mean('hallucination_score'):.2%}")
	print(f"Mean Citation Accuracy: {mean('citation_accuracy_score'):.2%}")


if __name__ == "__main__":
	main()
