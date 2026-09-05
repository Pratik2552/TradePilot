"use client";

import { useState } from "react";
import { useScanner } from "@/hooks/useScanner";
import PageHeader from "@/components/common/PageHeader";
import {
  Search,
  RefreshCw,
  Star,
  StarOff,
  TrendingUp,
  Zap,
  Activity,
  Clock,
} from "lucide-react";
import {
  formatPercent,
  formatCompactNumber,
  formatRelativeTime,
  formatDate,
} from "@/lib/formatters";
import { cn } from "@/lib/utils";
import type { ScanResult, CrossoverType, SignalStrength } from "@/types";

// ---- Signal Labels ---------------------------------------------------------

const CROSSOVER_LABELS: Record<CrossoverType, string> = {
  golden: "Golden Cross",
  death: "Death Cross",
  approaching_golden: "≈ Golden",
  approaching_death: "≈ Death",
};

const CROSSOVER_COLORS: Record<CrossoverType, string> = {
  golden: "bg-gain/10 text-gain border border-gain/20",
  death: "bg-loss/10 text-loss border border-loss/20",
  approaching_golden: "bg-primary/10 text-primary border border-primary/20",
  approaching_death: "bg-yellow-500/10 text-yellow-400 border border-yellow-500/20",
};

const STRENGTH_COLORS: Record<SignalStrength, string> = {
  strong: "text-gain",
  moderate: "text-yellow-400",
  weak: "text-muted-foreground",
};

const STRENGTH_DOTS: Record<SignalStrength, number> = {
  strong: 3,
  moderate: 2,
  weak: 1,
};

function SignalStrengthIndicator({ strength }: { strength: SignalStrength }) {
  const dots = STRENGTH_DOTS[strength];
  return (
    <div className="flex items-center gap-0.5">
      {[1, 2, 3].map((d) => (
        <span
          key={d}
          className={cn(
            "w-1.5 h-1.5 rounded-full",
            d <= dots ? STRENGTH_COLORS[strength] : "text-muted-foreground/30",
            d <= dots ? "opacity-100" : "opacity-30",
            "bg-current"
          )}
        />
      ))}
    </div>
  );
}

// ---- Scanner Row -----------------------------------------------------------

interface ScannerRowProps {
  result: ScanResult;
  onWatchlist: (symbol: string) => void;
}

