"""Server-side Supabase client and Postgres query helpers for ConstituteAI.

Always initialized with the **service role key** — never the anon key.
That means every query here bypasses Row Level Security entirely; ownership
enforcement for requests coming through FastAPI happens in the route
handlers (see `backend/api/dependencies.py` and the route modules), not by
relying on RLS at this layer. RLS (see `supabase/migrations/`) is still
defined for defense-in-depth against any future direct frontend-to-Supabase
reads using the anon key + a user's own session, per Section 8.2/8.3 of
`instructions_refactor.md`.
"""

from typing import Optional

from backend.config import SUPABASE_SERVICE_ROLE_KEY, SUPABASE_URL

_client = None


class SupabaseNotConfigured(RuntimeError):
	"""Raised when SUPABASE_URL/SUPABASE_SERVICE_ROLE_KEY aren't set."""


def get_client():
	"""Return the shared service-role Supabase client, creating it lazily."""
	global _client
	if _client is None:
		if not SUPABASE_URL or not SUPABASE_SERVICE_ROLE_KEY:
			raise SupabaseNotConfigured(
				"SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY are required"
			)
		from supabase import create_client

		_client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
	return _client


def get_user_from_token(access_token: str) -> dict:
	"""Resolve a bearer access token to {user_id, email} via Supabase Auth.

	Raises on any invalid/expired/rejected token — callers (the
	`get_current_user` dependency) turn that into a 401.
	"""
	response = get_client().auth.get_user(access_token)
	if response is None or response.user is None:
		raise ValueError("invalid or expired access token")
	return {"user_id": response.user.id, "email": response.user.email}


def create_conversation(conversation_id: str, user_id: str, language: str = "en") -> dict:
	result = (
		get_client()
		.table("conversations")
		.insert({"id": conversation_id, "user_id": user_id, "language": language})
		.execute()
	)
	return result.data[0] if result.data else {}


def get_conversation(conversation_id: str) -> Optional[dict]:
	result = (
		get_client()
		.table("conversations")
		.select("*")
		.eq("id", conversation_id)
		.limit(1)
		.execute()
	)
	return result.data[0] if result.data else None


def insert_message(conversation_id: str, role: str, content: str) -> dict:
	result = (
		get_client()
		.table("messages")
		.insert({"conversation_id": conversation_id, "role": role, "content": content})
		.execute()
	)
	return result.data[0] if result.data else {}


def list_messages(conversation_id: str) -> list[dict]:
	result = (
		get_client()
		.table("messages")
		.select("*")
		.eq("conversation_id", conversation_id)
		.order("created_at")
		.execute()
	)
	return result.data or []


def insert_citations(message_id: str, citations: list[dict]) -> None:
	if not citations:
		return
	rows = [
		{"message_id": message_id, "source_id": c["source_id"], "label": c["label"]}
		for c in citations
	]
	get_client().table("citations").insert(rows).execute()


def get_message(message_id: str) -> Optional[dict]:
	result = get_client().table("messages").select("*").eq("id", message_id).limit(1).execute()
	return result.data[0] if result.data else None


def insert_feedback(user_id: str, message_id: str, feedback: str) -> dict:
	result = (
		get_client()
		.table("feedback")
		.insert({"user_id": user_id, "message_id": message_id, "feedback": feedback})
		.execute()
	)
	return result.data[0] if result.data else {}


def create_share(share_id: str, conversation_id: str) -> dict:
	result = (
		get_client()
		.table("shares")
		.insert({"share_id": share_id, "conversation_id": conversation_id})
		.execute()
	)
	return result.data[0] if result.data else {}


def resolve_share(share_id: str) -> Optional[dict]:
	"""Resolve share_id -> conversation -> messages at read time (Section 8.3:
	don't fork message content into the share row, always reflect current
	data)."""
	share_result = (
		get_client().table("shares").select("*").eq("share_id", share_id).limit(1).execute()
	)
	if not share_result.data:
		return None
	conversation_id = share_result.data[0]["conversation_id"]
	conversation = get_conversation(conversation_id)
	if conversation is None:
		return None
	return {"conversation": conversation, "messages": list_messages(conversation_id)}
