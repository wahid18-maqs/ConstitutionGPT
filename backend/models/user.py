"""Authentication and user profile models for ConstituteAI."""

from pydantic import BaseModel, EmailStr


class AuthRequest(BaseModel):
	email: EmailStr
	password: str


class SignupResponse(BaseModel):
	user_id: str
	access_token: str
	token_type: str = "bearer"


class LoginResponse(BaseModel):
	access_token: str
	token_type: str = "bearer"
	expires_in: int


class UserResponse(BaseModel):
	user_id: str
	email: EmailStr