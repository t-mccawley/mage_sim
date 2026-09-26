"""Candidate generation and validation.

Rotation/encounter pairs of different types are not candidates. Every other
combination is a candidate; it is invalid when talent level, rank overrides,
or the spells its rotation uses are impossible for the character.
"""

import itertools
import random
from dataclasses import dataclass

from magesim.engine.simulator import Simulation
from magesim.engine.state import UnavailableSpellError
from magesim.model.character import Character
from magesim.model.encounter import Encounter
from magesim.model.meta import MetaConfig
from magesim.model.rotation import Rotation
from magesim.model.rotation_analysis import used_spells
from magesim.spells.availability import resolve_rank
from magesim.spells.definitions import SpellCatalog
from magesim.talents.build import TalentBuild
from magesim.talents.effects import TalentModifiers

PROBE_SEED = "probe"


@dataclass(frozen=True, slots=True, kw_only=True)
class Candidate:
    """One character + encounter + rotation + talents combination."""

    number: int
    character: Character
    encounter: Encounter
    rotation: Rotation
    talents: TalentBuild

    @property
    def label(self) -> str:
        """Short legend label."""
        return f"#{self.number}"


@dataclass(frozen=True, slots=True, kw_only=True)
class InvalidCandidate:
    """A combination that cannot happen in game, with the reasons why."""

    character: Character
    encounter: Encounter
    rotation: Rotation
    talents: TalentBuild
    reasons: tuple[str, ...]

    @classmethod
    def of(cls, candidate: Candidate, reason: str) -> "InvalidCandidate":
        """Reject a candidate found invalid while simulating."""
        return cls(
            character=candidate.character,
            encounter=candidate.encounter,
            rotation=candidate.rotation,
            talents=candidate.talents,
            reasons=(reason,),
        )


@dataclass(frozen=True, slots=True)
class CandidatePlan:
    """Valid candidates (numbered from 1) and rejected combinations."""

    valid: list[Candidate]
    invalid: list[InvalidCandidate]


def static_problems(
    character: Character, rotation: Rotation, talents: TalentBuild, catalog: SpellCatalog
) -> list[str]:
    """Problems detectable without simulating."""
    problems = []
    if talents.required_level != character.level:
        problems.append(
            f"talents require level {talents.required_level}, character is level {character.level}"
        )
    granted = TalentModifiers.from_build(talents).granted_spells
    for spell_id, rank in rotation.rank_overrides.items():
        resolution = resolve_rank(catalog[spell_id], character.level, granted, rank)
        if resolution.rank is None:
            problems.append(f"rank override: {spell_id.value} {resolution.reason}")
    for spell_id in sorted(
        used_spells(rotation.rotation_function) - rotation.rank_overrides.keys()
    ):
        resolution = resolve_rank(catalog[spell_id], character.level, granted)
        if resolution.rank is None:
            problems.append(str(UnavailableSpellError(spell_id.value, resolution.reason or "")))
    return problems


def probe_problem(
    character: Character,
    encounter: Encounter,
    rotation: Rotation,
    talents: TalentBuild,
    catalog: SpellCatalog,
    meta: MetaConfig,
) -> str | None:
    """Run one iteration; report a spell the rotation uses but cannot have."""
    sim = Simulation(
        character,
        encounter,
        talents,
        rotation,
        catalog,
        tick_seconds=meta.tick_seconds,
        peak_warmup_seconds=meta.peak_warmup_seconds,
    )
    try:
        sim.run(random.Random(PROBE_SEED))
    except UnavailableSpellError as error:
        return str(error)
    return None


def plan_candidates(
    characters: list[Character],
    encounters: list[Encounter],
    rotations: list[Rotation],
    talents: list[TalentBuild],
    catalog: SpellCatalog,
    meta: MetaConfig,
) -> CandidatePlan:
    """Validate every same-type combination and number the valid ones."""
    valid: list[Candidate] = []
    invalid: list[InvalidCandidate] = []
    for character, encounter, rotation, build in itertools.product(
        characters, encounters, rotations, talents
    ):
        if rotation.encounter_type is not encounter.encounter_type:
            continue
        problems = static_problems(character, rotation, build, catalog)
        if not problems:
            problem = probe_problem(character, encounter, rotation, build, catalog, meta)
            problems = [problem] if problem else []
        if problems:
            invalid.append(
                InvalidCandidate(
                    character=character,
                    encounter=encounter,
                    rotation=rotation,
                    talents=build,
                    reasons=tuple(problems),
                )
            )
            continue
        valid.append(
            Candidate(
                number=len(valid) + 1,
                character=character,
                encounter=encounter,
                rotation=rotation,
                talents=build,
            )
        )
    return CandidatePlan(valid, invalid)
