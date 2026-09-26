"""Read-only views passed to rotation functions."""

from collections.abc import Mapping

from magesim.engine.state import CasterState, Enemy, SpellHandle
from magesim.spells.definitions import SpellId


class SpellBook:
    """All spells, e.g. `spells.fireball.ready`."""

    __slots__ = ("_handles",)

    def __init__(self, handles: Mapping[SpellId, SpellHandle]) -> None:
        self._handles = dict(handles)

    def __getitem__(self, spell_id: SpellId) -> SpellHandle:
        return self._handles[spell_id]

    def all(self) -> tuple[SpellHandle, ...]:
        """Every spell handle."""
        return tuple(self._handles.values())

    @property
    def fireball(self) -> SpellHandle:
        """Fireball."""
        return self._handles[SpellId.FIREBALL]

    @property
    def frostbolt(self) -> SpellHandle:
        """Frostbolt."""
        return self._handles[SpellId.FROSTBOLT]

    @property
    def fire_blast(self) -> SpellHandle:
        """Fire Blast."""
        return self._handles[SpellId.FIRE_BLAST]

    @property
    def arcane_missiles(self) -> SpellHandle:
        """Arcane Missiles."""
        return self._handles[SpellId.ARCANE_MISSILES]

    @property
    def arcane_explosion(self) -> SpellHandle:
        """Arcane Explosion."""
        return self._handles[SpellId.ARCANE_EXPLOSION]

    @property
    def frost_nova(self) -> SpellHandle:
        """Frost Nova."""
        return self._handles[SpellId.FROST_NOVA]

    @property
    def flamestrike(self) -> SpellHandle:
        """Flamestrike."""
        return self._handles[SpellId.FLAMESTRIKE]

    @property
    def blizzard(self) -> SpellHandle:
        """Blizzard."""
        return self._handles[SpellId.BLIZZARD]

    @property
    def scorch(self) -> SpellHandle:
        """Scorch."""
        return self._handles[SpellId.SCORCH]

    @property
    def pyroblast(self) -> SpellHandle:
        """Pyroblast (talent)."""
        return self._handles[SpellId.PYROBLAST]

    @property
    def ice_lance(self) -> SpellHandle:
        """Ice Lance (talent)."""
        return self._handles[SpellId.ICE_LANCE]

    @property
    def arcane_blast(self) -> SpellHandle:
        """Arcane Blast (talent)."""
        return self._handles[SpellId.ARCANE_BLAST]

    @property
    def frostfire_bolt(self) -> SpellHandle:
        """Frostfire Bolt (counts as Fire and Frost)."""
        return self._handles[SpellId.FROSTFIRE_BOLT]

    @property
    def blast_wave(self) -> SpellHandle:
        """Blast Wave (talent)."""
        return self._handles[SpellId.BLAST_WAVE]

    @property
    def cone_of_cold(self) -> SpellHandle:
        """Cone of Cold."""
        return self._handles[SpellId.CONE_OF_COLD]


class TargetView:
    """Read-only view of an enemy."""

    __slots__ = ("_caster", "_enemy")

    def __init__(self, enemy: Enemy, caster: CasterState) -> None:
        self._enemy = enemy
        self._caster = caster

    @property
    def health(self) -> float:
        """Current health."""
        return self._enemy.health

    @property
    def max_health(self) -> float:
        """Maximum health."""
        return self._enemy.max_health

    @property
    def health_pct(self) -> float:
        """Health in percent (0-100)."""
        return 100.0 * self._enemy.health / self._enemy.max_health

    @property
    def level(self) -> int:
        """Absolute level."""
        return self._enemy.level

    @property
    def frozen(self) -> bool:
        """True while frozen (Frost Nova, Frostbite)."""
        return self._caster.time < self._enemy.frozen_until

    def has_dot(self, source: str) -> bool:
        """True if a DoT from `source` (e.g. 'Fireball', 'Ignite') is ticking."""
        return source in self._enemy.dots


class SimState:
    """Everything a rotation may inspect at the current tick."""

    __slots__ = ("_caster", "_enemies", "spells")

    def __init__(self, caster: CasterState, spells: SpellBook, enemies: list[Enemy]) -> None:
        self._caster = caster
        self._enemies = enemies
        self.spells = spells

    @property
    def time(self) -> float:
        """Seconds since the encounter started."""
        return self._caster.time

    @property
    def mana(self) -> float:
        """Current mana."""
        return self._caster.mana

    @property
    def max_mana(self) -> float:
        """Maximum mana."""
        return self._caster.max_mana

    @property
    def mana_pct(self) -> float:
        """Mana in percent (0-100)."""
        return 100.0 * self._caster.mana / self._caster.max_mana

    @property
    def clearcasting(self) -> bool:
        """True if the next damage spell is free."""
        return self._caster.clearcasting

    @property
    def arcane_blast_stacks(self) -> int:
        """Active Arcane Blast stacks."""
        return self._caster.active_arcane_blast_stacks

    @property
    def enemies(self) -> tuple[TargetView, ...]:
        """Living enemies."""
        return tuple(TargetView(e, self._caster) for e in self._enemies if e.alive)

    @property
    def enemy_count(self) -> int:
        """Number of living enemies."""
        return sum(1 for e in self._enemies if e.alive)

    @property
    def target(self) -> TargetView | None:
        """Current target (first living enemy)."""
        alive = next((e for e in self._enemies if e.alive), None)
        return TargetView(alive, self._caster) if alive else None
