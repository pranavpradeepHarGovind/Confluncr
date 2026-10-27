import React from 'react';
import { Transaction } from '../types';
import { ArrowDownLeft, ArrowUpRight, History, Lock, ShieldCheck } from 'lucide-react';

interface TransactionTableProps {
  transactions: Transaction[];
  isLoading: boolean;
  onOpenCredit: () => void;
}

export const TransactionTable: React.FC<TransactionTableProps> = ({
  transactions,
  isLoading,
  onOpenCredit,
}) => {
  const formatDate = (isoString: string) => {
    try {
      const date = new Date(isoString);
      return new Intl.DateTimeFormat('en-US', {
        month: 'short',
        day: 'numeric',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
      }).format(date);
    } catch {
      return isoString;
    }
  };

  return (
    <div className="bg-[#111827] border border-slate-800 rounded-2xl shadow-xl overflow-hidden">
      {/* Table Header / Title */}
      <div className="px-6 py-4 border-b border-slate-800 flex items-center justify-between">
        <div className="flex items-center gap-2.5">
          <History className="w-4 h-4 text-indigo-400" />
          <h3 className="text-sm font-semibold text-white">Transaction History</h3>
        </div>
        <div className="flex items-center gap-1.5 text-[11px] text-slate-400">
          <Lock className="w-3 h-3 text-slate-500" />
          <span>Immutable Ledger</span>
        </div>
      </div>

      {/* Table Content */}
      <div className="overflow-x-auto">
        <table className="w-full text-left text-xs">
          <thead>
            <tr className="border-b border-slate-800 bg-slate-900/40 text-[11px] font-semibold text-slate-400 uppercase tracking-wider">
              <th className="py-3 px-4">Date & Time</th>
              <th className="py-3 px-4">Reference ID</th>
              <th className="py-3 px-4">Type</th>
              <th className="py-3 px-4">Description</th>
              <th className="py-3 px-4 text-right">Amount</th>
              <th className="py-3 px-4 text-right">Balance After</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/60">
            {isLoading ? (
              // Loading skeletons
              Array.from({ length: 5 }).map((_, i) => (
                <tr key={i} className="animate-pulse">
                  <td className="py-3.5 px-4"><div className="h-4 bg-slate-800 rounded w-28" /></td>
                  <td className="py-3.5 px-4"><div className="h-4 bg-slate-800 rounded w-24" /></td>
                  <td className="py-3.5 px-4"><div className="h-5 bg-slate-800 rounded w-16" /></td>
                  <td className="py-3.5 px-4"><div className="h-4 bg-slate-800 rounded w-48" /></td>
                  <td className="py-3.5 px-4 text-right"><div className="h-4 bg-slate-800 rounded w-20 ml-auto" /></td>
                  <td className="py-3.5 px-4 text-right"><div className="h-4 bg-slate-800 rounded w-20 ml-auto" /></td>
                </tr>
              ))
            ) : transactions.length === 0 ? (
              <tr>
                <td colSpan={6} className="py-12 text-center">
                  <div className="max-w-sm mx-auto space-y-3">
                    <div className="w-12 h-12 rounded-2xl bg-slate-800/70 border border-slate-700/60 flex items-center justify-center mx-auto text-slate-500">
                      <ShieldCheck className="w-6 h-6" />
                    </div>
                    <div>
                      <h4 className="text-sm font-semibold text-slate-300">No transactions recorded yet</h4>
                      <p className="text-xs text-slate-500 mt-1">
                        Make an initial credit or deposit to start recording immutable ledger entries.
                      </p>
                    </div>
                    <button
                      onClick={onOpenCredit}
                      className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white font-medium rounded-lg text-xs shadow transition"
                    >
                      Deposit Funds
                    </button>
                  </div>
                </td>
              </tr>
            ) : (
              transactions.map((tx) => {
                const isCredit = tx.type === 'credit';
                const parsedAmount = parseFloat(tx.amount);
                const parsedBalanceAfter = parseFloat(tx.balance_after);

                return (
                  <tr
                    key={tx.id}
                    className="hover:bg-slate-800/40 transition-colors group"
                  >
                    {/* Timestamp */}
                    <td className="py-3.5 px-4 font-mono text-slate-300 whitespace-nowrap">
                      {formatDate(tx.created_at)}
                    </td>

                    {/* Reference ID */}
                    <td className="py-3.5 px-4 whitespace-nowrap">
                      <span className="px-2 py-0.5 rounded font-mono text-[11px] bg-slate-800 text-slate-300 border border-slate-700/60">
                        {tx.reference_id}
                      </span>
                    </td>

                    {/* Type Badge */}
                    <td className="py-3.5 px-4 whitespace-nowrap">
                      <span
                        className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[11px] font-semibold ${
                          isCredit
                            ? 'bg-emerald-950/80 text-emerald-400 border border-emerald-500/30'
                            : 'bg-rose-950/80 text-rose-400 border border-rose-500/30'
                        }`}
                      >
                        {isCredit ? (
                          <ArrowDownLeft className="w-3 h-3" />
                        ) : (
                          <ArrowUpRight className="w-3 h-3" />
                        )}
                        {isCredit ? 'Credit' : 'Debit'}
                      </span>
                    </td>

                    {/* Description */}
                    <td className="py-3.5 px-4 text-slate-200 max-w-xs truncate">
                      {tx.description}
                    </td>

                    {/* Amount */}
                    <td className="py-3.5 px-4 text-right font-mono font-bold whitespace-nowrap">
                      <span
                        className={isCredit ? 'text-emerald-400' : 'text-rose-400'}
                      >
                        {isCredit ? '+' : '-'}$
                        {parsedAmount.toLocaleString('en-US', {
                          minimumFractionDigits: 2,
                          maximumFractionDigits: 2,
                        })}
                      </span>
                    </td>

                    {/* Resulting Balance */}
                    <td className="py-3.5 px-4 text-right font-mono text-white whitespace-nowrap">
                      $
                      {parsedBalanceAfter.toLocaleString('en-US', {
                        minimumFractionDigits: 2,
                        maximumFractionDigits: 2,
                      })}
                    </td>
                  </tr>
                );
              })
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};
