// ============================================================
// Trade Domain Types
// Golden Cross Research Platform
// ============================================================

export type TradeStatus = "open" | "closed" | "partial";

export type TradeDirection = "long" | "short";

export type ExitReason =
  | "target"
  | "stop_loss"
  | "trailing_stop"
  | "manual"
  | "time_exit"
  | "signal_reversal";

export interface Trade {
  id: string;
  strategyId: string;
  symbol: string;
  companyName: string;
  exchange: "NSE" | "BSE";
  direction: TradeDirection;
  status: TradeStatus;

  // Entry
  entryDate: string; // ISO
  entryPrice: number;
  quantity: number;
  entryValue: number; // entryPrice * quantity

  // Exit
  exitDate?: string; // ISO — undefined if open
  exitPrice?: number;
  exitReason?: ExitReason;

  // P&L
  pnl?: number; // absolute ₹
  pnlPercent?: number; // percentage
  holdingDays?: number;

  // Risk
  stopLoss: number;
  target: number;
  riskRewardRatio: number;

  // Meta
  ema50AtEntry: number;
  ema200AtEntry: number;
  volumeAtEntry: number;
  notes?: string;
}

export interface TradeFilters {
  status?: TradeStatus;
  symbol?: string;
  exitReason?: ExitReason;
  dateFrom?: string;
  dateTo?: string;
  minPnl?: number;
  maxPnl?: number;
}

export interface TradeSummary {
  totalTrades: number;
  openTrades: number;
  closedTrades: number;
  winners: number;
  losers: number;
  winRate: number;
  avgWin: number;
  avgLoss: number;
  profitFactor: number;
  totalPnl: number;
  largestWin: number;
  largestLoss: number;
  avgHoldingDays: number;
  exitReasonBreakdown: Record<ExitReason, number>;
}
