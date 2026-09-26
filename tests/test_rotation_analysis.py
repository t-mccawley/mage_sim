"""Static spell-use detection in rotation functions."""

from magesim import SimState, SpellChoice, SpellId
from magesim.model.rotation_analysis import used_spells


def _guarded(s: SimState) -> SpellChoice:
    target = s.target
    if target is not None and target.frozen and s.spells.ice_lance.ready:
        return s.spells.ice_lance
    return s.spells.frostbolt


def _known_only(s: SimState) -> SpellChoice:
    if s.spells.pyroblast.known:
        return SpellId.FIREBALL
    return s.spells.scorch


def test_guarded_references_count_as_use() -> None:
    assert used_spells(_guarded) == {SpellId.ICE_LANCE, SpellId.FROSTBOLT}


def test_known_checks_do_not_count_and_spell_ids_do() -> None:
    assert used_spells(_known_only) == {SpellId.FIREBALL, SpellId.SCORCH}


def test_known_checked_spell_is_excluded_even_when_cast() -> None:
    def adaptive(s: SimState) -> SpellChoice:
        return s.spells.pyroblast if s.spells.pyroblast.known else s.spells.fireball

    assert used_spells(adaptive) == {SpellId.FIREBALL}
