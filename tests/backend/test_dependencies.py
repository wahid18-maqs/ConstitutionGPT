"""Unit tests for the get_current_user auth dependency."""

import unittest
from unittest.mock import patch

from fastapi import HTTPException

from backend.api.dependencies import get_current_user


class GetCurrentUserTests(unittest.TestCase):
	def test_valid_token_resolves_to_user(self):
		with patch(
			"backend.api.dependencies.get_user_from_token",
			return_value={"user_id": "u1", "email": "a@example.com"},
		):
			user = get_current_user(token="valid-token")
		self.assertEqual(user.user_id, "u1")
		self.assertEqual(user.email, "a@example.com")

	def test_rejected_token_raises_401(self):
		with patch(
			"backend.api.dependencies.get_user_from_token",
			side_effect=ValueError("invalid or expired access token"),
		):
			with self.assertRaises(HTTPException) as ctx:
				get_current_user(token="bad-token")
		self.assertEqual(ctx.exception.status_code, 401)


if __name__ == "__main__":
	unittest.main()
