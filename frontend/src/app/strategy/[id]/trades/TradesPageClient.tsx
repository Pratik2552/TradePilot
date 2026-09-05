"use client";

import { useState } from "react";
import { useTrades, useExportTrades } from "@/hooks/useTrades";
import PageHeader from "@/components/common/PageHeader";
import {
  Search,
  Download,
  ChevronLeft,
  ChevronRight,
  TrendingUp,
  TrendingDown,
} from "lucide-react";
import {
  formatCurrency,
  formatPercent,
  formatDate,
  formatDays,
} from "@/lib/formatters";
import { cn } from "@/lib/utils";
import type { Trade, TradeStatus } from "@/types";

// ---- Status / Direction Badges ---------------------------------------------

function StatusBadge({ status }: { status: TradeStatus }) {
  const styles: Record<TradeStatus, string> = {
    open: "bg-primary/10 text-primary border border-primary/20",
    closed: "bg-muted text-muted-foreground border border-border",
    partial: "bg-yellow-500/10 text-yellow-400 border border-yellow-500/20",
  };

  return (
    <span className={cn("text-[11px] px-2 py-0.5 rounded-full font-semibold capitalize", styles[status])}>
      {status}
    </span>
  );
}

function PnlCell({ trade }: { trade: Trade }) {
  if (trade.status === "open") {
    return <span className="text-sm text-muted-foreground">Open</span>;
  }
  const isWin = (trade.pnlPercent ?? 0) >= 0;
  return (
    <div className="text-right">
      <p className={cn("text-sm font-bold", isWin ? "text-gain" : "text-loss")}>
        {trade.pnl !== undefined
          ? `${isWin ? "+" : ""}${formatCurrency(trade.pnl, { compact: true })}`
          : "-"}
      </p>
      {trade.pnlPercent !== undefined && (
        <p className={cn("text-xs", isWin ? "text-gain/80" : "text-loss/80")}>
          {formatPercent(trade.pnlPercent, { showSign: true })}
        </p>
      )}
    </div>
  );
}

// ---- Page ------------------------------------------------------------------

interface TradesPageClientProps {
  strategyId: string;
}

