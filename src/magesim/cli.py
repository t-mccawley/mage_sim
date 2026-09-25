"""`magesim` command line entry point."""

import argparse
import sys
import webbrowser
from pathlib import Path

from magesim.config_loader import Configs, load_configs
from magesim.experiment.candidates import Candidate, build_candidates
from magesim.experiment.runner import run_all
from magesim.experiment.stats import CandidateSummary
from magesim.report.html import write_report
from magesim.talents.wowhead import refresh_snapshot


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog="magesim", description="WoW Forever mage DpS simulator.")
    parser.add_argument("--configs", type=Path, default=Path("configs"), help="configs directory")
    parser.add_argument("--no-open", action="store_true", help="do not open the report")
    parser.add_argument(
        "--refresh-talents", action="store_true", help="re-download Wowhead talent data first"
    )
    return parser.parse_args(argv)


def _print_skipped(configs: Configs, candidates: list[Candidate]) -> None:
    used = {c.talents.url for c in candidates}
    levels = {c.level for c in configs.characters}
    for build in configs.talents:
        if build.url not in used:
            print(
                f"  skipped talents {build.display_name}: requires level "
                f"{build.required_level}, characters are {sorted(levels)}"
            )
    types = {e.encounter_type for e in configs.encounters}
    for rotation in configs.rotations:
        if rotation.encounter_type not in types:
            kind = rotation.encounter_type
            print(f"  skipped rotation {rotation.display_name}: no {kind} encounter")


def _progress(candidate: Candidate, summary: CandidateSummary) -> None:
    d = summary.total_dps
    print(
        f"  {candidate.label:>4} {d.median:8.1f} DpS  [{d.low:.1f} - {d.high:.1f}]  "
        f"{candidate.rotation.display_name} | {candidate.talents.display_name} | "
        f"{candidate.encounter.display_name}"
    )


def main(argv: list[str] | None = None) -> int:
    """Run all compatible candidates and write the HTML report."""
    args = _parse_args(argv)
    if args.refresh_talents:
        print(f"Talent data refreshed: {refresh_snapshot()}")
    configs = load_configs(args.configs)
    candidates = build_candidates(
        configs.characters, configs.encounters, configs.rotations, configs.talents
    )
    print(f"{len(candidates)} candidates, {configs.meta.iterations} iterations each")
    _print_skipped(configs, candidates)
    if not candidates:
        print("Nothing to simulate: check encounter types and talent levels.", file=sys.stderr)
        return 1
    summaries = run_all(candidates, configs.meta, on_done=_progress)
    path = write_report(summaries, configs.meta)
    print(f"Report: {path.resolve()}")
    if configs.meta.open_report and not args.no_open:
        webbrowser.open(path.resolve().as_uri())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
