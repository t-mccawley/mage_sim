"""Game mechanics constants (Classic formulas via wowsims/classic)."""

from typing import Final

from magesim.core.enums import LevelDelta

MIN_LEVEL: Final = 1
MAX_LEVEL: Final = 60

GCD_SECONDS: Final = 1.5

# Spell hit table: base miss chance by enemy level delta, floored at 1%.
BASE_SPELL_MISS: Final[dict[LevelDelta, float]] = {
    LevelDelta.MINUS_3_OR_LESS: 0.01,
    LevelDelta.MINUS_2: 0.02,
    LevelDelta.MINUS_1: 0.03,
    LevelDelta.SAME: 0.04,
    LevelDelta.PLUS_1: 0.05,
    LevelDelta.PLUS_2: 0.06,
    LevelDelta.PLUS_3: 0.17,
}
MIN_SPELL_MISS: Final = 0.01

# Crit chance removed by higher-level enemies.
SPELL_CRIT_SUPPRESSION: Final[dict[LevelDelta, float]] = {
    LevelDelta.PLUS_2: 0.003,
    LevelDelta.PLUS_3: 0.021,
}

SPELL_CRIT_MULTIPLIER: Final = 1.5

# Average partial resist added per enemy level above the caster.
PARTIAL_RESIST_PER_LEVEL: Final = 0.02

# Mage spirit regen per second: (12.5 + Spirit / 4) per 2 s tick.
SPIRIT_REGEN_BASE_PER_SECOND: Final = 6.25
SPIRIT_REGEN_PER_SPIRIT_PER_SECOND: Final = 1.0 / 8.0
FIVE_SECOND_RULE_SECONDS: Final = 5.0
MP5_INTERVAL_SECONDS: Final = 5.0

# Mana from intellect: first 20 points give 1 mana each, the rest 15.
INTELLECT_MANA_THRESHOLD: Final = 20
MANA_PER_INTELLECT: Final = 15

# Spells learned below level 20 lose power: 3.75% per level under 20.
LOW_LEVEL_PENALTY_LEVEL: Final = 20
LOW_LEVEL_PENALTY_PER_LEVEL: Final = 0.0375

# Frozen targets take extra Ice Lance damage.
ICE_LANCE_FROZEN_MULTIPLIER: Final = 4.0
