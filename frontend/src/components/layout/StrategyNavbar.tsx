"use client";

import { useState } from "react";
import { Search, Bell, Sun, Moon, User, ChevronDown } from "lucide-react";
import { cn } from "@/lib/utils";
import { slugToTitle } from "@/lib/utils";
import { APP_TAGLINE } from "@/lib/constants";

// ---- Types -----------------------------------------------------------------

interface StrategyNavbarProps {
  strategyId: string;
  strategyName?: string;
  currentPageLabel?: string;
}

// ---- Component -------------------------------------------------------------

export default function StrategyNavbar({
  strategyId: _strategyId,
  strategyName = "Golden Cross",
  currentPageLabel,
}: StrategyNavbarProps) {
  const [isDark, setIsDark] = useState(true);
  const [searchValue, setSearchValue] = useState("");
  const [hasNotifications] = useState(true);

  const toggleTheme = () => {
    setIsDark((d) => !d);
    document.documentElement.classList.toggle("dark");
  };

  return (
    <header className="h-16 border-b border-border bg-background/80 backdrop-blur-sm shrink-0 flex items-center px-6 gap-4 sticky top-0 z-30">

      {/* Breadcrumb */}
      <div className="flex items-center gap-2 text-sm min-w-0 mr-auto">
        <span className="font-semibold text-foreground truncate">{strategyName}</span>
        {currentPageLabel && (
          <>
            <ChevronDown className="w-4 h-4 text-muted-foreground rotate-[-90deg] shrink-0" />
            <span className="text-muted-foreground truncate">{currentPageLabel}</span>
          </>
        )}
        <span className="hidden md:block text-xs text-muted-foreground/50 ml-2">
          {APP_TAGLINE}
        </span>
      </div>

      {/* Search */}
      <div className="relative hidden sm:flex items-center w-64">
        <Search className="absolute left-3 w-4 h-4 text-muted-foreground" />
        <input
          type="text"
          placeholder="Search symbol..."
          value={searchValue}
          onChange={(e) => setSearchValue(e.target.value)}
          className={cn(
            "w-full pl-9 pr-4 py-2 text-sm rounded-lg",
            "bg-muted/60 border border-border",
            "text-foreground placeholder:text-muted-foreground",
            "focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary/50",
            "transition-all duration-150"
          )}
        />
        <kbd className="absolute right-3 text-[10px] text-muted-foreground/60 hidden lg:block">
          ⌘K
        </kbd>
      </div>

      {/* Actions */}
      <div className="flex items-center gap-2">

        {/* Notifications */}
        <button
          className={cn(
            "relative p-2 rounded-lg",
            "text-muted-foreground hover:text-foreground hover:bg-accent",
            "transition-colors duration-150"
          )}
          aria-label="Notifications"
        >
          <Bell className="w-5 h-5" />
          {hasNotifications && (
            <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-primary rounded-full" />
          )}
        </button>

        {/* Theme Toggle */}
        <button
          onClick={toggleTheme}
          className={cn(
            "p-2 rounded-lg",
            "text-muted-foreground hover:text-foreground hover:bg-accent",
            "transition-colors duration-150"
          )}
          aria-label="Toggle theme"
        >
          {isDark ? <Sun className="w-5 h-5" /> : <Moon className="w-5 h-5" />}
        </button>

        {/* Profile */}
        <button
          className={cn(
            "flex items-center gap-2 px-3 py-1.5 rounded-lg",
            "text-sm text-muted-foreground hover:text-foreground hover:bg-accent",
            "transition-colors duration-150 border border-border"
          )}
          aria-label="Profile"
        >
          <div className="w-7 h-7 rounded-full bg-primary/10 flex items-center justify-center">
            <User className="w-4 h-4 text-primary" />
          </div>
          <span className="hidden md:block text-sm font-medium text-foreground">
            Pratik
          </span>
        </button>
      </div>
    </header>
  );
}
