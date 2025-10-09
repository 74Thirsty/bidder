"""Base plugin definition for trade-specific bid computations."""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, List


class BaseTradePlugin(ABC):
    """Abstract interface every trade plugin must implement."""

    trade_name: str

    @abstractmethod
    async def normalize_data(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize incoming job payload."""

    @abstractmethod
    async def fetch_public_data(self, normalized_payload: Dict[str, Any]) -> Dict[str, Any]:
        """Fetch auxiliary data from public APIs."""

    @abstractmethod
    async def compute_bid(self, enriched_payload: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate the canonical bid output."""

    @abstractmethod
    async def generate_instructions(self, bid_payload: Dict[str, Any]) -> List[str]:
        """Create a step-by-step instruction list."""

    @abstractmethod
    async def export_bid_report(self, bid_payload: Dict[str, Any]) -> Dict[str, Any]:
        """Return the final payload conforming to the canonical schema."""
