"""Character stats, copied from the in-game character sheet (after gear and buffs).

Percent stats are in percent (5.5 = 5.5%).
"""

from magesim import Character, SchoolValues, Water

CHARACTERS: list[Character] = [
    Character(
        display_name="Mage L20",
        level=20,
        intellect=50,
        spirit=55,
        mana=720,
        mp5=0,
        spell_power=SchoolValues(general=0),
        spell_crit=SchoolValues(general=1.6),
        spell_hit=SchoolValues(general=0),
        water=Water.CONJURED_PURIFIED_WATER,
    ),
]
