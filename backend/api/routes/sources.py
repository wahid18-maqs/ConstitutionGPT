"""Source explorer route for ConstituteAI (Section 4/1.5).

Anonymous access is fine here — Section 8.2 lists read-only reference
lookups as not needing an account.
"""

from fastapi import APIRouter, HTTPException

from backend.config import PINECONE_NAMESPACE
from backend.models.source import SourceResponse
from backend.services.pinecone import PineconeService
from backend.services.pinecone_chat import hits_from_response

router = APIRouter()

_service = None


def _get_service() -> PineconeService:
	global _service
	if _service is None:
		_service = PineconeService()
	return _service


@router.get("/api/source/{source_id}", response_model=SourceResponse)
def get_source(source_id: str):
	if source_id.startswith("article_"):
		article = source_id.removeprefix("article_")
		metadata_filter = {"article": {"$eq": article}, "document_type": {"$eq": "constitution"}}
		query_text = f"Article {article}"
	else:
		metadata_filter = {"case_id": {"$eq": source_id}, "document_type": {"$eq": "case_law"}}
		query_text = source_id.replace("_", " ")

	response = _get_service().search_text(
		text=query_text, top_k=5, filter=metadata_filter, namespace=PINECONE_NAMESPACE
	)
	hits = hits_from_response(response)
	if not hits:
		raise HTTPException(status_code=404, detail="Source not found")

	fields = hits[0].get("fields", {})
	combined_text = "\n\n".join(hit.get("fields", {}).get("text", "") for hit in hits)

	return SourceResponse(
		source_id=source_id,
		article=fields.get("article"),
		clause=fields.get("clause"),
		original_text=combined_text,
		document=fields.get("case_name") or "Constitution of India",
		page=int(fields["page"]) if fields.get("page") is not None else None,
		source_type=fields.get("source_type") or fields.get("category") or "unknown",
		related_provisions=[],
		related_cases=[],
	)
