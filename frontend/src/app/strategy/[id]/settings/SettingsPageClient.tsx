"use client";

import { useState } from "react";
import { useStrategy } from "@/hooks/useStrategy";
import PageHeader from "@/components/common/PageHeader";
import { Save, RotateCcw } from "lucide-react";
import { cn } from "@/lib/utils";
import type { StrategyConfig } from "@/types";
import { updateStrategyConfig } from "@/services/api/strategies.api";

// ---- Input ------------------------------------------------------------------

interface FieldProps {
  id: string;
  label: string;
  description?: string;
  type?: "text" | "number";
  value: string | number;
  unit?: string;
  min?: number;
  max?: number;
  onChange: (value: string) => void;
}

function SettingsField({ id, label, description, type = "number", value, unit, min, max, onChange }: FieldProps) {
  return (
    <div>
      <label htmlFor={id} className="block text-sm font-medium text-foreground mb-1">
        {label}
      </label>
      {description && (
        <p className="text-xs text-muted-foreground mb-2">{description}</p>
      )}
      <div className="relative">
        <input
          id={id}
          type={type}
          value={value}
          min={min}
          max={max}
          onChange={(e) => onChange(e.target.value)}
          className={cn(
            "w-full px-4 py-2.5 text-sm rounded-lg",
            "bg-muted/60 border border-border",
            "text-foreground placeholder:text-muted-foreground",
            "focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary/50",
            "transition-all duration-150",
            unit && "pr-14"
          )}
        />
        {unit && (
          <span className="absolute right-3 top-1/2 -translate-y-1/2 text-xs font-medium text-muted-foreground">
            {unit}
          </span>
        )}
      </div>
    </div>
  );
}

// ---- Section ----------------------------------------------------------------

function SettingsSection({ title, description, children }: {
  title: string;
  description?: string;
  children: React.ReactNode;
}) {
  return (
    <div className="rounded-xl border border-border bg-card p-6">
      <div className="mb-5">
        <h3 className="font-semibold text-foreground">{title}</h3>
        {description && <p className="text-xs text-muted-foreground mt-1">{description}</p>}
      </div>
      <div className="space-y-5">{children}</div>
    </div>
  );
}

// ---- Page ------------------------------------------------------------------

interface SettingsPageClientProps {
  strategyId: string;
}

