"use client";

import { cn } from "@/lib/utils";
import type { ReactNode } from "react";

// ---- Types -----------------------------------------------------------------

interface KpiCardProps {
  title: string;
  value: string;
  subValue?: string;
  delta?: number; // positive = good, negative = bad
  deltaLabel?: string;
  icon?: ReactNode;
  trend?: "up" | "down" | "neutral";
  variant?: "default" | "gain" | "loss" | "brand";
  className?: string;
}

// ---- Component -------------------------------------------------------------

export default function KpiCard({
  title,
  value,
  subValue,
  delta,
  deltaLabel,
  icon,
  variant = "default",
  className,
}: KpiCardProps) {
  const isPositiveDelta = delta !== undefined && delta >= 0;

  return (
    <div
      className={cn(
        "relative rounded-xl border border-border bg-card p-5",
        "flex flex-col gap-3 overflow-hidden",
        "transition-all duration-200 hover:border-border/80",
        className
      )}
    >
      {/* Background glow for branded variant */}
      {variant === "brand" && (
        <div className="absolute inset-0 bg-primary/5 pointer-events-none" />
      )}
      {variant === "gain" && (
        <div className="absolute inset-0 bg-gain/5 pointer-events-none" />
      )}
      {variant === "loss" && (
        <div className="absolute inset-0 bg-loss/5 pointer-events-none" />
      )}

      {/* Header */}
      <div className="flex items-center justify-between">
        <p className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
          {title}
        </p>
        {icon && (
          <div
            className={cn(
              "w-8 h-8 rounded-lg flex items-center justify-center",
              variant === "gain" && "bg-gain/10 text-gain",
              variant === "loss" && "bg-loss/10 text-loss",
              variant === "brand" && "bg-primary/10 text-primary",
              variant === "default" && "bg-muted text-muted-foreground"
            )}
          >
            {icon}
          </div>
        )}
      </div>

      {/* Value */}
      <div className="space-y-0.5">
        <p
          className={cn(
            "text-2xl font-bold tracking-tight",
            variant === "gain" && "text-gain",
            variant === "loss" && "text-loss",
            variant === "brand" && "text-primary",
            variant === "default" && "text-foreground"
          )}
        >
          {value}
        </p>
        {subValue && (
          <p className="text-sm text-muted-foreground">{subValue}</p>
        )}
      </div>

      {/* Delta / Change */}
      {delta !== undefined && (
        <div className="flex items-center gap-1.5">
          <span
            className={cn(
              "text-xs font-semibold px-1.5 py-0.5 rounded-md",
              isPositiveDelta
                ? "bg-gain/10 text-gain"
                : "bg-loss/10 text-loss"
            )}
          >
            {isPositiveDelta ? "+" : ""}
            {delta.toFixed(2)}%
          </span>
          {deltaLabel && (
            <span className="text-xs text-muted-foreground">{deltaLabel}</span>
          )}
        </div>
      )}
    </div>
  );
}
