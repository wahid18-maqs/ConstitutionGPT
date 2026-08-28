"""Metadata builder node: combines intent with the analyzer's regex filter."""

from backend.graph.state import GraphState

# Section 6 routing table: which document_type an intent should search.
# "history"/"general" deliberately search both constitutional text and case
# law, per the spec ("General Query -> text + case-law retrieval").
_DOCUMENT_TYPE_BY_INTENT = {
	"article": "constitution",
	"amendment": "constitution",
	"case_law": "case_law",
}


def build_metadata_filter(state: GraphState) -> GraphState:
	"""Layer an intent-driven document_type constraint onto the base filter."""
	metadata_filter = dict(state.get("metadata_filter") or {})
	intent = state.get("intent", "general")
	document_type = _DOCUMENT_TYPE_BY_INTENT.get(intent)
	if intent == "case_law":
		# article/clause are constitution-only fields; case-law chunks never
		# carry them, so keeping them here would zero out every match.
		metadata_filter.pop("article", None)
		metadata_filter.pop("clause", None)
	if document_type:
		metadata_filter["document_type"] = {"$eq": document_type}
	return {**state, "metadata_filter": metadata_filter or None}
