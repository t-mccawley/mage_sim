"""Wowhead Forever talent data and calculator URL decoding.

URL format (from Wowhead's TalentCalcClassic.js):
    .../talent-calc/mage/<version><tree0>-<tree1>-<tree2>[_<suffix>...][/<pick order>]
Each tree string holds one rank digit per talent, ordered by (row, col); trailing
zeros and empty trailing trees may be omitted. Suffix `t<n>` is the Talented perk
rank, which lowers the first talent level by n.
"""

import json
import re
import urllib.request
from dataclasses import dataclass
from functools import cache
from importlib import resources
from pathlib import Path
from typing import Final

from magesim.core.enums import TalentTree

DATA_URL: Final = "https://nether.wowhead.com/forever/data/talents-classic"
SNAPSHOT_FILE: Final = "forever_mage_talents.json"
HASH_VERSION: Final = "v1"
TALENTED_SUFFIX: Final = "t"
FIRST_TALENT_LEVEL: Final = 10

# Wowhead tree ids for the mage, in calculator order.
TREE_IDS: Final[dict[TalentTree, str]] = {
    TalentTree.ARCANE: "81",
    TalentTree.FIRE: "41",
    TalentTree.FROST: "61",
}

_URL_PATTERN: Final = re.compile(r"talent-calc/mage/([^/?#]+)")


@dataclass(frozen=True, slots=True)
class TalentInfo:
    """One talent in a tree."""

    tree: TalentTree
    name: str
    row: int
    col: int
    max_rank: int
    description: str


@dataclass(frozen=True, slots=True)
class DecodedBuild:
    """Ranks parsed from a calculator URL."""

    ranks: dict[str, int]
    points: dict[TalentTree, int]
    talented_rank: int


def refresh_snapshot(target: Path | None = None) -> Path:
    """Download current talent data and write the mage snapshot."""
    request = urllib.request.Request(DATA_URL, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(request, timeout=30) as response:
        text = response.read().decode("utf-8")
    payload = json.JSONDecoder().raw_decode(text[text.index(",") + 1 :])[0]
    snapshot = {
        tree.value: [
            {
                "name": t["name"],
                "row": t["row"],
                "col": t["col"],
                "max_rank": len(t["ranks"]),
                "description": t["descriptions"][str(len(t["ranks"]))],
            }
            for t in payload["talents"][tree_id].values()
        ]
        for tree, tree_id in TREE_IDS.items()
    }
    path = target or Path(str(resources.files("magesim.data").joinpath(SNAPSHOT_FILE)))
    path.write_text(json.dumps(snapshot, indent=1), encoding="utf-8")
    load_talent_trees.cache_clear()
    return path


@cache
def load_talent_trees() -> dict[TalentTree, tuple[TalentInfo, ...]]:
    """Talents per tree, ordered by (row, col)."""
    raw = json.loads(
        resources.files("magesim.data").joinpath(SNAPSHOT_FILE).read_text(encoding="utf-8")
    )
    trees: dict[TalentTree, tuple[TalentInfo, ...]] = {}
    for tree in TalentTree:
        infos = [
            TalentInfo(tree, t["name"], t["row"], t["col"], t["max_rank"], t["description"])
            for t in raw[tree.value]
        ]
        trees[tree] = tuple(sorted(infos, key=lambda t: (t.row, t.col)))
    return trees


def decode_url(url: str) -> DecodedBuild:
    """Parse a Wowhead Forever mage talent calculator URL."""
    match = _URL_PATTERN.search(url)
    if match is None:
        raise ValueError(f"not a Wowhead mage talent calculator URL: {url}")
    code = match.group(1)
    if not code.startswith(HASH_VERSION):
        raise ValueError(f"unsupported talent hash version in {url}")
    points_code, *suffixes = code[len(HASH_VERSION) :].split("_")
    talented_rank = 0
    for suffix in suffixes:
        if suffix.startswith(TALENTED_SUFFIX) and suffix[1:].isdigit():
            talented_rank = int(suffix[1:])

    trees = load_talent_trees()
    tree_codes = points_code.split("-")
    ranks: dict[str, int] = {}
    points: dict[TalentTree, int] = {}
    for index, tree in enumerate(TalentTree):
        digits = tree_codes[index] if index < len(tree_codes) else ""
        talents = trees[tree]
        if len(digits) > len(talents):
            raise ValueError(f"{tree} has {len(talents)} talents, URL gives {len(digits)}")
        spent = 0
        for talent, digit in zip(talents, digits, strict=False):
            rank = int(digit)
            if rank > talent.max_rank:
                raise ValueError(f"{talent.name} rank {rank} exceeds max {talent.max_rank}")
            if rank:
                ranks[talent.name] = rank
                spent += rank
        points[tree] = spent
    return DecodedBuild(ranks=ranks, points=points, talented_rank=talented_rank)
