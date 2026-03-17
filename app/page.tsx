"use client";

import { useState } from "react";
import { opportunities, calculateWeightedScore, scoreWeights } from "./data/opportunities";
import type { Opportunity } from "./data/opportunities";

function getRank(opp: Opportunity, all: Opportunity[]): number {
  const sorted = [...all].sort(
    (a, b) =>
      calculateWeightedScore(b.scores, scoreWeights) -
      calculateWeightedScore(a.scores, scoreWeights)
  );
  return sorted.findIndex((o) => o.id === opp.id) + 1;
}

function ScorePill({ value }: { value: number }) {
  const bg =
    value >= 8
      ? "bg-emerald-100 text-emerald-700"
      : value >= 6
        ? "bg-amber-100 text-amber-700"
        : "bg-red-100 text-red-700";
  return (
    <span className={`inline-block px-2 py-0.5 rounded-full text-xs font-bold ${bg}`}>
      {value}/10
    </span>
  );
}

function OpportunityCard({
  opp,
  rank,
  isOpen,
  onToggle,
}: {
  opp: Opportunity;
  rank: number;
  isOpen: boolean;
  onToggle: () => void;
}) {
  const score = calculateWeightedScore(opp.scores, scoreWeights);
  const medalColors: Record<number, string> = {
    1: "border-l-yellow-400",
    2: "border-l-gray-400",
    3: "border-l-amber-600",
  };
  const borderClass = medalColors[rank] || "border-l-gray-200";

  return (
    <div
      className={`bg-white rounded-xl border border-gray-200 border-l-4 ${borderClass} shadow-sm hover:shadow-md transition-shadow`}
    >
      {/* Card Header — always visible */}
      <button
        onClick={onToggle}
        className="w-full text-left p-5 flex items-start gap-4 cursor-pointer"
      >
        {/* Rank */}
        <div className="flex-shrink-0 w-10 h-10 rounded-full bg-gray-100 flex items-center justify-center">
          {rank <= 3 ? (
            <span className="text-lg">{["🥇", "🥈", "🥉"][rank - 1]}</span>
          ) : (
            <span className="text-sm font-bold text-gray-500">#{rank}</span>
          )}
        </div>

        {/* Main Info */}
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 flex-wrap">
            <span className="text-lg">{opp.icon}</span>
            <h3 className="font-semibold text-gray-900 text-base">{opp.shortName}</h3>
            <span className="text-xs font-bold text-white bg-gray-800 rounded-full px-2.5 py-0.5">
              {score.toFixed(1)}
            </span>
          </div>
          <p className="text-sm text-gray-500 mt-1 leading-snug">{opp.tagline}</p>

          {/* Quick Stats Row */}
          <div className="flex flex-wrap gap-x-5 gap-y-1 mt-3 text-sm">
            <div>
              <span className="text-gray-400">TAM </span>
              <span className="font-semibold text-gray-700">{opp.tam}</span>
            </div>
            <div>
              <span className="text-gray-400">Revenue </span>
              <span className="font-semibold text-gray-700">{opp.monthlyPotential}/mo</span>
            </div>
            <div>
              <span className="text-gray-400">Time </span>
              <span className="font-semibold text-gray-700">{opp.timeToRevenue}</span>
            </div>
          </div>
        </div>

        {/* Expand Arrow */}
        <div className="flex-shrink-0 pt-1">
          <svg
            className={`w-5 h-5 text-gray-400 transition-transform ${isOpen ? "rotate-180" : ""}`}
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
            strokeWidth={2}
          >
            <path strokeLinecap="round" strokeLinejoin="round" d="M19 9l-7 7-7-7" />
          </svg>
        </div>
      </button>

      {/* Expanded Detail */}
      {isOpen && (
        <div className="px-5 pb-5 pt-0 border-t border-gray-100">
          {/* Key Insight */}
          <div className="bg-blue-50 rounded-lg p-3 mt-4 mb-4">
            <p className="text-sm font-medium text-blue-800">
              Key Insight
            </p>
            <p className="text-sm text-blue-700 mt-1">{opp.keyInsight}</p>
          </div>

          {/* ROI */}
          <div className="bg-emerald-50 rounded-lg p-3 mb-4">
            <p className="text-sm font-medium text-emerald-800">
              ROI: <span className="font-bold">{opp.roi}</span>
            </p>
          </div>

          {/* Scores Grid */}
          <p className="text-xs font-semibold text-gray-400 uppercase tracking-wide mb-2">
            Scores
          </p>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
            {([
              ["Revenue", opp.scores.revenue],
              ["Market Size", opp.scores.marketSize],
              ["Ease of Build", opp.scores.easeOfBuild],
              ["Low Complexity", opp.scores.complexity],
              ["Hard to Copy", opp.scores.replication],
              ["Low Competition", opp.scores.competition],
              ["Market Gap", opp.scores.marketGap],
              ["Autonomy", opp.scores.autonomy],
            ] as [string, number][]).map(([label, value]) => (
              <div key={label} className="flex items-center justify-between bg-gray-50 rounded-lg px-3 py-2">
                <span className="text-xs text-gray-500">{label}</span>
                <ScorePill value={value} />
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

export default function Home() {
  const [openId, setOpenId] = useState<number | null>(null);
  const [sortBy, setSortBy] = useState<"score" | "revenue" | "ease">("score");

  const sorted = [...opportunities].sort((a, b) => {
    if (sortBy === "revenue") return b.scores.revenue - a.scores.revenue;
    if (sortBy === "ease") return b.scores.easeOfBuild - a.scores.easeOfBuild;
    return (
      calculateWeightedScore(b.scores, scoreWeights) -
      calculateWeightedScore(a.scores, scoreWeights)
    );
  });

  return (
    <main className="max-w-3xl mx-auto px-4 py-10">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">
          AI Business Opportunities
        </h1>
        <p className="text-gray-500 mt-2">
          12 opportunities ranked by potential. Click any card to see details.
        </p>
      </div>

      {/* Sort Bar */}
      <div className="flex items-center gap-2 mb-6">
        <span className="text-sm text-gray-400">Sort by:</span>
        {([
          ["score", "Overall Score"],
          ["revenue", "Revenue"],
          ["ease", "Easiest to Build"],
        ] as [typeof sortBy, string][]).map(([key, label]) => (
          <button
            key={key}
            onClick={() => setSortBy(key)}
            className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${
              sortBy === key
                ? "bg-gray-900 text-white"
                : "bg-gray-100 text-gray-600 hover:bg-gray-200"
            }`}
          >
            {label}
          </button>
        ))}
      </div>

      {/* Cards */}
      <div className="space-y-3">
        {sorted.map((opp) => (
          <OpportunityCard
            key={opp.id}
            opp={opp}
            rank={getRank(opp, opportunities)}
            isOpen={openId === opp.id}
            onToggle={() => setOpenId(openId === opp.id ? null : opp.id)}
          />
        ))}
      </div>

      {/* Footer */}
      <div className="text-center text-xs text-gray-400 mt-10 pb-8">
        Research compiled March 2026 from 5 parallel deep-research agents.
      </div>
    </main>
  );
}
