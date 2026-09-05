"use client";

import { usePortfolio } from "@/hooks/usePortfolio";
import PageHeader from "@/components/common/PageHeader";
import AllocationPieChart from "@/components/charts/AllocationPieChart";
import KpiCard from "@/components/cards/KpiCard";
import {
  BriefcaseBusiness,
  TrendingUp,
  TrendingDown,
  Wallet,
  DollarSign,
  ArrowUpRight,
  ArrowDownRight,
} from "lucide-react";
import {
  formatCurrency,
  formatPercent,
  formatDays,
  formatDate,
} from "@/lib/formatters";
import { cn } from "@/lib/utils";
import type { Position } from "@/types";

// ---- Position Row ----------------------------------------------------------

function PositionRow({ position }: { position: Position }) {
  const isPositive = position.unrealizedPnl >= 0;
  const distToSl = ((position.currentPrice - position.stopLoss) / position.currentPrice) * 100;
  const distToTarget = ((position.target - position.currentPrice) / position.currentPrice) * 100;

  return (
    <tr className="border-b border-border hover:bg-muted/30 transition-colors">
      <td className="py-3.5 pl-5 pr-3">
        <div>
          <p className="font-bold text-sm text-foreground">{position.symbol}</p>
          <p className="text-xs text-muted-foreground truncate max-w-[160px]">
            {position.companyName}
          </p>
        </div>
      </td>
      <td className="py-3.5 px-3 hidden sm:table-cell">
        <span className="text-xs text-muted-foreground bg-muted px-2 py-0.5 rounded-full">
          {position.sector}
        </span>
      </td>
      <td className="py-3.5 px-3 text-right">
        <p className="text-sm font-semibold text-foreground">
          ₹{position.currentPrice.toLocaleString("en-IN")}
        </p>
        <p className="text-xs text-muted-foreground">
          Avg: ₹{position.entryPrice.toLocaleString("en-IN")}
        </p>
      </td>
      <td className="py-3.5 px-3 text-right">
        <p className="text-sm font-semibold text-foreground">{position.quantity}</p>
        <p className="text-xs text-muted-foreground">{formatDays(position.holdingDays)} held</p>
      </td>
      <td className="py-3.5 px-3 text-right hidden md:table-cell">
        <p className="text-sm font-semibold text-foreground">
          {formatCurrency(position.currentValue, { compact: true })}
        </p>
        <p className="text-xs text-muted-foreground">
          {position.allocationPercent.toFixed(1)}% of portfolio
        </p>
      </td>
      <td className="py-3.5 px-3 text-right">
        <p className={cn("text-sm font-bold", isPositive ? "text-gain" : "text-loss")}>
          {isPositive ? "+" : ""}
          {formatCurrency(position.unrealizedPnl, { compact: true })}
        </p>
        <p className={cn("text-xs font-medium", isPositive ? "text-gain/80" : "text-loss/80")}>
          {formatPercent(position.unrealizedPnlPercent, { showSign: true })}
        </p>
      </td>
      <td className="py-3.5 px-3 text-right hidden lg:table-cell">
        <p className="text-xs text-loss">
          SL: ₹{position.stopLoss.toLocaleString("en-IN", { maximumFractionDigits: 0 })}
        </p>
        <p className="text-xs text-muted-foreground">
          {distToSl.toFixed(1)}% away
        </p>
      </td>
      <td className="py-3.5 pl-3 pr-5 text-right hidden xl:table-cell">
        <p className="text-xs text-gain">
          Target: ₹{position.target.toLocaleString("en-IN", { maximumFractionDigits: 0 })}
        </p>
        <p className="text-xs text-muted-foreground">
          +{distToTarget.toFixed(1)}% upside
        </p>
      </td>
    </tr>
  );
}

// ---- Page ------------------------------------------------------------------

interface PortfolioPageClientProps {
  strategyId: string;
}

