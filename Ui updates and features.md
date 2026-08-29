# ConstituteAI — UI Design Spec Updates & Future Feature Ideas

> Companion file to `instructions_refactor.md`. This file holds two kinds
> of content, kept clearly separated:
> 1. **Ready-to-build** — a concrete visual design spec that refines/locks
>    the existing Section 1 layout with exact colors and styling. Build
>    this now, it doesn't change scope, only visual polish.
> 2. **Proposed, not yet scoped** — feature ideas raised but not approved
>    for build. Do not implement anything in Part 2 without it first being
>    promoted into `instructions_refactor.md` with a real scope decision,
>    same as multilingual/auth/Supabase were.

---

## Part 1 — UI Visual Design Spec (ready to build)

This refines `instructions_refactor.md` Section 1's layout with an exact
color palette, spacing, and component styling. It does not add new
features or change the information architecture — same sidebar (5 links +
Settings), same 3-column layout, same chat structure. This is styling
detail only.

**Visual reference confirmed:** a generated mockup image
(`Gemini_Generated_Image_66b4jn66b4jn66b4.png`) matches this spec closely
and should be treated as the authoritative visual target when building —
dark navy/charcoal (`#0B0F17`/`#111827`) background, gold/beige
(`#C5A880`→`#B39369`) accent on "New Chat," citation chips, and active
nav state, Indian State Emblem icon in the brand header, and the full
3-column layout (sidebar → chat → Source Explorer) with Fundamental Rights
shown in its active/selected state — a **filled gold-tinted background**,
not just a border accent. Build to match this image pixel-for-pixel where
the spec below doesn't specify an exact value.

### 1.1 Color palette

| Token | Hex | Usage |
|---|---|---|
| Main app background | `#0B0F17` | Base canvas |
| Sidebar / panels / cards | `#111827` | Sidebar, Source Explorer, AI response blocks |
| Borders / active states | `#1F2937` | All borders, dividers, active nav item background |
| Accent gradient | `#C5A880` → `#B39369` | Primary buttons (New Chat, Cite Source), highlighted citation tags |
| Primary heading text | `#F3F4F6` | Titles, brand wordmark |
| Body text | `#E2E8F0` / `#D1D5DB` | AI response body, general copy |
| Muted text/icons | `#9CA3AF` | Placeholder text, secondary labels |
| User message bubble | `#1F2937` bg, `#374151`/50 border | User's own chat bubble |

