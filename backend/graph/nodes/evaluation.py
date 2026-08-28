"""Context evaluation node: heuristic weak/good gate and the retry rewrite."""

from backend.graph.state import GraphState

# llama-text-embed-v2 integrated-search scores run low in absolute terms —
# a genuinely relevant top hit against this corpus scores roughly 0.2-0.25
# (confirmed against a live query), not the 0.7+ a cosine-similarity
# intuition might suggest. This threshold is a conservative floor meant to
# catch true near-misses, not to second-guess moderately-scored hits.
WEAK_SCORE_THRESHOLD = 0.05


def _top_score(hits: list[dict]) -> float:
	if not hits:
		return 0.0
	top = hits[0]
	return top.get("_score", top.get("score", 0.0)) or 0.0


def evaluate_context(state: GraphState) -> GraphState:
	"""Flag retrieved context as "weak" when there's little or no signal."""
	hits = state.get("retrieved_documents") or []
	context = state.get("context", "")
	quality = "good"
	if not hits or not context.strip() or _top_score(hits) < WEAK_SCORE_THRESHOLD:
		quality = "weak"
	return {**state, "context_quality": quality}


def rewrite_query(state: GraphState) -> GraphState:
	"""Widen the search for a retry: drop an over-specific metadata filter."""
	metadata_filter = state.get("metadata_filter")
	if metadata_filter:
		# The regex/intent filter likely matched the wrong reference (or one
		# that doesn't exist in the index) — fall back to pure semantic
		# search over the full corpus for the retry.
		metadata_filter = None
	return {
		**state,
		"query": state.get("original_query", state["query"]),
		"metadata_filter": metadata_filter,
		"retry_count": state.get("retry_count", 0) + 1,
	}


def route_after_evaluation(state: GraphState) -> str:
	"""Conditional-edge function: retry once on weak context, else generate."""
	if state.get("context_quality") == "weak" and state.get("retry_count", 0) == 0:
		return "rewrite"
	return "generate"
