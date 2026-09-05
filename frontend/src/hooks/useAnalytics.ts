"use client";

import { useState, useEffect } from "react";
import type { AnalyticsSnapshot } from "@/types";
import { fetchAnalytics } from "@/services/api/analytics.api";

interface UseAnalyticsReturn {
  analytics: AnalyticsSnapshot | null;
  isLoading: boolean;
  error: Error | null;
  refetch: () => void;
}

export function useAnalytics(strategyId: string): UseAnalyticsReturn {
  const [analytics, setAnalytics] = useState<AnalyticsSnapshot | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);
  const [tick, setTick] = useState(0);

  useEffect(() => {
    if (!strategyId) return;
    let cancelled = false;
    setIsLoading(true);
    setError(null);

    fetchAnalytics(strategyId)
      .then((data) => { if (!cancelled) setAnalytics(data); })
      .catch((err: Error) => {
        console.error(`[useAnalytics] strategyId=${strategyId}`, err);
        if (!cancelled) setError(err);
      })
      .finally(() => { if (!cancelled) setIsLoading(false); });

    return () => { cancelled = true; };
  }, [strategyId, tick]);

  return { analytics, isLoading, error, refetch: () => setTick((t) => t + 1) };
}
