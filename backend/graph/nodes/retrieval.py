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


def _retrieve_hits(retriever: PineconeRetriever, query: str, metadata_filter: dict | None) -> list[dict]:
	return hits_from_response(retriever.retrieve(query, metadata_filter_override=metadata_filter))


def retrieve(state: GraphState, retriever: PineconeRetriever | None = None) -> GraphState:
	"""Query Pinecone with the graph's assembled filter and set context.

	When the filter has no document_type constraint (general/history
	intent — see backend/graph/nodes/metadata.py), a single unconstrained
	search lets one corpus's writing style dominate the other entirely by
	raw similarity score: case-law judgments discuss a topic at length and
	consistently out-score a terse constitutional clause on a conceptual
	question, even when the clause is the actually-authoritative answer
	(confirmed: "What freedom protects... speech" never surfaced Article 19
	at all under a single blended search — see KNOWN_ISSUES.md). Running
	one search per document_type and combining them guarantees both
	corpora get a chance to reach the model's context; the anti-fabrication
	citation resolver in generation.py already ensures the model only ever
	cites what's actually here, so this doesn't risk false citations — it
	just stops one corpus from crowding the other out of context entirely.
	"""
	active_retriever = retriever or _get_retriever()
	query = state["query"]
	base_filter = state.get("metadata_filter") or {}

	if "document_type" in base_filter:
		hits = _retrieve_hits(active_retriever, query, base_filter or None)
	else:
		top_k = active_retriever.top_k
		constitution_hits = _retrieve_hits(
			active_retriever, query, {**base_filter, "document_type": {"$eq": "constitution"}}
		)[: max(1, top_k // 2)]
		case_law_hits = _retrieve_hits(
			active_retriever, query, {**base_filter, "document_type": {"$eq": "case_law"}}
		)[: top_k - len(constitution_hits)]
		# Constitutional text first -- it's the authoritative source; case
		# law is interpretation (matches the system prompt's own framing).
		hits = constitution_hits + case_law_hits

	context = "\n\n".join(_labeled_passage(hit) for hit in hits)
	return {**state, "retrieved_documents": hits, "context": context}
