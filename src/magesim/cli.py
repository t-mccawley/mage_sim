"""`magesim` command line entry point."""

import argparse
import sys
import webbrowser
from pathlib import Path

from magesim.config_loader import Configs, load_configs, load_spell_catalog
from magesim.experiment.candidates import Candidate, build_candidates
from magesim.experiment.runner import run_all
from magesim.experiment.stats import CandidateSummary
from magesim.report.html import write_report
from magesim.spells.export import write_spellbook_csv
from magesim.talents.wowhead import refresh_snapshot

RUN_COMMAND = "run"
SPELLBOOK_COMMAND = "spellbook"
STDOUT_PATH = "-"
DEFAULT_SPELLBOOK_CSV = Path("results") / "spellbook.csv"


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog="magesim", description="WoW Forever mage DpS simulator.")
    parser.add_argument("--configs", type=Path, default=Path("configs"), help="configs directory")
    parser.add_argument("--no-open", action="store_true", help="do not open the report")
    parser.add_argument(
        "--refresh-talents", action="store_true", help="re-download Wowhead talent data first"
    )
    commands = parser.add_subparsers(dest="command")
    commands.add_parser(RUN_COMMAND, help="simulate all candidates (default)")
    spellbook = commands.add_parser(
        SPELLBOOK_COMMAND, help="export configured spell ranks and calculated coefficients"
    )
    spellbook.add_argument(
        "--out",
        default=str(DEFAULT_SPELLBOOK_CSV),
        help=f"CSV path, or '{STDOUT_PATH}' for stdout (default: {DEFAULT_SPELLBOOK_CSV})",
    )
    return parser.parse_args(argv)


def _export_spellbook(configs_dir: Path, out: str) -> int:
    catalog = load_spell_catalog(configs_dir)
    if out == STDOUT_PATH:
        write_spellbook_csv(catalog, None)
        return 0
    path = Path(out)
    write_spellbook_csv(catalog, path)
    print(f"Spellbook: {path.resolve()}")
    return 0


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
    """Run a MageSim command (default: simulate and write the HTML report)."""
    args = _parse_args(argv)
    if args.command == SPELLBOOK_COMMAND:
        return _export_spellbook(args.configs, args.out)
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
    summaries = run_all(candidates, configs.catalog, configs.meta, on_done=_progress)
    path = write_report(summaries, configs.meta)
    print(f"Report: {path.resolve()}")
    if configs.meta.open_report and not args.no_open:
        webbrowser.open(path.resolve().as_uri())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
