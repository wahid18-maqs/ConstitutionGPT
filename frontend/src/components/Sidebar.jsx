import { Link } from "react-router-dom";

const TOPIC_ITEMS = [
  {
    label: "Constitutional History",
    query: "When was the Constitution of India adopted, and what is its history?",
  },
  {
    label: "Fundamental Rights",
    query: "What are the Fundamental Rights guaranteed by the Constitution of India?",
  },
  {
    label: "Directive Principles",
    query: "What are the Directive Principles of State Policy?",
  },
  {
    label: "Case Studies",
    query: "What are some landmark Supreme Court case studies on the Constitution of India?",
  },
];

export default function Sidebar({ onNewChat, onFocusSearch, onTopicSelect }) {
  return (
    <aside className="flex h-screen w-64 shrink-0 flex-col bg-navy text-white">
      <div className="flex items-center gap-2 px-4 py-4 text-lg font-semibold">
        <span>ConstituteAI</span>
      </div>

      <div className="px-4">
        <button
          type="button"
          onClick={onNewChat}
          className="w-full rounded-full bg-amber py-2 text-sm font-semibold text-white transition hover:bg-amber/90"
        >
          + New Chat
        </button>
      </div>

      <nav className="mt-6 flex-1 space-y-1 px-2">
        <button
          type="button"
          onClick={onFocusSearch}
          className="w-full rounded-md px-3 py-2 text-left text-sm text-white/80 transition hover:bg-white/10 hover:text-white"
        >
          Search Articles
        </button>
        {TOPIC_ITEMS.map((item) => (
          <button
            key={item.label}
            type="button"
            onClick={() => onTopicSelect(item.query)}
            className="w-full rounded-md px-3 py-2 text-left text-sm text-white/80 transition hover:bg-white/10 hover:text-white"
          >
            {item.label}
          </button>
        ))}
      </nav>

      <div className="space-y-1 px-2 pb-4">
        <Link
          to="/history"
          className="block w-full rounded-md px-3 py-2 text-left text-sm text-white/80 transition hover:bg-white/10 hover:text-white"
        >
          History
        </Link>
        <button
          type="button"
          className="w-full rounded-md px-3 py-2 text-left text-sm text-white/80 transition hover:bg-white/10 hover:text-white"
        >
          Settings
        </button>
      </div>
    </aside>
  );
}
