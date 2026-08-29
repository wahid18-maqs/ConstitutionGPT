"""Unit tests for /api/chat and /api/history auth + persistence wiring."""

import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

from backend.api.dependencies import get_current_user
from backend.main import app
from backend.models.user import UserResponse


USER_A = UserResponse(user_id="user-a", email="a@example.com")
USER_B = UserResponse(user_id="user-b", email="b@example.com")


class ChatAuthTests(unittest.TestCase):
	def setUp(self):
		self.client = TestClient(app, raise_server_exceptions=False)
		app.dependency_overrides.pop(get_current_user, None)

	def tearDown(self):
		app.dependency_overrides.pop(get_current_user, None)

	def test_chat_without_token_is_rejected(self):
		response = self.client.post(
			"/api/chat",
			json={"message": "What is Article 21?", "conversation_id": "c1"},
		)
		self.assertEqual(response.status_code, 403)  # HTTPBearer's own missing-credentials response

	def test_chat_with_valid_token_persists_and_returns_answer(self):
		app.dependency_overrides[get_current_user] = lambda: USER_A
		with patch("backend.api.routes.chat.supabase_service") as mock_supabase, \
			patch("backend.api.routes.chat.run_chat_graph") as mock_run:
			mock_supabase.get_conversation.return_value = None
			mock_supabase.insert_message.side_effect = [
				{"id": "msg-user"}, {"id": "msg-assistant"},
			]
			mock_run.return_value = {
				"answer": "Article 21 protects life and liberty.",
				"citations": [{"source_id": "article_21", "label": "Article 21"}],
				"intent": "article",
			}
			response = self.client.post(
				"/api/chat",
				json={"message": "What is Article 21?", "conversation_id": "c1"},
				headers={"Authorization": "Bearer good-token"},
			)
		self.assertEqual(response.status_code, 200)
		body = response.json()
		self.assertEqual(body["answer"], "Article 21 protects life and liberty.")
		self.assertEqual(body["citations"], [{"source_id": "article_21", "label": "Article 21"}])
		mock_supabase.create_conversation.assert_called_once_with(
			"c1", "user-a", "en", title="What is Article 21?"
		)
		mock_supabase.insert_citations.assert_called_once_with(
			"msg-assistant", [{"source_id": "article_21", "label": "Article 21"}]
		)

	def test_chat_rejects_conversation_owned_by_another_user(self):
		app.dependency_overrides[get_current_user] = lambda: USER_B
		with patch("backend.api.routes.chat.supabase_service") as mock_supabase:
			mock_supabase.get_conversation.return_value = {"id": "c1", "user_id": "user-a"}
			response = self.client.post(
				"/api/chat",
				json={"message": "Hello", "conversation_id": "c1"},
				headers={"Authorization": "Bearer good-token"},
			)
		self.assertEqual(response.status_code, 403)

	def test_history_rejects_conversation_owned_by_another_user(self):
		app.dependency_overrides[get_current_user] = lambda: USER_B
		with patch("backend.api.routes.chat.supabase_service") as mock_supabase:
			mock_supabase.get_conversation.return_value = {"id": "c1", "user_id": "user-a"}
			response = self.client.get(
				"/api/history",
				params={"conversation_id": "c1"},
				headers={"Authorization": "Bearer good-token"},
			)
		self.assertEqual(response.status_code, 403)

	def test_history_returns_persisted_messages_for_owner(self):
		app.dependency_overrides[get_current_user] = lambda: USER_A
		with patch("backend.api.routes.chat.supabase_service") as mock_supabase:
			mock_supabase.get_conversation.return_value = {"id": "c1", "user_id": "user-a"}
			mock_supabase.list_messages.return_value = [
				{"id": "m1", "role": "user", "content": "Hi", "created_at": None},
			]
			response = self.client.get(
				"/api/history",
				params={"conversation_id": "c1"},
				headers={"Authorization": "Bearer good-token"},
			)
		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.json()["messages"][0]["content"], "Hi")


if __name__ == "__main__":
	unittest.main()
