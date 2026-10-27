import React, { useState, useEffect } from 'react';
import { Account, TransactionType } from '../types';
import { X, ArrowDownLeft, ArrowUpRight, AlertCircle, Sparkles } from 'lucide-react';

interface TransactionFormModalProps {
  isOpen: boolean;
  initialType?: TransactionType;
  account: Account;
  onClose: () => void;
  onSubmit: (data: {
    type: TransactionType;
    amount: string;
    description: string;
    reference_id: string;
  }) => Promise<void>;
}

export const TransactionFormModal: React.FC<TransactionFormModalProps> = ({
  isOpen,
  initialType = 'credit',
  account,
  onClose,
  onSubmit,
}) => {
  const [type, setType] = useState<TransactionType>(initialType);
  const [amount, setAmount] = useState('');
  const [description, setDescription] = useState('');
  const [referenceId, setReferenceId] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Generate a random default reference ID whenever opened
  const generateNewReference = () => {
    const timestamp = Date.now().toString().slice(-6);
    const random = Math.floor(Math.random() * 900 + 100);
    return `REF-${timestamp}-${random}`;
  };

  useEffect(() => {
    if (isOpen) {
      setType(initialType);
      setAmount('');
      setDescription(initialType === 'credit' ? 'Deposit' : 'Withdrawal');
      setReferenceId(generateNewReference());
      setError(null);
    }
  }, [isOpen, initialType]);

  if (!isOpen) return null;

  const currentBalance = parseFloat(account.balance);
  const parsedAmount = parseFloat(amount) || 0;
  const isDebit = type === 'debit';
  const newBalance = isDebit ? currentBalance - parsedAmount : currentBalance + parsedAmount;
  const isOverdraft = isDebit && parsedAmount > currentBalance;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (parsedAmount <= 0) {
      setError('Amount must be greater than zero.');
      return;
    }

    if (isOverdraft) {
      setError(
        `Insufficient balance. Cannot debit $${parsedAmount.toFixed(
          2
        )} from current balance of $${currentBalance.toFixed(2)}.`
      );
      return;
    }

    if (!description.trim()) {
      setError('Description is required.');
      return;
    }

    if (!referenceId.trim()) {
      setError('Reference ID is required.');
      return;
    }

    try {
      setIsSubmitting(true);
      setError(null);
      await onSubmit({
        type,
        amount: parsedAmount.toFixed(2),
        description: description.trim(),
        reference_id: referenceId.trim(),
      });
      onClose();
    } catch (err: unknown) {
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError('Transaction failed.');
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm animate-fade-in">
      <div className="bg-[#111827] border border-slate-700/80 rounded-2xl w-full max-w-md shadow-2xl overflow-hidden">
        {/* Header */}
        <div className="px-6 py-5 border-b border-slate-800 flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <div
              className={`p-2 rounded-lg ${
                isDebit ? 'bg-rose-500/10 text-rose-400' : 'bg-emerald-500/10 text-emerald-400'
              }`}
            >
              {isDebit ? <ArrowUpRight className="w-5 h-5" /> : <ArrowDownLeft className="w-5 h-5" />}
            </div>
            <div>
              <h3 className="text-base font-semibold text-white">
                {isDebit ? 'Debit / Withdraw Funds' : 'Credit / Deposit Funds'}
              </h3>
              <p className="text-xs text-slate-400">Account: {account.name}</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          {error && (
            <div className="p-3 rounded-lg bg-rose-950/60 border border-rose-500/30 flex items-start gap-2.5 text-xs text-rose-200">
              <AlertCircle className="w-4 h-4 text-rose-400 shrink-0 mt-0.5" />
              <span>{error}</span>
            </div>
          )}

          {/* Type Toggle */}
          <div className="grid grid-cols-2 gap-2 p-1 bg-slate-900 rounded-xl border border-slate-800">
            <button
              type="button"
              onClick={() => setType('credit')}
              className={`py-2 text-xs font-semibold rounded-lg flex items-center justify-center gap-1.5 transition ${
                !isDebit
                  ? 'bg-emerald-600 text-white shadow'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              <ArrowDownLeft className="w-3.5 h-3.5" />
              Credit (Deposit)
            </button>
            <button
              type="button"
              onClick={() => setType('debit')}
              className={`py-2 text-xs font-semibold rounded-lg flex items-center justify-center gap-1.5 transition ${
                isDebit
                  ? 'bg-rose-600 text-white shadow'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              <ArrowUpRight className="w-3.5 h-3.5" />
              Debit (Withdraw)
            </button>
          </div>

          {/* Amount Input */}
          <div>
            <label htmlFor="tx-amount" className="block text-xs font-medium text-slate-300 mb-1.5">
              Amount (USD) <span className="text-rose-400">*</span>
            </label>
            <div className="relative">
              <span className="absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400 font-mono text-sm">
                $
              </span>
              <input
                id="tx-amount"
                type="number"
                step="0.01"
                min="0.01"
                required
                value={amount}
                onChange={(e) => setAmount(e.target.value)}
                placeholder="0.00"
                className="w-full pl-8 pr-4 py-2.5 bg-slate-900 border border-slate-700 rounded-xl text-sm font-mono text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-indigo-500/50 focus:border-indigo-500 transition"
                autoFocus
              />
            </div>
          </div>

          {/* Real-time Balance Preview */}
          <div className="p-3 rounded-xl bg-slate-900/80 border border-slate-800 flex items-center justify-between text-xs">
            <span className="text-slate-400">Projected Balance:</span>
            <div className="text-right font-mono">
              <span className="text-slate-400 mr-2">
                ${currentBalance.toFixed(2)} {isDebit ? '-' : '+'} ${parsedAmount.toFixed(2)} =
              </span>
              <span
                className={`font-bold ${
                  isOverdraft
                    ? 'text-rose-400'
                    : isDebit
                    ? 'text-slate-100'
                    : 'text-emerald-400'
                }`}
              >
                ${newBalance.toFixed(2)}
              </span>
            </div>
          </div>

          {/* Description */}
          <div>
            <label htmlFor="tx-desc" className="block text-xs font-medium text-slate-300 mb-1.5">
              Description <span className="text-rose-400">*</span>
            </label>
            <input
              id="tx-desc"
              type="text"
              required
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="e.g. Consulting Fee or Payroll"
              className="w-full px-3.5 py-2.5 bg-slate-900 border border-slate-700 rounded-xl text-sm text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-indigo-500/50 focus:border-indigo-500 transition"
            />
          </div>

          {/* Reference ID */}
          <div>
            <div className="flex items-center justify-between mb-1.5">
              <label htmlFor="tx-ref" className="block text-xs font-medium text-slate-300">
                Reference ID (Idempotency Key) <span className="text-rose-400">*</span>
              </label>
              <button
                type="button"
                onClick={() => setReferenceId(generateNewReference())}
                className="text-[11px] text-indigo-400 hover:text-indigo-300 flex items-center gap-1"
              >
                <Sparkles className="w-3 h-3" />
                Regenerate
              </button>
            </div>
            <input
              id="tx-ref"
              type="text"
              required
              value={referenceId}
              onChange={(e) => setReferenceId(e.target.value)}
              placeholder="Unique identifier per account"
              className="w-full px-3.5 py-2.5 bg-slate-900 border border-slate-700 rounded-xl text-xs font-mono text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-indigo-500/50 focus:border-indigo-500 transition"
            />
            <p className="text-[10px] text-slate-500 mt-1">
              Enforced unique per account at database level to prevent duplicate processing.
            </p>
          </div>

          {/* Actions */}
          <div className="pt-2 flex items-center justify-end gap-3">
            <button
              type="button"
              onClick={onClose}
              disabled={isSubmitting}
              className="px-4 py-2 text-xs font-medium text-slate-400 hover:text-white hover:bg-slate-800/60 rounded-lg transition"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isSubmitting || isOverdraft}
              className={`px-5 py-2 text-white text-xs font-semibold rounded-lg shadow-md transition disabled:opacity-50 flex items-center gap-1.5 ${
                isDebit
                  ? 'bg-rose-600 hover:bg-rose-500 shadow-rose-600/30'
                  : 'bg-emerald-600 hover:bg-emerald-500 shadow-emerald-600/30'
              }`}
            >
              {isSubmitting ? 'Processing...' : isDebit ? 'Confirm Debit' : 'Confirm Credit'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
