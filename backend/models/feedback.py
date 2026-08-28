"""Feedback models for ConstituteAI."""

from typing import Literal

from pydantic import BaseModel


class FeedbackRequest(BaseModel):
	message_id: str
	feedback: Literal["positive", "negative"]


class FeedbackResponse(BaseModel):
	message_id: str
	feedback: Literal["positive", "negative"]
