# Known Issues

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

## Incomplete: Phase 4 responsive mobile layout not built

**Status:** Not started. Every other Phase 4 UI step (login/signup, chat interface, citations/Source Explorer, search/navigation, language selector, conversation history, feedback/sharing) is built and live-verified against the real backend — all of it is desktop-only.

**What's missing, per `instructions_refactor.md` Section 1.6:**
- Sidebar (`frontend/src/components/Sidebar.jsx`) is a fixed 256px column always rendered — no slide-out drawer / hamburger toggle for narrow viewports.
- Source Explorer (`frontend/src/components/SourceExplorer.jsx`) is a fixed 320px side panel — no bottom-sheet/full-screen fallback on citation tap for mobile.
- Quick-action chips (`frontend/src/components/TopBar.jsx`) wrap onto multiple lines on a narrow screen instead of scrolling horizontally.
- No responsive breakpoints anywhere yet — `Chat.jsx`'s `flex h-screen` three-column layout has no mobile-specific collapse to a single column.

**Why deferred rather than attempted inline:** the layout was built to the desktop mockup first per the user's own step ordering (chat interface → ... → responsive layout last); retrofitting breakpoints is a distinct, contained pass across the same few components rather than something to bolt on incrementally per-feature.

**Expected resolution:** a dedicated pass adding Tailwind responsive breakpoints (`sm:`/`md:`/`lg:`) to `Sidebar.jsx` (drawer + hamburger), `SourceExplorer.jsx` (bottom sheet below `md`), `TopBar.jsx` (horizontal-scrolling chip row), and `Chat.jsx` (single-column stacking below `md`) — no backend changes needed, this is frontend-only.
