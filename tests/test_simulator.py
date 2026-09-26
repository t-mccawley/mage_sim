"""Engine behaviour."""

import math
import random

import numpy as np
import pytest

from magesim import (
    Character,
    Encounter,
    EncounterType,
    Rotation,
    RotationFunction,
    SimState,
    SpellChoice,
    SpellId,
    SpellRank,
    Water,
)
from magesim.core.enums import TalentTree
from magesim.engine.simulator import Simulation
from magesim.engine.state import UnavailableSpellError
from magesim.spells.definitions import SpellCatalog
from magesim.spells.mechanics import build_catalog
from magesim.talents.build import TalentBuild

NO_TALENTS = TalentBuild(url="", ranks={}, points=dict.fromkeys(TalentTree, 0))


def _rotation(
    function: RotationFunction, kind: EncounterType = EncounterType.SINGLE_TARGET
) -> Rotation:
    return Rotation(
        display_name="t", description="", encounter_type=kind, rotation_function=function
    )


def _fireball(s: SimState) -> SpellChoice:
    return s.spells.fireball


def _fire_blast_only(s: SimState) -> SpellChoice:
    return s.spells.fire_blast if s.spells.fire_blast.ready else None


def _sim(
    character: Character, encounter: Encounter, rotation: Rotation, catalog: SpellCatalog
) -> Simulation:
    return Simulation(
        character,
        encounter,
        NO_TALENTS,
        rotation,
        catalog,
        tick_seconds=0.1,
        peak_warmup_seconds=5.0,
    )


def test_same_seed_is_reproducible(
    rich_mage: Character, dummy: Encounter, catalog: SpellCatalog
) -> None:
    sim = _sim(rich_mage, dummy, _rotation(_fireball), catalog)
    a = sim.run(random.Random(7))
    b = sim.run(random.Random(7))
    assert a.total_dps == b.total_dps


def test_fireball_dps_matches_expectation(
    rich_mage: Character, dummy: Encounter, catalog: SpellCatalog
) -> None:
    sim = _sim(rich_mage, dummy, _rotation(_fireball), catalog)
    rng = random.Random(1)
    dps = np.mean([sim.run(rng).total_dps for _ in range(200)])
    rank = catalog[SpellId.FIREBALL].rank_for_level(20)
    assert rank is not None and rank.dot is not None
    # Recasts every 3 s overwrite the 2 s-tick DoT, so one tick lands per cast.
    per_cast = 0.96 * (rank.average_damage + rank.dot.damage_per_tick)
    assert dps == pytest.approx(per_cast / rank.cast_time, rel=0.03)


def test_cooldown_limits_casts(
    rich_mage: Character, dummy: Encounter, catalog: SpellCatalog
) -> None:
    result = _sim(rich_mage, dummy, _rotation(_fire_blast_only), catalog).run(random.Random(0))
    rank = catalog[SpellId.FIRE_BLAST].rank_for_level(20)
    assert rank is not None
    assert result.casts["Fire Blast (Rank 2)"] == math.floor(dummy.duration / rank.cooldown) + 1


def test_single_target_ends_on_kill(rich_mage: Character, catalog: SpellCatalog) -> None:
    encounter = Encounter(
        display_name="e",
        description="",
        duration=60,
        enemy_count=1,
        enemy_health=200,
        encounter_type=EncounterType.SINGLE_TARGET,
    )
    result = _sim(rich_mage, encounter, _rotation(_fireball), catalog).run(random.Random(0))
    assert result.enemies_killed == 1
    assert result.elapsed < 60
    assert np.isnan(result.dps_series[-1])


def test_leveling_drinks_between_pulls(catalog: SpellCatalog) -> None:
    character = Character(
        display_name="c",
        level=20,
        intellect=50,
        spirit=50,
        mana=600,
        water=Water.CONJURED_PURIFIED_WATER,
    )
    encounter = Encounter(
        display_name="e",
        description="",
        duration=300,
        enemy_count=1,
        enemy_health=300,
        encounter_type=EncounterType.MULTI_TARGET_LEVELING,
        drink_below_mana_pct=50,
    )
    rotation = _rotation(_fireball, EncounterType.MULTI_TARGET_LEVELING)
    result = _sim(character, encounter, rotation, catalog).run(random.Random(0))
    assert result.enemies_killed > 3
    assert result.drinking_time > 0
    assert not np.isnan(result.dps_series[-1])


def _pyro_if_ready(s: SimState) -> SpellChoice:
    return s.spells.pyroblast if s.spells.pyroblast.ready else None


def _scorch(s: SimState) -> SpellChoice:
    return SpellId.SCORCH


@pytest.mark.parametrize(
    ("function", "reason"),
    [
        (_pyro_if_ready, "rotation uses Pyroblast, which requires the Pyroblast talent"),
        (_scorch, "rotation uses Scorch, which has no ranks in configs/spellbook.py"),
    ],
)
def test_unavailable_spell_raises(
    rich_mage: Character,
    dummy: Encounter,
    catalog: SpellCatalog,
    function: RotationFunction,
    reason: str,
) -> None:
    sim = _sim(rich_mage, dummy, _rotation(function), catalog)
    with pytest.raises(UnavailableSpellError, match=reason):
        sim.run(random.Random(0))


FIREBALL_RANKS = [
    SpellRank(rank=r, level=level, min_damage=10 * r, max_damage=10 * r, cast_time=1.5)
    for r, level in ((1, 1), (2, 6), (3, 12), (4, 18))
]


@pytest.mark.parametrize(
    ("level", "overrides", "expected"),
    [(5, {}, 1), (12, {}, 3), (20, {}, 4), (20, {SpellId.FIREBALL: 2}, 2)],
)
def test_casts_max_rank_or_override(
    dummy: Encounter, level: int, overrides: dict[SpellId, int], expected: int
) -> None:
    character = Character(display_name="c", level=level, intellect=20, spirit=20, mana=1e6)
    rotation = Rotation(
        display_name="t",
        description="",
        encounter_type=EncounterType.SINGLE_TARGET,
        rotation_function=_fireball,
        rank_overrides=overrides,
    )
    catalog = build_catalog({SpellId.FIREBALL: FIREBALL_RANKS})
    result = _sim(character, dummy, rotation, catalog).run(random.Random(0))
    assert list(result.casts) == [f"Fireball (Rank {expected})"]
