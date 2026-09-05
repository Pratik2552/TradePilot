"use client";

import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine,
} from "recharts";
import { formatCompactCurrency, formatDate, formatPercent } from "@/lib/formatters";
import { CHART_COLORS } from "@/lib/constants";
import type { EquityPoint } from "@/types";
import { cn } from "@/lib/utils";

// ---- Custom Tooltip --------------------------------------------------------

interface TooltipPayload {
  name: string;
  value: number;
  color: string;
}

function CustomTooltip({
  active,
  payload,
  label,
}: {
  active?: boolean;
  payload?: TooltipPayload[];
  label?: string;
}) {
  if (!active || !payload?.length) return null;

  const equity = payload.find((p) => p.name === "equity");
  const benchmark = payload.find((p) => p.name === "benchmark");

  return (
    <div className="rounded-xl border border-border bg-popover px-4 py-3 shadow-xl text-sm">
      <p className="text-xs text-muted-foreground mb-2 font-medium">
        {label ? formatDate(label) : ""}
      </p>
      {equity && (
        <div className="flex items-center justify-between gap-6">
          <span className="flex items-center gap-1.5 text-muted-foreground">
            <span className="w-2 h-2 rounded-full bg-primary inline-block" />
            Strategy
          </span>
          <span className="font-bold text-foreground">
            {formatCompactCurrency(equity.value)}
          </span>
        </div>
      )}
      {benchmark && (
        <div className="flex items-center justify-between gap-6 mt-1">
          <span className="flex items-center gap-1.5 text-muted-foreground">
            <span className="w-2 h-2 rounded-full inline-block" style={{ background: CHART_COLORS.benchmark }} />
            NIFTY 50
          </span>
          <span className="font-semibold text-muted-foreground">
            {formatCompactCurrency(benchmark.value)}
          </span>
        </div>
      )}
    </div>
  );
}

// ---- Component -------------------------------------------------------------

interface EquityCurveChartProps {
  data: EquityPoint[];
  showBenchmark?: boolean;
  className?: string;
  height?: number;
}

export default function EquityCurveChart({
  data,
  showBenchmark = true,
  className,
  height = 280,
}: EquityCurveChartProps) {
  if (!data?.length) {
    return (
      <div
        className={cn("flex items-center justify-center text-muted-foreground text-sm rounded-xl border border-border", className)}
        style={{ height }}
      >
        No data available
      </div>
    );
  }

  const initialEquity = data[0]?.equity ?? 0;
  const lastEquity = data[data.length - 1]?.equity ?? 0;
  const isPositive = lastEquity >= initialEquity;

  // Thin data for performance
  const displayData =
    data.length > 150
      ? data.filter((_, i) => i % Math.ceil(data.length / 150) === 0)
      : data;

  return (
    <div className={cn("w-full", className)}>
      <ResponsiveContainer width="100%" height={height}>
        <AreaChart
          data={displayData}
          margin={{ top: 8, right: 8, left: 0, bottom: 0 }}
        >
          <defs>
            <linearGradient id="equityGradient" x1="0" y1="0" x2="0" y2="1">
              <stop
                offset="5%"
                stopColor={isPositive ? CHART_COLORS.primary : CHART_COLORS.loss}
                stopOpacity={0.25}
              />
              <stop
                offset="95%"
                stopColor={isPositive ? CHART_COLORS.primary : CHART_COLORS.loss}
                stopOpacity={0}
              />
            </linearGradient>
            <linearGradient id="benchmarkGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor={CHART_COLORS.benchmark} stopOpacity={0.12} />
              <stop offset="95%" stopColor={CHART_COLORS.benchmark} stopOpacity={0} />
            </linearGradient>
          </defs>

          <CartesianGrid
            strokeDasharray="3 3"
            stroke={CHART_COLORS.grid}
            vertical={false}
          />

          <XAxis
            dataKey="date"
            tick={{ fill: CHART_COLORS.muted, fontSize: 11 }}
            tickLine={false}
            axisLine={false}
            tickFormatter={(v) => formatDate(v, { month: "short", day: "numeric" })}
            interval="preserveStartEnd"
          />

          <YAxis
            tick={{ fill: CHART_COLORS.muted, fontSize: 11 }}
            tickLine={false}
            axisLine={false}
            tickFormatter={(v) => formatCompactCurrency(v)}
            width={72}
          />

          <Tooltip content={<CustomTooltip />} />

          <ReferenceLine
            y={initialEquity}
            stroke={CHART_COLORS.muted}
            strokeDasharray="4 4"
            strokeOpacity={0.4}
          />

          {showBenchmark && (
            <Area
              type="monotone"
              dataKey="benchmark"
              stroke={CHART_COLORS.benchmark}
              strokeWidth={1.5}
              fill="url(#benchmarkGradient)"
              strokeOpacity={0.7}
              dot={false}
              activeDot={false}
            />
          )}

          <Area
            type="monotone"
            dataKey="equity"
            stroke={isPositive ? CHART_COLORS.primary : CHART_COLORS.loss}
            strokeWidth={2}
            fill="url(#equityGradient)"
            dot={false}
            activeDot={{ r: 4, strokeWidth: 2 }}
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}
