"""Rotation configuration."""

from collections.abc import Callable
from dataclasses import dataclass

from magesim.core.enums import EncounterType
from magesim.engine.state import SpellHandle
from magesim.engine.views import SimState
from magesim.spells.definitions import SpellId

type SpellChoice = SpellHandle | SpellId | None
"""A rotation's pick: a spell, or None to wait this tick."""

type RotationFunction = Callable[[SimState], SpellChoice]


@dataclass(frozen=True, slots=True, kw_only=True)
class Rotation:
    """A priority function called whenever the caster is free to act."""

    display_name: str
    description: str
    encounter_type: EncounterType
    rotation_function: RotationFunction
