"""Unit tests for metadata extraction and hybrid retrieval."""

import unittest

from backend.rag.retriever import PineconeRetriever, extract_metadata_filter


class FakePineconeService:
	def __init__(self):
		self.calls = []

	def search_text(self, **kwargs):
		self.calls.append(kwargs)
		return {"matches": []}


class RetrieverTests(unittest.TestCase):
	def test_article_reference_becomes_filter(self):
		self.assertEqual(
			extract_metadata_filter("What is Article 21?"),
			{"article": {"$eq": "21"}},
		)

	def test_clause_reference_combines_with_article(self):
		self.assertEqual(
			extract_metadata_filter(
				"Explain Article 368, clause 2, and the amendment procedure"
			),
			{
				"article": {"$eq": "368"},
				"clause": {"$eq": "2"},
			},
		)

	def test_unindexed_category_reference_does_not_create_filter(self):
		self.assertEqual(
			extract_metadata_filter("Explain fundamental rights"),
			{},
		)

	def test_retriever_combines_filter_with_semantic_top_k(self):
		service = FakePineconeService()
		retriever = PineconeRetriever(service, top_k=5, use_reranker=True)
		retriever.retrieve("What is Article 21?")
		self.assertEqual(service.calls[0]["filter"], {"article": {"$eq": "21"}})
		self.assertEqual(service.calls[0]["top_k"], 25)
		self.assertEqual(service.calls[0]["rerank"]["top_n"], 5)
		self.assertEqual(service.calls[0]["rerank"]["model"], "bge-reranker-v2-m3")
		self.assertEqual(service.calls[0]["text"], "What is Article 21?")


if __name__ == "__main__":
	unittest.main()