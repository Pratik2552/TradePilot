import apiClient from "./client";
import type { Trade, TradeFilters, TradeSummary } from "@/types";
import type { ApiResponse, PaginatedResponse, QueryConfig } from "@/types";

export async function fetchTrades(
  strategyId: string,
  filters?: TradeFilters,
  query?: QueryConfig
): Promise<PaginatedResponse<Trade>> {
  const params: Record<string, unknown> = {
    page: query?.pagination?.page ?? 1,
    pageSize: query?.pagination?.pageSize ?? 20,
    sort: query?.sort?.field ?? "entryDate",
    dir: query?.sort?.direction ?? "desc",
  };
  if (filters?.status) params.status = filters.status;
  if (filters?.symbol) params.symbol = filters.symbol;
  if (filters?.exitReason) params.exitReason = filters.exitReason;
  if (filters?.dateFrom) params.dateFrom = filters.dateFrom;
  if (filters?.dateTo) params.dateTo = filters.dateTo;

  const res = await apiClient.get<ApiResponse<PaginatedResponse<Trade>>>(
    `/strategies/${strategyId}/trades`,
    { params }
  );
  return res.data.data;
}

export async function fetchTradeSummary(strategyId: string): Promise<TradeSummary> {
  const res = await apiClient.get<ApiResponse<TradeSummary>>(
    `/strategies/${strategyId}/trades/summary`
  );
  return res.data.data;
}

export async function exportTrades(strategyId: string): Promise<Blob> {
  const res = await apiClient.get(`/strategies/${strategyId}/trades/export`, {
    responseType: "blob",
  });
  return res.data;
}
