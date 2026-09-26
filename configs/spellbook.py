"""Spell ranks as shown in game (trainer / tooltip values).

Coefficients are calculated from these values; audit them with `magesim spellbook`.
Channels: `cast_time` is the channel duration and damage is per tick.
DoTs: DotData(damage=total, duration=seconds, ticks=count).
Initial values are from Wowhead's Forever database.
"""
# ruff: noqa: E501
# fmt: off

from magesim import DotData, SpellId, SpellRank

SPELL_RANKS: dict[SpellId, list[SpellRank]] = {
    SpellId.FIREBALL: [
        SpellRank(rank=1, level=1, min_damage=16, max_damage=24, mana_cost=30, cast_time=1.5, dot=DotData(damage=2, duration=4, ticks=2), wowhead_id=133),
        SpellRank(rank=2, level=6, min_damage=33, max_damage=47, mana_cost=45, cast_time=2.0, dot=DotData(damage=3, duration=6, ticks=3), wowhead_id=143),
        SpellRank(rank=3, level=12, min_damage=48, max_damage=65, mana_cost=65, cast_time=2.5, dot=DotData(damage=6, duration=6, ticks=3), wowhead_id=145),
        SpellRank(rank=4, level=18, min_damage=67, max_damage=90, mana_cost=95, cast_time=3.0, dot=DotData(damage=12, duration=8, ticks=4), wowhead_id=3140),
    ],
    SpellId.FROSTBOLT: [
        SpellRank(rank=1, level=4, min_damage=20, max_damage=22, mana_cost=25, cast_time=1.5, wowhead_id=116),
        SpellRank(rank=2, level=8, min_damage=33.8, max_damage=37.8, mana_cost=35, cast_time=1.8, wowhead_id=205),
        SpellRank(rank=3, level=14, min_damage=47.0444, max_damage=52.1556, mana_cost=50, cast_time=2.2, wowhead_id=837),
        SpellRank(rank=4, level=20, min_damage=61.3231, max_damage=67.4769, mana_cost=65, cast_time=2.6, wowhead_id=7322),
    ],
    SpellId.FIRE_BLAST: [
        SpellRank(rank=1, level=6, min_damage=27, max_damage=35, mana_cost=40, cooldown=8, wowhead_id=2136),
        SpellRank(rank=2, level=14, min_damage=57, max_damage=69, mana_cost=75, cooldown=8, wowhead_id=2137),
        SpellRank(rank=3, level=22, min_damage=97, max_damage=117, mana_cost=115, cooldown=8, wowhead_id=2138),
    ],
    SpellId.ARCANE_MISSILES: [
        SpellRank(rank=1, level=8, min_damage=25, max_damage=25, mana_cost=85, cast_time=3.0, channel_ticks=3, wowhead_id=5143),
        SpellRank(rank=2, level=16, min_damage=33, max_damage=33, mana_cost=140, cast_time=4.0, channel_ticks=4, wowhead_id=5144),
    ],
    SpellId.ARCANE_EXPLOSION: [
        SpellRank(rank=1, level=14, min_damage=32, max_damage=36, mana_cost=75, wowhead_id=1449),
        SpellRank(rank=2, level=22, min_damage=55, max_damage=61, mana_cost=120, wowhead_id=8437),
    ],
    SpellId.FROST_NOVA: [
        SpellRank(rank=1, level=10, min_damage=21.5, max_damage=23.5, mana_cost=55, cooldown=25, wowhead_id=122),
    ],
    SpellId.FLAMESTRIKE: [
        SpellRank(rank=1, level=16, min_damage=55, max_damage=71, mana_cost=195, cast_time=3.0, dot=DotData(damage=44, duration=8, ticks=4), wowhead_id=2120),
    ],
    SpellId.BLIZZARD: [
        SpellRank(rank=1, level=20, min_damage=24.5, max_damage=24.5, mana_cost=320, cast_time=8.0, channel_ticks=8, wowhead_id=10),
    ],
    SpellId.SCORCH: [
        SpellRank(rank=1, level=22, min_damage=38, max_damage=46, mana_cost=50, cast_time=1.5, wowhead_id=2948),
    ],
    SpellId.PYROBLAST: [
        SpellRank(rank=1, level=20, min_damage=101, max_damage=131, mana_cost=125, cast_time=6.0, dot=DotData(damage=44, duration=12, ticks=4), wowhead_id=11366),
    ],
    SpellId.ICE_LANCE: [
        SpellRank(rank=1, level=20, min_damage=28, max_damage=32, mana_cost=45, wowhead_id=1312002),
    ],
    SpellId.ARCANE_BLAST: [
        SpellRank(rank=1, level=20, min_damage=57, max_damage=65, base_mana_pct=15, cast_time=2.5, wowhead_id=400574),
    ],
}
