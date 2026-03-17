"use client";

import { useState, useMemo, Suspense } from "react";
import dynamic from "next/dynamic";
import { motion, AnimatePresence } from "framer-motion";
import {
  opportunities,
  scoreWeights,
  calculateWeightedScore,
  scoreLabels,
} from "./data/opportunities";
import type { Opportunity } from "./data/opportunities";
import RankingTable from "./components/RankingTable";
import DetailPanel from "./components/DetailPanel";
import WeightSliders from "./components/WeightSliders";
import CompareMode from "./components/CompareMode";

const Scene3D = dynamic(() => import("./components/Scene3D"), {
  ssr: false,
  loading: () => (
    <div className="w-full h-[500px] rounded-2xl bg-gray-900/50 flex items-center justify-center border border-purple-900/30">
      <div className="text-purple-400 animate-pulse">Loading 3D Universe...</div>
    </div>
  ),
});

type ViewMode = "ranking" | "compare" | "matrix";

export default function Home() {
  const [selectedId, setSelectedId] = useState<number | null>(null);
  const [compareId, setCompareId] = useState<number | null>(null);
  const [viewMode, setViewMode] = useState<ViewMode>("ranking");
  const [showWeights, setShowWeights] = useState(false);
  const [show3D, setShow3D] = useState(true);
  const [customWeights, setCustomWeights] =
    useState<Record<keyof Opportunity["scores"], number>>(scoreWeights);

  const sorted = useMemo(
    () =>
      [...opportunities]
        .map((o) => ({
          ...o,
          weightedScore: calculateWeightedScore(o.scores, customWeights),
        }))
        .sort((a, b) => b.weightedScore - a.weightedScore),
    [customWeights]
  );

  const selected = opportunities.find((o) => o.id === selectedId) ?? null;
  const compared = opportunities.find((o) => o.id === compareId) ?? null;
  const selectedRank = selected
    ? sorted.findIndex((o) => o.id === selected.id) + 1
    : 0;

  function handleWeightChange(
    key: keyof Opportunity["scores"],
    value: number
  ) {
    setCustomWeights((prev) => ({ ...prev, [key]: value }));
  }

  function handleSelect(id: number) {
    if (viewMode === "compare") {
      if (selectedId === null) {
        setSelectedId(id);
      } else if (compareId === null && id !== selectedId) {
        setCompareId(id);
      } else {
        setSelectedId(id);
        setCompareId(null);
      }
    } else {
      setSelectedId(id === selectedId ? null : id);
    }
  }

  const keys = Object.keys(scoreWeights) as (keyof Opportunity["scores"])[];

  return (
    <main className="max-w-[1400px] mx-auto px-4 py-8 space-y-8">
      {/* Hero */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="text-center space-y-3"
      >
        <h1 className="text-4xl md:text-5xl font-black bg-gradient-to-r from-purple-400 via-pink-400 to-yellow-400 bg-clip-text text-transparent">
          Hidden Gold Mines
        </h1>
        <p className="text-gray-400 text-sm md:text-base max-w-2xl mx-auto">
          Interactive ranking of 12 AI-powered business opportunities.
          Scored across 8 dimensions. Adjust weights to match{" "}
          <span className="text-purple-300 font-semibold">your</span> priorities.
        </p>

        {/* Controls */}
        <div className="flex flex-wrap items-center justify-center gap-2 pt-2">
          {(["ranking", "compare", "matrix"] as ViewMode[]).map((mode) => (
            <button
              key={mode}
              onClick={() => {
                setViewMode(mode);
                if (mode !== "compare") setCompareId(null);
              }}
              className={`px-4 py-1.5 rounded-full text-xs font-semibold uppercase tracking-wider transition-all
                ${viewMode === mode
                  ? "bg-purple-600 text-white shadow-[0_0_15px_rgba(124,58,237,0.4)]"
                  : "bg-gray-800/50 text-gray-400 hover:bg-gray-700/50"
                }`}
            >
              {mode === "ranking" && "Ranking"}
              {mode === "compare" && "Compare"}
              {mode === "matrix" && "Matrix"}
            </button>
          ))}
          <div className="w-px h-6 bg-gray-700" />
          <button
            onClick={() => setShow3D(!show3D)}
            className={`px-4 py-1.5 rounded-full text-xs font-semibold transition-all
              ${show3D ? "bg-blue-600/20 text-blue-300 border border-blue-500/30" : "bg-gray-800/50 text-gray-500"}`}
          >
            3D View
          </button>
          <button
            onClick={() => setShowWeights(!showWeights)}
            className={`px-4 py-1.5 rounded-full text-xs font-semibold transition-all
              ${showWeights ? "bg-yellow-600/20 text-yellow-300 border border-yellow-500/30" : "bg-gray-800/50 text-gray-500"}`}
          >
            Weight Tuner
          </button>
        </div>
      </motion.div>

      {/* Compare mode hint */}
      {viewMode === "compare" && !compareId && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="text-center text-xs text-purple-300 bg-purple-900/20 rounded-lg py-2"
        >
          {!selectedId
            ? "Click the first opportunity to compare"
            : "Now click a second opportunity to compare against"}
        </motion.div>
      )}

      {/* 3D Scene */}
      <AnimatePresence>
        {show3D && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: "auto" }}
            exit={{ opacity: 0, height: 0 }}
            transition={{ duration: 0.3 }}
          >
            <Suspense fallback={null}>
              <Scene3D
                opportunities={opportunities}
                selectedId={selectedId}
                onSelect={handleSelect}
              />
            </Suspense>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Weight Sliders Panel */}
        <AnimatePresence>
          {showWeights && (
            <motion.div
              initial={{ opacity: 0, width: 0 }}
              animate={{ opacity: 1, width: "auto" }}
              exit={{ opacity: 0, width: 0 }}
              className="lg:col-span-3 glass rounded-2xl p-4 overflow-hidden"
            >
              <WeightSliders
                weights={customWeights}
                onChange={handleWeightChange}
              />
              <button
                onClick={() => setCustomWeights(scoreWeights)}
                className="w-full mt-4 text-xs text-gray-500 hover:text-purple-300 transition-colors py-2 border border-gray-800 rounded-lg"
              >
                Reset to Default Weights
              </button>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Ranking / Matrix */}
        <div className={showWeights ? "lg:col-span-4" : "lg:col-span-5"}>
          {viewMode === "matrix" ? (
            <MatrixView
              opportunities={sorted}
              selectedId={selectedId}
              onSelect={handleSelect}
            />
          ) : (
            <RankingTable
              opportunities={opportunities}
              selectedId={selectedId}
              onSelect={handleSelect}
              customWeights={customWeights}
            />
          )}
        </div>

        {/* Detail / Compare Panel */}
        <div className={showWeights ? "lg:col-span-5" : "lg:col-span-7"}>
          {viewMode === "compare" && selected && compared ? (
            <CompareMode a={selected} b={compared} />
          ) : (
            <DetailPanel
              opportunity={selected}
              compareWith={compared}
              rank={selectedRank}
            />
          )}
        </div>
      </div>

      {/* Footer stats */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.5 }}
        className="glass rounded-2xl p-6"
      >
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
          {[
            { label: "Opportunities Analyzed", value: "12" },
            { label: "Data Sources", value: "80+" },
            { label: "Combined TAM", value: "$1.4T+" },
            { label: "Research Agents Used", value: "5" },
          ].map((stat) => (
            <div key={stat.label}>
              <div className="text-2xl font-black bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">
                {stat.value}
              </div>
              <div className="text-xs text-gray-500 mt-1">{stat.label}</div>
            </div>
          ))}
        </div>
      </motion.div>

      {/* Source attribution */}
      <div className="text-center text-xs text-gray-600 pb-8">
        Research compiled March 2026 from 5 parallel deep-research agents.
        All statistics verified against original sources.
        <br />
        <span className="text-purple-500/50">
          Built with Next.js + Three.js + Framer Motion
        </span>
      </div>
    </main>
  );
}

