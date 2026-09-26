"""Spell ranks as shown in game (trainer / tooltip values).

Coefficients are calculated from these values; audit them with `magesim spellbook`.
Channels: `cast_time` is the channel duration and damage is per tick.
DoTs: DotData(damage=total, duration=seconds, ticks=count).
Pre-filled from Wowhead's Forever database (levels 1-60); set
`confirmed_in_game_date` on each rank once checked against the in-game trainer.
Talent spells (Pyroblast, Ice Lance, Arcane Blast, Blast Wave) need their talent for every rank.
"""
# ruff: noqa: E501
# fmt: off

from magesim import DotData, SpellId, SpellRank

SPELL_RANKS: dict[SpellId, list[SpellRank]] = {
    SpellId.FIREBALL: [
        SpellRank(rank=1, level=1, min_damage=18, max_damage=27, mana_cost=30, cast_time=1.5, dot=DotData(damage=2, duration=4, ticks=2), wowhead_id=133, confirmed_in_game_date="2026-09-26"),
        SpellRank(rank=2, level=6, min_damage=35, max_damage=50, mana_cost=45, cast_time=2.0, dot=DotData(damage=3, duration=6, ticks=3), wowhead_id=143, confirmed_in_game_date="2026-09-26"),
        SpellRank(rank=3, level=12, min_damage=51, max_damage=68, mana_cost=65, cast_time=2.5, dot=DotData(damage=6, duration=6, ticks=3), wowhead_id=145, confirmed_in_game_date="2026-09-26"),
        SpellRank(rank=4, level=18, min_damage=66, max_damage=91, mana_cost=95, cast_time=3.0, dot=DotData(damage=12, duration=8, ticks=4), wowhead_id=3140, confirmed_in_game_date="2026-09-26"),
        SpellRank(rank=5, level=24, min_damage=97, max_damage=129, mana_cost=140, cast_time=3.5, dot=DotData(damage=16, duration=8, ticks=4), wowhead_id=8400, confirmed_in_game_date="2026-09-26"),
        SpellRank(rank=6, level=30, min_damage=136, max_damage=180, mana_cost=185, cast_time=3.5, dot=DotData(damage=24, duration=8, ticks=4), wowhead_id=8401, confirmed_in_game_date="2026-09-26"),
        SpellRank(rank=7, level=36, min_damage=171, max_damage=222, mana_cost=220, cast_time=3.5, dot=DotData(damage=24, duration=8, ticks=4), wowhead_id=8402),
        SpellRank(rank=8, level=42, min_damage=213, max_damage=275, mana_cost=260, cast_time=3.5, dot=DotData(damage=32, duration=8, ticks=4), wowhead_id=10148),
        SpellRank(rank=9, level=48, min_damage=272, max_damage=348, mana_cost=305, cast_time=3.5, dot=DotData(damage=40, duration=8, ticks=4), wowhead_id=10149),
        SpellRank(rank=10, level=54, min_damage=339, max_damage=431, mana_cost=350, cast_time=3.5, dot=DotData(damage=48, duration=8, ticks=4), wowhead_id=10150),
        SpellRank(rank=11, level=60, min_damage=409, max_damage=517, mana_cost=395, cast_time=3.5, dot=DotData(damage=56, duration=8, ticks=4), wowhead_id=10151),
        SpellRank(rank=12, level=60, min_damage=437, max_damage=553, mana_cost=410, cast_time=3.5, dot=DotData(damage=60, duration=8, ticks=4), wowhead_id=25306),
    ],
    SpellId.FROSTBOLT: [
        SpellRank(rank=1, level=4, min_damage=20, max_damage=22, mana_cost=24, cast_time=1.5, wowhead_id=116, confirmed_in_game_date="2026-09-26"),
        SpellRank(rank=2, level=8, min_damage=36, max_damage=40, mana_cost=35, cast_time=1.8, wowhead_id=205, confirmed_in_game_date="2026-09-26"),
        SpellRank(rank=3, level=14, min_damage=47, max_damage=53, mana_cost=50, cast_time=2.2, wowhead_id=837, confirmed_in_game_date="2026-09-26"),
        SpellRank(rank=4, level=20, min_damage=61, max_damage=67, mana_cost=65, cast_time=2.6, wowhead_id=7322, confirmed_in_game_date="2026-09-26"),
        SpellRank(rank=5, level=26, min_damage=96.6818, max_damage=105.318, mana_cost=100, cast_time=3, wowhead_id=8406),
        SpellRank(rank=6, level=32, min_damage=134.91, max_damage=146.69, mana_cost=130, cast_time=3, wowhead_id=8407),
        SpellRank(rank=7, level=38, min_damage=181.363, max_damage=196.637, mana_cost=160, cast_time=3, wowhead_id=8408),
        SpellRank(rank=8, level=44, min_damage=243.568, max_damage=262.832, mana_cost=195, cast_time=3, wowhead_id=10179),
        SpellRank(rank=9, level=50, min_damage=305.846, max_damage=330.954, mana_cost=225, cast_time=3, wowhead_id=10180),
        SpellRank(rank=10, level=56, min_damage=382.887, max_damage=412.313, mana_cost=260, cast_time=3, wowhead_id=10181),
        SpellRank(rank=11, level=60, min_damage=470.043, max_damage=505.557, mana_cost=290, cast_time=3, wowhead_id=25304),
    ],
    SpellId.FROSTFIRE_BOLT: [
        SpellRank(rank=1, level=40, min_damage=96, max_damage=113, mana_cost=205, cast_time=3, dot=DotData(damage=29, duration=10, ticks=5), wowhead_id=401502, confirmed_in_game_date="2026-09-26"),
        SpellRank(rank=2, level=50, min_damage=172, max_damage=201, mana_cost=285, cast_time=3, dot=DotData(damage=43, duration=10, ticks=5), wowhead_id=1237312, confirmed_in_game_date="2026-09-26"),
        SpellRank(rank=3, level=60, min_damage=274, max_damage=319, mana_cost=370, cast_time=3, dot=DotData(damage=63, duration=10, ticks=5), wowhead_id=1237313, confirmed_in_game_date="2026-09-26"),
    ],
    SpellId.FIRE_BLAST: [
        SpellRank(rank=1, level=6, min_damage=29, max_damage=38, mana_cost=40, cooldown=8, wowhead_id=2136, confirmed_in_game_date="2026-09-26"),
        SpellRank(rank=2, level=14, min_damage=55, max_damage=68, mana_cost=75, cooldown=8, wowhead_id=2137, confirmed_in_game_date="2026-09-26"),
        SpellRank(rank=3, level=22, min_damage=97, max_damage=117, mana_cost=115, cooldown=8, wowhead_id=2138),
        SpellRank(rank=4, level=30, min_damage=157, max_damage=187, mana_cost=165, cooldown=8, wowhead_id=8412),
        SpellRank(rank=5, level=38, min_damage=226, max_damage=268, mana_cost=220, cooldown=8, wowhead_id=8413),
        SpellRank(rank=6, level=46, min_damage=316, max_damage=372, mana_cost=280, cooldown=8, wowhead_id=10197),
        SpellRank(rank=7, level=54, min_damage=417, max_damage=489, mana_cost=340, cooldown=8, wowhead_id=10199),
    ],
    SpellId.SCORCH: [
        SpellRank(rank=1, level=22, min_damage=37, max_damage=46, mana_cost=50, cast_time=1.5, wowhead_id=2948, confirmed_in_game_date="2026-09-26"),
        SpellRank(rank=2, level=28, min_damage=54, max_damage=64, mana_cost=65, cast_time=1.5, wowhead_id=8444),
        SpellRank(rank=3, level=34, min_damage=67, max_damage=79, mana_cost=80, cast_time=1.5, wowhead_id=8445),
        SpellRank(rank=4, level=40, min_damage=90, max_damage=106, mana_cost=100, cast_time=1.5, wowhead_id=8446),
        SpellRank(rank=5, level=46, min_damage=112, max_damage=131, mana_cost=115, cast_time=1.5, wowhead_id=10205),
        SpellRank(rank=6, level=52, min_damage=143, max_damage=169, mana_cost=135, cast_time=1.5, wowhead_id=10206),
        SpellRank(rank=7, level=58, min_damage=170, max_damage=200, mana_cost=150, cast_time=1.5, wowhead_id=10207),
    ],
    SpellId.PYROBLAST: [
        SpellRank(rank=1, level=20, min_damage=100, max_damage=130, mana_cost=125, cast_time=6, dot=DotData(damage=47, duration=12, ticks=4), wowhead_id=11366, confirmed_in_game_date="2026-09-26"),
        SpellRank(rank=2, level=24, min_damage=126, max_damage=162, mana_cost=150, cast_time=6, dot=DotData(damage=56, duration=12, ticks=4), wowhead_id=12505),
        SpellRank(rank=3, level=30, min_damage=180, max_damage=227, mana_cost=195, cast_time=6, dot=DotData(damage=76, duration=12, ticks=4), wowhead_id=12522),
        SpellRank(rank=4, level=36, min_damage=230, max_damage=289, mana_cost=240, cast_time=6, dot=DotData(damage=100, duration=12, ticks=4), wowhead_id=12523),
        SpellRank(rank=5, level=42, min_damage=291, max_damage=364, mana_cost=285, cast_time=6, dot=DotData(damage=124, duration=12, ticks=4), wowhead_id=12524),
        SpellRank(rank=6, level=48, min_damage=368, max_damage=456, mana_cost=335, cast_time=6, dot=DotData(damage=152, duration=12, ticks=4), wowhead_id=12525),
        SpellRank(rank=7, level=54, min_damage=448, max_damage=555, mana_cost=385, cast_time=6, dot=DotData(damage=184, duration=12, ticks=4), wowhead_id=12526),
        SpellRank(rank=8, level=60, min_damage=547, max_damage=674, mana_cost=440, cast_time=6, dot=DotData(damage=212, duration=12, ticks=4), wowhead_id=18809),
    ],
    SpellId.BLAST_WAVE: [
        SpellRank(rank=1, level=30, min_damage=148, max_damage=179, mana_cost=215, cooldown=45, wowhead_id=11113, confirmed_in_game_date="2026-09-26"),
        SpellRank(rank=2, level=36, min_damage=200, max_damage=238, mana_cost=270, cooldown=45, wowhead_id=13018),
        SpellRank(rank=3, level=44, min_damage=276, max_damage=327, mana_cost=355, cooldown=45, wowhead_id=13019),
        SpellRank(rank=4, level=52, min_damage=365, max_damage=432, mana_cost=450, cooldown=45, wowhead_id=13020),
        SpellRank(rank=5, level=60, min_damage=464, max_damage=545, mana_cost=545, cooldown=45, wowhead_id=13021),
    ],
    SpellId.FLAMESTRIKE: [
        SpellRank(rank=1, level=16, min_damage=55, max_damage=71, mana_cost=195, cast_time=3, dot=DotData(damage=44, duration=8, ticks=4), wowhead_id=2120),
        SpellRank(rank=2, level=24, min_damage=100, max_damage=126, mana_cost=330, cast_time=3, dot=DotData(damage=84, duration=8, ticks=4), wowhead_id=2121),
        SpellRank(rank=3, level=32, min_damage=159, max_damage=197, mana_cost=490, cast_time=3, dot=DotData(damage=132, duration=8, ticks=4), wowhead_id=8422),
        SpellRank(rank=4, level=40, min_damage=227, max_damage=279, mana_cost=650, cast_time=3, dot=DotData(damage=188, duration=8, ticks=4), wowhead_id=8423),
        SpellRank(rank=5, level=48, min_damage=299, max_damage=367, mana_cost=815, cast_time=3, dot=DotData(damage=256, duration=8, ticks=4), wowhead_id=10215),
        SpellRank(rank=6, level=56, min_damage=384, max_damage=468, mana_cost=990, cast_time=3, dot=DotData(damage=332, duration=8, ticks=4), wowhead_id=10216),
    ],
    SpellId.ARCANE_MISSILES: [
        SpellRank(rank=1, level=8, min_damage=26, max_damage=26, mana_cost=85, cast_time=3, channel_ticks=3, wowhead_id=5143, confirmed_in_game_date="2026-09-26"),
        SpellRank(rank=2, level=16, min_damage=32, max_damage=32, mana_cost=140, cast_time=4, channel_ticks=4, wowhead_id=5144, confirmed_in_game_date="2026-09-26"),
        SpellRank(rank=3, level=24, min_damage=46, max_damage=46, mana_cost=235, cast_time=5, channel_ticks=5, wowhead_id=5145),
        SpellRank(rank=4, level=32, min_damage=68, max_damage=68, mana_cost=320, cast_time=5, channel_ticks=5, wowhead_id=8416),
        SpellRank(rank=5, level=40, min_damage=98, max_damage=98, mana_cost=410, cast_time=5, channel_ticks=5, wowhead_id=8417),
        SpellRank(rank=6, level=48, min_damage=133, max_damage=133, mana_cost=500, cast_time=5, channel_ticks=5, wowhead_id=10211),
        SpellRank(rank=7, level=56, min_damage=175, max_damage=175, mana_cost=595, cast_time=5, channel_ticks=5, wowhead_id=10212),
        SpellRank(rank=8, level=56, min_damage=213, max_damage=213, mana_cost=655, cast_time=5, channel_ticks=5, wowhead_id=25345),
    ],
    SpellId.ARCANE_EXPLOSION: [
        SpellRank(rank=1, level=14, min_damage=32, max_damage=36, mana_cost=75, wowhead_id=1449),
        SpellRank(rank=2, level=22, min_damage=55, max_damage=61, mana_cost=120, wowhead_id=8437),
        SpellRank(rank=3, level=30, min_damage=95, max_damage=102, mana_cost=185, wowhead_id=8438),
        SpellRank(rank=4, level=38, min_damage=134, max_damage=145, mana_cost=250, wowhead_id=8439),
        SpellRank(rank=5, level=46, min_damage=181, max_damage=196, mana_cost=315, wowhead_id=10201),
        SpellRank(rank=6, level=54, min_damage=239, max_damage=258, mana_cost=390, wowhead_id=10202),
    ],
    SpellId.ARCANE_BLAST: [
        SpellRank(rank=1, level=20, min_damage=53, max_damage=62, base_mana_pct=15, cast_time=2.5, wowhead_id=400574, confirmed_in_game_date="2026-09-26"),
        SpellRank(rank=2, level=30, min_damage=131, max_damage=151, base_mana_pct=15, cast_time=2.5, wowhead_id=1239696),
        SpellRank(rank=3, level=40, min_damage=169, max_damage=195, base_mana_pct=15, cast_time=2.5, wowhead_id=1239697),
        SpellRank(rank=4, level=50, min_damage=270, max_damage=311, base_mana_pct=15, cast_time=2.5, wowhead_id=1239699),
        SpellRank(rank=5, level=60, min_damage=385, max_damage=445, base_mana_pct=15, cast_time=2.5, wowhead_id=1239700),
    ],
    SpellId.FROST_NOVA: [
        SpellRank(rank=1, level=10, min_damage=21.5, max_damage=23.5, mana_cost=55, cooldown=25, wowhead_id=122),
        SpellRank(rank=2, level=26, min_damage=34.5571, max_damage=38.4429, mana_cost=85, cooldown=25, wowhead_id=865),
        SpellRank(rank=3, level=40, min_damage=52.6091, max_damage=58.3909, mana_cost=115, cooldown=25, wowhead_id=6131),
        SpellRank(rank=4, level=54, min_damage=71.6067, max_damage=79.3933, mana_cost=145, cooldown=25, wowhead_id=10230),
    ],
    SpellId.CONE_OF_COLD: [
        SpellRank(rank=1, level=26, min_damage=96.2913, max_damage=105.709, mana_cost=210, cooldown=10, wowhead_id=120),
        SpellRank(rank=2, level=34, min_damage=142.412, max_damage=155.588, mana_cost=290, cooldown=10, wowhead_id=8492),
        SpellRank(rank=3, level=42, min_damage=200.423, max_damage=219.577, mana_cost=380, cooldown=10, wowhead_id=10159),
        SpellRank(rank=4, level=50, min_damage=260.969, max_damage=286.031, mana_cost=465, cooldown=10, wowhead_id=10160),
        SpellRank(rank=5, level=58, min_damage=332.929, max_damage=362.071, mana_cost=555, cooldown=10, wowhead_id=10161),
    ],
    SpellId.BLIZZARD: [
        SpellRank(rank=1, level=20, min_damage=24.5, max_damage=24.5, mana_cost=320, cast_time=8, channel_ticks=8, wowhead_id=10),
        SpellRank(rank=2, level=28, min_damage=43, max_damage=43, mana_cost=520, cast_time=8, channel_ticks=8, wowhead_id=6141),
        SpellRank(rank=3, level=36, min_damage=63, max_damage=63, mana_cost=720, cast_time=8, channel_ticks=8, wowhead_id=8427),
        SpellRank(rank=4, level=44, min_damage=88.5, max_damage=88.5, mana_cost=935, cast_time=8, channel_ticks=8, wowhead_id=10185),
        SpellRank(rank=5, level=52, min_damage=115.5, max_damage=115.5, mana_cost=1160, cast_time=8, channel_ticks=8, wowhead_id=10186),
        SpellRank(rank=6, level=60, min_damage=148, max_damage=148, mana_cost=1400, cast_time=8, channel_ticks=8, wowhead_id=10187),
    ],
    SpellId.ICE_LANCE: [
        SpellRank(rank=1, level=20, min_damage=26, max_damage=30, mana_cost=45, wowhead_id=1312002, confirmed_in_game_date="2026-09-26"),
        SpellRank(rank=2, level=28, min_damage=35, max_damage=41, mana_cost=55, wowhead_id=400640),
        SpellRank(rank=3, level=34, min_damage=44, max_damage=52, mana_cost=70, wowhead_id=1240044),
        SpellRank(rank=4, level=42, min_damage=77, max_damage=90, mana_cost=105, wowhead_id=1240045),
        SpellRank(rank=5, level=48, min_damage=95, max_damage=112, mana_cost=120, wowhead_id=1240046),
        SpellRank(rank=6, level=56, min_damage=140, max_damage=164, mana_cost=160, wowhead_id=1240047),
    ],
}
