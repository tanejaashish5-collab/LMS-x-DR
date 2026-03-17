"use client";

import { useState, useMemo } from "react";
import {
  opportunities,
  calculateWeightedScore,
  scoreWeights,
} from "./data/opportunities";
import type { Opportunity } from "./data/opportunities";

/* ─── Helpers ─── */
function getSortedOpportunities(sortBy: string) {
  return [...opportunities].sort((a, b) => {
    if (sortBy === "revenue") return b.scores.revenue - a.scores.revenue;
    if (sortBy === "ease") return b.scores.easeOfBuild - a.scores.easeOfBuild;
    if (sortBy === "autonomy") return b.scores.autonomy - a.scores.autonomy;
    return (
      calculateWeightedScore(b.scores, scoreWeights) -
      calculateWeightedScore(a.scores, scoreWeights)
    );
  });
}

function getGlobalRank(opp: Opportunity): number {
  const sorted = [...opportunities].sort(
    (a, b) =>
      calculateWeightedScore(b.scores, scoreWeights) -
      calculateWeightedScore(a.scores, scoreWeights)
  );
  return sorted.findIndex((o) => o.id === opp.id) + 1;
}

function scoreColor(v: number): string {
  if (v >= 9) return "#34d399";
  if (v >= 7) return "#6366f1";
  if (v >= 5) return "#fbbf24";
  return "#fb7185";
}

function ScoreBar({ value, label }: { value: number; label: string }) {
  return (
    <div className="flex items-center gap-3">
      <span className="text-xs text-[var(--text-secondary)] w-28 shrink-0">
        {label}
      </span>
      <div className="flex-1 h-2 rounded-full bg-white/5 overflow-hidden">
        <div
          className="score-bar h-full rounded-full"
          style={{
            width: `${value * 10}%`,
            background: `linear-gradient(90deg, ${scoreColor(value)}90, ${scoreColor(value)})`,
          }}
        />
      </div>
      <span
        className="text-xs font-bold w-6 text-right"
        style={{ color: scoreColor(value) }}
      >
        {value}
      </span>
    </div>
  );
}

/* ─── Hero Stats ─── */
function HeroStats() {
  const stats = [
    { label: "Opportunities", value: "12", sub: "Deep Researched" },
    { label: "Total TAM", value: "$1.4T+", sub: "Addressable Market" },
    { label: "Avg Score", value: "7.1", sub: "Weighted Average" },
    { label: "Fastest ROI", value: "2 Wks", sub: "Time to Revenue" },
  ];
  return (
    <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mt-10">
      {stats.map((s) => (
        <div
          key={s.label}
          className="glass rounded-xl p-5 text-center hover-lift"
        >
          <div className="text-2xl lg:text-3xl font-bold gradient-text">
            {s.value}
          </div>
          <div className="text-sm text-[var(--text-secondary)] mt-1">
            {s.sub}
          </div>
        </div>
      ))}
    </div>
  );
}

