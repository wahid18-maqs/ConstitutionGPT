# ConstituteAI — Refactor & Build Instructions (for GitHub Copilot)

> This file is the single source of truth for refactoring **ConstitutionGPT** into
> **ConstituteAI** — a citation-grounded Constitutional AI research assistant.
> Follow this document top to bottom. Do not skip ahead to UI polish before the
> backend contracts in Section 4 are implemented — the frontend depends on them.

---

## 0. Product Identity

- **Product name:** ConstituteAI
- **Tagline concept:** Constitutional research assistant with traceable citations
- **Brand color:** Navy/indigo primary (`#1E3A8A`-ish), off-white/cream background,
  warm accent (amber/gold, used on "New Chat" button in mockup)
- **Tone:** Professional, legal-research-grade, not a casual chatbot

---

## 1. Reference UI (source of truth for layout)

A mockup image (`1786991936055.png`) defines the target layout. Build to match
this structure exactly — do not invent alternate layouts.

### 1.1 Desktop layout (three-column)

```
┌────────────┬──────────────────────────────────────┬──────────────────┐
│  SIDEBAR   │              MAIN CHAT                │  SOURCE EXPLORER │
│  (fixed)   │              (fluid)                  │  (collapsible)   │
└────────────┴──────────────────────────────────────┴──────────────────┘
```

- Sidebar: fixed width (~260px), navy background, white text
- Main chat: fluid width, cream/white background
- Source Explorer: fixed width (~320px), opens on citation click, closable
  via `X` button top-right of panel — collapses main chat to two columns
  when closed

### 1.2 Sidebar (left)

Top to bottom:
1. Logo + "ConstituteAI" wordmark + hamburger/collapse icon
2. **"+ New Chat"** button — pill-shaped, amber/gold accent, sits visually
   apart from nav list below it
3. Nav list (icon + label each):
   - Search Articles
   - Constitutional History
   - Fundamental Rights
   - Directive Principles
   - Case Studies
4. Spacer
5. Settings (pinned to bottom)

### 1.3 Top bar (main chat header)

- Universal search input, full width, placeholder:
  `Ask about Articles, Schedules, or Amendments...`
- Below the search bar: horizontal row of **Quick Action chips**
  (pill buttons): `Preamble`, `Fundamental Rights`, `Emergency Provisions`,
  `President of India`
- Top-right cluster: `Share` button (icon + label), user avatar, and a
  **language selector** dropdown — supports all 22 languages of the Eighth
  Schedule (see Section 7), not just English/Hindi. Default label shows
  current language (e.g. `English`), dropdown lists all 22 in native script.

### 1.4 Chat message area

- User messages: right-aligned, navy bubble, white text
- AI messages: left-aligned, no bubble (flows in page), structured as:
  1. Optional **"Summary:"** line (short answer, 1–2 sentences)
  2. Section headers matching the cited article/topic (e.g. **Article 368**)
  3. Body text with **inline citation chips** — small pill/badge inline
     with text, e.g. `[Art. 368, Clause 2]` — clickable, opens Source
     Explorer scoped to that citation
  4. **Key Clauses** section as a bullet list, each bullet may also carry
     an inline citation chip
  5. **Explanation** section — plain-language gloss of the legal text
  6. Footer row: `Cite Source` button (left) + thumbs up/down feedback
     icons (right)

### 1.5 Source Explorer panel (right)

- Header: article/citation label (e.g. "Article 368") + close (`X`)
- Body, stacked cards:
  - Retrieved question/context recap
  - Primary source text block (the actual constitutional clause)
  - **Landmark Supreme Court judgments** — list of related case
    references, each a short card (case name + 1–2 line summary)
- Scrollable independently of main chat

### 1.6 Mobile layout (from mockup's phone frame)

- Single column, full width
- Sidebar becomes a slide-out drawer (hamburger-triggered), not shown by
  default
- Source Explorer becomes a bottom sheet or full-screen modal on citation
  tap, not a persistent side panel
- Quick action chips scroll horizontally
- Input bar pinned to bottom with send button

