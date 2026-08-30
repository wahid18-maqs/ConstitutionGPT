"""Unit tests for GET /api/search (Ui updates and features.md 2.2 B1)."""

import unittest
from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient

from backend.main import app


def _hit(fields: dict, score: float) -> dict:
	return {"fields": fields, "_score": score}


class SearchRouteTests(unittest.TestCase):
	def setUp(self):
		self.client = TestClient(app, raise_server_exceptions=False)

	def test_empty_query_is_rejected(self):
		response = self.client.get("/api/search", params={"q": "  "})
		self.assertEqual(response.status_code, 400)

	def test_results_are_deduped_by_source_and_carry_score(self):
		mock_service = MagicMock()
		mock_service.search_text.return_value = {
			"result": {
				"hits": [
					_hit({"article": "14", "document_type": "constitution", "text": "14. Equality..."}, 0.5),
					_hit(
						{
							"case_id": "maneka_gandhi_1978",
							"case_name": "Maneka Gandhi v. Union of India",
							"document_type": "case_law",
							"text": "equality before the law...",
						},
						0.43,
					),
					# Second chunk from the same case — should collapse into one result.
					_hit(
						{
							"case_id": "maneka_gandhi_1978",
							"case_name": "Maneka Gandhi v. Union of India",
							"document_type": "case_law",
							"text": "a different passage from the same judgment",
						},
						0.30,
					),
				]
			}
		}
		with patch("backend.api.routes.search._get_service", return_value=mock_service):
			response = self.client.get("/api/search", params={"q": "equality before law"})
		self.assertEqual(response.status_code, 200)
		body = response.json()
		self.assertEqual(len(body["results"]), 2)
		self.assertEqual(body["results"][0]["source_id"], "article_14")
		self.assertEqual(body["results"][0]["score"], 0.5)
		self.assertEqual(body["results"][1]["source_id"], "maneka_gandhi_1978")

	def test_long_text_is_truncated_to_a_snippet(self):
		long_text = "x" * 1000
		mock_service = MagicMock()
		mock_service.search_text.return_value = {
			"result": {"hits": [_hit({"article": "21", "document_type": "constitution", "text": long_text}, 0.9)]}
		}
		with patch("backend.api.routes.search._get_service", return_value=mock_service):
			response = self.client.get("/api/search", params={"q": "life and liberty"})
		snippet = response.json()["results"][0]["snippet"]
		self.assertLess(len(snippet), len(long_text))
		self.assertTrue(snippet.endswith("…"))


if __name__ == "__main__":
	unittest.main()
