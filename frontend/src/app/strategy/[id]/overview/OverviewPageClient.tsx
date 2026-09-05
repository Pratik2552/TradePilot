"use client";

import { useStrategy } from "@/hooks/useStrategy";
import { useAnalytics } from "@/hooks/useAnalytics";
import { useTrades } from "@/hooks/useTrades";
import { usePortfolio } from "@/hooks/usePortfolio";
import PageHeader from "@/components/common/PageHeader";
import KpiCard from "@/components/cards/KpiCard";
import EquityCurveChart from "@/components/charts/EquityCurveChart";
import {
  Wallet,
  TrendingUp,
  BriefcaseBusiness,
  BarChart3,
  Target,
  Zap,
  Clock,
  Sigma,
} from "lucide-react";
import {
  formatCurrency,
  formatPercent,
  formatNumber,
  formatDays,
  formatDate,
  formatRelativeTime,
} from "@/lib/formatters";
import { cn } from "@/lib/utils";
import type { Trade } from "@/types";

// ---- Exit Reason Badge -----------------------------------------------------

const EXIT_REASON_LABELS: Record<string, string> = {
  target: "Target",
  stop_loss: "Stop Loss",
  trailing_stop: "Trailing Stop",
  manual: "Manual",
  time_exit: "Time Exit",
  signal_reversal: "Reversal",
};

const EXIT_REASON_COLORS: Record<string, string> = {
  target: "bg-gain/10 text-gain",
  stop_loss: "bg-loss/10 text-loss",
  trailing_stop: "bg-primary/10 text-primary",
  manual: "bg-muted text-muted-foreground",
  time_exit: "bg-muted text-muted-foreground",
  signal_reversal: "bg-yellow-500/10 text-yellow-400",
};

function ExitReasonBadge({ reason }: { reason: string }) {
  return (
    <span
      className={cn(
        "px-2 py-0.5 rounded-full text-[11px] font-semibold",
        EXIT_REASON_COLORS[reason] ?? "bg-muted text-muted-foreground"
      )}
    >
      {EXIT_REASON_LABELS[reason] ?? reason}
    </span>
  );
}

// ---- Recent Trade Row ------------------------------------------------------

function TradeRow({ trade }: { trade: Trade }) {
  const isWin = (trade.pnlPercent ?? 0) >= 0;

  return (
    <div className="flex items-center gap-4 py-3 border-b border-border last:border-0">
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2">
          <span className="font-semibold text-sm text-foreground">{trade.symbol}</span>
          {trade.exitReason && <ExitReasonBadge reason={trade.exitReason} />}
        </div>
        <p className="text-xs text-muted-foreground mt-0.5">
          {trade.entryDate ? formatDate(trade.entryDate) : ""}{" "}
          {trade.holdingDays !== undefined ? `· ${formatDays(trade.holdingDays)}` : ""}
        </p>
      </div>

      <div className="text-right shrink-0">
        <p
          className={cn(
            "text-sm font-bold",
            isWin ? "text-gain" : "text-loss"
          )}
        >
          {trade.pnl !== undefined
            ? `${isWin ? "+" : ""}${formatCurrency(trade.pnl, { compact: true })}`
            : "-"}
        </p>
        <p
          className={cn(
            "text-xs font-medium",
            isWin ? "text-gain/80" : "text-loss/80"
          )}
        >
          {trade.pnlPercent !== undefined
            ? formatPercent(trade.pnlPercent, { showSign: true })
            : ""}
        </p>
      </div>
    </div>
  );
}

// ---- Page ------------------------------------------------------------------

interface OverviewPageClientProps {
  strategyId: string;
}