---

## 2. Tech Stack (confirmed — do not substitute without discussion)

| Layer | Choice |
|---|---|
| Frontend | React + Vite, JavaScript (or TS if Copilot defaults to it) |
| Styling | Tailwind CSS (utility classes only, matches dark-navy/cream palette) |
| Backend | FastAPI + Pydantic |
| Orchestration | LangGraph |
| LLM | Gemini (via `langchain-google-genai`) |
| Vector DB | Pinecone (metadata-aware) — replaces existing FAISS index |
| Persistence + Auth | **Supabase** — Postgres (users, conversations, messages, citations, feedback, share links) + Supabase Auth (email/password + OAuth) + Row Level Security for per-user data isolation |
| Deployment | Vercel (frontend), backend TBD (Vercel supports FastAPI natively via serverless Python Functions, but see note below), Supabase Cloud |

> **Backend deployment note:** Vercel officially supports FastAPI as ASGI
> via Vercel Functions, so it's a real option, not ruled out. However it's
> serverless/stateless with a function timeout — Phase 3's LangGraph
> conditional retrieval loop (retrieve → evaluate → rewrite → re-retrieve)
> can run long on weak-context queries, and cold starts add latency on a
> chat UI. Before Phase 5, explicitly decide: deploy backend on Vercel
> Functions, or on a platform built for long-lived processes (Fly.io,
> Render, Railway, a VPS). Don't assume Vercel-for-backend by default just
> because the frontend is there — test actual LangGraph request latency
> first and pick based on real numbers.

> **Note:** MongoDB is no longer part of this project. Do not add `motor`,
> `pymongo`, or any Mongo-related service — persistence is Postgres via
> Supabase, using its client SDK (`supabase-py` on the backend,
> `@supabase/supabase-js` on the frontend) plus SQL migrations in
> `supabase/migrations/`.

---

## 3. Repository Structure (target — build incrementally, see Section 9 phases)

```
constitution-ai/
│
├── backend/
│   ├── api/
│   │   ├── routes/
│   │   │   ├── auth.py
│   │   │   ├── chat.py
│   │   │   ├── search.py
│   │   │   ├── sources.py
│   │   │   ├── articles.py
│   │   │   ├── cases.py
│   │   │   ├── feedback.py
│   │   │   └── share.py
│   │   │
│   │   └── dependencies.py
│   │
│   ├── graph/
│   │   ├── state.py
│   │   ├── workflow.py
│   │   └── nodes/
│   │       ├── analyzer.py
│   │       ├── router.py
│   │       ├── metadata.py
│   │       ├── retrieval.py
│   │       ├── evaluation.py
│   │       ├── generation.py
│   │       └── citations.py
│   │
│   ├── rag/
│   │   ├── embeddings.py
│   │   ├── retriever.py
│   │   ├── reranker.py
│   │   ├── context.py
│   │   └── prompts.py
│   │
│   ├── services/
│   │   ├── pinecone.py
│   │   ├── gemini.py
│   │   ├── supabase.py
│   │   ├── auth_service.py
│   │   └── source_service.py
│   │
│   ├── models/
│   │   ├── chat.py
│   │   ├── source.py
│   │   ├── feedback.py
│   │   └── user.py
│   │
│   ├── config.py
│   ├── main.py
│   ├── requirements.txt
│   └── .env
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Chat/
│   │   │   ├── Sidebar/
│   │   │   ├── SourceExplorer/
│   │   │   ├── Citation/
│   │   │   ├── SearchBar/
│   │   │   └── QuickActions/
│   │   │
│   │   ├── pages/
│   │   │   ├── Chat.jsx
│   │   │   ├── Search.jsx
│   │   │   ├── History.jsx
│   │   │   ├── Cases.jsx
│   │   │   └── Settings.jsx
│   │   │
│   │   ├── services/
│   │   │   ├── api.js
│   │   │   └── supabase.js
│   │   │
│   │   ├── hooks/
│   │   ├── context/
│   │   ├── utils/
│   │   ├── App.jsx
│   │   └── main.jsx
│   │
│   ├── package.json
│   ├── vite.config.js
│   └── .env
│
├── supabase/
│   ├── migrations/
│   │   ├── 001_initial_schema.sql
│   │   ├── 002_chat.sql
│   │   ├── 003_citations.sql
│   │   └── 004_feedback.sql
│   │
│   └── seed.sql
│
├── data/
│   ├── raw/
│   │   ├── constitution/
│   │   │   └── constitution_of_india.pdf
│   │   ├── amendments/
│   │   └── case_law/
│   │
│   ├── processed/
│   │   ├── chunks/
│   │   └── metadata/
│   │
│   └── evaluation/
│       └── questions.json
│
├── scripts/
│   ├── ingest.py
│   ├── chunk.py
│   └── index.py
│
├── tests/
│   ├── backend/
│   └── rag/
│
├── README.md
└── .gitignore
```

