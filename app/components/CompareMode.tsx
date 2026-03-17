"use client";

import { motion } from "framer-motion";
import type { Opportunity } from "../data/opportunities";
import {
  calculateWeightedScore,
  scoreLabels,
} from "../data/opportunities";

export default function CompareMode({
  a,
  b,
}: {
  a: Opportunity;
  b: Opportunity;
}) {
  const keys = Object.keys(a.scores) as (keyof Opportunity["scores"])[];
  const scoreA = calculateWeightedScore(a.scores);
  const scoreB = calculateWeightedScore(b.scores);

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="glass rounded-2xl p-6 space-y-4"
    >
      <h3 className="text-sm font-semibold text-purple-300 uppercase tracking-wider text-center">
        Head-to-Head Comparison
      </h3>

      {/* Header row */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <span className="text-2xl">{a.icon}</span>
          <div>
            <div className="font-bold text-sm" style={{ color: a.color }}>{a.shortName}</div>
            <div className="text-2xl font-black" style={{ color: a.color }}>{scoreA.toFixed(1)}</div>
          </div>
        </div>
        <div className="text-gray-600 text-xs font-bold">VS</div>
        <div className="flex items-center gap-2 text-right">
          <div>
            <div className="font-bold text-sm" style={{ color: b.color }}>{b.shortName}</div>
            <div className="text-2xl font-black" style={{ color: b.color }}>{scoreB.toFixed(1)}</div>
          </div>
          <span className="text-2xl">{b.icon}</span>
        </div>
      </div>

      {/* Score comparison bars */}
      <div className="space-y-3">
        {keys.map((key) => {
          const sA = a.scores[key];
          const sB = b.scores[key];
          const winner = sA > sB ? "a" : sB > sA ? "b" : "tie";

          return (
            <div key={key} className="space-y-1">
              <div className="flex items-center justify-between text-[10px] text-gray-500">
                <span className={winner === "a" ? "text-white font-bold" : ""}>
                  {sA}
                </span>
                <span className="uppercase tracking-wider">{scoreLabels[key]}</span>
                <span className={winner === "b" ? "text-white font-bold" : ""}>
                  {sB}
                </span>
              </div>
              <div className="flex gap-1 h-2">
                <div className="flex-1 flex justify-end">
                  <motion.div
                    initial={{ width: 0 }}
                    animate={{ width: `${(sA / 10) * 100}%` }}
                    transition={{ duration: 0.6 }}
                    className="h-full rounded-l-full"
                    style={{ backgroundColor: a.color }}
                  />
                </div>
                <div className="w-px bg-gray-700" />
                <div className="flex-1">
                  <motion.div
                    initial={{ width: 0 }}
                    animate={{ width: `${(sB / 10) * 100}%` }}
                    transition={{ duration: 0.6 }}
                    className="h-full rounded-r-full"
                    style={{ backgroundColor: b.color }}
                  />
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Summary */}
      <div className="text-center text-xs text-gray-500 pt-2 border-t border-gray-800">
        {scoreA > scoreB
          ? `${a.shortName} leads by ${(scoreA - scoreB).toFixed(1)} points`
          : scoreB > scoreA
            ? `${b.shortName} leads by ${(scoreB - scoreA).toFixed(1)} points`
            : "Dead heat!"}
      </div>
    </motion.div>
  );
}
