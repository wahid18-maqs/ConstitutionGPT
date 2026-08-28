-- Citation schema for ConstituteAI.

create table public.citations (
  id uuid primary key default gen_random_uuid(),
  message_id uuid references public.messages(id) not null,
  source_id text not null,
  label text not null
);

alter table public.citations enable row level security;

-- Same join-based ownership pattern as messages (Section 8.3), one hop
-- further: citations -> messages -> conversations.user_id.
create policy "Users manage own citations"
  on public.citations for all
  using (
    exists (
      select 1 from public.messages m
      join public.conversations c on c.id = m.conversation_id
      where m.id = citations.message_id
        and c.user_id = auth.uid()
    )
  );