**Framework:** React + Tailwind CSS + Lucide React icons (already the
project's stack per Section 2 — no new dependency).

### 1.2 Sidebar (left) — styling detail

- Expanded width: `w-72`, background `#111827`, right border `#1F2937`,
  flex column
- Brand header: `h-16`, `px-5`, bottom border `#1F2937` — Indian State
  Emblem icon + "ConstituteAI" wordmark, font-semibold, tracking-wide,
  text `#F3F4F6`
- **"+ New Chat" button:** full width, `p-4` container padding, gap-2.5,
  gradient background `#C5A880` → `#B39369`, text `#0B0F17`, font-medium,
  `py-2.5 px-4`, `rounded-xl`, drop-shadow
- Nav list: `px-3 py-2` per item, `space-y-1.5` between items. Icons via
  Lucide React:
  - Search Articles → `Search` icon
  - Constitutional History → `BookOpen` icon
  - Fundamental Rights → `Scale` icon (active/highlighted state uses
    background `#1F2937` + gold accent border/text)
  - Directive Principles → `Scale` icon (or a distinct icon — confirm
    doesn't collide visually with Fundamental Rights)
  - Case Studies → `Gavel` icon
  - Settings → `Settings` icon (pinned to bottom, per Section 1.2's
    existing spec)

### 1.3 Top bar — styling detail

- `h-16`, bottom border `#1F2937`, background `#0B0F17`/80 with
  `backdrop-blur-md`, `px-6`, flex `items-center justify-between`
- Centered search input: `max-w-2xl`, `mx-auto`, background `#111827`,
  border `#1F2937`, `rounded-xl`, `pl-10 pr-4 py-2`, `text-sm`, text
  `#F3F4F6`, placeholder `#6B7280`
- Right utilities: language selector (22-language dropdown per Section 7
  of the main instructions — not just English/Hindi), Share button, user
  avatar

### 1.4 Quick-action chips sub-bar — styling detail

- `px-6 py-3`, bottom border `#1F2937`/50, background `#111827`/30, flex
  `items-center gap-2`, `overflow-x-auto`
- Pills: `Preamble`, `Fundamental Rights`, `Emergency Provisions`,
  `President of India`

### 1.5 Chat flow — styling detail

- Container: flex-1, `overflow-y-auto`, `p-6`, `space-y-6`
- **User bubble:** right-aligned, background `#1F2937`, border
  `#374151`/50, text `#F3F4F6`, `text-sm`, `rounded-2xl`
- **AI response block:** left-aligned, background `#111827`, border
  `#1F2937`, text `#E2E8F0`, `text-sm`, `rounded-2xl`, `space-y-4`:
  - Summary paragraph with inline citation tags in soft beige
    (`[Art. 368, Clause 2]` style)
  - Key Clauses box: background `#0B0F17`/60, border `#1F2937`,
    `rounded-xl`, `p-4`, bulleted
  - Footer row: "Cite Source" button — solid `#C5A880` background, text
    `#0B0F17` — plus thumbs up/down feedback icons

### 1.6 Source Explorer panel — styling detail

- Width `w-96`, background `#111827`, left border `#1F2937`, flex column,
  `shadow-2xl`
- Header: `h-16`, `px-5`, bottom border `#1F2937`, flex
  `items-center justify-between` — title "Source Explorer" + close (`X`)
- Body: `overflow-y-auto`, `p-5`, `space-y-6`:
  - Verified legal extract section — verbatim article/case text, with a
    "Pinecone RAG verified" badge/indicator
  - Landmark judgments section — metadata blocks for related case law
    (already built and live-verified per Phase 4 progress — this is
    styling only, not new functionality)

### 1.7 Icons — Lucide React mapping, and the State Emblem issue

**All UI icons use Lucide React** (already the project's icon library per
Section 2 of the main instructions doc) — no image files, no custom
assets needed for any of these:

| Location | Icon | Lucide component |
|---|---|---|
| Search Articles (nav) | Magnifying glass | `Search` |
| Constitutional History (nav) | Open book | `BookOpen` |
| Fundamental Rights (nav) | Shield | `Shield` |
| Directive Principles (nav) | Scale/balance | `Scale` |
| Case Studies (nav) | Gavel | `Gavel` |
| Settings (nav) | Gear | `Settings` |
| Top bar — Share | Share arrow | `Share2` |
| Top bar — language selector | Globe | `Globe` |
| Feedback — positive | Thumbs up | `ThumbsUp` |
| Feedback — negative | Thumbs down | `ThumbsDown` |
| "Cite Source" button | Book/link mark | `BookMarked` (or `Link`) |

**Build instruction:**
```
Add Lucide React icons throughout the UI per this table: Search
(Search Articles), BookOpen (Constitutional History), Shield
(Fundamental Rights), Scale (Directive Principles), Gavel (Case
Studies), Settings (Settings), Share2 (top bar), Globe (language
selector), ThumbsUp/ThumbsDown (feedback). For the sidebar brand
header icon, use Landmark instead of any Ashoka Emblem imagery — flag
this as a deliberate substitution for legal/licensing reasons, don't
attempt to recreate the State Emblem.
```

#### The State Emblem of India (Ashoka Lion Capital) — do not use

The reference mockup (`Gemini_Generated_Image_66b4jn66b4jn66b4.png`)
shows a lion-capital-style icon in the sidebar brand header, evoking the
official State Emblem of India (the Ashoka Lion Capital of Sarnath).

**This must not be used as an actual app logo/icon.** The State Emblem is
a protected national symbol under the **State Emblem of India
(Prohibition of Improper Use) Act, 2005** — its use, including in
commercial or product branding, is legally restricted and generally
requires government authorization. This applies even to a
constitutional-research tool where the symbol might feel thematically
appropriate; thematic relevance doesn't grant a licensing exemption.

**Brand mark decision — use one of these instead:**
1. **`Landmark` (Lucide icon)** — a classical building/institution icon,
   free, open-source, zero legal risk, fits "constitutional institution"
   branding, requires no design work since it's already in the icon
   library the project uses. **Default choice until a custom mark is
   designed.**
2. **`Scale` (Lucide icon)** — already used for Directive Principles, but
   could double as the primary brand mark if a distinct one isn't wanted
   yet.
3. **A custom, original brand mark** — e.g. an abstract combination of an
   open book + scale, or a stylized letter mark — fully safe since it
   isn't reproducing a protected symbol. Not yet designed; revisit if the
   project wants a distinct visual identity beyond a stock icon.

**Do not use:** the Ashoka Chakra alone is somewhat more common in
decorative/civic-themed apps, but still carries some of the same
sensitivity as a national symbol — treat with the same caution rather
than assuming it's automatically safe as a substitute.

**Status: use `Landmark` now. Custom mark design is optional future
work, not blocking.**

---

### 1.8 Implementation note

Nothing here changes `instructions_refactor.md` Section 1's layout or
Section 4's API contracts. This is a pure styling/Tailwind-class pass over
components already built (MessageBubble, SourceExplorer, Sidebar,
CitationChip, etc.) — safe to hand to Copilot/Claude Code as a direct
styling task against existing components.

---

## Part 2 — Proposed features (NOT yet scoped — do not build)

These were raised in discussion but are explicitly **not approved for
build**. Each needs its own scope decision, cost estimate, and — for
anything needing new source data — its own ingestion plan, before being
promoted into `instructions_refactor.md`.

### 2.1 Expandable sidebar sub-menus

**Discussion / rationale (why this is parked, not just a table):**

Right now the sidebar is 5 flat links that, per the base spec, just exist —
not wired to anything beyond basic navigation. The proposal is to make
each one expand into sub-items, and clicking any sub-item pushes relevant
content into the Source Explorer panel — turning the sidebar from
"navigation" into a browsable content library alongside the chat, reusing
the same panel that already displays citation-triggered source text.

Breaking down each one, what it actually is and how big it is:

1. **Search Articles → Search by Number / by Topic / Full-Text Search** —
   reasonable, and fairly cheap. Article metadata (article, clause, part)
   already exists in Pinecone. "Search by Number" is basically the lookup
   already supported via chat. "By Topic"/"Full-Text" is closer to a real
   search UI feature — new frontend work; backend-wise mostly reuses
   existing retrieval.
2. **Constitutional History → Timeline of Drafting / Key Debates /
   Amendments History** — this is a **new content problem, not just a UI
   problem**. Constituent Assembly debates and drafting-timeline material
   aren't in the corpus at all right now — only the Constitution text plus
   2 case-law judgments are ingested. This needs entirely new source data
   (transcripts, historical records) — a whole new ingestion effort,
   bigger than it looks from the sidebar description alone.
3. **Fundamental Rights / Directive Principles → sub-chapters** — cheapest
   of the bunch. Really just a curated static index into content already
   indexed (Articles 12–35, 36–51), presented as a browsable list instead
   of requiring a chat query. Mostly frontend + maybe a small backend
   endpoint for "articles in range X–Y."
4. **Case Studies → Landmark Judgments / Case Analysis** — directly
   extends the existing Phase 2.5 case-law work, but only 2 of 7 planned
   cases are ingested so far. Building this now would expose that
   incompleteness directly in the UI — a "browse all landmark cases" page
   with only 2 real entries looks unfinished, worse than not having the
   page at all.
5. **Settings → Account / Theme / AI Model Preferences** — standard stuff.
   "Account Details" ties into Supabase auth (real, cheap). "AI Model
   Preferences" is odd — no established product reason yet to let users
   pick between Gemini models; wasn't part of anything already built or
   planned, and raises cost/consistency/support questions that haven't
   been discussed.

**The real question before deciding anything:** this is genuinely a
large, multi-part feature — some pieces are cheap and build directly on
what exists (Fundamental Rights browsing, Search by Number), and some
pieces require entirely new data that doesn't exist yet (Constitutional
History, a fully-populated Case Studies section). Bundling all of this as
one "sidebar expansion" feature risks either scope-creeping the frontend
work indefinitely, or shipping a sidebar full of dead-end links that
expose empty/thin content.

**Decision: do not approve this as one feature.** Split it — decide
separately, per sub-item, whether it's "build now" (reuses existing
data), "build later" (needs new ingestion), or "cut" (unclear value, e.g.
AI Model Preferences). The table below reflects that per-item breakdown.



