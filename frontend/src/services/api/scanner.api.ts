import apiClient from "./client";
import type { ScanResult, ScannerFilters, ScannerSummary, WatchlistItem } from "@/types";
import type { ApiResponse, PaginatedResponse } from "@/types";

export async function fetchScanResults(
  strategyId: string,
  filters?: ScannerFilters,
  page = 1,
  pageSize = 50
): Promise<PaginatedResponse<ScanResult>> {
  const params: Record<string, unknown> = { page, pageSize };
  if (filters?.searchQuery) params.search = filters.searchQuery;
  if (filters?.signalStrength?.length) params.signalStrength = filters.signalStrength;
  if (filters?.isWatchlisted !== undefined) params.isWatchlisted = filters.isWatchlisted;

  const res = await apiClient.get<ApiResponse<PaginatedResponse<ScanResult>>>(
    `/strategies/${strategyId}/scanner`,
    { params }
  );
  return res.data.data;
}

export async function fetchScannerSummary(strategyId: string): Promise<ScannerSummary> {
  const res = await apiClient.get<ApiResponse<ScannerSummary>>(
    `/strategies/${strategyId}/scanner/summary`
  );
  return res.data.data;
}

export async function fetchWatchlist(strategyId: string): Promise<WatchlistItem[]> {
  const res = await apiClient.get<ApiResponse<WatchlistItem[]>>(
    `/strategies/${strategyId}/scanner/watchlist`
  );
  return res.data.data;
}

export async function toggleWatchlist(strategyId: string, symbol: string): Promise<boolean> {
  const res = await apiClient.post<ApiResponse<{ isWatchlisted: boolean }>>(
    `/strategies/${strategyId}/watchlist/${symbol}`
  );
  return res.data.data.isWatchlisted;
}
