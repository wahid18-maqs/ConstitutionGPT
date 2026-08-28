"""Generation node: grounded, language-aware Gemini answer generation."""

from typing import Any, Optional

from langchain_core.messages import AIMessage, HumanMessage

from backend.config import GEMINI_API_KEY, GEMINI_MODEL
from backend.graph.state import GraphState

# Section 6 generation constraints + Section 7.2 (retrieve English, answer in
# the user's language, keep citation labels untranslated).
SYSTEM_PROMPT = (
	"You are ConstituteAI, a constitutional research assistant for the "
	"Indian Constitution. Ground every claim strictly in the retrieved "
	"context below — never fabricate a citation or a case holding. "
	"Distinguish constitutional text from case-law interpretation. If the "
	"context is insufficient to answer, say so explicitly rather than "
	"guessing. Keep article/clause identifiers and case citation labels "
	"(e.g. \"Article 21\", \"Maneka Gandhi v. Union of India\") exactly as "
	"given, never translated, even when answering in another language. "
	"Answer in {language_name}. End your answer with: \"This is a research "
	"aid, not legal advice.\"\n\nRetrieved context:\n{context}"
)

# ISO code -> English name for every Eighth Schedule language in
# backend/models/chat.py's LanguageCode, plus English itself.
LANGUAGE_NAMES = {
	"en": "English", "as": "Assamese", "bn": "Bengali", "brx": "Bodo",
	"doi": "Dogri", "gu": "Gujarati", "hi": "Hindi", "kn": "Kannada",
	"ks": "Kashmiri", "kok": "Konkani", "mai": "Maithili", "ml": "Malayalam",
	"mni": "Manipuri", "mr": "Marathi", "ne": "Nepali", "or": "Odia",
	"pa": "Punjabi", "sa": "Sanskrit", "sat": "Santali", "sd": "Sindhi",
	"ta": "Tamil", "te": "Telugu", "ur": "Urdu",
}

_model = None


def _get_model():
	global _model
	if _model is None:
		if not GEMINI_API_KEY:
			raise ValueError("GEMINI_API_KEY is required")
		from langchain_google_genai import GoogleGenerativeAI

		_model = GoogleGenerativeAI(model=GEMINI_MODEL, google_api_key=GEMINI_API_KEY)
	return _model


def build_prompt(state: GraphState) -> str:
	"""Assemble the full generation prompt for one turn."""
	language_name = LANGUAGE_NAMES.get(state.get("language", "en"), "English")
	system = SYSTEM_PROMPT.format(language_name=language_name, context=state.get("context", ""))
	history = "\n".join(
		f"{getattr(message, 'type', 'message')}: {getattr(message, 'content', message)}"
		for message in state.get("chat_history", [])
	)
	return f"{system}\n\nChat history:\n{history}\n\nQuestion: {state['query']}"


def generate_answer(state: GraphState, model: Optional[Any] = None) -> GraphState:
	"""Call Gemini (or an injected model) to produce the grounded answer."""
	active_model = model or _get_model()
	prompt = build_prompt(state)
	answer = str(active_model.invoke(prompt))
	return {**state, "answer": answer}


def append_exchange(chat_history: list[Any], question: str, answer: str) -> None:
	"""Append a completed exchange to the conversation history."""
	chat_history.append(HumanMessage(content=question))
	chat_history.append(AIMessage(content=answer))
