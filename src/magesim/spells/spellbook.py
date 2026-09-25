"""Mage spellbook data.

Damage, mana, and cast times: WoW Forever tooltips (Wowhead).
Coefficients: wowsims/classic; values marked ESTIMATED use the standard
Classic formula because the spell has no wowsims entry.
"""

from typing import Final

from magesim.core.constants import LOW_LEVEL_PENALTY_LEVEL, LOW_LEVEL_PENALTY_PER_LEVEL
from magesim.core.enums import CastKind, School, Targeting
from magesim.spells.definitions import DotData, SpellDefinition, SpellId, SpellRank


def _low_level_penalty(level: int) -> float:
    """Classic coefficient penalty for spells learned below level 20."""
    return 1.0 - max(LOW_LEVEL_PENALTY_LEVEL - level, 0) * LOW_LEVEL_PENALTY_PER_LEVEL


FIREBALL: Final = SpellDefinition(
    spell_id=SpellId.FIREBALL,
    school=School.FIRE,
    cast_kind=CastKind.CAST,
    targeting=Targeting.SINGLE,
    ranks=(
        SpellRank(
            rank=1,
            level=1,
            wowhead_id=133,
            min_damage=16,
            max_damage=24,
            coefficient=0.123,
            mana_cost=30,
            cast_time=1.5,
            dot=DotData(damage=2, ticks=2, tick_interval=2.0),
        ),
        SpellRank(
            rank=2,
            level=6,
            wowhead_id=143,
            min_damage=33,
            max_damage=47,
            coefficient=0.271,
            mana_cost=45,
            cast_time=2.0,
            dot=DotData(damage=3, ticks=3, tick_interval=2.0),
        ),
        SpellRank(
            rank=3,
            level=12,
            wowhead_id=145,
            min_damage=48,
            max_damage=65,
            coefficient=0.5,
            mana_cost=65,
            cast_time=2.5,
            dot=DotData(damage=6, ticks=3, tick_interval=2.0),
        ),
        SpellRank(
            rank=4,
            level=18,
            wowhead_id=3140,
            min_damage=67,
            max_damage=90,
            coefficient=0.793,
            mana_cost=95,
            cast_time=3.0,
            dot=DotData(damage=12, ticks=4, tick_interval=2.0),
        ),
    ),
)

FROSTBOLT: Final = SpellDefinition(
    spell_id=SpellId.FROSTBOLT,
    school=School.FROST,
    cast_kind=CastKind.CAST,
    targeting=Targeting.SINGLE,
    chills=True,
    ranks=(
        SpellRank(
            rank=1,
            level=4,
            wowhead_id=116,
            min_damage=20,
            max_damage=22,
            coefficient=0.163,
            mana_cost=25,
            cast_time=1.5,
        ),
        SpellRank(
            rank=2,
            level=8,
            wowhead_id=205,
            min_damage=33.8,
            max_damage=37.8,
            coefficient=0.269,
            mana_cost=35,
            cast_time=1.8,
        ),
        SpellRank(
            rank=3,
            level=14,
            wowhead_id=837,
            min_damage=47.0444,
            max_damage=52.1556,
            coefficient=0.463,
            mana_cost=50,
            cast_time=2.2,
        ),
        SpellRank(
            rank=4,
            level=20,
            wowhead_id=7322,
            min_damage=61.3231,
            max_damage=67.4769,
            coefficient=0.706,
            mana_cost=65,
            cast_time=2.6,
        ),
    ),
)

FIRE_BLAST: Final = SpellDefinition(
    spell_id=SpellId.FIRE_BLAST,
    school=School.FIRE,
    cast_kind=CastKind.INSTANT,
    targeting=Targeting.SINGLE,
    cooldown=8.0,
    ranks=(
        SpellRank(
            rank=1,
            level=6,
            wowhead_id=2136,
            min_damage=27,
            max_damage=35,
            coefficient=0.204,
            mana_cost=40,
        ),
        SpellRank(
            rank=2,
            level=14,
            wowhead_id=2137,
            min_damage=57,
            max_damage=69,
            coefficient=0.332,
            mana_cost=75,
        ),
        SpellRank(
            rank=3,
            level=22,
            wowhead_id=2138,
            min_damage=97,
            max_damage=117,
            coefficient=0.429,
            mana_cost=115,
        ),
    ),
)

ARCANE_MISSILES: Final = SpellDefinition(
    spell_id=SpellId.ARCANE_MISSILES,
    school=School.ARCANE,
    cast_kind=CastKind.CHANNEL,
    targeting=Targeting.SINGLE,
    ranks=(
        SpellRank(
            rank=1,
            level=8,
            wowhead_id=5143,
            min_damage=25,
            max_damage=25,
            coefficient=0.132,
            mana_cost=85,
            cast_time=3.0,
            channel_ticks=3,
        ),
        SpellRank(
            rank=2,
            level=16,
            wowhead_id=5144,
            min_damage=33,
            max_damage=33,
            coefficient=0.204,
            mana_cost=140,
            cast_time=4.0,
            channel_ticks=4,
        ),
    ),
)

