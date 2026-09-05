"use client";

import { useAnalytics } from "@/hooks/useAnalytics";
import PageHeader from "@/components/common/PageHeader";
import KpiCard from "@/components/cards/KpiCard";
import EquityCurveChart from "@/components/charts/EquityCurveChart";
import DrawdownChart from "@/components/charts/DrawdownChart";
import MonthlyReturnsChart from "@/components/charts/MonthlyReturnsChart";
import ReturnDistributionChart from "@/components/charts/ReturnDistributionChart";
import {
  TrendingUp,
  Target,
  Shield,
  Sigma,
  BarChart2,
  Clock,
  Zap,
  ArrowDownRight,
} from "lucide-react";
import {
  formatPercent,
  formatNumber,
  formatDays,
  formatCurrency,
} from "@/lib/formatters";

// ---- Metric Row ------------------------------------------------------------

function MetricRow({ label, value, subtext }: { label: string; value: string; subtext?: string }) {
  return (
    <div className="flex items-center justify-between py-2.5 border-b border-border last:border-0">
      <span className="text-sm text-muted-foreground">{label}</span>
      <div className="text-right">
        <span className="text-sm font-semibold text-foreground">{value}</span>
        {subtext && <span className="ml-2 text-xs text-muted-foreground">{subtext}</span>}
      </div>
    </div>
  );
}

// ---- Page ------------------------------------------------------------------

interface AnalyticsPageClientProps {
  strategyId: string;
}

