"use client";

import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from "recharts";
import { CHART_COLORS, MONTHS } from "@/lib/constants";
import { formatPercent } from "@/lib/formatters";
import type { MonthlyReturn } from "@/types";
import { cn } from "@/lib/utils";

function CustomTooltip({
  active,
  payload,
  label,
}: {
  active?: boolean;
  payload?: Array<{ value: number }>;
  label?: string;
}) {
  if (!active || !payload?.length) return null;
  const value = payload[0].value;

  return (
    <div className="rounded-xl border border-border bg-popover px-4 py-3 shadow-xl text-sm">
      <p className="text-xs text-muted-foreground mb-1">{label}</p>
      <p className={cn("font-bold", value >= 0 ? "text-gain" : "text-loss")}>
        {formatPercent(value, { showSign: true })}
      </p>
    </div>
  );
}

interface MonthlyReturnsChartProps {
  data: MonthlyReturn[];
  className?: string;
  height?: number;
}

export default function MonthlyReturnsChart({
  data,
  className,
  height = 220,
}: MonthlyReturnsChartProps) {
  if (!data?.length) return null;

  const chartData = data.map((d) => ({
    label: `${MONTHS[d.month - 1]} '${String(d.year).slice(2)}`,
    return: parseFloat(d.returnPercent.toFixed(2)),
  }));

  return (
    <div className={cn("w-full", className)}>
      <ResponsiveContainer width="100%" height={height}>
        <BarChart
          data={chartData}
          margin={{ top: 4, right: 8, left: 0, bottom: 0 }}
          barSize={20}
        >
          <CartesianGrid
            strokeDasharray="3 3"
            stroke={CHART_COLORS.grid}
            vertical={false}
          />
          <XAxis
            dataKey="label"
            tick={{ fill: CHART_COLORS.muted, fontSize: 11 }}
            tickLine={false}
            axisLine={false}
          />
          <YAxis
            tick={{ fill: CHART_COLORS.muted, fontSize: 11 }}
            tickLine={false}
            axisLine={false}
            tickFormatter={(v) => `${v}%`}
            width={44}
          />
          <Tooltip content={<CustomTooltip />} cursor={{ fill: "rgba(255,255,255,0.04)" }} />
          <Bar dataKey="return" radius={[4, 4, 0, 0]}>
            {chartData.map((entry, index) => (
              <Cell
                key={index}
                fill={entry.return >= 0 ? CHART_COLORS.gain : CHART_COLORS.loss}
                fillOpacity={0.85}
              />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
