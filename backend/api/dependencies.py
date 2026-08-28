"""Shared FastAPI dependencies for ConstituteAI."""

from fastapi import HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from backend.models.user import UserResponse
from backend.services.supabase import get_user_from_token

_bearer_scheme = HTTPBearer()


def get_bearer_token(
	credentials: HTTPAuthorizationCredentials = Security(_bearer_scheme),
) -> str:
	"""Return the raw bearer token, for handlers that need to act on it
	directly (e.g. logout's session revocation) rather than only the
	resolved user."""
	return credentials.credentials


def get_current_user(token: str = Security(get_bearer_token)) -> UserResponse:
	"""Resolve the Supabase bearer token on the request to a UserResponse.

	Raises 401 on a missing (handled by HTTPBearer itself), malformed, or
	Supabase-rejected token.
	"""
	try:
		user = get_user_from_token(token)
	except Exception as exc:
		raise HTTPException(status_code=401, detail="Invalid or expired token") from exc
	return UserResponse(user_id=user["user_id"], email=user["email"])
