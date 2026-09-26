"""Rotation configuration."""

from collections.abc import Callable
from dataclasses import dataclass, field

from magesim.core.enums import EncounterType
from magesim.engine.state import SpellHandle
from magesim.engine.views import SimState
from magesim.spells.definitions import SpellId

type SpellChoice = SpellHandle | SpellId | None
"""A rotation's pick: a spell, or None to wait this tick."""

type RotationFunction = Callable[[SimState], SpellChoice]


@dataclass(frozen=True, slots=True, kw_only=True)
class Rotation:
    """A priority function called whenever the caster is free to act.

    Spells cast at the highest rank known at the character's level unless
    `rank_overrides` pins a rank, e.g. {SpellId.FROSTBOLT: 1}.
    """

    display_name: str
    description: str
    encounter_type: EncounterType
    rotation_function: RotationFunction
    rank_overrides: dict[SpellId, int] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if any(rank < 1 for rank in self.rank_overrides.values()):
            raise ValueError(f"{self.display_name}: rank overrides must be >= 1")
