import { useState } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { Navbar } from './components/Navbar';
import { DashboardPage } from './pages/DashboardPage';
import { NewAuditPage } from './pages/NewAuditPage';
import { ResultsPage } from './pages/ResultsPage';
import { ExportModal } from './components/ExportModal';
import type { AuditResponse } from './types/audit';

export function App() {
  const [auditResult, setAuditResult] = useState<AuditResponse | null>(null);
  const [isExportOpen, setIsExportOpen] = useState<boolean>(false);

  return (
    <BrowserRouter>
      <div className="min-h-screen bg-slate-50 text-slate-900 flex flex-col font-sans selection:bg-blue-600 selection:text-white">
        {/* Navigation Bar */}
        <Navbar
          auditResult={auditResult}
          onOpenExport={() => setIsExportOpen(true)}
        />

        {/* Main Content Area */}
        <main className="flex-1 max-w-7xl w-full mx-auto px-4 lg:px-8 py-6">
          <Routes>
            <Route
              path="/"
              element={<DashboardPage onSetAuditResult={setAuditResult} />}
            />
            <Route
              path="/audit/new"
              element={<NewAuditPage onSetAuditResult={setAuditResult} />}
            />
            <Route
              path="/audit/result"
              element={
                <ResultsPage
                  auditResult={auditResult}
                  onOpenExportModal={() => setIsExportOpen(true)}
                />
              }
            />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </main>

        {/* Export Modal */}
        {auditResult && (
          <ExportModal
            audit={auditResult}
            isOpen={isExportOpen}
            onClose={() => setIsExportOpen(false)}
          />
        )}

        {/* Light Footer */}
        <footer className="border-t border-slate-200 bg-white py-6 px-4 text-xs text-slate-500">
          <div className="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-3">
            <span>
              <strong>PS-03 Ad-to-Landing-Page Message Match Auditor</strong> &bull; Hackathon MVP
            </span>
            <span className="text-[11px] text-slate-400">
              Deterministic quote verification &bull; Formula-governed scoring &bull; WCAG AA contrast
            </span>
          </div>
        </footer>
      </div>
    </BrowserRouter>
  );
}

export default App;
