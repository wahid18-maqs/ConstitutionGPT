"""Unit tests for Pinecone-hosted reranking configuration."""

import unittest

from backend.rag.reranker import PineconeReranker


class FakeService:
	def __init__(self):
		self.calls = []

	def search_text(self, **kwargs):
		self.calls.append(kwargs)
		return {"result": {"hits": []}}


class RerankerTests(unittest.TestCase):
	def test_wide_candidates_are_reranked_to_final_k(self):
		service = FakeService()
		reranker = PineconeReranker(service, candidate_k=25, final_k=10)
		reranker.retrieve("constitutional rights", {"article": {"$eq": "21"}}, "constitution-v2")
		call = service.calls[0]
		self.assertEqual(call["top_k"], 25)
		self.assertEqual(call["rerank"], {
			"model": "bge-reranker-v2-m3",
			"rank_fields": ["text"],
			"top_n": 10,
		})
		self.assertEqual(call["namespace"], "constitution-v2")

	def test_candidate_k_cannot_be_smaller_than_final_k(self):
		with self.assertRaises(ValueError):
			PineconeReranker(FakeService(), candidate_k=5, final_k=10)


if __name__ == "__main__":
	unittest.main()