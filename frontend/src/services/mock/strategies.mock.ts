// ============================================================
// Strategies Mock Data
// Golden Cross Research Platform
//
// Realistic mock data for Golden Cross EMA50/EMA200 strategy.
// ============================================================

import type { Strategy, StrategyListItem } from "@/types";

export const STRATEGY_MOCK: Record<string, Strategy> = {
  "golden-cross": {
    id: "golden-cross",
    name: "Golden Cross",
    description: "EMA50 crossing above EMA200 — trend-following momentum strategy on NSE FO stocks",
    longDescription:
      "The Golden Cross strategy identifies stocks where the 50-period Exponential Moving Average crosses above the 200-period EMA, signaling a shift from bearish to bullish momentum. Entry is confirmed with volume surge and ATR-based stop loss placement.",
    status: "active",
    category: "trend_following",
    stocks: 2386,
    lastScan: new Date(Date.now() - 3 * 60 * 60 * 1000).toISOString(), // 3h ago
    createdAt: "2024-01-15T08:00:00.000Z",
    tags: ["EMA", "Trend Following", "NSE FO", "Daily"],
    config: {
      initialCapital: 2_000_000, // ₹20L
      riskPerTrade: 2,
      maxPositions: 20,
      emaPeriodFast: 50,
      emaPeriodSlow: 200,
      stopLossPercent: 7,
      takeProfitPercent: 20,
      scanTimeframe: "1D",
      universe: "NSE_FO",
    },
    stats: {
      portfolioValue: 2_847_320,
      capitalDeployed: 1_624_800,
      openPositions: 11,
      closedTrades: 187,
      winRate: 64.7,
      profitFactor: 2.31,
      averageReturn: 8.4,
      averageHoldingDays: 23,
      totalReturn: 42.37,
      cagr: 28.6,
      sharpeRatio: 1.84,
      maxDrawdown: -14.2,
    },
  },
};

export const STRATEGIES_LIST_MOCK: StrategyListItem[] = [
  {
    id: "golden-cross",
    name: "Golden Cross",
    description: "EMA50 crossing above EMA200 — trend-following momentum strategy",
    status: "active",
    stocks: 2386,
    lastScan: new Date(Date.now() - 3 * 60 * 60 * 1000).toISOString(),
    tags: ["EMA", "Trend Following", "NSE FO", "Daily"],
    stats: {
      portfolioValue: 2_847_320,
      totalReturn: 42.37,
      winRate: 64.7,
      openPositions: 11,
    },
  },
  // Future strategies (inactive/coming soon)
  {
    id: "supertrend",
    name: "Supertrend",
    description: "ATR-based supertrend with dynamic stop loss and re-entry logic",
    status: "inactive",
    stocks: 0,
    lastScan: "",
    tags: ["ATR", "Supertrend", "NSE EQ"],
    stats: {
      portfolioValue: 0,
      totalReturn: 0,
      winRate: 0,
      openPositions: 0,
    },
  },
  {
    id: "rsi-reversal",
    name: "RSI Reversal",
    description: "RSI oversold bounce with trend confirmation and risk-reward filter",
    status: "inactive",
    stocks: 0,
    lastScan: "",
    tags: ["RSI", "Mean Reversion", "Midcap"],
    stats: {
      portfolioValue: 0,
      totalReturn: 0,
      winRate: 0,
      openPositions: 0,
    },
  },
];
