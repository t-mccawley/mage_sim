"""Runtime state and the read-only views given to rotation functions."""

from dataclasses import dataclass, field

from magesim.core.enums import CastKind, School
from magesim.spells.definitions import SpellDefinition, SpellId, SpellRank
from magesim.spells.spellbook import ARCANE_BLAST_COST_PER_STACK


@dataclass(slots=True, kw_only=True)
class CasterState:
    """Mutable caster state."""

    time: float = 0.0
    mana: float
    max_mana: float
    base_mana: float
    busy_until: float = 0.0
    gcd_until: float = 0.0
    five_second_rule_until: float = 0.0
    drinking_until: float = 0.0
    clearcasting: bool = False
    arcane_blast_stacks: int = 0
    arcane_blast_until: float = 0.0
    wake_of_fire_until: float = 0.0

    @property
    def idle(self) -> bool:
        """True when a new action can start."""
        return self.time >= max(self.busy_until, self.gcd_until, self.drinking_until)

    @property
    def active_arcane_blast_stacks(self) -> int:
        """Arcane Blast stacks that have not expired."""
        return self.arcane_blast_stacks if self.time < self.arcane_blast_until else 0


@dataclass(slots=True, kw_only=True)
class DotState:
    """A periodic effect ticking on an enemy."""

    source: str
    school: School
    tick_damage: float
    ticks_left: int
    tick_interval: float


@dataclass(slots=True, kw_only=True)
class Enemy:
    """Mutable enemy state."""

    index: int
    level: int
    max_health: float
    health: float
    frozen_until: float = 0.0
    dots: dict[str, DotState] = field(default_factory=dict)

    @property
    def alive(self) -> bool:
        """True while health remains."""
        return self.health > 0.0


class SpellHandle:
    """A spell as seen by a rotation: static data plus live cooldown and cost."""

    __slots__ = ("_caster", "base_cost", "cast_time", "cooldown", "definition", "rank", "ready_at")

    def __init__(
        self,
        definition: SpellDefinition,
        rank: SpellRank | None,
        caster: CasterState,
        *,
        cast_time: float,
        cooldown: float,
        base_cost: float,
    ) -> None:
        self.definition = definition
        self.rank = rank
        self.cast_time = cast_time
        self.cooldown = cooldown
        self.base_cost = base_cost
        self.ready_at = 0.0
        self._caster = caster

    def __repr__(self) -> str:
        return f"SpellHandle({self.name}, rank={self.rank.rank if self.rank else None})"

    @property
    def spell_id(self) -> SpellId:
        """Spell identifier."""
        return self.definition.spell_id

    @property
    def name(self) -> str:
        """Display name."""
        return self.definition.name

    @property
    def school(self) -> School:
        """Magic school."""
        return self.definition.school

    @property
    def known(self) -> bool:
        """True if learned (level and talents allow it)."""
        return self.rank is not None

    @property
    def cooldown_remaining(self) -> float:
        """Seconds until off cooldown."""
        return max(self.ready_at - self._caster.time, 0.0)

    @property
    def on_cooldown(self) -> bool:
        """True while on cooldown."""
        return self.cooldown_remaining > 0.0

    @property
    def is_channel(self) -> bool:
        """True for channeled spells."""
        return self.definition.cast_kind is CastKind.CHANNEL

    @property
    def mana_cost(self) -> float:
        """Current cost including clearcasting and Arcane Blast stacks."""
        if self.rank is None:
            return 0.0
        if self._caster.clearcasting:
            return 0.0
        cost = self.base_cost
        if self.spell_id is SpellId.ARCANE_BLAST:
            cost *= 1.0 + ARCANE_BLAST_COST_PER_STACK * self._caster.active_arcane_blast_stacks
        return cost

    @property
    def affordable(self) -> bool:
        """True if current mana covers the cost."""
        return self._caster.mana >= self.mana_cost

    @property
    def ready(self) -> bool:
        """True if known, off cooldown, and affordable."""
        return self.known and not self.on_cooldown and self.affordable
