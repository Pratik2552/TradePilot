"""
TradePilot — Trade Schemas

Matches frontend TypeScript types:
    Trade, TradeSummary, TradeFilters
"""

from __future__ import annotations

from typing import Dict, List, Optional

from pydantic import BaseModel


class Trade(BaseModel):
    id: str
    strategyId: str
    symbol: str
    companyName: str = ""
    exchange: str = "NSE"
    direction: str = "long"
    status: str = "closed"

    # Entry
    entryDate: str
    entryPrice: float
    quantity: float = 0
    entryValue: float = 0

    # Exit
    exitDate: Optional[str] = None
    exitPrice: Optional[float] = None
    exitReason: Optional[str] = None

    # P&L
    pnl: Optional[float] = None
    pnlPercent: Optional[float] = None
    holdingDays: Optional[int] = None

    # Risk
    stopLoss: float = 0
    target: float = 0
    riskRewardRatio: float = 0

    # Meta
    ema50AtEntry: float = 0
    ema200AtEntry: float = 0
    volumeAtEntry: float = 0

    # Engine extras (not in TS but informative)
    mfe: Optional[float] = None
    mae: Optional[float] = None
    highestGap: Optional[float] = None
    exitGapPercent: Optional[float] = None

    notes: Optional[str] = None


class TradeSummary(BaseModel):
    totalTrades: int = 0
    openTrades: int = 0
    closedTrades: int = 0
    winners: int = 0
    losers: int = 0
    winRate: float = 0
    avgWin: float = 0
    avgLoss: float = 0
    profitFactor: float = 0
    totalPnl: float = 0
    largestWin: float = 0
    largestLoss: float = 0
    avgHoldingDays: float = 0
    exitReasonBreakdown: Dict[str, int] = {}
