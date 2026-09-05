"use client";

import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from "recharts";
import { CHART_COLORS } from "@/lib/constants";
import { formatPercent } from "@/lib/formatters";
import type { ReturnDistributionBucket } from "@/types";
import { cn } from "@/lib/utils";

function CustomTooltip({
  active,
  payload,
  label,
}: {
  active?: boolean;
  payload?: Array<{ value: number; payload: ReturnDistributionBucket }>;
  label?: string;
}) {
  if (!active || !payload?.length) return null;
  const { count, percent } = payload[0].payload;

  return (
    <div className="rounded-xl border border-border bg-popover px-4 py-3 shadow-xl text-sm">
      <p className="font-semibold text-foreground mb-1">{label}</p>
      <p className="text-muted-foreground">{count} trades</p>
      <p className="text-xs text-muted-foreground">{formatPercent(percent)} of all trades</p>
    </div>
  );
}

interface ReturnDistributionChartProps {
  data: ReturnDistributionBucket[];
  className?: string;
  height?: number;
}

export default function ReturnDistributionChart({
  data,
  className,
  height = 220,
}: ReturnDistributionChartProps) {
  if (!data?.length) return null;

  return (
    <div className={cn("w-full", className)}>
      <ResponsiveContainer width="100%" height={height}>
        <BarChart
          data={data}
          margin={{ top: 4, right: 8, left: 0, bottom: 0 }}
          barSize={28}
        >
          <CartesianGrid
            strokeDasharray="3 3"
            stroke={CHART_COLORS.grid}
            vertical={false}
          />
          <XAxis
            dataKey="rangeLabel"
            tick={{ fill: CHART_COLORS.muted, fontSize: 10 }}
            tickLine={false}
            axisLine={false}
            interval={0}
            angle={-30}
            textAnchor="end"
            height={48}
          />
          <YAxis
            tick={{ fill: CHART_COLORS.muted, fontSize: 11 }}
            tickLine={false}
            axisLine={false}
            width={36}
          />
          <Tooltip content={<CustomTooltip />} cursor={{ fill: "rgba(255,255,255,0.04)" }} />
          <Bar dataKey="count" radius={[4, 4, 0, 0]}>
            {data.map((entry, index) => (
              <Cell
                key={index}
                fill={entry.rangeMin >= 0 ? CHART_COLORS.gain : CHART_COLORS.loss}
                fillOpacity={0.85}
              />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
