"""Unit tests for /api/auth error surfacing."""

import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient
from supabase_auth.errors import AuthApiError

from backend.main import app


class AuthErrorSurfacingTests(unittest.TestCase):
	def setUp(self):
		self.client = TestClient(app, raise_server_exceptions=False)

	def test_rate_limit_error_surfaces_as_429_not_generic_400(self):
		with patch(
			"backend.api.routes.auth.auth_service.sign_up",
			side_effect=AuthApiError("email rate limit exceeded", 429, "over_email_send_rate_limit"),
		):
			response = self.client.post(
				"/api/auth/signup", json={"email": "a@example.com", "password": "pw123456"}
			)
		self.assertEqual(response.status_code, 429)
		self.assertEqual(response.json()["detail"], "email rate limit exceeded")

	def test_invalid_email_error_surfaces_its_own_status(self):
		with patch(
			"backend.api.routes.auth.auth_service.sign_up",
			side_effect=AuthApiError('Email address "x" is invalid', 400, "validation_failed"),
		):
			response = self.client.post(
				"/api/auth/signup", json={"email": "a@example.com", "password": "pw123456"}
			)
		self.assertEqual(response.status_code, 400)
		self.assertIn("invalid", response.json()["detail"])

	def test_unexpected_error_falls_back_to_generic_message(self):
		with patch(
			"backend.api.routes.auth.auth_service.sign_in",
			side_effect=RuntimeError("boom"),
		):
			response = self.client.post(
				"/api/auth/login", json={"email": "a@example.com", "password": "pw123456"}
			)
		self.assertEqual(response.status_code, 401)
		self.assertEqual(response.json()["detail"], "Invalid credentials")


if __name__ == "__main__":
	unittest.main()