function ScannerRow({ result, onWatchlist }: ScannerRowProps) {
  const isDayPositive = result.dayChangePercent >= 0;
  const volRatioHigh = result.volumeRatio >= 1.5;

  return (
    <tr className="border-b border-border hover:bg-muted/30 transition-colors">
      {/* Symbol */}
      <td className="py-3.5 pl-5 pr-3">
        <div>
          <p className="font-bold text-sm text-foreground">{result.symbol}</p>
          <p className="text-xs text-muted-foreground truncate max-w-[140px]">
            {result.companyName}
          </p>
        </div>
      </td>

      {/* Signal */}
      <td className="py-3.5 px-3">
        <div className="flex flex-col gap-1">
          <span
            className={cn(
              "inline-flex px-2 py-0.5 rounded-full text-[11px] font-semibold",
              CROSSOVER_COLORS[result.crossoverType]
            )}
          >
            {CROSSOVER_LABELS[result.crossoverType]}
          </span>
          <SignalStrengthIndicator strength={result.signalStrength} />
        </div>
      </td>

      {/* Price */}
      <td className="py-3.5 px-3 text-right">
        <p className="font-semibold text-sm text-foreground">
          ₹{result.currentPrice.toLocaleString("en-IN")}
        </p>
        <p
          className={cn(
            "text-xs font-medium",
            isDayPositive ? "text-gain" : "text-loss"
          )}
        >
          {formatPercent(result.dayChangePercent, { showSign: true })}
        </p>
      </td>

      {/* EMA Data */}
      <td className="py-3.5 px-3 text-right hidden md:table-cell">
        <p className="text-xs text-muted-foreground">
          EMA50: <span className="text-foreground font-medium">₹{result.ema50.toLocaleString("en-IN", { maximumFractionDigits: 0 })}</span>
        </p>
        <p className="text-xs text-muted-foreground">
          EMA200: <span className="text-foreground font-medium">₹{result.ema200.toLocaleString("en-IN", { maximumFractionDigits: 0 })}</span>
        </p>
      </td>

      {/* Volume */}
      <td className="py-3.5 px-3 text-right hidden lg:table-cell">
        <p className="text-xs font-medium text-foreground">
          {formatCompactNumber(result.volume)}
        </p>
        <p
          className={cn(
            "text-xs",
            volRatioHigh ? "text-gain" : "text-muted-foreground"
          )}
        >
          {result.volumeRatio.toFixed(1)}x avg
        </p>
      </td>

      {/* RSI */}
      <td className="py-3.5 px-3 text-center hidden xl:table-cell">
        {result.rsi14 !== undefined && (
          <span
            className={cn(
              "text-xs font-semibold px-2 py-0.5 rounded",
              result.rsi14 > 70
                ? "text-loss bg-loss/10"
                : result.rsi14 < 30
                  ? "text-gain bg-gain/10"
                  : "text-muted-foreground"
            )}
          >
            {result.rsi14.toFixed(1)}
          </span>
        )}
      </td>

      {/* Sector */}
      <td className="py-3.5 px-3 hidden xl:table-cell">
        <span className="text-xs text-muted-foreground">{result.sector}</span>
      </td>

      {/* Scan date */}
      <td className="py-3.5 px-3 hidden md:table-cell">
        <div className="flex items-center gap-1 text-xs text-muted-foreground">
          <Clock className="w-3 h-3" />
          {result.crossoverDate ? formatDate(result.crossoverDate, { month: "short", day: "numeric" }) : "Today"}
        </div>
      </td>

      {/* Watchlist */}
      <td className="py-3.5 pl-3 pr-5 text-right">
        <button
          onClick={() => onWatchlist(result.symbol)}
          className={cn(
            "p-1.5 rounded-lg transition-colors",
            result.isWatchlisted
              ? "text-primary hover:text-primary/80"
              : "text-muted-foreground hover:text-foreground"
          )}
          title={result.isWatchlisted ? "Remove from watchlist" : "Add to watchlist"}
        >
          {result.isWatchlisted ? (
            <Star className="w-4 h-4 fill-current" />
          ) : (
            <StarOff className="w-4 h-4" />
          )}
        </button>
      </td>
    </tr>
  );
}

// ---- Page ------------------------------------------------------------------

interface ScannerPageClientProps {
  strategyId: string;
}