/* ─── Opportunity Card ─── */
function OpportunityCard({
  opp,
  rank,
  isExpanded,
  onToggle,
}: {
  opp: Opportunity;
  rank: number;
  isExpanded: boolean;
  onToggle: () => void;
}) {
  const score = calculateWeightedScore(opp.scores, scoreWeights);
  const globalRank = getGlobalRank(opp);
  const medal = globalRank <= 3;

  return (
    <div
      className={`glass rounded-2xl overflow-hidden hover-lift transition-all duration-300 ${
        isExpanded ? "ring-1 ring-[var(--accent-blue)]/30" : ""
      }`}
    >
      {/* Header */}
      <button
        onClick={onToggle}
        className="w-full text-left p-5 lg:p-6 flex items-start gap-4 cursor-pointer"
      >
        {/* Rank Badge */}
        <div
          className={`flex-shrink-0 w-11 h-11 rounded-xl flex items-center justify-center text-sm font-bold ${
            medal
              ? "bg-gradient-to-br from-[var(--accent-blue)] to-[var(--accent-purple)] text-white"
              : "bg-white/5 text-[var(--text-secondary)]"
          }`}
        >
          {medal ? (
            <span className="text-lg">{["🥇", "🥈", "🥉"][globalRank - 1]}</span>
          ) : (
            `#${globalRank}`
          )}
        </div>

        {/* Content */}
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-3 flex-wrap">
            <span className="text-xl">{opp.icon}</span>
            <h3 className="font-semibold text-[var(--text-primary)] text-base lg:text-lg">
              {opp.shortName}
            </h3>
            {/* Score Chip */}
            <div
              className="px-2.5 py-1 rounded-lg text-xs font-bold"
              style={{
                background: `${scoreColor(score)}15`,
                color: scoreColor(score),
              }}
            >
              {score.toFixed(1)}
            </div>
          </div>

          <p className="text-sm text-[var(--text-secondary)] mt-1.5 leading-relaxed">
            {opp.tagline}
          </p>

          {/* Quick Stats */}
          <div className="flex flex-wrap gap-x-6 gap-y-1.5 mt-3">
            <Stat label="TAM" value={opp.tam} />
            <Stat label="Monthly" value={opp.monthlyPotential} />
            <Stat label="Time" value={opp.timeToRevenue} />
            <Stat label="ROI" value={opp.roi} />
          </div>
        </div>

        {/* Chevron */}
        <svg
          className={`w-5 h-5 text-[var(--text-muted)] transition-transform duration-300 shrink-0 mt-1 ${
            isExpanded ? "rotate-180" : ""
          }`}
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
          strokeWidth={2}
        >
          <path strokeLinecap="round" strokeLinejoin="round" d="M19 9l-7 7-7-7" />
        </svg>
      </button>

      {/* Expanded Detail */}
      {isExpanded && (
        <div className="px-5 lg:px-6 pb-6 border-t border-white/5 animate-fade-in">
          {/* Insight + ROI Row */}
          <div className="grid md:grid-cols-2 gap-4 mt-5">
            <div className="rounded-xl bg-[var(--accent-blue)]/10 border border-[var(--accent-blue)]/20 p-4">
              <p className="text-xs font-semibold text-[var(--accent-blue)] uppercase tracking-wider mb-1.5">
                Key Insight
              </p>
              <p className="text-sm text-[var(--text-primary)] leading-relaxed">
                {opp.keyInsight}
              </p>
            </div>
            <div className="rounded-xl bg-[var(--accent-emerald)]/10 border border-[var(--accent-emerald)]/20 p-4">
              <p className="text-xs font-semibold text-[var(--accent-emerald)] uppercase tracking-wider mb-1.5">
                Return on Investment
              </p>
              <p className="text-2xl font-bold text-[var(--accent-emerald)]">
                {opp.roi}
              </p>
              <p className="text-xs text-[var(--text-secondary)] mt-1">
                Monthly potential: {opp.monthlyPotential}
              </p>
            </div>
          </div>

          {/* Score Bars */}
          <div className="mt-5">
            <p className="text-xs font-semibold text-[var(--text-muted)] uppercase tracking-wider mb-3">
              Dimension Scores
            </p>
            <div className="space-y-2.5">
              <ScoreBar label="Revenue" value={opp.scores.revenue} />
              <ScoreBar label="Market Size" value={opp.scores.marketSize} />
              <ScoreBar label="Ease of Build" value={opp.scores.easeOfBuild} />
              <ScoreBar label="Low Complexity" value={opp.scores.complexity} />
              <ScoreBar label="Hard to Copy" value={opp.scores.replication} />
              <ScoreBar label="Low Competition" value={opp.scores.competition} />
              <ScoreBar label="Market Gap" value={opp.scores.marketGap} />
              <ScoreBar label="Autonomy" value={opp.scores.autonomy} />
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

function Stat({ label, value }: { label: string; value: string }) {
  return (
    <div className="text-sm">
      <span className="text-[var(--text-muted)]">{label} </span>
      <span className="font-medium text-[var(--text-primary)]">{value}</span>
    </div>
  );
}

/* ─── Top 3 Showcase ─── */
function TopThreeShowcase() {
  const top3 = [...opportunities]
    .sort(
      (a, b) =>
        calculateWeightedScore(b.scores, scoreWeights) -
        calculateWeightedScore(a.scores, scoreWeights)
    )
    .slice(0, 3);

  const gradients = [
    "from-yellow-500/20 to-amber-500/5 border-yellow-500/30",
    "from-gray-400/15 to-gray-500/5 border-gray-400/25",
    "from-amber-700/15 to-amber-800/5 border-amber-700/25",
  ];
  const labels = ["Gold", "Silver", "Bronze"];

  return (
    <div className="grid md:grid-cols-3 gap-4 mb-10">
      {top3.map((opp, i) => {
        const score = calculateWeightedScore(opp.scores, scoreWeights);
        return (
          <div
            key={opp.id}
            className={`rounded-2xl bg-gradient-to-b ${gradients[i]} border p-6 hover-lift pulse-glow`}
          >
            <div className="flex items-center gap-2 mb-3">
              <span className="text-2xl">
                {["🥇", "🥈", "🥉"][i]}
              </span>
              <span className="text-xs font-bold uppercase tracking-wider text-[var(--text-secondary)]">
                {labels[i]}
              </span>
            </div>
            <div className="flex items-center gap-2 mb-2">
              <span className="text-xl">{opp.icon}</span>
              <h3 className="font-bold text-lg text-[var(--text-primary)]">
                {opp.shortName}
              </h3>
            </div>
            <p className="text-sm text-[var(--text-secondary)] leading-relaxed mb-4">
              {opp.tagline}
            </p>
            <div className="flex items-baseline gap-2">
              <span className="text-3xl font-black gradient-text">
                {score.toFixed(1)}
              </span>
              <span className="text-sm text-[var(--text-muted)]">/ 10</span>
            </div>
            <div className="grid grid-cols-2 gap-2 mt-4 text-xs">
              <div className="bg-white/5 rounded-lg px-3 py-2">
                <span className="text-[var(--text-muted)]">TAM</span>
                <div className="font-semibold text-[var(--text-primary)] mt-0.5">{opp.tam}</div>
              </div>
              <div className="bg-white/5 rounded-lg px-3 py-2">
                <span className="text-[var(--text-muted)]">Revenue</span>
                <div className="font-semibold text-[var(--text-primary)] mt-0.5">{opp.monthlyPotential}</div>
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
}

/* ─── Sort Tabs ─── */
function SortTabs({
  active,
  onChange,
}: {
  active: string;
  onChange: (v: string) => void;
}) {
  const tabs = [
    { key: "score", label: "Overall Score", icon: "◆" },
    { key: "revenue", label: "Revenue", icon: "$" },
    { key: "ease", label: "Easiest Build", icon: "⚡" },
    { key: "autonomy", label: "Most Autonomous", icon: "🤖" },
  ];
  return (
    <div className="flex flex-wrap gap-2 mb-6">
      {tabs.map((t) => (
        <button
          key={t.key}
          onClick={() => onChange(t.key)}
          className={`px-4 py-2 rounded-xl text-sm font-medium transition-all duration-200 cursor-pointer ${
            active === t.key
              ? "bg-gradient-to-r from-[var(--accent-blue)] to-[var(--accent-purple)] text-white shadow-lg shadow-[var(--accent-blue)]/20"
              : "glass text-[var(--text-secondary)] hover:text-[var(--text-primary)]"
          }`}
        >
          <span className="mr-1.5">{t.icon}</span>
          {t.label}
        </button>
      ))}
    </div>
  );
}

/* ─── Main Page ─── */
export default function Home() {
  const [openId, setOpenId] = useState<number | null>(null);
  const [sortBy, setSortBy] = useState("score");

  const sorted = useMemo(() => getSortedOpportunities(sortBy), [sortBy]);

  return (
    <>
      {/* Background Mesh */}
      <div className="bg-mesh" />

      <div className="relative z-10">
        {/* ─── Hero ─── */}
        <header className="max-w-6xl mx-auto px-5 pt-16 pb-12">
          {/* Nav */}
          <nav className="flex items-center justify-between mb-16">
            <div className="flex items-center gap-3">
              <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-[var(--accent-blue)] to-[var(--accent-purple)] flex items-center justify-center">
                <span className="text-white text-sm font-black">L×D</span>
              </div>
              <span className="font-bold text-lg tracking-tight">LMS×DR</span>
            </div>
            <div className="flex items-center gap-4 text-sm text-[var(--text-secondary)]">
              <a href="#opportunities" className="hover:text-[var(--text-primary)] transition-colors">
                Rankings
              </a>
              <a href="#methodology" className="hover:text-[var(--text-primary)] transition-colors">
                Methodology
              </a>
            </div>
          </nav>

          {/* Hero Content */}
          <div className="max-w-3xl">
            <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full glass text-xs font-medium text-[var(--accent-cyan)] mb-6">
              <span className="w-1.5 h-1.5 rounded-full bg-[var(--accent-cyan)] animate-pulse" />
              Powered by 5 parallel deep-research AI agents
            </div>
            <h1 className="text-4xl lg:text-6xl font-black leading-tight tracking-tight">
              AI Business
              <br />
              <span className="gradient-text">Opportunity Intelligence</span>
            </h1>
            <p className="text-lg text-[var(--text-secondary)] mt-5 leading-relaxed max-w-2xl">
              12 high-potential AI business opportunities — scored across 8 dimensions,
              weighted by market reality, ranked by buildability. Research-backed. Data-driven.
            </p>
          </div>

          <HeroStats />
        </header>

        {/* ─── Top 3 ─── */}
        <section className="max-w-6xl mx-auto px-5 pb-8">
          <h2 className="text-xl font-bold mb-6 flex items-center gap-2">
            <span className="w-1 h-6 rounded-full bg-gradient-to-b from-[var(--accent-blue)] to-[var(--accent-purple)]" />
            Top Ranked
          </h2>
          <TopThreeShowcase />
        </section>

        {/* ─── All Opportunities ─── */}
        <section id="opportunities" className="max-w-6xl mx-auto px-5 pb-16">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6">
            <h2 className="text-xl font-bold flex items-center gap-2">
              <span className="w-1 h-6 rounded-full bg-gradient-to-b from-[var(--accent-cyan)] to-[var(--accent-blue)]" />
              All Opportunities
            </h2>
            <SortTabs active={sortBy} onChange={setSortBy} />
          </div>

          <div className="space-y-3 stagger">
            {sorted.map((opp, idx) => (
              <OpportunityCard
                key={opp.id}
                opp={opp}
                rank={idx + 1}
                isExpanded={openId === opp.id}
                onToggle={() =>
                  setOpenId(openId === opp.id ? null : opp.id)
                }
              />
            ))}
          </div>
        </section>

        {/* ─── Methodology ─── */}
        <section id="methodology" className="max-w-6xl mx-auto px-5 pb-20">
          <div className="glass rounded-2xl p-8 lg:p-10">
            <h2 className="text-xl font-bold mb-6 flex items-center gap-2">
              <span className="w-1 h-6 rounded-full bg-gradient-to-b from-[var(--accent-purple)] to-[var(--accent-rose)]" />
              Methodology
            </h2>
            <div className="grid md:grid-cols-2 gap-8">
              <div>
                <h3 className="font-semibold text-[var(--text-primary)] mb-3">
                  8-Dimension Scoring
                </h3>
                <p className="text-sm text-[var(--text-secondary)] leading-relaxed">
                  Each opportunity is rated 1–10 across Revenue Potential, Market Size,
                  Ease of Build, Complexity, Replication Difficulty, Competition Level,
                  Market Gap, and Autonomy Potential.
                </p>
              </div>
              <div>
                <h3 className="font-semibold text-[var(--text-primary)] mb-3">
                  Weighted Composite
                </h3>
                <p className="text-sm text-[var(--text-secondary)] leading-relaxed">
                  Scores are weighted by practical importance — Revenue (1.5x), Market Gap (1.4x),
                  Ease of Build (1.3x), Autonomy (1.3x), Market Size (1.2x), Competition (1.2x),
                  Replication (1.1x), and Complexity (1.0x).
                </p>
              </div>
              <div>
                <h3 className="font-semibold text-[var(--text-primary)] mb-3">
                  Research Sources
                </h3>
                <p className="text-sm text-[var(--text-secondary)] leading-relaxed">
                  Data compiled from 5 parallel deep-research agents analyzing market reports,
                  founder interviews, industry databases, and competitive intelligence. March 2026.
                </p>
              </div>
              <div>
                <h3 className="font-semibold text-[var(--text-primary)] mb-3">
                  How to Use This
                </h3>
                <p className="text-sm text-[var(--text-secondary)] leading-relaxed">
                  Sort by what matters to you. Click any card to drill into dimension scores,
                  key insights, and ROI projections. Top 3 are highlighted for quick scanning.
                </p>
              </div>
            </div>
          </div>
        </section>

        {/* ─── Footer ─── */}
        <footer className="border-t border-white/5 py-8">
          <div className="max-w-6xl mx-auto px-5 flex flex-col sm:flex-row items-center justify-between gap-4">
            <div className="flex items-center gap-2 text-sm text-[var(--text-muted)]">
              <div className="w-6 h-6 rounded-lg bg-gradient-to-br from-[var(--accent-blue)] to-[var(--accent-purple)] flex items-center justify-center">
                <span className="text-white text-[10px] font-black">L</span>
              </div>
              LMS×DR Intelligence — Learning × Demand Analysis Platform
            </div>
            <div className="text-xs text-[var(--text-muted)]">
              Built with AI deep-research agents
            </div>
          </div>
        </footer>
      </div>
    </>
  );
}
