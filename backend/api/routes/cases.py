"""Case-law listing route, powering the sidebar's Case Studies ->
Landmark Judgments sub-item (Ui updates and features.md 2.2 B2).

Only ever lists cases actually indexed in Pinecone (CASE_METADATA) —
never the aspirational PENDING_CASE_METADATA list (see ingestion.md) —
so the sidebar can't expose unfetched content as if it already existed.
"""

from fastapi import APIRouter

from backend.api.routes.sources import _build_source_response
from backend.case_law import CASE_METADATA
from backend.models.source import ArticleGroupResponse

router = APIRouter()


@router.get("/api/cases", response_model=ArticleGroupResponse)
def list_cases():
	sources = []
	for case_id in CASE_METADATA:
		source = _build_source_response(case_id)
		if source is not None:
			sources.append(source)
	return ArticleGroupResponse(category="landmark_judgments", label="Landmark Judgments", sources=sources)
