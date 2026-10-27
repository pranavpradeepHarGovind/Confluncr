import React from 'react';
import { PaginationMeta } from '../types';
import { ChevronLeft, ChevronRight } from 'lucide-react';

interface PaginationProps {
  pagination: PaginationMeta;
  onPageChange: (newPage: number) => void;
  onLimitChange: (newLimit: number) => void;
}

export const Pagination: React.FC<PaginationProps> = ({
  pagination,
  onPageChange,
  onLimitChange,
}) => {
  const { current_page, limit, total_records, total_pages } = pagination;

  const startRecord = total_records === 0 ? 0 : (current_page - 1) * limit + 1;
  const endRecord = Math.min(current_page * limit, total_records);

  return (
    <div className="flex flex-col sm:flex-row items-center justify-between gap-4 py-3 px-4 border-t border-slate-800 text-xs text-slate-400">
      {/* Records count & limit selector */}
      <div className="flex items-center gap-3">
        <span>
          Showing <strong className="text-white font-medium">{startRecord}</strong> to{' '}
          <strong className="text-white font-medium">{endRecord}</strong> of{' '}
          <strong className="text-white font-medium">{total_records}</strong> transactions
        </span>

        <div className="flex items-center gap-1.5 ml-2">
          <label htmlFor="limit-select" className="text-slate-500 text-[11px]">
            Rows:
          </label>
          <select
            id="limit-select"
            value={limit}
            onChange={(e) => onLimitChange(Number(e.target.value))}
            className="bg-slate-900 border border-slate-700/80 rounded px-2 py-1 text-slate-300 text-xs focus:outline-none focus:ring-1 focus:ring-indigo-500"
          >
            <option value="5">5</option>
            <option value="10">10</option>
            <option value="20">20</option>
            <option value="50">50</option>
          </select>
        </div>
      </div>

      {/* Page controls */}
      <div className="flex items-center gap-2">
        <span className="text-slate-400">
          Page <strong className="text-white font-medium">{current_page}</strong> of{' '}
          <strong className="text-white font-medium">{total_pages || 1}</strong>
        </span>

        <div className="flex items-center gap-1">
          <button
            onClick={() => onPageChange(current_page - 1)}
            disabled={current_page <= 1}
            className="p-1.5 rounded-lg border border-slate-800 bg-slate-900 text-slate-300 hover:text-white hover:bg-slate-800 disabled:opacity-40 disabled:cursor-not-allowed transition"
            title="Previous page"
          >
            <ChevronLeft className="w-4 h-4" />
          </button>
          <button
            onClick={() => onPageChange(current_page + 1)}
            disabled={current_page >= total_pages || total_pages === 0}
            className="p-1.5 rounded-lg border border-slate-800 bg-slate-900 text-slate-300 hover:text-white hover:bg-slate-800 disabled:opacity-40 disabled:cursor-not-allowed transition"
            title="Next page"
          >
            <ChevronRight className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  );
};
