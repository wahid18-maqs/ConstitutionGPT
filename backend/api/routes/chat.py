"""Chat routes for ConstituteAI."""

import logging
from uuid import uuid4

from fastapi import APIRouter, HTTPException, Request

from backend.models.chat import ChatRequest, ChatResponse, Citation
from backend.services.pinecone_chat import PineconeChatService, append_exchange


router = APIRouter()
logger = logging.getLogger(__name__)
pinecone_chat_service = None


def _citations(response):
	citations = []
	seen = set()
	for hit in response.get("context", []):
		metadata = hit.get("fields", hit.get("metadata", {}))
		article = metadata.get("article")
		source_id = metadata.get("source_id")
		if article:
			source_id = f"article_{article}"
		label = metadata.get("label") or (f"Article {article}" if article else None)
		if source_id and source_id not in seen:
			citations.append(Citation(source_id=str(source_id), label=str(label or source_id)))
			seen.add(source_id)
	return citations


@router.post("/api/chat", response_model=ChatResponse)
def chat(request: Request, payload: ChatRequest):
	global pinecone_chat_service
	try:
		histories = request.app.state.conversation_histories
		history = histories.setdefault(payload.conversation_id, [])
		if pinecone_chat_service is None:
			pinecone_chat_service = PineconeChatService()
		response = pinecone_chat_service.process(payload.message, history)
		answer = response.get("answer")
		if not isinstance(answer, str) or not answer:
			raise RuntimeError("chat service returned no answer")
		append_exchange(history, payload.message, answer)
		logger.info(
			"chat request completed",
			extra={
				"structured": {
					"path": "/api/chat",
					"conversation_id": payload.conversation_id,
					"language": payload.language,
					"status_code": 200,
				}
			},
		)
		return ChatResponse(
			message_id=uuid4(), answer=answer, citations=_citations(response)
		)
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
