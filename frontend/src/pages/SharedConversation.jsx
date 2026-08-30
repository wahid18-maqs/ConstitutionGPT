import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import MessageBubble from "../components/MessageBubble";
import SourceExplorer from "../components/SourceExplorer";
import { getSharedConversation } from "../services/api";

/** Public, anonymous view of a shared conversation (Section 8.3: resolved
 * server-side via the service-role client, no auth required to view). */
export default function SharedConversation() {
  const { shareId } = useParams();
  const [messages, setMessages] = useState(null);
  const [error, setError] = useState(null);
  const [activeCitation, setActiveCitation] = useState(null);

  useEffect(() => {
    getSharedConversation(shareId)
      .then((data) => setMessages(data.messages))
      .catch((err) => setError(err.message || "This share link could not be found."));
  }, [shareId]);

  return (
    <div className="flex min-h-screen bg-base">
      <div className="flex-1 px-6 py-6">
        <div className="mx-auto max-w-2xl">
          <div className="mb-4 flex items-center justify-between">
            <h1 className="text-lg font-semibold text-heading">Shared conversation</h1>
            <Link to="/chat" className="text-sm text-gold underline">
              Open ConstituteAI
            </Link>
          </div>

          {error && <p className="text-sm text-red-400">{error}</p>}
          {!error && !messages && <p className="text-sm text-muted">Loading…</p>}

          <div className="space-y-4">
            {messages?.map((message) => (
              <MessageBubble
                key={message.id}
                {...message}
                keyClauses={message.key_clauses}
                readOnly
                onCitationClick={setActiveCitation}
              />
            ))}
          </div>
        </div>
      </div>

      {activeCitation && (
        <SourceExplorer citation={activeCitation} onClose={() => setActiveCitation(null)} />
      )}
    </div>
  );
}
