"""Spell data types.

`SpellRank` holds values visible in game (configured in configs/spellbook.py).
`SpellMechanics` holds fixed behaviour and coefficient scales (spells/mechanics.py).
"""

from dataclasses import dataclass
from enum import StrEnum

from magesim.core.constants import MAX_LEVEL, MIN_LEVEL
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
    FROSTFIRE_BOLT = "Frostfire Bolt"
    BLAST_WAVE = "Blast Wave"
    CONE_OF_COLD = "Cone of Cold"


@dataclass(frozen=True, slots=True, kw_only=True)
class DotData:
    """Periodic damage applied on hit, e.g. 'an additional 12 Fire damage over 8 sec'."""

    damage: float
    duration: float
    ticks: int

    def __post_init__(self) -> None:
        if self.duration <= 0 or self.ticks < 1:
            raise ValueError("dot needs a positive duration and at least one tick")

    @property
    def tick_interval(self) -> float:
        """Seconds between ticks."""
        return self.duration / self.ticks

    @property
    def damage_per_tick(self) -> float:
        """Base damage of one tick."""
        return self.damage / self.ticks


@dataclass(frozen=True, slots=True, kw_only=True)
class SpellRank:
    """One learnable rank, as shown in game.

    For channels, `cast_time` is the channel duration and min/max damage are per tick.
    """

    rank: int
    level: int
    min_damage: float
    max_damage: float
    mana_cost: float = 0.0
    base_mana_pct: float = 0.0
    cast_time: float = 0.0
    cooldown: float = 0.0
    channel_ticks: int = 0
    dot: DotData | None = None
    wowhead_id: int | None = None
    confirmed_in_game_date: str | None = None

    def __post_init__(self) -> None:
        if not MIN_LEVEL <= self.level <= MAX_LEVEL:
            raise ValueError(f"rank {self.rank}: level {self.level} out of range")
        if self.min_damage > self.max_damage:
            raise ValueError(f"rank {self.rank}: min_damage exceeds max_damage")
        if min(self.mana_cost, self.base_mana_pct, self.cast_time, self.cooldown) < 0:
            raise ValueError(f"rank {self.rank}: negative cost, cast time, or cooldown")

    @property
    def average_damage(self) -> float:
        """Mean of the damage range."""
        return (self.min_damage + self.max_damage) / 2


@dataclass(frozen=True, slots=True, kw_only=True)
class SpellMechanics:
    """Fixed spell behaviour.

    `direct_scale` and `dot_scale` multiply the formula coefficient (see coefficients.py).
    `extra_schools` lists further schools the spell counts as (Frostfire Bolt).
    """

    spell_id: SpellId
    school: School
    extra_schools: tuple[School, ...] = ()
    cast_kind: CastKind
    targeting: Targeting
    direct_scale: float = 1.0
    dot_scale: float = 1.0
    scale_note: str = ""
    granted_by_talent: str | None = None
    chills: bool = False
    freeze_duration: float = 0.0

    @property
    def schools(self) -> tuple[School, ...]:
        """Every school the spell counts as, primary first."""
        return (self.school, *self.extra_schools)


@dataclass(frozen=True, slots=True)
class SpellDefinition:
    """A spell's mechanics plus its configured ranks (may be empty)."""

    mechanics: SpellMechanics
    ranks: tuple[SpellRank, ...]

    def __post_init__(self) -> None:
        numbers = [r.rank for r in self.ranks]
        if len(numbers) != len(set(numbers)):
            raise ValueError(f"{self.name}: duplicate rank numbers")
        if self.cast_kind is CastKind.CHANNEL and any(r.channel_ticks < 1 for r in self.ranks):
            raise ValueError(f"{self.name}: channel ranks need channel_ticks")

    @property
    def spell_id(self) -> SpellId:
        """Identifier."""
        return self.mechanics.spell_id

    @property
    def name(self) -> str:
        """Display name."""
        return self.mechanics.spell_id.value

    @property
    def school(self) -> School:
        """Primary magic school."""
        return self.mechanics.school

    @property
    def schools(self) -> tuple[School, ...]:
        """Every school the spell counts as."""
        return self.mechanics.schools

    @property
    def cast_kind(self) -> CastKind:
        """Instant, cast, or channel."""
        return self.mechanics.cast_kind

    @property
    def targeting(self) -> Targeting:
        """Single target or AoE."""
        return self.mechanics.targeting

    def rank_for_level(self, level: int) -> SpellRank | None:
        """Highest rank learnable at `level`, if any."""
        known = [r for r in self.ranks if r.level <= level]
        return max(known, key=lambda r: r.rank) if known else None


type SpellCatalog = dict[SpellId, SpellDefinition]
"""Every spell with its configured ranks."""
