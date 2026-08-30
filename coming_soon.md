# Coming Soon — remaining sidebar placeholders

> The two sub-items still showing "Coming soon" in the sidebar
> (`frontend/src/components/Sidebar.jsx`), tracked here so they're easy
> to pick back up. Everything else in the sidebar dropdown-expand
> feature (Search by Number, Search by Topic, Fundamental Rights/
> Directive Principles sub-items, Case Studies -> Landmark Judgments) is
> already built and wired to real data.

## 1. Full-Text Search (under Search Articles)

**Status:** Disabled placeholder. No backend capability exists.

**What it needs:**
- New Postgres full-text search infrastructure — nothing like this
  exists in the backend today. Unlike Search by Topic (which reuses
  Pinecone's existing semantic search), a literal keyword/phrase match
  is a different retrieval mode entirely.
- Per `Ui updates and features.md` 2.2 Tier B1's framing, the content
  shape is also different from Search by Topic's ranked semantic
  results: "a list of literal keyword matches, each showing the matched
  snippet in context" — closer to a `grep`-style result than a
  relevance-ranked list.

**Implementation sketch (not yet built):**
1. Decide the search backend: Postgres full-text search (`tsvector`/
   `tsquery`) against a table of chunk text, or a simpler `ILIKE`/regex
   scan if the corpus stays small. Postgres FTS is the more correct
   long-term choice given Supabase is already the Postgres provider in
   use.
2. New migration: a searchable table (or materialized view) mirroring
   the indexed chunk text + metadata (article/case_id, document_type),
   since Pinecone itself doesn't support literal substring search.
3. New `GET /api/search/fulltext?q=...` endpoint (distinct from the
   existing semantic `GET /api/search?q=...` used by Search by Topic) —
   returns literal matches with the matched snippet highlighted/
   contextualized, not a relevance score.
4. Frontend: reuse `SourceExplorer`'s existing "results" content shape
   (see `SourceExplorer.jsx`'s `ResultRow`) if the response shape can
   match `SearchResult` closely enough, or extend it if literal-match
   context needs different rendering (e.g. highlighting the matched
   substring inline).
5. Wire the Sidebar's disabled `Full-Text Search` `SubItem` to a real
   input, same pattern as Search by Topic's inline form.

## 2. Case Analysis (under Case Studies)

**Status:** Disabled placeholder. No backend capability exists.

**What it needs:**
- A "Case Analysis" view implies something beyond the raw judgment text
  `GET /api/cases` and `GET /api/source/{case_id}` already return today
  — e.g. the case's holding/ratio decidendi, its constitutional
  significance, which later cases cite it, or a plain-language summary.
  None of that is derived or stored anywhere right now.
- Per `Ui updates and features.md` 2.1's original framing, Case Studies'
  two sub-items ("Landmark Judgments" and "Case Analysis") were treated
  as the same content shape — but Landmark Judgments turned out to just
  need the raw text (already built), while Case Analysis is a genuinely
  different, deeper feature that was never scoped in detail.

**Open question before implementation starts:** what should "analysis"
actually contain? Options, roughly increasing in cost:
1. **Cheapest:** a static, human-written 1-2 paragraph summary per case
   (significance + holding), stored in `backend/case_law.py` alongside
   the existing metadata (e.g. a new `summary` field) — no LLM call
   needed, fully controlled/accurate content.
2. **Medium:** Gemini-generated summary at request time, grounded in the
   case's already-retrieved text (same anti-fabrication pattern as
   `backend/graph/nodes/generation.py`'s structured generation) — riskier
   since it depends on generation quality per case.
3. **Larger:** a citation graph (which cases/articles cite or are cited
   by this one) — needs new metadata and possibly new ingestion work
   beyond what's tracked in `ingestion.md`.

**Recommendation:** start with option 1 if/when this gets built — it's
the cheapest, most accurate, and reuses the existing `CASE_METADATA`
pattern with no new infrastructure. Confirm the desired content type
with the user before implementing, since none of the three has been
decided yet.
