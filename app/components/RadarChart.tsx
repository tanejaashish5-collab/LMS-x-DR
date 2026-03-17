"use client";

import { motion } from "framer-motion";
import type { Opportunity } from "../data/opportunities";
import { scoreLabels } from "../data/opportunities";

function polarToCartesian(
  cx: number,
  cy: number,
  radius: number,
  angleInDeg: number
): { x: number; y: number } {
  const angleInRad = ((angleInDeg - 90) * Math.PI) / 180;
  return {
    x: cx + radius * Math.cos(angleInRad),
    y: cy + radius * Math.sin(angleInRad),
  };
}

export default function RadarChart({
  opportunity,
  compareWith,
  size = 280,
}: {
  opportunity: Opportunity;
  compareWith?: Opportunity | null;
  size?: number;
}) {
  const cx = size / 2;
  const cy = size / 2;
  const maxR = size * 0.38;
  const keys = Object.keys(opportunity.scores) as (keyof Opportunity["scores"])[];
  const angleStep = 360 / keys.length;

  function getPolygonPoints(scores: Opportunity["scores"]): string {
    return keys
      .map((key, i) => {
        const r = (scores[key] / 10) * maxR;
        const { x, y } = polarToCartesian(cx, cy, r, i * angleStep);
        return `${x},${y}`;
      })
      .join(" ");
  }

  const gridLevels = [2, 4, 6, 8, 10];

  return (
    <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`} className="mx-auto">
      {/* Grid */}
      {gridLevels.map((level) => (
        <polygon
          key={level}
          points={keys
            .map((_, i) => {
              const r = (level / 10) * maxR;
              const { x, y } = polarToCartesian(cx, cy, r, i * angleStep);
              return `${x},${y}`;
            })
            .join(" ")}
          fill="none"
          stroke="rgba(124,58,237,0.15)"
          strokeWidth={1}
        />
      ))}

      {/* Axis lines */}
      {keys.map((_, i) => {
        const { x, y } = polarToCartesian(cx, cy, maxR, i * angleStep);
        return (
          <line
            key={i}
            x1={cx}
            y1={cy}
            x2={x}
            y2={y}
            stroke="rgba(124,58,237,0.1)"
            strokeWidth={1}
          />
        );
      })}

      {/* Comparison polygon */}
      {compareWith && (
        <motion.polygon
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          points={getPolygonPoints(compareWith.scores)}
          fill={`${compareWith.color}15`}
          stroke={compareWith.color}
          strokeWidth={1.5}
          strokeDasharray="4 4"
        />
      )}

      {/* Main polygon */}
      <motion.polygon
        initial={{ opacity: 0, scale: 0 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.5, type: "spring" }}
        style={{ transformOrigin: `${cx}px ${cy}px` }}
        points={getPolygonPoints(opportunity.scores)}
        fill={`${opportunity.color}25`}
        stroke={opportunity.color}
        strokeWidth={2}
      />

      {/* Data points */}
      {keys.map((key, i) => {
        const r = (opportunity.scores[key] / 10) * maxR;
        const { x, y } = polarToCartesian(cx, cy, r, i * angleStep);
        return (
          <motion.circle
            key={key}
            initial={{ r: 0 }}
            animate={{ r: 4 }}
            transition={{ delay: 0.1 * i }}
            cx={x}
            cy={y}
            fill={opportunity.color}
            stroke="white"
            strokeWidth={1.5}
          />
        );
      })}

      {/* Labels */}
      {keys.map((key, i) => {
        const { x, y } = polarToCartesian(cx, cy, maxR + 22, i * angleStep);
        const shortLabel = scoreLabels[key].split(" ").slice(0, 2).join(" ");
        return (
          <text
            key={key}
            x={x}
            y={y}
            textAnchor="middle"
            dominantBaseline="middle"
            fill="#8888aa"
            fontSize={9}
            fontFamily="system-ui"
          >
            {shortLabel}
          </text>
        );
      })}
    </svg>
  );
}