- `backend/services/supabase.py` — initializes the Supabase client (using
  the **service role key**, server-side only, never exposed to frontend)
  and exposes query helpers used by the route handlers.
- `frontend/src/services/supabase.js` — initializes the Supabase client
  using the **anon/public key**, used for client-side auth (`signUp`,
  `signInWithPassword`, `signOut`, `onAuthStateChange`) and any
  RLS-protected direct reads the frontend does without going through
  FastAPI.
- `supabase/migrations/*.sql` are the source of truth for schema — do not
  create tables ad hoc through the Supabase dashboard; every schema change
  goes through a numbered migration file, in order, so the schema is
  reproducible.
- `tests/backend/` covers API routes and auth; `tests/rag/` covers
  retrieval/graph nodes (recall/precision, citation correctness — see
  Section 9 Phase 5).

### 3.1 `data/` — local only, not committed

`data/` is where all PDFs, extracted text, chunked output, and evaluation
sets live locally. **The entire `data/` directory is gitignored** — nothing
under it is committed, including the PDFs.

```
data/
├── raw/
│   ├── constitution/
│   │   └── constitution_of_india.pdf
│   ├── amendments/
│   └── case_law/          ← Phase 2.5 judgment source files land here
│
├── processed/
│   ├── chunks/             ← chunked text ready for embedding
│   └── metadata/           ← per-chunk metadata (Section 5 schema) before upsert
│
└── evaluation/
    └── questions.json      ← benchmark dataset (Section 9 Phase 5)
```

- **Do not** rely on committed `.gitkeep` files to make this structure
  visible on GitHub. Document the convention in `README.md` instead, and
  have `scripts/ingest.py` / `scripts/chunk.py` create any missing
  subdirectories at runtime (`os.makedirs(path, exist_ok=True)`) so a fresh
  clone works without manual directory setup.
- `scripts/ingest.py` — reads `data/raw/**`, extracts text (this replaces
  the old `pdf.py`/`pdf.ipynb` prototype), writes to `data/processed/`.
- `scripts/chunk.py` — chunks processed text, attaches metadata per the
  Section 5 schema, writes to `data/processed/chunks/` and
  `data/processed/metadata/`.
- `scripts/index.py` — embeds chunks and upserts into Pinecone.
- These three scripts are the production version of what `pdf.ipynb` and
  `constituition.ipynb` did ad hoc — the notebooks can stay as exploration
  artifacts, but the ingestion pipeline Copilot builds should be scripted
  and re-runnable, not notebook-only.

### 3.2 `.gitignore` (baseline)

```gitignore
# Environment variables
.env
.env.*
!.env.example

# Application data
data/

# Python
__pycache__/
*.py[cod]
.venv/
venv/

# Node
node_modules/
dist/

# IDE
.vscode/
.idea/

# Logs
*.log
```

---

## 4. API Contracts (implement these exactly — frontend is built against them)

### `POST /api/auth/signup`
Request:
```json
{ "email": "user@example.com", "password": "..." }
```
Response:
```json
{ "user_id": "u_123", "access_token": "...", "token_type": "bearer" }
```

