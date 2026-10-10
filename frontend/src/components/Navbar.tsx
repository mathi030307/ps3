import React from 'react';
import { NavLink } from 'react-router-dom';
import { Target, PlusCircle, LayoutDashboard, FileBarChart, ShieldCheck } from 'lucide-react';
import type { AuditResponse } from '../types/audit';

interface NavbarProps {
  auditResult: AuditResponse | null;
  onOpenExport?: () => void;
}

export const Navbar: React.FC<NavbarProps> = ({ auditResult, onOpenExport }) => {
  return (
    <header className="border-b border-slate-200 bg-white/95 backdrop-blur-md sticky top-0 z-40 px-4 lg:px-8 py-3 shadow-xs">
      <div className="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-4">
        {/* Brand */}
        <NavLink to="/" className="flex items-center gap-3 group">
          <div className="w-9 h-9 rounded-xl bg-slate-900 p-0.5 shadow-sm flex items-center justify-center group-hover:bg-blue-600 transition-colors">
            <Target className="w-5 h-5 text-white" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-bold text-base tracking-tight text-slate-900 group-hover:text-blue-600 transition-colors">
                Message Match Auditor
              </span>
              <span className="text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded-full bg-slate-100 text-slate-700 border border-slate-200">
                PS-03
              </span>
            </div>
            <p className="text-[11px] text-slate-500">
              Deterministic Continuity &amp; Quote Provenance
            </p>
          </div>
        </NavLink>

        {/* Navigation Tabs */}
        <nav className="flex items-center gap-1 bg-slate-100 p-1 rounded-xl border border-slate-200 text-xs font-semibold">
          <NavLink
            to="/"
            end
            className={({ isActive }) =>
              `flex items-center gap-1.5 px-3 py-1.5 rounded-lg transition-all ${
                isActive
                  ? 'bg-white text-slate-900 shadow-xs'
                  : 'text-slate-600 hover:text-slate-900'
              }`
            }
          >
            <LayoutDashboard className="w-3.5 h-3.5" />
            <span>Dashboard</span>
          </NavLink>

          <NavLink
            to="/audit/new"
            className={({ isActive }) =>
              `flex items-center gap-1.5 px-3 py-1.5 rounded-lg transition-all ${
                isActive
                  ? 'bg-white text-blue-600 shadow-xs'
                  : 'text-slate-600 hover:text-slate-900'
              }`
            }
          >
            <PlusCircle className="w-3.5 h-3.5" />
            <span>New Audit</span>
          </NavLink>

          <NavLink
            to="/audit/result"
            className={({ isActive }) =>
              `flex items-center gap-1.5 px-3 py-1.5 rounded-lg transition-all ${
                isActive
                  ? 'bg-white text-blue-600 shadow-xs'
                  : 'text-slate-600 hover:text-slate-900'
              }`
            }
          >
            <FileBarChart className="w-3.5 h-3.5" />
            <span>Audit Results</span>
          </NavLink>
        </nav>

        {/* Security / Action info */}
        <div className="flex items-center gap-2">
          {auditResult && onOpenExport && (
            <button
              onClick={onOpenExport}
              className="px-3 py-1.5 text-xs font-semibold text-white bg-blue-600 hover:bg-blue-700 rounded-lg shadow-xs transition-colors cursor-pointer"
            >
              Export Report
            </button>
          )}

          <div className="hidden lg:flex items-center gap-1 text-[11px] font-medium text-emerald-700 bg-emerald-50 border border-emerald-200 px-2 py-1 rounded-md">
            <ShieldCheck className="w-3.5 h-3.5 text-emerald-600" />
            <span>SSRF Guard</span>
          </div>
        </div>
      </div>
    </header>
  );
};
