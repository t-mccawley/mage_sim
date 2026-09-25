"""Simulation settings."""

from pathlib import Path

from magesim import MetaConfig

META = MetaConfig(
    seed=42,
    iterations=300,
    tick_seconds=0.1,
    peak_warmup_seconds=5.0,
    output_dir=Path("results"),
    open_report=True,
)
