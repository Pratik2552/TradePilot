"use client";

import { useState, useEffect } from "react";
import type { PortfolioSnapshot } from "@/types";
import { fetchPortfolio } from "@/services/api/portfolio.api";

interface UsePortfolioReturn {
  portfolio: PortfolioSnapshot | null;
  isLoading: boolean;
  error: Error | null;
  refetch: () => void;
}

export function usePortfolio(strategyId: string): UsePortfolioReturn {
  const [portfolio, setPortfolio] = useState<PortfolioSnapshot | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);
  const [tick, setTick] = useState(0);

  useEffect(() => {
    if (!strategyId) return;
    let cancelled = false;
    setIsLoading(true);
    setError(null);

    fetchPortfolio(strategyId)
      .then((data) => { if (!cancelled) setPortfolio(data); })
      .catch((err: Error) => {
        console.error(`[usePortfolio] strategyId=${strategyId}`, err);
        if (!cancelled) setError(err);
      })
      .finally(() => { if (!cancelled) setIsLoading(false); });

    return () => { cancelled = true; };
  }, [strategyId, tick]);

  return { portfolio, isLoading, error, refetch: () => setTick((t) => t + 1) };
}
