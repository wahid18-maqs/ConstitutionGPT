"""Unit tests for /api/source/{id} and /api/articles (Ui updates and
features.md 2.2 A1's Fundamental Rights / Directive Principles sub-menus)."""

import unittest
from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient

from backend.main import app


def _hit(article: str, text: str) -> dict:
	return {"fields": {"article": article, "text": text, "page": 1}}


class SourceRouteTests(unittest.TestCase):
	def setUp(self):
		self.client = TestClient(app, raise_server_exceptions=False)

	def test_get_source_for_known_article_includes_related_case(self):
		mock_service = MagicMock()
		mock_service.search_text.return_value = {
			"result": {"hits": [_hit("21", "21. Protection of life...")]}
		}
		with patch("backend.api.routes.sources._get_service", return_value=mock_service):
			response = self.client.get("/api/source/article_21")
		self.assertEqual(response.status_code, 200)
		body = response.json()
		self.assertEqual(body["article"], "21")
		self.assertIn("Maneka Gandhi v. Union of India (1978)", body["related_cases"])

	def test_get_source_for_unlinked_article_has_no_related_cases(self):
		mock_service = MagicMock()
		mock_service.search_text.return_value = {
			"result": {"hits": [_hit("14", "14. Equality before law...")]}
		}
		with patch("backend.api.routes.sources._get_service", return_value=mock_service):
			response = self.client.get("/api/source/article_14")
		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.json()["related_cases"], [])

	def test_get_source_404s_when_nothing_found(self):
		mock_service = MagicMock()
		mock_service.search_text.return_value = {"result": {"hits": []}}
		with patch("backend.api.routes.sources._get_service", return_value=mock_service):
			response = self.client.get("/api/source/article_999")
		self.assertEqual(response.status_code, 404)


class ArticleGroupRouteTests(unittest.TestCase):
	def setUp(self):
		self.client = TestClient(app, raise_server_exceptions=False)

	def test_unknown_category_404s(self):
		response = self.client.get("/api/articles", params={"category": "bogus"})
		self.assertEqual(response.status_code, 404)

	def test_known_category_returns_stacked_sources_in_order(self):
		mock_service = MagicMock()
		mock_service.search_text.side_effect = [
			{"result": {"hits": [_hit(article, f"{article}. text")]}}
			for article in ["14", "15", "16", "17", "18"]
		]
		with patch("backend.api.routes.sources._get_service", return_value=mock_service):
			response = self.client.get("/api/articles", params={"category": "equality"})
		self.assertEqual(response.status_code, 200)
		body = response.json()
		self.assertEqual(body["label"], "Right to Equality")
		self.assertEqual([s["article"] for s in body["sources"]], ["14", "15", "16", "17", "18"])

	def test_missing_article_in_category_is_skipped_not_fatal(self):
		mock_service = MagicMock()
		mock_service.search_text.side_effect = [
			{"result": {"hits": [_hit("23", "23. text")]}},
			{"result": {"hits": []}},  # article 24 missing from the index
		]
		with patch("backend.api.routes.sources._get_service", return_value=mock_service):
			response = self.client.get("/api/articles", params={"category": "against_exploitation"})
		self.assertEqual(response.status_code, 200)
		body = response.json()
		self.assertEqual([s["article"] for s in body["sources"]], ["23"])


if __name__ == "__main__":
	unittest.main()
