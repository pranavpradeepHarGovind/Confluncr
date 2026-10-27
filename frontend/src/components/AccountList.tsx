import React, { useState } from 'react';
import { Account } from '../types';
import { Wallet, Search, ArrowRight, User } from 'lucide-react';

interface AccountListProps {
  accounts: Account[];
  selectedAccountId: string | null;
  onSelectAccount: (accountId: string) => void;
  isLoading: boolean;
}

export const AccountList: React.FC<AccountListProps> = ({
  accounts,
  selectedAccountId,
  onSelectAccount,
  isLoading,
}) => {
  const [search, setSearch] = useState('');

  const filtered = accounts.filter(
    (acc) =>
      acc.name.toLowerCase().includes(search.toLowerCase()) ||
      acc.id.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="bg-[#111827] border border-slate-800 rounded-2xl p-5 shadow-xl">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <Wallet className="w-4 h-4 text-indigo-400" />
          <h2 className="text-sm font-semibold text-white">Accounts ({accounts.length})</h2>
        </div>
      </div>

      {/* Search Input */}
      {accounts.length > 3 && (
        <div className="relative mb-3">
          <Search className="w-3.5 h-3.5 text-slate-500 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search accounts..."
            className="w-full pl-8 pr-3 py-1.5 bg-slate-900 border border-slate-700/60 rounded-lg text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
          />
        </div>
      )}

      {/* Loading Skeletons */}
      {isLoading && accounts.length === 0 ? (
        <div className="space-y-2">
          {[1, 2, 3].map((n) => (
            <div key={n} className="h-16 rounded-xl bg-slate-800/50 animate-pulse" />
          ))}
        </div>
      ) : filtered.length === 0 ? (
        <div className="py-8 text-center text-xs text-slate-500">
          {search ? 'No accounts match your search.' : 'No accounts found. Create one to begin.'}
        </div>
      ) : (
        <div className="space-y-2 max-h-[460px] overflow-y-auto pr-1">
          {filtered.map((acc) => {
            const isSelected = acc.id === selectedAccountId;
            return (
              <button
                key={acc.id}
                onClick={() => onSelectAccount(acc.id)}
                className={`w-full text-left p-3.5 rounded-xl border transition-all duration-200 flex items-center justify-between group ${
                  isSelected
                    ? 'bg-indigo-950/40 border-indigo-500/50 shadow-md shadow-indigo-500/10'
                    : 'bg-slate-900/60 border-slate-800 hover:border-slate-700 hover:bg-slate-900'
                }`}
              >
                <div className="flex items-center gap-3 min-w-0">
                  <div
                    className={`w-8 h-8 rounded-lg flex items-center justify-center shrink-0 ${
                      isSelected
                        ? 'bg-indigo-600 text-white shadow-sm shadow-indigo-600/30'
                        : 'bg-slate-800 text-slate-400 group-hover:text-slate-200'
                    }`}
                  >
                    <User className="w-4 h-4" />
                  </div>
                  <div className="truncate">
                    <h4
                      className={`text-xs font-semibold truncate ${
                        isSelected ? 'text-indigo-200' : 'text-slate-200 group-hover:text-white'
                      }`}
                    >
                      {acc.name}
                    </h4>
                    <p className="text-[10px] text-slate-500 font-mono truncate mt-0.5">
                      {acc.id.slice(0, 8)}...{acc.id.slice(-6)}
                    </p>
                  </div>
                </div>

                <div className="text-right shrink-0 ml-2">
                  <span
                    className={`text-xs font-mono font-bold block ${
                      isSelected ? 'text-white' : 'text-slate-300'
                    }`}
                  >
                    ${parseFloat(acc.balance).toLocaleString('en-US', { minimumFractionDigits: 2 })}
                  </span>
                  <div className="flex items-center justify-end gap-1 text-[10px] text-indigo-400 opacity-0 group-hover:opacity-100 transition-opacity mt-0.5">
                    <span>view</span>
                    <ArrowRight className="w-2.5 h-2.5" />
                  </div>
                </div>
              </button>
            );
          })}
        </div>
      )}
    </div>
  );
};
