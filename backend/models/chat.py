"""Pydantic models for the ConstituteAI chat contract."""

from typing import Literal
from pydantic import BaseModel, Field


LanguageCode = Literal[
	"en", "as", "bn", "brx", "doi", "gu", "hi", "kn", "ks", "kok", "mai",
	"ml", "mni", "mr", "ne", "or", "pa", "sa", "sat", "sd", "ta", "te", "ur",
]


class ChatRequest(BaseModel):
	message: str = Field(..., min_length=1)
	language: LanguageCode = "en"
	conversation_id: str = Field(..., min_length=1)


class Citation(BaseModel):
	source_id: str
	label: str


class ChatResponse(BaseModel):
	message_id: str
	answer: str
	citations: list[Citation] = Field(default_factory=list)
