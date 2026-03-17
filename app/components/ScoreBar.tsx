"use client";

import { motion } from "framer-motion";

export default function ScoreBar({
  label,
  score,
  color,
  delay = 0,
  maxScore = 10,
}: {
  label: string;
  score: number;
  color: string;
  delay?: number;
  maxScore?: number;
}) {
  const pct = (score / maxScore) * 100;

  return (
    <div className="flex items-center gap-3">
      <span className="text-xs text-gray-400 w-28 text-right shrink-0">
        {label}
      </span>
      <div className="flex-1 h-3 bg-gray-800 rounded-full overflow-hidden relative">
        <motion.div
          initial={{ width: 0 }}
          animate={{ width: `${pct}%` }}
          transition={{ duration: 0.8, delay, ease: "easeOut" }}
          className="h-full rounded-full relative"
          style={{ background: `linear-gradient(90deg, ${color}88, ${color})` }}
        >
          <div
            className="absolute inset-0 rounded-full"
            style={{
              background: `linear-gradient(180deg, rgba(255,255,255,0.15) 0%, transparent 60%)`,
            }}
          />
        </motion.div>
      </div>
      <span
        className="text-sm font-bold w-8 text-right"
        style={{ color }}
      >
        {score}
      </span>
    </div>
  );
}
