"use client";

import Link from "next/link";
import {
  TrendingUp,
  TrendingDown,
  Activity,
  CirclePause,
  ArrowRight,
  Zap,
  Clock,
  Layers,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { formatCurrency, formatPercent, formatRelativeTime } from "@/lib/formatters";
import { ROUTES } from "@/lib/constants";
import type { StrategyListItem, StrategyStatus } from "@/types";

// ---- Status Badge ----------------------------------------------------------

const STATUS_CONFIG: Record<
  StrategyStatus,
  { label: string; className: string; Icon: React.ComponentType<{ className?: string }> }
> = {
  active: {
    label: "Active",
    className: "bg-gain/10 text-gain border border-gain/20",
    Icon: Activity,
  },
  inactive: {
    label: "Inactive",
    className: "bg-muted text-muted-foreground border border-border",
    Icon: CirclePause,
  },
  backtesting: {
    label: "Backtesting",
    className: "bg-primary/10 text-primary border border-primary/20",
    Icon: Zap,
  },
  paused: {
    label: "Paused",
    className: "bg-yellow-500/10 text-yellow-400 border border-yellow-500/20",
    Icon: CirclePause,
  },
};

// ---- Component -------------------------------------------------------------

interface StrategyCardProps {
  strategy: StrategyListItem;
}

export default function StrategyCard({ strategy }: StrategyCardProps) {
  const statusConfig = STATUS_CONFIG[strategy.status];
  const StatusIcon = statusConfig.Icon;
  const isActive = strategy.status === "active";
  const isPositive = strategy.stats.totalReturn >= 0;

  return (
    <Link
      href={ROUTES.STRATEGY(strategy.id)}
      className={cn(
        "group block rounded-2xl border border-border bg-card",
        "p-6 card-hover",
        isActive ? "hover:border-primary/30" : "hover:border-border/60"
      )}
      aria-label={`Open ${strategy.name} strategy`}
    >
      {/* Header */}
      <div className="flex items-start justify-between gap-3 mb-4">
        <div className="flex items-center gap-3">
          <div
            className={cn(
              "w-10 h-10 rounded-xl flex items-center justify-center shrink-0",
              isActive ? "bg-primary/10" : "bg-muted"
            )}
          >
            {isActive ? (
              <TrendingUp className="w-5 h-5 text-primary" />
            ) : (
              <TrendingDown className="w-5 h-5 text-muted-foreground" />
            )}
          </div>

          <div>
            <h2 className="text-base font-bold text-foreground leading-tight">
              {strategy.name}
            </h2>
            <div className="flex flex-wrap gap-1 mt-1">
              {strategy.tags.slice(0, 2).map((tag) => (
                <span
                  key={tag}
                  className="text-[10px] px-1.5 py-0.5 rounded bg-muted text-muted-foreground font-medium"
                >
                  {tag}
                </span>
              ))}
            </div>
          </div>
        </div>

        {/* Status Badge */}
        <div
          className={cn(
            "flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold shrink-0",
            statusConfig.className
          )}
        >
          <StatusIcon className="w-3 h-3" />
          {statusConfig.label}
        </div>
      </div>

      {/* Description */}
      <p className="text-sm text-muted-foreground line-clamp-2 mb-5">
        {strategy.description}
      </p>

      {isActive ? (
        <>
          {/* Metrics Grid */}
          <div className="grid grid-cols-2 gap-3 mb-5">
            {/* Portfolio Value */}
            <div className="rounded-lg bg-muted/50 p-3">
              <p className="text-[10px] text-muted-foreground uppercase tracking-wide font-semibold mb-1">
                Portfolio Value
              </p>
              <p className="text-sm font-bold text-foreground">
                {formatCurrency(strategy.stats.portfolioValue, { compact: true })}
              </p>
            </div>

            {/* Total Return */}
            <div className="rounded-lg bg-muted/50 p-3">
              <p className="text-[10px] text-muted-foreground uppercase tracking-wide font-semibold mb-1">
                Total Return
              </p>
              <p
                className={cn(
                  "text-sm font-bold",
                  isPositive ? "text-gain" : "text-loss"
                )}
              >
                {isPositive ? "+" : ""}
                {formatPercent(strategy.stats.totalReturn)}
              </p>
            </div>

            {/* Win Rate */}
            <div className="rounded-lg bg-muted/50 p-3">
              <p className="text-[10px] text-muted-foreground uppercase tracking-wide font-semibold mb-1">
                Win Rate
              </p>
              <p className="text-sm font-bold text-foreground">
                {formatPercent(strategy.stats.winRate)}
              </p>
            </div>

            {/* Open Positions */}
            <div className="rounded-lg bg-muted/50 p-3">
              <p className="text-[10px] text-muted-foreground uppercase tracking-wide font-semibold mb-1">
                Open Positions
              </p>
              <p className="text-sm font-bold text-foreground">
                {strategy.stats.openPositions}
              </p>
            </div>
          </div>

          {/* Footer */}
          <div className="flex items-center justify-between pt-4 border-t border-border">
            <div className="flex items-center gap-4 text-xs text-muted-foreground">
              <span className="flex items-center gap-1.5">
                <Layers className="w-3.5 h-3.5" />
                {strategy.stocks.toLocaleString()} stocks
              </span>
              <span className="flex items-center gap-1.5">
                <Clock className="w-3.5 h-3.5" />
                {strategy.lastScan ? formatRelativeTime(strategy.lastScan) : "Never"}
              </span>
            </div>

            <div className="flex items-center gap-1.5 text-xs font-semibold text-primary opacity-0 group-hover:opacity-100 transition-opacity duration-200">
              Open
              <ArrowRight className="w-3.5 h-3.5" />
            </div>
          </div>
        </>
      ) : (
        /* Coming Soon State */
        <div className="flex flex-col items-center justify-center py-6 text-center">
          <div className="w-12 h-12 rounded-full bg-muted flex items-center justify-center mb-3">
            <Zap className="w-6 h-6 text-muted-foreground" />
          </div>
          <p className="text-sm font-medium text-muted-foreground">Coming Soon</p>
          <p className="text-xs text-muted-foreground/60 mt-1">
            This strategy is not yet configured
          </p>
        </div>
      )}
    </Link>
  );
}