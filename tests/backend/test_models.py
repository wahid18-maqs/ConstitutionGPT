"""Unit tests for Phase 1 API models."""

import unittest

from pydantic import ValidationError

from backend.models.chat import ChatRequest
from backend.models.feedback import FeedbackRequest
from backend.models.source import SearchRequest
from backend.models.user import AuthRequest


class ModelTests(unittest.TestCase):
	def test_chat_contract_defaults_language(self):
		request = ChatRequest(message="What is Article 21?", conversation_id="abc123")
		self.assertEqual(request.language, "en")

	def test_chat_contract_rejects_unknown_language(self):
		with self.assertRaises(ValidationError):
			ChatRequest(message="Question", language="xx", conversation_id="abc123")

	def test_auth_email_is_validated(self):
		with self.assertRaises(ValidationError):
			AuthRequest(email="not-an-email", password="secret")

	def test_feedback_accepts_only_supported_values(self):
		with self.assertRaises(ValidationError):
			FeedbackRequest(message_id="msg123", feedback="neutral")

	def test_search_rejects_empty_query(self):
		with self.assertRaises(ValidationError):
			SearchRequest(query="")


if __name__ == "__main__":
	unittest.main()
