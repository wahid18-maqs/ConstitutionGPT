/** Inline citation chip (Section 1.4: "e.g. [Art. 368, Clause 2] — clickable,
 * opens Source Explorer scoped to that citation"). */
export default function CitationChip({ citation, onClick }) {
  return (
    <button
      type="button"
      onClick={() => onClick(citation)}
      className="inline-flex items-center rounded-full bg-navy/10 px-2 py-0.5 text-xs font-medium text-navy transition hover:bg-navy/20"
    >
      {citation.label}
    </button>
  );
}
