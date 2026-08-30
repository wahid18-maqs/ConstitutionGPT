# Known Issues

## Deferred (not blocking): Phase 2.5 case-law ingestion is a pilot, not the full corpus

**Status:** Pilot complete and verified (pipeline built, indexed, live-retrieval-tested) and considered sufficient for now. Expanding beyond the pilot's 2 cases via the Indian Kanoon fetch integration below is intentionally deferred indefinitely — not scheduled — since the pilot already meets the product's working bar. Revisit only if there's a concrete need for broader case-law coverage.

**Sourcing strategy revised:** Case law is now an open-ended, continuously growing list, not a fixed 7-case target. Ingestion is therefore moving from manual PDF hunting to an API-driven fetch step feeding the existing pipeline unchanged.

## What's done

* Ingestion/chunking/indexing pipeline for case law:

  * `scripts/ingest.py` — boilerplate stripping
  * `scripts/chunk_case_law.py` — paragraph-boundary chunking
  * Case-law metadata schema
  * `scripts/index.py` — reused unchanged
* 2 cases ingested and indexed under `document_type: case_law`:

  * **Maneka Gandhi v. Union of India (1978)**
  * **Shreya Singhal v. Union of India (2015)**
* Both cases were sourced from official/public-domain SC judgment text (SCI JUDIS PDFs).
* Live retrieval verified: both cases are correctly retrievable.
* Citations are correctly wired through `backend/graph/nodes/citations.py`.
* Case-law benchmark currently reports **100% recall / 100% precision** after the graph fix. The earlier 75%/75% result is superseded; see `KNOWN_ISSUES.md` for the post-fix benchmark numbers.

## Sourcing strategy — revised

The landmark-case list is no longer fixed at 7. It is an open, growing set spanning multiple eras, including recent (2023–2026) judgments that don't reliably exist as standalone SCI JUDIS PDFs yet.

### Foundational

* Kesavananda Bharati (1973)
* Golaknath (1967)
* Minerva Mills (1980)
* S.R. Bommai (1994)
* K.S. Puttaswamy (2017)

### Modern Constitutional

* In Re: Article 370 (2023)
* ADR v. Election Commission (2024)
* State of Punjab v. Davinder Singh (2024)
* Property Owners Association (2024)

### AI / Legal-AI

* Pooja Ramesh Singh v. J&K Bank (2026)

A one-time manual SCI-PDF hunt per case doesn't scale against a list that keeps growing. Each new landmark judgment, especially recent ones, would otherwise require repeating the same manual sourcing effort indefinitely.

## Decision

Use the **Indian Kanoon API** as the *fetch mechanism only*, not as a replacement for the existing pipeline or citation standards.

1. Indian Kanoon's search/document API locates and fetches judgment text, solving the scaling problem of manually sourcing each case, especially recent judgments that are not yet cleanly available as SCI PDFs.

2. Fetched text feeds into the **existing, unchanged** pipeline:

   ```text
   Indian Kanoon API
          ↓
   Case-law fetch
          ↓
   scripts/chunk_case_law.py
          ↓
   scripts/index.py
          ↓
   Pinecone
   ```

   No changes are needed to the parsing, chunking, metadata schema, or indexing logic already proven on the first two cases.

3. **"Powered by IKanoon" attribution**, required by their API terms for RAG use, will be added once, prominently, in the app's About/Sources section rather than per result, consistent with the terms' expectations.

4. **Apply for Indian Kanoon's non-commercial API verification early.** The stated ₹10,000/month free credit is preferable to the ₹0.50/request pay-as-you-go rate if approved. Apply now rather than after building the pipeline around the API, since approval timing is unknown.

5. **Where an official SCI JUDIS PDF exists for a case, continue to prefer citing/linking it as the canonical source** in the app's citations. Indian Kanoon is the fetch mechanism; SCI remains the source of record where available. This preserves the existing authority/copyright rationale rather than fully substituting Indian Kanoon for the official source.

## What's remaining

### 1. Indian Kanoon fetch integration

None of the foundational, modern, or AI/legal-AI cases listed above are yet ingested.

The next step is building the Indian Kanoon fetch integration:

* `search_case_law()`
* `get_case()`

This is **not** a replacement for the existing ingestion pipeline.

The downstream pipeline remains unchanged and rerunnable:

```text
API fetch
   ↓
scripts/chunk_case_law.py
   ↓
scripts/index.py
   ↓
Pinecone
```

Each new case should still only require an entry in `CASE_METADATA` in `scripts/chunk_case_law.py`.

### 2. "Case law not yet available" placeholder guard

The **"case law not yet available" placeholder guard** from `instructions_refactor.md` non-negotiable #6 is not implemented.

Currently, asking about an unindexed case, for example:

> "Explain Kesavananda Bharati"

is correctly classified as `case_law` intent and does not fabricate an answer about that case.

However, it also does not explicitly say:

> "This case is not yet available."

Instead, it silently falls back to whatever case law *is* indexed. This could appear as a non-sequitur to the user rather than a clear availability message.

This guard belongs to the **Phase 3 intent router / Phase 4 Source Explorer** from the original plan because there is currently no dedicated case-law route or UI panel to attach it to.

Therefore, implement it when those components land rather than as a standalone patch now.

Once the Indian Kanoon fetch tool exists, the guard should distinguish between:

* **Not indexed but fetchable on demand**
* **Not available at all**

This is a design decision to resolve alongside the guard rather than before the fetch integration.

### 3. Case-law evaluation coverage

Case-law-specific evaluation coverage is currently thin:

* Only 4 benchmark questions exist in `data/evaluation/questions.json`.
* These are `q29–q32`.
* All four currently test against the same two ingested cases.

Coverage should grow alongside each newly ingested case.

At minimum, add one evaluation question for each newly added tier:

* **Foundational**
* **Modern Constitutional**
* **AI / Legal-AI**

once cases from those tiers are ingested.


## Incomplete: Phase 4 responsive mobile layout not built

**Status:** Not started. Every other Phase 4 UI step (login/signup, chat interface, citations/Source Explorer, search/navigation, language selector, conversation history, feedback/sharing) is built and live-verified against the real backend — all of it is desktop-only.

**What's missing, per `instructions_refactor.md` Section 1.6:**
- Sidebar (`frontend/src/components/Sidebar.jsx`) is a fixed 256px column always rendered — no slide-out drawer / hamburger toggle for narrow viewports.
- Source Explorer (`frontend/src/components/SourceExplorer.jsx`) is a fixed 320px side panel — no bottom-sheet/full-screen fallback on citation tap for mobile.
- Quick-action chips (`frontend/src/components/TopBar.jsx`) wrap onto multiple lines on a narrow screen instead of scrolling horizontally.
- No responsive breakpoints anywhere yet — `Chat.jsx`'s `flex h-screen` three-column layout has no mobile-specific collapse to a single column.

**Why deferred rather than attempted inline:** the layout was built to the desktop mockup first per the user's own step ordering (chat interface → ... → responsive layout last); retrofitting breakpoints is a distinct, contained pass across the same few components rather than something to bolt on incrementally per-feature.

**Expected resolution:** a dedicated pass adding Tailwind responsive breakpoints (`sm:`/`md:`/`lg:`) to `Sidebar.jsx` (drawer + hamburger), `SourceExplorer.jsx` (bottom sheet below `md`), `TopBar.jsx` (horizontal-scrolling chip row), and `Chat.jsx` (single-column stacking below `md`) — no backend changes needed, this is frontend-only.
