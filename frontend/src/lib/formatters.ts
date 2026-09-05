// ============================================================
// Number and Date Formatters
// Golden Cross Research Platform
// ============================================================

const INR_FORMATTER = new Intl.NumberFormat("en-IN", {
  style: "currency",
  currency: "INR",
  minimumFractionDigits: 0,
  maximumFractionDigits: 0,
});

const INR_FORMATTER_DECIMAL = new Intl.NumberFormat("en-IN", {
  style: "currency",
  currency: "INR",
  minimumFractionDigits: 2,
  maximumFractionDigits: 2,
});

const NUMBER_FORMATTER = new Intl.NumberFormat("en-IN", {
  minimumFractionDigits: 0,
  maximumFractionDigits: 2,
});

// ---- Currency ---------------------------------------------------------------

export function formatCurrency(
  value: number,
  options: { decimals?: boolean; compact?: boolean } = {}
): string {
  if (options.compact) {
    return formatCompactCurrency(value);
  }
  return options.decimals
    ? INR_FORMATTER_DECIMAL.format(value)
    : INR_FORMATTER.format(value);
}

export function formatCompactCurrency(value: number): string {
  const abs = Math.abs(value);
  const sign = value < 0 ? "-" : "";

  if (abs >= 1_00_00_000) {
    return `${sign}₹${(abs / 1_00_00_000).toFixed(2)}Cr`;
  }
  if (abs >= 1_00_000) {
    return `${sign}₹${(abs / 1_00_000).toFixed(2)}L`;
  }
  if (abs >= 1_000) {
    return `${sign}₹${(abs / 1_000).toFixed(1)}K`;
  }
  return `${sign}₹${abs.toFixed(0)}`;
}

// ---- Percentage -------------------------------------------------------------

export function formatPercent(
  value: number,
  options: { decimals?: number; showSign?: boolean } = {}
): string {
  const { decimals = 2, showSign = false } = options;
  const formatted = `${Math.abs(value).toFixed(decimals)}%`;
  if (showSign) {
    return value >= 0 ? `+${formatted}` : `-${formatted}`;
  }
  return formatted;
}

export function formatPercentSigned(value: number, decimals = 2): string {
  return formatPercent(value, { decimals, showSign: true });
}

// ---- Numbers ----------------------------------------------------------------

export function formatNumber(value: number, decimals = 2): string {
  return NUMBER_FORMATTER.format(
    parseFloat(value.toFixed(decimals))
  );
}

export function formatCompactNumber(value: number): string {
  const abs = Math.abs(value);
  const sign = value < 0 ? "-" : "";

  if (abs >= 1_00_00_000) return `${sign}${(abs / 1_00_00_000).toFixed(1)}Cr`;
  if (abs >= 1_00_000) return `${sign}${(abs / 1_00_000).toFixed(1)}L`;
  if (abs >= 1_000) return `${sign}${(abs / 1_000).toFixed(1)}K`;
  return `${sign}${abs.toFixed(0)}`;
}

// ---- Dates ------------------------------------------------------------------

export function formatDate(
  isoString: string,
  options: Intl.DateTimeFormatOptions = {
    year: "numeric",
    month: "short",
    day: "numeric",
  }
): string {
  return new Date(isoString).toLocaleDateString("en-IN", options);
}

export function formatDateTime(isoString: string): string {
  return new Date(isoString).toLocaleString("en-IN", {
    year: "numeric",
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

export function formatRelativeTime(isoString: string): string {
  const now = new Date();
  const date = new Date(isoString);
  const diffMs = now.getTime() - date.getTime();
  const diffMins = Math.floor(diffMs / 60_000);
  const diffHours = Math.floor(diffMs / 3_600_000);
  const diffDays = Math.floor(diffMs / 86_400_000);

  if (diffMins < 1) return "Just now";
  if (diffMins < 60) return `${diffMins}m ago`;
  if (diffHours < 24) return `${diffHours}h ago`;
  if (diffDays < 7) return `${diffDays}d ago`;
  return formatDate(isoString);
}

export function formatMonthYear(year: number, month: number): string {
  const date = new Date(year, month - 1);
  return date.toLocaleDateString("en-IN", { year: "numeric", month: "short" });
}

// ---- Ratios / Metrics -------------------------------------------------------

export function formatRatio(value: number, decimals = 2): string {
  return value.toFixed(decimals) + "x";
}

export function formatMultiple(value: number, decimals = 2): string {
  const sign = value >= 0 ? "+" : "";
  return `${sign}${value.toFixed(decimals)}x`;
}

export function formatDays(days: number): string {
  if (days < 1) return "<1 day";
  if (days === 1) return "1 day";
  if (days < 30) return `${Math.round(days)}d`;
  if (days < 365) return `${(days / 30).toFixed(1)}mo`;
  return `${(days / 365).toFixed(1)}yr`;
}
