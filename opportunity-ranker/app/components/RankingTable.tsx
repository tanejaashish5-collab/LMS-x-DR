"use client";

import { motion } from "framer-motion";
import type { Opportunity } from "../data/opportunities";
import {
  calculateWeightedScore,
  scoreLabels,
  scoreWeights,
} from "../data/opportunities";

function getMedalStyle(rank: number): string {
  if (rank === 0) return "glow-gold border-yellow-400/50";
  if (rank === 1) return "glow-silver border-slate-400/50";
  if (rank === 2) return "glow-bronze border-amber-600/50";
  return "border-purple-900/30";
}

function getMedalEmoji(rank: number): string {
  if (rank === 0) return "🥇";
  if (rank === 1) return "🥈";
  if (rank === 2) return "🥉";
  return `#${rank + 1}`;
}

export default function RankingTable({
  opportunities,
  selectedId,
  onSelect,
  customWeights,
}: {
  opportunities: Opportunity[];
  selectedId: number | null;
  onSelect: (id: number) => void;
  customWeights: Record<keyof Opportunity["scores"], number>;
}) {
  const sorted = [...opportunities]
    .map((o) => ({
      ...o,
      weightedScore: calculateWeightedScore(o.scores, customWeights),
    }))
    .sort((a, b) => b.weightedScore - a.weightedScore);

  return (
    <div className="space-y-2">
      {sorted.map((opp, rank) => (
        <motion.div
          key={opp.id}
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: rank * 0.05 }}
          onClick={() => onSelect(opp.id)}
          className={`
            flex items-center gap-4 p-3 rounded-xl cursor-pointer transition-all duration-300
            border ${getMedalStyle(rank)}
            ${selectedId === opp.id ? "bg-purple-900/30 ring-2 ring-purple-500/50" : "bg-gray-900/40 hover:bg-gray-800/50"}
          `}
        >
          {/* Rank */}
          <div className="text-lg font-bold w-10 text-center shrink-0">
            {getMedalEmoji(rank)}
          </div>

          {/* Icon + Name */}
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2">
              <span className="text-lg">{opp.icon}</span>
              <span className="font-semibold text-sm truncate">{opp.shortName}</span>
            </div>
            <div className="text-xs text-gray-500 truncate">{opp.tam} TAM</div>
          </div>

          {/* Score */}
          <div className="text-right shrink-0">
            <div
              className="text-xl font-black"
              style={{ color: opp.color }}
            >
              {opp.weightedScore.toFixed(1)}
            </div>
            <div className="text-[10px] text-gray-500 uppercase tracking-wider">
              score
            </div>
          </div>

          {/* Mini bar */}
          <div className="w-20 shrink-0">
            <div className="h-2 bg-gray-800 rounded-full overflow-hidden">
              <motion.div
                initial={{ width: 0 }}
                animate={{ width: `${(opp.weightedScore / 10) * 100}%` }}
                transition={{ duration: 0.6, delay: rank * 0.05 }}
                className="h-full rounded-full"
                style={{ backgroundColor: opp.color }}
              />
            </div>
          </div>
        </motion.div>
      ))}
    </div>
  );
}