/* ---- Matrix View Component ---- */
function MatrixView({
  opportunities,
  selectedId,
  onSelect,
}: {
  opportunities: (Opportunity & { weightedScore: number })[];
  selectedId: number | null;
  onSelect: (id: number) => void;
}) {
  const keys = Object.keys(scoreLabels) as (keyof Opportunity["scores"])[];

  return (
    <div className="glass rounded-2xl p-4 overflow-x-auto">
      <table className="w-full text-xs">
        <thead>
          <tr className="text-gray-500">
            <th className="text-left py-2 px-1 sticky left-0 bg-[var(--bg-card)]">
              Opportunity
            </th>
            {keys.map((k) => (
              <th key={k} className="py-2 px-1 text-center">
                {scoreLabels[k].split(" ")[0]}
              </th>
            ))}
            <th className="py-2 px-1 text-center text-purple-400">Total</th>
          </tr>
        </thead>
        <tbody>
          {opportunities.map((opp, rank) => (
            <tr
              key={opp.id}
              onClick={() => onSelect(opp.id)}
              className={`cursor-pointer transition-colors border-t border-gray-800/50
                ${selectedId === opp.id ? "bg-purple-900/20" : "hover:bg-gray-800/30"}`}
            >
              <td className="py-2 px-1 sticky left-0 bg-[var(--bg-card)] whitespace-nowrap">
                <span className="mr-1">{rank < 3 ? ["🥇", "🥈", "🥉"][rank] : `#${rank + 1}`}</span>
                <span className="mr-1">{opp.icon}</span>
                {opp.shortName}
              </td>
              {keys.map((k) => {
                const v = opp.scores[k];
                const bg =
                  v >= 8
                    ? "bg-green-500/20 text-green-300"
                    : v >= 6
                      ? "bg-yellow-500/15 text-yellow-300"
                      : v >= 4
                        ? "bg-orange-500/15 text-orange-300"
                        : "bg-red-500/15 text-red-300";
                return (
                  <td key={k} className="py-2 px-1 text-center">
                    <span className={`inline-block w-7 rounded-md py-0.5 ${bg} font-bold`}>
                      {v}
                    </span>
                  </td>
                );
              })}
              <td className="py-2 px-1 text-center font-black" style={{ color: opp.color }}>
                {opp.weightedScore.toFixed(1)}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
