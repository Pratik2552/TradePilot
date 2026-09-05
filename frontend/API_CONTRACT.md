# API_CONTRACT.md — Golden Cross Research Platform

## Overview
All API calls go through the Axios client at `src/services/api/client.ts`.
Base URL: `NEXT_PUBLIC_API_URL` env var (default: `http://localhost:8000`)

## Strategies

### GET /strategies
Returns list of all strategies for the authenticated user.
```typescript
Response: ApiResponse<StrategyListItem[]>
```

### GET /strategies/:id
Returns full strategy details including config and stats.
```typescript
Response: ApiResponse<Strategy>
```

### POST /strategies
Create a new strategy.
```typescript
Body: Omit<Strategy, "id" | "createdAt" | "stats">
Response: ApiResponse<Strategy>
```

### PATCH /strategies/:id/config
Update strategy configuration.
```typescript
Body: Partial<StrategyConfig>
Response: ApiResponse<Strategy>
```

## Trades

### GET /strategies/:id/trades
Paginated trade list with filtering and sorting.
```typescript
Query params: status, symbol, exitReason, dateFrom, dateTo, page, pageSize, sort, dir
Response: ApiResponse<PaginatedResponse<Trade>>
```

### GET /strategies/:id/trades/summary
Trade statistics summary.
```typescript
Response: ApiResponse<TradeSummary>
```

### GET /strategies/:id/trades/export
Export as CSV.
```typescript
Response: Blob (text/csv)
```

## Portfolio

### GET /strategies/:id/portfolio
Current portfolio snapshot with positions and sector allocation.
```typescript
Response: ApiResponse<PortfolioSnapshot>
```

## Scanner

### GET /strategies/:id/scanner
Scan results with filtering and pagination.
```typescript
Query params: crossoverType[], signalStrength[], sector[], exchange[], isWatchlisted, searchQuery, page, pageSize
Response: ApiResponse<PaginatedResponse<ScanResult>>
```

### GET /strategies/:id/scanner/summary
Scanner run summary stats.
```typescript
Response: ApiResponse<ScannerSummary>
```

### POST /strategies/:id/watchlist/:symbol
Toggle watchlist for a symbol.
```typescript
Response: ApiResponse<{ isWatchlisted: boolean }>
```

## Analytics

### GET /strategies/:id/analytics
Full analytics snapshot including all time series data.
```typescript
Response: ApiResponse<AnalyticsSnapshot>
```

## Common Response Format

```typescript
interface ApiResponse<T> {
  data: T;
  message: string;
  success: boolean;
  timestamp: string; // ISO
}

interface PaginatedResponse<T> {
  data: T[];
  total: number;
  page: number;
  pageSize: number;
  totalPages: number;
  hasMore: boolean;
}
```

## Error Format

```typescript
interface ApiError {
  code: string;        // e.g. "STRATEGY_NOT_FOUND"
  message: string;
  details?: Record<string, string[]>;
  statusCode: number;
}
```

## Authentication
All endpoints require `Authorization: Bearer <supabase_jwt>` header.
The Axios client interceptor will attach this automatically once Supabase Auth is integrated.

## Backend Tech Stack (Planned)
- FastAPI (Python)
- PostgreSQL
- Redis (caching scan results)
- Supabase Auth
- Celery (background scan tasks)
