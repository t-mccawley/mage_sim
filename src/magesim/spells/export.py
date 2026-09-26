"""Spellbook audit export."""

import csv
import dataclasses
import sys
from dataclasses import dataclass
from pathlib import Path

from magesim.spells.coefficients import calculate
from magesim.spells.definitions import SpellCatalog


@dataclass(frozen=True, slots=True)
class SpellbookRow:
    """One CSV row: configured values followed by calculated values."""

    spell: str
    rank: int
    level: int
    school: str
    cast_kind: str
    targeting: str
    min_damage: float
    max_damage: float
    average_damage: float
    mana_cost: float
    base_mana_pct: float
    cast_time: float
    cooldown: float
    channel_ticks: int
    dot_damage: float
    dot_duration: float
    dot_ticks: int
    wowhead_id: int | None
    low_level_penalty: float
    direct_base: float
    direct_scale: float
    direct_coefficient: float
    dot_base: float
    dot_scale: float
    dot_coefficient_per_tick: float
    total_coefficient: float
    scale_note: str


def spellbook_rows(catalog: SpellCatalog) -> list[SpellbookRow]:
    """Every configured rank with its calculated coefficients."""
    rows: list[SpellbookRow] = []
    for definition in catalog.values():
        m = definition.mechanics
        for rank in sorted(definition.ranks, key=lambda r: r.rank):
            c = calculate(m, rank)
            rows.append(
                SpellbookRow(
                    spell=definition.name,
                    rank=rank.rank,
                    level=rank.level,
                    school=m.school.value,
                    cast_kind=m.cast_kind.value,
                    targeting=m.targeting.value,
                    min_damage=rank.min_damage,
                    max_damage=rank.max_damage,
                    average_damage=rank.average_damage,
                    mana_cost=rank.mana_cost,
                    base_mana_pct=rank.base_mana_pct,
                    cast_time=rank.cast_time,
                    cooldown=rank.cooldown,
                    channel_ticks=rank.channel_ticks,
                    dot_damage=rank.dot.damage if rank.dot else 0.0,
                    dot_duration=rank.dot.duration if rank.dot else 0.0,
                    dot_ticks=rank.dot.ticks if rank.dot else 0,
                    wowhead_id=rank.wowhead_id,
                    low_level_penalty=round(c.low_level_penalty, 4),
                    direct_base=round(c.direct_base, 4),
                    direct_scale=round(m.direct_scale, 4),
                    direct_coefficient=round(c.direct, 4),
                    dot_base=round(c.dot_base, 4),
                    dot_scale=round(m.dot_scale, 4),
                    dot_coefficient_per_tick=round(c.dot_per_tick, 4),
                    total_coefficient=round(c.total, 4),
                    scale_note=m.scale_note,
                )
            )
    return rows


def write_spellbook_csv(catalog: SpellCatalog, path: Path | None) -> None:
    """Write the audit CSV to `path`, or stdout when None."""
    fields = [f.name for f in dataclasses.fields(SpellbookRow)]
    rows = [dataclasses.asdict(r) for r in spellbook_rows(catalog)]
    if path is None:
        writer = csv.DictWriter(sys.stdout, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
