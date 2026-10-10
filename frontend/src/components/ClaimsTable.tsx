import React, { useState } from 'react';
import {
  CheckCircle,
  AlertCircle,
  HelpCircle,
  XCircle,
  AlertTriangle,
  Quote,
  Check,
  Search,
} from 'lucide-react';
import type { ClaimAudit, MatchStatus } from '../types/audit';

interface ClaimsTableProps {
  claims: ClaimAudit[];
}

export const ClaimsTable: React.FC<ClaimsTableProps> = ({ claims }) => {
  const [filter, setFilter] = useState<string>('ALL');
  const [searchQuery, setSearchQuery] = useState<string>('');

  const statusConfig: Record<
    MatchStatus,
    { label: string; icon: React.ReactNode; badgeClass: string; borderClass: string }
  > = {
    Supported: {
      label: 'Supported',
      icon: <CheckCircle className="w-3.5 h-3.5" />,
      badgeClass: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30',
      borderClass: 'border-l-emerald-500',
    },
    'Partial Match': {
      label: 'Partial Match',
      icon: <AlertCircle className="w-3.5 h-3.5" />,
      badgeClass: 'bg-amber-500/10 text-amber-400 border-amber-500/30',
      borderClass: 'border-l-amber-500',
    },
    'Not Found': {
      label: 'Not Found',
      icon: <HelpCircle className="w-3.5 h-3.5" />,
      badgeClass: 'bg-slate-500/10 text-slate-400 border-slate-500/30',
      borderClass: 'border-l-slate-600',
    },
    Contradicted: {
      label: 'Contradicted',
      icon: <XCircle className="w-3.5 h-3.5" />,
      badgeClass: 'bg-rose-500/10 text-rose-400 border-rose-500/30',
      borderClass: 'border-l-rose-500',
    },
    Uncertain: {
      label: 'Uncertain',
      icon: <AlertTriangle className="w-3.5 h-3.5" />,
      badgeClass: 'bg-indigo-500/10 text-indigo-400 border-indigo-500/30',
      borderClass: 'border-l-indigo-500',
    },
  };

  const filteredClaims = claims.filter((claim) => {
    const matchesFilter = filter === 'ALL' || claim.status === filter;
    const matchesSearch =
      claim.claim_text.toLowerCase().includes(searchQuery.toLowerCase()) ||
      claim.category.toLowerCase().includes(searchQuery.toLowerCase()) ||
      (claim.evidence_quote && claim.evidence_quote.toLowerCase().includes(searchQuery.toLowerCase()));
    return matchesFilter && matchesSearch;
  });

  return (
    <div className="bg-slate-900/90 border border-slate-800 rounded-2xl shadow-xl p-5 lg:p-6 space-y-5">
      {/* Header and Controls */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-800/80 pb-4">
        <div>
          <h2 className="text-base font-semibold text-white flex items-center gap-2">
            <span>Atomic Claim Audit &amp; Quote Verification</span>
            <span className="text-xs bg-slate-800 text-slate-300 px-2 py-0.5 rounded-full font-mono">
              {claims.length} claims
            </span>
          </h2>
          <p className="text-xs text-slate-400 mt-0.5">
            Every displayed quote is deterministically verified against the extracted page text.
          </p>
        </div>

        {/* Filter Pills and Search */}
        <div className="flex flex-wrap items-center gap-2">
          {/* Search box */}
          <div className="relative flex items-center">
            <Search className="w-3.5 h-3.5 text-slate-500 absolute left-2.5" />
            <input
              type="text"
              placeholder="Search claims..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="bg-slate-950/80 border border-slate-800 focus:border-indigo-500 text-xs text-slate-200 placeholder-slate-600 rounded-lg pl-8 pr-2.5 py-1 outline-none w-36 lg:w-44"
            />
          </div>

          <div className="flex flex-wrap items-center gap-1">
            {['ALL', 'Supported', 'Partial Match', 'Not Found', 'Contradicted', 'Uncertain'].map(
              (statusKey) => (
                <button
                  key={statusKey}
                  onClick={() => setFilter(statusKey)}
                  className={`px-2 py-1 text-xs rounded-lg font-medium transition-all cursor-pointer ${
                    filter === statusKey
                      ? 'bg-indigo-600 text-white shadow-sm'
                      : 'bg-slate-950/80 text-slate-400 hover:text-slate-200 border border-slate-800'
                  }`}
                >
                  {statusKey}
                </button>
              )
            )}
          </div>
        </div>
      </div>

      {/* Claims List */}
      <div className="space-y-3">
        {filteredClaims.length === 0 ? (
          <div className="text-center py-12 text-slate-500 text-xs">
            No claims found matching current filter.
          </div>
        ) : (
          filteredClaims.map((claim) => {
            const config = statusConfig[claim.status];
            return (
              <div
                key={claim.claim_id}
                className={`bg-slate-950/60 border border-slate-800/90 rounded-xl p-4 transition-all hover:border-slate-700/80 border-l-4 ${config.borderClass} space-y-3`}
              >
                {/* Claim Top Meta */}
                <div className="flex flex-wrap items-center justify-between gap-2">
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-mono font-bold text-slate-400 bg-slate-900 px-1.5 py-0.5 rounded border border-slate-800">
                      {claim.claim_id}
                    </span>
                    <span className="text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded bg-slate-800/80 text-slate-300">
                      From {claim.source_part}
                    </span>
                    <span className="text-[10px] font-semibold text-indigo-300 bg-indigo-950/40 border border-indigo-800/30 px-2 py-0.5 rounded">
                      {claim.category}
                    </span>
                  </div>

                  <div className="flex items-center gap-2">
                    <span
                      className={`flex items-center gap-1 text-xs font-semibold px-2.5 py-0.5 rounded-full border ${config.badgeClass}`}
                    >
                      {config.icon}
                      <span>{claim.status}</span>
                    </span>
                    <span className="text-xs font-mono font-medium text-slate-400 bg-slate-900/80 px-2 py-0.5 rounded border border-slate-800">
                      {Math.round(claim.similarity_score)}% sim
                    </span>
                  </div>
                </div>

                {/* Claim Assertion Text */}
                <div className="text-sm font-medium text-white pl-1">
                  "{claim.claim_text}"
                </div>

                {/* Deterministic Verified Evidence Quote Box (Rule 1) */}
                <div className="bg-slate-900/80 border border-slate-800 rounded-lg p-3 space-y-1.5">
                  <div className="flex items-center justify-between">
                    <span className="text-[11px] font-bold uppercase tracking-wider text-slate-400 flex items-center gap-1">
                      <Quote className="w-3 h-3 text-slate-500" />
                      <span>Extracted Page Evidence</span>
                    </span>

                    {claim.is_quote_verified ? (
                      <span className="flex items-center gap-1 text-[10px] font-bold text-emerald-400 bg-emerald-950/40 border border-emerald-800/40 px-2 py-0.5 rounded">
                        <Check className="w-3 h-3" />
                        <span>Verified Substring in [{claim.quote_source_element || 'body'}]</span>
                      </span>
                    ) : (
                      <span className="text-[10px] font-medium text-slate-500">
                        Unverified
                      </span>
                    )}
                  </div>

                  <div className="text-xs italic text-slate-300">
                    {claim.is_quote_verified ? (
                      <span className="text-emerald-300/90 font-mono">
                        "{claim.evidence_quote}"
                      </span>
                    ) : (
                      <span className="text-slate-500">
                        {claim.evidence_quote || 'No verified evidence quote available.'}
                      </span>
                    )}
                  </div>
                </div>

                {/* Reason & Action Footer */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-2 text-xs pt-1 border-t border-slate-850">
                  <div className="text-slate-400">
                    <strong className="text-slate-300 font-semibold">Evaluation:</strong>{' '}
                    {claim.status_reason}
                  </div>
                  <div className="text-indigo-300">
                    <strong className="text-indigo-200 font-semibold">Suggested Fix:</strong>{' '}
                    {claim.suggested_action}
                  </div>
                </div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
};
