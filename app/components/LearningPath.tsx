"use client";

import { useState } from "react";

interface LearningModule {
  id: string;
  title: string;
  duration: string;
  difficulty: "Beginner" | "Intermediate" | "Advanced";
  topics: string[];
  completed?: boolean;
}

interface LearningPathProps {
  opportunityId: string;
  opportunityName: string;
}

const learningPaths: Record<string, LearningModule[]> = {
  "home-services": [
    {
      id: "hs-1",
      title: "Understanding the Home Services Market",
      duration: "2 hours",
      difficulty: "Beginner",
      topics: ["Market size", "Key players", "Pain points", "Opportunity gaps"],
    },
    {
      id: "hs-2",
      title: "Voice AI Fundamentals",
      duration: "3 hours",
      difficulty: "Intermediate",
      topics: ["Speech recognition", "NLP basics", "Voice UX design", "API integration"],
    },
    {
      id: "hs-3",
      title: "Building Your MVP",
      duration: "5 hours",
      difficulty: "Advanced",
      topics: ["Tech stack selection", "Voice workflow design", "Testing with contractors", "Go-to-market"],
    },
  ],
  "ar-collections": [
    {
      id: "ar-1",
      title: "The Collections Industry Landscape",
      duration: "2 hours",
      difficulty: "Beginner",
      topics: ["Industry overview", "Compliance requirements", "Key metrics", "Customer psychology"],
    },
    {
      id: "ar-2",
      title: "AI-Powered Communication",
      duration: "4 hours",
      difficulty: "Intermediate",
      topics: ["Sentiment analysis", "Message personalization", "Timing optimization", "Compliance automation"],
    },
    {
      id: "ar-3",
      title: "Implementation & Scale",
      duration: "6 hours",
      difficulty: "Advanced",
      topics: ["CRM integration", "Payment processing", "Performance tracking", "Enterprise sales"],
    },
  ],
};

