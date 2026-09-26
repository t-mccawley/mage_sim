"""Shared test fixtures."""

import pytest

from magesim import (
    Character,
    DotData,
    Encounter,
    EncounterType,
    LevelDelta,
    SchoolValues,
    SpellId,
    SpellRank,
)
from magesim.spells.definitions import SpellCatalog
from magesim.spells.mechanics import build_catalog


@pytest.fixture
def catalog() -> SpellCatalog:
    """Small spellbook independent of configs/spellbook.py."""
    return build_catalog(
        {
            SpellId.FIREBALL: [
                SpellRank(
                    rank=4,
                    level=18,
                    min_damage=67,
                    max_damage=90,
                    mana_cost=95,
                    cast_time=3.0,
                    dot=DotData(damage=12, duration=8, ticks=4),
                ),
            ],
            SpellId.FIRE_BLAST: [
                SpellRank(rank=2, level=14, min_damage=57, max_damage=69, mana_cost=75, cooldown=8),
            ],
            SpellId.PYROBLAST: [
                SpellRank(
                    rank=1,
                    level=20,
                    min_damage=101,
                    max_damage=131,
                    mana_cost=125,
                    cast_time=6.0,
                    dot=DotData(damage=44, duration=12, ticks=4),
                ),
            ],
        }
    )


@pytest.fixture
def rich_mage() -> Character:
    """Level 20 mage with effectively infinite mana."""
    return Character(
        display_name="Test",
        level=20,
        intellect=50,
        spirit=50,
        mana=1_000_000,
        spell_power=SchoolValues(general=0),
        spell_crit=SchoolValues(general=0),
        spell_hit=SchoolValues(general=0),
    )


@pytest.fixture
def dummy() -> Encounter:
    """Immortal same-level target, 60 s."""
    return Encounter(
        display_name="Dummy",
        description="",
        encounter_type=EncounterType.SINGLE_TARGET,
        duration=60,
        enemy_count=1,
        enemy_health=1e12,
        enemy_level_delta=LevelDelta.SAME,
    )
