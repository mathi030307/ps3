import React, { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import {
  ArrowRight,
  Sparkles,
  ShieldCheck,
  Play,
  Loader2
} from 'lucide-react';
import type { SyntheticScenario, AuditResponse } from '../types/audit';
import { fetchDemoScenarios, fetchDemoScenarioById, auditGeneral } from '../services/api';

interface DashboardPageProps {
  onSetAuditResult: (result: AuditResponse) => void;
}

export const DashboardPage: React.FC<DashboardPageProps> = ({ onSetAuditResult }) => {
  const navigate = useNavigate();
  const [scenarios, setScenarios] = useState<SyntheticScenario[]>([]);
  const [loadingScenarioId, setLoadingScenarioId] = useState<string | null>(null);
  const [loadingList, setLoadingList] = useState<boolean>(true);

  useEffect(() => {
    fetchDemoScenarios()
      .then((data) => {
        setScenarios(data);
        setLoadingList(false);
      })
      .catch((err) => {
        console.error('Failed to load scenarios', err);
        setLoadingList(false);
      });
  }, []);

  const handleRunDemo = async (scenario: SyntheticScenario) => {
    setLoadingScenarioId(scenario.id);
    try {
      const detailed = await fetchDemoScenarioById(scenario.id);
      const result = await auditGeneral({
        ad: detailed.ad,
        html_content: detailed.html_content,
        is_synthetic_demo: true,
      });
      onSetAuditResult(result);
      navigate('/audit/result');
    } catch (err) {
      console.error('Failed to run demo scenario', err);
    } finally {
      setLoadingScenarioId(null);
    }
  };

  return (
    <div className="space-y-12 py-4">
      {/* Hero Section */}
      <section className="bg-white border border-slate-200 rounded-3xl p-8 lg:p-10 shadow-sm relative overflow-hidden">
        <div className="absolute top-0 right-0 -mr-16 -mt-16 w-80 h-80 rounded-full bg-blue-50/60 pointer-events-none" />
        <div className="max-w-3xl relative z-10 space-y-4">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-50 border border-blue-200 text-blue-700 text-xs font-semibold">
            <Sparkles className="w-3.5 h-3.5" />
            <span>Deterministic Continuity &amp; Substring Quote Provenance</span>
          </div>
          <h1 className="text-3xl lg:text-4xl font-extrabold text-slate-900 tracking-tight leading-tight">
            PS-03 Ad-to-Landing-Page Message Match Auditor
          </h1>
          <p className="text-base text-slate-600 leading-relaxed">
            Eliminate wasted ad spend caused by broken message match. Enter your ad headline, description, and landing page destination to deterministically audit continuity, verify factual claims against source text, and receive an explainable 0–100 score.
          </p>
          <div className="pt-2 flex flex-wrap items-center gap-4">
            <Link
              to="/audit/new"
              className="inline-flex items-center gap-2 px-6 py-3 rounded-xl font-semibold text-sm bg-slate-900 hover:bg-slate-800 text-white shadow-sm transition-all cursor-pointer"
            >
              <span>Start New Audit</span>
              <ArrowRight className="w-4 h-4" />
            </Link>
            <div className="flex items-center gap-1.5 text-xs text-slate-500 font-medium">
              <ShieldCheck className="w-4 h-4 text-emerald-600" />
              <span>Zero Hallucinations &bull; Exact Substrings Enforced</span>
            </div>
          </div>
        </div>
      </section>

      {/* 4-Step Workflow Section */}
      <section className="space-y-4">
        <div>
          <h2 className="text-xl font-bold text-slate-900 tracking-tight">
            How The Deterministic Audit Works
          </h2>
          <p className="text-sm text-slate-500">
            Four rigorous phases verify claims without guessing or fabricating page content.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {/* Step 1 */}
          <div className="bg-white border border-slate-200 rounded-2xl p-5 space-y-3 shadow-xs">
            <div className="w-9 h-9 rounded-xl bg-blue-50 border border-blue-100 text-blue-600 flex items-center justify-center font-bold text-sm">
              1
            </div>
            <h3 className="font-bold text-slate-900 text-sm">
              Input Ad &amp; Destination
            </h3>
            <p className="text-xs text-slate-600 leading-relaxed">
              Provide your ad headline, body copy, optional CTA, and either a live URL (SSRF-protected) or an uploaded HTML snapshot.
            </p>
          </div>

          {/* Step 2 */}
          <div className="bg-white border border-slate-200 rounded-2xl p-5 space-y-3 shadow-xs">
            <div className="w-9 h-9 rounded-xl bg-indigo-50 border border-indigo-100 text-indigo-600 flex items-center justify-center font-bold text-sm">
              2
            </div>
            <h3 className="font-bold text-slate-900 text-sm">
              Extract Visible DOM
            </h3>
            <p className="text-xs text-slate-600 leading-relaxed">
              Passive extraction strips scripts, styles, and hidden CSS text. Validates content threshold to reject empty client SPA shells.
            </p>
          </div>

          {/* Step 3 */}
          <div className="bg-white border border-slate-200 rounded-2xl p-5 space-y-3 shadow-xs">
            <div className="w-9 h-9 rounded-xl bg-emerald-50 border border-emerald-100 text-emerald-600 flex items-center justify-center font-bold text-sm">
              3
            </div>
            <h3 className="font-bold text-slate-900 text-sm">
              Deterministic Quote Check
            </h3>
            <p className="text-xs text-slate-600 leading-relaxed">
              Every candidate quote is verified against source text using <code className="text-slate-800 bg-slate-100 px-1 py-0.5 rounded">verify_quote()</code>. Failsafe outputs fallback notice on any gap.
            </p>
          </div>

          {/* Step 4 */}
          <div className="bg-white border border-slate-200 rounded-2xl p-5 space-y-3 shadow-xs">
            <div className="w-9 h-9 rounded-xl bg-amber-50 border border-amber-100 text-amber-600 flex items-center justify-center font-bold text-sm">
              4
            </div>
            <h3 className="font-bold text-slate-900 text-sm">
              Explainable 0–100 Score
            </h3>
            <p className="text-xs text-slate-600 leading-relaxed">
              Calculates documented weighted score (material claims 2.0x, penalties, hard cap 40 if contradicted) with contribution table.
            </p>
          </div>
        </div>
      </section>

      {/* Synthetic Scenarios Demo List */}
      <section className="space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
          <div>
            <h2 className="text-xl font-bold text-slate-900 tracking-tight flex items-center gap-2">
              <span>Pre-Configured Audit Scenarios</span>
              <span className="text-xs font-semibold px-2.5 py-0.5 rounded-full bg-slate-100 text-slate-700 border border-slate-200">
                7 Scenarios
              </span>
            </h2>
            <p className="text-sm text-slate-500">
              Each scenario executes live through the actual backend pipeline using real HTML samples in <code className="text-slate-700 bg-slate-100 px-1 rounded">sample_data/pages/</code>.
            </p>
          </div>
        </div>

        {loadingList ? (
          <div className="flex items-center justify-center py-12 text-slate-500 text-sm">
            <Loader2 className="w-5 h-5 animate-spin mr-2" />
            <span>Loading evaluation scenarios...</span>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {scenarios.map((scenario) => {
              const isRunning = loadingScenarioId === scenario.id;
              return (
                <div
                  key={scenario.id}
                  className="bg-white border border-slate-200 rounded-2xl p-5 shadow-xs flex flex-col justify-between hover:border-slate-300 transition-all space-y-4"
                >
                  <div className="space-y-2.5">
                    <div className="flex items-center justify-between gap-2">
                      <span className="text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-md bg-amber-50 text-amber-700 border border-amber-200">
                        {scenario.label}
                      </span>
                      <span className="text-[11px] font-semibold text-slate-500">
                        {scenario.category}
                      </span>
                    </div>

                    <h3 className="font-bold text-slate-900 text-sm leading-snug">
                      {scenario.name}
                    </h3>

                    <p className="text-xs text-slate-600 line-clamp-3 leading-relaxed">
                      {scenario.mismatch_description}
                    </p>

                    <div className="bg-slate-50 border border-slate-200 rounded-lg p-2.5 space-y-1 text-xs">
                      <div className="text-slate-500 text-[10px] uppercase font-bold tracking-wider">
                        Ad Headline:
                      </div>
                      <div className="font-semibold text-slate-800 line-clamp-1">
                        "{scenario.ad.headline}"
                      </div>
                    </div>
                  </div>

                  <div className="pt-2 border-t border-slate-100 flex items-center justify-between">
                    <button
                      type="button"
                      onClick={() => handleRunDemo(scenario)}
                      disabled={loadingScenarioId !== null}
                      className="w-full inline-flex items-center justify-center gap-1.5 px-4 py-2 text-xs font-semibold text-slate-900 hover:text-white bg-slate-100 hover:bg-slate-900 border border-slate-200 hover:border-slate-900 rounded-xl transition-all cursor-pointer disabled:opacity-50"
                    >
                      {isRunning ? (
                        <>
                          <Loader2 className="w-3.5 h-3.5 animate-spin" />
                          <span>Executing Pipeline...</span>
                        </>
                      ) : (
                        <>
                          <Play className="w-3.5 h-3.5 fill-current" />
                          <span>Run Live Audit</span>
                        </>
                      )}
                    </button>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </section>
    </div>
  );
};