| Sidebar item | Proposed sub-items | Feasibility |
|---|---|---|
| Search Articles | Search by Number, Search by Topic, Full-Text Search | **Cheap** — Search by Number reuses existing chat retrieval. Topic/Full-Text search is a real UI feature needing new frontend work, benefits from reranking (already deferred, see main doc). |
| Fundamental Rights | Right to Equality, Right to Freedom, Right against Exploitation, Freedom of Religion, Cultural/Educational Rights, Constitutional Remedies | **Cheap** — curated static index into already-indexed Articles 12–35. Mostly frontend + a small "articles in range" backend endpoint. |
| Directive Principles | Socialist / Gandhian / Liberal-Intellectual Principles | **Cheap** — same pattern as above, Articles 36–51. |
| Case Studies | Landmark Judgments, Case Analysis | **Medium** — technically works today via existing case-law pipeline, but only 2 of 7 planned cases are ingested (Phase 2.5 pilot). Building this now would visibly expose incomplete data. **Recommend: wait until more cases are ingested.** |
| Constitutional History | Timeline of Drafting, Key Historical Debates, Amendments History | **Large — new corpus required.** No Constituent Assembly debate transcripts or drafting-history content has been sourced or ingested at all. This is a full new ingestion phase, comparable in size to Phase 2.5, not a UI task. **Do not build the UI for this until the content pipeline exists** — an empty/thin history browser is worse than no history browser. |
| Settings | Account Details, Display Theme, AI Model Preferences | **Account Details: cheap**, direct Supabase Auth extension. **Display Theme: cheap**, pure UI. **AI Model Preferences: unclear value** — no product reason established yet for letting users choose between Gemini models; raises cost/consistency/support questions that haven't been discussed. Recommend cutting unless a real use case is defined. |

