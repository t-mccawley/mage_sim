"""Candidate generation from configs."""

import itertools
from dataclasses import dataclass

from magesim.model.character import Character
from magesim.model.encounter import Encounter
from magesim.model.rotation import Rotation
from magesim.talents.build import TalentBuild


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


def is_compatible(
    character: Character, encounter: Encounter, rotation: Rotation, talents: TalentBuild
) -> bool:
    """Rotation matches encounter type and talents match character level."""
    return (
        rotation.encounter_type is encounter.encounter_type
        and talents.required_level == character.level
    )


def build_candidates(
    characters: list[Character],
    encounters: list[Encounter],
    rotations: list[Rotation],
    talents: list[TalentBuild],
) -> list[Candidate]:
    """All compatible combinations, numbered from 1."""
    combos = [
        combo
        for combo in itertools.product(characters, encounters, rotations, talents)
        if is_compatible(*combo)
    ]
    return [
        Candidate(number=i, character=c, encounter=e, rotation=r, talents=t)
        for i, (c, e, r, t) in enumerate(combos, start=1)
    ]
