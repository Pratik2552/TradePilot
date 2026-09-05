"""
TradePilot — In-Memory Event Bus

Strategies emit events → registered handlers receive them.
Today: synchronous, in-process, in-memory.
Tomorrow: swap to AsyncIO or Redis Streams without changing emitters.

Usage:
    bus = get_event_bus()
    bus.subscribe("scanner.completed", my_handler)
    bus.publish(ScanCompleted(strategy_id="golden-cross", payload={"found": 12}))
"""

from __future__ import annotations

import asyncio
from collections import defaultdict
from typing import Callable, Awaitable

from app.domain.events import DomainEvent
from app.core.logging import get_logger

logger = get_logger(__name__)

# Type alias for event handlers
EventHandler = Callable[[DomainEvent], Awaitable[None] | None]


class EventBus:
    """
    Simple pub/sub event bus. Supports both sync and async handlers.
    """

    def __init__(self) -> None:
        self._handlers: dict[str, list[EventHandler]] = defaultdict(list)

    def subscribe(self, event_type: str, handler: EventHandler) -> None:
        """Register a handler for a specific event type."""
        self._handlers[event_type].append(handler)
        logger.debug(f"EventBus: subscribed handler for '{event_type}'")

    def subscribe_all(self, handler: EventHandler) -> None:
        """Register a handler that receives ALL events."""
        self.subscribe("*", handler)

    async def publish(self, event: DomainEvent) -> None:
        """
        Publish an event to all registered handlers.
        Handlers for the specific event type AND wildcard '*' handlers are called.
        """
        handlers = (
            self._handlers.get(event.event_type, [])
            + self._handlers.get("*", [])
        )

        for handler in handlers:
            try:
                result = handler(event)
                if asyncio.iscoroutine(result):
                    await result
            except Exception as exc:
                logger.error(
                    f"EventBus: handler error for '{event.event_type}'",
                    extra={"error": str(exc)},
                )

    def publish_sync(self, event: DomainEvent) -> None:
        """
        Synchronous publish — use in non-async contexts (e.g. background threads).
        Creates a new event loop if needed.
        """
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                loop.create_task(self.publish(event))
            else:
                loop.run_until_complete(self.publish(event))
        except RuntimeError:
            asyncio.run(self.publish(event))


# ---- Singleton -----------------------------------------------------------

_event_bus: EventBus | None = None


def get_event_bus() -> EventBus:
    global _event_bus
    if _event_bus is None:
        _event_bus = EventBus()
    return _event_bus
