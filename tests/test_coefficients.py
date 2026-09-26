"""Calculated spell power coefficients."""

import pytest

from magesim import DotData, SpellId, SpellRank
from magesim.spells.coefficients import calculate
from magesim.spells.mechanics import SPELL_MECHANICS

# Classic ranks learned at level 20+ (no Classic low-level penalty), with wowsims/classic
# coefficients: (spell, level, cast/channel time, channel ticks, dot, direct, dot per tick).
WOWSIMS_CASES = [
    (SpellId.FIREBALL, 30, 3.5, 0, None, 1.0, 0.0),
    (SpellId.FROSTBOLT, 20, 2.6, 0, None, 0.706, 0.0),
    (SpellId.FROSTBOLT, 26, 3.0, 0, None, 0.814, 0.0),
    (SpellId.FIRE_BLAST, 22, 0.0, 0, None, 0.429, 0.0),
    (SpellId.ARCANE_MISSILES, 24, 5.0, 5, None, 0.24, 0.0),
    (SpellId.ARCANE_EXPLOSION, 22, 0.0, 0, None, 0.143, 0.0),
    (SpellId.FLAMESTRIKE, 24, 3.0, 0, DotData(damage=88, duration=8, ticks=4), 0.157, 0.02),
    (SpellId.BLIZZARD, 20, 8.0, 8, None, 0.042, 0.0),
    (SpellId.SCORCH, 22, 1.5, 0, None, 0.429, 0.0),
    (SpellId.PYROBLAST, 20, 6.0, 0, DotData(damage=56, duration=12, ticks=4), 1.0, 0.15),
    (SpellId.BLAST_WAVE, 30, 0.0, 0, None, 0.129, 0.0),
]


def _rank(
    level: int, cast_time: float, channel_ticks: int = 0, dot: DotData | None = None
) -> SpellRank:
    return SpellRank(
        rank=1,
        level=level,
        min_damage=1,
        max_damage=1,
        cast_time=cast_time,
        channel_ticks=channel_ticks,
        dot=dot,
    )


@pytest.mark.parametrize(
    ("spell", "level", "cast_time", "channel_ticks", "dot", "direct", "dot_per_tick"),
    WOWSIMS_CASES,
)
def test_matches_wowsims(
    spell: SpellId,
    level: int,
    cast_time: float,
    channel_ticks: int,
    dot: DotData | None,
    direct: float,
    dot_per_tick: float,
) -> None:
    result = calculate(SPELL_MECHANICS[spell], _rank(level, cast_time, channel_ticks, dot))
    assert result.direct == pytest.approx(direct, abs=0.0015)
    assert result.dot_per_tick == pytest.approx(dot_per_tick, abs=0.0015)


@pytest.mark.parametrize(
    ("spell", "level", "cast_time", "channel_ticks", "direct"),
    [
        (SpellId.FIREBALL, 1, 1.5, 0, 1.5 / 3.5),
        (SpellId.FROSTBOLT, 4, 1.5, 0, 1.5 / 3.5 * 0.95),
        (SpellId.ARCANE_MISSILES, 8, 3.0, 3, 3.0 / 3.5 * 0.84 / 3),
        (SpellId.FROST_NOVA, 10, 0.0, 0, 1.5 / 3.5 / 3 * 0.95),
    ],
)
def test_low_level_ranks_get_full_coefficient(
    spell: SpellId, level: int, cast_time: float, channel_ticks: int, direct: float
) -> None:
    result = calculate(SPELL_MECHANICS[spell], _rank(level, cast_time, channel_ticks))
    assert result.direct == pytest.approx(direct)


def test_cast_time_is_clamped() -> None:
    mechanics = SPELL_MECHANICS[SpellId.SCORCH]
    assert calculate(mechanics, _rank(30, 6.0)).direct == pytest.approx(1.0)
    assert calculate(mechanics, _rank(30, 0.0)).direct == pytest.approx(1.5 / 3.5)
