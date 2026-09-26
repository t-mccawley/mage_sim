"""MageSim: WoW Forever mage DpS simulator.

Configs import everything they need from here.
"""

from magesim.core.enums import EncounterType, LevelDelta, School
from magesim.engine.state import SpellHandle
from magesim.engine.views import SimState, SpellBook, TargetView
from magesim.model.character import Character, SchoolValues
from magesim.model.consumables import Water
from magesim.model.encounter import Encounter
from magesim.model.meta import MetaConfig
from magesim.model.rotation import Rotation, RotationFunction, SpellChoice
from magesim.spells.definitions import DotData, SpellId, SpellRank

__all__ = [
    "Character",
    "DotData",
    "Encounter",
    "EncounterType",
    "LevelDelta",
    "MetaConfig",
    "Rotation",
    "RotationFunction",
    "School",
    "SchoolValues",
    "SimState",
    "SpellBook",
    "SpellChoice",
    "SpellHandle",
    "SpellId",
    "SpellRank",
    "TargetView",
    "Water",
]