export default function LearningPath({ opportunityId, opportunityName }: LearningPathProps) {
  const [expandedModules, setExpandedModules] = useState<Set<string>>(new Set());
  const [completedModules, setCompletedModules] = useState<Set<string>>(new Set());

  const modules = learningPaths[opportunityId] || [];
  const progress = modules.length > 0 ? (completedModules.size / modules.length) * 100 : 0;

  const toggleModule = (moduleId: string) => {
    setExpandedModules(prev => {
      const newSet = new Set(prev);
      if (newSet.has(moduleId)) {
        newSet.delete(moduleId);
      } else {
        newSet.add(moduleId);
      }
      return newSet;
    });
  };

  const toggleComplete = (moduleId: string) => {
    setCompletedModules(prev => {
      const newSet = new Set(prev);
      if (newSet.has(moduleId)) {
        newSet.delete(moduleId);
      } else {
        newSet.add(moduleId);
      }
      return newSet;
    });
  };

  const getDifficultyColor = (difficulty: string) => {
    switch(difficulty) {
      case "Beginner": return "#10b981";
      case "Intermediate": return "#f59e0b";
      case "Advanced": return "#ef4444";
      default: return "#6b7280";
    }
  };

  if (modules.length === 0) {
    return (
      <div className="mt-6 p-6 glass rounded-xl">
        <div className="flex items-center gap-3 mb-4">
          <span className="text-2xl">📚</span>
          <h3 className="text-lg font-bold">Learning Path</h3>
        </div>
        <p className="text-sm text-[var(--text-secondary)]">
          Learning modules for {opportunityName} are being developed by our AI agents.
        </p>
      </div>
    );
  }

  return (
    <div className="mt-6 p-6 glass rounded-xl">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <span className="text-2xl">📚</span>
          <h3 className="text-lg font-bold">Learning Path</h3>
        </div>
        <div className="flex items-center gap-3">
          <span className="text-sm text-[var(--text-secondary)]">
            {completedModules.size} of {modules.length} completed
          </span>
        </div>
      </div>

      {/* Progress Bar */}
      <div className="mb-6">
        <div className="h-2 bg-white/5 rounded-full overflow-hidden">
          <div
            className="h-full bg-gradient-to-r from-[var(--accent-blue)] to-[var(--accent-purple)] transition-all duration-500"
            style={{ width: `${progress}%` }}
          />
        </div>
      </div>

      {/* Modules */}
      <div className="space-y-3">
        {modules.map((module, index) => {
          const isExpanded = expandedModules.has(module.id);
          const isCompleted = completedModules.has(module.id);

          return (
            <div key={module.id} className="border border-white/10 rounded-lg overflow-hidden">
              <button
                onClick={() => toggleModule(module.id)}
                className="w-full p-4 text-left hover:bg-white/5 transition-colors"
              >
                <div className="flex items-start gap-4">
                  {/* Module Number */}
                  <div className={`
                    w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold
                    ${isCompleted
                      ? 'bg-green-500/20 text-green-400'
                      : 'bg-white/10 text-[var(--text-secondary)]'
                    }
                  `}>
                    {isCompleted ? '✓' : index + 1}
                  </div>

                  {/* Content */}
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-1">
                      <h4 className="font-semibold">{module.title}</h4>
                      <span
                        className="px-2 py-0.5 rounded text-xs font-medium"
                        style={{
                          backgroundColor: `${getDifficultyColor(module.difficulty)}20`,
                          color: getDifficultyColor(module.difficulty),
                        }}
                      >
                        {module.difficulty}
                      </span>
                    </div>
                    <div className="flex items-center gap-4 text-sm text-[var(--text-secondary)]">
                      <span>⏱ {module.duration}</span>
                      <span>• {module.topics.length} topics</span>
                    </div>
                  </div>

                  {/* Chevron */}
                  <svg
                    className={`w-5 h-5 text-[var(--text-muted)] transition-transform ${isExpanded ? 'rotate-180' : ''}`}
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                  </svg>
                </div>
              </button>

              {/* Expanded Content */}
              {isExpanded && (
                <div className="px-4 pb-4 border-t border-white/10">
                  <div className="pt-4">
                    <h5 className="text-sm font-semibold mb-2">Topics covered:</h5>
                    <ul className="space-y-1">
                      {module.topics.map((topic, i) => (
                        <li key={i} className="flex items-center gap-2 text-sm text-[var(--text-secondary)]">
                          <span className="text-[var(--accent-cyan)]">→</span>
                          {topic}
                        </li>
                      ))}
                    </ul>
                    <button
                      onClick={() => toggleComplete(module.id)}
                      className={`
                        mt-4 px-4 py-2 rounded-lg text-sm font-medium transition-all
                        ${isCompleted
                          ? 'bg-green-500/20 text-green-400 hover:bg-green-500/30'
                          : 'bg-[var(--accent-blue)]/20 text-[var(--accent-blue)] hover:bg-[var(--accent-blue)]/30'
                        }
                      `}
                    >
                      {isCompleted ? '✓ Completed' : 'Mark as Complete'}
                    </button>
                  </div>
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* Call to Action */}
      <div className="mt-6 p-4 bg-gradient-to-r from-[var(--accent-blue)]/10 to-[var(--accent-purple)]/10 rounded-lg border border-[var(--accent-blue)]/20">
        <div className="flex items-center justify-between">
          <div>
            <p className="font-medium">Ready to start building?</p>
            <p className="text-sm text-[var(--text-secondary)] mt-1">
              Complete all modules to unlock your implementation toolkit
            </p>
          </div>
          <button className="px-4 py-2 bg-gradient-to-r from-[var(--accent-blue)] to-[var(--accent-purple)] text-white rounded-lg font-medium text-sm hover:opacity-90 transition-opacity">
            Start Learning
          </button>
        </div>
      </div>
    </div>
  );
}