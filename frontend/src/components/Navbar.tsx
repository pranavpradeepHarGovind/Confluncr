import React from 'react';
import { ShieldCheck, Plus, BookOpen, RefreshCw } from 'lucide-react';

interface NavbarProps {
  onOpenCreateAccount: () => void;
  onRefresh: () => void;
  isRefreshing: boolean;
}

export const Navbar: React.FC<NavbarProps> = ({
  onOpenCreateAccount,
  onRefresh,
  isRefreshing,
}) => {
  return (
    <header className="sticky top-0 z-40 border-b border-slate-800 bg-[#0B0F19]/80 backdrop-blur-md">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        {/* Brand */}
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-indigo-600 via-indigo-500 to-purple-500 flex items-center justify-center shadow-lg shadow-indigo-500/20">
            <ShieldCheck className="w-6 h-6 text-white" />
          </div>
          <div>
            <span className="text-xl font-bold tracking-tight text-white flex items-center gap-2">
              VaultFlow
              <span className="text-[10px] font-semibold tracking-wider uppercase px-2 py-0.5 rounded-full bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
                Core Banking
              </span>
            </span>
          </div>
        </div>

        {/* Actions */}
        <div className="flex items-center gap-3">
          <button
            onClick={onRefresh}
            disabled={isRefreshing}
            className="p-2 text-slate-400 hover:text-slate-100 rounded-lg hover:bg-slate-800/80 transition flex items-center gap-1.5 text-xs font-medium border border-slate-800"
            title="Refresh accounts & balances"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${isRefreshing ? 'animate-spin text-indigo-400' : ''}`} />
            <span className="hidden sm:inline">Refresh</span>
          </button>

          <a
            href="http://localhost:8000/docs"
            target="_blank"
            rel="noopener noreferrer"
            className="hidden sm:flex items-center gap-1.5 px-3 py-2 text-xs font-medium text-slate-300 hover:text-white rounded-lg hover:bg-slate-800/80 border border-slate-800 transition"
          >
            <BookOpen className="w-3.5 h-3.5 text-indigo-400" />
            API Docs (Swagger)
          </a>

          <button
            onClick={onOpenCreateAccount}
            className="flex items-center gap-1.5 px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold rounded-lg shadow-md shadow-indigo-600/25 transition active:scale-[0.98]"
          >
            <Plus className="w-4 h-4" />
            New Account
          </button>
        </div>
      </div>
    </header>
  );
};
