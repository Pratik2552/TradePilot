"""
TradePilot — Scanner Schemas

Matches frontend TypeScript types:
    ScanResult, ScannerSummary, ScannerFilters, WatchlistItem
"""

from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel


class ScanResult(BaseModel):
    id: str
    strategyId: str
    symbol: str
    companyName: str = ""
    exchange: str = "NSE"
    sector: str = ""
    industry: str = ""

    # Signal
    crossoverType: str = "golden"
    scanStatus: str = "fresh"
    signalStrength: str = "moderate"
    scannedAt: str = ""

    # Price data
    currentPrice: float = 0
    dayChangePercent: float = 0
    weekChangePercent: float = 0
    volume: float = 0
    avgVolume: float = 0
    volumeRatio: float = 0

    # EMA data
    ema50: float = 0
    ema200: float = 0
    ema50ema200Gap: float = 0
    crossoverDate: Optional[str] = None

    # Risk / Entry
    suggestedEntry: float = 0
    suggestedStopLoss: float = 0
    suggestedTarget: float = 0
    riskRewardRatio: float = 0

    # Links (extra — not in TS but useful)
    tradingViewUrl: Optional[str] = None
    screenerUrl: Optional[str] = None

    # Watchlist
    isWatchlisted: bool = False
    hasAlert: bool = False
    notes: Optional[str] = None


class ScannerSummary(BaseModel):
    totalResults: int = 0
    freshCrossovers: int = 0
    existingSignals: int = 0
    addedToWatchlist: int = 0
    lastScanAt: str = ""
    scannedSymbols: int = 0


class WatchlistItem(BaseModel):
    symbol: str
    companyName: str = ""
    addedAt: str = ""
    currentPrice: float = 0
    dayChangePercent: float = 0


class ToggleWatchlistResponse(BaseModel):
    isWatchlisted: bool
    symbol: str


class RunScanRequest(BaseModel):
    """Optional config overrides when triggering a scan."""
    goldenCrossLookback: Optional[int] = None
