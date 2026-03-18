import {
  getDashboardStats,
  getTopOpportunities,
  getRecentLogs,
  getBudgetSummary,
  isLive,
} from "@/app/lib/atlas-data";
import { AGENT_COLORS } from "@/app/lib/atlas-types";

function ScoreBadge({ score }: { score: number | null }) {
  if (score === null) return <span className="text-[var(--text-muted)]">--</span>;
  const color =
    score >= 80 ? "text-[var(--accent-emerald)]" : score >= 60 ? "text-[var(--accent-amber)]" : "text-[var(--accent-rose)]";
  return <span className={`font-bold ${color}`}>{score}</span>;
}

function formatTime(iso: string): string {
  const d = new Date(iso);
  const now = new Date();
  const diff = now.getTime() - d.getTime();
  const mins = Math.floor(diff / 60000);
  if (mins < 60) return `${mins}m ago`;
  const hours = Math.floor(mins / 60);
  if (hours < 24) return `${hours}h ago`;
  const days = Math.floor(hours / 24);
  return `${days}d ago`;
}

export default async function DashboardOverview() {
  const [stats, topOpps, recentLogs, budget] = await Promise.all([
    getDashboardStats(),
    getTopOpportunities(5),
    getRecentLogs(168), // 7 days for demo
    getBudgetSummary(),
  ]);

  const live = isLive();
  const percentSpent = budget.total_deposited > 0
    ? (budget.total_spent / budget.total_deposited) * 100
    : 0;

  return (
    <div>
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-2xl font-bold">ATLAS Operations</h1>
          <p className="text-sm text-[var(--text-secondary)] mt-1">
            {live ? "Connected to Supabase -- live data" : "Demo mode -- connect Supabase for live data"}
          </p>
        </div>
        {!live && (
          <span className="px-3 py-1 rounded-full text-xs font-medium bg-[var(--accent-amber)]/10 text-[var(--accent-amber)]">
            Demo Data
          </span>
        )}
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <div className="glass rounded-xl p-5">
          <div className="text-xs text-[var(--text-muted)] uppercase tracking-wider mb-2">Opportunities</div>
          <div className="text-3xl font-bold gradient-text">{stats.totalOpportunities}</div>
          <div className="text-xs text-[var(--text-secondary)] mt-1">Scored by AI</div>
        </div>
        <div className="glass rounded-xl p-5">
          <div className="text-xs text-[var(--text-muted)] uppercase tracking-wider mb-2">Budget Left</div>
          <div className="text-3xl font-bold text-[var(--accent-emerald)]">${stats.budgetRemaining.toFixed(0)}</div>
          <div className="text-xs text-[var(--text-secondary)] mt-1">of ${stats.budgetLimit} monthly</div>
        </div>
        <div className="glass rounded-xl p-5">
          <div className="text-xs text-[var(--text-muted)] uppercase tracking-wider mb-2">Experiments</div>
          <div className="text-3xl font-bold text-[var(--accent-purple)]">{stats.activeExperiments}</div>
          <div className="text-xs text-[var(--text-secondary)] mt-1">Active / running</div>
        </div>
        <div className="glass rounded-xl p-5">
          <div className="text-xs text-[var(--text-muted)] uppercase tracking-wider mb-2">Distributions</div>
          <div className="text-3xl font-bold text-[var(--accent-cyan)]">{stats.distributionsSent}</div>
          <div className="text-xs text-[var(--text-secondary)] mt-1">Posts & emails sent</div>
        </div>
      </div>

      {/* Two-column layout */}
      <div className="grid lg:grid-cols-5 gap-6">
        {/* Top Opportunities (3 cols) */}
        <div className="lg:col-span-3">
          <div className="glass rounded-xl p-5">
            <h2 className="font-semibold mb-4">Top Opportunities</h2>
            <div className="space-y-3">
              {topOpps.map((opp, i) => (
                <div key={opp.id} className="flex items-center gap-3">
                  <span className="w-6 h-6 rounded-md bg-white/5 flex items-center justify-center text-xs text-[var(--text-muted)] font-bold">
                    {i + 1}
                  </span>
                  <div className="flex-1 min-w-0">
                    <div className="text-sm font-medium truncate">{opp.title}</div>
                    <div className="text-xs text-[var(--text-muted)]">
                      {opp.target_vertical ?? opp.category} &middot; {opp.source}
                    </div>
                  </div>
                  <ScoreBadge score={opp.sonnet_score} />
                </div>
              ))}
            </div>
          </div>

          {/* Budget Burn Bar */}
          <div className="glass rounded-xl p-5 mt-6">
            <div className="flex items-center justify-between mb-3">
              <h2 className="font-semibold">Budget Burn</h2>
              <span className="text-xs text-[var(--text-muted)]">{budget.month_key}</span>
            </div>
            <div className="flex items-center gap-4 mb-3">
              <div className="flex-1">
                <div className="w-full h-3 rounded-full bg-white/5 overflow-hidden">
                  <div
                    className="h-full rounded-full transition-all duration-700"
                    style={{
                      width: `${Math.min(percentSpent, 100)}%`,
                      background:
                        percentSpent > 80
                          ? "var(--accent-rose)"
                          : percentSpent > 50
                          ? "var(--accent-amber)"
                          : "var(--accent-emerald)",
                    }}
                  />
                </div>
              </div>
              <span className="text-sm font-bold whitespace-nowrap">
                ${budget.total_spent.toFixed(2)} / ${budget.total_deposited.toFixed(0)}
              </span>
            </div>
            {/* Agent breakdown */}
            <div className="grid grid-cols-4 gap-2">
              {(["scout", "vault", "forge", "mercury"] as const).map((agent) => (
                <div key={agent} className="text-center">
                  <div
                    className="w-8 h-8 rounded-lg mx-auto flex items-center justify-center text-xs font-bold mb-1"
                    style={{
                      background: `${AGENT_COLORS[agent]}20`,
                      color: AGENT_COLORS[agent],
                    }}
                  >
                    {agent[0].toUpperCase()}
                  </div>
                  <div className="text-[10px] text-[var(--text-muted)] capitalize">{agent}</div>
                </div>
              ))}
            </div>
            {percentSpent >= 80 && (
              <div className="mt-3 px-3 py-2 rounded-lg bg-[var(--accent-rose)]/10 text-[var(--accent-rose)] text-xs font-medium">
                Conservation mode active - spending restricted
              </div>
            )}
          </div>
        </div>

        {/* Activity Feed (2 cols) */}
        <div className="lg:col-span-2">
          <div className="glass rounded-xl p-5">
            <h2 className="font-semibold mb-4">Recent Activity</h2>
            <div className="space-y-3 max-h-[480px] overflow-y-auto pr-1">
              {recentLogs.slice(0, 15).map((log) => (
                <div key={log.id} className="flex items-start gap-3">
                  <div
                    className="w-7 h-7 rounded-md flex items-center justify-center text-xs font-bold shrink-0 mt-0.5"
                    style={{
                      background: `${AGENT_COLORS[log.agent] ?? "#666"}20`,
                      color: AGENT_COLORS[log.agent] ?? "#666",
                    }}
                  >
                    {log.agent[0].toUpperCase()}
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="text-sm">
                      <span className="font-medium capitalize">{log.agent}</span>{" "}
                      <span className="text-[var(--text-secondary)]">{log.action.replace(/_/g, " ")}</span>
                    </div>
                    {log.output && (
                      <div className="text-xs text-[var(--text-muted)] truncate mt-0.5">
                        {log.output.length > 80 ? log.output.slice(0, 80) + "..." : log.output}
                      </div>
                    )}
                    <div className="flex items-center gap-2 mt-1">
                      <span
                        className={`text-[10px] px-1.5 py-0.5 rounded font-medium ${
                          log.status === "success"
                            ? "bg-[var(--accent-emerald)]/10 text-[var(--accent-emerald)]"
                            : log.status === "blocked"
                            ? "bg-[var(--accent-rose)]/10 text-[var(--accent-rose)]"
                            : "bg-white/5 text-[var(--text-muted)]"
                        }`}
                      >
                        {log.status}
                      </span>
                      {log.cost_usd !== null && log.cost_usd > 0 && (
                        <span className="text-[10px] text-[var(--text-muted)]">
                          ${log.cost_usd.toFixed(4)}
                        </span>
                      )}
                      <span className="text-[10px] text-[var(--text-muted)]">
                        {formatTime(log.created_at)}
                      </span>
                    </div>
                  </div>
                </div>
              ))}
              {recentLogs.length === 0 && (
                <p className="text-sm text-[var(--text-muted)]">No recent activity</p>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
