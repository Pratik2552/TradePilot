"""
TradePilot — Domain Events

Strategies emit events. Events power notifications, WebSocket feeds,
audit logs, and analytics pipelines. The event bus is in-memory today
and can be swapped to Redis Pub/Sub or Kafka tomorrow.

Event Taxonomy:
    Scanner:   ScanStarted, ScanCompleted, ScanFailed, SignalFound
    Backtest:  BacktestStarted, BacktestCompleted, BacktestFailed
    Trade:     TradeOpened, TradeClosed, StopLossTriggered, GapExit
    Portfolio: PortfolioUpdated
    System:    EngineReady, EngineError
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


def _now() -> datetime:
    return datetime.now(timezone.utc)


@dataclass
class DomainEvent:
    """Base class for all domain events."""
    event_type: str
    strategy_id: str
    user_id: str = "default"
    occurred_at: datetime = field(default_factory=_now)
    payload: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "event_type": self.event_type,
            "strategy_id": self.strategy_id,
            "user_id": self.user_id,
            "occurred_at": self.occurred_at.isoformat(),
            "payload": self.payload,
        }


# ==============================================================
# Scanner Events
# ==============================================================

@dataclass
class ScanStarted(DomainEvent):
    event_type: str = "scanner.started"


@dataclass
class ScanCompleted(DomainEvent):
    event_type: str = "scanner.completed"


@dataclass
class ScanFailed(DomainEvent):
    event_type: str = "scanner.failed"


@dataclass
class SignalFound(DomainEvent):
    event_type: str = "scanner.signal_found"


# ==============================================================
# Backtest Events
# ==============================================================

@dataclass
class BacktestStarted(DomainEvent):
    event_type: str = "backtest.started"


@dataclass
class BacktestCompleted(DomainEvent):
    event_type: str = "backtest.completed"


@dataclass
class BacktestFailed(DomainEvent):
    event_type: str = "backtest.failed"


# ==============================================================
# Trade Events
# ==============================================================

@dataclass
class TradeOpened(DomainEvent):
    event_type: str = "trade.opened"


@dataclass
class TradeClosed(DomainEvent):
    event_type: str = "trade.closed"


@dataclass
class StopLossTriggered(DomainEvent):
    event_type: str = "trade.stop_loss"


@dataclass
class GapExit(DomainEvent):
    event_type: str = "trade.gap_exit"


@dataclass
class DeathCrossConfirmed(DomainEvent):
    event_type: str = "trade.death_cross"


# ==============================================================
# Analytics Events
# ==============================================================

@dataclass
class AnalyticsUpdated(DomainEvent):
    event_type: str = "analytics.updated"