### `POST /api/auth/login`
Request:
```json
{ "email": "user@example.com", "password": "..." }
```
Response:
```json
{ "access_token": "...", "token_type": "bearer", "expires_in": 3600 }
```

### `POST /api/auth/logout`
- Invalidates the current session/refresh token server-side (blacklist or
  short-lived JWT + refresh-token revocation — pick one, document the
  choice in `auth_service.py`).
- Response: `204 No Content`

### `GET /api/auth/me`
- Returns the current authenticated user's profile from the bearer token.
- All `/api/chat`, `/api/history`, `/api/feedback`, `/api/share` routes
  require a valid bearer token going forward — see Section 8.

### `POST /api/chat`
Request:
```json
{
  "message": "What are the limits on Parliament's power to amend the Constitution?",
  "language": "en",
  "conversation_id": "abc123"
}
```
> `language` accepts any of the 22 Eighth Schedule language codes (see
> Section 7), not just `"en"`/`"hi"`. Validate against that fixed list in
> the Pydantic model — reject unsupported codes with a clear error rather
> than silently falling back to English.
Response:
```json
{
  "message_id": "msg123",
  "answer": "Parliament's amending power is subject to the basic structure doctrine...",
  "citations": [
    { "source_id": "article_368", "label": "Article 368" },
    { "source_id": "kesavananda_bharati_1973", "label": "Kesavananda Bharati" }
  ]
}
```
> `conversation_id` is required — chat history MUST be scoped per conversation,
> never a global in-memory list (this was a real bug in the original
> ConstitutionGPT `main.py`; do not reintroduce it). With auth in place
> (Section 8), conversations are also scoped to the authenticated
> `user_id` — a conversation_id must belong to the requesting user or the
> endpoint returns `403`.

### Other endpoints
```
POST /api/search
GET  /api/source/{source_id}
GET  /api/article/{article_number}
GET  /api/case/{case_id}
GET  /api/history?conversation_id=...
POST /api/feedback
POST /api/share
GET  /api/share/{share_id}
```

`GET /api/source/{source_id}` powers the Source Explorer panel — must return
article number, clause, original text, document, page, source type, related
provisions, and related cases (see metadata schema below).

---

## 5. Metadata Schema (for Pinecone ingestion)

Constitutional text chunks:
```json
{
  "article": "368",
  "clause": "2",
  "part": "XX",
  "schedule": null,
  "amendment": null,
  "category": "amendment",
  "document_type": "constitution",
  "source_type": "constitutional_text",
  "language": "english",
  "page": 142
}
```

Case-law chunks:
```json
{
  "case_name": "Kesavananda Bharati v. State of Kerala",
  "year": 1973,
  "court": "Supreme Court of India",
  "category": "constitutional_law",
  "document_type": "case_law",
  "language": "english"
}
```

Retrieval must combine metadata filter + semantic top-K, e.g.:
```python
filter = {
    "article": {"$eq": "368"},
    "document_type": {"$eq": "constitution"}
}
```

---

## 6. LangGraph Workflow

```
START
  → Query Analyzer
  → Intent Router
  → Metadata Builder
  → Pinecone Retrieval
  → Context Evaluation
      ├── Good → Answer Generation
      └── Weak → Query Rewrite → Re-retrieval → Context Evaluation (loop once, then force-generate)
  → Citation Builder
  → END
```

Intent routing targets (query type → retrieval strategy):
- Article Query (`"What is Article 21?"`) → constitutional article retrieval
- Amendment Query (`"How can the Constitution be amended?"`) → Article 368 +
  amendment retrieval
- Case Law Query (`"Explain Kesavananda Bharati."`) → case-law retrieval
- History Query (`"When was the Constitution adopted?"`) → constitutional
  history retrieval
- General Query → text + case-law retrieval

**Efficiency constraint:** Query Analyzer + Metadata Builder should be a
single structured-output LLM call where possible, not two separate LLM
round-trips — the point of this refactor is fewer unnecessary LLM calls, not
more graph nodes for their own sake.

