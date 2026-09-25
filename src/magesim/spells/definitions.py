"""Static spell data types."""

from dataclasses import dataclass
from enum import StrEnum

from magesim.core.enums import CastKind, School, Targeting


class SpellId(StrEnum):
    """Every simulated spell."""

    FIREBALL = "Fireball"
    FROSTBOLT = "Frostbolt"
    FIRE_BLAST = "Fire Blast"
    ARCANE_MISSILES = "Arcane Missiles"
    ARCANE_EXPLOSION = "Arcane Explosion"
    FROST_NOVA = "Frost Nova"
    FLAMESTRIKE = "Flamestrike"
    BLIZZARD = "Blizzard"
    SCORCH = "Scorch"
    PYROBLAST = "Pyroblast"
    ICE_LANCE = "Ice Lance"
    ARCANE_BLAST = "Arcane Blast"


@dataclass(frozen=True, slots=True, kw_only=True)
class DotData:
    """Periodic damage applied on hit."""

    damage: float
    ticks: int
    tick_interval: float
    coefficient_per_tick: float = 0.0

    @property
    def damage_per_tick(self) -> float:
        """Base damage of one tick."""
        return self.damage / self.ticks


@dataclass(frozen=True, slots=True, kw_only=True)
class SpellRank:
    """One learnable rank.

    For channels, min/max damage and coefficient are per channel tick.
    """

    rank: int
    level: int
    wowhead_id: int
    min_damage: float
    max_damage: float
    coefficient: float
    mana_cost: float = 0.0
    base_mana_pct: float = 0.0
    cast_time: float = 0.0
    dot: DotData | None = None
    channel_ticks: int = 0


@dataclass(frozen=True, slots=True, kw_only=True)
class SpellDefinition:
    """A spell and all its ranks."""

    spell_id: SpellId
    school: School
    cast_kind: CastKind
    targeting: Targeting
    ranks: tuple[SpellRank, ...]
    cooldown: float = 0.0
    granted_by_talent: str | None = None
    chills: bool = False
    freeze_duration: float = 0.0

    def __post_init__(self) -> None:
        if not self.ranks:
            raise ValueError(f"{self.spell_id} has no ranks")
        if self.cast_kind is CastKind.CHANNEL and any(r.channel_ticks < 1 for r in self.ranks):
            raise ValueError(f"{self.spell_id} channel ranks need channel_ticks")

    @property
    def name(self) -> str:
        """Display name."""
        return self.spell_id.value

    def rank_for_level(self, level: int) -> SpellRank | None:
        """Highest rank learnable at `level`, if any."""
        known = [r for r in self.ranks if r.level <= level]
        return max(known, key=lambda r: r.rank) if known else None
