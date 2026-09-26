"""Calculated coefficients reproduce wowsims/classic per-rank values."""

import pytest

from magesim import DotData, SpellId, SpellRank
from magesim.spells.coefficients import calculate, low_level_penalty
from magesim.spells.mechanics import SPELL_MECHANICS

# (spell, level learned, cast/channel time, channel ticks, dot, wowsims direct coefficient,
#  wowsims dot coefficient per tick), using Classic rank data.
WOWSIMS_CASES = [
    (SpellId.FIREBALL, 1, 1.5, 0, None, 0.123, 0.0),
    (SpellId.FIREBALL, 6, 2.0, 0, None, 0.271, 0.0),
    (SpellId.FIREBALL, 12, 2.5, 0, None, 0.5, 0.0),
    (SpellId.FIREBALL, 18, 3.0, 0, None, 0.793, 0.0),
    (SpellId.FIREBALL, 30, 3.5, 0, None, 1.0, 0.0),
    (SpellId.FROSTBOLT, 4, 1.5, 0, None, 0.163, 0.0),
    (SpellId.FROSTBOLT, 8, 1.8, 0, None, 0.269, 0.0),
    (SpellId.FROSTBOLT, 14, 2.2, 0, None, 0.463, 0.0),
    (SpellId.FROSTBOLT, 20, 2.6, 0, None, 0.706, 0.0),
    (SpellId.FROSTBOLT, 26, 3.0, 0, None, 0.814, 0.0),
    (SpellId.FIRE_BLAST, 6, 0.0, 0, None, 0.204, 0.0),
    (SpellId.FIRE_BLAST, 14, 0.0, 0, None, 0.332, 0.0),
    (SpellId.FIRE_BLAST, 22, 0.0, 0, None, 0.429, 0.0),
    (SpellId.ARCANE_MISSILES, 8, 3.0, 3, None, 0.132, 0.0),
    (SpellId.ARCANE_MISSILES, 16, 4.0, 4, None, 0.204, 0.0),
    (SpellId.ARCANE_MISSILES, 24, 5.0, 5, None, 0.24, 0.0),
    (SpellId.ARCANE_EXPLOSION, 14, 0.0, 0, None, 0.111, 0.0),
    (SpellId.ARCANE_EXPLOSION, 22, 0.0, 0, None, 0.143, 0.0),
    (SpellId.FLAMESTRIKE, 16, 3.0, 0, DotData(damage=48, duration=8, ticks=4), 0.134, 0.017),
    (SpellId.FLAMESTRIKE, 24, 3.0, 0, DotData(damage=88, duration=8, ticks=4), 0.157, 0.02),
    (SpellId.BLIZZARD, 20, 8.0, 8, None, 0.042, 0.0),
    (SpellId.SCORCH, 22, 1.5, 0, None, 0.429, 0.0),
    (SpellId.PYROBLAST, 20, 6.0, 0, DotData(damage=56, duration=12, ticks=4), 1.0, 0.15),
]


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
    rank = SpellRank(
        rank=1,
        level=level,
        min_damage=1,
        max_damage=1,
        cast_time=cast_time,
        channel_ticks=channel_ticks,
        dot=dot,
    )
    result = calculate(SPELL_MECHANICS[spell], rank)
    assert result.direct == pytest.approx(direct, abs=0.0015)
    assert result.dot_per_tick == pytest.approx(dot_per_tick, abs=0.0015)


def test_low_level_penalty() -> None:
    assert low_level_penalty(1) == pytest.approx(0.2875)
    assert low_level_penalty(20) == 1.0
    assert low_level_penalty(60) == 1.0


def test_cast_time_is_clamped() -> None:
    mechanics = SPELL_MECHANICS[SpellId.SCORCH]
    slow = SpellRank(rank=1, level=30, min_damage=1, max_damage=1, cast_time=6.0)
    instant = SpellRank(rank=1, level=30, min_damage=1, max_damage=1)
    assert calculate(mechanics, slow).direct == pytest.approx(1.0)
    assert calculate(mechanics, instant).direct == pytest.approx(1.5 / 3.5)