export default function SettingsPageClient({ strategyId }: SettingsPageClientProps) {
  const { strategy, isLoading } = useStrategy(strategyId);
  const [config, setConfig] = useState<StrategyConfig | null>(null);
  const [saved, setSaved] = useState(false);

  // Initialize config from strategy on load
  if (strategy && !config) {
    setConfig({ ...strategy.config });
  }

  const updateConfig = (key: keyof StrategyConfig, value: string) => {
    setConfig((prev) => {
      if (!prev) return prev;
      const numericKeys: (keyof StrategyConfig)[] = [
        "initialCapital", "riskPerTrade", "maxPositions",
        "emaPeriodFast", "emaPeriodSlow", "stopLossPercent", "takeProfitPercent",
        "goldenCrossLookback", "gapThreshold", "allocation",
      ];
      return {
        ...prev,
        [key]: numericKeys.includes(key) ? parseFloat(value) || 0 : value,
      };
    });
    setSaved(false);
  };

  const handleSave = async () => {
    if (!config) return;
    try {
      await updateStrategyConfig(strategyId, config);
      setSaved(true);
      setTimeout(() => setSaved(false), 2000);
    } catch (err) {
      console.error("Failed to save config", err);
    }
  };

  const handleReset = () => {
    if (strategy) {
      setConfig({ ...strategy.config });
      setSaved(false);
    }
  };

  if (isLoading) {
    return (
      <div className="px-6 pt-8 space-y-5">
        <div className="h-8 w-40 bg-muted animate-pulse rounded-lg" />
        <div className="space-y-4">
          {Array.from({ length: 3 }).map((_, i) => (
            <div key={i} className="h-48 bg-muted animate-pulse rounded-xl" />
          ))}
        </div>
      </div>
    );
  }

  if (!config) return null;

  return (
    <div className="pb-8">
      <PageHeader
        title="Settings"
        subtitle={`Configure ${strategy?.name ?? "strategy"} parameters`}
        actions={
          <div className="flex items-center gap-2">
            <button
              onClick={handleReset}
              className={cn(
                "flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium",
                "border border-border bg-card hover:bg-muted text-foreground",
                "transition-colors duration-150"
              )}
            >
              <RotateCcw className="w-4 h-4" />
              Reset
            </button>
            <button
              onClick={handleSave}
              className={cn(
                "flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium",
                "bg-primary text-primary-foreground hover:bg-primary/90",
                "transition-all duration-150",
                saved && "bg-gain hover:bg-gain/90"
              )}
            >
              <Save className="w-4 h-4" />
              {saved ? "Saved!" : "Save Changes"}
            </button>
          </div>
        }
      />

      <div className="px-6 space-y-5 max-w-3xl">

        {/* Capital & Risk */}
        <SettingsSection
          title="Capital & Risk Management"
          description="Define how much capital to deploy and your risk parameters"
        >
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-5">
            <SettingsField
              id="initialCapital"
              label="Initial Capital"
              description="Starting capital for this strategy"
              value={config.initialCapital}
              unit="₹"
              min={0}
              onChange={(v) => updateConfig("initialCapital", v)}
            />
            <SettingsField
              id="riskPerTrade"
              label="Risk Per Trade"
              description="Maximum capital at risk per position"
              value={config.riskPerTrade}
              unit="%"
              min={0.1}
              max={10}
              onChange={(v) => updateConfig("riskPerTrade", v)}
            />
            <SettingsField
              id="maxPositions"
              label="Max Positions"
              description="Maximum concurrent open positions"
              value={config.maxPositions}
              min={1}
              max={100}
              onChange={(v) => updateConfig("maxPositions", v)}
            />
            <SettingsField
              id="stopLossPercent"
              label="Stop Loss"
              description="Maximum loss per trade before exit"
              value={config.stopLossPercent}
              unit="%"
              min={1}
              max={30}
              onChange={(v) => updateConfig("stopLossPercent", v)}
            />
            <SettingsField
              id="takeProfitPercent"
              label="Take Profit"
              description="Target gain percentage for exit"
              value={config.takeProfitPercent}
              unit="%"
              min={1}
              max={100}
              onChange={(v) => updateConfig("takeProfitPercent", v)}
            />
          </div>
        </SettingsSection>

        {/* EMA Settings */}
        <SettingsSection
          title="EMA Configuration"
          description="Configure the EMA periods that define the Golden Cross signal"
        >
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-5">
            <SettingsField
              id="emaPeriodFast"
              label="Fast EMA Period"
              description="Short-term EMA (Golden Cross: EMA50)"
              value={config.emaPeriodFast}
              unit="days"
              min={5}
              max={200}
              onChange={(v) => updateConfig("emaPeriodFast", v)}
            />
            <SettingsField
              id="emaPeriodSlow"
              label="Slow EMA Period"
              description="Long-term EMA (Golden Cross: EMA200)"
              value={config.emaPeriodSlow}
              unit="days"
              min={20}
              max={500}
              onChange={(v) => updateConfig("emaPeriodSlow", v)}
            />
          </div>
        </SettingsSection>

        {/* Scanner Settings */}
        <SettingsSection
          title="Scanner Configuration"
          description="Control which universe of stocks to scan and when"
        >
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-5">
            <div>
              <label htmlFor="universe" className="block text-sm font-medium text-foreground mb-1">
                Scan Universe
              </label>
              <p className="text-xs text-muted-foreground mb-2">Which set of stocks to scan</p>
              <select
                id="universe"
                value={config.universe}
                onChange={(e) => updateConfig("universe", e.target.value)}
                className={cn(
                  "w-full px-4 py-2.5 text-sm rounded-lg",
                  "bg-muted/60 border border-border text-foreground",
                  "focus:outline-none focus:ring-2 focus:ring-primary/50"
                )}
              >
                <option value="NSE_FO">NSE F&O Stocks</option>
                <option value="NSE_EQ">NSE All Equities</option>
                <option value="NIFTY500">NIFTY 500</option>
                <option value="NIFTY200">NIFTY 200</option>
                <option value="NIFTY50">NIFTY 50</option>
              </select>
            </div>
            <div>
              <label htmlFor="scanTimeframe" className="block text-sm font-medium text-foreground mb-1">
                Scan Timeframe
              </label>
              <p className="text-xs text-muted-foreground mb-2">Data resolution for crossover detection</p>
              <select
                id="scanTimeframe"
                value={config.scanTimeframe}
                onChange={(e) => updateConfig("scanTimeframe", e.target.value)}
                className={cn(
                  "w-full px-4 py-2.5 text-sm rounded-lg",
                  "bg-muted/60 border border-border text-foreground",
                  "focus:outline-none focus:ring-2 focus:ring-primary/50"
                )}
              >
                <option value="1D">Daily</option>
                <option value="1W">Weekly</option>
                <option value="1M">Monthly</option>
              </select>
            </div>
          </div>
        </SettingsSection>

      </div>
    </div>
  );
}
