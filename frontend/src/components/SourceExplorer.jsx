import { useEffect, useState } from "react";
import { BadgeCheck, X } from "lucide-react";
import { getSource } from "../services/api";

/** Section 1.5: opens on citation click, closable, scrolls independently. */
export default function SourceExplorer({ citation, onClose }) {
  const [source, setSource] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let active = true;
    setSource(null);
    setError(null);
    setLoading(true);
    getSource(citation.source_id)
      .then((data) => active && setSource(data))
      .catch((err) => active && setError(err.message || "Could not load this source."))
      .finally(() => active && setLoading(false));
    return () => {
      active = false;
    };
  }, [citation.source_id]);

  return (
    <aside className="flex h-screen w-96 shrink-0 flex-col border-l border-border bg-panel shadow-2xl">
      <div className="flex h-16 items-center justify-between border-b border-border px-5">
        <h2 className="text-sm font-semibold text-heading">Source Explorer</h2>
        <button
          type="button"
          onClick={onClose}
          aria-label="Close"
          className="text-muted hover:text-heading"
        >
          <X size={18} />
        </button>
      </div>

      <div className="flex-1 overflow-y-auto p-5 text-sm">
        {loading && <p className="text-muted">Loading…</p>}
        {error && <p className="text-red-400">{error}</p>}
        {source && (
          <div className="space-y-6">
            <div>
              <div className="mb-2 flex items-center gap-1.5 text-xs font-medium text-gold">
                <BadgeCheck size={14} />
                Pinecone RAG verified
              </div>
              <div className="rounded-xl border border-border bg-base/60 p-4">
                <p className="text-xs font-medium uppercase tracking-wide text-muted">
                  {source.document}
                  {source.page ? ` · p.${source.page}` : ""}
                </p>
                <p className="mt-2 whitespace-pre-wrap text-body">{source.original_text}</p>
              </div>
            </div>

            {source.related_cases.length > 0 && (
              <div>
                <p className="text-xs font-medium uppercase tracking-wide text-muted">
                  Landmark Supreme Court judgments
                </p>
                <ul className="mt-2 space-y-2">
                  {source.related_cases.map((item) => (
                    <li key={item} className="rounded-lg border border-border p-2 text-body">
                      {item}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        )}
      </div>
    </aside>
  );
}
