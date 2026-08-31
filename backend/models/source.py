"""Source lookup models for ConstituteAI."""

from typing import Optional

from pydantic import BaseModel, Field


class SearchRequest(BaseModel):
	query: str = Field(..., min_length=1)


class SourceResponse(BaseModel):
	source_id: str
	article: Optional[str] = None
	clause: Optional[str] = None
	original_text: str
	document: str
	page: Optional[int] = None
	source_type: str
	related_provisions: list[str] = Field(default_factory=list)
	related_cases: list[str] = Field(default_factory=list)


class ArticleGroupResponse(BaseModel):
	"""Powers the sidebar's Fundamental Rights / Directive Principles
	sub-menus (Ui updates and features.md 2.2 A1) — a curated, named group
	of articles rendered as multiple stacked Source Explorer blocks."""

	category: str
	label: str
	sources: list[SourceResponse] = Field(default_factory=list)


class CaseAnalysis(BaseModel):
	"""One case's static, human-written significance/holding summary
	(coming_soon.md #2, option 1) — distinct from the raw judgment text
	SourceResponse carries, which /api/cases already returns."""

	case_id: str
	case_name: str
	year: Optional[int] = None
	analysis: str


class CaseAnalysisListResponse(BaseModel):
	label: str = "Case Analysis"
	analyses: list[CaseAnalysis] = Field(default_factory=list)
