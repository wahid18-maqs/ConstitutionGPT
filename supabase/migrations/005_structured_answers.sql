-- Persist the structured answer (Summary/sections/Key Clauses/Explanation,
-- Section 1.4) alongside a message's flattened `content`, so a conversation
-- loaded later from History renders identically to how it looked live —
-- not degraded to flat text. Nullable and unused for user messages; set on
-- assistant messages only. Shape mirrors ChatResponse exactly: {summary,
-- sections: [{heading, body, citations}], key_clauses: [{text, citations}],
-- explanation} — citations embedded here are for rendering only, the
-- normalized public.citations table (003_citations.sql) stays the source
-- of truth for querying/benchmarking citation correctness.

alter table public.messages
  add column structured_answer jsonb;
