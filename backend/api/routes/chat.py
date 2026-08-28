"""Chat routes for ConstituteAI."""

import logging
from uuid import uuid4

from fastapi import APIRouter, HTTPException, Request

from backend.graph.workflow import run as run_chat_graph
from backend.models.chat import ChatRequest, ChatResponse, Citation


router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/api/chat", response_model=ChatResponse)
def chat(request: Request, payload: ChatRequest):
	try:
		histories = request.app.state.conversation_histories
		history = histories.setdefault(payload.conversation_id, [])
		result = run_chat_graph(payload.message, payload.language, history)
		answer = result.get("answer")
		if not isinstance(answer, str) or not answer:
			raise RuntimeError("chat service returned no answer")
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
		citations = [Citation(**citation) for citation in result.get("citations", [])]
		return ChatResponse(message_id=str(uuid4()), answer=answer, citations=citations)
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