export default function AnalyticsPageClient({ strategyId }: AnalyticsPageClientProps) {
  const { analytics, isLoading, error } = useAnalytics(strategyId);

  if (isLoading) {
    return (
      <div className="px-6 pt-8 space-y-5">
        <div className="h-8 w-40 bg-muted animate-pulse rounded-lg" />
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {Array.from({ length: 8 }).map((_, i) => (
            <div key={i} className="h-28 bg-muted animate-pulse rounded-xl" />
          ))}
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="px-6 pt-16 text-center">
        <p className="text-muted-foreground">Failed to load analytics.</p>
        <p className="text-xs text-muted-foreground/60 mt-2">{error.message}</p>
      </div>
    );
  }

  if (!analytics) return null;

  return (
    <div className="pb-8">
      <PageHeader
        title="Analytics"
        subtitle="Deep performance analysis of your strategy"
      />

      {/* Top KPIs */}
      <div className="px-6 grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-4 mb-6">
        <KpiCard
          title="Total Return"
          value={formatPercent(analytics.totalReturn, { showSign: true })}
          icon={<TrendingUp className="w-4 h-4" />}
          variant={analytics.totalReturn >= 0 ? "gain" : "loss"}
        />
        <KpiCard
          title="CAGR"
          value={formatPercent(analytics.cagr, { showSign: true })}
          subValue="annualized"
          icon={<Zap className="w-4 h-4" />}
          variant={analytics.cagr >= 15 ? "gain" : "default"}
        />
        <KpiCard
          title="Sharpe Ratio"
          value={formatNumber(analytics.sharpeRatio)}
          subValue="risk-adjusted return"
          icon={<Sigma className="w-4 h-4" />}
          variant={analytics.sharpeRatio >= 1.5 ? "gain" : "default"}
        />
        <KpiCard
          title="Max Drawdown"
          value={formatPercent(analytics.maxDrawdown)}
          subValue={`${analytics.maxDrawdownDuration} days duration`}
          icon={<ArrowDownRight className="w-4 h-4" />}
          variant="loss"
        />
        <KpiCard
          title="Win Rate"
          value={formatPercent(analytics.winRate)}
          icon={<Target className="w-4 h-4" />}
          variant={analytics.winRate >= 60 ? "gain" : "default"}
        />
        <KpiCard
          title="Profit Factor"
          value={formatNumber(analytics.profitFactor) + "x"}
          icon={<BarChart2 className="w-4 h-4" />}
          variant={analytics.profitFactor >= 2 ? "gain" : "default"}
        />
        <KpiCard
          title="Sortino Ratio"
          value={formatNumber(analytics.sortinoRatio)}
          icon={<Shield className="w-4 h-4" />}
          variant={analytics.sortinoRatio >= 2 ? "gain" : "default"}
        />
        <KpiCard
          title="Avg Holding"
          value={formatDays(analytics.avgHoldingDays)}
          icon={<Clock className="w-4 h-4" />}
        />
      </div>

      {/* Equity Curve */}
      <div className="px-6 mb-5">
        <div className="rounded-xl border border-border bg-card p-5">
          <h3 className="font-semibold text-foreground mb-1">Equity Curve</h3>
          <p className="text-xs text-muted-foreground mb-5">Portfolio value over time vs NIFTY 50</p>
          <EquityCurveChart data={analytics.equityCurve} height={280} />
        </div>
      </div>

      {/* Drawdown */}
      <div className="px-6 mb-5">
        <div className="rounded-xl border border-border bg-card p-5">
          <h3 className="font-semibold text-foreground mb-1">Drawdown</h3>
          <p className="text-xs text-muted-foreground mb-5">Underwater equity (% from peak)</p>
          <DrawdownChart data={analytics.equityCurve} height={200} />
        </div>
      </div>

      {/* Monthly Returns + Distribution */}
      <div className="px-6 grid grid-cols-1 lg:grid-cols-2 gap-5 mb-5">
        <div className="rounded-xl border border-border bg-card p-5">
          <h3 className="font-semibold text-foreground mb-1">Monthly Returns</h3>
          <p className="text-xs text-muted-foreground mb-5">Month-by-month performance</p>
          <MonthlyReturnsChart data={analytics.monthlyReturns} height={220} />
        </div>

        <div className="rounded-xl border border-border bg-card p-5">
          <h3 className="font-semibold text-foreground mb-1">Return Distribution</h3>
          <p className="text-xs text-muted-foreground mb-5">Frequency of returns by bucket</p>
          <ReturnDistributionChart data={analytics.returnDistribution} height={220} />
        </div>
      </div>

      {/* Detailed Metrics */}
      <div className="px-6 grid grid-cols-1 lg:grid-cols-2 gap-5">
        {/* Return Metrics */}
        <div className="rounded-xl border border-border bg-card p-5">
          <h3 className="font-semibold text-foreground mb-4">Return Metrics</h3>
          <MetricRow label="Total Return" value={formatPercent(analytics.totalReturn, { showSign: true })} />
          <MetricRow label="CAGR" value={formatPercent(analytics.cagr, { showSign: true })} />
          <MetricRow label="Alpha" value={formatPercent(analytics.alpha, { showSign: true })} subtext="vs benchmark" />
          <MetricRow label="Beta" value={formatNumber(analytics.beta, 2)} />
          <MetricRow label="Annual Volatility" value={formatPercent(analytics.volatilityAnnual)} />
          <MetricRow label="Recovery Factor" value={formatNumber(analytics.recoveryFactor) + "x"} />
        </div>

        {/* Trade Metrics */}
        <div className="rounded-xl border border-border bg-card p-5">
          <h3 className="font-semibold text-foreground mb-4">Trade Metrics</h3>
          <MetricRow label="Total Trades" value={String(analytics.totalTrades)} />
          <MetricRow label="Win Rate" value={formatPercent(analytics.winRate)} />
          <MetricRow label="Avg Win" value={formatPercent(analytics.avgWinPercent, { showSign: true })} />
          <MetricRow label="Avg Loss" value={formatPercent(analytics.avgLossPercent)} />
          <MetricRow label="Profit Factor" value={formatNumber(analytics.profitFactor) + "x"} />
          <MetricRow label="Expectancy" value={formatCurrency(analytics.expectancy, { compact: true })} subtext="per trade" />
        </div>
      </div>
    </div>
  );
}
