// ============================================================
// Analytics Domain Types
// Golden Cross Research Platform
// ============================================================

export interface EquityPoint {
  date: string; // ISO
  equity: number; // absolute portfolio value
  benchmark?: number; // e.g. NIFTY 50 rebased to same start
  drawdownPercent: number; // negative
}

export interface DrawdownPeriod {
  startDate: string;
  endDate?: string; // undefined = still in drawdown
  peakValue: number;
  troughValue: number;
  drawdownPercent: number; // negative
  recoveryDays?: number;
}

export interface MonthlyReturn {
  year: number;
  month: number; // 1–12
  returnPercent: number;
  benchmark?: number;
}

export interface RollingMetricPoint {
  date: string; // ISO
  rollingCagr?: number;
  rollingSharpe?: number;
  rollingSortino?: number;
  rollingMaxDrawdown?: number;
}

export interface ReturnDistributionBucket {
  rangeLabel: string; // e.g. "-10% to -5%"
  rangeMin: number;
  rangeMax: number;
  count: number;
  percent: number; // % of total trades
}

export interface HoldingDistributionBucket {
  rangeLabel: string; // e.g. "0–5 days"
  rangeMin: number;
  rangeMax: number;
  count: number;
  avgReturn: number;
}

export interface AnalyticsSnapshot {
  strategyId: string;
  computedAt: string; // ISO

  // Core metrics
  totalReturn: number; // percentage
  cagr: number;
  sharpeRatio: number;
  sortinoRatio: number;
  calmarRatio: number;
  maxDrawdown: number; // negative percentage
  maxDrawdownDuration: number; // days
  recoveryFactor: number;

  // Trade metrics
  totalTrades: number;
  winRate: number;
  avgWinPercent: number;
  avgLossPercent: number;
  profitFactor: number;
  expectancy: number; // expected return per trade in ₹
  avgHoldingDays: number;

  // Risk metrics
  volatilityAnnual: number;
  beta: number;
  alpha: number;
  informationRatio: number;

  // Time series
  equityCurve: EquityPoint[];
  drawdownPeriods: DrawdownPeriod[];
  monthlyReturns: MonthlyReturn[];
  rollingMetrics: RollingMetricPoint[];
  returnDistribution: ReturnDistributionBucket[];
  holdingDistribution: HoldingDistributionBucket[];
}
