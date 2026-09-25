"""Talent effects on damage, cost, and timing.

Per-rank values come from WoW Forever talent descriptions (Wowhead).
"""

from collections import defaultdict
from dataclasses import dataclass, field
from typing import Final

from magesim.core.enums import School
from magesim.spells.definitions import SpellId
from magesim.spells.spellbook import SPELLBOOK
from magesim.talents.build import TalentBuild

# Talents with no effect on simulated damage.
NO_DAMAGE_EFFECT: Final = frozenset(
    {
        "Wand Specialization",
        "Improved Channeling",
        "Arcane Subtlety",
        "Magic Absorption",
        "Arcane Resilience",
        "Arcane Geometry",
        "Flame Throwing",
        "Impact",
        "Burning Soul",
        "Frost Warding",
        "Permafrost",
    }
)

# Talents modeled by TalentModifiers.
_IMPLEMENTED: Final = frozenset(
    {
        "Arcane Focus",
        "Arcane Concentration",
        "Arcane Impact",
        "Arcane Blast",
        "Wake of Fire",
        "Incineration",
        "Improved Fireball",
        "Ignite",
        "Improved Flamestrike",
        "Pyroblast",
        "Improved Frostbolt",
        "Elemental Precision",
        "Ice Shards",
        "Improved Frost Nova",
        "Frostbite",
        "Piercing Ice",
        "Frost Channeling",
        "Ice Lance",
        "Improved Blizzard",
    }
)


@dataclass(frozen=True, slots=True, kw_only=True)
class TalentModifiers:
    """Aggregated talent effects. Percent values are in percent."""

    hit_pct: dict[School, float] = field(default_factory=dict)
    crit_pct_school: dict[School, float] = field(default_factory=dict)
    crit_pct_spell: dict[SpellId, float] = field(default_factory=dict)
    crit_damage_bonus: dict[School, float] = field(default_factory=dict)
    damage_multiplier: dict[School, float] = field(default_factory=dict)
    cost_multiplier: dict[School, float] = field(default_factory=dict)
    cast_time_reduction: dict[SpellId, float] = field(default_factory=dict)
    cooldown_reduction: dict[SpellId, float] = field(default_factory=dict)
    granted_spells: frozenset[SpellId] = frozenset()
    clearcasting_chance: float = 0.0
    ignite_fraction: float = 0.0
    frostbite_chance: float = 0.0
    blizzard_chills: bool = False
    wake_of_fire_crit_pct: float = 0.0
    unimplemented: tuple[str, ...] = ()

    @classmethod
    def from_build(cls, build: TalentBuild) -> "TalentModifiers":
        """Compute modifiers from talent ranks."""
        r = build.rank
        hit: defaultdict[School, float] = defaultdict(float)
        hit[School.ARCANE] += 1.0 * r("Arcane Focus")
        hit[School.FIRE] += 1.0 * r("Elemental Precision")
        hit[School.FROST] += 1.0 * r("Elemental Precision")

        crit_spell: defaultdict[SpellId, float] = defaultdict(float)
        for spell in (SpellId.FIRE_BLAST, SpellId.ICE_LANCE, SpellId.ARCANE_BLAST, SpellId.SCORCH):
            crit_spell[spell] += 2.0 * r("Incineration")
        crit_spell[SpellId.FLAMESTRIKE] += 5.0 * r("Improved Flamestrike")

        granted = frozenset(
            s.spell_id
            for s in SPELLBOOK.values()
            if s.granted_by_talent is not None and r(s.granted_by_talent) > 0
        )
        known = NO_DAMAGE_EFFECT | _IMPLEMENTED
        return cls(
            hit_pct=dict(hit),
            crit_pct_school={School.ARCANE: 2.0 * r("Arcane Impact")},
            crit_pct_spell=dict(crit_spell),
            crit_damage_bonus={School.FROST: 0.2 * r("Ice Shards")},
            damage_multiplier={School.FROST: 1.0 + 0.02 * r("Piercing Ice")},
            cost_multiplier={School.FROST: 1.0 - 0.05 * r("Frost Channeling")},
            cast_time_reduction={
                SpellId.FIREBALL: 0.1 * r("Improved Fireball"),
                SpellId.FROSTBOLT: 0.1 * r("Improved Frostbolt"),
            },
            cooldown_reduction={
                SpellId.FIRE_BLAST: 1.0 * r("Wake of Fire"),
                SpellId.FROST_NOVA: 2.0 * r("Improved Frost Nova"),
            },
            granted_spells=granted,
            clearcasting_chance=0.02 * r("Arcane Concentration"),
            ignite_fraction=0.08 * r("Ignite"),
            frostbite_chance=0.05 * r("Frostbite"),
            blizzard_chills=r("Improved Blizzard") > 0,
            wake_of_fire_crit_pct=25.0 * r("Wake of Fire"),
            unimplemented=tuple(sorted(name for name in build.ranks if name not in known)),
        )
