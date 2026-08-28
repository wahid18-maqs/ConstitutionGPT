-- Chat schema for ConstituteAI.

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

alter table public.conversations enable row level security;
alter table public.messages enable row level security;

create policy "Users manage own conversations"
  on public.conversations for all
  using (auth.uid() = user_id);

-- messages have no user_id column of their own — ownership is enforced
-- through the parent conversation, per instructions_refactor.md Section
-- 8.3 ("messages/feedback follow the same pattern, scoped through their
-- parent conversation's user_id via a join or a denormalized user_id
-- column — pick one approach"). This picks the join approach so the
-- schema stays exactly as specified, with no denormalized column.
create policy "Users manage own messages"
  on public.messages for all
  using (
    exists (
      select 1 from public.conversations c
      where c.id = messages.conversation_id
        and c.user_id = auth.uid()
    )
  );
