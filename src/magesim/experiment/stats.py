"""Aggregation of iteration results."""

import warnings
from collections import Counter
from dataclasses import dataclass
from typing import Final

import numpy as np

from magesim.engine.results import FloatArray, IterationResult
from magesim.experiment.candidates import Candidate

LOW_PERCENTILE: Final = 15.0
HIGH_PERCENTILE: Final = 85.0


@dataclass(frozen=True, slots=True)
class Percentiles:
    """Median with a 15th-85th percentile band."""

    low: float
    median: float
    high: float

    @classmethod
    def of(cls, values: FloatArray) -> "Percentiles":
        """Summarize `values`."""
        low, median, high = np.percentile(values, [LOW_PERCENTILE, 50.0, HIGH_PERCENTILE])
        return cls(float(low), float(median), float(high))


@dataclass(frozen=True, slots=True, kw_only=True)
class CandidateSummary:
    """Aggregated results for one candidate."""

    candidate: Candidate
    iterations: int
    total_dps: Percentiles
    peak_dps: Percentiles
    times: FloatArray
    median_dps_series: FloatArray
    damage_share: dict[str, float]
    casts_per_iteration: dict[str, float]
    blocked_seconds_per_iteration: dict[str, float]
    mean_kills: float
    mean_drinking_time: float
    unimplemented_talents: tuple[str, ...]


def summarize(
    candidate: Candidate,
    results: list[IterationResult],
    tick_seconds: float,
    unimplemented_talents: tuple[str, ...],
) -> CandidateSummary:
    """Reduce iterations to percentiles and a median time series."""
    n = len(results)
    series = np.vstack([r.dps_series for r in results])
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", category=RuntimeWarning)
        median_series = np.nanmedian(series, axis=0)
    damage: Counter[str] = Counter()
    casts: Counter[str] = Counter()
    blocked: Counter[str] = Counter()
    for r in results:
        damage.update(r.damage_by_source)
        casts.update(r.casts)
        blocked.update(r.blocked_seconds)
    total_damage = sum(damage.values()) or 1.0
    return CandidateSummary(
        candidate=candidate,
        iterations=n,
        total_dps=Percentiles.of(np.array([r.total_dps for r in results])),
        peak_dps=Percentiles.of(np.array([r.peak_dps for r in results])),
        times=np.arange(1, series.shape[1] + 1, dtype=np.float64) * tick_seconds,
        median_dps_series=median_series,
        damage_share={k: v / total_damage for k, v in damage.most_common()},
        casts_per_iteration={k: v / n for k, v in casts.most_common()},
        blocked_seconds_per_iteration={k: v / n for k, v in blocked.most_common()},
        mean_kills=float(np.mean([r.enemies_killed for r in results])),
        mean_drinking_time=float(np.mean([r.drinking_time for r in results])),
        unimplemented_talents=unimplemented_talents,
    )
