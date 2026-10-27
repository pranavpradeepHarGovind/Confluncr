export interface Account {
  id: string;
  name: string;
  balance: string; // Decimal string e.g. "100.00"
  created_at: string;
  updated_at: string;
}

export type TransactionType = 'credit' | 'debit';

export interface Transaction {
  id: string;
  account_id: string;
  type: TransactionType;
  amount: string; // Decimal string e.g. "50.00"
  description: string;
  reference_id: string;
  balance_after: string; // Decimal string e.g. "150.00"
  created_at: string;
}

export interface PaginationMeta {
  current_page: number;
  limit: number;
  total_records: number;
  total_pages: number;
}

export interface PaginatedResponse<T> {
  items: T[];
  pagination: PaginationMeta;
}

export interface TransferRequest {
  source_account_id: string;
  destination_account_id: string;
  amount: string;
  description: string;
  reference_id: string;
}

export interface TransferResponse {
  transfer_reference: string;
  source_transaction: Transaction;
  destination_transaction: Transaction;
  amount: string;
  timestamp: string;
}

export interface ApiError {
  code: string;
  message: string;
  details?: unknown;
}

export interface ErrorResponsePayload {
  error: ApiError;
}
