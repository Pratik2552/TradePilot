"""
TradePilot — Strategy Schemas

Matches frontend TypeScript types:
    Strategy, StrategyListItem, StrategyConfig, StrategyStats
"""

from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel


class StrategyConfig(BaseModel):
    initialCapital: float = 100_000
    riskPerTrade: float = 2.0
    maxPositions: int = 10
    emaPeriodFast: int = 50
    emaPeriodSlow: int = 200
    stopLossPercent: float = 7.0
    takeProfitPercent: float = 20.0
    scanTimeframe: str = "1D"
    universe: str = "NSE"
    # Engine-specific extensions (not in TS but passed to engine)
    goldenCrossLookback: int = 3
    gapThreshold: float = 0.50
    allocation: float = 0.10


class StrategyStats(BaseModel):
    portfolioValue: float = 0
    capitalDeployed: float = 0
    openPositions: int = 0
    closedTrades: int = 0
    winRate: float = 0
    profitFactor: float = 0
    averageReturn: float = 0
    averageHoldingDays: float = 0
    totalReturn: float = 0
    cagr: float = 0
    sharpeRatio: float = 0
    maxDrawdown: float = 0


class Strategy(BaseModel):
    id: str
    name: str
    description: str
    longDescription: Optional[str] = None
    status: str = "active"
    category: str = "trend_following"
    stocks: int = 0
    lastScan: str = ""
    createdAt: str = ""
    config: StrategyConfig
    stats: StrategyStats
    tags: List[str] = []


class StrategyListItemStats(BaseModel):
    portfolioValue: float = 0
    totalReturn: float = 0
    winRate: float = 0
    openPositions: int = 0


class StrategyListItem(BaseModel):
    id: str
    name: str
    description: str
    status: str
    stocks: int
    lastScan: str
    tags: List[str]
    stats: StrategyListItemStats


class UpdateStrategyConfigRequest(BaseModel):
    initialCapital: Optional[float] = None
    riskPerTrade: Optional[float] = None
    maxPositions: Optional[int] = None
    emaPeriodFast: Optional[int] = None
    emaPeriodSlow: Optional[int] = None
    stopLossPercent: Optional[float] = None
    takeProfitPercent: Optional[float] = None
    scanTimeframe: Optional[str] = None
    universe: Optional[str] = None
    goldenCrossLookback: Optional[int] = None
    gapThreshold: Optional[float] = None
    allocation: Optional[float] = None
