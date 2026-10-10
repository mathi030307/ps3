import React from 'react';
import {
  AlertTriangle,
  TrendingDown,
  Info
} from 'lucide-react';
import { ResponsiveContainer, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar } from 'recharts';
import type { AuditResponse } from '../types/audit';

interface ScoreCardProps {
  audit: AuditResponse;
}

export const ScoreCard: React.FC<ScoreCardProps> = ({ audit }) => {
  const {
    overall_score,
    grade,
    summary_verdict,
    score_breakdown,
    is_synthetic_demo,
    demo_badge
  } = audit;

  const isScoreAvailable = overall_score !== null && overall_score !== undefined;

  // Grade color scheme
  const getGradeColor = (g?: string | null) => {
    switch (g) {
      case 'A':
        return 'text-emerald-400 bg-emerald-500/10 border-emerald-500/30';
      case 'B':
        return 'text-cyan-400 bg-cyan-500/10 border-cyan-500/30';
      case 'C':
        return 'text-amber-400 bg-amber-500/10 border-amber-500/30';
      case 'D':
        return 'text-orange-400 bg-orange-500/10 border-orange-500/30';
      case 'F':
        return 'text-rose-400 bg-rose-500/10 border-rose-500/30';
      default:
        return 'text-slate-400 bg-slate-800 border-slate-700';
    }
  };

  // Prepare radar chart data if breakdown exists
  const radarData = score_breakdown
    ? [
        { subject: 'Headline Match', value: score_breakdown.headline_hero_alignment },
        { subject: 'CTA Alignment', value: score_breakdown.cta_alignment },
        { subject: 'Claim Coverage', value: score_breakdown.claim_coverage_rate },
        { subject: 'Offer Consistency', value: score_breakdown.offer_consistency },
      ]
    : [];

  return (
    <div className="bg-slate-900/90 border border-slate-800 rounded-2xl shadow-xl p-5 lg:p-6 space-y-6">
      {/* Top Banner: Synthetic example notice if applicable */}
      {is_synthetic_demo && (
        <div className="flex items-center justify-between bg-amber-500/10 border border-amber-500/30 rounded-xl px-4 py-2.5">
          <div className="flex items-center gap-2">
            <AlertTriangle className="w-4 h-4 text-amber-400 shrink-0" />
            <span className="text-xs font-semibold text-amber-300">
              {demo_badge || 'Synthetic example'}: Pre-configured evaluation scenario.
            </span>
          </div>
          <span className="text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded bg-amber-500/20 text-amber-300">
            Demo Mode
          </span>
        </div>
      )}

      {/* Main Score Header */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 items-center">
        {/* Left: Overall Score Gauge & Grade */}
        <div className="flex items-center gap-5 md:col-span-1">
          <div className="relative flex items-center justify-center">
            {/* Circular score ring container */}
            <div className="w-28 h-28 rounded-full bg-slate-950 border-4 border-slate-800 flex flex-col items-center justify-center shadow-inner">
              {isScoreAvailable ? (
                <>
                  <span className="text-3xl font-extrabold text-white tracking-tight">
                    {Math.round(overall_score!)}
                  </span>
                  <span className="text-[10px] uppercase tracking-wider text-slate-500 font-semibold">
                    out of 100
                  </span>
                </>
              ) : (
                <span className="text-xs text-slate-500 font-semibold text-center px-2">
                  Unavailable
                </span>
              )}
            </div>
          </div>

          <div className="space-y-1.5">
            <div className="flex items-center gap-2">
              <span className="text-xs uppercase font-bold text-slate-400 tracking-wider">
                Overall Match
              </span>
              {grade && (
                <span
                  className={`text-sm font-extrabold px-2.5 py-0.5 rounded-md border ${getGradeColor(
                    grade
                  )}`}
                >
                  Grade {grade}
                </span>
              )}
            </div>
            <p className="text-xs text-slate-300 font-medium leading-snug">
              {summary_verdict || 'Analysis results pending.'}
            </p>
          </div>
        </div>

        {/* Center: Factor Breakdown Bars */}
        <div className="space-y-2.5 md:col-span-1 border-y md:border-y-0 md:border-x border-slate-800/80 py-4 md:py-0 md:px-6">
          <span className="text-[11px] font-bold uppercase tracking-wider text-slate-400 block mb-1">
            Explainable Factors
          </span>

          {score_breakdown ? (
            <>
              {/* Factor 1: Headline to Hero */}
              <div>
                <div className="flex justify-between text-xs mb-1">
                  <span className="text-slate-300 flex items-center gap-1">
                    Headline &bull; Hero
                  </span>
                  <span className="font-semibold text-slate-200">
                    {Math.round(score_breakdown.headline_hero_alignment)}%
                  </span>
                </div>
                <div className="w-full bg-slate-950 rounded-full h-1.5 overflow-hidden">
                  <div
                    className="bg-indigo-500 h-1.5 rounded-full transition-all duration-500"
                    style={{ width: `${score_breakdown.headline_hero_alignment}%` }}
                  />
                </div>
              </div>

              {/* Factor 2: CTA Alignment */}
              <div>
                <div className="flex justify-between text-xs mb-1">
                  <span className="text-slate-300">CTA Alignment</span>
                  <span className="font-semibold text-slate-200">
                    {Math.round(score_breakdown.cta_alignment)}%
                  </span>
                </div>
                <div className="w-full bg-slate-950 rounded-full h-1.5 overflow-hidden">
                  <div
                    className="bg-cyan-500 h-1.5 rounded-full transition-all duration-500"
                    style={{ width: `${score_breakdown.cta_alignment}%` }}
                  />
                </div>
              </div>

              {/* Factor 3: Claim Coverage */}
              <div>
                <div className="flex justify-between text-xs mb-1">
                  <span className="text-slate-300">Claim Coverage</span>
                  <span className="font-semibold text-slate-200">
                    {Math.round(score_breakdown.claim_coverage_rate)}%
                  </span>
                </div>
                <div className="w-full bg-slate-950 rounded-full h-1.5 overflow-hidden">
                  <div
                    className="bg-emerald-500 h-1.5 rounded-full transition-all duration-500"
                    style={{ width: `${score_breakdown.claim_coverage_rate}%` }}
                  />
                </div>
              </div>

              {/* Factor 4: Offer Consistency */}
              <div>
                <div className="flex justify-between text-xs mb-1">
                  <span className="text-slate-300">Offer Consistency</span>
                  <span className="font-semibold text-slate-200">
                    {Math.round(score_breakdown.offer_consistency)}%
                  </span>
                </div>
                <div className="w-full bg-slate-950 rounded-full h-1.5 overflow-hidden">
                  <div
                    className="bg-amber-500 h-1.5 rounded-full transition-all duration-500"
                    style={{ width: `${score_breakdown.offer_consistency}%` }}
                  />
                </div>
              </div>

              {/* Contradiction Penalty if applied */}
              {score_breakdown.contradiction_penalty > 0 && (
                <div className="pt-1 flex items-center justify-between text-[11px] text-rose-400 font-semibold bg-rose-500/10 px-2 py-1 rounded-md border border-rose-500/20">
                  <span className="flex items-center gap-1">
                    <TrendingDown className="w-3.5 h-3.5" />
                    Contradiction Penalty
                  </span>
                  <span>-{score_breakdown.contradiction_penalty} pts</span>
                </div>
              )}
            </>
          ) : (
            <p className="text-xs text-slate-500">Breakdown unavailable.</p>
          )}
        </div>

        {/* Right: Radar Chart Visualization */}
        <div className="md:col-span-1 h-44 flex items-center justify-center">
          {radarData.length > 0 ? (
            <ResponsiveContainer width="100%" height="100%">
              <RadarChart cx="50%" cy="50%" outerRadius="70%" data={radarData}>
                <PolarGrid stroke="#334155" />
                <PolarAngleAxis dataKey="subject" stroke="#94a3b8" tick={{ fontSize: 10 }} />
                <PolarRadiusAxis angle={30} domain={[0, 100]} stroke="#475569" tick={false} />
                <Radar
                  name="Score"
                  dataKey="value"
                  stroke="#6366f1"
                  fill="#6366f1"
                  fillOpacity={0.4}
                />
              </RadarChart>
            </ResponsiveContainer>
          ) : (
            <div className="text-center text-slate-500 text-xs">
              <Info className="w-6 h-6 mx-auto mb-1 opacity-40" />
              Chart displays once audit completes
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
