"""Chat routes for ConstituteAI."""

import logging
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Request

from backend.api.dependencies import get_current_user
from backend.graph.workflow import run as run_chat_graph
from backend.models.chat import ChatRequest, ChatResponse, Citation, HistoryMessage, HistoryResponse
from backend.models.user import UserResponse
from backend.services import supabase as supabase_service


router = APIRouter()
logger = logging.getLogger(__name__)


def _ensure_conversation_ownership(conversation_id: str, user: UserResponse, language: str) -> None:
	"""Create the conversation on first use, or 403 if it belongs to someone else."""
	conversation = supabase_service.get_conversation(conversation_id)
	if conversation is None:
		supabase_service.create_conversation(conversation_id, user.user_id, language)
		return
	if conversation["user_id"] != user.user_id:
		raise HTTPException(status_code=403, detail="Conversation belongs to another user")


@router.post("/api/chat", response_model=ChatResponse)
def chat(
	request: Request,
	payload: ChatRequest,
	current_user: UserResponse = Depends(get_current_user),
):
	_ensure_conversation_ownership(payload.conversation_id, current_user, payload.language)
	try:
		histories = request.app.state.conversation_histories
		history = histories.setdefault(payload.conversation_id, [])
		result = run_chat_graph(payload.message, payload.language, history)
		answer = result.get("answer")
		if not isinstance(answer, str) or not answer:
			raise RuntimeError("chat service returned no answer")

		supabase_service.insert_message(payload.conversation_id, "user", payload.message)
		assistant_message = supabase_service.insert_message(
			payload.conversation_id, "assistant", answer
		)
		citations = result.get("citations", [])
		if assistant_message.get("id"):
			supabase_service.insert_citations(assistant_message["id"], citations)

		logger.info(
			"chat request completed",
			extra={
				"structured": {
					"path": "/api/chat",
					"conversation_id": payload.conversation_id,
					"language": payload.language,
					"intent": result.get("intent"),
					"status_code": 200,
				}
			},
		)
		return ChatResponse(
			message_id=assistant_message.get("id", str(uuid4())),
			answer=answer,
			citations=[Citation(**citation) for citation in citations],
		)
	except HTTPException:
		raise
	except Exception as exc:
		logger.exception(
			"chat request failed",
			extra={
				"structured": {
					"path": "/api/chat",
					"conversation_id": payload.conversation_id,
					"language": payload.language,
					"status_code": 502,
				}
			},
		)
		raise HTTPException(
			status_code=502, detail="Chat service unavailable"
		) from exc


@router.get("/api/history", response_model=HistoryResponse)
def history(
	conversation_id: str,
	current_user: UserResponse = Depends(get_current_user),
):
	conversation = supabase_service.get_conversation(conversation_id)
	if conversation is None or conversation["user_id"] != current_user.user_id:
		raise HTTPException(status_code=403, detail="Conversation belongs to another user")
	messages = supabase_service.list_messages(conversation_id)
	return HistoryResponse(
		conversation_id=conversation_id,
		messages=[HistoryMessage(**message) for message in messages],
	)
