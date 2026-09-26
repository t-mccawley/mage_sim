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
    Water,
)
from magesim.core.enums import TalentTree
from magesim.engine.simulator import Simulation
from magesim.spells.definitions import SpellCatalog
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
    assert result.casts["Fire Blast"] == math.floor(dummy.duration / rank.cooldown) + 1


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


def test_untalented_spell_is_blocked(
    rich_mage: Character, dummy: Encounter, catalog: SpellCatalog
) -> None:
    def pyro(s: SimState) -> SpellChoice:
        return s.spells.pyroblast

    result = _sim(rich_mage, dummy, _rotation(pyro), catalog).run(random.Random(0))
    assert result.total_dps == 0
    assert result.blocked_seconds["Pyroblast: not known"] == pytest.approx(60, abs=0.2)


def test_spell_without_ranks_is_unknown(
    rich_mage: Character, dummy: Encounter, catalog: SpellCatalog
) -> None:
    def scorch(s: SimState) -> SpellChoice:
        return s.spells.scorch

    result = _sim(rich_mage, dummy, _rotation(scorch), catalog).run(random.Random(0))
    assert result.casts == {}
    assert "Scorch: not known" in result.blocked_seconds
