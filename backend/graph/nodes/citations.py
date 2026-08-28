"""Citation builder node: derives source citations from retrieved hits."""

from backend.graph.state import GraphState


def build_citations(state: GraphState) -> GraphState:
	"""Build the deduplicated citation list from retrieved_documents' metadata."""
	citations = []
	seen = set()
	for hit in state.get("retrieved_documents") or []:
		metadata = hit.get("fields", hit.get("metadata", {}))
		article = metadata.get("article")
		source_id = metadata.get("source_id")
		label = metadata.get("label")
		if metadata.get("document_type") == "case_law":
			source_id = metadata.get("case_id") or source_id
			label = metadata.get("case_name") or label
		elif article:
			source_id = f"article_{article}"
			label = label or f"Article {article}"
		if source_id and source_id not in seen:
			citations.append({"source_id": str(source_id), "label": str(label or source_id)})
			seen.add(source_id)
	return {**state, "citations": citations}
