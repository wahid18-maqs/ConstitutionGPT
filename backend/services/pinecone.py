"""Shared Pinecone client, index, upsert, and query service."""

from typing import Any, Iterable, Optional

from backend.config import (
	PINECONE_API_KEY,
	PINECONE_CLOUD,
	PINECONE_INDEX_NAME,
	PINECONE_REGION,
)


class PineconeService:
	"""Provide one configured Pinecone client for indexing and retrieval."""

	def __init__(
		self,
		api_key: Optional[str] = PINECONE_API_KEY,
		index_name: str = PINECONE_INDEX_NAME,
	):
		if not api_key:
			raise ValueError("PINECONE_API_KEY is required")
		from pinecone import Pinecone

		self.client = Pinecone(api_key=api_key)
		self.index_name = index_name
		self._index = None

	def ensure_index(self, dimension: int) -> Any:
		"""Create the configured serverless index when it does not exist."""
		from pinecone import ServerlessSpec

		if self.index_name not in self.client.list_indexes().names():
			self.client.create_index(
				name=self.index_name,
				dimension=dimension,
				metric="cosine",
				spec=ServerlessSpec(cloud=PINECONE_CLOUD, region=PINECONE_REGION),
			)
		self._index = self.client.Index(self.index_name)
		return self._index

	def index(self) -> Any:
		"""Return the configured index, assuming it already exists."""
		if self._index is None:
			self._index = self.client.Index(self.index_name)
		return self._index

	def upsert(self, vectors: Iterable[dict], namespace: str = "default") -> Any:
		"""Upsert vector dictionaries into the configured namespace."""
		return self.index().upsert(vectors=list(vectors), namespace=namespace)

	def upsert_records(self, records: Iterable[dict], namespace: str = "default") -> Any:
		"""Upsert text records for server-side integrated embedding."""
		return self.index().upsert_records(
			namespace=namespace, records=list(records)
		)

	def search_text(
		self,
		text: str,
		top_k: int = 10,
		filter: Optional[dict] = None,
		namespace: str = "default",
		rerank: Optional[dict] = None,
	) -> Any:
		"""Search an integrated-embedding index using raw query text."""
		query = {"inputs": {"text": text}, "top_k": top_k}
		if filter:
			query["filter"] = filter
		search_kwargs = {"namespace": namespace, "query": query}
		if rerank:
			search_kwargs["rerank"] = rerank
		return self.index().search(**search_kwargs)

	def query(
		self,
		vector: list[float],
		top_k: int = 10,
		filter: Optional[dict] = None,
		namespace: str = "default",
	) -> Any:
		"""Query the configured index for a vector and optional metadata filter."""
		return self.index().query(
			vector=vector,
			top_k=top_k,
			include_metadata=True,
			namespace=namespace,
			filter=filter,
		)
