"""Frostfire Bolt counts as both Fire and Frost."""

import pytest

from magesim import Character, SchoolValues, SpellId
from magesim.core.enums import LevelDelta, School
from magesim.engine.combat import SpellProfile
from magesim.spells.mechanics import SPELL_MECHANICS, build_catalog
from magesim.talents.build import TalentBuild
from magesim.talents.effects import TalentModifiers

CALC = "https://www.wowhead.com/forever/talent-calc/mage/"


def _profile(talents: TalentBuild, character: Character) -> SpellProfile:
    catalog = build_catalog({})
    mods = TalentModifiers.from_build(talents)
    return SpellProfile.build(character, mods, catalog[SpellId.FROSTFIRE_BOLT], LevelDelta.SAME)


def test_frostfire_counts_as_both_schools() -> None:
    assert SPELL_MECHANICS[SpellId.FROSTFIRE_BOLT].schools == (School.FIRE, School.FROST)


def test_frostfire_uses_best_school_stats_and_all_damage_bonuses() -> None:
    character = Character(
        display_name="c",
        level=60,
        intellect=100,
        spirit=100,
        mana=5000,
        spell_power=SchoolValues(general=100, fire=20, frost=50),
        spell_crit=SchoolValues(general=5, fire=3, frost=1),
    )
    # Frost: Piercing Ice 3 (+6% frost damage), Ice Shards 5 (+100% crit bonus).
    frost = TalentBuild.from_url(CALC + "v2--00050003")
    profile = _profile(frost, character)
    assert profile.spell_power == 150
    assert profile.crit_chance == pytest.approx(0.08)
    assert profile.damage_multiplier == pytest.approx(1.06)
    assert profile.crit_multiplier == pytest.approx(2.0)


def test_improved_fireball_speeds_up_frostfire() -> None:
    mods = TalentModifiers.from_build(TalentBuild.from_url(CALC + "v2-005"))
    assert mods.cast_time_reduction[SpellId.FROSTFIRE_BOLT] == pytest.approx(0.5)
