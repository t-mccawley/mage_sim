"""Monte Carlo execution of candidates."""

import random
from collections.abc import Callable
from dataclasses import dataclass

from magesim.engine.simulator import Simulation
from magesim.engine.state import UnavailableSpellError
from magesim.experiment.candidates import Candidate, InvalidCandidate
from magesim.experiment.stats import CandidateSummary, summarize
from magesim.model.meta import MetaConfig
from magesim.spells.definitions import SpellCatalog

type ProgressCallback = Callable[[Candidate, CandidateSummary], None]


@dataclass(frozen=True, slots=True)
class RunResults:
    """Summaries of completed candidates, plus any found invalid mid-run."""

    summaries: list[CandidateSummary]
    invalid: list[InvalidCandidate]


def run_candidate(
    candidate: Candidate, catalog: SpellCatalog, meta: MetaConfig
) -> CandidateSummary:
    """Simulate one candidate for `meta.iterations` iterations."""
    sim = Simulation(
        candidate.character,
        candidate.encounter,
        candidate.talents,
        candidate.rotation,
        catalog,
        tick_seconds=meta.tick_seconds,
        peak_warmup_seconds=meta.peak_warmup_seconds,
    )
    rng = random.Random(f"{meta.seed}:{candidate.number}")
    results = [sim.run(rng) for _ in range(meta.iterations)]
    return summarize(candidate, results, meta, sim.modifiers.unimplemented)


def run_all(
    candidates: list[Candidate],
    catalog: SpellCatalog,
    meta: MetaConfig,
    on_done: ProgressCallback | None = None,
) -> RunResults:
    """Simulate every candidate in order."""
    summaries: list[CandidateSummary] = []
    invalid: list[InvalidCandidate] = []
    for candidate in candidates:
        try:
            summary = run_candidate(candidate, catalog, meta)
        except UnavailableSpellError as error:
            invalid.append(InvalidCandidate.of(candidate, str(error)))
            continue
        summaries.append(summary)
        if on_done is not None:
            on_done(candidate, summary)
    return RunResults(summaries, invalid)
