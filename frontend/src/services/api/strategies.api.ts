import apiClient from "./client";
import type { Strategy, StrategyListItem, StrategyConfig } from "@/types";
import type { ApiResponse } from "@/types";

export async function fetchStrategies(): Promise<StrategyListItem[]> {
  const res = await apiClient.get<ApiResponse<StrategyListItem[]>>("/strategies");
  return res.data.data;
}

export async function fetchStrategy(id: string): Promise<Strategy> {
  const res = await apiClient.get<ApiResponse<Strategy>>(`/strategies/${id}`);
  return res.data.data;
}

export async function updateStrategyConfig(
  id: string,
  config: Partial<StrategyConfig>
): Promise<Strategy> {
  const res = await apiClient.patch<ApiResponse<Strategy>>(
    `/strategies/${id}/config`,
    config
  );
  return res.data.data;
}
