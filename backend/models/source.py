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
