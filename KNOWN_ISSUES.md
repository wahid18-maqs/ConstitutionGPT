# Known Issues

## Known Issue: Conceptual queries can be out-ranked by verbose case-law text

**Symptom:** Queries phrased without an explicit article number (e.g. "What freedom protects a person's ability to speak and express opinions?" instead of "What is Article 19?") can retrieve case-law judgment text instead of the correct, terse constitutional article text, even when the correct article exists in the index under proper metadata.

**Root cause:** Pure vector similarity favors long, lexically-dense case-law prose (which discusses a topic extensively) over short, authoritative constitutional clauses (which state it tersely). This is a structural property of semantic search, not a chunking, metadata, or filter bug — confirmed via direct investigation of q24 (Article 19) in the benchmark set.

**Status:** Deferred, not a blocker for current phase.

**Expected resolution path:**
- (a) Reranking — a cross-encoder rerank pass over top candidates, planned as a near-term follow-up, should correct for this by judging actual relevance rather than raw embedding similarity.
- (b) Phase 3 LangGraph intent-based document_type routing (scaffolded in backend/graph/nodes/metadata.py but not yet wired into retrieval) — biasing toward document_type=constitution for general/conceptual queries may also mitigate this.

**Do not attempt a standalone fix** until (a) or (b) is implemented — a point-fix now would likely be discarded once the proper architecture lands.

**Affected benchmark case:** q24 in data/evaluation/questions.json (Article 19), 0% recall in both constitution-v2 and constitution-v3 — unrelated to the schedule/chunking fix that resolved q17/q25.

## Incomplete: Phase 2.5 case-law ingestion is a pilot, not the full corpus

**Status:** Pilot complete and verified (pipeline built, indexed, live-retrieval-tested); the remaining scope from `instructions_refactor.md` Section "Phase 2.5" is not done.

**What's done:**
- Ingestion/chunking/indexing pipeline for case law (`scripts/ingest.py` boilerplate stripping, `scripts/chunk_case_law.py` paragraph-boundary chunking, case-law metadata schema, `scripts/index.py` reused unchanged).
- 2 of the 7 landmark cases named in the product spec ingested and indexed under `document_type: case_law`: **Maneka Gandhi v. Union of India (1978)** and **Shreya Singhal v. Union of India (2015)**, sourced from official/public-domain SC judgment text.
- Retrieval verified live: both cases correctly retrievable, citations correctly wired (`backend/graph/nodes/citations.py`), 75% recall/precision on the 4 case-law benchmark questions.

**What's remaining:**
- **5 of 7 spec-named landmark cases are not yet ingested**: Kesavananda Bharati v. State of Kerala, Minerva Mills v. Union of India, I.C. Golaknath v. State of Punjab, S.R. Bommai v. Union of India, K.S. Puttaswamy v. Union of India. These were deliberately deferred (some run 500+ pages) to keep the pilot scoped — the same pipeline (`scripts/ingest.py` → `scripts/chunk_case_law.py` → `scripts/index.py`) is rerunnable to add them incrementally; each new case only needs its source PDF placed in `data/raw/case_law/` and an entry added to `CASE_METADATA` in `scripts/chunk_case_law.py`.
- **The "case law not yet available" placeholder guard (instructions_refactor.md non-negotiable #6) is not implemented.** Today, asking about an unindexed case (e.g. "Explain Kesavananda Bharati") is correctly classified as `case_law` intent and correctly does *not* fabricate an answer about that case — but it also doesn't say "not yet available"; it silently falls back to whatever *is* indexed (currently only Maneka Gandhi/Shreya Singhal content), which could read as a non-sequitur to a user rather than a clear "we don't have this yet." This guard belongs to the Phase 3 intent router / Phase 4 Source Explorer per the original plan, since no case-law-specific route or UI panel exists yet to attach it to — implement it when those land, not as a standalone patch now.
- Case-law-specific evaluation coverage is thin: only 4 benchmark questions (`data/evaluation/questions.json`, q29–q32), both against the same 2 ingested cases. Should grow alongside each newly-ingested case.