export default function PortfolioPageClient({ strategyId }: PortfolioPageClientProps) {
  const { portfolio, isLoading, error } = usePortfolio(strategyId);

  if (isLoading) {
    return (
      <div className="px-6 pt-8 space-y-5">
        <div className="h-8 w-40 bg-muted animate-pulse rounded-lg" />
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {Array.from({ length: 4 }).map((_, i) => (
            <div key={i} className="h-28 bg-muted animate-pulse rounded-xl" />
          ))}
        </div>
      </div>
    );
  }

  if (error || !portfolio) {
    return (
      <div className="px-6 pt-16 text-center">
        <p className="text-muted-foreground">No portfolio data available.</p>
      </div>
    );
  }

  const cashPct = (portfolio.cash / portfolio.totalValue) * 100;
  const investedPct = (portfolio.invested / portfolio.totalValue) * 100;

  return (
    <div className="pb-8">
      <PageHeader
        title="Portfolio"
        subtitle="Open positions and allocation"
      />

      {/* KPI Row */}
      <div className="px-6 grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
        <KpiCard
          title="Total Value"
          value={formatCurrency(portfolio.totalValue, { compact: true })}
          delta={portfolio.dayChangePercent}
          deltaLabel="today"
          icon={<Wallet className="w-4 h-4" />}
          variant="brand"
        />
        <KpiCard
          title="Invested"
          value={formatCurrency(portfolio.invested, { compact: true })}
          subValue={formatPercent(investedPct) + " deployed"}
          icon={<BriefcaseBusiness className="w-4 h-4" />}
        />
        <KpiCard
          title="Cash"
          value={formatCurrency(portfolio.cash, { compact: true })}
          subValue={formatPercent(cashPct) + " available"}
          icon={<DollarSign className="w-4 h-4" />}
        />
        <KpiCard
          title="Unrealized P&L"
          value={formatCurrency(portfolio.unrealizedPnl, { compact: true })}
          delta={portfolio.unrealizedPnlPercent}
          icon={portfolio.unrealizedPnl >= 0 ? <ArrowUpRight className="w-4 h-4" /> : <ArrowDownRight className="w-4 h-4" />}
          variant={portfolio.unrealizedPnl >= 0 ? "gain" : "loss"}
        />
      </div>

      {/* Allocation + Pie */}
      <div className="px-6 mb-6">
        <div className="rounded-xl border border-border bg-card p-5">
          <h3 className="font-semibold text-foreground mb-2">Sector Allocation</h3>
          <p className="text-xs text-muted-foreground mb-5">
            Breakdown of deployed capital across sectors
          </p>
          <AllocationPieChart
            data={portfolio.sectorAllocations}
            height={260}
          />
        </div>
      </div>

      {/* Positions Table */}
      <div className="px-6">
        <div className="rounded-xl border border-border bg-card overflow-hidden">
          <div className="flex items-center justify-between px-5 py-4 border-b border-border">
            <h3 className="font-semibold text-foreground">
              Open Positions
              <span className="ml-2 text-sm font-normal text-muted-foreground">
                ({portfolio.openPositions})
              </span>
            </h3>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-border bg-muted/30">
                  {[
                    { label: "Symbol", align: "left", cl: "pl-5 pr-3" },
                    { label: "Sector", align: "left", cl: "px-3 hidden sm:table-cell" },
                    { label: "Price", align: "right", cl: "px-3" },
                    { label: "Qty / Held", align: "right", cl: "px-3" },
                    { label: "Value", align: "right", cl: "px-3 hidden md:table-cell" },
                    { label: "Unrealized P&L", align: "right", cl: "px-3" },
                    { label: "Stop Loss", align: "right", cl: "px-3 hidden lg:table-cell" },
                    { label: "Target", align: "right", cl: "pl-3 pr-5 hidden xl:table-cell" },
                  ].map(({ label, cl }) => (
                    <th
                      key={label}
                      className={cn(
                        "text-left text-[11px] font-semibold uppercase tracking-wide text-muted-foreground py-3",
                        cl
                      )}
                    >
                      {label}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {portfolio.positions.map((position) => (
                  <PositionRow key={position.id} position={position} />
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}
