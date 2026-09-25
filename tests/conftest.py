"""Shared test fixtures."""

import pytest

from magesim import Character, Encounter, EncounterType, LevelDelta, SchoolValues


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
