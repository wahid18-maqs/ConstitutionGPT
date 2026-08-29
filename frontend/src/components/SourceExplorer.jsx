import { useEffect, useState } from "react";
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
    <aside className="flex h-screen w-80 shrink-0 flex-col border-l border-navy/10 bg-white">
      <div className="flex items-center justify-between border-b border-navy/10 px-4 py-4">
        <h2 className="text-sm font-semibold text-navy">{citation.label}</h2>
        <button
          type="button"
          onClick={onClose}
          aria-label="Close"
          className="text-navy/50 hover:text-navy"
        >
          ✕
        </button>
      </div>

      <div className="flex-1 overflow-y-auto px-4 py-4 text-sm">
        {loading && <p className="text-navy/50">Loading…</p>}
        {error && <p className="text-red-600">{error}</p>}
        {source && (
          <div className="space-y-4">
            <div className="rounded-md bg-cream p-3">
              <p className="text-xs font-medium uppercase tracking-wide text-navy/50">
                {source.document}
                {source.page ? ` · p.${source.page}` : ""}
              </p>
              <p className="mt-2 whitespace-pre-wrap text-navy">{source.original_text}</p>
            </div>

            {source.related_cases.length > 0 && (
              <div>
                <p className="text-xs font-medium uppercase tracking-wide text-navy/50">
                  Landmark Supreme Court judgments
                </p>
                <ul className="mt-2 space-y-2">
                  {source.related_cases.map((item) => (
                    <li key={item} className="rounded-md border border-navy/10 p-2 text-navy">
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
