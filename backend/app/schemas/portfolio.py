"""
TradePilot — Portfolio Schemas

Matches frontend TypeScript types:
    PortfolioSnapshot, Position, SectorAllocation
"""

from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel


class Position(BaseModel):
    id: str
    strategyId: str
    symbol: str
    companyName: str = ""
    exchange: str = "NSE"
    sector: str = ""
    industry: str = ""

    quantity: float = 0
    entryPrice: float = 0
    currentPrice: float = 0
    entryDate: str = ""
    holdingDays: int = 0

    entryValue: float = 0
    currentValue: float = 0

    unrealizedPnl: float = 0
    unrealizedPnlPercent: float = 0

    stopLoss: float = 0
    target: float = 0
    stopLossPercent: float = 0
    targetPercent: float = 0

    allocationPercent: float = 0


class SectorAllocation(BaseModel):
    sector: str
    value: float
    percent: float
    positions: int
    color: str = "#6366f1"


class PortfolioSnapshot(BaseModel):
    snapshotDate: str = ""
    totalValue: float = 0
    cash: float = 0
    invested: float = 0
    unrealizedPnl: float = 0
    unrealizedPnlPercent: float = 0
    dayChange: float = 0
    dayChangePercent: float = 0
    openPositions: int = 0
    sectorAllocations: List[SectorAllocation] = []
    positions: List[Position] = []
