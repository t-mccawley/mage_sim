"""Encounters to simulate."""

from magesim import Encounter, EncounterType, LevelDelta

ENCOUNTERS: list[Encounter] = [
    Encounter(
        display_name="Raid Boss",
        description="Single target raid boss (+3 levels) that never dies, 1 minute.",
        encounter_type=EncounterType.SINGLE_TARGET,
        duration=60,
        enemy_count=1,
        enemy_health=1_000_000_000_000,
        enemy_level_delta=LevelDelta.PLUS_3,
    ),
    # Encounter(
    #     display_name="Dummy",
    #     description="Single same-level target that never dies, 3 minutes.",
    #     encounter_type=EncounterType.SINGLE_TARGET,
    #     duration=180,
    #     enemy_count=1,
    #     enemy_health=1_000_000,
    #     enemy_level_delta=LevelDelta.SAME,
    # ),
    # Encounter(
    #     display_name="Leveling pulls",
    #     description="One same-level mob per pull for 10 minutes; drink below 40% mana.",
    #     encounter_type=EncounterType.MULTI_TARGET_LEVELING,
    #     duration=600,
    #     enemy_count=1,
    #     enemy_health=450,
    #     enemy_level_delta=LevelDelta.SAME,
    #     drink_below_mana_pct=40,
    # ),
]
