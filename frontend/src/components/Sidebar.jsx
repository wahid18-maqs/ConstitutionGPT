import { Link } from "react-router-dom";
import { BookOpen, Gavel, Landmark, Scale, Search, Settings, Shield } from "lucide-react";

// NB: the Ashoka State Emblem shown in the reference mockup is a protected
// national symbol (State Emblem of India (Prohibition of Improper Use) Act,
// 2005) and must not be reproduced as an app logo. `Landmark` is used as a
// deliberate, license-safe substitute per Ui updates and features.md 1.7.

const TOPIC_ITEMS = [
  {
    label: "Constitutional History",
    icon: BookOpen,
    query: "When was the Constitution of India adopted, and what is its history?",
  },
  {
    label: "Fundamental Rights",
    icon: Shield,
    query: "What are the Fundamental Rights guaranteed by the Constitution of India?",
  },
  {
    label: "Directive Principles",
    icon: Scale,
    query: "What are the Directive Principles of State Policy?",
  },
  {
    label: "Case Studies",
    icon: Gavel,
    query: "What are some landmark Supreme Court case studies on the Constitution of India?",
  },
];

function NavButton({ icon: Icon, label, active, onClick }) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={`flex w-full items-center gap-2.5 rounded-lg px-3 py-2 text-left text-sm transition ${
        active
          ? "bg-gold/10 text-gold"
          : "text-muted hover:bg-border/60 hover:text-heading"
      }`}
    >
      <Icon size={16} className="shrink-0" />
      <span>{label}</span>
    </button>
  );
}

export default function Sidebar({ onNewChat, onFocusSearch, onTopicSelect, activeTopic }) {
  return (
    <aside className="flex h-screen w-72 shrink-0 flex-col border-r border-border bg-panel">
      <div className="flex h-16 items-center gap-2.5 border-b border-border px-5">
        <Landmark size={20} className="shrink-0 text-gold" />
        <span className="font-semibold tracking-wide text-heading">ConstituteAI</span>
      </div>

      <div className="p-4">
        <button
          type="button"
          onClick={onNewChat}
          className="flex w-full items-center justify-center gap-2.5 rounded-xl bg-gold-gradient px-4 py-2.5 text-sm font-medium text-base shadow-lg transition hover:opacity-95"
        >
          + New Chat
        </button>
      </div>

      <nav className="flex-1 space-y-1.5 px-3 py-2">
        <NavButton icon={Search} label="Search Articles" onClick={onFocusSearch} />
        {TOPIC_ITEMS.map((item) => (
          <NavButton
            key={item.label}
            icon={item.icon}
            label={item.label}
            active={activeTopic === item.label}
            onClick={() => onTopicSelect(item)}
          />
        ))}
      </nav>

      <div className="space-y-1.5 px-3 pb-4">
        <Link
          to="/history"
          className="flex w-full items-center gap-2.5 rounded-lg px-3 py-2 text-left text-sm text-muted transition hover:bg-border/60 hover:text-heading"
        >
          <BookOpen size={16} className="shrink-0" />
          History
        </Link>
        <button
          type="button"
          className="flex w-full items-center gap-2.5 rounded-lg px-3 py-2 text-left text-sm text-muted transition hover:bg-border/60 hover:text-heading"
        >
          <Settings size={16} className="shrink-0" />
          Settings
        </button>
      </div>
    </aside>
  );
}
