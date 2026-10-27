import {
  Account,
  Transaction,
  PaginatedResponse,
  TransferRequest,
  TransferResponse,
  ErrorResponsePayload,
} from '../types';

const BASE_URL = import.meta.env.VITE_API_URL || '/api/v1';

export class ApiClientError extends Error {
  code: string;
  details?: unknown;
  status: number;

  constructor(status: number, code: string, message: string, details?: unknown) {
    super(message);
    this.name = 'ApiClientError';
    this.status = status;
    this.code = code;
    this.details = details;
  }
}

async function request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const url = `${BASE_URL}${endpoint}`;
  const headers = {
    'Content-Type': 'application/json',
    ...(options.headers || {}),
  };

  const response = await fetch(url, {
    ...options,
    headers,
  });

  if (!response.ok) {
    let errorCode = 'REQUEST_FAILED';
    let errorMessage = `Request failed with status ${response.status}`;
    let errorDetails: unknown = null;

    try {
      const errData = (await response.json()) as ErrorResponsePayload;
      if (errData?.error) {
        errorCode = errData.error.code || errorCode;
        errorMessage = errData.error.message || errorMessage;
        errorDetails = errData.error.details || null;
      }
    } catch {
      // Body wasn't JSON
    }

    throw new ApiClientError(response.status, errorCode, errorMessage, errorDetails);
  }

  return response.json() as Promise<T>;
}

export const api = {
  // Accounts
  async getAccounts(): Promise<Account[]> {
    return request<Account[]>('/accounts');
  },

  async getAccount(accountId: string): Promise<Account> {
    return request<Account>(`/accounts/${accountId}`);
  },

  async createAccount(name: string): Promise<Account> {
    return request<Account>('/accounts', {
      method: 'POST',
      body: JSON.stringify({ name }),
    });
  },

  // Transactions
  async getTransactions(
    accountId: string,
    page: number = 1,
    limit: number = 10
  ): Promise<PaginatedResponse<Transaction>> {
    return request<PaginatedResponse<Transaction>>(
      `/accounts/${accountId}/transactions?page=${page}&limit=${limit}`
    );
  },

  async createTransaction(
    accountId: string,
    data: {
      type: 'credit' | 'debit';
      amount: string;
      description: string;
      reference_id: string;
    }
  ): Promise<Transaction> {
    return request<Transaction>(`/accounts/${accountId}/transactions`, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  // Transfers
  async createTransfer(data: TransferRequest): Promise<TransferResponse> {
    return request<TransferResponse>('/transfers', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },
};
