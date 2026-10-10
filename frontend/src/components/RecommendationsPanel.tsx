import React, { useState } from 'react';
import { Lightbulb, Copy, Check, Sparkles } from 'lucide-react';
import type { Recommendation, PriorityLevel } from '../types/audit';

interface RecommendationsPanelProps {
  recommendations: Recommendation[];
}

export const RecommendationsPanel: React.FC<RecommendationsPanelProps> = ({
  recommendations,
}) => {
  const [copiedId, setCopiedId] = useState<string | null>(null);

  const handleCopy = (text: string, id: string) => {
    navigator.clipboard.writeText(text);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  const priorityStyles: Record<
    PriorityLevel,
    { badge: string; border: string; label: string }
  > = {
    HIGH: {
      badge: 'bg-rose-500/10 text-rose-400 border-rose-500/30',
      border: 'border-l-rose-500',
      label: 'High Impact',
    },
    MEDIUM: {
      badge: 'bg-amber-500/10 text-amber-400 border-amber-500/30',
      border: 'border-l-amber-500',
      label: 'Medium Impact',
    },
    LOW: {
      badge: 'bg-indigo-500/10 text-indigo-400 border-indigo-500/30',
      border: 'border-l-indigo-500',
      label: 'Optimization',
    },
  };

  return (
    <div className="bg-slate-900/90 border border-slate-800 rounded-2xl shadow-xl p-5 lg:p-6 space-y-5">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-slate-800/80 pb-4">
        <div>
          <h2 className="text-base font-semibold text-white flex items-center gap-2">
            <Lightbulb className="w-5 h-5 text-amber-400" />
            <span>Actionable Message Match Fixes</span>
            <span className="text-xs bg-slate-800 text-slate-300 px-2 py-0.5 rounded-full font-mono">
              {recommendations.length} recommendations
            </span>
          </h2>
          <p className="text-xs text-slate-400 mt-0.5">
            Prioritized copy and continuity adjustments to maximize conversion rate and Quality Score.
          </p>
        </div>
      </div>

      {/* Recommendations List */}
      <div className="space-y-4">
        {recommendations.length === 0 ? (
          <div className="text-center py-8 text-slate-400 text-xs">
            <Sparkles className="w-6 h-6 text-emerald-400 mx-auto mb-2" />
            No critical gaps found! High message match alignment achieved.
          </div>
        ) : (
          recommendations.map((rec) => {
            const pStyle = priorityStyles[rec.priority];
            return (
              <div
                key={rec.id}
                className={`bg-slate-950/60 border border-slate-800 rounded-xl p-4.5 space-y-3 border-l-4 ${pStyle.border} hover:border-slate-700/80 transition-all`}
              >
                {/* Meta Header */}
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span
                      className={`text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-md border ${pStyle.badge}`}
                    >
                      {pStyle.label}
                    </span>
                    <span className="text-xs font-semibold text-slate-300">
                      {rec.category}
                    </span>
                  </div>
                  <span className="text-[11px] font-mono text-slate-500">
                    {rec.id}
                  </span>
                </div>

                {/* Issue Description */}
                <div>
                  <h4 className="text-sm font-semibold text-white mb-1">
                    {rec.issue}
                  </h4>
                  <p className="text-xs text-slate-400">
                    <strong className="text-slate-300">Business Impact:</strong> {rec.impact}
                  </p>
                </div>

                {/* Recommended Fix */}
                <div className="bg-slate-900/80 border border-slate-800/90 rounded-lg p-3 text-xs text-slate-300">
                  <strong className="text-indigo-300 font-semibold block mb-1">
                    Recommended Fix:
                  </strong>
                  {rec.recommended_fix}
                </div>

                {/* Suggested Copy Snippets */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3 pt-1">
                  {rec.suggested_page_copy && (
                    <div className="bg-slate-900/60 border border-slate-800 rounded-lg p-2.5 space-y-1.5">
                      <div className="flex items-center justify-between">
                        <span className="text-[10px] font-bold uppercase tracking-wider text-cyan-400">
                          Suggested Landing Page Copy
                        </span>
                        <button
                          onClick={() =>
                            handleCopy(rec.suggested_page_copy!, `${rec.id}-page`)
                          }
                          className="text-[10px] text-slate-400 hover:text-slate-200 flex items-center gap-1 cursor-pointer"
                        >
                          {copiedId === `${rec.id}-page` ? (
                            <>
                              <Check className="w-3 h-3 text-emerald-400" />
                              <span className="text-emerald-400">Copied</span>
                            </>
                          ) : (
                            <>
                              <Copy className="w-3 h-3" />
                              <span>Copy</span>
                            </>
                          )}
                        </button>
                      </div>
                      <div className="text-xs font-mono text-slate-200 bg-slate-950 p-2 rounded border border-slate-850">
                        {rec.suggested_page_copy}
                      </div>
                    </div>
                  )}

                  {rec.suggested_ad_copy && (
                    <div className="bg-slate-900/60 border border-slate-800 rounded-lg p-2.5 space-y-1.5">
                      <div className="flex items-center justify-between">
                        <span className="text-[10px] font-bold uppercase tracking-wider text-indigo-400">
                          Suggested Ad Copy Alternative
                        </span>
                        <button
                          onClick={() =>
                            handleCopy(rec.suggested_ad_copy!, `${rec.id}-ad`)
                          }
                          className="text-[10px] text-slate-400 hover:text-slate-200 flex items-center gap-1 cursor-pointer"
                        >
                          {copiedId === `${rec.id}-ad` ? (
                            <>
                              <Check className="w-3 h-3 text-emerald-400" />
                              <span className="text-emerald-400">Copied</span>
                            </>
                          ) : (
                            <>
                              <Copy className="w-3 h-3" />
                              <span>Copy</span>
                            </>
                          )}
                        </button>
                      </div>
                      <div className="text-xs font-mono text-slate-200 bg-slate-950 p-2 rounded border border-slate-850">
                        {rec.suggested_ad_copy}
                      </div>
                    </div>
                  )}
                </div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
};
