"""Authentication routes for ConstituteAI (Section 4)."""

from fastapi import APIRouter, Depends, HTTPException, Response
from supabase_auth.errors import AuthApiError

from backend.api.dependencies import get_bearer_token, get_current_user
from backend.models.user import AuthRequest, LoginResponse, SignupResponse, UserResponse
from backend.services import auth_service

router = APIRouter(prefix="/api/auth")


def _http_exception_for(exc: Exception, fallback_status: int, fallback_detail: str) -> HTTPException:
	"""Surface Supabase's own status/message (e.g. a 429 rate limit) instead
	of collapsing every failure into one generic error — a real Supabase
	rejection reason (invalid email, rate limited, wrong password) is very
	different from this backend actually being broken, and callers need to
	tell them apart."""
	if isinstance(exc, AuthApiError):
		return HTTPException(status_code=exc.status, detail=exc.message)
	return HTTPException(status_code=fallback_status, detail=fallback_detail)


@router.post("/signup", response_model=SignupResponse)
def signup(payload: AuthRequest):
	try:
		return auth_service.sign_up(payload.email, payload.password)
	except Exception as exc:
		raise _http_exception_for(exc, 400, "Signup failed") from exc


@router.post("/login", response_model=LoginResponse)
def login(payload: AuthRequest):
	try:
		return auth_service.sign_in(payload.email, payload.password)
	except Exception as exc:
		raise _http_exception_for(exc, 401, "Invalid credentials") from exc


@router.post("/logout", status_code=204, response_class=Response)
def logout(
	current_user: UserResponse = Depends(get_current_user),
	token: str = Depends(get_bearer_token),
):
	try:
		auth_service.sign_out(token)
	except Exception as exc:
		raise _http_exception_for(exc, 400, "Logout failed") from exc
	return Response(status_code=204)


@router.get("/me", response_model=UserResponse)
def me(current_user: UserResponse = Depends(get_current_user)):
	return current_user