**Generation constraints (system prompt for Gemini node):**
- Ground every claim in retrieved context
- Never fabricate a citation
- Distinguish constitutional text from case-law interpretation
- State explicitly when context is insufficient to answer
- Include a visible disclaimer that this is a research aid, not legal advice

---

## 7. Multilingual Support (Eighth Schedule — 22 languages)

ConstituteAI supports all 22 languages constitutionally recognized in the
Eighth Schedule, not just English/Hindi. This is a distinguishing feature —
treat it as first-class, not a UI afterthought.

### 9.1 Supported languages

Assamese, Bengali, Bodo, Dogri, Gujarati, Hindi, Kannada, Kashmiri, Konkani,
Maithili, Malayalam, Manipuri, Marathi, Nepali, Odia, Punjabi, Sanskrit,
Santali, Sindhi, Tamil, Telugu, Urdu — plus English as the default/fallback.

Dropdown must render each language in its own native script (e.g. `हिन्दी`,
`বাংলা`, `தமிழ்`), not transliterated.

### 9.2 Architecture principle — do not translate the source text

Do **not** translate or re-embed the constitutional source text into 22
languages. That compounds translation errors into retrieval and multiplies
the corpus 22x for no accuracy benefit. Instead:

1. Retrieve the authoritative English source (constitutional text / case
   law) as normal, language-independent.
2. Generate the **explanation** in the user's selected language.
3. Keep article/clause identifiers and citation labels language-independent
   (e.g. always "Article 21", never translated).

Example: a Tamil-language question about Article 21 retrieves the
authoritative English Article 21 text, and Gemini generates the explanation
in Tamil while citing the untranslated source.

### 9.3 LangGraph state

`language` is part of graph state, threaded through every node:

```python
class GraphState(TypedDict):
    query: str
    language: str          # e.g. "ta", "hi", "en"
    intent: str
    metadata_filter: dict
    retrieved_documents: list
    context: str
    answer: str
    citations: list
```

Updated workflow (supersedes the language-agnostic version in Section 6 —
language selection happens immediately after the query arrives):

```
User Query
  → Language Selection (from request, defaults to "en")
  → Query Analyzer (multilingual query understanding)
  → Intent Router
  → Metadata Builder
  → Pinecone Retrieval (retrieval stays language-independent — English source)
  → Context Evaluation
  → Answer Generation (generate in selected language)
  → Citation Builder (labels stay language-independent)
  → END
```

### 9.4 Requirements checklist

- [ ] Add 22-language selector (native script labels) to the language
      dropdown in Section 1.3
- [ ] Store selected language in conversation/graph state, not just a UI
      toggle
- [ ] Support multilingual query understanding (query may arrive in any of
      the 22 languages)
- [ ] Retrieval stays on the authoritative English/original-language source
      — do not fork the vector index per language
- [ ] Generate responses in the selected language
- [ ] Preserve authoritative source citations, always in original form
- [ ] Keep article/clause identifiers language-independent across all 22
      languages
- [ ] Test retrieval quality is unaffected by query language
- [ ] Test answer quality across a representative sample of the 22
      languages (do not assume uniform LLM quality across all of them —
      Gemini's fluency varies by language, spot-check the lower-resource
      ones like Dogri, Bodo, Santali)
- [ ] Provide English fallback when generation quality or confidence in a
      requested language is low

---

## 8. Auth & Persistence (Supabase)

Login/logout and persistence are in scope, built entirely on **Supabase**
(Postgres + Supabase Auth + Row Level Security) — not a custom JWT
implementation and not MongoDB.

### 8.1 Why

- `/api/feedback`, `/api/share`, and `/api/history` are defined in Section 4
  but have nowhere to persist data without a database — right now they'd
  only work in-memory (lost on restart).
- Persistent per-user chat history across sessions requires knowing who the
  user is, which requires auth.
- Supabase gives us Postgres + Auth + RLS in one managed service, so the
  backend doesn't need to hand-roll password hashing, token issuance, or
  refresh-token rotation — Supabase Auth handles it.

### 8.2 Auth model