ARCANE_EXPLOSION: Final = SpellDefinition(
    spell_id=SpellId.ARCANE_EXPLOSION,
    school=School.ARCANE,
    cast_kind=CastKind.INSTANT,
    targeting=Targeting.AOE,
    ranks=(
        SpellRank(
            rank=1,
            level=14,
            wowhead_id=1449,
            min_damage=32,
            max_damage=36,
            coefficient=0.111,
            mana_cost=75,
        ),
        SpellRank(
            rank=2,
            level=22,
            wowhead_id=8437,
            min_damage=55,
            max_damage=61,
            coefficient=0.143,
            mana_cost=120,
        ),
    ),
)

FROST_NOVA: Final = SpellDefinition(
    spell_id=SpellId.FROST_NOVA,
    school=School.FROST,
    cast_kind=CastKind.INSTANT,
    targeting=Targeting.AOE,
    cooldown=25.0,
    freeze_duration=8.0,
    ranks=(
        # ESTIMATED: Classic max-rank 0.136 scaled by the low-level penalty.
        SpellRank(
            rank=1,
            level=10,
            wowhead_id=122,
            min_damage=21.5,
            max_damage=23.5,
            coefficient=0.136 * _low_level_penalty(10),
            mana_cost=55,
        ),
    ),
)

FLAMESTRIKE: Final = SpellDefinition(
    spell_id=SpellId.FLAMESTRIKE,
    school=School.FIRE,
    cast_kind=CastKind.CAST,
    targeting=Targeting.AOE,
    ranks=(
        SpellRank(
            rank=1,
            level=16,
            wowhead_id=2120,
            min_damage=55,
            max_damage=71,
            coefficient=0.134,
            mana_cost=195,
            cast_time=3.0,
            dot=DotData(damage=44, ticks=4, tick_interval=2.0, coefficient_per_tick=0.017),
        ),
    ),
)

BLIZZARD: Final = SpellDefinition(
    spell_id=SpellId.BLIZZARD,
    school=School.FROST,
    cast_kind=CastKind.CHANNEL,
    targeting=Targeting.AOE,
    ranks=(
        SpellRank(
            rank=1,
            level=20,
            wowhead_id=10,
            min_damage=24.5,
            max_damage=24.5,
            coefficient=0.042,
            mana_cost=320,
            cast_time=8.0,
            channel_ticks=8,
        ),
    ),
)

SCORCH: Final = SpellDefinition(
    spell_id=SpellId.SCORCH,
    school=School.FIRE,
    cast_kind=CastKind.CAST,
    targeting=Targeting.SINGLE,
    ranks=(
        SpellRank(
            rank=1,
            level=22,
            wowhead_id=2948,
            min_damage=38,
            max_damage=46,
            coefficient=0.429,
            mana_cost=50,
            cast_time=1.5,
        ),
    ),
)

PYROBLAST: Final = SpellDefinition(
    spell_id=SpellId.PYROBLAST,
    school=School.FIRE,
    cast_kind=CastKind.CAST,
    targeting=Targeting.SINGLE,
    granted_by_talent="Pyroblast",
    ranks=(
        SpellRank(
            rank=1,
            level=20,
            wowhead_id=11366,
            min_damage=101,
            max_damage=131,
            coefficient=1.0,
            mana_cost=125,
            cast_time=6.0,
            dot=DotData(damage=44, ticks=4, tick_interval=3.0, coefficient_per_tick=0.15),
        ),
    ),
)

ICE_LANCE: Final = SpellDefinition(
    spell_id=SpellId.ICE_LANCE,
    school=School.FROST,
    cast_kind=CastKind.INSTANT,
    targeting=Targeting.SINGLE,
    granted_by_talent="Ice Lance",
    ranks=(
        # ESTIMATED: instant-cast formula 1.5 / 3.5.
        SpellRank(
            rank=1,
            level=20,
            wowhead_id=1312002,
            min_damage=28,
            max_damage=32,
            coefficient=1.5 / 3.5,
            mana_cost=45,
        ),
    ),
)

ARCANE_BLAST: Final = SpellDefinition(
    spell_id=SpellId.ARCANE_BLAST,
    school=School.ARCANE,
    cast_kind=CastKind.CAST,
    targeting=Targeting.SINGLE,
    granted_by_talent="Arcane Blast",
    ranks=(
        # ESTIMATED: cast-time formula 2.5 / 3.5.
        SpellRank(
            rank=1,
            level=20,
            wowhead_id=400574,
            min_damage=57,
            max_damage=65,
            coefficient=2.5 / 3.5,
            base_mana_pct=15.0,
            cast_time=2.5,
        ),
    ),
)

SPELLBOOK: Final[dict[SpellId, SpellDefinition]] = {
    spell.spell_id: spell
    for spell in (
        FIREBALL,
        FROSTBOLT,
        FIRE_BLAST,
        ARCANE_MISSILES,
        ARCANE_EXPLOSION,
        FROST_NOVA,
        FLAMESTRIKE,
        BLIZZARD,
        SCORCH,
        PYROBLAST,
        ICE_LANCE,
        ARCANE_BLAST,
    )
}

# Arcane Blast buff: per stack, +10% damage to other spells and +175% own cost.
ARCANE_BLAST_MAX_STACKS: Final = 4
ARCANE_BLAST_DAMAGE_PER_STACK: Final = 0.10
ARCANE_BLAST_COST_PER_STACK: Final = 1.75
ARCANE_BLAST_DURATION: Final = 8.0
