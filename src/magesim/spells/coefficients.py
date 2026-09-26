"""Spell power coefficients, calculated from configured rank values.

Classic formula (reproduces wowsims/classic per-rank values):
    direct   = clamp(cast_time, 1.5, 3.5) / 3.5            (instants count as 1.5 s)
    channel  = channel_duration / 3.5, split across ticks
    dot      = dot_duration / 15, split across ticks
each times the spell's scale (mechanics.py) and the low-level penalty
1 - 3.75% per level the rank is learned below 20.
"""

from dataclasses import dataclass
from typing import Final

from magesim.core.constants import LOW_LEVEL_PENALTY_LEVEL, LOW_LEVEL_PENALTY_PER_LEVEL
from magesim.core.enums import CastKind
from magesim.spells.definitions import SpellMechanics, SpellRank

MIN_CAST_TIME: Final = 1.5
MAX_CAST_TIME: Final = 3.5
CAST_TIME_DIVISOR: Final = 3.5
DOT_DURATION_DIVISOR: Final = 15.0

# Standard Classic scale factors.
AOE_SCALE: Final = 1.0 / 3.0
CONTROL_EFFECT_SCALE: Final = 0.95


@dataclass(frozen=True, slots=True)
class RankCoefficients:
    """Calculated coefficients for one rank.

    `direct` applies per hit (per tick for channels); `dot_per_tick` per DoT tick.
    """

    low_level_penalty: float
    direct_base: float
    direct: float
    dot_base: float
    dot_per_tick: float
    total: float


def low_level_penalty(level: int) -> float:
    """Coefficient multiplier for ranks learned below level 20."""
    return 1.0 - max(LOW_LEVEL_PENALTY_LEVEL - level, 0) * LOW_LEVEL_PENALTY_PER_LEVEL


def direct_base(mechanics: SpellMechanics, rank: SpellRank) -> float:
    """Unscaled coefficient of the whole direct (or channeled) component."""
    if mechanics.cast_kind is CastKind.CHANNEL:
        return rank.cast_time / CAST_TIME_DIVISOR
    return min(max(rank.cast_time, MIN_CAST_TIME), MAX_CAST_TIME) / CAST_TIME_DIVISOR


def calculate(mechanics: SpellMechanics, rank: SpellRank) -> RankCoefficients:
    """Coefficients for `rank` of the spell described by `mechanics`."""
    penalty = low_level_penalty(rank.level)
    base = direct_base(mechanics, rank)
    hits = rank.channel_ticks if mechanics.cast_kind is CastKind.CHANNEL else 1
    direct = base * mechanics.direct_scale * penalty / hits
    dot_base = rank.dot.duration / DOT_DURATION_DIVISOR if rank.dot else 0.0
    dot_ticks = rank.dot.ticks if rank.dot else 1
    dot_per_tick = dot_base * mechanics.dot_scale * penalty / dot_ticks
    return RankCoefficients(
        low_level_penalty=penalty,
        direct_base=base,
        direct=direct,
        dot_base=dot_base,
        dot_per_tick=dot_per_tick,
        total=direct * hits + dot_per_tick * dot_ticks,
    )
