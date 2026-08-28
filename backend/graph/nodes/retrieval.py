"""Retrieval node: runs Pinecone retrieval with the assembled metadata filter."""

from backend.graph.state import GraphState
from backend.rag.retriever import PineconeRetriever, create_retriever
from backend.services.pinecone_chat import hits_from_response

_retriever: PineconeRetriever | None = None


def _get_retriever() -> PineconeRetriever:
	global _retriever
	if _retriever is None:
		_retriever = create_retriever()
	return _retriever


def retrieve(state: GraphState, retriever: PineconeRetriever | None = None) -> GraphState:
	"""Query Pinecone with the graph's assembled filter and set context."""
	active_retriever = retriever or _get_retriever()
	response = active_retriever.retrieve(
		state["query"], metadata_filter_override=state.get("metadata_filter")
	)
	hits = hits_from_response(response)
	context = "\n\n".join(hit.get("fields", {}).get("text", "") for hit in hits)
	return {**state, "retrieved_documents": hits, "context": context}
