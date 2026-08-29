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
    <header className="border-b border-navy/10 bg-white px-6 py-4">
      <form onSubmit={onSearchSubmit}>
        <input
          ref={searchInputRef}
          type="text"
          value={searchValue}
          onChange={(event) => onSearchChange(event.target.value)}
          placeholder="Ask about Articles, Schedules, or Amendments…"
          className="w-full rounded-full border border-navy/20 px-4 py-2 text-sm focus:border-navy focus:outline-none"
        />
      </form>

      <div className="mt-3 flex items-center justify-between">
        <div className="flex flex-wrap gap-2">
          {QUICK_ACTIONS.map((label) => (
            <button
              key={label}
              type="button"
              onClick={() => onQuickAction(label)}
              className="rounded-full border border-navy/20 px-3 py-1 text-xs font-medium text-navy transition hover:bg-navy/5"
            >
              {label}
            </button>
          ))}
        </div>

        <div className="flex shrink-0 items-center gap-3 pl-4">
          {shareStatus && <span className="text-xs text-navy/50">{shareStatus}</span>}
          <button
            type="button"
            onClick={onShare}
            className="rounded-full border border-navy/20 px-3 py-1 text-xs font-medium text-navy transition hover:bg-navy/5"
          >
            Share
          </button>
          <LanguageSelector value={language} onChange={onLanguageChange} />
          <button
            type="button"
            title={user?.email}
            onClick={signOut}
            className="flex h-8 w-8 items-center justify-center rounded-full bg-navy text-xs font-semibold text-white"
          >
            {user?.email?.[0]?.toUpperCase() ?? "?"}
          </button>
        </div>
      </div>
    </header>
  );
}
