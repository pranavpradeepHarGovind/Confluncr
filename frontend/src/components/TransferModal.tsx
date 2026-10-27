import React, { useState, useEffect } from 'react';
import { Account, TransferRequest } from '../types';
import { X, ArrowLeftRight, AlertCircle, Sparkles, ShieldAlert } from 'lucide-react';

interface TransferModalProps {
  isOpen: boolean;
  accounts: Account[];
  sourceAccount: Account;
  onClose: () => void;
  onSubmit: (data: TransferRequest) => Promise<void>;
}

export const TransferModal: React.FC<TransferModalProps> = ({
  isOpen,
  accounts,
  sourceAccount,
  onClose,
  onSubmit,
}) => {
  const [destinationAccountId, setDestinationAccountId] = useState('');
  const [amount, setAmount] = useState('');
  const [description, setDescription] = useState('Account-to-Account Transfer');
  const [referenceId, setReferenceId] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Available destination accounts (excluding source)
  const availableDestinations = accounts.filter((acc) => acc.id !== sourceAccount.id);

  const generateNewReference = () => {
    const timestamp = Date.now().toString().slice(-6);
    const random = Math.floor(Math.random() * 900 + 100);
    return `TRF-${timestamp}-${random}`;
  };

  useEffect(() => {
    if (isOpen) {
      setDestinationAccountId(availableDestinations[0]?.id || '');
      setAmount('');
      setDescription('Account-to-Account Transfer');
      setReferenceId(generateNewReference());
      setError(null);
    }
  }, [isOpen, sourceAccount.id]);

  if (!isOpen) return null;

  const currentBalance = parseFloat(sourceAccount.balance);
  const parsedAmount = parseFloat(amount) || 0;
  const isOverdraft = parsedAmount > currentBalance;
  const targetAccount = accounts.find((acc) => acc.id === destinationAccountId);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!destinationAccountId) {
      setError('Please select a destination account.');
      return;
    }

    if (destinationAccountId === sourceAccount.id) {
      setError('Source and destination accounts must be different.');
      return;
    }

    if (parsedAmount <= 0) {
      setError('Transfer amount must be greater than zero.');
      return;
    }

    if (isOverdraft) {
      setError(
        `Insufficient balance. Cannot transfer $${parsedAmount.toFixed(
          2
        )} from source balance of $${currentBalance.toFixed(2)}.`
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
        source_account_id: sourceAccount.id,
        destination_account_id: destinationAccountId,
        amount: parsedAmount.toFixed(2),
        description: description.trim(),
        reference_id: referenceId.trim(),
      });
      onClose();
    } catch (err: unknown) {
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError('Transfer failed.');
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm animate-fade-in">
      <div className="bg-[#111827] border border-slate-700/80 rounded-2xl w-full max-w-lg shadow-2xl overflow-hidden">
        {/* Header */}
        <div className="px-6 py-5 border-b border-slate-800 flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <div className="p-2 rounded-lg bg-indigo-500/10 text-indigo-400">
              <ArrowLeftRight className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-base font-semibold text-white">Atomic Funds Transfer</h3>
              <p className="text-xs text-slate-400">
                Deterministic row locking & rollback protection
              </p>
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

          {/* Account Route Flow Visualizer */}
          <div className="p-3.5 rounded-xl bg-slate-900/90 border border-slate-800 grid grid-cols-2 gap-3 relative">
            <div>
              <span className="text-[10px] font-semibold uppercase text-slate-400 block mb-1">
                From (Source)
              </span>
              <p className="text-xs font-bold text-white truncate">{sourceAccount.name}</p>
              <p className="text-[11px] font-mono text-slate-400 mt-0.5">
                Balance: ${currentBalance.toFixed(2)}
              </p>
            </div>

            <div className="border-l border-slate-800 pl-3">
              <span className="text-[10px] font-semibold uppercase text-slate-400 block mb-1">
                To (Destination)
              </span>
              {availableDestinations.length === 0 ? (
                <p className="text-xs text-amber-400">No other accounts available</p>
              ) : (
                <>
                  <p className="text-xs font-bold text-indigo-300 truncate">
                    {targetAccount?.name || 'Select below'}
                  </p>
                  <p className="text-[11px] font-mono text-slate-400 mt-0.5">
                    Balance: ${targetAccount ? parseFloat(targetAccount.balance).toFixed(2) : '0.00'}
                  </p>
                </>
              )}
            </div>
          </div>

          {/* Destination Account Dropdown */}
          <div>
            <label htmlFor="dest-account" className="block text-xs font-medium text-slate-300 mb-1.5">
              Select Destination Account <span className="text-rose-400">*</span>
            </label>
            <select
              id="dest-account"
              value={destinationAccountId}
              onChange={(e) => setDestinationAccountId(e.target.value)}
              disabled={availableDestinations.length === 0}
              className="w-full px-3.5 py-2.5 bg-slate-900 border border-slate-700 rounded-xl text-sm text-white focus:outline-none focus:ring-2 focus:ring-indigo-500/50 focus:border-indigo-500 transition"
            >
              {availableDestinations.length === 0 ? (
                <option value="">No other account available. Create one first.</option>
              ) : (
                availableDestinations.map((acc) => (
                  <option key={acc.id} value={acc.id}>
                    {acc.name} (${parseFloat(acc.balance).toFixed(2)}) — {acc.id.slice(0, 8)}...
                  </option>
                ))
              )}
            </select>
          </div>

          {/* Amount */}
          <div>
            <label htmlFor="transfer-amount" className="block text-xs font-medium text-slate-300 mb-1.5">
              Transfer Amount (USD) <span className="text-rose-400">*</span>
            </label>
            <div className="relative">
              <span className="absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400 font-mono text-sm">
                $
              </span>
              <input
                id="transfer-amount"
                type="number"
                step="0.01"
                min="0.01"
                required
                value={amount}
                onChange={(e) => setAmount(e.target.value)}
                placeholder="0.00"
                className="w-full pl-8 pr-4 py-2.5 bg-slate-900 border border-slate-700 rounded-xl text-sm font-mono text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-indigo-500/50 focus:border-indigo-500 transition"
              />
            </div>
          </div>

          {/* Description */}
          <div>
            <label htmlFor="transfer-desc" className="block text-xs font-medium text-slate-300 mb-1.5">
              Description <span className="text-rose-400">*</span>
            </label>
            <input
              id="transfer-desc"
              type="text"
              required
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="e.g. Invoice payment or Split rent"
              className="w-full px-3.5 py-2.5 bg-slate-900 border border-slate-700 rounded-xl text-sm text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-indigo-500/50 focus:border-indigo-500 transition"
            />
          </div>

          {/* Reference ID */}
          <div>
            <div className="flex items-center justify-between mb-1.5">
              <label htmlFor="transfer-ref" className="block text-xs font-medium text-slate-300">
                Transfer Reference <span className="text-rose-400">*</span>
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
              id="transfer-ref"
              type="text"
              required
              value={referenceId}
              onChange={(e) => setReferenceId(e.target.value)}
              placeholder="Unique transfer reference"
              className="w-full px-3.5 py-2.5 bg-slate-900 border border-slate-700 rounded-xl text-xs font-mono text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-indigo-500/50 focus:border-indigo-500 transition"
            />
          </div>

          {/* Concurrency & Atomicity Guarantee Banner */}
          <div className="p-3 rounded-xl bg-indigo-950/30 border border-indigo-500/20 text-xs text-indigo-300 flex items-start gap-2.5">
            <ShieldAlert className="w-4 h-4 text-indigo-400 shrink-0 mt-0.5" />
            <div>
              <span className="font-semibold text-white">Deadlock & Race Condition Protected:</span>
              <p className="mt-0.5 text-[11px] text-indigo-200/80">
                Both accounts are locked deterministically using PostgreSQL <code className="text-indigo-300">FOR UPDATE</code>. If any check fails, the transaction is completely rolled back with zero balance changes.
              </p>
            </div>
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
              disabled={isSubmitting || isOverdraft || availableDestinations.length === 0}
              className="px-5 py-2 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white text-xs font-semibold rounded-lg shadow-md shadow-indigo-600/30 transition flex items-center gap-1.5"
            >
              {isSubmitting ? 'Transferring...' : 'Execute Transfer'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
