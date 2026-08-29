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
    <div className="min-h-screen bg-cream px-6 py-6">
      <div className="mx-auto max-w-2xl">
        <div className="mb-4 flex items-center justify-between">
          <h1 className="text-lg font-semibold text-navy">Conversation history</h1>
          <Link to="/chat" className="text-sm text-navy underline">
            Back to chat
          </Link>
        </div>

        {loading && <p className="text-sm text-navy/50">Loading…</p>}
        {error && <p className="text-sm text-red-600">{error}</p>}
        {!loading && !error && conversations.length === 0 && (
          <p className="text-sm text-navy/50">No conversations yet.</p>
        )}

        <ul className="space-y-2">
          {conversations.map((conversation) => (
            <li key={conversation.id}>
              <Link
                to={`/chat?conversation=${conversation.id}`}
                className="block rounded-md border border-navy/10 bg-white px-4 py-3 text-sm text-navy transition hover:border-navy/30"
              >
                <p className="font-medium">{conversation.title || "Untitled conversation"}</p>
                {conversation.updated_at && (
                  <p className="mt-1 text-xs text-navy/50">
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
