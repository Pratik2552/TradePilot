"use client";

import {
  PieChart,
  Pie,
  Cell,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from "recharts";
import { formatCompactCurrency, formatPercent } from "@/lib/formatters";
import type { SectorAllocation } from "@/types";
import { cn } from "@/lib/utils";

// ---- Custom Tooltip --------------------------------------------------------

function CustomTooltip({
  active,
  payload,
}: {
  active?: boolean;
  payload?: Array<{ name: string; value: number; payload: SectorAllocation }>;
}) {
  if (!active || !payload?.length) return null;
  const item = payload[0].payload;

  return (
    <div className="rounded-xl border border-border bg-popover px-4 py-3 shadow-xl text-sm">
      <p className="font-semibold text-foreground mb-1">{item.sector}</p>
      <p className="text-muted-foreground">{formatCompactCurrency(item.value)}</p>
      <p className="text-xs text-muted-foreground">{formatPercent(item.percent)} of portfolio</p>
      <p className="text-xs text-muted-foreground">{item.positions} position{item.positions !== 1 ? "s" : ""}</p>
    </div>
  );
}

// ---- Custom Legend ---------------------------------------------------------

function CustomLegend({
  payload,
}: {
  payload?: Array<{ value: string; color: string; payload: { payload: SectorAllocation } }>;
}) {
  if (!payload?.length) return null;

  return (
    <div className="flex flex-col gap-2 pl-4">
      {payload.map((entry) => (
        <div key={entry.value} className="flex items-center gap-2.5 text-xs">
          <span
            className="w-2.5 h-2.5 rounded-full shrink-0"
            style={{ background: entry.color }}
          />
          <span className="text-muted-foreground truncate max-w-[120px]">{entry.value}</span>
          <span className="ml-auto font-semibold text-foreground">
            {formatPercent(entry.payload.payload.percent)}
          </span>
        </div>
      ))}
    </div>
  );
}

// ---- Component -------------------------------------------------------------

interface AllocationPieChartProps {
  data: SectorAllocation[];
  className?: string;
  height?: number;
}

export default function AllocationPieChart({
  data,
  className,
  height = 280,
}: AllocationPieChartProps) {
  if (!data?.length) {
    return (
      <div
        className={cn("flex items-center justify-center text-muted-foreground text-sm", className)}
        style={{ height }}
      >
        No allocation data
      </div>
    );
  }

  return (
    <div className={cn("w-full", className)}>
      <ResponsiveContainer width="100%" height={height}>
        <PieChart>
          <Pie
            data={data}
            cx="38%"
            cy="50%"
            innerRadius="55%"
            outerRadius="80%"
            paddingAngle={2}
            dataKey="percent"
            nameKey="sector"
          >
            {data.map((entry) => (
              <Cell key={entry.sector} fill={entry.color} strokeWidth={0} />
            ))}
          </Pie>
          <Tooltip content={<CustomTooltip />} />
          <Legend
            layout="vertical"
            align="right"
            verticalAlign="middle"
            content={<CustomLegend />}
          />
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
}
