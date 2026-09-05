"use client";

import { useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  ScanLine,
  BriefcaseBusiness,
  BarChart3,
  LineChart,
  Settings2,
  ChevronLeft,
  ChevronRight,
  TrendingUp,
  Zap,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { ROUTES } from "@/lib/constants";

// ---- Types -----------------------------------------------------------------

interface NavItem {
  label: string;
  href: string;
  icon: React.ComponentType<{ className?: string }>;
  badge?: number;
}

interface StrategySidebarProps {
  strategyId: string;
  strategyName?: string;
}

// ---- Nav config ------------------------------------------------------------

function getNavItems(strategyId: string): NavItem[] {
  return [
    {
      label: "Overview",
      href: ROUTES.STRATEGY_OVERVIEW(strategyId),
      icon: LayoutDashboard,
    },
    {
      label: "Scanner",
      href: ROUTES.STRATEGY_SCANNER(strategyId),
      icon: ScanLine,
    },
    {
      label: "Portfolio",
      href: ROUTES.STRATEGY_PORTFOLIO(strategyId),
      icon: BriefcaseBusiness,
    },
    {
      label: "Trades",
      href: ROUTES.STRATEGY_TRADES(strategyId),
      icon: BarChart3,
    },
    {
      label: "Analytics",
      href: ROUTES.STRATEGY_ANALYTICS(strategyId),
      icon: LineChart,
    },
    {
      label: "Settings",
      href: ROUTES.STRATEGY_SETTINGS(strategyId),
      icon: Settings2,
    },
  ];
}

// ---- Component -------------------------------------------------------------

export default function StrategySidebar({
  strategyId,
  strategyName = "Golden Cross",
}: StrategySidebarProps) {
  const [collapsed, setCollapsed] = useState(false);
  const pathname = usePathname();
  const navItems = getNavItems(strategyId);

  return (
    <aside
      className={cn(
        "relative flex flex-col h-screen bg-sidebar border-r border-sidebar-border",
        "transition-all duration-300 ease-in-out shrink-0",
        collapsed ? "w-[68px]" : "w-[220px]"
      )}
    >
      {/* Logo / Brand */}
      <div className="flex items-center gap-3 px-4 h-16 border-b border-sidebar-border overflow-hidden">
        <div className="flex items-center justify-center w-9 h-9 rounded-lg bg-primary/10 shrink-0">
          <Zap className="w-5 h-5 text-primary" />
        </div>

        {!collapsed && (
          <div className="overflow-hidden">
            <p className="text-xs font-semibold text-muted-foreground uppercase tracking-widest leading-none mb-0.5">
              Strategy
            </p>
            <p className="text-sm font-bold text-foreground truncate leading-none">
              {strategyName}
            </p>
          </div>
        )}
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-2 py-4 space-y-1 overflow-y-auto">
        {navItems.map((item) => {
          const isActive = pathname === item.href || pathname.startsWith(item.href + "/");
          const Icon = item.icon;

          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                "relative flex items-center gap-3 px-3 py-2.5 rounded-lg",
                "text-sm font-medium transition-all duration-150 group",
                "overflow-hidden",
                isActive
                  ? "bg-primary/10 text-primary"
                  : "text-muted-foreground hover:bg-accent hover:text-accent-foreground"
              )}
              title={collapsed ? item.label : undefined}
            >
              {/* Active indicator */}
              {isActive && (
                <span className="absolute left-0 top-1/2 -translate-y-1/2 w-0.5 h-5 bg-primary rounded-r-full" />
              )}

              <Icon
                className={cn(
                  "w-5 h-5 shrink-0 transition-colors",
                  isActive ? "text-primary" : "text-muted-foreground group-hover:text-foreground"
                )}
              />

              {!collapsed && (
                <span className="truncate leading-none">{item.label}</span>
              )}

              {/* Badge */}
              {!collapsed && item.badge !== undefined && item.badge > 0 && (
                <span className="ml-auto text-[11px] font-semibold bg-primary/10 text-primary px-1.5 py-0.5 rounded-full">
                  {item.badge}
                </span>
              )}
            </Link>
          );
        })}
      </nav>

      {/* Back to Home */}
      <div className="px-2 pb-2 border-t border-sidebar-border pt-2">
        <Link
          href={ROUTES.HOME}
          className={cn(
            "flex items-center gap-3 px-3 py-2.5 rounded-lg",
            "text-sm font-medium text-muted-foreground",
            "hover:bg-accent hover:text-accent-foreground transition-all duration-150",
            "overflow-hidden"
          )}
          title={collapsed ? "All Strategies" : undefined}
        >
          <TrendingUp className="w-5 h-5 shrink-0" />
          {!collapsed && <span className="truncate">All Strategies</span>}
        </Link>
      </div>

      {/* Collapse Toggle */}
      <button
        onClick={() => setCollapsed((c) => !c)}
        aria-label={collapsed ? "Expand sidebar" : "Collapse sidebar"}
        className={cn(
          "absolute -right-3 top-20 z-10",
          "w-6 h-6 rounded-full border border-sidebar-border bg-sidebar",
          "flex items-center justify-center",
          "text-muted-foreground hover:text-foreground",
          "transition-colors duration-150 shadow-sm"
        )}
      >
        {collapsed ? (
          <ChevronRight className="w-3.5 h-3.5" />
        ) : (
          <ChevronLeft className="w-3.5 h-3.5" />
        )}
      </button>
    </aside>
  );
}
