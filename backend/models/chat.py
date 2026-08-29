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


class AnswerSection(BaseModel):
	heading: str
	body: str
	citations: list[Citation] = Field(default_factory=list)


class KeyClause(BaseModel):
	text: str
	citations: list[Citation] = Field(default_factory=list)


class StructuredAnswer(BaseModel):
	"""Shared shape for the Summary/sections/Key Clauses/Explanation
	breakdown (Section 1.4) — used by both a live ChatResponse and a
	HistoryMessage loaded later, so a conversation renders identically
	either way instead of degrading to flat text once persisted."""

	summary: str = ""
	sections: list[AnswerSection] = Field(default_factory=list)
	key_clauses: list[KeyClause] = Field(default_factory=list)
	explanation: str = ""


class ChatResponse(StructuredAnswer):
	message_id: str
	answer: str
	citations: list[Citation] = Field(default_factory=list)


class HistoryMessage(StructuredAnswer):
	id: str
	role: Literal["user", "assistant"]
	content: str
	created_at: Optional[datetime] = None


class HistoryResponse(BaseModel):
	conversation_id: str
	messages: list[HistoryMessage] = Field(default_factory=list)


class ConversationSummary(BaseModel):
	id: str
	title: Optional[str] = None
	language: str = "en"
	updated_at: Optional[datetime] = None


class ConversationListResponse(BaseModel):
	conversations: list[ConversationSummary] = Field(default_factory=list)


class ShareRequest(BaseModel):
	conversation_id: str = Field(..., min_length=1)


class ShareResponse(BaseModel):
	share_id: str


class SharedConversationResponse(BaseModel):
	conversation_id: str
	messages: list[HistoryMessage] = Field(default_factory=list)
