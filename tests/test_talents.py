"""Talent URL parsing and effects."""

import pytest

from magesim.core.enums import School, TalentTree
from magesim.spells.definitions import SpellId
from magesim.talents.build import TalentBuild
from magesim.talents.effects import TalentModifiers

EXAMPLE_URL = "https://www.wowhead.com/forever/talent-calc/mage/v1-22-02_t0/1Abb2bb"


def test_example_url_decodes() -> None:
    build = TalentBuild.from_url(EXAMPLE_URL)
    assert build.points == {TalentTree.ARCANE: 0, TalentTree.FIRE: 4, TalentTree.FROST: 2}
    assert build.ranks == {"Wake of Fire": 2, "Incineration": 2, "Improved Frostbolt": 2}
    assert build.display_name == "Fire (0 / 4 / 2)"
    assert build.required_level == 15


def test_talented_rank_lowers_required_level() -> None:
    build = TalentBuild.from_url(EXAMPLE_URL.replace("_t0", "_t2"))
    assert build.required_level == 13


def test_arcane_first_tree_has_no_separator() -> None:
    build = TalentBuild.from_url("https://www.wowhead.com/forever/talent-calc/mage/v10500050001")
    assert build.points[TalentTree.ARCANE] == 11
    assert build.primary_tree is TalentTree.ARCANE


def test_rank_above_max_rejected() -> None:
    with pytest.raises(ValueError, match="exceeds max"):
        TalentBuild.from_url("https://www.wowhead.com/forever/talent-calc/mage/v1-3")


def test_non_calculator_url_rejected() -> None:
    with pytest.raises(ValueError, match="not a Wowhead"):
        TalentBuild.from_url("https://example.com")


def test_modifiers_from_ranks() -> None:
    build = TalentBuild.from_url("https://www.wowhead.com/forever/talent-calc/mage/v1--0505000001")
    mods = TalentModifiers.from_build(build)
    assert mods.cast_time_reduction[SpellId.FROSTBOLT] == pytest.approx(0.5)
    assert mods.crit_damage_bonus[School.FROST] == pytest.approx(1.0)
    assert SpellId.ICE_LANCE in mods.granted_spells
    assert mods.unimplemented == ()
