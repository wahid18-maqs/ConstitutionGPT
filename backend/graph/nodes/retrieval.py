"""Retrieval node: runs Pinecone retrieval with the assembled metadata filter."""

from backend.graph.nodes.citations import citation_for
from backend.graph.state import GraphState
from backend.rag.retriever import PineconeRetriever, create_retriever
from backend.services.pinecone_chat import hits_from_response

_retriever: PineconeRetriever | None = None


def _get_retriever() -> PineconeRetriever:
	global _retriever
	if _retriever is None:
		_retriever = create_retriever()
	return _retriever


def _labeled_passage(hit: dict) -> str:
	"""Tag a retrieved chunk with its source_id so the generation node can
	attribute a claim back to a specific citation instead of guessing."""
	fields = hit.get("fields", {})
	text = fields.get("text", "")
	citation = citation_for(fields)
	source_id = citation["source_id"] if citation else "unknown_source"
	return f"[source_id: {source_id}]\n{text}"


def retrieve(state: GraphState, retriever: PineconeRetriever | None = None) -> GraphState:
	"""Query Pinecone with the graph's assembled filter and set context."""
	active_retriever = retriever or _get_retriever()
	response = active_retriever.retrieve(
		state["query"], metadata_filter_override=state.get("metadata_filter")
	)
	hits = hits_from_response(response)
	context = "\n\n".join(_labeled_passage(hit) for hit in hits)
	return {**state, "retrieved_documents": hits, "context": context}
