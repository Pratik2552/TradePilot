import apiClient from "./client";
import type { AnalyticsSnapshot } from "@/types";
import type { ApiResponse } from "@/types";

export async function fetchAnalytics(strategyId: string): Promise<AnalyticsSnapshot> {
  const res = await apiClient.get<ApiResponse<AnalyticsSnapshot>>(
    `/strategies/${strategyId}/analytics`
  );
  return res.data.data;
}
