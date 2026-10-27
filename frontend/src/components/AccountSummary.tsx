import React, { useState } from 'react';
import { Account } from '../types';
import { Copy, Check, ArrowDownLeft, ArrowUpRight, ArrowLeftRight, Landmark } from 'lucide-react';

interface AccountSummaryProps {
  account: Account;
  onOpenCredit: () => void;
  onOpenDebit: () => void;
  onOpenTransfer: () => void;
}

export const AccountSummary: React.FC<AccountSummaryProps> = ({
  account,
  onOpenCredit,
  onOpenDebit,
  onOpenTransfer,
}) => {
  const [copied, setCopied] = useState(false);

  const handleCopyId = () => {
    navigator.clipboard.writeText(account.id);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const balanceNumber = parseFloat(account.balance);
  const formattedBalance = balanceNumber.toLocaleString('en-US', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  });

  return (
    <div className="relative overflow-hidden rounded-2xl border border-slate-800 bg-gradient-to-br from-[#131b2e] via-[#111827] to-[#0d1322] p-6 sm:p-8 shadow-xl">
      {/* Decorative gradient glow */}
      <div className="absolute top-0 right-0 -mr-20 -mt-20 w-80 h-80 rounded-full bg-indigo-500/10 blur-3xl pointer-events-none" />
      <div className="absolute bottom-0 left-0 -ml-20 -mb-20 w-80 h-80 rounded-full bg-purple-500/10 blur-3xl pointer-events-none" />

      <div className="relative flex flex-col md:flex-row md:items-center md:justify-between gap-6">
        {/* Left Column: Account Info & Balance */}
        <div className="space-y-3">
          <div className="flex items-center gap-2">
            <span className="p-1.5 rounded-lg bg-indigo-500/10 text-indigo-400">
              <Landmark className="w-4 h-4" />
            </span>
            <span className="text-xs font-semibold uppercase tracking-wider text-indigo-400">
              Active Account
            </span>
          </div>

          <div>
            <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight text-white">
              {account.name}
            </h1>
            <div className="flex items-center gap-2 mt-1.5">
              <span className="text-xs font-mono text-slate-400 select-all">
                {account.id}
              </span>
              <button
                onClick={handleCopyId}
                className="p-1 text-slate-500 hover:text-slate-300 rounded hover:bg-slate-800 transition"
                title="Copy Account ID"
              >
                {copied ? (
                  <Check className="w-3.5 h-3.5 text-emerald-400" />
                ) : (
                  <Copy className="w-3.5 h-3.5" />
                )}
              </button>
            </div>
          </div>

          <div className="pt-2">
            <span className="text-xs font-medium text-slate-400 block mb-1">
              Available Balance
            </span>
            <div className="flex items-baseline gap-2">
              <span className="text-3xl sm:text-4xl font-extrabold font-mono text-white tracking-tight">
                ${formattedBalance}
              </span>
              <span className="text-xs font-medium px-2 py-0.5 rounded bg-slate-800 text-slate-400 border border-slate-700/60 font-mono">
                USD
              </span>
            </div>
          </div>
        </div>

        {/* Right Column: Actions */}
        <div className="flex flex-wrap sm:flex-nowrap gap-3 shrink-0">
          <button
            onClick={onOpenCredit}
            className="flex-1 sm:flex-none flex items-center justify-center gap-2 px-4 py-2.5 bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold rounded-xl shadow-lg shadow-emerald-900/30 transition active:scale-[0.98]"
          >
            <ArrowDownLeft className="w-4 h-4" />
            <span>Credit / Deposit</span>
          </button>

          <button
            onClick={onOpenDebit}
            className="flex-1 sm:flex-none flex items-center justify-center gap-2 px-4 py-2.5 bg-rose-600 hover:bg-rose-500 text-white text-xs font-semibold rounded-xl shadow-lg shadow-rose-900/30 transition active:scale-[0.98]"
          >
            <ArrowUpRight className="w-4 h-4" />
            <span>Debit / Withdraw</span>
          </button>

          <button
            onClick={onOpenTransfer}
            className="w-full sm:w-auto flex items-center justify-center gap-2 px-4 py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold rounded-xl shadow-lg shadow-indigo-900/30 transition active:scale-[0.98]"
          >
            <ArrowLeftRight className="w-4 h-4" />
            <span>Transfer</span>
          </button>
        </div>
      </div>
    </div>
  );
};
