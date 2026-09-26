"""Spell power coefficients, calculated from configured rank values.

Classic formula (reproduces wowsims/classic values for ranks learned at level 20+):
    direct   = clamp(cast_time, 1.5, 3.5) / 3.5            (instants count as 1.5 s)
    channel  = channel_duration / 3.5, split across ticks
    dot      = dot_duration / 15, split across ticks
each times the spell's scale (mechanics.py).

Unlike Classic, there is no penalty for ranks learned below level 20: the
Forever beta client stores the full coefficient on every rank.
"""

from dataclasses import dataclass
from typing import Final

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

    direct_base: float
    direct: float
    dot_base: float
    dot_per_tick: float
    total: float


def direct_base(mechanics: SpellMechanics, rank: SpellRank) -> float:
    """Unscaled coefficient of the whole direct (or channeled) component."""
    if mechanics.cast_kind is CastKind.CHANNEL:
        return rank.cast_time / CAST_TIME_DIVISOR
    return min(max(rank.cast_time, MIN_CAST_TIME), MAX_CAST_TIME) / CAST_TIME_DIVISOR


def calculate(mechanics: SpellMechanics, rank: SpellRank) -> RankCoefficients:
    """Coefficients for `rank` of the spell described by `mechanics`."""
    base = direct_base(mechanics, rank)
    hits = rank.channel_ticks if mechanics.cast_kind is CastKind.CHANNEL else 1
    direct = base * mechanics.direct_scale / hits
    dot_base = rank.dot.duration / DOT_DURATION_DIVISOR if rank.dot else 0.0
    dot_ticks = rank.dot.ticks if rank.dot else 1
    dot_per_tick = dot_base * mechanics.dot_scale / dot_ticks
    return RankCoefficients(
        direct_base=base,
        direct=direct,
        dot_base=dot_base,
        dot_per_tick=dot_per_tick,
        total=direct * hits + dot_per_tick * dot_ticks,
    )
