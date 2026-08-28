-- Feedback and share-link schema for ConstituteAI.

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

alter table public.feedback enable row level security;
alter table public.shares enable row level security;

create policy "Users manage own feedback"
  on public.feedback for all
  using (auth.uid() = user_id);

-- Owner-only at the RLS layer: a viewer resolving GET /api/share/{id}
-- never queries this table directly — the backend's service-role client
-- resolves share_id -> conversation -> messages server-side, bypassing
-- RLS entirely (see backend/services/supabase.py and
-- backend/api/routes/share.py). This policy only governs any future
-- direct anon-key + user-JWT access from the frontend, where only the
-- owner should be able to manage (create/list/revoke) their own shares.
create policy "Users manage own shares"
  on public.shares for all
  using (
    exists (
      select 1 from public.conversations c
      where c.id = shares.conversation_id
        and c.user_id = auth.uid()
    )
  );
