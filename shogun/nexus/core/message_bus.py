"""Nexus in-memory message bus module."""

from __future__ import annotations

import logging
from collections import defaultdict
from typing import Any, Callable, Coroutine

logger = logging.getLogger(__name__)

# Type definition for async event handlers
EventHandler = Callable[[str, Any], Coroutine[Any, Any, None]]


class MessageBus:
    """Simple asynchronous in-memory pub-sub message bus."""

    def __init__(self):
        self._handlers: dict[str, list[EventHandler]] = defaultdict(list)

    def subscribe(self, event_type: str, handler: EventHandler) -> None:
        """Register a handler for a specific event type."""
        self._handlers[event_type].append(handler)
        logger.debug("MessageBus: subscribed handler to event '%s'", event_type)

    def unsubscribe(self, event_type: str, handler: EventHandler) -> None:
        """Remove a handler registration."""
        if handler in self._handlers[event_type]:
            self._handlers[event_type].remove(handler)
            logger.debug("MessageBus: unsubscribed handler from event '%s'", event_type)

    async def publish(self, event_type: str, data: Any) -> None:
        """Asynchronously publish an event to all registered subscribers."""
        logger.info("MessageBus: publishing event '%s'", event_type)
        handlers = self._handlers[event_type] + self._handlers["*"]
        
        for handler in handlers:
            try:
                await handler(event_type, data)
            except Exception as exc:
                logger.error(
                    "MessageBus: error in handler %s for event '%s': %s",
                    handler.__name__ if hasattr(handler, "__name__") else "unnamed",
                    event_type,
                    exc,
                    exc_info=True
                )


# Global singleton instance
message_bus = MessageBus()
