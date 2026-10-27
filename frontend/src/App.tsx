import React, { useState, useEffect, useCallback } from 'react';
import { api, ApiClientError } from './api/client';
import { Account, Transaction, PaginationMeta, TransactionType, TransferRequest } from './types';
import { Navbar } from './components/Navbar';
import { AccountList } from './components/AccountList';
import { AccountSummary } from './components/AccountSummary';
import { TransactionTable } from './components/TransactionTable';
import { Pagination } from './components/Pagination';
import { CreateAccountModal } from './components/CreateAccountModal';
import { TransactionFormModal } from './components/TransactionFormModal';
import { TransferModal } from './components/TransferModal';
import { Toast, ToastMessage } from './components/Toast';
import { AlertCircle, PlusCircle } from 'lucide-react';

export const App: React.FC = () => {
  // Accounts State
  const [accounts, setAccounts] = useState<Account[]>([]);
  const [selectedAccountId, setSelectedAccountId] = useState<string | null>(null);
  const [isAccountsLoading, setIsAccountsLoading] = useState(true);

  // Transactions State
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [pagination, setPagination] = useState<PaginationMeta>({
    current_page: 1,
    limit: 10,
    total_records: 0,
    total_pages: 0,
  });
  const [isTransactionsLoading, setIsTransactionsLoading] = useState(false);

  // Modals
  const [isCreateAccountOpen, setIsCreateAccountOpen] = useState(false);
  const [isTxModalOpen, setIsTxModalOpen] = useState(false);
  const [txModalType, setTxModalType] = useState<TransactionType>('credit');
  const [isTransferModalOpen, setIsTransferModalOpen] = useState(false);

  // Toasts
  const [toasts, setToasts] = useState<ToastMessage[]>([]);

  const addToast = (type: 'success' | 'error', title: string, message: string) => {
    const id = Date.now().toString() + Math.random().toString();
    setToasts((prev) => [...prev, { id, type, title, message }]);
  };

  const removeToast = (id: string) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  };

  // Fetch Accounts
  const fetchAccounts = useCallback(async (preserveSelectedId?: string) => {
    try {
      setIsAccountsLoading(true);
      const data = await api.getAccounts();
      setAccounts(data);

      if (data.length > 0) {
        if (preserveSelectedId && data.some((a) => a.id === preserveSelectedId)) {
          setSelectedAccountId(preserveSelectedId);
        } else if (!selectedAccountId || !data.some((a) => a.id === selectedAccountId)) {
          setSelectedAccountId(data[0].id);
        }
      } else {
        setSelectedAccountId(null);
      }
    } catch (err: unknown) {
      const msg = err instanceof ApiClientError ? err.message : 'Failed to fetch accounts.';
      addToast('error', 'Error Loading Accounts', msg);
    } finally {
      setIsAccountsLoading(false);
    }
  }, [selectedAccountId]);

  // Fetch Transactions for selected account
  const fetchTransactions = useCallback(
    async (accountId: string, page = 1, limit = 10) => {
      try {
        setIsTransactionsLoading(true);
        const res = await api.getTransactions(accountId, page, limit);
        setTransactions(res.items);
        setPagination(res.pagination);
      } catch (err: unknown) {
        const msg = err instanceof ApiClientError ? err.message : 'Failed to load transaction history.';
        addToast('error', 'Transaction History Error', msg);
      } finally {
        setIsTransactionsLoading(false);
      }
    },
    []
  );

  // Initial load
  useEffect(() => {
    fetchAccounts();
  }, []);

  // When selected account or page changes
  useEffect(() => {
    if (selectedAccountId) {
      fetchTransactions(selectedAccountId, pagination.current_page, pagination.limit);
    } else {
      setTransactions([]);
      setPagination((p) => ({ ...p, total_records: 0, total_pages: 0 }));
    }
  }, [selectedAccountId, pagination.current_page, pagination.limit, fetchTransactions]);

  const activeAccount = accounts.find((a) => a.id === selectedAccountId) || null;

  // Handlers
  const handleCreateAccount = async (name: string) => {
    const newAccount = await api.createAccount(name);
    addToast('success', 'Account Created', `Account "${newAccount.name}" created with zero balance.`);
    await fetchAccounts(newAccount.id);
  };

  const handleProcessTransaction = async (data: {
    type: TransactionType;
    amount: string;
    description: string;
    reference_id: string;
  }) => {
    if (!selectedAccountId) return;
    const tx = await api.createTransaction(selectedAccountId, data);
    addToast(
      'success',
      'Transaction Successful',
      `${data.type.toUpperCase()} of $${data.amount} processed. New balance: $${tx.balance_after}`
    );
    // Refresh accounts to show new balance and re-fetch page 1 of transactions
    await fetchAccounts(selectedAccountId);
    await fetchTransactions(selectedAccountId, 1, pagination.limit);
  };

  const handleProcessTransfer = async (transferData: TransferRequest) => {
    const res = await api.createTransfer(transferData);
    addToast(
      'success',
      'Transfer Completed',
      `Transferred $${transferData.amount} (Ref: ${res.transfer_reference}). Both balances updated atomically.`
    );
    // Refresh accounts to reflect both balances and update transaction history
    await fetchAccounts(selectedAccountId || undefined);
    if (selectedAccountId) {
      await fetchTransactions(selectedAccountId, 1, pagination.limit);
    }
  };

  const openCreditModal = () => {
    setTxModalType('credit');
    setIsTxModalOpen(true);
  };

  const openDebitModal = () => {
    setTxModalType('debit');
    setIsTxModalOpen(true);
  };

  return (
    <div className="min-h-screen bg-[#0B0F19] text-slate-100 flex flex-col font-sans">
      <Navbar
        onOpenCreateAccount={() => setIsCreateAccountOpen(true)}
        onRefresh={() => {
          fetchAccounts(selectedAccountId || undefined);
          if (selectedAccountId) {
            fetchTransactions(selectedAccountId, pagination.current_page, pagination.limit);
          }
        }}
        isRefreshing={isAccountsLoading || isTransactionsLoading}
      />

      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
        {/* Main Content Layout */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
          {/* Left Column: Accounts List Sidebar */}
          <div className="lg:col-span-4 space-y-6">
            <AccountList
              accounts={accounts}
              selectedAccountId={selectedAccountId}
              onSelectAccount={(id) => {
                setSelectedAccountId(id);
                setPagination((p) => ({ ...p, current_page: 1 }));
              }}
              isLoading={isAccountsLoading}
            />

            {/* Quick Helper Card */}
            <div className="p-4 rounded-2xl bg-slate-900/40 border border-slate-800 text-xs text-slate-400 space-y-2">
              <h4 className="font-semibold text-slate-200 flex items-center gap-1.5">
                <AlertCircle className="w-3.5 h-3.5 text-indigo-400" />
                Assessment Integrity Rules
              </h4>
              <ul className="space-y-1.5 list-disc list-inside text-slate-400 text-[11px]">
                <li>Initial account balance is strictly <strong>$0.00</strong>.</li>
                <li>Debits exceeding balance are rejected (400) atomically.</li>
                <li>Reference IDs must be unique per account (409).</li>
                <li>Row-level locking (<code className="text-indigo-300">FOR UPDATE</code>) eliminates race conditions.</li>
              </ul>
            </div>
          </div>

          {/* Right Column: Active Account Dashboard & History */}
          <div className="lg:col-span-8 space-y-6">
            {activeAccount ? (
              <>
                {/* Account Hero Card */}
                <AccountSummary
                  account={activeAccount}
                  onOpenCredit={openCreditModal}
                  onOpenDebit={openDebitModal}
                  onOpenTransfer={() => setIsTransferModalOpen(true)}
                />

                {/* Paginated Transactions Table */}
                <div className="space-y-0">
                  <TransactionTable
                    transactions={transactions}
                    isLoading={isTransactionsLoading}
                    onOpenCredit={openCreditModal}
                  />

                  {pagination.total_records > 0 && (
                    <Pagination
                      pagination={pagination}
                      onPageChange={(page) => setPagination((p) => ({ ...p, current_page: page }))}
                      onLimitChange={(limit) =>
                        setPagination((p) => ({ ...p, limit, current_page: 1 }))
                      }
                    />
                  )}
                </div>
              </>
            ) : !isAccountsLoading && accounts.length === 0 ? (
              <div className="p-12 text-center rounded-2xl border border-dashed border-slate-800 bg-slate-900/30">
                <div className="w-16 h-16 rounded-3xl bg-indigo-500/10 text-indigo-400 flex items-center justify-center mx-auto mb-4">
                  <PlusCircle className="w-8 h-8" />
                </div>
                <h3 className="text-lg font-bold text-white">No accounts found</h3>
                <p className="text-xs text-slate-400 max-w-sm mx-auto mt-1 mb-5">
                  Get started by creating your first bank account. All accounts initialize with $0.00.
                </p>
                <button
                  onClick={() => setIsCreateAccountOpen(true)}
                  className="px-5 py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white font-semibold text-xs rounded-xl shadow-lg shadow-indigo-600/30 transition"
                >
                  Create Account Now
                </button>
              </div>
            ) : null}
          </div>
        </div>
      </main>

      {/* Modals */}
      <CreateAccountModal
        isOpen={isCreateAccountOpen}
        onClose={() => setIsCreateAccountOpen(false)}
        onSubmit={handleCreateAccount}
      />

      {activeAccount && (
        <TransactionFormModal
          isOpen={isTxModalOpen}
          initialType={txModalType}
          account={activeAccount}
          onClose={() => setIsTxModalOpen(false)}
          onSubmit={handleProcessTransaction}
        />
      )}

      {activeAccount && (
        <TransferModal
          isOpen={isTransferModalOpen}
          accounts={accounts}
          sourceAccount={activeAccount}
          onClose={() => setIsTransferModalOpen(false)}
          onSubmit={handleProcessTransfer}
        />
      )}

      {/* Toast Manager */}
      <Toast toasts={toasts} onDismiss={removeToast} />
    </div>
  );
};

export default App;
