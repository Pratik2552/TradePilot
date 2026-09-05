"""
TradePilot — Analytics Schemas

Matches frontend TypeScript types:
    AnalyticsSnapshot, EquityPoint, DrawdownPeriod,
    MonthlyReturn, RollingMetricPoint,
    ReturnDistributionBucket, HoldingDistributionBucket
"""

from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel


class EquityPoint(BaseModel):
    date: str
    equity: float
    benchmark: Optional[float] = None
    drawdownPercent: float = 0


class DrawdownPeriod(BaseModel):
    startDate: str
    endDate: Optional[str] = None
    peakValue: float
    troughValue: float
    drawdownPercent: float
    recoveryDays: Optional[int] = None


class MonthlyReturn(BaseModel):
    year: int
    month: int
    returnPercent: float
    benchmark: Optional[float] = None


class RollingMetricPoint(BaseModel):
    date: str
    rollingCagr: Optional[float] = None
    rollingSharpe: Optional[float] = None
    rollingSortino: Optional[float] = None
    rollingMaxDrawdown: Optional[float] = None


class ReturnDistributionBucket(BaseModel):
    rangeLabel: str
    rangeMin: float
    rangeMax: float
    count: int
    percent: float


class HoldingDistributionBucket(BaseModel):
    rangeLabel: str
    rangeMin: float
    rangeMax: float
    count: int
    avgReturn: float


class AnalyticsSnapshot(BaseModel):
    strategyId: str
    computedAt: str

    # Core metrics
    totalReturn: float = 0
    cagr: float = 0
    sharpeRatio: float = 0
    sortinoRatio: float = 0
    calmarRatio: float = 0
    maxDrawdown: float = 0
    maxDrawdownDuration: int = 0
    recoveryFactor: float = 0

    # Trade metrics
    totalTrades: int = 0
    winRate: float = 0
    avgWinPercent: float = 0
    avgLossPercent: float = 0
    profitFactor: float = 0
    expectancy: float = 0
    avgHoldingDays: float = 0

    # Risk metrics
    volatilityAnnual: float = 0
    beta: float = 0
    alpha: float = 0
    informationRatio: float = 0

    # Time series
    equityCurve: List[EquityPoint] = []
    drawdownPeriods: List[DrawdownPeriod] = []
    monthlyReturns: List[MonthlyReturn] = []
    rollingMetrics: List[RollingMetricPoint] = []
    returnDistribution: List[ReturnDistributionBucket] = []
    holdingDistribution: List[HoldingDistributionBucket] = []
