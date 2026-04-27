"""
`tradingagents.graph` package.

This package is used both at runtime (LangGraph + LangChain dependencies) and in
lightweight unit tests that may not have those optional dependencies installed.

To keep `import tradingagents.graph.*` cheap and robust, we avoid importing
heavy modules at package import time and instead lazy-load via `__getattr__`.
"""

from __future__ import annotations

from importlib import import_module
from typing import Any

__all__ = ["TradingAgentsGraph", "ConditionalLogic", "GraphSetup", "Propagator", "Reflector", "SignalProcessor"]


def __getattr__(name: str) -> Any:  # pragma: no cover
    if name == "TradingAgentsGraph":
        return import_module(".trading_graph", __name__).TradingAgentsGraph
    if name == "ConditionalLogic":
        return import_module(".conditional_logic", __name__).ConditionalLogic
    if name == "GraphSetup":
        return import_module(".setup", __name__).GraphSetup
    if name == "Propagator":
        return import_module(".propagation", __name__).Propagator
    if name == "Reflector":
        return import_module(".reflection", __name__).Reflector
    if name == "SignalProcessor":
        return import_module(".signal_processing", __name__).SignalProcessor
    raise AttributeError(name)
