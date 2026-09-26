"""Candidate planning and validation."""

import pytest

from magesim import (
    Character,
    Encounter,
    EncounterType,
    MetaConfig,
    Rotation,
    RotationFunction,
    SimState,
    SpellChoice,
    SpellId,
)
from magesim.experiment.candidates import CandidatePlan, plan_candidates
from magesim.spells.definitions import SpellCatalog
from magesim.talents.build import TalentBuild

CALC = "https://www.wowhead.com/forever/talent-calc/mage/"
FIRE_20 = TalentBuild.from_url(CALC + "v2-005500001")  # 11 points, Pyroblast
ARCANE_20 = TalentBuild.from_url(CALC + "v20500050001")  # 11 points, no Pyroblast
FIRE_15 = TalentBuild.from_url(CALC + "v2-22-02")  # 6 points
META = MetaConfig(iterations=1)


def _fireball(s: SimState) -> SpellChoice:
    return s.spells.fireball


def _pyro_if_ready(s: SimState) -> SpellChoice:
    return s.spells.pyroblast if s.spells.pyroblast.ready else s.spells.fireball


def _pyro_if_known(s: SimState) -> SpellChoice:
    return s.spells.pyroblast if s.spells.pyroblast.known else s.spells.fireball


def _rotation(function: RotationFunction, **overrides: int) -> Rotation:
    return Rotation(
        display_name=function.__name__,
        description="",
        encounter_type=EncounterType.SINGLE_TARGET,
        rotation_function=function,
        rank_overrides={SpellId[k.upper()]: v for k, v in overrides.items()},
    )


def _plan(
    character: Character,
    encounter: Encounter,
    catalog: SpellCatalog,
    rotations: list[Rotation],
    talents: list[TalentBuild],
) -> CandidatePlan:
    return plan_candidates([character], [encounter], rotations, talents, catalog, META)


def test_valid_candidates_are_numbered(
    rich_mage: Character, dummy: Encounter, catalog: SpellCatalog
) -> None:
    plan = _plan(rich_mage, dummy, catalog, [_rotation(_fireball)], [FIRE_20, ARCANE_20])
    assert [c.number for c in plan.valid] == [1, 2]
    assert plan.invalid == []


def test_encounter_type_mismatch_is_not_a_candidate(
    rich_mage: Character, dummy: Encounter, catalog: SpellCatalog
) -> None:
    leveling = Rotation(
        display_name="l",
        description="",
        encounter_type=EncounterType.MULTI_TARGET_LEVELING,
        rotation_function=_fireball,
    )
    plan = _plan(rich_mage, dummy, catalog, [leveling], [FIRE_20])
    assert plan.valid == [] and plan.invalid == []


def test_talent_level_mismatch_is_invalid(
    rich_mage: Character, dummy: Encounter, catalog: SpellCatalog
) -> None:
    plan = _plan(rich_mage, dummy, catalog, [_rotation(_fireball)], [FIRE_15])
    assert plan.valid == []
    assert plan.invalid[0].reasons == ("talents require level 15, character is level 20",)


def test_rotation_using_untalented_spell_is_invalid(
    rich_mage: Character, dummy: Encounter, catalog: SpellCatalog
) -> None:
    plan = _plan(rich_mage, dummy, catalog, [_rotation(_pyro_if_ready)], [FIRE_20, ARCANE_20])
    assert [c.talents for c in plan.valid] == [FIRE_20]
    assert plan.invalid[0].talents is ARCANE_20
    assert "Pyroblast talent" in plan.invalid[0].reasons[0]


def _pyro_never_reached(s: SimState) -> SpellChoice:
    if s.time < 0 and s.spells.pyroblast.ready:
        return s.spells.pyroblast
    return s.spells.fireball


def test_unreached_untalented_reference_is_invalid(
    rich_mage: Character, dummy: Encounter, catalog: SpellCatalog
) -> None:
    plan = _plan(rich_mage, dummy, catalog, [_rotation(_pyro_never_reached)], [ARCANE_20])
    assert plan.valid == []
    assert plan.invalid[0].reasons == (
        "rotation uses Pyroblast, which requires the Pyroblast talent",
    )


def test_checking_known_is_allowed(
    rich_mage: Character, dummy: Encounter, catalog: SpellCatalog
) -> None:
    plan = _plan(rich_mage, dummy, catalog, [_rotation(_pyro_if_known)], [ARCANE_20])
    assert len(plan.valid) == 1


@pytest.mark.parametrize(
    ("rank", "reason"),
    [
        (5, "has no rank 5 in configs/spellbook.py"),
        (4, "rank 4 is learned at level 18 (character is 12)"),
    ],
)
def test_bad_rank_override_is_invalid(
    dummy: Encounter, catalog: SpellCatalog, rank: int, reason: str
) -> None:
    level_12 = Character(display_name="low", level=12, intellect=30, spirit=30, mana=300)
    talents_12 = TalentBuild.from_url(CALC + "v2-003")  # 3 points
    rotation = _rotation(_fireball, fireball=rank)
    plan = _plan(level_12, dummy, catalog, [rotation], [talents_12])
    assert plan.valid == []
    assert plan.invalid[0].reasons == (f"rank override: Fireball {reason}",)
