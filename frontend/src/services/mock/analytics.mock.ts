// ============================================================
// Analytics Mock Data
// Golden Cross Research Platform
// ============================================================

import type { AnalyticsSnapshot } from "@/types";

// Generate equity curve from Jan 2024 to Dec 2024
function generateEquityCurve() {
  const points = [];
  let equity = 2_000_000;
  let benchmark = 2_000_000;
  const startDate = new Date("2024-01-01");

  for (let i = 0; i < 240; i++) {
    const date = new Date(startDate);
    date.setDate(date.getDate() + i);

    // Skip weekends
    if (date.getDay() === 0 || date.getDay() === 6) continue;

    // Random walk with upward bias
    const dailyReturn = (Math.random() - 0.42) * 0.025;
    const benchmarkReturn = (Math.random() - 0.45) * 0.018;

    equity = equity * (1 + dailyReturn);
    benchmark = benchmark * (1 + benchmarkReturn);

    // Calculate running drawdown
    const peak = 2_847_320; // simplified — use running max in real
    const drawdown = ((equity - peak) / peak) * 100;

    points.push({
      date: date.toISOString().split("T")[0],
      equity: Math.round(equity),
      benchmark: Math.round(benchmark),
      drawdownPercent: Math.min(0, parseFloat(drawdown.toFixed(2))),
    });
  }

  return points;
}

// Monthly returns for 12 months
const MONTHLY_RETURNS = [
  { year: 2024, month: 1, returnPercent: 4.2, benchmark: 1.8 },
  { year: 2024, month: 2, returnPercent: -2.1, benchmark: -1.2 },
  { year: 2024, month: 3, returnPercent: 6.8, benchmark: 3.4 },
  { year: 2024, month: 4, returnPercent: 3.1, benchmark: 2.1 },
  { year: 2024, month: 5, returnPercent: 8.4, benchmark: 4.8 },
  { year: 2024, month: 6, returnPercent: -3.2, benchmark: -1.4 },
  { year: 2024, month: 7, returnPercent: 5.6, benchmark: 2.8 },
  { year: 2024, month: 8, returnPercent: 7.2, benchmark: 3.6 },
  { year: 2024, month: 9, returnPercent: -1.8, benchmark: -0.8 },
  { year: 2024, month: 10, returnPercent: 4.4, benchmark: 2.2 },
  { year: 2024, month: 11, returnPercent: 6.1, benchmark: 3.0 },
  { year: 2024, month: 12, returnPercent: 2.4, benchmark: 1.2 },
];

const RETURN_DISTRIBUTION = [
  { rangeLabel: "< -10%", rangeMin: -100, rangeMax: -10, count: 4, percent: 2.27 },
  { rangeLabel: "-10% to -7%", rangeMin: -10, rangeMax: -7, count: 18, percent: 10.23 },
  { rangeLabel: "-7% to -3%", rangeMin: -7, rangeMax: -3, count: 24, percent: 13.64 },
  { rangeLabel: "-3% to 0%", rangeMin: -3, rangeMax: 0, count: 16, percent: 9.09 },
  { rangeLabel: "0% to 5%", rangeMin: 0, rangeMax: 5, count: 28, percent: 15.91 },
  { rangeLabel: "5% to 10%", rangeMin: 5, rangeMax: 10, count: 42, percent: 23.86 },
  { rangeLabel: "10% to 15%", rangeMin: 10, rangeMax: 15, count: 32, percent: 18.18 },
  { rangeLabel: "15% to 20%", rangeMin: 15, rangeMax: 20, count: 8, percent: 4.55 },
  { rangeLabel: "> 20%", rangeMin: 20, rangeMax: 100, count: 4, percent: 2.27 },
];

const HOLDING_DISTRIBUTION = [
  { rangeLabel: "0–5 days", rangeMin: 0, rangeMax: 5, count: 8, avgReturn: -3.2 },
  { rangeLabel: "6–10 days", rangeMin: 6, rangeMax: 10, count: 14, avgReturn: 1.4 },
  { rangeLabel: "11–20 days", rangeMin: 11, rangeMax: 20, count: 42, avgReturn: 5.8 },
  { rangeLabel: "21–30 days", rangeMin: 21, rangeMax: 30, count: 68, avgReturn: 8.4 },
  { rangeLabel: "31–45 days", rangeMin: 31, rangeMax: 45, count: 38, avgReturn: 10.2 },
  { rangeLabel: "46–60 days", rangeMin: 46, rangeMax: 60, count: 12, avgReturn: 12.8 },
  { rangeLabel: "> 60 days", rangeMin: 60, rangeMax: 999, count: 5, avgReturn: 14.6 },
];

export const ANALYTICS_MOCK: Record<string, AnalyticsSnapshot> = {
  "golden-cross": {
    strategyId: "golden-cross",
    computedAt: new Date().toISOString(),

    // Core metrics
    totalReturn: 42.37,
    cagr: 28.6,
    sharpeRatio: 1.84,
    sortinoRatio: 2.42,
    calmarRatio: 2.01,
    maxDrawdown: -14.2,
    maxDrawdownDuration: 38,
    recoveryFactor: 2.98,

    // Trade metrics
    totalTrades: 187,
    winRate: 64.7,
    avgWinPercent: 10.2,
    avgLossPercent: -6.8,
    profitFactor: 2.31,
    expectancy: 4520,
    avgHoldingDays: 23,

    // Risk metrics
    volatilityAnnual: 18.4,
    beta: 0.82,
    alpha: 14.2,
    informationRatio: 1.24,

    // Time series
    equityCurve: generateEquityCurve(),
    drawdownPeriods: [
      {
        startDate: "2024-02-01",
        endDate: "2024-02-28",
        peakValue: 2_180_000,
        troughValue: 1_870_000,
        drawdownPercent: -14.22,
        recoveryDays: 38,
      },
      {
        startDate: "2024-06-03",
        endDate: "2024-06-24",
        peakValue: 2_420_000,
        troughValue: 2_240_000,
        drawdownPercent: -7.44,
        recoveryDays: 22,
      },
      {
        startDate: "2024-09-09",
        peakValue: 2_720_000,
        troughValue: 2_580_000,
        drawdownPercent: -5.15,
      },
    ],
    monthlyReturns: MONTHLY_RETURNS,
    rollingMetrics: [],
    returnDistribution: RETURN_DISTRIBUTION,
    holdingDistribution: HOLDING_DISTRIBUTION,
  },
};
