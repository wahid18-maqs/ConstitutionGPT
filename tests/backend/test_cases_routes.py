"""Unit tests for GET /api/cases/analysis (coming_soon.md #2)."""

import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

from backend.main import app


class CaseAnalysisRouteTests(unittest.TestCase):
	def setUp(self):
		self.client = TestClient(app, raise_server_exceptions=False)

	def test_only_cases_with_an_analysis_entry_are_returned(self):
		fake_metadata = {
			"case_with_analysis": {"case_name": "Case With Analysis", "year": 2000, "analysis": "A summary."},
			"case_without_analysis": {"case_name": "Case Without Analysis", "year": 2001},
		}
		with patch("backend.api.routes.cases.CASE_METADATA", fake_metadata):
			response = self.client.get("/api/cases/analysis")
		self.assertEqual(response.status_code, 200)
		body = response.json()
		self.assertEqual(len(body["analyses"]), 1)
		self.assertEqual(body["analyses"][0]["case_id"], "case_with_analysis")
		self.assertEqual(body["analyses"][0]["analysis"], "A summary.")


if __name__ == "__main__":
	unittest.main()
