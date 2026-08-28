"""Feedback routes for ConstituteAI (Section 4)."""

from fastapi import APIRouter, Depends, HTTPException

from backend.api.dependencies import get_current_user
from backend.models.feedback import FeedbackRequest, FeedbackResponse
from backend.models.user import UserResponse
from backend.services import supabase as supabase_service

router = APIRouter()


@router.post("/api/feedback", response_model=FeedbackResponse)
def feedback(
	payload: FeedbackRequest,
	current_user: UserResponse = Depends(get_current_user),
):
	message = supabase_service.get_message(payload.message_id)
	if message is None:
		raise HTTPException(status_code=404, detail="Message not found")
	conversation = supabase_service.get_conversation(message["conversation_id"])
	if conversation is None or conversation["user_id"] != current_user.user_id:
		raise HTTPException(status_code=403, detail="Message belongs to another user")

	supabase_service.insert_feedback(current_user.user_id, payload.message_id, payload.feedback)
	return FeedbackResponse(message_id=payload.message_id, feedback=payload.feedback)
