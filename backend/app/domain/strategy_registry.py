"""
TradePilot — Strategy Plugin Registry

Auto-discovers all strategy plugins from the strategies/ directory.
Each plugin folder must contain a manifest.yaml and a strategy.py
with a class that subclasses BaseStrategy.

Usage:
    registry = get_strategy_registry()
    manifests = registry.list_manifests()
    golden = registry.get_manifest("golden-cross")

Adding a new strategy requires ZERO changes here.
Just drop a new folder under app/strategies/ with manifest.yaml.
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List

import yaml

from app.domain.strategy_manifest import (
    StrategyManifest,
    ParameterSpec,
    SupportedFeatures,
)
from app.core.logging import get_logger

logger = get_logger(__name__)

# Absolute path to the strategies directory
STRATEGIES_DIR = Path(__file__).resolve().parent.parent / "strategies"


def _parse_parameter(raw: dict) -> ParameterSpec:
    return ParameterSpec(
        key=raw["key"],
        label=raw.get("label", raw["key"]),
        type=raw.get("type", "number"),
        default=raw.get("default"),
        description=raw.get("description", ""),
        min=raw.get("min"),
        max=raw.get("max"),
        options=raw.get("options", []),
        required=raw.get("required", True),
    )


def _parse_features(raw: dict) -> SupportedFeatures:
    return SupportedFeatures(
        scanner=raw.get("scanner", False),
        backtester=raw.get("backtester", False),
        optimizer=raw.get("optimizer", False),
        paper_trading=raw.get("paper_trading", False),
        live_trading=raw.get("live_trading", False),
        portfolio=raw.get("portfolio", False),
        analytics=raw.get("analytics", False),
    )


def _load_manifest(manifest_path: Path) -> StrategyManifest | None:
    try:
        with open(manifest_path, "r", encoding="utf-8") as f:
            raw = yaml.safe_load(f)

        parameters = [_parse_parameter(p) for p in raw.get("parameters", [])]
        features = _parse_features(raw.get("supported_features", {}))

        return StrategyManifest(
            id=raw["id"],
            name=raw["name"],
            description=raw.get("description", ""),
            version=raw.get("version", "1.0.0"),
            long_description=raw.get("long_description", ""),
            category=raw.get("category", "trend_following"),
            author=raw.get("author", "TradePilot"),
            tags=raw.get("tags", []),
            universe=raw.get("universe", "NSE"),
            exchange=raw.get("exchange", "NSE"),
            timeframe=raw.get("timeframe", "1D"),
            parameters=parameters,
            supported_features=features,
        )
    except Exception as exc:
        logger.error(
            f"Failed to load manifest from {manifest_path}: {exc}"
        )
        return None


class StrategyRegistry:
    """
    Auto-discovering registry of all installed strategy plugins.
    Scans app/strategies/ at startup. Thread-safe read-after-initialization.
    """

    def __init__(self) -> None:
        self._manifests: Dict[str, StrategyManifest] = {}
        self._discover()

    def _discover(self) -> None:
        """Walk strategies/ and load every manifest.yaml found."""
        if not STRATEGIES_DIR.exists():
            logger.warning(f"Strategies directory not found: {STRATEGIES_DIR}")
            return

        for strategy_dir in sorted(STRATEGIES_DIR.iterdir()):
            if not strategy_dir.is_dir():
                continue
            if strategy_dir.name.startswith("_"):
                continue

            manifest_path = strategy_dir / "manifest.yaml"
            if not manifest_path.exists():
                logger.warning(
                    f"Strategy folder '{strategy_dir.name}' has no manifest.yaml — skipping."
                )
                continue

            manifest = _load_manifest(manifest_path)
            if manifest is None:
                continue

            self._manifests[manifest.id] = manifest
            logger.info(
                f"Registered strategy: [{manifest.id}] {manifest.name} v{manifest.version}"
            )

        logger.info(
            f"Strategy registry loaded {len(self._manifests)} plugin(s): "
            f"{list(self._manifests.keys())}"
        )

    def list_manifests(self) -> List[StrategyManifest]:
        return list(self._manifests.values())

    def get_manifest(self, strategy_id: str) -> StrategyManifest | None:
        return self._manifests.get(strategy_id)

    def exists(self, strategy_id: str) -> bool:
        return strategy_id in self._manifests

    @property
    def strategy_ids(self) -> List[str]:
        return list(self._manifests.keys())


# ---- Singleton -----------------------------------------------------------

_registry: StrategyRegistry | None = None


def get_strategy_registry() -> StrategyRegistry:
    global _registry
    if _registry is None:
        _registry = StrategyRegistry()
    return _registry
