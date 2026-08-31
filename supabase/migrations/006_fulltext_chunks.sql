-- Full-Text Search (coming_soon.md #1): a literal keyword/phrase match
-- across the whole corpus, distinct from the existing semantic Search by
-- Topic (GET /api/search, Pinecone-backed). Pinecone has no literal
-- substring search, so this needs its own backing store -- Supabase
-- Postgres, already the project's Postgres provider (Section 8).
--
-- Populated by scripts/sync_fulltext.py from the same processed chunk
-- JSONL files scripts/chunk.py / scripts/chunk_case_law.py already write
-- -- this table is a search index, not a new source of truth. Re-run the
-- sync script whenever the underlying corpus changes.
--
-- pg_trgm + a GIN index make ILIKE ('%term%') reasonably fast even
-- without a dedicated full-text-search engine, which is enough for a
-- corpus this size (per Ui updates and features.md 2.2 B1's own
-- "ILIKE/regex scan if the corpus stays small" allowance).

create extension if not exists pg_trgm;

create table public.document_chunks (
  id bigint generated always as identity primary key,
  source_id text not null,
  label text not null,
  document_type text not null check (document_type in ('constitution', 'case_law')),
  chunk_text text not null
);

create index document_chunks_text_trgm_idx
  on public.document_chunks using gin (chunk_text gin_trgm_ops);

-- Read-only reference data, same anonymous-access model as Pinecone-backed
-- lookups (Section 8.2) -- no per-user ownership, RLS just needs to allow
-- anonymous SELECT while blocking writes from anything but the
-- service-role key the sync script and backend both use.
alter table public.document_chunks enable row level security;

create policy "Anyone can read document chunks"
  on public.document_chunks for select
  using (true);