export default function OverviewPageClient({ strategyId }: OverviewPageClientProps) {
  const { strategy, isLoading: strategyLoading } = useStrategy(strategyId);
  const { analytics, isLoading: analyticsLoading } = useAnalytics(strategyId);
  const { trades, isLoading: tradesLoading } = useTrades(strategyId);
  const { portfolio } = usePortfolio(strategyId);

  const stats = strategy?.stats;
  const recentClosedTrades = trades.filter((t) => t.status === "closed").slice(0, 6);

  if (strategyLoading) {
    return (
      <div className="px-6 pt-8 space-y-6">
        <div className="h-8 w-48 bg-muted animate-pulse rounded-lg" />
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {Array.from({ length: 8 }).map((_, i) => (
            <div key={i} className="h-28 bg-muted animate-pulse rounded-xl" />
          ))}
        </div>
        <div className="h-80 bg-muted animate-pulse rounded-xl" />
      </div>
    );
  }

  if (!strategy) {
    return (
      <div className="px-6 pt-16 text-center">
        <p className="text-muted-foreground">Strategy not found or backend unavailable.</p>
      </div>
    );
  }

  return (
    <div className="pb-8">
      <PageHeader
        title="Overview"
        subtitle={`Last scan: ${strategy?.lastScan ? formatRelativeTime(strategy.lastScan) : "N/A"}`}
      />

      {/* ---- KPI Grid ---- */}
      <div className="px-6 grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-4 mb-6">
        <KpiCard
          title="Portfolio Value"
          value={formatCurrency(stats?.portfolioValue ?? 0, { compact: true })}
          delta={portfolio?.dayChangePercent}
          deltaLabel="today"
          icon={<Wallet className="w-4 h-4" />}
          variant="brand"
        />
        <KpiCard
          title="Capital Deployed"
          value={formatCurrency(stats?.capitalDeployed ?? 0, { compact: true })}
          subValue={`of ${formatCurrency(strategy?.config?.initialCapital ?? 0, { compact: true })} capital`}
          icon={<TrendingUp className="w-4 h-4" />}
        />
        <KpiCard
          title="Open Positions"
          value={String(stats?.openPositions ?? 0)}
          subValue={`of ${strategy?.config?.maxPositions ?? 0} max`}
          icon={<BriefcaseBusiness className="w-4 h-4" />}
        />
        <KpiCard
          title="Closed Trades"
          value={String(stats?.closedTrades ?? 0)}
          icon={<BarChart3 className="w-4 h-4" />}
        />
        <KpiCard
          title="Win Rate"
          value={formatPercent(stats?.winRate ?? 0)}
          subValue="of closed trades"
          icon={<Target className="w-4 h-4" />}
          variant={stats && stats.winRate >= 50 ? "gain" : "loss"}
        />
        <KpiCard
          title="Profit Factor"
          value={formatNumber(stats?.profitFactor ?? 0) + "x"}
          subValue="Gross profit / Gross loss"
          icon={<Sigma className="w-4 h-4" />}
          variant={stats && stats.profitFactor >= 1.5 ? "gain" : "default"}
        />
        <KpiCard
          title="Avg Return"
          value={formatPercent(stats?.averageReturn ?? 0, { showSign: true })}
          subValue="per trade"
          icon={<Zap className="w-4 h-4" />}
          variant={stats && stats.averageReturn >= 0 ? "gain" : "loss"}
        />
        <KpiCard
          title="Avg Holding"
          value={formatDays(stats?.averageHoldingDays ?? 0)}
          subValue="per closed trade"
          icon={<Clock className="w-4 h-4" />}
        />
      </div>

      {/* ---- Equity Curve ---- */}
      <div className="px-6 mb-6">
        <div className="rounded-xl border border-border bg-card p-5">
          <div className="flex items-center justify-between mb-5">
            <div>
              <h3 className="font-semibold text-foreground">Equity Curve</h3>
              <p className="text-xs text-muted-foreground mt-0.5">
                Strategy vs NIFTY 50 (rebased to ₹20L)
              </p>
            </div>
            <div className="flex items-center gap-3 text-xs">
              <span className="flex items-center gap-1.5 text-muted-foreground">
                <span className="w-2 h-2 rounded-full bg-primary inline-block" />
                Strategy
              </span>
              <span className="flex items-center gap-1.5 text-muted-foreground">
                <span className="w-2 h-2 rounded-full inline-block" style={{ background: "#f59e0b" }} />
                NIFTY 50
              </span>
            </div>
          </div>

          <EquityCurveChart
            data={analytics?.equityCurve ?? []}
            showBenchmark
            height={280}
          />
        </div>
      </div>

      {/* ---- Bottom Grid: Recent Trades + Exit Reasons ---- */}
      <div className="px-6 grid grid-cols-1 lg:grid-cols-3 gap-5">

        {/* Recent Trades */}
        <div className="lg:col-span-2 rounded-xl border border-border bg-card p-5">
          <div className="flex items-center justify-between mb-4">
            <h3 className="font-semibold text-foreground">Recent Trades</h3>
            <span className="text-xs text-muted-foreground">Last 6 closed</span>
          </div>
          <div>
            {recentClosedTrades.length > 0 ? (
              recentClosedTrades.map((trade) => (
                <TradeRow key={trade.id} trade={trade} />
              ))
            ) : (
              <p className="text-sm text-muted-foreground text-center py-8">
                No closed trades yet
              </p>
            )}
          </div>
        </div>

        {/* Exit Reasons */}
        <div className="rounded-xl border border-border bg-card p-5">
          <h3 className="font-semibold text-foreground mb-4">Exit Reasons</h3>
          {analytics && (
            <div className="space-y-3">
              {Object.entries(analytics.holdingDistribution).length === 0 && (
                <p className="text-sm text-muted-foreground">No data</p>
              )}
              {/* Derive from trades */}
              {Object.entries(
                trades
                  .filter((t) => t.exitReason)
                  .reduce<Record<string, number>>((acc, t) => {
                    if (t.exitReason) {
                      acc[t.exitReason] = (acc[t.exitReason] ?? 0) + 1;
                    }
                    return acc;
                  }, {})
              ).sort((a, b) => b[1] - a[1]).map(([reason, count]) => {
                const total = trades.filter((t) => t.exitReason).length;
                const pct = total > 0 ? (count / total) * 100 : 0;
                return (
                  <div key={reason}>
                    <div className="flex items-center justify-between text-xs mb-1">
                      <ExitReasonBadge reason={reason} />
                      <span className="text-muted-foreground font-medium">
                        {count} ({pct.toFixed(0)}%)
                      </span>
                    </div>
                    <div className="h-1.5 bg-muted rounded-full overflow-hidden">
                      <div
                        className={cn(
                          "h-full rounded-full transition-all duration-500",
                          reason === "target" ? "bg-gain" :
                          reason === "stop_loss" ? "bg-loss" :
                          "bg-primary"
                        )}
                        style={{ width: `${pct}%` }}
                      />
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
