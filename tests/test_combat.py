"""Hit, crit, and resist math."""

import random

import pytest

from magesim.core.enums import LevelDelta
from magesim.engine.combat import ResistTable, crit_multiplier, hit_chance, level_delta
from magesim.model.character import Character


@pytest.mark.parametrize(
    ("delta", "expected"),
    [(LevelDelta.SAME, 0.96), (LevelDelta.PLUS_3, 0.83), (LevelDelta.MINUS_3_OR_LESS, 0.99)],
)
def test_hit_chance_by_level(delta: LevelDelta, expected: float) -> None:
    assert hit_chance(delta, 0.0) == pytest.approx(expected)


def test_hit_chance_capped_at_99() -> None:
    assert hit_chance(LevelDelta.SAME, 10.0) == pytest.approx(0.99)


def test_level_delta_clamps() -> None:
    assert level_delta(20, 10) is LevelDelta.MINUS_3_OR_LESS
    assert level_delta(20, 30) is LevelDelta.PLUS_3


def test_crit_multiplier_with_ice_shards() -> None:
    assert crit_multiplier(0.0) == pytest.approx(1.5)
    assert crit_multiplier(1.0) == pytest.approx(2.0)


def test_no_partial_resists_at_same_level() -> None:
    table = ResistTable.for_level_gap(0)
    assert table.roll_multiplier(random.Random(0)) == 1.0


def test_partial_resists_average_two_percent_per_level() -> None:
    table = ResistTable.for_level_gap(3)
    rng = random.Random(0)
    mean = sum(table.roll_multiplier(rng) for _ in range(200_000)) / 200_000
    assert mean == pytest.approx(0.94, abs=0.01)


def test_base_mana_excludes_intellect(rich_mage: Character) -> None:
    assert rich_mage.base_mana == pytest.approx(1_000_000 - (20 + 15 * 30))
