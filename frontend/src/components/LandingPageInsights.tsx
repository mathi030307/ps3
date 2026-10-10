import React from 'react';
import { FileText, Clock, Type, MousePointerClick, AlignLeft } from 'lucide-react';
import type { PageExtractionSummary } from '../types/audit';

interface LandingPageInsightsProps {
  summary: PageExtractionSummary | null | undefined;
}

export const LandingPageInsights: React.FC<LandingPageInsightsProps> = ({ summary }) => {
  if (!summary) return null;

  return (
    <div className="bg-slate-900/90 border border-slate-800 rounded-2xl shadow-xl p-5 lg:p-6 space-y-5">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-slate-800/80 pb-4">
        <div>
          <h2 className="text-base font-semibold text-white flex items-center gap-2">
            <FileText className="w-4 h-4 text-cyan-400" />
            <span>Extracted Landing Page Intelligence</span>
          </h2>
          <p className="text-xs text-slate-400 mt-0.5">
            Normalized DOM structure extracted from the target page.
          </p>
        </div>
      </div>

      {/* Quick Metric Pills */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        <div className="bg-slate-950/80 border border-slate-800 rounded-xl p-3">
          <span className="text-[10px] uppercase font-bold text-slate-500 tracking-wider flex items-center gap-1">
            <Type className="w-3 h-3 text-indigo-400" />
            Total Words
          </span>
          <span className="text-lg font-bold text-white mt-1 block">
            {summary.word_count.toLocaleString()}
          </span>
        </div>

        <div className="bg-slate-950/80 border border-slate-800 rounded-xl p-3">
          <span className="text-[10px] uppercase font-bold text-slate-500 tracking-wider flex items-center gap-1">
            <Clock className="w-3 h-3 text-cyan-400" />
            Reading Time
          </span>
          <span className="text-lg font-bold text-white mt-1 block">
            ~{summary.reading_time_minutes} min
          </span>
        </div>

        <div className="bg-slate-950/80 border border-slate-800 rounded-xl p-3">
          <span className="text-[10px] uppercase font-bold text-slate-500 tracking-wider flex items-center gap-1">
            <AlignLeft className="w-3 h-3 text-emerald-400" />
            H1 Headings
          </span>
          <span className="text-lg font-bold text-white mt-1 block">
            {summary.headings_h1.length}
          </span>
        </div>

        <div className="bg-slate-950/80 border border-slate-800 rounded-xl p-3">
          <span className="text-[10px] uppercase font-bold text-slate-500 tracking-wider flex items-center gap-1">
            <MousePointerClick className="w-3 h-3 text-amber-400" />
            Active CTAs
          </span>
          <span className="text-lg font-bold text-white mt-1 block">
            {summary.detected_ctas.length}
          </span>
        </div>
      </div>

      {/* Structural Elements */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
        {/* Title & H1s */}
        <div className="bg-slate-950/60 border border-slate-800 rounded-xl p-3.5 space-y-2">
          <span className="text-[11px] font-bold uppercase tracking-wider text-slate-400 block">
            Page Title &amp; Primary Headings
          </span>
          <div className="text-slate-300">
            <strong className="text-slate-400 font-medium">Title:</strong>{' '}
            {summary.title || 'No <title> tag detected'}
          </div>
          {summary.headings_h1.length > 0 && (
            <div className="text-slate-300">
              <strong className="text-slate-400 font-medium">H1:</strong>{' '}
              {summary.headings_h1.join(' | ')}
            </div>
          )}
          {summary.hero_text && (
            <div className="text-slate-400 pt-1 border-t border-slate-850">
              <strong className="text-slate-300 font-medium block mb-0.5">Hero Snippet:</strong>
              <span className="line-clamp-2 italic">"{summary.hero_text}"</span>
            </div>
          )}
        </div>

        {/* Detected CTAs */}
        <div className="bg-slate-950/60 border border-slate-800 rounded-xl p-3.5 space-y-2">
          <span className="text-[11px] font-bold uppercase tracking-wider text-slate-400 block">
            Detected Landing Page Call-to-Actions
          </span>
          {summary.detected_ctas.length > 0 ? (
            <div className="flex flex-wrap gap-1.5">
              {summary.detected_ctas.map((cta, idx) => (
                <span
                  key={idx}
                  className="bg-slate-900 border border-slate-700/80 text-cyan-300 px-2.5 py-1 rounded-lg text-xs font-medium"
                >
                  "{cta}"
                </span>
              ))}
            </div>
          ) : (
            <p className="text-slate-500 italic">No prominent CTA button elements detected.</p>
          )}
        </div>
      </div>
    </div>
  );
};
