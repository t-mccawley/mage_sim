"""Shared enumerations."""

from enum import IntEnum, StrEnum


class School(StrEnum):
    """Magic school of a spell."""

    ARCANE = "arcane"
    FIRE = "fire"
    FROST = "frost"


class TalentTree(StrEnum):
    """Mage talent trees, in in-game order."""

    ARCANE = "Arcane"
    FIRE = "Fire"
    FROST = "Frost"


class EncounterType(StrEnum):
    """Encounter kind; rotations only run against encounters of the same type."""

    SINGLE_TARGET = "single_target"
    MULTI_TARGET_AOE = "multi_target_aoe"
    MULTI_TARGET_LEVELING = "multi_target_leveling"


class LevelDelta(IntEnum):
    """Enemy level relative to the character."""

    MINUS_3_OR_LESS = -3
    MINUS_2 = -2
    MINUS_1 = -1
    SAME = 0
    PLUS_1 = 1
    PLUS_2 = 2
    PLUS_3 = 3


class CastKind(StrEnum):
    """How a spell occupies the caster."""

    INSTANT = "instant"
    CAST = "cast"
    CHANNEL = "channel"


class Targeting(StrEnum):
    """Which enemies a spell hits."""

    SINGLE = "single"
    AOE = "aoe"


class HitOutcome(StrEnum):
    """Result of a damage roll."""

    MISS = "miss"
    HIT = "hit"
    CRIT = "crit"
