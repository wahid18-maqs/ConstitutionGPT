"""Metadata-aware semantic retrieval for ConstituteAI."""

import re
import time
from typing import Any, Dict, Optional

from backend.config import PINECONE_NAMESPACE, RERANK_ENABLED
from backend.rag.reranker import PineconeReranker
from backend.services.pinecone import PineconeService


ARTICLE_PATTERN = re.compile(
	r"\b(?:article|art\.?)[\s.-]*(\d{1,3}[A-Z]?)\b", re.IGNORECASE
)
CLAUSE_PATTERN = re.compile(r"\bclause\s*\(?\s*([0-9]+|[a-z])\s*\)?", re.IGNORECASE)
def extract_metadata_filter(query: str) -> Dict[str, Dict[str, str]]:
	"""Extract article and clause references present in indexed metadata."""
	metadata_filter: Dict[str, Dict[str, str]] = {}
	article_match = ARTICLE_PATTERN.search(query)
	if article_match:
		metadata_filter["article"] = {"$eq": article_match.group(1).upper()}
	clause_match = CLAUSE_PATTERN.search(query)
	if clause_match:
		metadata_filter["clause"] = {"$eq": clause_match.group(1).lower()}
	return metadata_filter


class PineconeRetriever:
	"""Run metadata-filtered semantic retrieval with Pinecone embeddings."""

	def __init__(
		self,
		pinecone_service: PineconeService,
		top_k: int = 10,
		namespace: str = PINECONE_NAMESPACE,
		candidate_k: int = 25,
		reranker: Optional[PineconeReranker] = None,
		use_reranker: bool = RERANK_ENABLED,
	):
		if top_k <= 0:
			raise ValueError("top_k must be positive")
		if candidate_k < top_k:
			raise ValueError("candidate_k must be at least top_k")
		self.pinecone_service = pinecone_service
		self.top_k = top_k
		self.namespace = namespace
		self.reranker = reranker or (
			PineconeReranker(pinecone_service, candidate_k, top_k)
			if use_reranker
			else None
		)
		self.last_retrieval_latency_ms = 0.0
		self.last_rerank_latency_ms = 0.0

	def retrieve(self, query: str, metadata_filter_override: Optional[dict] = None) -> Any:
		"""Return semantic matches constrained by explicit or derived metadata.

		`metadata_filter_override` lets a caller (e.g. the LangGraph retrieval
		node, which has already combined intent-based and regex-derived
		filters) supply the filter directly instead of having it re-derived
		from the raw query text. `None` preserves the original behavior of
		deriving the filter here via `extract_metadata_filter`. Pass `{}`
		explicitly to force an unfiltered search.
		"""
		if not query.strip():
			raise ValueError("query must not be empty")
		if metadata_filter_override is not None:
			metadata_filter = metadata_filter_override or None
		else:
			metadata_filter = extract_metadata_filter(query) or None
		started = time.perf_counter()
		if self.reranker:
			response = self.reranker.retrieve(
				query, metadata_filter, self.namespace
			)
			self.last_rerank_latency_ms = self.reranker.last_latency_ms
		else:
			response = self.pinecone_service.search_text(
				text=query,
				top_k=self.top_k,
				filter=metadata_filter,
				namespace=self.namespace,
			)
			self.last_rerank_latency_ms = 0.0
		self.last_retrieval_latency_ms = (time.perf_counter() - started) * 1000
		return response


def create_retriever(
	top_k: int = 10,
	namespace: str = PINECONE_NAMESPACE,
	use_reranker: bool = RERANK_ENABLED,
) -> PineconeRetriever:
	"""Build the configured Pinecone integrated-embedding retriever."""
	return PineconeRetriever(
		pinecone_service=PineconeService(),
		top_k=top_k,
		namespace=namespace,
		use_reranker=use_reranker,
	)