export default function ScannerPageClient({ strategyId }: ScannerPageClientProps) {
  const { results, summary, isLoading, error, filters, setFilters, toggleWatchlistItem, refetch } =
    useScanner(strategyId);

  const [searchQuery, setSearchQuery] = useState("");

  const handleSearch = (q: string) => {
    setSearchQuery(q);
    setFilters({ ...filters, searchQuery: q });
  };

  if (error && !isLoading && results.length === 0) {
    return (
      <div className="pb-8">
        <PageHeader title="Scanner" subtitle="Market scanner" />
        <div className="px-6 pt-8 text-center">
          <p className="text-muted-foreground">No scan data available. Run a scan first.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="pb-8">
      <PageHeader
        title="Scanner"
        subtitle={
          summary
            ? `${summary.scannedSymbols.toLocaleString()} symbols scanned · Last run ${formatRelativeTime(summary.lastScanAt)}`
            : "Market scanner"
        }
        actions={
          <button
            onClick={refetch}
            className={cn(
              "flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium",
              "bg-primary text-primary-foreground hover:bg-primary/90",
              "transition-colors duration-150"
            )}
          >
            <RefreshCw className={cn("w-4 h-4", isLoading && "animate-spin")} />
            Re-scan
          </button>
        }
      />

      {/* Summary Pills */}
      {summary && (
        <div className="px-6 flex flex-wrap gap-3 mb-6">
          {[
            { icon: Zap, label: "Fresh Crossovers", value: summary.freshCrossovers, color: "text-gain" },
            { icon: Activity, label: "Existing Signals", value: summary.existingSignals, color: "text-primary" },
            { icon: Star, label: "In Watchlist", value: summary.addedToWatchlist, color: "text-yellow-400" },
            { icon: TrendingUp, label: "Total Signals", value: summary.totalResults, color: "text-muted-foreground" },
          ].map(({ icon: Icon, label, value, color }) => (
            <div
              key={label}
              className="flex items-center gap-2.5 px-4 py-2.5 rounded-xl border border-border bg-card"
            >
              <Icon className={cn("w-4 h-4", color)} />
              <div>
                <p className="text-xs text-muted-foreground leading-none">{label}</p>
                <p className="text-base font-bold text-foreground leading-tight mt-0.5">{value}</p>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Search */}
      <div className="px-6 mb-4">
        <div className="relative max-w-sm">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
          <input
            type="text"
            placeholder="Search symbol or company..."
            value={searchQuery}
            onChange={(e) => handleSearch(e.target.value)}
            className={cn(
              "w-full pl-9 pr-4 py-2.5 text-sm rounded-lg",
              "bg-muted/60 border border-border",
              "text-foreground placeholder:text-muted-foreground",
              "focus:outline-none focus:ring-2 focus:ring-primary/50"
            )}
          />
        </div>
      </div>

      {/* Table */}
      <div className="px-6">
        <div className="rounded-xl border border-border bg-card overflow-hidden">
          {isLoading ? (
            <div className="space-y-3 p-5">
              {Array.from({ length: 6 }).map((_, i) => (
                <div key={i} className="h-14 bg-muted animate-pulse rounded-lg" />
              ))}
            </div>
          ) : results.length === 0 ? (
            <div className="flex flex-col items-center py-16 text-muted-foreground">
              <TrendingUp className="w-10 h-10 mb-3 opacity-30" />
              <p className="font-medium">No signals found</p>
              <p className="text-sm mt-1">Try adjusting your filters or run a new scan</p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-border bg-muted/30">
                    <th className="text-left text-[11px] font-semibold uppercase tracking-wide text-muted-foreground py-3 pl-5 pr-3">
                      Symbol
                    </th>
                    <th className="text-left text-[11px] font-semibold uppercase tracking-wide text-muted-foreground py-3 px-3">
                      Signal
                    </th>
                    <th className="text-right text-[11px] font-semibold uppercase tracking-wide text-muted-foreground py-3 px-3">
                      Price
                    </th>
                    <th className="text-right text-[11px] font-semibold uppercase tracking-wide text-muted-foreground py-3 px-3 hidden md:table-cell">
                      EMA Levels
                    </th>
                    <th className="text-right text-[11px] font-semibold uppercase tracking-wide text-muted-foreground py-3 px-3 hidden lg:table-cell">
                      Volume
                    </th>
                    <th className="text-center text-[11px] font-semibold uppercase tracking-wide text-muted-foreground py-3 px-3 hidden xl:table-cell">
                      RSI
                    </th>
                    <th className="text-left text-[11px] font-semibold uppercase tracking-wide text-muted-foreground py-3 px-3 hidden xl:table-cell">
                      Sector
                    </th>
                    <th className="text-left text-[11px] font-semibold uppercase tracking-wide text-muted-foreground py-3 px-3 hidden md:table-cell">
                      Crossover
                    </th>
                    <th className="py-3 pl-3 pr-5" />
                  </tr>
                </thead>
                <tbody>
                  {results.map((result) => (
                    <ScannerRow
                      key={result.id}
                      result={result}
                      onWatchlist={toggleWatchlistItem}
                    />
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
