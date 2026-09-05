// ============================================================
// Application Constants
// Golden Cross Research Platform
// ============================================================

export const APP_NAME = "Golden Cross";
export const APP_DESCRIPTION = "Quantitative Trading Research Platform";
export const APP_TAGLINE = "Research • Backtest • Scan • Optimize";

// ---- Routes ----------------------------------------------------------------

export const ROUTES = {
  HOME: "/",
  STRATEGY: (id: string) => `/strategy/${id}`,
  STRATEGY_OVERVIEW: (id: string) => `/strategy/${id}/overview`,
  STRATEGY_SCANNER: (id: string) => `/strategy/${id}/scanner`,
  STRATEGY_PORTFOLIO: (id: string) => `/strategy/${id}/portfolio`,
  STRATEGY_TRADES: (id: string) => `/strategy/${id}/trades`,
  STRATEGY_ANALYTICS: (id: string) => `/strategy/${id}/analytics`,
  STRATEGY_SETTINGS: (id: string) => `/strategy/${id}/settings`,
} as const;

// ---- Design ----------------------------------------------------------------

export const CHART_COLORS = {
  gain: "#10b981",     // emerald-500
  loss: "#ef4444",     // red-500
  primary: "#3b82f6",  // blue-500
  secondary: "#8b5cf6", // violet-500
  muted: "#71717a",    // zinc-500
  benchmark: "#f59e0b", // amber-500
  grid: "rgba(255,255,255,0.06)",
  tooltip: "rgba(9,9,11,0.95)",
} as const;

export const SECTOR_COLORS: Record<string, string> = {
  "Financial Services": "#3b82f6",
  "Information Technology": "#8b5cf6",
  "Healthcare": "#10b981",
  "Consumer Goods": "#f59e0b",
  "Industrials": "#06b6d4",
  "Energy": "#f97316",
  "Materials": "#84cc16",
  "Real Estate": "#ec4899",
  "Communication": "#6366f1",
  "Utilities": "#14b8a6",
  "Automobiles": "#a855f7",
  "Other": "#71717a",
};

// ---- Pagination -------------------------------------------------------------

export const DEFAULT_PAGE_SIZE = 20;
export const PAGE_SIZE_OPTIONS = [10, 20, 50, 100] as const;

// ---- API -------------------------------------------------------------------

export const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export const API_TIMEOUT_MS = 30_000;

// ---- Feature Flags ---------------------------------------------------------

export const FEATURES = {
  LIVE_TRADING: false,
  PAPER_TRADING: false,
  BROKER_CONNECT: false,
  MULTI_STRATEGY: true,
  NOTIFICATIONS: true,
  EXPORT_CSV: true,
  DARK_MODE: true,
} as const;

// ---- Trading Constants -----------------------------------------------------

export const EXCHANGES = ["NSE", "BSE"] as const;

export const TIMEFRAMES = [
  { label: "Daily", value: "1D" },
  { label: "Weekly", value: "1W" },
  { label: "Monthly", value: "1M" },
] as const;

export const MONTHS = [
  "Jan", "Feb", "Mar", "Apr", "May", "Jun",
  "Jul", "Aug", "Sep", "Oct", "Nov", "Dec",
] as const;
