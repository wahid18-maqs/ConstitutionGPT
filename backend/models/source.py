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