export default function TradesPageClient({ strategyId }: TradesPageClientProps) {
  const { trades, pagination, isLoading, error, setQuery, setFilters } = useTrades(strategyId);
  const { exportCsv, isExporting } = useExportTrades(strategyId);
  const [searchValue, setSearchValue] = useState("");
  const [currentPage, setCurrentPage] = useState(1);

  const handleSearch = (q: string) => {
    setSearchValue(q);
    setFilters({ symbol: q });
    setCurrentPage(1);
  };

  const handlePageChange = (page: number) => {
    setCurrentPage(page);
    setQuery({ pagination: { page, pageSize: 20 } });
  };

  return (
    <div className="pb-8">
      <PageHeader
        title="Trade History"
        subtitle={`${pagination.total} total trades`}
        actions={
          <button
            onClick={exportCsv}
            disabled={isExporting}
            className={cn(
              "flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium",
              "border border-border bg-card hover:bg-muted",
              "text-foreground transition-colors duration-150"
            )}
          >
            <Download className="w-4 h-4" />
            {isExporting ? "Exporting..." : "Export CSV"}
          </button>
        }
      />

      {/* Search */}
      <div className="px-6 mb-5">
        <div className="relative max-w-sm">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
          <input
            type="text"
            placeholder="Search by symbol..."
            value={searchValue}
            onChange={(e) => handleSearch(e.target.value)}
            className={cn(
              "w-full pl-9 pr-4 py-2.5 text-sm rounded-lg",
              "bg-muted/60 border border-border text-foreground placeholder:text-muted-foreground",
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
              {Array.from({ length: 8 }).map((_, i) => (
                <div key={i} className="h-14 bg-muted animate-pulse rounded-lg" />
              ))}
            </div>
          ) : (
            <>
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b border-border bg-muted/30">
                      {[
                        { l: "Symbol", c: "pl-5 pr-3 text-left" },
                        { l: "Status", c: "px-3 text-left" },
                        { l: "Entry Date", c: "px-3 text-left hidden sm:table-cell" },
                        { l: "Entry Price", c: "px-3 text-right hidden md:table-cell" },
                        { l: "Exit Date", c: "px-3 text-left hidden lg:table-cell" },
                        { l: "Exit Price", c: "px-3 text-right hidden md:table-cell" },
                        { l: "Qty", c: "px-3 text-right hidden sm:table-cell" },
                        { l: "P&L", c: "px-3 text-right" },
                        { l: "Holding", c: "pl-3 pr-5 text-right hidden xl:table-cell" },
                      ].map(({ l, c }) => (
                        <th
                          key={l}
                          className={cn(
                            "text-[11px] font-semibold uppercase tracking-wide text-muted-foreground py-3",
                            c
                          )}
                        >
                          {l}
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {trades.map((trade) => (
                      <tr
                        key={trade.id}
                        className="border-b border-border hover:bg-muted/30 transition-colors"
                      >
                        <td className="py-3.5 pl-5 pr-3">
                          <div className="flex items-center gap-2">
                            {trade.status === "open" ? (
                              <TrendingUp className="w-3.5 h-3.5 text-primary shrink-0" />
                            ) : (trade.pnlPercent ?? 0) >= 0 ? (
                              <TrendingUp className="w-3.5 h-3.5 text-gain shrink-0" />
                            ) : (
                              <TrendingDown className="w-3.5 h-3.5 text-loss shrink-0" />
                            )}
                            <div>
                              <p className="font-bold text-sm text-foreground">{trade.symbol}</p>
                              <p className="text-xs text-muted-foreground">{trade.exchange}</p>
                            </div>
                          </div>
                        </td>
                        <td className="py-3.5 px-3">
                          <StatusBadge status={trade.status} />
                        </td>
                        <td className="py-3.5 px-3 hidden sm:table-cell">
                          <span className="text-sm text-foreground">
                            {formatDate(trade.entryDate, { month: "short", day: "numeric", year: "2-digit" })}
                          </span>
                        </td>
                        <td className="py-3.5 px-3 text-right hidden md:table-cell">
                          <span className="text-sm text-foreground">
                            ₹{trade.entryPrice.toLocaleString("en-IN")}
                          </span>
                        </td>
                        <td className="py-3.5 px-3 hidden lg:table-cell">
                          <span className="text-sm text-foreground">
                            {trade.exitDate
                              ? formatDate(trade.exitDate, { month: "short", day: "numeric", year: "2-digit" })
                              : "—"}
                          </span>
                        </td>
                        <td className="py-3.5 px-3 text-right hidden md:table-cell">
                          <span className="text-sm text-foreground">
                            {trade.exitPrice ? `₹${trade.exitPrice.toLocaleString("en-IN")}` : "—"}
                          </span>
                        </td>
                        <td className="py-3.5 px-3 text-right hidden sm:table-cell">
                          <span className="text-sm text-foreground">{trade.quantity}</span>
                        </td>
                        <td className="py-3.5 px-3 text-right">
                          <PnlCell trade={trade} />
                        </td>
                        <td className="py-3.5 pl-3 pr-5 text-right hidden xl:table-cell">
                          <span className="text-sm text-muted-foreground">
                            {trade.holdingDays !== undefined ? formatDays(trade.holdingDays) : "—"}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              {/* Pagination */}
              <div className="flex items-center justify-between px-5 py-3 border-t border-border">
                <p className="text-xs text-muted-foreground">
                  Showing {(currentPage - 1) * 20 + 1}–{Math.min(currentPage * 20, pagination.total)} of {pagination.total}
                </p>
                <div className="flex items-center gap-2">
                  <button
                    onClick={() => handlePageChange(currentPage - 1)}
                    disabled={currentPage <= 1}
                    className={cn(
                      "p-1.5 rounded-lg border border-border",
                      "text-muted-foreground hover:text-foreground hover:bg-muted",
                      "disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
                    )}
                  >
                    <ChevronLeft className="w-4 h-4" />
                  </button>
                  <span className="text-sm text-foreground font-medium px-2">
                    {currentPage} / {pagination.totalPages}
                  </span>
                  <button
                    onClick={() => handlePageChange(currentPage + 1)}
                    disabled={!pagination.hasMore}
                    className={cn(
                      "p-1.5 rounded-lg border border-border",
                      "text-muted-foreground hover:text-foreground hover:bg-muted",
                      "disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
                    )}
                  >
                    <ChevronRight className="w-4 h-4" />
                  </button>
                </div>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