- **Supabase Auth** handles signup/login/logout/session refresh — do not
  build a custom JWT/bcrypt auth flow. `backend/services/auth_service.py`
  wraps Supabase Auth calls; it does not implement its own token issuance.
- Email/password to start. Supabase Auth supports OAuth providers (Google)
  as a later addition — not required for v1, don't scope-creep into it
  unless explicitly asked.
- Frontend (`frontend/src/services/supabase.js`, anon key) calls
  `supabase.auth.signUp`, `signInWithPassword`, `signOut`, and subscribes
  to `onAuthStateChange` directly — the frontend talks to Supabase Auth
  itself rather than proxying every auth call through FastAPI.
- Every request from frontend to FastAPI attaches the Supabase session's
  access token: `Authorization: Bearer <supabase_access_token>`.
- Backend (`backend/services/supabase.py`, **service role key**, never
  shipped to the frontend) validates that token on protected routes via a
  `get_current_user` dependency in `api/dependencies.py`, which calls
  Supabase's token verification / `auth.getUser()` equivalent to resolve
  the `user_id`.
- **Row Level Security (RLS)** is the primary enforcement layer, not just
  the FastAPI dependency: every table in Section 8.3 has RLS policies so a
  user can only ever `SELECT`/`INSERT`/`UPDATE` rows where `user_id`
  matches their own `auth.uid()`. This means the `403` behavior in Section
  4 is backed by the database, not just application code.
- Anonymous/guest use should still be possible for `/api/search`,
  `/api/article/{article_number}`, `/api/case/{case_id}` — read-only
  reference lookups don't need login. Only chat history, feedback, and
  sharing require an account.

### 8.3 Supabase schema (Postgres — via `supabase/migrations/`)

`001_initial_schema.sql`:
```sql
-- users table is managed by Supabase Auth (auth.users) — do not recreate it.
-- Add a public profile table only if extra fields beyond auth.users are needed:
create table public.profiles (
  id uuid references auth.users(id) primary key,
  email text,
  created_at timestamptz default now()
);
```

`002_chat.sql`:
```sql
create table public.conversations (
  id uuid primary key default gen_random_uuid(),
  user_id uuid references auth.users(id) not null,
  title text,
  language text default 'en',
  created_at timestamptz default now(),
  updated_at timestamptz default now()
);

create table public.messages (
  id uuid primary key default gen_random_uuid(),
  conversation_id uuid references public.conversations(id) not null,
  role text check (role in ('user', 'assistant')) not null,
  content text not null,
  created_at timestamptz default now()
);
```

`003_citations.sql`:
```sql
create table public.citations (
  id uuid primary key default gen_random_uuid(),
  message_id uuid references public.messages(id) not null,
  source_id text not null,
  label text not null
);
```

`004_feedback.sql`:
```sql
create table public.feedback (
  id uuid primary key default gen_random_uuid(),
  user_id uuid references auth.users(id) not null,
  message_id uuid references public.messages(id) not null,
  feedback text check (feedback in ('positive', 'negative')) not null,
  created_at timestamptz default now()
);

create table public.shares (
  id uuid primary key default gen_random_uuid(),
  share_id text unique not null,
  conversation_id uuid references public.conversations(id) not null,
  created_at timestamptz default now()
);
```

RLS policies (add to the relevant migration, one per table):
```sql
alter table public.conversations enable row level security;
create policy "Users manage own conversations"
  on public.conversations for all
  using (auth.uid() = user_id);

-- messages/feedback follow the same pattern, scoped through their
-- parent conversation's user_id via a join or a denormalized user_id column
-- — pick one approach and apply it consistently across all four tables.
```

- `citations` is a normalized table (not embedded JSON) so citation
  correctness can be queried/benchmarked directly (Section 9 Phase 5).
- `shares` stays minimal — resolve `share_id → conversation_id → messages`
  at read time rather than duplicating message content into the share row,
  same reasoning as before: a share link should always reflect current
  data and shouldn't fork private content into a separately-permissioned
  table.

### 8.4 Requirements checklist

