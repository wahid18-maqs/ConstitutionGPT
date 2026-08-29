import { useState } from "react";
import CitationChip from "./CitationChip";
import { postFeedback } from "../services/api";

function CitationRow({ citations, onCitationClick }) {
  if (!citations?.length) return null;
  return (
    <div className="mt-1 flex flex-wrap gap-1.5">
      {citations.map((citation) => (
        <CitationChip key={citation.source_id} citation={citation} onClick={onCitationClick} />
      ))}
    </div>
  );
}

/** Section 1.4 footer: thumbs up/down feedback on one assistant message.
 * ("Cite Source" isn't a separate button here — the inline citation chips
 * already open the Source Explorer, which serves the same purpose.) Hidden
 * entirely on a read-only view (e.g. a shared conversation), since giving
 * feedback requires being the message's own authenticated owner. */
function FeedbackRow({ messageId }) {
  const [choice, setChoice] = useState(null);
  const [error, setError] = useState(null);

  async function choose(feedback) {
    if (choice || !messageId) return;
    setChoice(feedback);
    try {
      await postFeedback(messageId, feedback);
    } catch (err) {
      setChoice(null);
      setError(err.message || "Could not send feedback.");
    }
  }

  return (
    <div className="flex items-center gap-2 pt-1">
      <button
        type="button"
        onClick={() => choose("positive")}
        disabled={choice !== null}
        aria-label="Helpful"
        className={`text-sm ${choice === "positive" ? "text-amber" : "text-navy/40 hover:text-navy"}`}
      >
        👍
      </button>
      <button
        type="button"
        onClick={() => choose("negative")}
        disabled={choice !== null}
        aria-label="Not helpful"
        className={`text-sm ${choice === "negative" ? "text-amber" : "text-navy/40 hover:text-navy"}`}
      >
        👎
      </button>
      {choice && <span className="text-xs text-navy/50">Thanks for the feedback.</span>}
      {error && <span className="text-xs text-red-600">{error}</span>}
    </div>
  );
}

/** Per Section 1.4: user messages are right-aligned navy bubbles; AI
 * messages flow left-aligned with no bubble, structured as Summary ->
 * section headers -> Key Clauses -> Explanation, each citation attached to
 * the specific piece of content it supports. History-loaded messages carry
 * the same structure (persisted alongside the flat `content`, see
 * backend/api/routes/chat.py's structured_answer column) so this renders
 * identically live or reloaded. Falls back to flat `content` only for a
 * message that genuinely has no structure (e.g. a message persisted before
 * the structured_answer column existed). */
export default function MessageBubble({
  id,
  role,
  content,
  summary,
  sections,
  keyClauses,
  explanation,
  citations,
  onCitationClick,
  readOnly,
}) {
  if (role === "user") {
    return (
      <div className="flex justify-end">
        <div className="max-w-lg rounded-2xl bg-navy px-4 py-2 text-sm text-white">{content}</div>
      </div>
    );
  }

  const hasStructure = summary || sections?.length || keyClauses?.length || explanation;
  if (!hasStructure) {
    return (
      <div className="max-w-2xl space-y-2 text-sm text-navy">
        <p className="whitespace-pre-wrap">{content}</p>
        <CitationRow citations={citations} onCitationClick={onCitationClick} />
        {!readOnly && <FeedbackRow messageId={id} />}
      </div>
    );
  }

  return (
    <div className="max-w-2xl space-y-4 text-sm text-navy">
      {summary && (
        <p>
          <span className="font-semibold">Summary: </span>
          {summary}
        </p>
      )}

      {sections?.map((section, index) => (
        <div key={index}>
          <h3 className="font-semibold text-navy">{section.heading}</h3>
          <p className="mt-1 whitespace-pre-wrap">{section.body}</p>
          <CitationRow citations={section.citations} onCitationClick={onCitationClick} />
        </div>
      ))}

      {keyClauses?.length > 0 && (
        <div>
          <h3 className="font-semibold text-navy">Key Clauses</h3>
          <ul className="mt-1 list-disc space-y-2 pl-5">
            {keyClauses.map((clause, index) => (
              <li key={index}>
                {clause.text}
                <CitationRow citations={clause.citations} onCitationClick={onCitationClick} />
              </li>
            ))}
          </ul>
        </div>
      )}

      {explanation && (
        <div>
          <h3 className="font-semibold text-navy">Explanation</h3>
          <p className="mt-1 whitespace-pre-wrap text-navy/90">{explanation}</p>
        </div>
      )}

      {!readOnly && <FeedbackRow messageId={id} />}
    </div>
  );
}
