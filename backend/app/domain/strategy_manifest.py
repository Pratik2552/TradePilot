"""
TradePilot — Strategy Manifest

Each strategy plugin declares a manifest.yaml that describes itself.
The registry loads these manifests to expose strategy metadata to the API
without hardcoding any strategy-specific knowledge in the backend core.

Manifest fields are the source of truth for:
  - Frontend strategy cards (name, description, tags)
  - Parameter forms (config schema)
  - Feature flags (scanner, backtester, portfolio, etc.)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, List


@dataclass
class ParameterSpec:
    """Describes a single configurable parameter for a strategy."""
    key: str
    label: str
    type: str              # "number", "integer", "string", "boolean"
    default: Any
    description: str = ""
    min: float | None = None
    max: float | None = None
    options: List[str] = field(default_factory=list)  # for type == "select"
    required: bool = True


@dataclass
class SupportedFeatures:
    """Which engine features this strategy plugin supports."""
    scanner: bool = False
    backtester: bool = False
    optimizer: bool = False
    paper_trading: bool = False
    live_trading: bool = False
    portfolio: bool = False
    analytics: bool = False


@dataclass
class StrategyManifest:
    """
    The complete machine-readable description of a strategy plugin.
    Loaded from manifest.yaml inside each strategy's folder.
    """
    id: str                        # kebab-case, e.g. "golden-cross"
    name: str                      # Display name, e.g. "Golden Cross"
    description: str
    version: str = "1.0.0"
    long_description: str = ""
    category: str = "trend_following"
    author: str = "TradePilot"
    tags: List[str] = field(default_factory=list)
    universe: str = "NSE"
    exchange: str = "NSE"
    timeframe: str = "1D"
    parameters: List[ParameterSpec] = field(default_factory=list)
    supported_features: SupportedFeatures = field(
        default_factory=SupportedFeatures
    )

    def get_default_config(self) -> dict[str, Any]:
        """Returns a dict of {key: default_value} for all parameters."""
        return {p.key: p.default for p in self.parameters}

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "longDescription": self.long_description,
            "version": self.version,
            "category": self.category,
            "author": self.author,
            "tags": self.tags,
            "universe": self.universe,
            "exchange": self.exchange,
            "timeframe": self.timeframe,
            "parameters": [
                {
                    "key": p.key,
                    "label": p.label,
                    "type": p.type,
                    "default": p.default,
                    "description": p.description,
                    "min": p.min,
                    "max": p.max,
                    "options": p.options,
                    "required": p.required,
                }
                for p in self.parameters
            ],
            "supportedFeatures": {
                "scanner": self.supported_features.scanner,
                "backtester": self.supported_features.backtester,
                "optimizer": self.supported_features.optimizer,
                "paperTrading": self.supported_features.paper_trading,
                "liveTrading": self.supported_features.live_trading,
                "portfolio": self.supported_features.portfolio,
                "analytics": self.supported_features.analytics,
            },
        }
