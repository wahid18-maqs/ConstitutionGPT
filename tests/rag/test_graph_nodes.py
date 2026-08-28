"""Unit tests for the Phase 3 LangGraph nodes."""

import unittest

from backend.graph.nodes.analyzer import analyze_query, classify_intent
from backend.graph.nodes.citations import build_citations
from backend.graph.nodes.evaluation import evaluate_context, rewrite_query, route_after_evaluation
from backend.graph.nodes.generation import LANGUAGE_NAMES, build_prompt
from backend.graph.nodes.metadata import build_metadata_filter
from backend.graph.nodes.retrieval import retrieve


class AnalyzerTests(unittest.TestCase):
	def test_article_reference_classified_as_article(self):
		state = analyze_query({"query": "What is Article 21?"})
		self.assertEqual(state["intent"], "article")
		self.assertEqual(state["metadata_filter"], {"article": {"$eq": "21"}})

	def test_article_368_classified_as_amendment(self):
		state = analyze_query({"query": "Explain Article 368 clause 2"})
		self.assertEqual(state["intent"], "amendment")

	def test_amendment_keyword_classified_as_amendment(self):
		self.assertEqual(classify_intent("How can the Constitution be amended?", {}), "amendment")

	def test_known_case_name_classified_as_case_law(self):
		self.assertEqual(classify_intent("Explain Kesavananda Bharati.", {}), "case_law")

	def test_registered_case_name_classified_as_case_law(self):
		self.assertEqual(
			classify_intent("What did the court hold in Maneka Gandhi v. Union of India?", {}),
			"case_law",
		)

	def test_history_keyword_classified_as_history(self):
		self.assertEqual(classify_intent("When was the Constitution adopted?", {}), "history")

	def test_unmatched_query_classified_as_general(self):
		self.assertEqual(classify_intent("Explain fundamental rights", {}), "general")

	def test_original_query_preserved_across_calls(self):
		state = analyze_query({"query": "rewritten query", "original_query": "first query"})
		self.assertEqual(state["original_query"], "first query")


class MetadataBuilderTests(unittest.TestCase):
	def test_article_intent_constrains_to_constitution(self):
		state = build_metadata_filter({"intent": "article", "metadata_filter": {"article": {"$eq": "21"}}})
		self.assertEqual(
			state["metadata_filter"],
			{"article": {"$eq": "21"}, "document_type": {"$eq": "constitution"}},
		)

	def test_case_law_intent_strips_article_and_clause(self):
		state = build_metadata_filter({
			"intent": "case_law",
			"metadata_filter": {"article": {"$eq": "21"}, "clause": {"$eq": "1"}},
		})
		self.assertEqual(state["metadata_filter"], {"document_type": {"$eq": "case_law"}})

	def test_general_intent_adds_no_document_type_constraint(self):
		state = build_metadata_filter({"intent": "general", "metadata_filter": {}})
		self.assertIsNone(state["metadata_filter"])


class RetrievalNodeTests(unittest.TestCase):
	def test_retrieve_passes_filter_and_builds_context(self):
		class FakeRetriever:
			def retrieve(self, query, metadata_filter_override=None):
				self.called_with = (query, metadata_filter_override)
				return {"matches": [{"fields": {"text": "hit one"}}, {"fields": {"text": "hit two"}}]}

		retriever = FakeRetriever()
		state = retrieve({"query": "What is Article 21?", "metadata_filter": {"article": {"$eq": "21"}}}, retriever=retriever)
		self.assertEqual(retriever.called_with, ("What is Article 21?", {"article": {"$eq": "21"}}))
		self.assertEqual(len(state["retrieved_documents"]), 2)
		self.assertEqual(state["context"], "hit one\n\nhit two")


class EvaluationTests(unittest.TestCase):
	def test_no_hits_is_weak(self):
		state = evaluate_context({"retrieved_documents": [], "context": ""})
		self.assertEqual(state["context_quality"], "weak")

	def test_low_score_hit_is_weak(self):
		state = evaluate_context({
			"retrieved_documents": [{"_score": 0.01, "fields": {"text": "x"}}],
			"context": "x",
		})
		self.assertEqual(state["context_quality"], "weak")

	def test_reasonable_score_hit_is_good(self):
		state = evaluate_context({
			"retrieved_documents": [{"_score": 0.25, "fields": {"text": "x"}}],
			"context": "x",
		})
		self.assertEqual(state["context_quality"], "good")

	def test_rewrite_clears_filter_and_increments_retry(self):
		state = rewrite_query({
			"query": "Article 999 rights",
			"original_query": "Article 999 rights",
			"metadata_filter": {"article": {"$eq": "999"}},
			"retry_count": 0,
		})
		self.assertIsNone(state["metadata_filter"])
		self.assertEqual(state["retry_count"], 1)

	def test_route_retries_once_then_forces_generation(self):
		weak_first_try = {"context_quality": "weak", "retry_count": 0}
		weak_second_try = {"context_quality": "weak", "retry_count": 1}
		good = {"context_quality": "good", "retry_count": 0}
		self.assertEqual(route_after_evaluation(weak_first_try), "rewrite")
		self.assertEqual(route_after_evaluation(weak_second_try), "generate")
		self.assertEqual(route_after_evaluation(good), "generate")


class GenerationPromptTests(unittest.TestCase):
	def test_prompt_requests_target_language(self):
		prompt = build_prompt({"query": "What is Article 21?", "language": "ta", "context": "context text", "chat_history": []})
		self.assertIn(LANGUAGE_NAMES["ta"], prompt)
		self.assertIn("research aid, not legal advice", prompt)
		self.assertIn("context text", prompt)

	def test_prompt_defaults_to_english(self):
		prompt = build_prompt({"query": "q", "context": "", "chat_history": []})
		self.assertIn("English", prompt)


class CitationsTests(unittest.TestCase):
	def test_article_hit_produces_article_citation(self):
		state = build_citations({"retrieved_documents": [{"fields": {"article": "21", "document_type": "constitution"}}]})
		self.assertEqual(state["citations"], [{"source_id": "article_21", "label": "Article 21"}])

	def test_case_law_hit_produces_case_citation(self):
		state = build_citations({
			"retrieved_documents": [{
				"fields": {
					"document_type": "case_law",
					"case_id": "maneka_gandhi_1978",
					"case_name": "Maneka Gandhi v. Union of India",
				}
			}]
		})
		self.assertEqual(
			state["citations"],
			[{"source_id": "maneka_gandhi_1978", "label": "Maneka Gandhi v. Union of India"}],
		)

	def test_duplicate_sources_are_deduplicated(self):
		hit = {"fields": {"article": "21", "document_type": "constitution"}}
		state = build_citations({"retrieved_documents": [hit, hit]})
		self.assertEqual(len(state["citations"]), 1)


if __name__ == "__main__":
	unittest.main()
