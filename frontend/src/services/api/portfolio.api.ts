import apiClient from "./client";
import type { PortfolioSnapshot } from "@/types";
import type { ApiResponse } from "@/types";

export async function fetchPortfolio(strategyId: string): Promise<PortfolioSnapshot> {
  const res = await apiClient.get<ApiResponse<PortfolioSnapshot>>(
    `/strategies/${strategyId}/portfolio`
  );
  return res.data.data;
}
