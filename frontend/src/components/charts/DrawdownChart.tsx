"use client";

import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";
import { formatDate, formatPercent } from "@/lib/formatters";
import { CHART_COLORS } from "@/lib/constants";
import type { EquityPoint } from "@/types";
import { cn } from "@/lib/utils";

function CustomTooltip({
  active,
  payload,
  label,
}: {
  active?: boolean;
  payload?: Array<{ name: string; value: number }>;
  label?: string;
}) {
  if (!active || !payload?.length) return null;

  return (
    <div className="rounded-xl border border-border bg-popover px-4 py-3 shadow-xl text-sm">
      <p className="text-xs text-muted-foreground mb-1 font-medium">
        {label ? formatDate(label) : ""}
      </p>
      <p className="font-bold text-loss">
        {formatPercent(payload[0].value, { showSign: true })}
      </p>
    </div>
  );
}

interface DrawdownChartProps {
  data: EquityPoint[];
  className?: string;
  height?: number;
}

export default function DrawdownChart({
  data,
  className,
  height = 200,
}: DrawdownChartProps) {
  if (!data?.length) return null;

  const displayData =
    data.length > 150
      ? data.filter((_, i) => i % Math.ceil(data.length / 150) === 0)
      : data;

  return (
    <div className={cn("w-full", className)}>
      <ResponsiveContainer width="100%" height={height}>
        <AreaChart
          data={displayData}
          margin={{ top: 4, right: 8, left: 0, bottom: 0 }}
        >
          <defs>
            <linearGradient id="drawdownGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor={CHART_COLORS.loss} stopOpacity={0.3} />
              <stop offset="95%" stopColor={CHART_COLORS.loss} stopOpacity={0.05} />
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
            tickFormatter={(v) => `${v.toFixed(1)}%`}
            width={56}
          />

          <Tooltip content={<CustomTooltip />} />

          <Area
            type="monotone"
            dataKey="drawdownPercent"
            stroke={CHART_COLORS.loss}
            strokeWidth={1.5}
            fill="url(#drawdownGradient)"
            dot={false}
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}
