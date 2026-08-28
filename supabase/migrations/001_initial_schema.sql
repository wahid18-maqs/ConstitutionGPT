-- Initial Supabase schema for ConstituteAI.
-- users table is managed by Supabase Auth (auth.users) — do not recreate it.

create table public.profiles (
  id uuid references auth.users(id) primary key,
  email text,
  created_at timestamptz default now()
);

alter table public.profiles enable row level security;

create policy "Users manage own profile"
  on public.profiles for all
  using (auth.uid() = id);
