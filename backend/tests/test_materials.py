import asyncio
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.services import materials


def test_resolve_material_costs_uses_baseline(monkeypatch):
    async def fake_search(_query):
        return None

    monkeypatch.setattr(materials, "search_material_price", fake_search)

    costs = asyncio.run(materials.resolve_material_costs(["concrete mix", "unknown item"]))

    assert costs["concrete mix"] > 0
    assert costs["unknown item"] == materials.DEFAULT_MATERIAL_PRICE
