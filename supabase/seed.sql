-- Development-only seed data for ConstituteAI. Not real user data.
--
-- conversations/messages/feedback/shares all foreign-key to auth.users(id),
-- so a row can't be seeded here for a user that doesn't exist yet. Sign up
-- one throwaway dev user first (e.g. via POST /api/auth/signup, or
-- backend.services.auth_service.sign_up in a REPL), then replace
-- '00000000-0000-0000-0000-000000000000' below with that user's real id
-- before running this file.

insert into public.conversations (id, user_id, title, language)
values (
  '11111111-1111-1111-1111-111111111111',
  '00000000-0000-0000-0000-000000000000',
  'Sample conversation about Article 21',
  'en'
);

insert into public.messages (conversation_id, role, content)
values
  ('11111111-1111-1111-1111-111111111111', 'user', 'What is Article 21?'),
  ('11111111-1111-1111-1111-111111111111', 'assistant',
   'Article 21 protects the right to life and personal liberty. This is a research aid, not legal advice.');
