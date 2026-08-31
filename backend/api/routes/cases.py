"""Case-law listing route, powering the sidebar's Case Studies ->
Landmark Judgments sub-item (Ui updates and features.md 2.2 B2).

Only ever lists cases actually indexed in Pinecone (CASE_METADATA) —
never the aspirational PENDING_CASE_METADATA list (see ingestion.md) —
so the sidebar can't expose unfetched content as if it already existed.
"""

from fastapi import APIRouter

from backend.api.routes.sources import _build_source_response
from backend.case_law import CASE_METADATA
from backend.models.source import ArticleGroupResponse, CaseAnalysis, CaseAnalysisListResponse

router = APIRouter()


@router.get("/api/cases", response_model=ArticleGroupResponse)
def list_cases():
	sources = []
	for case_id in CASE_METADATA:
		source = _build_source_response(case_id)
		if source is not None:
			sources.append(source)
	return ArticleGroupResponse(category="landmark_judgments", label="Landmark Judgments", sources=sources)


@router.get("/api/cases/analysis", response_model=CaseAnalysisListResponse)
def list_case_analyses():
	"""Case Analysis sub-item (coming_soon.md #2) -- static, human-written
	summaries, not raw judgment text. Only cases with an `analysis` entry
	are returned, so an ingested-but-not-yet-summarized case is silently
	omitted rather than shown with placeholder/missing text."""
	analyses = [
		CaseAnalysis(case_id=case_id, case_name=meta["case_name"], year=meta.get("year"), analysis=meta["analysis"])
		for case_id, meta in CASE_METADATA.items()
		if meta.get("analysis")
	]
	return CaseAnalysisListResponse(analyses=analyses)
