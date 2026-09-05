# ARCHITECTURE.md — Golden Cross Research Platform

## Overview

The Golden Cross Research Platform is a **feature-first, layered Next.js 16 application** designed for production scalability, multi-strategy support, and future backend/live trading integration.

## Architectural Principles

- **Feature-first directory structure** — pages and their client components co-located
- **Strict separation of concerns** — UI → Hooks → Services → API → Types
- **Mock → API ready** — every service function has a `TODO (Backend)` comment pointing to the real endpoint
- **Server/Client component split** — SSR for metadata and data-fetching, client components for interactivity
- **Composition over inheritance** — small, reusable components composed into pages
- **Strong typing everywhere** — no `any`, all domain types in `src/types/`

## Layer Architecture

```
┌─────────────────────────────────────────────────────┐
│                     PAGES (app router)               │
│  Server components → extract params → delegate       │
├─────────────────────────────────────────────────────┤
│                 CLIENT COMPONENTS                    │
│  *PageClient.tsx files — all UI, hooks, interactivity│
├─────────────────────────────────────────────────────┤
│                      HOOKS                           │
│  useStrategy, useTrades, usePortfolio, useScanner,  │
│  useAnalytics — single boundary, manage state       │
├─────────────────────────────────────────────────────┤
│                    SERVICES/API                      │
│  strategies.api.ts, trades.api.ts, etc.             │
│  Currently: returns mock data                       │
│  Future: calls Axios apiClient → FastAPI backend    │
├─────────────────────────────────────────────────────┤
│                    MOCK DATA                         │
│  services/mock/*.mock.ts — realistic NSE data       │
├─────────────────────────────────────────────────────┤
│                      TYPES                           │
│  src/types/*.types.ts — pure TypeScript interfaces  │
└─────────────────────────────────────────────────────┘
```

## Directory Structure

```
frontend/
├── src/
│   ├── app/                          # Next.js App Router
│   │   ├── layout.tsx                # Root layout (Inter font, dark theme)
│   │   ├── globals.css               # Design token CSS
│   │   ├── page.tsx                  # Home / strategy listing
│   │   └── strategy/
│   │       └── [id]/
│   │           ├── layout.tsx        # Strategy shell (sidebar + navbar)
│   │           ├── page.tsx          # Redirect → /overview
│   │           ├── overview/
│   │           │   ├── page.tsx      # Server wrapper
│   │           │   └── OverviewPageClient.tsx
│   │           ├── scanner/
│   │           │   ├── page.tsx
│   │           │   └── ScannerPageClient.tsx
│   │           ├── portfolio/
│   │           │   ├── page.tsx
│   │           │   └── PortfolioPageClient.tsx
│   │           ├── trades/
│   │           │   ├── page.tsx
│   │           │   └── TradesPageClient.tsx
│   │           ├── analytics/
│   │           │   ├── page.tsx
│   │           │   └── AnalyticsPageClient.tsx
│   │           └── settings/
│   │               ├── page.tsx
│   │               └── SettingsPageClient.tsx
│   ├── components/
│   │   ├── layout/
│   │   │   ├── StrategySidebar.tsx   # Collapsible sidebar
│   │   │   └── StrategyNavbar.tsx    # Top navbar
│   │   ├── cards/
│   │   │   ├── KpiCard.tsx           # Generic KPI metric card
│   │   │   └── StrategyCard.tsx      # Home page strategy card
│   │   ├── charts/
│   │   │   ├── EquityCurveChart.tsx  # Area chart + benchmark
│   │   │   ├── DrawdownChart.tsx     # Underwater equity
│   │   │   ├── MonthlyReturnsChart.tsx
│   │   │   ├── ReturnDistributionChart.tsx
│   │   │   └── AllocationPieChart.tsx
│   │   ├── common/
│   │   │   ├── PageHeader.tsx
│   │   │   └── EmptyState.tsx
│   │   └── ui/                       # shadcn/ui components
│   ├── hooks/
│   │   ├── useStrategy.ts
│   │   ├── useTrades.ts
│   │   ├── usePortfolio.ts
│   │   ├── useScanner.ts
│   │   └── useAnalytics.ts
│   ├── services/
│   │   ├── api/
│   │   │   ├── client.ts             # Axios instance
│   │   │   ├── strategies.api.ts
│   │   │   ├── trades.api.ts
│   │   │   ├── portfolio.api.ts
│   │   │   ├── scanner.api.ts
│   │   │   └── analytics.api.ts
│   │   └── mock/
│   │       ├── strategies.mock.ts
│   │       ├── trades.mock.ts
│   │       ├── portfolio.mock.ts
│   │       ├── scanner.mock.ts
│   │       └── analytics.mock.ts
│   ├── types/
│   │   ├── index.ts                  # Barrel export
│   │   ├── strategy.types.ts
│   │   ├── trade.types.ts
│   │   ├── portfolio.types.ts
│   │   ├── scanner.types.ts
│   │   ├── analytics.types.ts
│   │   └── api.types.ts
│   └── lib/
│       ├── utils.ts                  # cn(), helpers
│       ├── formatters.ts             # INR, %, dates, ratios
│       └── constants.ts              # Routes, colors, feature flags
```

## Design System

- **Theme**: Dark by default (`dark` class on `<html>`)
- **Colors**: oklch-based design tokens in globals.css
  - `--primary` = brand blue
  - `--gain` = emerald green (positive P&L)
  - `--loss` = red (negative P&L)
- **Typography**: Inter (Google Fonts)
- **Cards**: `bg-card border-border rounded-xl`
- **Glassmorphism**: `.glass` and `.glass-md` utility classes
- **Gradient text**: `.gradient-text` and `.gradient-text-gold`

## Key Decisions

1. **No top-level Dashboard/Scanner/Portfolio pages** — everything lives inside a strategy
2. **Server/Client split**: SSR pages extract params, client components handle all state
3. **Mock-first**: All APIs return mock data now; replace in one function when backend is ready
4. **Hooks own state**: UI components never call services directly
5. **Formatters are pure functions**: All number/date formatting in `src/lib/formatters.ts`
