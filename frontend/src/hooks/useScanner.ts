"use client";

import { useState, useEffect, useCallback } from "react";
import type { ScanResult, ScannerFilters, ScannerSummary } from "@/types";
import type { PaginatedResponse } from "@/types";
import {
  fetchScanResults,
  fetchScannerSummary,
  toggleWatchlist,
} from "@/services/api/scanner.api";

interface UseScannerReturn {
  results: ScanResult[];
  pagination: Omit<PaginatedResponse<ScanResult>, "data">;
  summary: ScannerSummary | null;
  isLoading: boolean;
  error: Error | null;
  filters: ScannerFilters;
  setFilters: (filters: ScannerFilters) => void;
  toggleWatchlistItem: (symbol: string) => Promise<void>;
  refetch: () => void;
}

export function useScanner(strategyId: string): UseScannerReturn {
  const [results, setResults] = useState<ScanResult[]>([]);
  const [summary, setSummary] = useState<ScannerSummary | null>(null);
  const [filters, setFilters] = useState<ScannerFilters>({});
  const [page] = useState(1);
  const [pageSize] = useState(50);
  const [pagination, setPagination] = useState<Omit<PaginatedResponse<ScanResult>, "data">>({
    total: 0,
    page: 1,
    pageSize: 50,
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

    Promise.all([
      fetchScanResults(strategyId, filters, page, pageSize),
      fetchScannerSummary(strategyId),
    ])
      .then(([{ data, ...meta }, summaryData]) => {
        if (!cancelled) {
          setResults(data);
          setPagination(meta);
          setSummary(summaryData);
        }
      })
      .catch((err: Error) => {
        console.error(`[useScanner] strategyId=${strategyId}`, err);
        if (!cancelled) setError(err);
      })
      .finally(() => { if (!cancelled) setIsLoading(false); });

    return () => { cancelled = true; };
  }, [strategyId, filters, page, pageSize, tick]);

  const toggleWatchlistItem = useCallback(
    async (symbol: string) => {
      await toggleWatchlist(strategyId, symbol);
      setResults((prev) =>
        prev.map((r) =>
          r.symbol === symbol ? { ...r, isWatchlisted: !r.isWatchlisted } : r
        )
      );
    },
    [strategyId]
  );

  return {
    results,
    pagination,
    summary,
    isLoading,
    error,
    filters,
    setFilters,
    toggleWatchlistItem,
    refetch: () => setTick((t) => t + 1),
  };
}
