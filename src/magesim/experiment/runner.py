"""Monte Carlo execution of candidates."""

import random
from collections.abc import Callable

from magesim.engine.simulator import Simulation
from magesim.experiment.candidates import Candidate
from magesim.experiment.stats import CandidateSummary, summarize
from magesim.model.meta import MetaConfig

type ProgressCallback = Callable[[Candidate, CandidateSummary], None]


def run_candidate(candidate: Candidate, meta: MetaConfig) -> CandidateSummary:
    """Simulate one candidate for `meta.iterations` iterations."""
    sim = Simulation(
        candidate.character,
        candidate.encounter,
        candidate.talents,
        candidate.rotation,
        tick_seconds=meta.tick_seconds,
        peak_warmup_seconds=meta.peak_warmup_seconds,
    )
    rng = random.Random(f"{meta.seed}:{candidate.number}")
    results = [sim.run(rng) for _ in range(meta.iterations)]
    return summarize(candidate, results, meta.tick_seconds, sim.modifiers.unimplemented)


def run_all(
    candidates: list[Candidate],
    meta: MetaConfig,
    on_done: ProgressCallback | None = None,
) -> list[CandidateSummary]:
    """Simulate every candidate in order."""
    summaries: list[CandidateSummary] = []
    for candidate in candidates:
        summary = run_candidate(candidate, meta)
        summaries.append(summary)
        if on_done is not None:
            on_done(candidate, summary)
    return summaries
