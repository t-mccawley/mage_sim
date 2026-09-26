"""Candidate matching."""

from magesim import Character, Encounter, EncounterType, Rotation, SimState, SpellChoice
from magesim.experiment.candidates import build_candidates
from magesim.talents.build import TalentBuild


def _noop(s: SimState) -> SpellChoice:
    return None


def test_only_compatible_combinations(rich_mage: Character, dummy: Encounter) -> None:
    rotations = [
        Rotation(display_name=k.value, description="", encounter_type=k, rotation_function=_noop)
        for k in EncounterType
    ]
    talents = [
        TalentBuild.from_url("https://www.wowhead.com/forever/talent-calc/mage/v2-005500001"),
        TalentBuild.from_url("https://www.wowhead.com/forever/talent-calc/mage/v2-22-02"),
    ]
    candidates = build_candidates([rich_mage], [dummy], rotations, talents)
    assert [(c.rotation.encounter_type, c.talents.required_level) for c in candidates] == [
        (EncounterType.SINGLE_TARGET, 20)
    ]
    assert candidates[0].number == 1
