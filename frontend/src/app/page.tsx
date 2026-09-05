import type { Metadata } from "next";
import {
  TrendingUp,
  Plus,
  Sparkles,
  Shield,
  BarChart2,
  Cpu,
} from "lucide-react";
import StrategyCard from "@/components/cards/StrategyCard";
import { fetchStrategies } from "@/services/api/strategies.api";
import { APP_NAME, APP_DESCRIPTION, APP_TAGLINE } from "@/lib/constants";
import { cn } from "@/lib/utils";

export const metadata: Metadata = {
  title: `${APP_NAME} — ${APP_DESCRIPTION}`,
  description:
    "Professional quantitative trading research platform for Indian markets. Create strategies, run backtests, scan for signals, and analyze portfolio performance.",
};

// ---- Feature Pills ---------------------------------------------------------

const FEATURES = [
  { icon: Sparkles, label: "Strategy Builder" },
  { icon: BarChart2, label: "Backtesting" },
  { icon: Cpu, label: "Market Scanner" },
  { icon: Shield, label: "Risk Analytics" },
];

// ---- Page ------------------------------------------------------------------

export default async function HomePage() {
  let strategies: import("@/types").StrategyListItem[] = [];
  try {
    strategies = await fetchStrategies();
  } catch {
    // Backend not running or no data yet — show empty state
  }

  return (
    <div className="min-h-screen bg-background">

      {/* ---- Top Bar ---- */}
      <header className="border-b border-border px-6 h-16 flex items-center justify-between">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-lg bg-primary/10 flex items-center justify-center">
            <TrendingUp className="w-4 h-4 text-primary" />
          </div>
          <span className="font-bold text-foreground">{APP_NAME}</span>
        </div>
        <div className="text-xs text-muted-foreground hidden sm:block">
          {APP_TAGLINE}
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-6 py-16">

        {/* ---- Hero ---- */}
        <div className="text-center mb-16">

          {/* Platform badge */}
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-primary/10 border border-primary/20 mb-8">
            <Sparkles className="w-3.5 h-3.5 text-primary" />
            <span className="text-xs font-semibold text-primary tracking-wide uppercase">
              Quantitative Research Platform
            </span>
          </div>

          {/* Title */}
          <h1 className="text-5xl sm:text-6xl md:text-7xl font-extrabold tracking-tight text-foreground mb-4 leading-tight">
            <span className="gradient-text-gold">{APP_NAME}</span>
            <br />
            <span className="text-foreground/90">Research Platform</span>
          </h1>

          {/* Tagline */}
          <p className="text-lg text-muted-foreground mb-8 max-w-2xl mx-auto">
            {APP_TAGLINE}
          </p>

          {/* Feature pills */}
          <div className="flex flex-wrap items-center justify-center gap-2 mb-10">
            {FEATURES.map(({ icon: Icon, label }) => (
              <div
                key={label}
                className="flex items-center gap-2 px-3 py-1.5 rounded-full border border-border bg-card text-sm text-muted-foreground"
              >
                <Icon className="w-3.5 h-3.5" />
                {label}
              </div>
            ))}
          </div>

          {/* CTA */}
          <button
            className={cn(
              "inline-flex items-center gap-2 px-6 py-3 rounded-xl",
              "bg-primary text-primary-foreground font-semibold text-sm",
              "hover:bg-primary/90 transition-all duration-200",
              "shadow-lg shadow-primary/20 hover:shadow-primary/30 hover:-translate-y-0.5"
            )}
            aria-label="Create a new strategy"
          >
            <Plus className="w-4 h-4" />
            New Strategy
          </button>
        </div>

        {/* ---- Strategy Grid ---- */}
        <div>
          <div className="flex items-center justify-between mb-6">
            <div>
              <h2 className="text-xl font-bold text-foreground">Your Strategies</h2>
              <p className="text-sm text-muted-foreground mt-0.5">
                {strategies.length} {strategies.length === 1 ? "strategy" : "strategies"}
              </p>
            </div>
          </div>

          <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
            {strategies.map((strategy) => (
              <StrategyCard key={strategy.id} strategy={strategy} />
            ))}
          </div>
        </div>

        {/* ---- Bottom Notice ---- */}
        <div className="mt-16 text-center">
          <p className="text-xs text-muted-foreground/50">
            For research and educational purposes only. Not financial advice.
          </p>
        </div>
      </main>
    </div>
  );
}