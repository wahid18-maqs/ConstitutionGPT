"""LangGraph workflow assembling the ConstituteAI chat pipeline (Section 6)."""

from typing import Any, Optional

from langgraph.graph import END, StateGraph

from backend.graph.nodes.analyzer import analyze_query
from backend.graph.nodes.citations import build_citations
from backend.graph.nodes.evaluation import evaluate_context, rewrite_query, route_after_evaluation
from backend.graph.nodes.generation import append_exchange, generate_answer
from backend.graph.nodes.metadata import build_metadata_filter
from backend.graph.nodes.retrieval import retrieve
from backend.graph.state import GraphState


def build_graph():
	"""Compile the analyzer -> metadata -> retrieval -> evaluation -> ... graph."""
	graph = StateGraph(GraphState)
	graph.add_node("analyzer", analyze_query)
	graph.add_node("metadata", build_metadata_filter)
	graph.add_node("retrieval", retrieve)
	graph.add_node("evaluation", evaluate_context)
	graph.add_node("rewrite", rewrite_query)
	graph.add_node("generation", generate_answer)
	# Named "citation_builder", not "citations" — langgraph forbids a node id
	# that collides with a GraphState field name, and "citations" is one.
	graph.add_node("citation_builder", build_citations)

	graph.set_entry_point("analyzer")
	graph.add_edge("analyzer", "metadata")
	graph.add_edge("metadata", "retrieval")
	graph.add_edge("retrieval", "evaluation")
	graph.add_conditional_edges(
		"evaluation", route_after_evaluation, {"rewrite": "rewrite", "generate": "generation"}
	)
	# One retry only: rewrite always re-enters retrieval/evaluation, and
	# route_after_evaluation only ever returns "rewrite" once (retry_count
	# gates it), so this can't loop indefinitely.
	graph.add_edge("rewrite", "retrieval")
	graph.add_edge("generation", "citation_builder")
	graph.add_edge("citation_builder", END)

	return graph.compile()


_compiled_graph = None


def _get_graph():
	global _compiled_graph
	if _compiled_graph is None:
		_compiled_graph = build_graph()
	return _compiled_graph


def run(query: str, language: str, chat_history: Optional[list[Any]] = None) -> dict:
	"""Run one chat turn through the graph and append it to chat_history."""
	history = chat_history if chat_history is not None else []
	initial_state: GraphState = {
		"query": query,
		"language": language,
		"chat_history": history,
		"retry_count": 0,
	}
	final_state = _get_graph().invoke(initial_state)
	append_exchange(history, query, final_state["answer"])
	return {
		"answer": final_state["answer"],
		"citations": final_state.get("citations", []),
		"context": final_state.get("retrieved_documents", []),
		"intent": final_state.get("intent"),
	}
