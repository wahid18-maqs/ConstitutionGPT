import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { getConversations } from "../services/api";

/** Lists the current user's past conversations; clicking one continues it
 * in Chat (which loads that conversation's persisted messages). Past
 * messages render as flat text (see MessageBubble's fallback) since
 * persistence only stores the flattened answer, not the structured
 * sections/key-clauses breakdown. */
export default function History() {
  const [conversations, setConversations] = useState([]);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getConversations()
      .then((data) => setConversations(data.conversations))
      .catch((err) => setError(err.message || "Could not load your conversations."))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="min-h-screen bg-base px-6 py-6">
      <div className="mx-auto max-w-2xl">
        <div className="mb-4 flex items-center justify-between">
          <h1 className="text-lg font-semibold text-heading">Conversation history</h1>
          <Link to="/chat" className="text-sm text-gold underline">
            Back to chat
          </Link>
        </div>

        {loading && <p className="text-sm text-muted">Loading…</p>}
        {error && <p className="text-sm text-red-400">{error}</p>}
        {!loading && !error && conversations.length === 0 && (
          <p className="text-sm text-muted">No conversations yet.</p>
        )}

        <ul className="space-y-2">
          {conversations.map((conversation) => (
            <li key={conversation.id}>
              <Link
                to={`/chat?conversation=${conversation.id}`}
                className="block rounded-lg border border-border bg-panel px-4 py-3 text-sm text-body transition hover:border-gold/50"
              >
                <p className="font-medium text-heading">{conversation.title || "Untitled conversation"}</p>
                {conversation.updated_at && (
                  <p className="mt-1 text-xs text-muted">
                    {new Date(conversation.updated_at).toLocaleString()}
                  </p>
                )}
              </Link>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}
