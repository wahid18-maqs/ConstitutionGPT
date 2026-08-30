/** Supabase client for SamvidhanAI — anon/public key, client-side auth only.
 *
 * Per instructions_refactor.md Section 8.2, the frontend talks to Supabase
 * Auth directly (signUp/signInWithPassword/signOut/onAuthStateChange) rather
 * than proxying every auth call through FastAPI. Only the resulting session
 * access token gets attached as a Bearer header on backend API calls.
 */
import { createClient } from "@supabase/supabase-js";

export const supabase = createClient(
  import.meta.env.VITE_SUPABASE_URL,
  import.meta.env.VITE_SUPABASE_ANON_KEY,
);

export function signUp(email, password) {
  return supabase.auth.signUp({ email, password });
}

export function signInWithPassword(email, password) {
  return supabase.auth.signInWithPassword({ email, password });
}

export function signOut() {
  return supabase.auth.signOut();
}

export function getSession() {
  return supabase.auth.getSession();
}

export function onAuthStateChange(callback) {
  return supabase.auth.onAuthStateChange(callback);
}
