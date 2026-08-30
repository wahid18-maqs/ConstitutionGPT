import { Search, Share2 } from "lucide-react";
import { useAuth } from "../context/AuthContext";
import LanguageSelector from "./LanguageSelector";

const QUICK_ACTIONS = ["Preamble", "Fundamental Rights", "Emergency Provisions", "President of India"];

export default function TopBar({
  searchValue,
  onSearchChange,
  onSearchSubmit,
  onQuickAction,
  searchInputRef,
  language,
  onLanguageChange,
  onShare,
  shareStatus,
}) {
  const { user, signOut } = useAuth();

  return (
    <header className="border-b border-border bg-base/80 backdrop-blur-md">
      <div className="flex h-16 items-center justify-between gap-4 px-6">
        <form onSubmit={onSearchSubmit} className="relative mx-auto w-full max-w-2xl">
          <Search size={16} className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-muted" />
          <input
            ref={searchInputRef}
            type="text"
            value={searchValue}
            onChange={(event) => onSearchChange(event.target.value)}
            placeholder="Ask about Articles, Schedules, or Amendments…"
            className="w-full rounded-xl border border-border bg-panel py-2 pl-10 pr-4 text-sm text-heading placeholder-muted focus:border-gold focus:outline-none"
          />
        </form>

        <div className="flex shrink-0 items-center gap-3">
          {shareStatus && <span className="text-xs text-muted">{shareStatus}</span>}
          <button
            type="button"
            onClick={onShare}
            className="flex items-center gap-1.5 rounded-full border border-border px-3 py-1 text-xs font-medium text-body transition hover:bg-border/60"
          >
            <Share2 size={14} />
            Share
          </button>
          <LanguageSelector value={language} onChange={onLanguageChange} />
          <button
            type="button"
            title={user?.email}
            onClick={signOut}
            className="flex h-8 w-8 items-center justify-center rounded-full bg-gold-gradient text-xs font-semibold text-base"
          >
            {user?.email?.[0]?.toUpperCase() ?? "?"}
          </button>
        </div>
      </div>

      <div className="flex items-center gap-2 overflow-x-auto border-b border-border/50 bg-panel/30 px-6 py-3">
        {QUICK_ACTIONS.map((label) => (
          <button
            key={label}
            type="button"
            onClick={() => onQuickAction(label)}
            className="shrink-0 rounded-full border border-border px-3 py-1 text-xs font-medium text-body transition hover:bg-border/60"
          >
            {label}
          </button>
        ))}
      </div>
    </header>
  );
}
