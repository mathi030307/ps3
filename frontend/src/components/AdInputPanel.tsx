import React, { useState, useRef } from 'react';
import { Globe, Upload, ArrowRight, Loader2, AlertCircle, FileCheck } from 'lucide-react';
import type { AdInput } from '../types/audit';

interface AdInputPanelProps {
  ad: AdInput;
  setAd: React.Dispatch<React.SetStateAction<AdInput>>;
  url: string;
  setUrl: (val: string) => void;
  htmlContent: string;
  setHtmlContent: (val: string) => void;
  selectedFile: File | null;
  setSelectedFile: (file: File | null) => void;
  onRunAudit: () => void;
  loading: boolean;
  isSynthetic: boolean;
}

export const AdInputPanel: React.FC<AdInputPanelProps> = ({
  ad,
  setAd,
  url,
  setUrl,
  htmlContent,
  setHtmlContent,
  selectedFile,
  setSelectedFile,
  onRunAudit,
  loading,
  isSynthetic,
}) => {
  const [activeTab, setActiveTab] = useState<'url' | 'upload' | 'raw'>(
    htmlContent ? 'raw' : 'url'
  );
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      setSelectedFile(file);
      const reader = new FileReader();
      reader.onload = (event) => {
        if (event.target?.result) {
          setHtmlContent(event.target.result as string);
        }
      };
      reader.readAsText(file);
    }
  };

  const isAdValid = ad.headline.trim().length >= 2 && ad.description.trim().length >= 2;
  const isPageValid =
    (activeTab === 'url' && url.trim().length >= 5) ||
    (activeTab === 'upload' && selectedFile !== null) ||
    (activeTab === 'raw' && htmlContent.trim().length >= 10);

  const canSubmit = isAdValid && isPageValid && !loading;

  return (
    <div className="bg-white border border-slate-200 rounded-3xl shadow-xs p-6 lg:p-8 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-slate-100 pb-4">
        <div>
          <h2 className="text-base font-bold text-slate-900 flex items-center gap-2">
            <span>Audit Parameters</span>
            {isSynthetic && (
              <span className="text-[11px] font-bold text-amber-800 bg-amber-50 border border-amber-200 px-2 py-0.5 rounded-full">
                Synthetic example
              </span>
            )}
          </h2>
          <p className="text-xs text-slate-500 mt-0.5">
            Compare your ad assertions against the actual landing page content.
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Left Column: Ad Inputs */}
        <div className="space-y-4">
          <h3 className="text-xs font-bold uppercase tracking-wider text-blue-700 flex items-center gap-1.5">
            <span>1. Ad Copy Assertion</span>
          </h3>

          {/* Headline */}
          <div>
            <div className="flex justify-between text-xs text-slate-700 font-semibold mb-1.5">
              <label htmlFor="ad-headline">Ad Headline *</label>
              <span className="text-[11px] text-slate-400 font-normal">{ad.headline.length}/100</span>
            </div>
            <input
              id="ad-headline"
              type="text"
              placeholder="e.g. Modern Project Management Software for Agile Teams"
              value={ad.headline}
              onChange={(e) => setAd({ ...ad, headline: e.target.value })}
              className="w-full bg-slate-50 border border-slate-200 focus:bg-white focus:border-blue-600 focus:ring-1 focus:ring-blue-600 text-sm text-slate-900 placeholder-slate-400 rounded-xl px-3.5 py-2.5 transition-all outline-none font-medium"
              disabled={loading}
            />
          </div>

          {/* Description */}
          <div>
            <div className="flex justify-between text-xs text-slate-700 font-semibold mb-1.5">
              <label htmlFor="ad-description">Ad Body / Description *</label>
              <span className="text-[11px] text-slate-400 font-normal">{ad.description.length}/500</span>
            </div>
            <textarea
              id="ad-description"
              rows={3}
              placeholder="e.g. Automate sprint planning and track roadmaps with 99.9% uptime. Includes 14-day free trial."
              value={ad.description}
              onChange={(e) => setAd({ ...ad, description: e.target.value })}
              className="w-full bg-slate-50 border border-slate-200 focus:bg-white focus:border-blue-600 focus:ring-1 focus:ring-blue-600 text-sm text-slate-900 placeholder-slate-400 rounded-xl px-3.5 py-2.5 transition-all outline-none resize-none font-medium"
              disabled={loading}
            />
          </div>

          {/* CTA */}
          <div>
            <div className="flex justify-between text-xs text-slate-700 font-semibold mb-1.5">
              <label htmlFor="ad-cta">Ad Call to Action (Optional)</label>
              <span className="text-[11px] text-slate-400 font-normal">{ad.cta?.length || 0}/50</span>
            </div>
            <input
              id="ad-cta"
              type="text"
              placeholder="e.g. Start 14-Day Free Trial"
              value={ad.cta || ''}
              onChange={(e) => setAd({ ...ad, cta: e.target.value })}
              className="w-full bg-slate-50 border border-slate-200 focus:bg-white focus:border-blue-600 focus:ring-1 focus:ring-blue-600 text-sm text-slate-900 placeholder-slate-400 rounded-xl px-3.5 py-2.5 transition-all outline-none font-medium"
              disabled={loading}
            />
          </div>
        </div>

        {/* Right Column: Landing Page Source */}
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-800 flex items-center gap-1.5">
              <span>2. Landing Page Destination</span>
            </h3>

            {/* Source tabs */}
            <div className="flex bg-slate-100 p-0.5 rounded-xl border border-slate-200 text-xs font-semibold">
              <button
                type="button"
                onClick={() => setActiveTab('url')}
                className={`px-3 py-1 rounded-lg transition-all cursor-pointer ${
                  activeTab === 'url'
                    ? 'bg-white text-slate-900 shadow-xs'
                    : 'text-slate-600 hover:text-slate-900'
                }`}
              >
                Live URL
              </button>
              <button
                type="button"
                onClick={() => setActiveTab('upload')}
                className={`px-3 py-1 rounded-lg transition-all cursor-pointer ${
                  activeTab === 'upload'
                    ? 'bg-white text-slate-900 shadow-xs'
                    : 'text-slate-600 hover:text-slate-900'
                }`}
              >
                Upload Snapshot
              </button>
              <button
                type="button"
                onClick={() => setActiveTab('raw')}
                className={`px-3 py-1 rounded-lg transition-all cursor-pointer ${
                  activeTab === 'raw'
                    ? 'bg-white text-slate-900 shadow-xs'
                    : 'text-slate-600 hover:text-slate-900'
                }`}
              >
                Direct HTML
              </button>
            </div>
          </div>

          {/* Tab 1: Live URL */}
          {activeTab === 'url' && (
            <div className="space-y-2">
              <label htmlFor="page-url" className="text-xs text-slate-700 font-semibold block">
                Public Website URL
              </label>
              <div className="relative">
                <Globe className="w-4 h-4 text-slate-400 absolute left-3.5 top-3" />
                <input
                  id="page-url"
                  type="url"
                  placeholder="https://example.com/landing-page"
                  value={url}
                  onChange={(e) => setUrl(e.target.value)}
                  className="w-full bg-slate-50 border border-slate-200 focus:bg-white focus:border-blue-600 focus:ring-1 focus:ring-blue-600 text-sm text-slate-900 placeholder-slate-400 rounded-xl pl-10 pr-3.5 py-2.5 transition-all outline-none"
                  disabled={loading}
                />
              </div>
              <p className="text-[11px] text-slate-500 flex items-center gap-1">
                <AlertCircle className="w-3.5 h-3.5 text-blue-600" />
                SSRF-protected. Blocks private subnets, cloud metadata (169.254.169.254), and non-HTTP schemes.
              </p>
            </div>
          )}

          {/* Tab 2: Upload HTML Snapshot */}
          {activeTab === 'upload' && (
            <div className="space-y-2">
              <label className="text-xs text-slate-700 font-semibold block">
                HTML Snapshot File (.html or .htm)
              </label>
              <div
                onClick={() => fileInputRef.current?.click()}
                className={`border-2 border-dashed rounded-2xl p-6 text-center cursor-pointer transition-all ${
                  selectedFile
                    ? 'border-blue-500 bg-blue-50/40'
                    : 'border-slate-300 hover:border-slate-400 bg-slate-50'
                }`}
              >
                <input
                  ref={fileInputRef}
                  type="file"
                  accept=".html,.htm"
                  onChange={handleFileChange}
                  className="hidden"
                  disabled={loading}
                />
                {selectedFile ? (
                  <div className="flex flex-col items-center">
                    <FileCheck className="w-8 h-8 text-emerald-600 mb-1.5" />
                    <span className="text-xs font-bold text-slate-900">
                      {selectedFile.name}
                    </span>
                    <span className="text-[11px] text-slate-500 mt-0.5">
                      {(selectedFile.size / 1024).toFixed(1)} KB &bull; Click to replace
                    </span>
                  </div>
                ) : (
                  <div className="flex flex-col items-center">
                    <Upload className="w-8 h-8 text-slate-400 mb-1.5" />
                    <span className="text-xs font-bold text-slate-800">
                      Click or drag HTML snapshot file here
                    </span>
                    <span className="text-[11px] text-slate-500 mt-1">
                      Strict validation: &le; 5MB, plain text, scripts stripped passively.
                    </span>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Tab 3: Direct Raw HTML */}
          {activeTab === 'raw' && (
            <div className="space-y-2">
              <div className="flex justify-between text-xs text-slate-700 font-semibold">
                <label htmlFor="raw-html">Direct HTML Snapshot Code</label>
                <span className="text-[11px] text-slate-400 font-normal">{htmlContent.length} chars</span>
              </div>
              <textarea
                id="raw-html"
                rows={5}
                placeholder="<html><body><h1>Landing Page</h1>...</body></html>"
                value={htmlContent}
                onChange={(e) => setHtmlContent(e.target.value)}
                className="w-full font-mono text-xs bg-slate-50 border border-slate-200 focus:bg-white focus:border-blue-600 focus:ring-1 focus:ring-blue-600 text-slate-800 placeholder-slate-400 rounded-xl p-3 transition-all outline-none resize-none"
                disabled={loading}
              />
            </div>
          )}
        </div>
      </div>

      {/* Action Footer */}
      <div className="flex items-center justify-end pt-4 border-t border-slate-100">
        <button
          type="button"
          onClick={onRunAudit}
          disabled={!canSubmit}
          className={`inline-flex items-center gap-2 px-6 py-2.5 rounded-xl font-semibold text-sm transition-all shadow-xs ${
            canSubmit
              ? 'bg-slate-900 hover:bg-slate-800 text-white cursor-pointer'
              : 'bg-slate-200 text-slate-400 cursor-not-allowed'
          }`}
        >
          {loading ? (
            <>
              <Loader2 className="w-4 h-4 animate-spin" />
              <span>Analyzing Continuity...</span>
            </>
          ) : (
            <>
              <span>Run Message Match Audit</span>
              <ArrowRight className="w-4 h-4" />
            </>
          )}
        </button>
      </div>
    </div>
  );
};
