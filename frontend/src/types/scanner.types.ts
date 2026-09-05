// ============================================================
// Scanner Domain Types
// Golden Cross Research Platform
// ============================================================

export type SignalStrength = "strong" | "moderate" | "weak";
export type CrossoverType = "golden" | "death" | "approaching_golden" | "approaching_death";
export type ScanStatus = "fresh" | "existing" | "exited";

export interface ScanResult {
  id: string;
  strategyId: string;
  symbol: string;
  companyName: string;
  exchange: "NSE" | "BSE";
  sector: string;
  industry: string;

  // Signal
  crossoverType: CrossoverType;
  scanStatus: ScanStatus;
  signalStrength: SignalStrength;
  scannedAt: string; // ISO

  // Price data
  currentPrice: number;
  dayChangePercent: number;
  weekChangePercent: number;
  volume: number;
  avgVolume: number;
  volumeRatio: number; // volume / avgVolume

  // EMA data
  ema50: number;
  ema200: number;
  ema50ema200Gap: number; // percentage gap between EMAs
  crossoverDate?: string; // ISO — when crossover occurred

  // Fundamentals (optional, for richer screening)
  marketCap?: number;
  peRatio?: number;
  fiftyTwoWeekHigh?: number;
  fiftyTwoWeekLow?: number;

  // Technical
  rsi14?: number;
  atr14?: number;
  adx14?: number;

  // Risk / Entry
  suggestedEntry: number;
  suggestedStopLoss: number;
  suggestedTarget: number;
  riskRewardRatio: number;

  // Watchlist
  isWatchlisted: boolean;
  hasAlert: boolean;
  notes?: string;
}

export interface ScannerFilters {
  crossoverType?: CrossoverType[];
  signalStrength?: SignalStrength[];
  sector?: string[];
  exchange?: ("NSE" | "BSE")[];
  minMarketCap?: number;
  maxMarketCap?: number;
  minVolume?: number;
  minRsi?: number;
  maxRsi?: number;
  isWatchlisted?: boolean;
  searchQuery?: string;
}

export interface ScannerSummary {
  totalResults: number;
  freshCrossovers: number;
  existingSignals: number;
  addedToWatchlist: number;
  lastScanAt: string; // ISO
  scannedSymbols: number;
}

export interface WatchlistItem {
  symbol: string;
  companyName: string;
  addedAt: string;
  currentPrice: number;
  dayChangePercent: number;
  alert?: {
    type: "price_above" | "price_below" | "crossover";
    value: number;
    triggered: boolean;
  };
}
