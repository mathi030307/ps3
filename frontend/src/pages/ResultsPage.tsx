import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import {
  AlertTriangle,
  Clock,
  Globe,
  Download,
  CheckCircle2,
  AlertCircle,
  FileText,
  Table,
  Code2,
  Copy,
  Check,
  Quote,
  Scale,
  Sparkles,
  ArrowLeft,
  MousePointerClick
} from 'lucide-react';
import type { AuditResponse, MatchStatus } from '../types/audit';
import { exportReport } from '../services/api';

interface ResultsPageProps {
  auditResult: AuditResponse | null;
  onOpenExportModal: () => void;
}

export const ResultsPage: React.FC<ResultsPageProps> = ({ auditResult, onOpenExportModal }) => {
  const [filter, setFilter] = useState<string>('ALL');
  const [copiedId, setCopiedId] = useState<string | null>(null);

  if (!auditResult) {
    return (
      <div className="bg-white border border-slate-200 rounded-3xl p-12 text-center max-w-xl mx-auto my-12 shadow-xs space-y-4">
        <div className="w-12 h-12 rounded-full bg-slate-100 text-slate-500 mx-auto flex items-center justify-center">
          <FileText className="w-6 h-6" />
        </div>
        <h2 className="text-xl font-bold text-slate-900">No Active Audit Results</h2>
        <p className="text-sm text-slate-600">
          Run an audit from the New Audit page or select a demo scenario from the Dashboard to view message match findings.
        </p>
        <Link
          to="/audit/new"
          className="inline-flex items-center gap-1.5 px-5 py-2.5 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-xl text-xs shadow-xs transition-all cursor-pointer"
        >
          <span>Start New Audit</span>
        </Link>
      </div>
    );
  }

  const {
    overall_score,
    grade,
    presentation_aid_note,
    summary_verdict,
    score_breakdown,
    cta_analysis,
    is_synthetic_demo,
    demo_badge,
    timestamp,
    source_description,
    total_claims,
    supported_count,
    partial_count,
    not_found_count,
    contradicted_count,
    uncertain_count,
    claims,
    recommendations,
    page_summary
  } = auditResult;

  const isScoreAvailable = overall_score !== null && overall_score !== undefined;

  const handleCopy = (text: string, id: string) => {
    navigator.clipboard.writeText(text);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  const handleDirectDownload = async (format: 'csv' | 'html' | 'json') => {
    try {
      const content = await exportReport(auditResult, format);
      const mime = format === 'json' ? 'application/json' : format === 'html' ? 'text/html' : 'text/csv';
      const blob = new Blob([content], { type: mime });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `message-match-audit-${Date.now()}.${format}`;
      a.click();
      URL.revokeObjectURL(url);
    } catch (err) {
      console.error('Export failed', err);
    }
  };

  const filteredClaims = claims.filter((claim) => {
    if (filter === 'ALL') return true;
    return claim.status === filter;
  });

  return (
    <div className="space-y-8 py-4">
      {/* Top Banner: Synthetic example notice if applicable */}
      {is_synthetic_demo && (
        <div className="flex items-center justify-between bg-amber-50 border border-amber-300 rounded-2xl px-5 py-3 shadow-xs">
          <div className="flex items-center gap-2.5">
            <AlertTriangle className="w-5 h-5 text-amber-700 shrink-0" />
            <div>
              <span className="text-xs font-bold text-amber-900 block">
                {demo_badge || 'Synthetic example'}: Demonstration scenario for evaluation.
              </span>
              <span className="text-[11px] text-amber-700">
                Executed live through the real extraction, claim matching, and deterministic verification engine.
              </span>
            </div>
          </div>
          <span className="text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded bg-amber-200/80 text-amber-900 border border-amber-300">
            Synthetic example
          </span>
        </div>
      )}

      {/* Header & Provenance Meta */}
      <div className="bg-white border border-slate-200 rounded-3xl p-6 lg:p-8 shadow-xs flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 text-xs font-semibold text-slate-500 mb-1">
            <Link to="/" className="hover:text-blue-600 transition-colors flex items-center gap-1">
              <ArrowLeft className="w-3.5 h-3.5" />
              <span>Dashboard</span>
            </Link>
            <span>&bull;</span>
            <span>Audit Findings</span>
          </div>
          <h1 className="text-2xl font-extrabold text-slate-900 tracking-tight">
            Message Match Continuity Report
          </h1>
          <div className="flex flex-wrap items-center gap-4 text-xs text-slate-500 mt-1">
            <span className="flex items-center gap-1">
              <Globe className="w-3.5 h-3.5 text-slate-400" />
              <strong>Source:</strong> {source_description || 'Webpage Snapshot'}
            </span>
            <span className="flex items-center gap-1">
              <Clock className="w-3.5 h-3.5 text-slate-400" />
              <strong>Timestamp:</strong> {timestamp || 'Just now'}
            </span>
          </div>
        </div>

        {/* Quick Downloads */}
        <div className="flex flex-wrap items-center gap-2">
          <button
            onClick={() => handleDirectDownload('html')}
            className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold text-slate-700 hover:text-slate-900 bg-slate-100 hover:bg-slate-200 border border-slate-200 rounded-xl transition-all cursor-pointer"
          >
            <FileText className="w-3.5 h-3.5 text-blue-600" />
            <span>HTML Report</span>
          </button>
          <button
            onClick={() => handleDirectDownload('csv')}
            className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold text-slate-700 hover:text-slate-900 bg-slate-100 hover:bg-slate-200 border border-slate-200 rounded-xl transition-all cursor-pointer"
          >
            <Table className="w-3.5 h-3.5 text-emerald-600" />
            <span>Claims CSV</span>
          </button>
          <button
            onClick={() => handleDirectDownload('json')}
            className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold text-slate-700 hover:text-slate-900 bg-slate-100 hover:bg-slate-200 border border-slate-200 rounded-xl transition-all cursor-pointer"
          >
            <Code2 className="w-3.5 h-3.5 text-indigo-600" />
            <span>JSON</span>
          </button>
          <button
            onClick={onOpenExportModal}
            className="flex items-center gap-1.5 px-3.5 py-1.5 text-xs font-semibold text-white bg-slate-900 hover:bg-slate-800 rounded-xl shadow-xs transition-all cursor-pointer"
          >
            <Download className="w-3.5 h-3.5" />
            <span>Export View</span>
          </button>
        </div>
      </div>

      {/* 7 Summary Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-7 gap-3">
        {/* Card 1: Overall Score */}
        <div className="bg-white border border-slate-200 rounded-2xl p-4 shadow-xs col-span-2 md:col-span-2 lg:col-span-2 flex items-center justify-between">
          <div>
            <span className="text-[11px] font-bold uppercase tracking-wider text-slate-500 block">
              Overall Score
            </span>
            <div className="flex items-baseline gap-2 mt-1">
              <span className="text-3xl font-extrabold text-slate-900 tracking-tight">
                {isScoreAvailable ? `${overall_score!.toFixed(1)}` : 'Score unavailable'}
              </span>
              {isScoreAvailable && (
                <span className="text-xs text-slate-400 font-semibold">/ 100</span>
              )}
            </div>
            <p className="text-xs text-slate-600 mt-1 line-clamp-1">
              {summary_verdict || 'Analysis results pending.'}
            </p>
          </div>
          {grade && (
            <div className="flex flex-col items-center">
              <span className="text-xl font-extrabold px-3 py-1 rounded-xl bg-blue-50 text-blue-700 border border-blue-200">
                {grade}
              </span>
              <span className="text-[9px] text-slate-400 mt-0.5 font-medium">Grade aid</span>
            </div>
          )}
        </div>

        {/* Card 2: Total Claims */}
        <div className="bg-white border border-slate-200 rounded-2xl p-4 shadow-xs">
          <span className="text-[10px] font-bold uppercase tracking-wider text-slate-500 block">
            Total Claims
          </span>
          <span className="text-2xl font-bold text-slate-900 mt-1 block">
            {total_claims}
          </span>
          <span className="text-[11px] text-slate-500">Atomic units</span>
        </div>

        {/* Card 3: Supported */}
        <div className="bg-emerald-50/60 border border-emerald-200 rounded-2xl p-4 shadow-xs">
          <span className="text-[10px] font-bold uppercase tracking-wider text-emerald-800 block">
            Supported
          </span>
          <span className="text-2xl font-bold text-emerald-900 mt-1 block">
            {supported_count}
          </span>
          <span className="text-[11px] text-emerald-700 font-medium">Verified quote</span>
        </div>

        {/* Card 4: Partial Match */}
        <div className="bg-amber-50/60 border border-amber-200 rounded-2xl p-4 shadow-xs">
          <span className="text-[10px] font-bold uppercase tracking-wider text-amber-800 block">
            Partial Match
          </span>
          <span className="text-2xl font-bold text-amber-900 mt-1 block">
            {partial_count}
          </span>
          <span className="text-[11px] text-amber-700 font-medium">Minor gap</span>
        </div>

        {/* Card 5: Not Found */}
        <div className="bg-slate-50 border border-slate-200 rounded-2xl p-4 shadow-xs">
          <span className="text-[10px] font-bold uppercase tracking-wider text-slate-600 block">
            Not Found
          </span>
          <span className="text-2xl font-bold text-slate-800 mt-1 block">
            {not_found_count}
          </span>
          <span className="text-[11px] text-slate-500">Absent from page</span>
        </div>

        {/* Card 6: Contradicted */}
        <div className="bg-rose-50/70 border border-rose-200 rounded-2xl p-4 shadow-xs">
          <span className="text-[10px] font-bold uppercase tracking-wider text-rose-800 block">
            Contradicted
          </span>
          <span className="text-2xl font-bold text-rose-900 mt-1 block">
            {contradicted_count}
          </span>
          <span className="text-[11px] text-rose-700 font-medium">Conflicting facts</span>
        </div>

        {/* Card 7: Uncertain */}
        <div className="bg-purple-50/60 border border-purple-200 rounded-2xl p-4 shadow-xs">
          <span className="text-[10px] font-bold uppercase tracking-wider text-purple-800 block">
            Uncertain
          </span>
          <span className="text-2xl font-bold text-purple-900 mt-1 block">
            {uncertain_count}
          </span>
          <span className="text-[11px] text-purple-700 font-medium">Vague evidence</span>
        </div>
      </div>

      {/* CTA Analysis Section (Requirement 7) */}
      {cta_analysis && (
        <section className="bg-white border border-slate-200 rounded-3xl p-6 shadow-xs space-y-4">
          <div className="flex items-center justify-between border-b border-slate-100 pb-3">
            <div className="flex items-center gap-2">
              <MousePointerClick className="w-5 h-5 text-blue-600" />
              <h2 className="text-base font-bold text-slate-900">
                Call-to-Action (CTA) Continuity Analysis
              </h2>
            </div>
            {cta_analysis.friction_detected ? (
              <span className="text-xs font-bold text-rose-700 bg-rose-50 border border-rose-200 px-2.5 py-1 rounded-full flex items-center gap-1">
                <AlertCircle className="w-3.5 h-3.5" />
                <span>Action Friction Detected</span>
              </span>
            ) : (
              <span className="text-xs font-bold text-emerald-700 bg-emerald-50 border border-emerald-200 px-2.5 py-1 rounded-full flex items-center gap-1">
                <CheckCircle2 className="w-3.5 h-3.5" />
                <span>CTA Continuity Aligned</span>
              </span>
            )}
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
            {/* Ad Promise CTA */}
            <div className="bg-slate-50 border border-slate-200 rounded-xl p-4 space-y-1.5">
              <span className="text-[10px] font-bold uppercase tracking-wider text-slate-500">
                Promised Ad CTA
              </span>
              <div className="text-sm font-bold text-slate-900 font-mono">
                "{cta_analysis.ad_cta || 'No explicit CTA provided'}"
              </div>
            </div>

            {/* Landing Page CTAs */}
            <div className="bg-slate-50 border border-slate-200 rounded-xl p-4 space-y-1.5">
              <span className="text-[10px] font-bold uppercase tracking-wider text-slate-500">
                Detected Landing Page Primary CTA
              </span>
              <div className="text-sm font-bold text-slate-900 font-mono">
                "{cta_analysis.page_primary_cta || 'No buttons detected'}"
              </div>
              {cta_analysis.all_page_ctas.length > 1 && (
                <div className="text-[11px] text-slate-500 pt-1">
                  Other buttons: {cta_analysis.all_page_ctas.slice(1, 4).map(c => `"${c}"`).join(', ')}
                </div>
              )}
            </div>
          </div>

          <div className="bg-slate-50 border border-slate-200 rounded-xl p-3 text-xs text-slate-700">
            <strong>Continuity Assessment:</strong> {cta_analysis.friction_notes}
          </div>
        </section>
      )}

      {/* Claim Findings Table with Deterministic Substring Provenance */}
      <section className="bg-white border border-slate-200 rounded-3xl p-6 shadow-xs space-y-5">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-100 pb-4">
          <div>
            <h2 className="text-base font-bold text-slate-900 flex items-center gap-2">
              <span>Atomic Claim Audit &amp; Verified Quote Provenance</span>
              <span className="text-xs bg-slate-100 text-slate-700 px-2.5 py-0.5 rounded-full font-mono">
                {claims.length} claims
              </span>
            </h2>
            <p className="text-xs text-slate-500 mt-0.5">
              Rule 1: Every displayed quote must pass deterministic verify_quote() against extracted source text.
            </p>
          </div>

          {/* Filters */}
          <div className="flex flex-wrap items-center gap-1 bg-slate-100 p-1 rounded-xl text-xs font-medium">
            {['ALL', 'Supported', 'Partial Match', 'Not Found', 'Contradicted', 'Uncertain'].map((st) => (
              <button
                key={st}
                onClick={() => setFilter(st)}
                className={`px-2.5 py-1 rounded-lg transition-all cursor-pointer ${
                  filter === st
                    ? 'bg-white text-slate-900 font-bold shadow-xs'
                    : 'text-slate-600 hover:text-slate-900'
                }`}
              >
                {st}
              </button>
            ))}
          </div>
        </div>

        {/* Claims List */}
        <div className="space-y-3">
          {filteredClaims.length === 0 ? (
            <div className="text-center py-8 text-slate-400 text-xs">
              No claims match filter '{filter}'.
            </div>
          ) : (
            filteredClaims.map((claim) => {
              const statusStyles: Record<MatchStatus, { border: string; badge: string }> = {
                Supported: { border: 'border-l-emerald-500', badge: 'bg-emerald-50 text-emerald-800 border-emerald-200' },
                'Partial Match': { border: 'border-l-amber-500', badge: 'bg-amber-50 text-amber-800 border-amber-200' },
                'Not Found': { border: 'border-l-slate-400', badge: 'bg-slate-100 text-slate-700 border-slate-200' },
                Contradicted: { border: 'border-l-rose-500', badge: 'bg-rose-50 text-rose-800 border-rose-200' },
                Uncertain: { border: 'border-l-purple-500', badge: 'bg-purple-50 text-purple-800 border-purple-200' },
              };
              const sStyle = statusStyles[claim.status];

              return (
                <div
                  key={claim.claim_id}
                  className={`bg-slate-50/50 border border-slate-200 rounded-xl p-4 border-l-4 ${sStyle.border} space-y-3`}
                >
                  <div className="flex flex-wrap items-center justify-between gap-2">
                    <div className="flex items-center gap-2">
                      <span className="font-mono text-xs font-bold text-slate-600 bg-slate-100 px-1.5 py-0.5 rounded">
                        {claim.claim_id}
                      </span>
                      <span className="text-[10px] uppercase font-bold text-slate-500 bg-white border border-slate-200 px-2 py-0.5 rounded">
                        From {claim.source_part}
                      </span>
                      <span className="text-[10px] font-semibold text-blue-700 bg-blue-50 border border-blue-200 px-2 py-0.5 rounded">
                        {claim.category}
                      </span>
                    </div>

                    <div className="flex items-center gap-2">
                      <span className={`text-xs font-bold px-2.5 py-0.5 rounded-md border ${sStyle.badge}`}>
                        {claim.status}
                      </span>
                      <span className="text-xs font-mono text-slate-600 bg-white border border-slate-200 px-2 py-0.5 rounded">
                        {Math.round(claim.similarity_score)}% sim
                      </span>
                    </div>
                  </div>

                  {/* Assertion Text */}
                  <div className="text-sm font-bold text-slate-900">
                    "{claim.claim_text}"
                  </div>

                  {/* Verified Evidence Quote Box */}
                  <div className="bg-white border border-slate-200 rounded-lg p-3 space-y-1">
                    <div className="flex items-center justify-between text-[11px] font-bold text-slate-500">
                      <span className="flex items-center gap-1">
                        <Quote className="w-3 h-3 text-slate-400" />
                        <span>Extracted Page Evidence Quote</span>
                      </span>
                      {claim.is_quote_verified ? (
                        <span className="text-emerald-700 font-semibold flex items-center gap-1">
                          <Check className="w-3 h-3" />
                          <span>Exact Substring in [{claim.quote_source_element || 'body'}]</span>
                        </span>
                      ) : (
                        <span className="text-slate-400 font-normal">Unverified</span>
                      )}
                    </div>
                    <div className={`text-xs font-mono ${claim.is_quote_verified ? 'text-emerald-800 bg-emerald-50/50 p-2 rounded' : 'text-slate-500 italic'}`}>
                      {claim.evidence_quote || 'No verified evidence quote available.'}
                    </div>
                  </div>

                  {/* Reason & Action */}
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-2 text-xs pt-1 border-t border-slate-200/80">
                    <div className="text-slate-600">
                      <strong className="text-slate-800">Reason:</strong> {claim.status_reason}
                    </div>
                    <div className="text-blue-700">
                      <strong className="text-blue-900">Suggested Action:</strong> {claim.suggested_action}
                    </div>
                  </div>
                </div>
              );
            })
          )}
        </div>
      </section>

      {/* Score Explanation & Per-Claim Contribution Table (Requirement 3) */}
      {score_breakdown && (
        <section className="bg-white border border-slate-200 rounded-3xl p-6 shadow-xs space-y-5">
          <div className="border-b border-slate-100 pb-3">
            <h2 className="text-base font-bold text-slate-900 flex items-center gap-2">
              <Scale className="w-5 h-5 text-blue-600" />
              <span>Score Formula &amp; Per-Claim Contribution Table</span>
            </h2>
            <p className="text-xs text-slate-500 mt-1">
              Transparent, explainable mathematical breakdown of the 0–100 quality score.
            </p>
          </div>

          {/* Formula Callout */}
          <div className="bg-slate-50 border border-slate-200 rounded-xl p-4 space-y-1.5 text-xs">
            <div className="font-bold text-slate-700 uppercase tracking-wider text-[10px]">
              Documented Scoring Formula:
            </div>
            <p className="font-mono text-slate-800 leading-relaxed">
              {score_breakdown.formula_text}
            </p>
            {score_breakdown.is_capped_at_40 && (
              <div className="text-rose-700 font-semibold pt-1 flex items-center gap-1 text-[11px]">
                <AlertTriangle className="w-3.5 h-3.5" />
                <span>Hard Cap Applied: Contradicted claim restricts maximum possible score to 40.0.</span>
              </div>
            )}
            <div className="text-slate-500 text-[11px] pt-1">
              Note: {presentation_aid_note || score_breakdown.presentation_aid_label}
            </div>
          </div>

          {/* Per-Claim Contribution Table */}
          <div className="overflow-x-auto border border-slate-200 rounded-xl">
            <table className="w-full text-left text-xs border-collapse">
              <thead>
                <tr className="bg-slate-50 border-b border-slate-200 text-slate-600 font-semibold">
                  <th className="py-2.5 px-3">ID</th>
                  <th className="py-2.5 px-3">Claim Text</th>
                  <th className="py-2.5 px-3">Category</th>
                  <th className="py-2.5 px-3">Status</th>
                  <th className="py-2.5 px-3">Base Value</th>
                  <th className="py-2.5 px-3">Weight</th>
                  <th className="py-2.5 px-3">Points</th>
                  <th className="py-2.5 px-3">Contribution</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {score_breakdown.claim_contributions.map((c) => (
                  <tr key={c.claim_id} className="hover:bg-slate-50/50">
                    <td className="py-2 px-3 font-mono font-bold text-slate-700">{c.claim_id}</td>
                    <td className="py-2 px-3 font-medium text-slate-900 max-w-xs truncate">{c.claim_text}</td>
                    <td className="py-2 px-3 text-slate-600">{c.category}</td>
                    <td className="py-2 px-3 font-semibold text-slate-800">{c.status}</td>
                    <td className="py-2 px-3 font-mono">{c.base_value}</td>
                    <td className="py-2 px-3 font-mono font-semibold text-blue-700">{c.weight}x</td>
                    <td className="py-2 px-3 font-mono">{c.weighted_points} / {c.max_possible_points}</td>
                    <td className="py-2 px-3 font-mono font-bold text-slate-800">{c.contribution_percent}%</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      )}

      {/* Prioritized Recommendations */}
      <section className="bg-white border border-slate-200 rounded-3xl p-6 shadow-xs space-y-4">
        <div className="border-b border-slate-100 pb-3">
          <h2 className="text-base font-bold text-slate-900 flex items-center gap-2">
            <Sparkles className="w-5 h-5 text-amber-500" />
            <span>Prioritized Recommendations &amp; Copy Fixes</span>
          </h2>
          <p className="text-xs text-slate-500 mt-1">
            Actionable adjustments ordered by bounce-reduction and conversion impact.
          </p>
        </div>

        <div className="space-y-3">
          {recommendations.length === 0 ? (
            <div className="text-center py-6 text-slate-500 text-xs">
              No critical issues detected. Excellent message match!
            </div>
          ) : (
            recommendations.map((rec) => {
              const priorityStyles = {
                HIGH: 'border-l-rose-500 bg-rose-50/30 text-rose-800',
                MEDIUM: 'border-l-amber-500 bg-amber-50/30 text-amber-800',
                LOW: 'border-l-blue-500 bg-blue-50/30 text-blue-800',
              }[rec.priority];

              return (
                <div
                  key={rec.id}
                  className={`bg-white border border-slate-200 rounded-xl p-4 border-l-4 ${priorityStyles} space-y-3 shadow-2xs`}
                >
                  <div className="flex items-center justify-between">
                    <span className="text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded bg-slate-100 text-slate-700">
                      {rec.priority} Priority &bull; {rec.category}
                    </span>
                    <span className="font-mono text-xs text-slate-400">{rec.id}</span>
                  </div>

                  <div>
                    <h4 className="text-sm font-bold text-slate-900">{rec.issue}</h4>
                    <p className="text-xs text-slate-600 mt-0.5">
                      <strong>Impact:</strong> {rec.impact}
                    </p>
                  </div>

                  <div className="bg-slate-50 border border-slate-200 rounded-lg p-3 text-xs text-slate-700">
                    <strong className="text-blue-900 block mb-0.5">Recommended Fix:</strong>
                    {rec.recommended_fix}
                  </div>

                  {/* Copy suggestions */}
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3 pt-1">
                    {rec.suggested_page_copy && (
                      <div className="bg-slate-50 border border-slate-200 rounded-lg p-2.5 text-xs space-y-1">
                        <div className="flex items-center justify-between text-[10px] font-bold text-blue-700 uppercase">
                          <span>Suggested Landing Page Copy</span>
                          <button
                            onClick={() => handleCopy(rec.suggested_page_copy!, `${rec.id}-page`)}
                            className="text-slate-500 hover:text-slate-900 flex items-center gap-1 cursor-pointer"
                          >
                            {copiedId === `${rec.id}-page` ? (
                              <Check className="w-3 h-3 text-emerald-600" />
                            ) : (
                              <Copy className="w-3 h-3" />
                            )}
                            <span>Copy</span>
                          </button>
                        </div>
                        <div className="font-mono text-slate-800 bg-white p-1.5 rounded border border-slate-200">
                          {rec.suggested_page_copy}
                        </div>
                      </div>
                    )}

                    {rec.suggested_ad_copy && (
                      <div className="bg-slate-50 border border-slate-200 rounded-lg p-2.5 text-xs space-y-1">
                        <div className="flex items-center justify-between text-[10px] font-bold text-indigo-700 uppercase">
                          <span>Suggested Ad Copy</span>
                          <button
                            onClick={() => handleCopy(rec.suggested_ad_copy!, `${rec.id}-ad`)}
                            className="text-slate-500 hover:text-slate-900 flex items-center gap-1 cursor-pointer"
                          >
                            {copiedId === `${rec.id}-ad` ? (
                              <Check className="w-3 h-3 text-emerald-600" />
                            ) : (
                              <Copy className="w-3 h-3" />
                            )}
                            <span>Copy</span>
                          </button>
                        </div>
                        <div className="font-mono text-slate-800 bg-white p-1.5 rounded border border-slate-200">
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
      </section>

      {/* Extracted Landing Page Intelligence */}
      {page_summary && (
        <section className="bg-white border border-slate-200 rounded-3xl p-6 shadow-xs space-y-4">
          <div className="border-b border-slate-100 pb-3">
            <h2 className="text-base font-bold text-slate-900 flex items-center gap-2">
              <FileText className="w-4 h-4 text-blue-600" />
              <span>Extracted Landing Page Intelligence</span>
            </h2>
            <p className="text-xs text-slate-500 mt-0.5">
              Structural DOM elements extracted from the destination page.
            </p>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-xs">
            <div className="bg-slate-50 border border-slate-200 rounded-xl p-3">
              <span className="text-[10px] font-bold uppercase text-slate-500 block">Total Word Count</span>
              <span className="text-lg font-bold text-slate-900 mt-1 block">{page_summary.word_count} words</span>
            </div>
            <div className="bg-slate-50 border border-slate-200 rounded-xl p-3">
              <span className="text-[10px] font-bold uppercase text-slate-500 block">Est. Reading Time</span>
              <span className="text-lg font-bold text-slate-900 mt-1 block">~{page_summary.reading_time_minutes} min</span>
            </div>
            <div className="bg-slate-50 border border-slate-200 rounded-xl p-3">
              <span className="text-[10px] font-bold uppercase text-slate-500 block">H1 Headings</span>
              <span className="text-lg font-bold text-slate-900 mt-1 block">{page_summary.headings_h1.length}</span>
            </div>
            <div className="bg-slate-50 border border-slate-200 rounded-xl p-3">
              <span className="text-[10px] font-bold uppercase text-slate-500 block">Active CTAs</span>
              <span className="text-lg font-bold text-slate-900 mt-1 block">{page_summary.detected_ctas.length}</span>
            </div>
          </div>

          <div className="space-y-2 text-xs">
            <div className="text-slate-700">
              <strong>Title:</strong> {page_summary.title || 'None detected'}
            </div>
            {page_summary.headings_h1.length > 0 && (
              <div className="text-slate-700">
                <strong>H1:</strong> {page_summary.headings_h1.join(' | ')}
              </div>
            )}
            {page_summary.footer_disclosures.length > 0 && (
              <div className="bg-slate-50 border border-slate-200 rounded-lg p-3 text-slate-600">
                <strong className="text-slate-800 block mb-1">Footer Legal &amp; Fee Disclosures:</strong>
                {page_summary.footer_disclosures.map((f, i) => (
                  <div key={i} className="italic text-[11px] mb-1">"{f}"</div>
                ))}
              </div>
            )}
          </div>
        </section>
      )}
    </div>
  );
};
