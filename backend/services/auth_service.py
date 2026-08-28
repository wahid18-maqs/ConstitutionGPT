"""Supabase Auth wrapper for ConstituteAI — no custom JWT/bcrypt flow.

All signup/login/logout/session handling is delegated to Supabase Auth
(GoTrue), per `instructions_refactor.md` Section 8.2's non-negotiable: this
module issues no tokens of its own, it only calls Supabase.
"""

from backend.models.user import LoginResponse, SignupResponse
from backend.services.supabase import get_client


def sign_up(email: str, password: str) -> SignupResponse:
	response = get_client().auth.sign_up({"email": email, "password": password})
	if response.user is None or response.session is None:
		raise ValueError("signup failed")
	return SignupResponse(
		user_id=response.user.id, access_token=response.session.access_token
	)


def sign_in(email: str, password: str) -> LoginResponse:
	response = get_client().auth.sign_in_with_password(
		{"email": email, "password": password}
	)
	if response.session is None:
		raise ValueError("invalid credentials")
	return LoginResponse(
		access_token=response.session.access_token,
		expires_in=response.session.expires_in,
	)


def sign_out(access_token: str) -> None:
	"""Revoke the session behind this access token.

	Supabase issues short-lived JWTs; rather than treating logout as a
	no-op client-side token discard, this calls the Auth admin API's
	session-revocation endpoint (available because the backend holds the
	service role key) with `scope="global"`, which invalidates the
	underlying refresh token so the session can't be silently renewed.
	The access token itself keeps working until its own short TTL expires
	(Supabase Auth doesn't maintain an access-token blocklist), but no new
	one can be issued from this session afterward.
	"""
	get_client().auth.admin.sign_out(access_token, scope="global")
