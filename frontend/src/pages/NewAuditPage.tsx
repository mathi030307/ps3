import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { AdInputPanel } from '../components/AdInputPanel';
import type { AdInput, AuditResponse, SyntheticScenario } from '../types/audit';
import { fetchDemoScenarios, fetchDemoScenarioById, auditByUrl, auditBySnapshot, auditGeneral } from '../services/api';
import { ShieldAlert, Sparkles } from 'lucide-react';

interface NewAuditPageProps {
  onSetAuditResult: (result: AuditResponse) => void;
}

export const NewAuditPage: React.FC<NewAuditPageProps> = ({ onSetAuditResult }) => {
  const navigate = useNavigate();
  const [ad, setAd] = useState<AdInput>({
    headline: '',
    description: '',
    cta: '',
  });
  const [url, setUrl] = useState<string>('');
  const [htmlContent, setHtmlContent] = useState<string>('');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [isSynthetic, setIsSynthetic] = useState<boolean>(false);

  const [scenarios, setScenarios] = useState<SyntheticScenario[]>([]);
  const [selectedScenarioId, setSelectedScenarioId] = useState<string>('');

  const [loading, setLoading] = useState<boolean>(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [errorType, setErrorType] = useState<string | null>(null);

  useEffect(() => {
    fetchDemoScenarios()
      .then((data) => setScenarios(data))
      .catch((err) => console.error('Failed to load scenarios', err));
  }, []);

  const handleSelectScenario = async (scenarioId: string) => {
    setSelectedScenarioId(scenarioId);
    if (!scenarioId) return;

    try {
      const detailed = await fetchDemoScenarioById(scenarioId);
      setAd(detailed.ad);
      setHtmlContent(detailed.html_content || '');
      setUrl('');
      setSelectedFile(null);
      setIsSynthetic(true);
      setErrorMessage(null);
      setErrorType(null);
    } catch (err) {
      console.error('Failed to load scenario details', err);
    }
  };

  const handleRunAudit = async () => {
    setLoading(true);
    setErrorMessage(null);
    setErrorType(null);

    try {
      let response: AuditResponse;
      if (selectedFile) {
        response = await auditBySnapshot(ad, selectedFile);
      } else if (url && url.trim()) {
        response = await auditByUrl(ad, url.trim(), isSynthetic);
      } else {
        response = await auditGeneral({
          ad,
          html_content: htmlContent ? htmlContent.trim() : undefined,
          is_synthetic_demo: isSynthetic,
        });
      }

      onSetAuditResult(response);

      if (!response.success) {
        setErrorMessage(response.error_message || 'Audit analysis failed.');
        setErrorType(response.error_type || 'GENERAL_ERROR');
      } else {
        navigate('/audit/result');
      }
    } catch (err: any) {
      setErrorMessage(err.message || 'An unexpected network error occurred.');
      setErrorType('NETWORK_ERROR');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6 py-4 max-w-4xl mx-auto">
      {/* Page Header */}
      <div className="bg-white border border-slate-200 rounded-3xl p-6 lg:p-8 shadow-xs flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-blue-50 text-blue-700 text-xs font-semibold border border-blue-200 mb-2">
            <Sparkles className="w-3.5 h-3.5" />
            <span>Audit Configuration</span>
          </div>
          <h1 className="text-2xl font-extrabold text-slate-900 tracking-tight">
            Start a Message Match Audit
          </h1>
          <p className="text-sm text-slate-600 mt-1">
            Compare ad copy promises directly against extracted landing page text.
          </p>
        </div>

        {/* Preset scenario dropdown */}
        <div className="flex items-center gap-2 bg-slate-50 border border-slate-200 rounded-xl px-3 py-2">
          <span className="text-xs font-semibold text-slate-600 whitespace-nowrap">
            Load preset:
          </span>
          <select
            value={selectedScenarioId}
            onChange={(e) => handleSelectScenario(e.target.value)}
            className="bg-transparent text-xs text-slate-800 font-medium outline-none cursor-pointer"
          >
            <option value="">Choose Synthetic example...</option>
            {scenarios.map((s) => (
              <option key={s.id} value={s.id}>
                [{s.label}] {s.name}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Structured Error Alert (Rule 2) */}
      {errorMessage && (
        <div className="bg-rose-50 border border-rose-200 rounded-2xl p-5 flex items-start gap-3.5 shadow-xs">
          <ShieldAlert className="w-5 h-5 text-rose-600 shrink-0 mt-0.5" />
          <div className="space-y-1">
            <h3 className="text-sm font-bold text-rose-900">
              Audit Analysis Could Not Complete [{errorType}]
            </h3>
            <p className="text-xs text-rose-800 leading-relaxed">
              {errorMessage}
            </p>
            <p className="text-[11px] text-rose-600">
              Rule 2 strictly enforced: Never claims a page was analyzed if fetching or extraction failed. Score is marked Unavailable (null).
            </p>
          </div>
        </div>
      )}

      {/* Input Form Panel */}
      <AdInputPanel
        ad={ad}
        setAd={setAd}
        url={url}
        setUrl={setUrl}
        htmlContent={htmlContent}
        setHtmlContent={setHtmlContent}
        selectedFile={selectedFile}
        setSelectedFile={setSelectedFile}
        onRunAudit={handleRunAudit}
        loading={loading}
        isSynthetic={isSynthetic}
      />
    </div>
  );
};
