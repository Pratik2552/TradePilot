// ============================================================
// Strategy Domain Types
// Golden Cross Research Platform
// ============================================================

export type StrategyStatus = "active" | "inactive" | "backtesting" | "paused";

export type StrategyCategory =
  | "trend_following"
  | "mean_reversion"
  | "momentum"
  | "breakout"
  | "volatility";

export interface StrategyConfig {
  initialCapital: number;
  riskPerTrade: number;
  maxPositions: number;
  emaPeriodFast: number;
  emaPeriodSlow: number;
  stopLossPercent: number;
  takeProfitPercent: number;
  scanTimeframe: string;
  universe: string;
  // Engine-specific fields returned by backend
  goldenCrossLookback?: number;
  gapThreshold?: number;
  allocation?: number;
}

export interface StrategyStats {
  portfolioValue: number;
  capitalDeployed: number;
  openPositions: number;
  closedTrades: number;
  winRate: number; // 0–100
  profitFactor: number;
  averageReturn: number; // percentage
  averageHoldingDays: number;
  totalReturn: number; // percentage from inception
  cagr: number;
  sharpeRatio: number;
  maxDrawdown: number; // percentage, negative
}

export interface Strategy {
  id: string;
  name: string;
  description: string;
  longDescription?: string;
  status: StrategyStatus;
  category: StrategyCategory;
  stocks: number; // universe size
  lastScan: string; // ISO datetime string
  createdAt: string; // ISO datetime string
  config: StrategyConfig;
  stats: StrategyStats;
  tags: string[];
}

export interface StrategyListItem
  extends Pick<
    Strategy,
    "id" | "name" | "description" | "status" | "stocks" | "lastScan" | "tags"
  > {
  stats: Pick<
    StrategyStats,
    "portfolioValue" | "totalReturn" | "winRate" | "openPositions"
  >;
}
