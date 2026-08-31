/** FastAPI client for SamvidhanAI — attaches the current Supabase session's
 * access token as a Bearer header, per instructions_refactor.md Section 8.2
 * ("Every request from frontend to FastAPI attaches the Supabase session's
 * access token"). */
import { getSession } from "./supabase";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

async function parseOrThrow(response) {
  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    throw new Error(body.detail || `Request failed (${response.status})`);
  }
  return response.json();
}

async function authorizedFetch(path, options = {}) {
  const {
    data: { session },
  } = await getSession();
  if (!session) {
    throw new Error("Not signed in");
  }

  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${session.access_token}`,
      ...options.headers,
    },
  });
  return parseOrThrow(response);
}

/** For the routes Section 8.2 explicitly allows anonymous access to. */
async function anonymousFetch(path, options = {}) {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers: { "Content-Type": "application/json", ...options.headers },
  });
  return parseOrThrow(response);
}

/** POST /api/chat — returns { message_id, answer, citations }. */
export function postChat(message, language, conversationId) {
  return authorizedFetch("/api/chat", {
    method: "POST",
    body: JSON.stringify({ message, language, conversation_id: conversationId }),
  });
}

/** GET /api/conversations — the current user's past conversations. */
export function getConversations() {
  return authorizedFetch("/api/conversations");
}

/** GET /api/history?conversation_id=... — one conversation's messages. */
export function getHistory(conversationId) {
  return authorizedFetch(`/api/history?conversation_id=${encodeURIComponent(conversationId)}`);
}

/** GET /api/source/{source_id} — anonymous, no auth needed (Section 8.2). */
export function getSource(sourceId) {
  return anonymousFetch(`/api/source/${encodeURIComponent(sourceId)}`);
}

/** GET /api/articles?category=... — anonymous; a named Fundamental Rights
 * or Directive Principles article group (Ui updates and features.md 2.2 A1). */
export function getArticleGroup(category) {
  return anonymousFetch(`/api/articles?category=${encodeURIComponent(category)}`);
}

/** GET /api/cases — anonymous; the actually-indexed landmark judgments
 * (Ui updates and features.md 2.2 B2's Case Studies sub-menu). */
export function getCases() {
  return anonymousFetch("/api/cases");
}

/** GET /api/search?q=... — anonymous; ranked results list across the
 * whole corpus (Ui updates and features.md 2.2 B1's Search by Topic). */
export function search(query) {
  return anonymousFetch(`/api/search?q=${encodeURIComponent(query)}`);
}

/** GET /api/search/fulltext?q=... — anonymous; literal keyword/phrase
 * match across the whole corpus (coming_soon.md #1's Full-Text Search). */
export function searchFulltext(query) {
  return anonymousFetch(`/api/search/fulltext?q=${encodeURIComponent(query)}`);
}

/** GET /api/cases/analysis — anonymous; static case-significance
 * summaries (coming_soon.md #2's Case Analysis sub-item). */
export function getCaseAnalyses() {
  return anonymousFetch("/api/cases/analysis");
}

/** POST /api/feedback — thumbs up/down on one assistant message. */
export function postFeedback(messageId, feedback) {
  return authorizedFetch("/api/feedback", {
    method: "POST",
    body: JSON.stringify({ message_id: messageId, feedback }),
  });
}

/** POST /api/share — returns { share_id } for a conversation the caller owns. */
export function postShare(conversationId) {
  return authorizedFetch("/api/share", {
    method: "POST",
    body: JSON.stringify({ conversation_id: conversationId }),
  });
}

/** GET /api/share/{share_id} — anonymous, no auth needed (Section 8.3). */
export function getSharedConversation(shareId) {
  return anonymousFetch(`/api/share/${encodeURIComponent(shareId)}`);
}
