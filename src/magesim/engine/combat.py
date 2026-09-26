"""Hit, crit, and resist math (Classic formulas via wowsims/classic)."""

import random
from dataclasses import dataclass

from magesim.core.constants import (
    BASE_SPELL_MISS,
    MIN_SPELL_MISS,
    PARTIAL_RESIST_PER_LEVEL,
    SPELL_CRIT_MULTIPLIER,
    SPELL_CRIT_SUPPRESSION,
)
from magesim.core.enums import HitOutcome, LevelDelta
from magesim.model.character import Character
from magesim.spells.definitions import SpellDefinition
from magesim.talents.effects import TalentModifiers

_MAX_PARTIAL_RESIST = 0.75


def level_delta(character_level: int, enemy_level: int) -> LevelDelta:
    """Enemy-minus-character level, clamped to the LevelDelta range."""
    delta = enemy_level - character_level
    return LevelDelta(max(min(delta, LevelDelta.PLUS_3), LevelDelta.MINUS_3_OR_LESS))


def hit_chance(delta: LevelDelta, hit_pct: float) -> float:
    """Chance a spell lands (before partial resists)."""
    miss = max(BASE_SPELL_MISS[delta] - hit_pct / 100.0, MIN_SPELL_MISS)
    return 1.0 - miss


def crit_multiplier(crit_damage_bonus: float) -> float:
    """Damage multiplier on crit; bonus scales the extra 50%."""
    return 1.0 + (SPELL_CRIT_MULTIPLIER - 1.0) * (1.0 + crit_damage_bonus)


@dataclass(frozen=True, slots=True)
class ResistTable:
    """Partial resist roll thresholds for 25/50/75% resists."""

    no_resist: float
    resist_25: float
    resist_50: float

    @classmethod
    def for_level_gap(cls, level_gap: int) -> "ResistTable":
        """Level-based partial resists against higher-level enemies."""
        coef = min(max(level_gap, 0) * PARTIAL_RESIST_PER_LEVEL / _MAX_PARTIAL_RESIST, 1.0)
        val = coef * 3.0
        if val <= 1.0:
            return cls(0.76 * val, 0.21 * val, 0.03 * val)
        if val <= 2.0:
            val -= 1.0
            return cls(0.76 + 0.24 * val, 0.21 + 0.57 * val, 0.03 + 0.19 * val)
        val -= 2.0
        return cls(1.0, 0.78 + 0.18 * val, 0.22 + 0.58 * val)

    def roll_multiplier(self, rng: random.Random) -> float:
        """Random damage multiplier after partial resists."""
        if self.no_resist <= 0.0:
            return 1.0
        roll = rng.random()
        if roll > self.no_resist:
            return 1.0
        if roll > self.resist_25:
            return 0.75
        if roll > self.resist_50:
            return 0.5
        return 0.25


@dataclass(frozen=True, slots=True)
class SpellProfile:
    """Precomputed combat numbers for one spell against one enemy level."""

    hit_chance: float
    crit_chance: float
    crit_multiplier: float
    spell_power: float
    damage_multiplier: float

    @classmethod
    def build(
        cls,
        character: Character,
        mods: TalentModifiers,
        spell: SpellDefinition,
        delta: LevelDelta,
    ) -> "SpellProfile":
        """Combine character stats and talents for `spell`.

        A multi-school spell uses its best school for hit, crit, crit damage, and
        spell power, and gets every school's damage multiplier.
        """
        schools = spell.schools
        hit_pct = max(character.spell_hit.for_school(s) + mods.hit_pct.get(s, 0.0) for s in schools)
        crit_pct = max(
            character.spell_crit.for_school(s) + mods.crit_pct_school.get(s, 0.0) for s in schools
        ) + mods.crit_pct_spell.get(spell.spell_id, 0.0)
        crit = max(crit_pct / 100.0 - SPELL_CRIT_SUPPRESSION.get(delta, 0.0), 0.0)
        damage_multiplier = 1.0
        for s in schools:
            damage_multiplier *= mods.damage_multiplier.get(s, 1.0)
        return cls(
            hit_chance=hit_chance(delta, hit_pct),
            crit_chance=min(crit, 1.0),
            crit_multiplier=crit_multiplier(
                max(mods.crit_damage_bonus.get(s, 0.0) for s in schools)
            ),
            spell_power=max(character.spell_power.for_school(s) for s in schools),
            damage_multiplier=damage_multiplier,
        )

    def roll_outcome(self, rng: random.Random, bonus_crit: float = 0.0) -> HitOutcome:
        """Roll miss, then crit."""
        if rng.random() >= self.hit_chance:
            return HitOutcome.MISS
        if rng.random() < self.crit_chance + bonus_crit:
            return HitOutcome.CRIT
        return HitOutcome.HIT
