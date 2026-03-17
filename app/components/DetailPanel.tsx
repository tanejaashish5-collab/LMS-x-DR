"use client";

import { motion, AnimatePresence } from "framer-motion";
import type { Opportunity } from "../data/opportunities";
import {
  calculateWeightedScore,
  scoreLabels,
} from "../data/opportunities";
import RadarChart from "./RadarChart";
import ScoreBar from "./ScoreBar";

export default function DetailPanel({
  opportunity,
  compareWith,
  rank,
}: {
  opportunity: Opportunity | null;
  compareWith?: Opportunity | null;
  rank: number;
}) {
  if (!opportunity) {
    return (
      <div className="glass rounded-2xl p-8 text-center text-gray-500 h-full flex items-center justify-center">
        <div>
          <div className="text-4xl mb-4">👆</div>
          <p className="text-sm">Select an opportunity from the ranking<br />or click a sphere in the 3D view</p>
        </div>
      </div>
    );
  }

  const score = calculateWeightedScore(opportunity.scores);
  const keys = Object.keys(opportunity.scores) as (keyof Opportunity["scores"])[];

  return (
    <AnimatePresence mode="wait">
      <motion.div
        key={opportunity.id}
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: -20 }}
        transition={{ duration: 0.3 }}
        className="glass rounded-2xl p-6 space-y-5"
      >
        {/* Header */}
        <div className="flex items-start gap-4">
          <div
            className="text-4xl w-16 h-16 flex items-center justify-center rounded-xl"
            style={{ backgroundColor: `${opportunity.color}20` }}
          >
            {opportunity.icon}
          </div>
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2">
              <h2 className="text-lg font-bold truncate">{opportunity.name}</h2>
            </div>
            <p className="text-sm text-gray-400 italic mt-1">{opportunity.tagline}</p>
          </div>
          <div className="text-right shrink-0">
            <div className="text-3xl font-black" style={{ color: opportunity.color }}>
              {score.toFixed(1)}
            </div>
            <div className="text-xs text-gray-500">Rank #{rank}</div>
          </div>
        </div>

        {/* Key Metrics */}
        <div className="grid grid-cols-2 gap-3">
          {[
            { label: "TAM", value: opportunity.tam },
            { label: "Monthly Potential", value: opportunity.monthlyPotential },
            { label: "Time to Revenue", value: opportunity.timeToRevenue },
            { label: "ROI", value: opportunity.roi },
          ].map((m) => (
            <div key={m.label} className="bg-gray-900/50 rounded-lg p-3">
              <div className="text-[10px] text-gray-500 uppercase tracking-wider">{m.label}</div>
              <div className="text-sm font-bold mt-0.5" style={{ color: opportunity.color }}>
                {m.value}
              </div>
            </div>
          ))}
        </div>

        {/* Key Insight */}
        <div className="bg-yellow-900/10 border border-yellow-700/20 rounded-lg p-3">
          <div className="text-[10px] text-yellow-500 uppercase tracking-wider mb-1">Key Insight</div>
          <p className="text-xs text-gray-300 leading-relaxed">{opportunity.keyInsight}</p>
        </div>

        {/* Radar Chart */}
        <div className="flex justify-center">
          <RadarChart opportunity={opportunity} compareWith={compareWith} size={240} />
        </div>
        {compareWith && (
          <div className="flex items-center justify-center gap-4 text-xs text-gray-500">
            <span className="flex items-center gap-1">
              <span className="w-3 h-0.5 rounded" style={{ backgroundColor: opportunity.color }} />
              {opportunity.shortName}
            </span>
            <span className="flex items-center gap-1">
              <span className="w-3 h-0.5 rounded border-dashed border" style={{ borderColor: compareWith.color }} />
              {compareWith.shortName}
            </span>
          </div>
        )}

        {/* Score Breakdown */}
        <div className="space-y-2">
          <h3 className="text-xs text-gray-500 uppercase tracking-wider">Score Breakdown</h3>
          {keys.map((key, i) => (
            <ScoreBar
              key={key}
              label={scoreLabels[key]}
              score={opportunity.scores[key]}
              color={opportunity.color}
              delay={i * 0.05}
            />
          ))}
        </div>
      </motion.div>
    </AnimatePresence>
  );
}
