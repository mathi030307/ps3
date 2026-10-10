import React, { useState } from 'react';
import { X, Copy, Download, Check, FileText, Table, Code2, Globe } from 'lucide-react';
import type { AuditResponse } from '../types/audit';
import { exportReport } from '../services/api';

interface ExportModalProps {
  audit: AuditResponse;
  isOpen: boolean;
  onClose: () => void;
}

export const ExportModal: React.FC<ExportModalProps> = ({ audit, isOpen, onClose }) => {
  const [activeFormat, setActiveFormat] = useState<'html' | 'csv' | 'json' | 'markdown'>('html');
  const [exportedText, setExportedText] = useState<string>('');
  const [copied, setCopied] = useState<boolean>(false);
  const [loadingExport, setLoadingExport] = useState<boolean>(false);

  React.useEffect(() => {
    if (!isOpen) return;

    const loadContent = async () => {
      setLoadingExport(true);
      try {
        const text = await exportReport(audit, activeFormat);
        setExportedText(text);
      } catch (e) {
        setExportedText(JSON.stringify(audit, null, 2));
      } finally {
        setLoadingExport(false);
      }
    };

    loadContent();
  }, [isOpen, activeFormat, audit]);

  if (!isOpen) return null;

  const handleCopy = () => {
    navigator.clipboard.writeText(exportedText);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleDownload = () => {
    const ext = activeFormat === 'html' ? 'html' : activeFormat === 'csv' ? 'csv' : activeFormat === 'markdown' ? 'md' : 'json';
    const mime = activeFormat === 'json' ? 'application/json' : activeFormat === 'html' ? 'text/html' : 'text/plain';
    const blob = new Blob([exportedText], { type: mime });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `message-match-audit-${Date.now()}.${ext}`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-xs animate-in fade-in duration-200">
      <div className="bg-white border border-slate-200 rounded-3xl w-full max-w-3xl shadow-2xl flex flex-col max-h-[85vh] overflow-hidden">
        {/* Modal Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-200">
          <div className="flex items-center gap-2">
            <Download className="w-5 h-5 text-blue-600" />
            <h3 className="font-bold text-slate-900 text-base">
              Export Message Match Audit Report
            </h3>
          </div>
          <button
            onClick={onClose}
            className="text-slate-400 hover:text-slate-800 p-1.5 rounded-xl hover:bg-slate-100 transition-colors cursor-pointer"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Format Selector */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 px-6 py-3 bg-slate-50 border-b border-slate-200">
          <div className="flex flex-wrap bg-slate-200/70 p-1 rounded-xl gap-1">
            <button
              onClick={() => setActiveFormat('html')}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition-all cursor-pointer ${
                activeFormat === 'html'
                  ? 'bg-white text-blue-700 shadow-xs'
                  : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              <Globe className="w-3.5 h-3.5" />
              <span>HTML Report</span>
            </button>

            <button
              onClick={() => setActiveFormat('csv')}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition-all cursor-pointer ${
                activeFormat === 'csv'
                  ? 'bg-white text-emerald-700 shadow-xs'
                  : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              <Table className="w-3.5 h-3.5" />
              <span>Claims CSV</span>
            </button>

            <button
              onClick={() => setActiveFormat('json')}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition-all cursor-pointer ${
                activeFormat === 'json'
                  ? 'bg-white text-indigo-700 shadow-xs'
                  : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              <Code2 className="w-3.5 h-3.5" />
              <span>Raw JSON</span>
            </button>

            <button
              onClick={() => setActiveFormat('markdown')}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition-all cursor-pointer ${
                activeFormat === 'markdown'
                  ? 'bg-white text-slate-900 shadow-xs'
                  : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              <FileText className="w-3.5 h-3.5" />
              <span>Markdown</span>
            </button>
          </div>

          {/* Action Buttons */}
          <div className="flex items-center gap-2">
            <button
              onClick={handleCopy}
              className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold text-slate-700 hover:text-slate-900 bg-white hover:bg-slate-50 border border-slate-200 rounded-lg transition-all cursor-pointer"
            >
              {copied ? (
                <>
                  <Check className="w-3.5 h-3.5 text-emerald-600" />
                  <span className="text-emerald-700">Copied!</span>
                </>
              ) : (
                <>
                  <Copy className="w-3.5 h-3.5" />
                  <span>Copy</span>
                </>
              )}
            </button>

            <button
              onClick={handleDownload}
              className="flex items-center gap-1.5 px-3.5 py-1.5 text-xs font-semibold text-white bg-blue-600 hover:bg-blue-700 rounded-lg shadow-xs transition-all cursor-pointer"
            >
              <Download className="w-3.5 h-3.5" />
              <span>Download</span>
            </button>
          </div>
        </div>

        {/* Content Viewer */}
        <div className="p-6 overflow-y-auto flex-1 bg-slate-50 font-mono text-xs text-slate-800 whitespace-pre leading-relaxed select-all">
          {loadingExport ? (
            <div className="flex items-center justify-center py-12 text-slate-400">
              Generating formatted export...
            </div>
          ) : (
            exportedText
          )}
        </div>
      </div>
    </div>
  );
};
