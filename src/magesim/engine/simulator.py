"""Discrete-tick encounter simulator."""

import heapq
import itertools
import math
import random
from collections import Counter, defaultdict
from collections.abc import Callable
from dataclasses import dataclass

import numpy as np

from magesim.core.constants import (
    FIVE_SECOND_RULE_SECONDS,
    GCD_SECONDS,
    ICE_LANCE_FROZEN_MULTIPLIER,
    MP5_INTERVAL_SECONDS,
    SPIRIT_REGEN_BASE_PER_SECOND,
    SPIRIT_REGEN_PER_SPIRIT_PER_SECOND,
)
from magesim.core.enums import CastKind, EncounterType, HitOutcome, LevelDelta, School, Targeting
from magesim.engine.combat import ResistTable, SpellProfile, level_delta
from magesim.engine.results import IterationResult, dps_series, peak_dps
from magesim.engine.state import CasterState, DotState, Enemy, SpellHandle
from magesim.engine.views import SimState, SpellBook
from magesim.model.character import Character
from magesim.model.encounter import Encounter
from magesim.model.rotation import Rotation
from magesim.spells.coefficients import RankCoefficients, calculate
from magesim.spells.definitions import SpellCatalog, SpellDefinition, SpellId, SpellRank
from magesim.spells.mechanics import (
    ARCANE_BLAST_DAMAGE_PER_STACK,
    ARCANE_BLAST_DURATION,
    ARCANE_BLAST_MAX_STACKS,
)
from magesim.talents.build import TalentBuild
from magesim.talents.effects import TalentModifiers

IGNITE: str = "Ignite"
IGNITE_TICKS: int = 2
IGNITE_TICK_INTERVAL: float = 2.0
FROSTBITE_FREEZE: float = 5.0
WAKE_OF_FIRE_DURATION: float = 30.0


class RejectReason:
    """Why a rotation's pick could not be cast."""

    UNKNOWN = "not known"
    COOLDOWN = "on cooldown"
    MANA = "not enough mana"
    NO_TARGET = "no target"


@dataclass(frozen=True, slots=True)
class _SpellSetup:
    """Per-candidate static data for one spell."""

    definition: SpellDefinition
    rank: SpellRank | None
    coefficients: RankCoefficients | None
    profile: SpellProfile
    cast_time: float
    cooldown: float
    base_cost: float


class Simulation:
    """A candidate (character + encounter + talents + rotation) ready to run."""

    def __init__(
        self,
        character: Character,
        encounter: Encounter,
        talents: TalentBuild,
        rotation: Rotation,
        catalog: SpellCatalog,
        *,
        tick_seconds: float,
        peak_warmup_seconds: float,
    ) -> None:
        self.character = character
        self.encounter = encounter
        self.rotation = rotation
        self.tick_seconds = tick_seconds
        self.peak_warmup_seconds = peak_warmup_seconds
        self.modifiers = TalentModifiers.from_build(talents)
        self.enemy_level = encounter.enemy_level(character.level)
        delta = level_delta(character.level, self.enemy_level)
        self.resist_table = ResistTable.for_level_gap(self.enemy_level - character.level)
        self.spells = {
            spell_id: self._setup(definition, delta) for spell_id, definition in catalog.items()
        }

    def _setup(self, definition: SpellDefinition, delta: LevelDelta) -> _SpellSetup:
        mods = self.modifiers
        spell_id = definition.spell_id
        rank = definition.rank_for_level(self.character.level)
        if definition.mechanics.granted_by_talent and spell_id not in mods.granted_spells:
            rank = None
        profile = SpellProfile.build(self.character, mods, definition, delta)
        if rank is None:
            return _SpellSetup(definition, None, None, profile, 0.0, 0.0, 0.0)
        cost = rank.mana_cost + rank.base_mana_pct / 100.0 * self.character.base_mana
        cost *= mods.cost_multiplier.get(definition.school, 1.0)
        cast_time = max(rank.cast_time - mods.cast_time_reduction.get(spell_id, 0.0), 0.0)
        cooldown = max(rank.cooldown - mods.cooldown_reduction.get(spell_id, 0.0), 0.0)
        coefficients = calculate(definition.mechanics, rank)
        return _SpellSetup(definition, rank, coefficients, profile, cast_time, cooldown, cost)

    def run(self, rng: random.Random) -> IterationResult:
        """Simulate one iteration."""
        return _Iteration(self, rng).run()


