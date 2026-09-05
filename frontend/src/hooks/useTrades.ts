"use client";

import { useState, useEffect } from "react";
import type { Trade, TradeFilters, TradeSummary } from "@/types";
import type { PaginatedResponse, QueryConfig } from "@/types";
import { fetchTrades, fetchTradeSummary, exportTrades } from "@/services/api/trades.api";

interface UseTradesReturn {
  trades: Trade[];
  pagination: Omit<PaginatedResponse<Trade>, "data">;
  isLoading: boolean;
  error: Error | null;
  setFilters: (filters: TradeFilters) => void;
  setQuery: (query: QueryConfig) => void;
  refetch: () => void;
}

interface UseTradeSummaryReturn {
  summary: TradeSummary | null;
  isLoading: boolean;
  error: Error | null;
}

export function useTrades(strategyId: string): UseTradesReturn {
  const [trades, setTrades] = useState<Trade[]>([]);
  const [filters, setFilters] = useState<TradeFilters>({});
  const [query, setQuery] = useState<QueryConfig>({
    pagination: { page: 1, pageSize: 20 },
    sort: { field: "entryDate", direction: "desc" },
  });
  const [pagination, setPagination] = useState<Omit<PaginatedResponse<Trade>, "data">>({
    total: 0,
    page: 1,
    pageSize: 20,
    totalPages: 0,
    hasMore: false,
  });
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);
  const [tick, setTick] = useState(0);

  useEffect(() => {
    if (!strategyId) return;
    let cancelled = false;
    setIsLoading(true);
    setError(null);

    fetchTrades(strategyId, filters, query)
      .then(({ data, ...meta }) => {
        if (!cancelled) {
          setTrades(data);
          setPagination(meta);
        }
      })
      .catch((err: Error) => {
        console.error(`[useTrades] strategyId=${strategyId}`, err);
        if (!cancelled) setError(err);
      })
      .finally(() => {
        if (!cancelled) setIsLoading(false);
      });

    return () => { cancelled = true; };
  }, [strategyId, filters, query, tick]);

  return {
    trades,
    pagination,
    isLoading,
    error,
    setFilters,
    setQuery,
    refetch: () => setTick((t) => t + 1),
  };
}

export function useTradeSummary(strategyId: string): UseTradeSummaryReturn {
  const [summary, setSummary] = useState<TradeSummary | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    if (!strategyId) return;
    let cancelled = false;
    setIsLoading(true);

    fetchTradeSummary(strategyId)
      .then((data) => { if (!cancelled) setSummary(data); })
      .catch((err: Error) => { if (!cancelled) setError(err); })
      .finally(() => { if (!cancelled) setIsLoading(false); });

    return () => { cancelled = true; };
  }, [strategyId]);

  return { summary, isLoading, error };
}

export function useExportTrades(strategyId: string) {
  const [isExporting, setIsExporting] = useState(false);

  const exportCsv = async () => {
    setIsExporting(true);
    try {
      const blob = await exportTrades(strategyId);
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `trades-${strategyId}-${new Date().toISOString().split("T")[0]}.csv`;
      a.click();
      URL.revokeObjectURL(url);
    } finally {
      setIsExporting(false);
    }
  };

  return { exportCsv, isExporting };
}
