"""Article category/range lookup, powering the sidebar's Fundamental
Rights and Directive Principles sub-menus (Ui updates and features.md
2.2 A1). Anonymous access is fine here, same as /api/source (Section
8.2 — read-only reference lookups don't need an account).
"""

from fastapi import APIRouter, HTTPException

from backend.api.routes.sources import _build_source_response
from backend.article_categories import ARTICLE_CATEGORIES
from backend.models.source import ArticleGroupResponse

router = APIRouter()


@router.get("/api/articles", response_model=ArticleGroupResponse)
def get_articles(category: str):
	definition = ARTICLE_CATEGORIES.get(category)
	if definition is None:
		raise HTTPException(status_code=404, detail=f"Unknown category '{category}'")

	sources = []
	for article in definition["articles"]:
		source = _build_source_response(f"article_{article}")
		if source is not None:
			sources.append(source)

	return ArticleGroupResponse(category=category, label=definition["label"], sources=sources)
