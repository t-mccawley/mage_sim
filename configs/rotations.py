"""Rotations: priority functions called whenever the character can act.

Return a spell (e.g. `s.spells.fireball`) to cast it, or None to wait a tick.
Picks that are unknown, on cooldown, or unaffordable wait a tick; the time
lost is reported as "blocked" in the results.
"""

from magesim import EncounterType, Rotation, RotationFunction, SimState, SpellChoice

# LEVEL 20

# def fire(s: SimState) -> SpellChoice:
#     """Pyroblast opener, Fire Blast on cooldown, Fireball filler."""
#     sb = s.spells
#     target = s.target
#     if target is not None and target.health_pct == 100 and sb.pyroblast.ready:
#         return sb.pyroblast
#     if sb.fire_blast.ready:
#         return sb.fire_blast
#     return sb.fireball


# def frost(s: SimState) -> SpellChoice:
#     """Ice Lance on frozen targets, Frostbolt filler."""
#     sb = s.spells
#     target = s.target
#     if target is not None and target.frozen and sb.ice_lance.ready:
#         return sb.ice_lance
#     return sb.frostbolt

# def arcane_missile_only(s: SimState) -> SpellChoice:
#     """Spam Arcane Missiles."""
#     sb = s.spells
#     return sb.arcane_missiles

# def arcane_1stack(s: SimState) -> SpellChoice:
#     """Build Arcane Blast stacks, spend them on Arcane Missiles."""
#     sb = s.spells
#     if s.arcane_blast_stacks < 1 and sb.arcane_blast.ready:
#         return sb.arcane_blast
#     if sb.arcane_missiles.ready:
#         return sb.arcane_missiles
#     return sb.fireball

# def arcane_2stack(s: SimState) -> SpellChoice:
#     """Build Arcane Blast stacks, spend them on Arcane Missiles."""
#     sb = s.spells
#     if s.arcane_blast_stacks < 2 and sb.arcane_blast.ready:
#         return sb.arcane_blast
#     if sb.arcane_missiles.ready:
#         return sb.arcane_missiles
#     return sb.fireball

# def arcane_3stack(s: SimState) -> SpellChoice:
#     """Build Arcane Blast stacks, spend them on Arcane Missiles."""
#     sb = s.spells
#     if s.arcane_blast_stacks < 3 and sb.arcane_blast.ready:
#         return sb.arcane_blast
#     if sb.arcane_missiles.ready:
#         return sb.arcane_missiles
#     return sb.fireball

# def arcane_4stack(s: SimState) -> SpellChoice:
#     """Build Arcane Blast stacks, spend them on Arcane Missiles."""
#     sb = s.spells
#     if s.arcane_blast_stacks < 4 and sb.arcane_blast.ready:
#         return sb.arcane_blast
#     if sb.arcane_missiles.ready:
#         return sb.arcane_missiles
#     return sb.fireball


# def _for_encounters(name: str, description: str, function: RotationFunction) -> list[Rotation]:
#     """Register one rotation function for single target and leveling."""
#     return [
#         Rotation(
#             display_name=name,
#             description=description,
#             encounter_type=kind,
#             rotation_function=function,
#         )
#         for kind in (EncounterType.SINGLE_TARGET, EncounterType.MULTI_TARGET_LEVELING)
#     ]


# ROTATIONS: list[Rotation] = [
#     *_for_encounters("Fire", "Pyroblast opener, Fire Blast, Fireball.", fire),
#     *_for_encounters("Frost", "Ice Lance when frozen, Frostbolt.", frost),
#     *_for_encounters("Arcane Spam", "spam Arcane Missiles.", arcane_missile_only),
#     *_for_encounters("Arcane 1 Stack", "Arcane Blast x1, Arcane Missiles.", arcane_1stack),
#     *_for_encounters("Arcane 2 Stack", "Arcane Blast x2, Arcane Missiles.", arcane_2stack),
#     *_for_encounters("Arcane 3 Stack", "Arcane Blast x3, Arcane Missiles.", arcane_3stack),
#     *_for_encounters("Arcane 4 Stack", "Arcane Blast x4, Arcane Missiles.", arcane_4stack),
# ]

# LEVEL 60

def frost_fire_single_target(s: SimState) -> SpellChoice:
    """Pyroblast opener, Fire Blast on cooldown, Fireball filler."""
    sb = s.spells
    target = s.target
    if target is not None and target.health_pct == 100 and sb.pyroblast.ready:
        return sb.pyroblast
    if sb.fire_blast.ready:
        return sb.fire_blast
    return sb.frostfire_bolt

ROTATIONS: list[Rotation] = [
    Rotation(
        display_name="Frostfire",
        description="Frostfire Bolt spam.",
        encounter_type=EncounterType.SINGLE_TARGET,
        rotation_function=frost_fire_single_target,
    ),
]