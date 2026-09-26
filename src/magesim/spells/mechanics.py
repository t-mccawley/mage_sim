"""Fixed spell mechanics and catalog assembly.

Scales marked "wowsims" are Blizzard's per-spell adjustments, fitted so the
calculated coefficients match wowsims/classic for every Classic rank.
"""

from collections.abc import Mapping, Sequence
from typing import Final

from magesim.core.enums import CastKind, School, Targeting
from magesim.spells.coefficients import AOE_SCALE, CONTROL_EFFECT_SCALE
from magesim.spells.definitions import (
    SpellCatalog,
    SpellDefinition,
    SpellId,
    SpellMechanics,
    SpellRank,
)

SPELL_MECHANICS: Final[dict[SpellId, SpellMechanics]] = {
    m.spell_id: m
    for m in (
        SpellMechanics(
            spell_id=SpellId.FIREBALL,
            school=School.FIRE,
            cast_kind=CastKind.CAST,
            targeting=Targeting.SINGLE,
            dot_scale=0.0,
            scale_note="DoT does not scale with spell power",
        ),
        SpellMechanics(
            spell_id=SpellId.FROSTBOLT,
            school=School.FROST,
            cast_kind=CastKind.CAST,
            targeting=Targeting.SINGLE,
            direct_scale=CONTROL_EFFECT_SCALE,
            scale_note="slow effect",
            chills=True,
        ),
        SpellMechanics(
            spell_id=SpellId.FIRE_BLAST,
            school=School.FIRE,
            cast_kind=CastKind.INSTANT,
            targeting=Targeting.SINGLE,
        ),
        SpellMechanics(
            spell_id=SpellId.ARCANE_MISSILES,
            school=School.ARCANE,
            cast_kind=CastKind.CHANNEL,
            targeting=Targeting.SINGLE,
            direct_scale=0.84,
            scale_note="wowsims",
        ),
        SpellMechanics(
            spell_id=SpellId.ARCANE_EXPLOSION,
            school=School.ARCANE,
            cast_kind=CastKind.INSTANT,
            targeting=Targeting.AOE,
            direct_scale=AOE_SCALE,
            scale_note="AoE",
        ),
        SpellMechanics(
            spell_id=SpellId.FROST_NOVA,
            school=School.FROST,
            cast_kind=CastKind.INSTANT,
            targeting=Targeting.AOE,
            direct_scale=AOE_SCALE * CONTROL_EFFECT_SCALE,
            scale_note="AoE, root effect",
            freeze_duration=8.0,
        ),
        SpellMechanics(
            spell_id=SpellId.FLAMESTRIKE,
            school=School.FIRE,
            cast_kind=CastKind.CAST,
            targeting=Targeting.AOE,
            direct_scale=0.1832,
            dot_scale=0.15,
            scale_note="wowsims",
        ),
        SpellMechanics(
            spell_id=SpellId.BLIZZARD,
            school=School.FROST,
            cast_kind=CastKind.CHANNEL,
            targeting=Targeting.AOE,
            direct_scale=0.147,
            scale_note="wowsims",
        ),
        SpellMechanics(
            spell_id=SpellId.SCORCH,
            school=School.FIRE,
            cast_kind=CastKind.CAST,
            targeting=Targeting.SINGLE,
        ),
        SpellMechanics(
            spell_id=SpellId.PYROBLAST,
            school=School.FIRE,
            cast_kind=CastKind.CAST,
            targeting=Targeting.SINGLE,
            dot_scale=0.75,
            scale_note="wowsims",
            granted_by_talent="Pyroblast",
        ),
        SpellMechanics(
            spell_id=SpellId.ICE_LANCE,
            school=School.FROST,
            cast_kind=CastKind.INSTANT,
            targeting=Targeting.SINGLE,
            scale_note="new in Forever; standard formula",
            granted_by_talent="Ice Lance",
        ),
        SpellMechanics(
            spell_id=SpellId.ARCANE_BLAST,
            school=School.ARCANE,
            cast_kind=CastKind.CAST,
            targeting=Targeting.SINGLE,
            scale_note="new in Forever; standard formula",
            granted_by_talent="Arcane Blast",
        ),
        SpellMechanics(
            spell_id=SpellId.FROSTFIRE_BOLT,
            school=School.FIRE,
            extra_schools=(School.FROST,),
            cast_kind=CastKind.CAST,
            targeting=Targeting.SINGLE,
            direct_scale=CONTROL_EFFECT_SCALE,
            scale_note="new in Forever; standard formula, slow effect",
            chills=True,
        ),
        SpellMechanics(
            spell_id=SpellId.BLAST_WAVE,
            school=School.FIRE,
            cast_kind=CastKind.INSTANT,
            targeting=Targeting.AOE,
            direct_scale=0.301,
            scale_note="wowsims",
            granted_by_talent="Blast Wave",
        ),
        SpellMechanics(
            spell_id=SpellId.CONE_OF_COLD,
            school=School.FROST,
            cast_kind=CastKind.INSTANT,
            targeting=Targeting.AOE,
            direct_scale=AOE_SCALE * CONTROL_EFFECT_SCALE,
            scale_note="AoE, slow effect",
            chills=True,
        ),
    )
}

# Arcane Blast buff: per stack, +10% damage to other spells and +175% own cost.
ARCANE_BLAST_MAX_STACKS: Final = 4
ARCANE_BLAST_DAMAGE_PER_STACK: Final = 0.10
ARCANE_BLAST_COST_PER_STACK: Final = 1.75
ARCANE_BLAST_DURATION: Final = 8.0


def build_catalog(ranks: Mapping[SpellId, Sequence[SpellRank]]) -> SpellCatalog:
    """Combine mechanics with configured ranks; spells without ranks are never known."""
    return {
        spell_id: SpellDefinition(mechanics, tuple(ranks.get(spell_id, ())))
        for spell_id, mechanics in SPELL_MECHANICS.items()
    }
