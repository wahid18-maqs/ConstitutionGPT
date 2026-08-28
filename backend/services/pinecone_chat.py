"""Pinecone-backed chat generation for ConstituteAI."""

from typing import Any, Optional

from langchain_core.messages import AIMessage, HumanMessage

from backend.config import GEMINI_API_KEY, GEMINI_MODEL
from backend.rag.retriever import PineconeRetriever, create_retriever


SYSTEM_PROMPT = (
    "You are a friendly Law AI Bot. You always greet the user well and treat "
    "respectfully. You have knowledge related to Indian Constitution. Give a "
    "clear, complete answer grounded only in the retrieved context. If the "
    "context is insufficient, say so. Answer directly without mentioning your "
    "name.\n\nRetrieved context:\n{context}"
)


class PineconeChatService:
    """Retrieve source records from Pinecone and generate a grounded answer."""

    def __init__(self, retriever: Optional[PineconeRetriever] = None):
        if not GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY is required")
        from langchain_google_genai import GoogleGenerativeAI

        self.retriever = retriever or create_retriever()
        self.model = GoogleGenerativeAI(
            model=GEMINI_MODEL, google_api_key=GEMINI_API_KEY
        )

    def process(self, question: str, chat_history: list[Any]) -> dict:
        """Return generated answer plus the raw Pinecone hits used as context."""
        search_result = self.retriever.retrieve(question)
        hits = hits_from_response(search_result)
        context = "\n\n".join(
            hit.get("fields", {}).get("text", "") for hit in hits
        )
        history = "\n".join(
            f"{getattr(message, 'type', 'message')}: {getattr(message, 'content', message)}"
            for message in chat_history
        )
        prompt = f"{SYSTEM_PROMPT.format(context=context)}\n\nChat history:\n{history}\n\nQuestion: {question}"
        answer = self.model.invoke(prompt)
        return {"answer": str(answer), "context": hits}


def append_exchange(chat_history: list[Any], question: str, answer: str) -> None:
    """Append a completed exchange to the conversation history."""
    chat_history.append(HumanMessage(content=question))
    chat_history.append(AIMessage(content=answer))


def hits_from_response(response: Any) -> list[dict]:
    """Normalize Pinecone SDK and dictionary search responses to hit dictionaries."""
    if isinstance(response, dict):
        return response.get("result", {}).get("hits", response.get("matches", []))
    result = getattr(response, "result", None)
    if isinstance(result, dict):
        return result.get("hits", [])
    return list(getattr(result, "hits", [])) if result is not None else []