class _Iteration:
    """Mutable state for one run of a Simulation."""

    def __init__(self, sim: Simulation, rng: random.Random) -> None:
        self.sim = sim
        self.rng = rng
        self.dt = sim.tick_seconds
        self.end_tick = self._ticks(sim.encounter.duration)
        self.tick = 0
        char = sim.character
        self.caster = CasterState(mana=char.mana, max_mana=char.mana, base_mana=char.base_mana)
        self.handles = {
            spell_id: SpellHandle(
                s.definition,
                s.rank,
                self.caster,
                cast_time=s.cast_time,
                cooldown=s.cooldown,
                base_cost=s.base_cost,
            )
            for spell_id, s in sim.spells.items()
        }
        self.enemies: list[Enemy] = []
        self.state = SimState(self.caster, SpellBook(self.handles), self.enemies)
        self.events: list[tuple[int, int, Callable[[], None]]] = []
        self.sequence = itertools.count()
        self.action_id = 0
        self.pull_active = False
        self.fight_over = False
        self.finished_tick = self.end_tick
        self.mana_synced_at = 0.0
        self.drink_started = 0.0
        self.damage = np.zeros(self.end_tick + 1, dtype=np.float64)
        self.damage_by_source: defaultdict[str, float] = defaultdict(float)
        self.casts: Counter[str] = Counter()
        self.blocked: defaultdict[str, float] = defaultdict(float)
        self.kills = 0
        self.drinking_time = 0.0
        self.mp5_rate = char.mp5 / MP5_INTERVAL_SECONDS
        self.spirit_rate = (
            SPIRIT_REGEN_BASE_PER_SECOND + char.spirit * SPIRIT_REGEN_PER_SPIRIT_PER_SECOND
        )

    # --- time ---------------------------------------------------------------

    def _ticks(self, seconds: float) -> int:
        return max(round(seconds / self.dt), 0)

    def _at(self, tick: int) -> float:
        return tick * self.dt

    def _schedule(self, delay: float, action: Callable[[], None]) -> None:
        heapq.heappush(self.events, (self.tick + self._ticks(delay), next(self.sequence), action))

    # --- main loop ----------------------------------------------------------

    def run(self) -> IterationResult:
        self._spawn_pull()
        while self.tick <= self.end_tick and not self.fight_over:
            self.caster.time = self._at(self.tick)
            self._sync_mana()
            while self.events and self.events[0][0] <= self.tick:
                heapq.heappop(self.events)[2]()
                self._check_pull_cleared()
                if self.fight_over:
                    break
            if self.fight_over:
                break
            waiting = self.pull_active and self.caster.idle
            if waiting:
                self._act()
                self._check_pull_cleared()
            next_tick = self.events[0][0] if self.events else self.end_tick + 1
            if self.pull_active:
                next_tick = min(next_tick, self._next_free_tick())
            self.tick = next_tick
        return self._result()

    def _next_free_tick(self) -> int:
        """Next tick the caster can act (polls every tick while idle)."""
        c = self.caster
        free = self._ticks(max(c.busy_until, c.gcd_until, c.drinking_until))
        return max(free, self.tick + 1)

    def _result(self) -> IterationResult:
        end = min(self.finished_tick, self.end_tick)
        series = dps_series(self.damage, self.dt, end)
        elapsed = max(end, 1) * self.dt
        total = float(self.damage[: end + 1].sum())
        return IterationResult(
            total_dps=total / elapsed,
            peak_dps=peak_dps(series, self._ticks(self.sim.peak_warmup_seconds)),
            dps_series=series,
            elapsed=elapsed,
            damage_by_source=dict(self.damage_by_source),
            casts=dict(self.casts),
            blocked_seconds=dict(self.blocked),
            enemies_killed=self.kills,
            drinking_time=self.drinking_time,
        )

    # --- encounter flow -----------------------------------------------------

    def _spawn_pull(self) -> None:
        enc = self.sim.encounter
        self.enemies[:] = [
            Enemy(
                index=i,
                level=self.sim.enemy_level,
                max_health=enc.enemy_health,
                health=enc.enemy_health,
            )
            for i in range(enc.enemy_count)
        ]
        self.pull_active = True

    def _check_pull_cleared(self) -> None:
        if not self.pull_active or any(e.alive for e in self.enemies):
            return
        self.pull_active = False
        self.action_id += 1
        self.caster.busy_until = self.caster.time
        if self.sim.encounter.encounter_type is not EncounterType.MULTI_TARGET_LEVELING:
            self.fight_over = True
            self.finished_tick = self.tick
            return
        if self.state.mana_pct < self.sim.encounter.drink_below_mana_pct:
            self._start_drinking()
        else:
            self._spawn_pull()

    def _start_drinking(self) -> None:
        caster = self.caster
        drink_rate = self.sim.character.water.drink.mana_per_second
        deficit = caster.max_mana - caster.mana
        base_rate = drink_rate + self.mp5_rate
        pre_spirit = max(caster.five_second_rule_until - caster.time, 0.0)
        if base_rate * pre_spirit >= deficit:
            duration = deficit / base_rate
        else:
            duration = pre_spirit + (deficit - base_rate * pre_spirit) / (
                base_rate + self.spirit_rate
            )
        ticks = max(math.ceil(duration / self.dt - 1e-9), 1)
        self.drink_started = caster.time
        caster.drinking_until = self._at(self.tick + ticks)
        self.drinking_time += ticks * self.dt
        heapq.heappush(self.events, (self.tick + ticks, next(self.sequence), self._spawn_pull))

    # --- mana ---------------------------------------------------------------

    def _sync_mana(self) -> None:
        caster = self.caster
        start, now = self.mana_synced_at, caster.time
        if now <= start:
            return
        gain = self.mp5_rate * (now - start)
        gain += self.spirit_rate * max(now - max(start, caster.five_second_rule_until), 0.0)
        drink_end = min(now, caster.drinking_until)
        drink_start = max(start, self.drink_started)
        if drink_end > drink_start:
            gain += self.sim.character.water.drink.mana_per_second * (drink_end - drink_start)
        caster.mana = min(caster.mana + gain, caster.max_mana)
        self.mana_synced_at = now

    def _spend(self, handle: SpellHandle) -> bool:
        """Pay for a cast; False if mana is short."""
        cost = handle.mana_cost
        if self.caster.mana < cost:
            return False
        self.caster.clearcasting = False
        if cost > 0:
            self.caster.mana -= cost
            self.caster.five_second_rule_until = self.caster.time + FIVE_SECOND_RULE_SECONDS
        return True

    # --- actions ------------------------------------------------------------

    def _act(self) -> None:
        choice = self.sim.rotation.rotation_function(self.state)
        if choice is None:
            return
        handle = self.handles[choice] if isinstance(choice, SpellId) else choice
        reason = self._reject_reason(handle)
        if reason is not None:
            self.blocked[f"{handle.name}: {reason}"] += self.dt
            return
        caster = self.caster
        caster.gcd_until = self._at(self.tick + self._ticks(GCD_SECONDS))
        if handle.cooldown > 0:
            handle.ready_at = self._at(self.tick + self._ticks(handle.cooldown))
        self.action_id += 1
        action = self.action_id
        kind = handle.definition.cast_kind
        if kind is CastKind.INSTANT:
            self._spend(handle)
            self._resolve(handle, self._consume_buffs(handle))
        elif kind is CastKind.CAST:
            caster.busy_until = self._at(self.tick + self._ticks(handle.cast_time))
            self._schedule(handle.cast_time, lambda: self._complete_cast(handle, action))
        else:
            self._start_channel(handle, action)

    def _reject_reason(self, handle: SpellHandle) -> str | None:
        if not handle.known:
            return RejectReason.UNKNOWN
        if handle.on_cooldown:
            return RejectReason.COOLDOWN
        if not handle.affordable:
            return RejectReason.MANA
        if self.state.target is None:
            return RejectReason.NO_TARGET
        return None

    def _complete_cast(self, handle: SpellHandle, action: int) -> None:
        if action != self.action_id or not self.pull_active:
            return
        if not self._spend(handle):
            self.blocked[f"{handle.name}: {RejectReason.MANA}"] += handle.cast_time
            return
        self._resolve(handle, self._consume_buffs(handle))

    def _start_channel(self, handle: SpellHandle, action: int) -> None:
        rank = handle.rank
        assert rank is not None
        self._spend(handle)
        multiplier = self._consume_buffs(handle)
        self.casts[handle.name] += 1
        self.caster.busy_until = self._at(self.tick + self._ticks(handle.cast_time))
        interval = handle.cast_time / rank.channel_ticks
        for i in range(1, rank.channel_ticks + 1):
            self._schedule(interval * i, lambda: self._channel_tick(handle, action, multiplier))

    def _channel_tick(self, handle: SpellHandle, action: int, multiplier: float) -> None:
        if action != self.action_id or not self.pull_active:
            return
        self._hit_targets(handle, multiplier)

    def _consume_buffs(self, handle: SpellHandle) -> float:
        """Apply Arcane Blast stacks; return the damage multiplier for this cast."""
        caster = self.caster
        stacks = caster.active_arcane_blast_stacks
        if handle.spell_id is SpellId.ARCANE_BLAST:
            caster.arcane_blast_stacks = min(stacks + 1, ARCANE_BLAST_MAX_STACKS)
            caster.arcane_blast_until = caster.time + ARCANE_BLAST_DURATION
            return 1.0
        caster.arcane_blast_stacks = 0
        return 1.0 + ARCANE_BLAST_DAMAGE_PER_STACK * stacks

    # --- damage -------------------------------------------------------------

    def _resolve(self, handle: SpellHandle, multiplier: float) -> None:
        self.casts[handle.name] += 1
        self._hit_targets(handle, multiplier)

    def _hit_targets(self, handle: SpellHandle, multiplier: float) -> None:
        definition = handle.definition
        if definition.targeting is Targeting.AOE:
            targets = [e for e in self.enemies if e.alive]
        else:
            first = next((e for e in self.enemies if e.alive), None)
            targets = [first] if first else []
        landed = False
        for enemy in targets:
            landed |= self._hit(handle, enemy, multiplier)
        mods = self.sim.modifiers
        if landed and mods.clearcasting_chance and self.rng.random() < mods.clearcasting_chance:
            self.caster.clearcasting = True

    def _hit(self, handle: SpellHandle, enemy: Enemy, multiplier: float) -> bool:
        """Roll and apply one spell hit on one enemy; True if it landed."""
        setup = self.sim.spells[handle.spell_id]
        rank, coefficients = setup.rank, setup.coefficients
        assert rank is not None and coefficients is not None
        profile = setup.profile
        mods = self.sim.modifiers
        caster = self.caster
        bonus_crit = 0.0
        if handle.spell_id is SpellId.FIRE_BLAST and caster.time < caster.wake_of_fire_until:
            bonus_crit = mods.wake_of_fire_crit_pct / 100.0
            caster.wake_of_fire_until = 0.0
        outcome = profile.roll_outcome(self.rng, bonus_crit)
        if outcome is HitOutcome.MISS:
            return False
        frozen = caster.time < enemy.frozen_until
        damage = self.rng.uniform(rank.min_damage, rank.max_damage)
        damage += profile.spell_power * coefficients.direct
        damage *= profile.damage_multiplier * multiplier
        if handle.spell_id is SpellId.ICE_LANCE and frozen:
            damage *= ICE_LANCE_FROZEN_MULTIPLIER
        damage *= self.sim.resist_table.roll_multiplier(self.rng)
        if outcome is HitOutcome.CRIT:
            damage *= profile.crit_multiplier
            if handle.school is School.FIRE and mods.ignite_fraction:
                self._apply_ignite(enemy, damage * mods.ignite_fraction)
        self._deal(enemy, damage, handle.name)
        if enemy.alive:
            self._apply_effects(handle, enemy, rank, coefficients, profile)
        return True

    def _apply_effects(
        self,
        handle: SpellHandle,
        enemy: Enemy,
        rank: SpellRank,
        coefficients: RankCoefficients,
        profile: SpellProfile,
    ) -> None:
        mechanics = handle.definition.mechanics
        now = self.caster.time
        if mechanics.freeze_duration:
            enemy.frozen_until = max(enemy.frozen_until, now + mechanics.freeze_duration)
        mods = self.sim.modifiers
        chills = mechanics.chills or (handle.spell_id is SpellId.BLIZZARD and mods.blizzard_chills)
        if chills and mods.frostbite_chance and self.rng.random() < mods.frostbite_chance:
            enemy.frozen_until = max(enemy.frozen_until, now + FROSTBITE_FREEZE)
        if rank.dot is not None:
            tick_damage = rank.dot.damage_per_tick + profile.spell_power * coefficients.dot_per_tick
            self._start_dot(
                enemy,
                DotState(
                    source=handle.name,
                    school=handle.school,
                    tick_damage=tick_damage * profile.damage_multiplier,
                    ticks_left=rank.dot.ticks,
                    tick_interval=rank.dot.tick_interval,
                ),
            )

    def _apply_ignite(self, enemy: Enemy, amount: float) -> None:
        existing = enemy.dots.get(IGNITE)
        if existing is not None:
            amount += existing.tick_damage * existing.ticks_left
        self._start_dot(
            enemy,
            DotState(
                source=IGNITE,
                school=School.FIRE,
                tick_damage=amount / IGNITE_TICKS,
                ticks_left=IGNITE_TICKS,
                tick_interval=IGNITE_TICK_INTERVAL,
            ),
        )

    def _start_dot(self, enemy: Enemy, dot: DotState) -> None:
        enemy.dots[dot.source] = dot
        self._schedule(dot.tick_interval, lambda: self._dot_tick(enemy, dot))

    def _dot_tick(self, enemy: Enemy, dot: DotState) -> None:
        if not enemy.alive or enemy.dots.get(dot.source) is not dot:
            return
        damage = dot.tick_damage
        if dot.source != IGNITE:
            damage *= self.sim.resist_table.roll_multiplier(self.rng)
        dot.ticks_left -= 1
        self._deal(enemy, damage, dot.source)
        if dot.ticks_left > 0 and enemy.alive:
            self._schedule(dot.tick_interval, lambda: self._dot_tick(enemy, dot))
        else:
            enemy.dots.pop(dot.source, None)

    def _deal(self, enemy: Enemy, damage: float, source: str) -> None:
        dealt = min(damage, enemy.health)
        enemy.health -= dealt
        if self.tick <= self.end_tick:
            self.damage[self.tick] += dealt
        self.damage_by_source[source] += dealt
        if not enemy.alive:
            self.kills += 1
            enemy.dots.clear()
            if self.sim.modifiers.wake_of_fire_crit_pct:
                self.caster.wake_of_fire_until = self.caster.time + WAKE_OF_FIRE_DURATION
