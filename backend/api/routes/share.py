"""Share link routes for ConstituteAI (Section 4)."""

from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException

from backend.api.dependencies import get_current_user
from backend.api.routes.chat import history_message_from_row
from backend.models.chat import ShareRequest, ShareResponse, SharedConversationResponse
from backend.models.user import UserResponse
from backend.services import supabase as supabase_service

router = APIRouter()


@router.post("/api/share", response_model=ShareResponse)
def create_share(
	payload: ShareRequest,
	current_user: UserResponse = Depends(get_current_user),
):
	conversation = supabase_service.get_conversation(payload.conversation_id)
	if conversation is None or conversation["user_id"] != current_user.user_id:
		raise HTTPException(status_code=403, detail="Conversation belongs to another user")
	share_id = uuid4().hex
	supabase_service.create_share(share_id, payload.conversation_id)
	return ShareResponse(share_id=share_id)


@router.get("/api/share/{share_id}", response_model=SharedConversationResponse)
def get_share(share_id: str):
	# Intentionally no auth — a share link's purpose is external/anonymous
	# access. This resolves through the service-role client (bypasses RLS),
	# so the public/private boundary here is enforced by this route not
	# requiring a token, not by the database. See Section 8.3.
	resolved = supabase_service.resolve_share(share_id)
	if resolved is None:
		raise HTTPException(status_code=404, detail="Share link not found")
	return SharedConversationResponse(
		conversation_id=resolved["conversation"]["id"],
		messages=[history_message_from_row(message) for message in resolved["messages"]],
	)
