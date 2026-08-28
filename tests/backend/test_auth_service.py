"""Unit tests for the Supabase Auth wrapper (no custom JWT/bcrypt)."""

import unittest
from unittest.mock import MagicMock, patch

from backend.services import auth_service


def _fake_client(sign_up_result=None, sign_in_result=None):
	client = MagicMock()
	if sign_up_result is not None:
		client.auth.sign_up.return_value = sign_up_result
	if sign_in_result is not None:
		client.auth.sign_in_with_password.return_value = sign_in_result
	return client


class SignUpTests(unittest.TestCase):
	def test_sign_up_returns_user_id_and_access_token(self):
		response = MagicMock()
		response.user.id = "u1"
		response.session.access_token = "token123"
		with patch("backend.services.auth_service.get_client", return_value=_fake_client(sign_up_result=response)):
			result = auth_service.sign_up("a@example.com", "password123")
		self.assertEqual(result.user_id, "u1")
		self.assertEqual(result.access_token, "token123")

	def test_sign_up_without_session_raises(self):
		response = MagicMock()
		response.user = MagicMock()
		response.session = None
		with patch("backend.services.auth_service.get_client", return_value=_fake_client(sign_up_result=response)):
			with self.assertRaises(ValueError):
				auth_service.sign_up("a@example.com", "password123")


class SignInTests(unittest.TestCase):
	def test_sign_in_returns_access_token_and_expiry(self):
		response = MagicMock()
		response.session.access_token = "token456"
		response.session.expires_in = 3600
		with patch("backend.services.auth_service.get_client", return_value=_fake_client(sign_in_result=response)):
			result = auth_service.sign_in("a@example.com", "password123")
		self.assertEqual(result.access_token, "token456")
		self.assertEqual(result.expires_in, 3600)

	def test_sign_in_without_session_raises(self):
		response = MagicMock()
		response.session = None
		with patch("backend.services.auth_service.get_client", return_value=_fake_client(sign_in_result=response)):
			with self.assertRaises(ValueError):
				auth_service.sign_in("a@example.com", "wrong-password")


class SignOutTests(unittest.TestCase):
	def test_sign_out_revokes_via_admin_api_with_global_scope(self):
		client = MagicMock()
		with patch("backend.services.auth_service.get_client", return_value=client):
			auth_service.sign_out("token789")
		client.auth.admin.sign_out.assert_called_once_with("token789", scope="global")


if __name__ == "__main__":
	unittest.main()
