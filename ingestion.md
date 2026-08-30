# Case-law ingestion — pending work

> Tracks the remaining case-law ingestion for the cases listed in
> `backend/case_law.py`'s `PENDING_CASE_METADATA`. Nothing here is
> ingested yet — this file exists so the work is easy to pick back up
> once source text is available, without re-deriving the plan from
> scratch.

## Status

**Blocked on source text.** No PDFs or extracted text exist for any of
the 10 pending cases (`data/raw/case_law/` only has the 2 already-
ingested cases: `maneka_gandhi_1978.pdf`, `shreya_singhal_2015.pdf`).
Indian Kanoon API access has been applied for but not yet granted (see
`KNOWN_ISSUES.md`'s deferred Phase 2.5 entry) — until then, sourcing is
manual per case, same as the first 2.

## Cases pending (from `backend/case_law.py`)

| case_id | Case | Year | Related articles | Notes |
|---|---|---|---|---|
| `kesavananda_bharati_1973` | Kesavananda Bharati v. State of Kerala | 1973 | 368, 13, 19, 31 | Basic structure doctrine |
| `golaknath_1967` | I.C. Golaknath v. State of Punjab | 1967 | 368, 13 | |
| `minerva_mills_1980` | Minerva Mills v. Union of India | 1980 | 368, 31C | |
| `sr_bommai_1994` | S.R. Bommai v. Union of India | 1994 | 356 | |
| `puttaswamy_2017` | K.S. Puttaswamy v. Union of India | 2017 | 21 | Right to privacy |
| `in_re_article_370_2023` | In Re: Article 370 of the Constitution | 2023 | 370, 356 | Verify exact case title/citation before indexing |
| `adr_v_election_commission_2024` | Association for Democratic Reforms v. Union of India | 2024 | 19 | Electoral bonds case — verify exact title/citation |
| `state_of_punjab_v_davinder_singh_2024` | State of Punjab v. Davinder Singh | 2024 | 341, 342, 15, 16 | SC/ST sub-classification — verify before indexing |
| `property_owners_association_2024` | Property Owners Association v. State of Maharashtra | 2024 | 39, 31C | Verify exact title/citation |
| `pooja_ramesh_singh_v_jk_bank_2026` | Pooja Ramesh Singh v. Jammu and Kashmir Bank Ltd. & Anr. | 2026 | (none) | Citation: 2026 INSC 668. AI-hallucinated-precedents ruling — not a fundamental rights case, `related_articles` intentionally empty |

## Ingestion pipeline (unchanged, already proven on the first 2 cases)

For each case, once source text is in hand:

1. Save the source PDF/text into `data/raw/case_law/<case_id>.pdf` (or
   `.txt`) — filename stem must match the `case_id` key in
   `backend/case_law.py`.
2. Run `scripts/ingest.py` to extract text into
   `data/processed/case_law/<case_id>.txt`.
3. Run `scripts/chunk_case_law.py` to chunk by paragraph number (falls
   back to fixed windows if the judgment isn't cleanly numbered) and
   write `data/processed/chunks/case_law/<case_id>.jsonl` +
   `data/processed/metadata/case_law/<case_id>.jsonl`. This reads case
   metadata from `backend/case_law.py`'s `CASE_METADATA` — the entry
   must already be moved there from `PENDING_CASE_METADATA` before this
   step (see below).
4. Run `scripts/index.py` to embed and upsert into Pinecone under
   `document_type: "case_law"`.
5. Spot-check retrieval: query the case by name and by a related article
   number, confirm it comes back with a sensible top-K hit.
6. Move the case's entry from `PENDING_CASE_METADATA` to
   `CASE_METADATA` in `backend/case_law.py` **only after step 5
   confirms it's actually live** — `backend/case_law.py`'s own docstring
   warns that a `CASE_METADATA` entry with no indexed content silently
   breaks the Source Explorer's related-cases reverse lookup.
7. Add at least one benchmark question to
   `data/evaluation/questions.json` for the newly-ingested case (per
   `KNOWN_ISSUES.md`'s eval-coverage note).

## Notes on the specific list

- Several 2023–2026 cases are flagged "verify exact case title/citation
  before indexing" — these are recent enough that the metadata above was
  entered from memory/discussion, not confirmed against an official
  source. Confirm the citation is real and correctly identified before
  spending time sourcing/ingesting it.
- `pooja_ramesh_singh_v_jk_bank_2026`'s note ("AI hallucinated
  precedents ruling") suggests this case is itself *about* an AI
  generating fake citations — worth double-checking relevance/framing
  before ingesting, not just treating it as a standard landmark
  judgment.
- Where an official SCI JUDIS PDF exists for a case, prefer it as the
  source (same reasoning as the first 2 cases) — Indian Kanoon (once API
  access is granted) is the fetch mechanism, not a replacement for
  citing the canonical source per `KNOWN_ISSUES.md`.
