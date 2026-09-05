// ============================================================
// Portfolio Domain Types
// Golden Cross Research Platform
// ============================================================

export interface Position {
  id: string;
  strategyId: string;
  symbol: string;
  companyName: string;
  exchange: "NSE" | "BSE";
  sector: string;
  industry: string;

  // Position details
  quantity: number;
  entryPrice: number;
  currentPrice: number;
  entryDate: string; // ISO
  holdingDays: number;

  // Values
  entryValue: number;
  currentValue: number;

  // P&L (unrealized)
  unrealizedPnl: number;
  unrealizedPnlPercent: number;

  // Risk levels
  stopLoss: number;
  target: number;
  stopLossPercent: number; // distance to SL from current
  targetPercent: number; // distance to target from current

  // Weight in portfolio
  allocationPercent: number;
}

export interface SectorAllocation {
  sector: string;
  value: number;
  percent: number;
  positions: number;
  color: string;
}

export interface PortfolioSnapshot {
  snapshotDate: string; // ISO
  totalValue: number;
  cash: number;
  invested: number;
  unrealizedPnl: number;
  unrealizedPnlPercent: number;
  dayChange: number;
  dayChangePercent: number;
  openPositions: number;
  sectorAllocations: SectorAllocation[];
  positions: Position[];
}

export interface PortfolioMetrics {
  beta: number;
  alpha: number;
  correlation: number; // correlation with benchmark
  volatility: number; // annualized
  var95: number; // 1-day 95% VaR
  concentration: number; // Herfindahl index
}
