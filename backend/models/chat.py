"""Pydantic models for the ConstituteAI chat contract."""

from datetime import datetime
from typing import Literal, Optional
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


class HistoryMessage(BaseModel):
	id: str
	role: Literal["user", "assistant"]
	content: str
	created_at: Optional[datetime] = None


class HistoryResponse(BaseModel):
	conversation_id: str
	messages: list[HistoryMessage] = Field(default_factory=list)


class ShareRequest(BaseModel):
	conversation_id: str = Field(..., min_length=1)


class ShareResponse(BaseModel):
	share_id: str


class SharedConversationResponse(BaseModel):
	conversation_id: str
	messages: list[HistoryMessage] = Field(default_factory=list)
