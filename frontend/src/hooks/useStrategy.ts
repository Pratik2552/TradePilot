// ============================================================
// useStrategy Hook
// Golden Cross Research Platform
// ============================================================

"use client";

import { useState, useEffect } from "react";
import type { Strategy, StrategyListItem } from "@/types";
import { fetchStrategies, fetchStrategy } from "@/services/api/strategies.api";

interface UseStrategyListReturn {
  strategies: StrategyListItem[];
  isLoading: boolean;
  error: Error | null;
  refetch: () => void;
}

interface UseStrategyReturn {
  strategy: Strategy | null;
  isLoading: boolean;
  error: Error | null;
  refetch: () => void;
}

export function useStrategyList(): UseStrategyListReturn {
  const [strategies, setStrategies] = useState<StrategyListItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);
  const [tick, setTick] = useState(0);

  useEffect(() => {
    let cancelled = false;
    setIsLoading(true);
    setError(null);

    fetchStrategies()
      .then((data) => {
        if (!cancelled) setStrategies(data);
      })
      .catch((err: Error) => {
        if (!cancelled) setError(err);
      })
      .finally(() => {
        if (!cancelled) setIsLoading(false);
      });

    return () => { cancelled = true; };
  }, [tick]);

  return { strategies, isLoading, error, refetch: () => setTick((t) => t + 1) };
}

export function useStrategy(id: string): UseStrategyReturn {
  const [strategy, setStrategy] = useState<Strategy | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);
  const [tick, setTick] = useState(0);

  useEffect(() => {
    if (!id) return;
    let cancelled = false;
    setIsLoading(true);
    setError(null);

    fetchStrategy(id)
      .then((data) => {
        if (!cancelled) setStrategy(data);
      })
      .catch((err: Error) => {
        console.error(`[useStrategy] id=${id}`, err);
        if (!cancelled) setError(err);
      })
      .finally(() => {
        if (!cancelled) setIsLoading(false);
      });

    return () => { cancelled = true; };
  }, [id, tick]);

  return { strategy, isLoading, error, refetch: () => setTick((t) => t + 1) };
}
