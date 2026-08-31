"""Full-text/topic search across the whole corpus (Ui updates and
features.md 2.2 B1's Search by Topic sub-item) — unfiltered semantic
search returning a ranked results list, not a single generated answer.

Ships without reranking (RERANK_ENABLED=false, not yet implemented per
KNOWN_ISSUES.md) as the doc itself anticipated — conceptual queries can
still be out-ranked by verbose case-law text here, same known limitation
tracked there. Called out explicitly rather than shipped as if solved.
"""

from fastapi import APIRouter, HTTPException

from backend.config import PINECONE_NAMESPACE
from backend.graph.nodes.citations import citation_for
from backend.models.search import SearchResponse, SearchResult
from backend.services import supabase as supabase_service
from backend.services.pinecone import PineconeService
from backend.services.pinecone_chat import hits_from_response

router = APIRouter()

_service = None

SNIPPET_MAX_CHARS = 320
FULLTEXT_CONTEXT_CHARS = 120


def _get_service() -> PineconeService:
	global _service
	if _service is None:
		_service = PineconeService()
	return _service


def _snippet(text: str) -> str:
	text = text.strip()
	if len(text) <= SNIPPET_MAX_CHARS:
		return text
	return text[:SNIPPET_MAX_CHARS].rstrip() + "…"


def _snippet_around_match(text: str, query: str) -> str:
	"""Unlike Search by Topic's from-the-start snippet, a literal match's
	usefulness is showing the query *in context* -- window it around the
	first occurrence instead of always taking the opening characters."""
	lower_text = text.lower()
	index = lower_text.find(query.lower())
	if index == -1:
		return _snippet(text)
	start = max(0, index - FULLTEXT_CONTEXT_CHARS)
	end = min(len(text), index + len(query) + FULLTEXT_CONTEXT_CHARS)
	prefix = "…" if start > 0 else ""
	suffix = "…" if end < len(text) else ""
	return f"{prefix}{text[start:end].strip()}{suffix}"


@router.get("/api/search", response_model=SearchResponse)
def search(q: str):
	query = q.strip()
	if not query:
		raise HTTPException(status_code=400, detail="q must not be empty")

	response = _get_service().search_text(text=query, top_k=10, namespace=PINECONE_NAMESPACE)
	hits = hits_from_response(response)

	results = []
	seen_source_ids = set()
	for hit in hits:
		fields = hit.get("fields", {})
		citation = citation_for(fields)
		if citation is None or citation["source_id"] in seen_source_ids:
			continue
		seen_source_ids.add(citation["source_id"])
		results.append(
			SearchResult(
				source_id=citation["source_id"],
				label=citation["label"],
				snippet=_snippet(fields.get("text", "")),
				score=hit.get("_score"),
			)
		)

	return SearchResponse(query=query, results=results)


@router.get("/api/search/fulltext", response_model=SearchResponse)
def search_fulltext(q: str):
	"""Literal keyword/phrase match (coming_soon.md #1) -- distinct from
	the semantic search above. Backed by public.document_chunks (Supabase
	Postgres, ILIKE), populated by scripts/sync_fulltext.py, since Pinecone
	has no literal substring search of its own."""
	query = q.strip()
	if not query:
		raise HTTPException(status_code=400, detail="q must not be empty")

	rows = supabase_service.search_fulltext(query, limit=20)

	results = []
	seen_source_ids = set()
	for row in rows:
		source_id = row["source_id"]
		if source_id in seen_source_ids:
			continue
		seen_source_ids.add(source_id)
		results.append(
			SearchResult(
				source_id=source_id,
				label=row["label"],
				snippet=_snippet_around_match(row["chunk_text"], query),
				score=None,
			)
		)

	return SearchResponse(query=query, results=results)
