"use client";

import { scoreLabels } from "../data/opportunities";
import type { Opportunity } from "../data/opportunities";

const sliderDescriptions: Record<keyof Opportunity["scores"], string> = {
  revenue: "How much money can this make?",
  marketSize: "How big is the total addressable market?",
  easeOfBuild: "How quickly can you ship an MVP?",
  complexity: "Lower complexity = faster iteration",
  replication: "How hard is it for competitors to copy?",
  competition: "How few competitors exist today?",
  marketGap: "How wide is the gap between need & solution?",
  autonomy: "Can it run fully hands-off with AI?",
};

export default function WeightSliders({
  weights,
  onChange,
}: {
  weights: Record<keyof Opportunity["scores"], number>;
  onChange: (key: keyof Opportunity["scores"], value: number) => void;
}) {
  const keys = Object.keys(weights) as (keyof Opportunity["scores"])[];

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between mb-2">
        <h3 className="text-sm font-semibold text-purple-300 uppercase tracking-wider">
          Adjust Weights
        </h3>
        <span className="text-[10px] text-gray-500">
          Drag to reprioritize what matters to you
        </span>
      </div>
      {keys.map((key) => (
        <div key={key} className="space-y-1">
          <div className="flex items-center justify-between">
            <label className="text-xs text-gray-300">{scoreLabels[key]}</label>
            <span className="text-xs font-mono text-purple-400">
              {weights[key].toFixed(1)}x
            </span>
          </div>
          <div className="text-[10px] text-gray-600 mb-1">
            {sliderDescriptions[key]}
          </div>
          <input
            type="range"
            min="0"
            max="3"
            step="0.1"
            value={weights[key]}
            onChange={(e) => onChange(key, parseFloat(e.target.value))}
            className="w-full h-1.5 rounded-full appearance-none cursor-pointer
              bg-gray-800
              [&::-webkit-slider-thumb]:appearance-none
              [&::-webkit-slider-thumb]:w-4
              [&::-webkit-slider-thumb]:h-4
              [&::-webkit-slider-thumb]:rounded-full
              [&::-webkit-slider-thumb]:bg-purple-500
              [&::-webkit-slider-thumb]:shadow-[0_0_10px_rgba(124,58,237,0.5)]
              [&::-webkit-slider-thumb]:cursor-pointer
              [&::-webkit-slider-thumb]:transition-all
              [&::-webkit-slider-thumb]:hover:bg-purple-400
              [&::-webkit-slider-thumb]:hover:scale-125"
          />
        </div>
      ))}
    </div>
  );
}
