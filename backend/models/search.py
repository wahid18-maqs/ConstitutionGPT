"""Models for GET /api/search (Ui updates and features.md 2.2 B1's Search
by Topic sub-item) — a ranked results list, not a single generated answer."""

from typing import Optional

from pydantic import BaseModel, Field


class SearchResult(BaseModel):
	source_id: str
	label: str
	snippet: str
	score: Optional[float] = None


class SearchResponse(BaseModel):
	query: str
	results: list[SearchResult] = Field(default_factory=list)