- [ ] Add `backend/services/supabase.py` — service-role client init +
      query helpers used by route handlers
- [ ] Add `frontend/src/services/supabase.js` — anon-key client init +
      auth calls (`signUp`, `signInWithPassword`, `signOut`,
      `onAuthStateChange`)
- [ ] Write migrations in `supabase/migrations/` exactly as scaffolded in
      8.3 (schema changes only via new numbered migration files, never
      through the dashboard)
- [ ] Enable and write RLS policies for `conversations`, `messages`,
      `citations`, `feedback` — verify with a negative test (user A cannot
      read user B's conversation) before calling this phase done
- [ ] Implement `get_current_user` dependency, apply to protected routes
      (`/api/chat`, `/api/history`, `/api/feedback`, `/api/share`)
- [ ] Persist conversations + messages + citations on every `/api/chat` call
- [ ] Persist feedback on `POST /api/feedback`
- [ ] Persist + resolve share links on `POST /api/share` / `GET /api/share/{id}`
- [ ] Wire frontend: login/signup screen using Supabase Auth UI or custom
      form, session persisted via Supabase client, attach bearer token on
      all protected FastAPI requests, logout calls `supabase.auth.signOut()`
      and redirects to login
- [ ] Sidebar/top-bar user avatar (already in mockup, Section 1.3) becomes
      a real account menu — profile + logout
- [ ] Add `supabase/seed.sql` with a handful of dev-only sample rows for
      local testing (not committed with real user data)

---

## 9. Implementation Phases (build in this order)

### Phase 1 — Foundation & ConstitutionGPT refactor
- [ ] Split existing monolithic `main.py` into `api/`, `services/`, `models/`
- [ ] Add Pydantic request/response models for all endpoints in Section 4
- [ ] Fix global `chat_history` bug — scope by `conversation_id`
- [ ] Centralize config/env loading in `config.py`
- [ ] Add error handling + logging
- [ ] Lock down CORS (no more `allow_origins=["*"]` in prod config)
- [ ] Confirm existing FAISS-based RAG still answers correctly after refactor
- [ ] Move the source PDF into `data/raw/constitution/` per Section 3.1
- [ ] Add `.gitignore` per Section 3.2 (before committing `data/` contents)
- [ ] Write `scripts/ingest.py` — replaces `pdf.py`/`pdf.ipynb`, extracts
      text from `data/raw/**` into `data/processed/`, creating any missing
      directories at runtime

### Phase 2 — Metadata-aware Pinecone RAG
- [ ] Write `scripts/chunk.py` — chunks `data/processed/` text, attaches
      metadata schema (Section 5), writes to `data/processed/chunks/` and
      `data/processed/metadata/`
- [ ] Write `scripts/index.py` — embeds chunks, upserts into Pinecone
- [ ] Migrate/re-embed constitutional text into Pinecone via the scripts
      above (not manually, not from the old notebook)
- [ ] Implement query → metadata filter extraction
- [ ] Implement hybrid metadata + semantic retrieval
- [ ] Benchmark against old FAISS retrieval (Recall@K, Precision@K)
- [ ] Create `data/evaluation/questions.json` benchmark set (used again in
      Phase 5)

### Phase 2.5 — Case-law corpus ingestion
> Not covered by re-embedding the existing constitutional PDF. This is a
> separate data-sourcing task and should not be assumed "done" once Phase 2
> is complete.
- [ ] Identify source for full judgment text (e.g. Indian Kanoon, Supreme
      Court of India judgments portal) for the landmark cases listed in
      Section 1.5 / product spec (Kesavananda Bharati, Maneka Gandhi,
      Minerva Mills, Golaknath, S.R. Bommai, Puttaswamy, Shreya Singhal)
- [ ] Confirm license/reuse terms for whichever source is used before bulk
      downloading judgment text
- [ ] Save source files into `data/raw/case_law/` per Section 3.1
- [ ] Write a case-law-specific parser (judgments are long, inconsistently
      formatted PDFs/HTML — do not reuse `scripts/ingest.py`'s constitution
      parser as-is; extend or fork it)
- [ ] Chunk judgments preserving paragraph/holding structure, not fixed
      character windows — legal holdings lose meaning if split mid-paragraph
- [ ] Apply the case-law metadata schema (Section 5) per chunk
- [ ] Embed and upsert into the same Pinecone index, `document_type: "case_law"`
- [ ] Spot-check retrieval quality on 5–10 known case queries before wiring
      into the LangGraph case-law route

**Until this phase is complete:** the Case Law query route (Section 6) and
the "Landmark Supreme Court judgments" cards in the Source Explorer
(Section 1.5) should return a clearly labeled placeholder/empty state
("Case law index not yet available") rather than fabricated or hallucinated
case summaries. Do not let Gemini free-generate case content as a
substitute for missing retrieval data.

### Phase 3 — LangGraph orchestration
- [ ] Implement graph state + all nodes listed in Section 6
- [ ] Implement conditional edges (context evaluation → rewrite loop)
- [ ] Implement Citation Builder node
- [ ] Benchmark LLM calls/query and latency vs. Phase 1 baseline

### Phase 3.5 — Auth & Supabase persistence
- [ ] Create Supabase project (or local Supabase CLI for dev)
- [ ] Write and run migrations per Section 8.3 (`supabase/migrations/`)
- [ ] Enable RLS and write/test policies for all four tables
- [ ] Implement Supabase Auth signup/login/logout on frontend
- [ ] Implement `get_current_user` dependency, protect chat/history/
      feedback/share routes
- [ ] Persist conversations/messages/citations/feedback/shares
- [ ] Confirm `conversation_id` ownership check (`403` + RLS) works —
      test with two accounts

### Phase 4 — ConstituteAI UI (build to spec in Section 1)
- [ ] Login / signup screen (blocks access to chat until authenticated,
      except the read-only public routes noted in Section 8.2)
- [ ] Account menu on user avatar (profile, logout) per Section 8.4
- [ ] Sidebar, New Chat, nav list
- [ ] Universal search bar + Quick Action chips
- [ ] Chat message rendering (Summary / headers / inline citation chips /
      Key Clauses / Explanation / Cite Source / feedback)
- [ ] Source Explorer panel (open on citation click, closable)
- [ ] Language selector — full 22-language dropdown per Section 7 — wired
      to `language` field in `/api/chat`
- [ ] Share flow (`POST /api/share`)
- [ ] Responsive/mobile layout per Section 1.6

### Phase 5 — Evaluation, hardening, deployment
- [ ] Expand `data/evaluation/questions.json` (created in Phase 2) into a
      full benchmark dataset (question → expected source IDs)
- [ ] Measure retrieval + generation + latency metrics
- [ ] Produce ConstitutionGPT vs. ConstituteAI before/after comparison table
- [ ] Add API validation, timeouts, retries, rate limiting, health endpoint
- [ ] Verify secrets are not committed; configure Vercel + Pinecone +
      Gemini + Supabase (URL, anon key, service role key) env vars for
      production
- [ ] Update README with new architecture and screenshots

---

## 10. Non-negotiable constraints for Copilot

1. Do not reintroduce a global/module-level chat history object.
2. Do not fabricate citations in prompt templates — the system prompt must
   instruct the model to say "insufficient information" rather than guess.
3. Auth and persistence follow the Supabase model in Section 8 exactly —
   do not build a custom JWT/session implementation or swap in a different
   provider without discussion.
4. Match the UI structure in Section 1 exactly before adding any extra
   panels, pages, or nav items not listed there.
5. Every new backend module goes in the structure defined in Section 3 —
   no ad hoc top-level files.
6. If the case-law index (Phase 2.5) isn't populated yet, case-law queries
   must degrade to an explicit "not yet available" response — never let the
   model fill the gap with unsourced generated case summaries.
7. Never commit anything under `data/` — it must stay gitignored per
   Section 3.2. If a script needs a directory under `data/` to exist,
   create it at runtime rather than tracking a placeholder file in git.