"""Loads user configs from a configs directory."""

import importlib.util
from dataclasses import dataclass
from pathlib import Path
from types import ModuleType
from typing import Final

from magesim.model.character import Character
from magesim.model.encounter import Encounter
from magesim.model.meta import MetaConfig
from magesim.model.rotation import Rotation
from magesim.talents.build import TalentBuild

CHARACTER_FILE: Final = "character.py"
ENCOUNTERS_FILE: Final = "encounters.py"
ROTATIONS_FILE: Final = "rotations.py"
TALENTS_FILE: Final = "talents.py"
META_FILE: Final = "meta.py"


@dataclass(frozen=True, slots=True, kw_only=True)
class Configs:
    """All user configuration."""

    characters: list[Character]
    encounters: list[Encounter]
    rotations: list[Rotation]
    talents: list[TalentBuild]
    meta: MetaConfig


def _load_module(path: Path) -> ModuleType:
    if not path.is_file():
        raise FileNotFoundError(f"missing config file: {path}")
    spec = importlib.util.spec_from_file_location(f"magesim_configs.{path.stem}", path)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _list_of[T](module: ModuleType, name: str, kind: type[T]) -> list[T]:
    value = getattr(module, name, None)
    if not isinstance(value, list) or not all(isinstance(v, kind) for v in value):
        raise TypeError(f"{module.__name__}.{name} must be a list[{kind.__name__}]")
    return value


def load_configs(directory: Path) -> Configs:
    """Import every config file in `directory`."""
    meta = getattr(_load_module(directory / META_FILE), "META", None)
    if not isinstance(meta, MetaConfig):
        raise TypeError("meta.META must be a MetaConfig")
    urls = _list_of(_load_module(directory / TALENTS_FILE), "TALENT_URLS", str)
    return Configs(
        characters=_list_of(_load_module(directory / CHARACTER_FILE), "CHARACTERS", Character),
        encounters=_list_of(_load_module(directory / ENCOUNTERS_FILE), "ENCOUNTERS", Encounter),
        rotations=_list_of(_load_module(directory / ROTATIONS_FILE), "ROTATIONS", Rotation),
        talents=[TalentBuild.from_url(url) for url in urls],
        meta=meta,
    )