**Recommendation when this gets revisited:** split into three tracks —
(1) ship the cheap wins (Fundamental Rights/Directive Principles browsing,
Search by Number, Account Details, Display Theme) as a small Phase 4
addition; (2) hold Case Studies sub-menu until Phase 2.5 case-law
ingestion is more complete; (3) treat Constitutional History as its own
future phase requiring a dedicated data-sourcing plan, not scoped here.

**Status: parked. Nothing in this section should be built until
explicitly promoted with a scope decision per item.**

---

### 2.2 Implementation steps (for when/if promoted — tier by tier)

Written now so the plan exists, but per 2.1's status, **do not execute
any of this without first moving the relevant item(s) into
`instructions_refactor.md` as an approved phase addition.**

#### Tier A — Build now (cheap, reuses existing data/endpoints)

**A1. Right to Equality / Freedom / etc. — Fundamental Rights &
Directive Principles sub-chapter browsing**

Article ranges (fixed, from the Constitution's own structure):
- Right to Equality → Articles 14–18
- Right to Freedom → Articles 19–22
- Right against Exploitation → Articles 23–24
- Freedom of Religion → Articles 25–28
- Cultural and Educational Rights → Articles 29–30
- Right to Constitutional Remedies → Article 32
- Directive Principles sub-chapters → Articles 36–51, grouped by
  Socialist / Gandhian / Liberal-Intellectual Principles (grouping
  needs to be defined — not a fixed contiguous range like the others,
  confirm the article-to-category mapping before building)

Steps:
1. Backend: add `GET /api/articles?range=14-18` (or `?category=equality`)
   — a thin wrapper querying Pinecone/Postgres by the existing `article`
   metadata field for a range or named category, reusing
   `backend/services/pinecone.py` or `backend/services/supabase.py`
   query helpers already built.
2. Backend: define the DPSP category → article-range mapping explicitly
   (Socialist/Gandhian/Liberal-Intellectual) as a small config/constant,
   since this isn't a clean numeric range like Fundamental Rights.
3. Frontend: add sub-item list under each sidebar nav item (per the
   diagram already discussed) — expand/collapse UI, `▾`/`▸` states.
4. Frontend: clicking a sub-item calls the new endpoint and renders
   results in the **existing** Source Explorer component — no new panel
   component needed, only a new content-population path into it.
5. Test: confirm each range/category returns the correct, complete set
   of articles — spot-check against the real constitutional text.

**A2. Search by Number**

1. Frontend only: add a small input + "Go" button under the "Search
   Articles" sidebar sub-item.
2. On submit, call the **existing** `GET /api/source/{source_id}`
   endpoint (already built and live-verified) with `article_<N>` as the
   ID.
3. Render result in the existing Source Explorer component.
4. No backend changes needed — this is a UI-only addition.

**A3. Account Details (Settings)**

1. Frontend: Settings page/panel showing the logged-in user's email and
   basic profile info, sourced from the existing Supabase Auth session
   (`auth.getUser()` client-side, or `GET /api/auth/me` if that's been
   built).
2. No new backend work if `/api/auth/me` already exists per Section 4 of
   the main instructions doc — confirm it does before starting.

**A4. Display Theme (Settings)**

1. Frontend only — theme toggle (likely just confirming/locking the
   existing dark palette from Part 1 of this doc, or adding a light-mode
   alternative if genuinely wanted — clarify scope before building: is
   this "confirm dark mode is the only mode" or "build a real light mode
   too"?).
2. No backend work.

#### Tier B — Build later (needs more source data or deferred work)

**B1. Search by Topic**

1. Backend: add `GET /api/search?q=<query>` — thin wrapper calling the
   existing `backend/rag/retriever.py`, unfiltered semantic search,
   returning a ranked list (article/case + score) instead of a single
   generated answer.
2. Frontend: results-list UI in the Source Explorer, each result
   clickable → fetches full text via the same path as A2.
3. **Do this only after reranking is implemented** (already deferred
   elsewhere in the project, tracked as a separate prompt) — without
   reranking, this path inherits the same conceptual-query ranking
   weakness documented in `KNOWN_ISSUES.md` (verbose case-law text
   outranking terse constitutional text). Building this before reranking
   exists means shipping a visibly weak search feature.

**B2. Case Studies (Landmark Judgments / Case Analysis)**

1. Reuses the existing case-law retrieval and `GET /api/source/{id}`
   pattern (already working for the 2 ingested cases).
2. **Do not build the browsable UI for this until more of the 7 planned
   landmark cases are ingested** (Phase 2.5 currently has 2 of 7). A
   "browse all landmark cases" page with only 2 real entries looks
   unfinished — worse than not having the page.
3. When resumed: continue Phase 2.5's existing pipeline
   (`scripts/ingest.py` → `scripts/chunk_case_law.py` →
   `scripts/index.py`) for the remaining 5 cases, following the same
   process already proven for the first 2, before wiring this UI.

#### Tier C — Needs a new phase entirely (not just "later," genuinely new scope)

**C1. Constitutional History (Timeline of Drafting, Key Debates,
Amendments History)**

This is not a UI task — it requires an entirely new content pipeline,
comparable in size to Phase 2.5:
1. Source and confirm licensing for Constituent Assembly debate
   transcripts and constitutional drafting history material (likely
   Government of India / Parliament of India archives — verify official,
   reusable sources, same diligence as was done for case law's JUDIS
   source decision).
2. Build a new ingestion/parsing pipeline for this content type — it
   won't share structure with either the constitution-article parser or
   the case-law paragraph parser; debate transcripts have their own
   format (speaker turns, dates, session numbers).
3. Define a new metadata schema (e.g. `document_type: "history"`,
   `session_date`, `speaker`, `topic`) distinct from both existing
   schemas.
4. Index into Pinecone under this new document_type.
5. Only then build the sidebar UI and Source Explorer rendering for it.

**Do not attempt to build even a placeholder UI for this before the
content pipeline exists** — same principle as Case Studies (2.B2), but
more severe here since there's currently zero content, not partial
content.

**C2. AI Model Preferences (Settings)**

Not recommended for implementation as currently proposed — no defined
product reason exists for letting users choose between Gemini models.
Before any implementation steps are written for this, first answer:
what problem does this solve for the user? (cost control? response
speed vs. quality tradeoff? something else?) If a real reason emerges,
this becomes a small, cheap feature (a dropdown + a
`preferred_model` field on the user profile, read by
`backend/graph/nodes/generation.py`). Until then, this stays cut.