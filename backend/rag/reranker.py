"""Pinecone-hosted cross-encoder reranking for ConstituteAI."""

import time
from typing import Any, Optional

from backend.services.pinecone import PineconeService


class PineconeReranker:
	"""Retrieve a wide candidate set and rerank it server-side."""

	def __init__(
		self,
		pinecone_service: PineconeService,
		candidate_k: int = 25,
		final_k: int = 10,
		model: str = "bge-reranker-v2-m3",
	):
		if candidate_k < final_k or final_k <= 0:
			raise ValueError("candidate_k must be at least final_k and final_k must be positive")
		self.pinecone_service = pinecone_service
		self.candidate_k = candidate_k
		self.final_k = final_k
		self.model = model
		self.last_latency_ms = 0.0

	def retrieve(
		self, query: str, metadata_filter: Optional[dict], namespace: str
	) -> Any:
		"""Return the final reranked results and record request latency."""
		started = time.perf_counter()
		response = self.pinecone_service.search_text(
			text=query,
			top_k=self.candidate_k,
			filter=metadata_filter,
			namespace=namespace,
			rerank={
				"model": self.model,
				"rank_fields": ["text"],
				"top_n": self.final_k,
			},
		)
		self.last_latency_ms = (time.perf_counter() - started) * 1000
		return response
