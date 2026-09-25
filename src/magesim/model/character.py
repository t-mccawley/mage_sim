"""Character configuration."""

from dataclasses import dataclass, field

from magesim.core.constants import (
    INTELLECT_MANA_THRESHOLD,
    MANA_PER_INTELLECT,
    MAX_LEVEL,
    MIN_LEVEL,
)
from magesim.core.enums import School
from magesim.model.consumables import Water


@dataclass(frozen=True, slots=True, kw_only=True)
class SchoolValues:
    """A stat with a general value plus per-school bonuses."""

    general: float = 0.0
    fire: float = 0.0
    frost: float = 0.0
    arcane: float = 0.0

    def for_school(self, school: School) -> float:
        """Total value for a school (general + school bonus)."""
        bonus = {School.FIRE: self.fire, School.FROST: self.frost, School.ARCANE: self.arcane}
        return self.general + bonus[school]


@dataclass(frozen=True, slots=True, kw_only=True)
class Character:
    """Character stats as shown in game, after gear and buffs.

    Percent stats (crit, hit) are in percent, e.g. 5.5 for 5.5%.
    """

    display_name: str
    level: int
    intellect: float
    spirit: float
    mana: float
    mp5: float = 0.0
    spell_power: SchoolValues = field(default_factory=SchoolValues)
    spell_crit: SchoolValues = field(default_factory=SchoolValues)
    spell_hit: SchoolValues = field(default_factory=SchoolValues)
    water: Water = Water.CONJURED_WATER

    def __post_init__(self) -> None:
        if not MIN_LEVEL <= self.level <= MAX_LEVEL:
            raise ValueError(f"level must be in [{MIN_LEVEL}, {MAX_LEVEL}], got {self.level}")
        if self.mana <= 0:
            raise ValueError("mana must be positive")

    @property
    def base_mana(self) -> float:
        """Mana excluding intellect contribution."""
        from_int = min(self.intellect, INTELLECT_MANA_THRESHOLD) + MANA_PER_INTELLECT * max(
            self.intellect - INTELLECT_MANA_THRESHOLD, 0.0
        )
        return max(self.mana - from_int, 0.0)
