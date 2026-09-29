"""Command line: python -m gloss_eval <validate|marks|guidance|phrases|replay>."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from . import cases as case_files
from . import paths, pricing, runner
from .client import GlossClient, MissingKey
from .ledger import REFUSED, WORST_CASE_INPUT_TOKENS, SpendLedger, worst_case_cost
from .replay import replay
from .request import MAX_TOKENS


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        return args.handler(args)
    except (ValueError, OSError, MissingKey) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="python -m gloss_eval")
    sub = parser.add_subparsers(required=True, metavar="command")

    validate = sub.add_parser("validate", help="check case files offline")
    validate.add_argument("files", nargs="*", type=Path,
                          help="case files (default: every .json in cases/)")
    validate.set_defaults(handler=cmd_validate)

    for name, blurb in (("marks", "unmarked against marked user turns"),
                        ("guidance", "five rungs of guidance for a pronoun on an auxiliary"),
                        ("phrases", "six single-word clauses for a word inside a fixed phrase")):
        run = sub.add_parser(name, help=blurb)
        run.add_argument("--cases", type=Path, required=True, help="case file")
        run.add_argument("--model", choices=list(pricing.MODELS), required=True)
        run.add_argument("--trials", type=_positive_int, required=True,
                         help="trials per case and arm")
        run.add_argument("--max-usd", type=float,
                         help="spend ceiling in USD, required for a live run")
        run.add_argument("--ledger", type=Path,
                         help="JSON file carrying the spend across invocations")
        run.add_argument("--workers", type=_positive_int, default=4,
                         help="requests in flight at once (default 4)")
        run.add_argument("--out", type=Path, help="results directory, required for a live run")
        run.add_argument("--dry-run", action="store_true",
                         help="print the plan and each arm's first request; send nothing")
        run.set_defaults(handler=cmd_run, experiment=name)

    rep = sub.add_parser("replay", help="re-score a results directory and rebuild its report")
    rep.add_argument("dir", type=Path)
    rep.set_defaults(handler=cmd_replay)
    return parser


def _positive_int(text: str) -> int:
    value = int(text)
    if value < 1:
        raise argparse.ArgumentTypeError("must be 1 or more")
    return value


def cmd_validate(args: argparse.Namespace) -> int:
    files = args.files or sorted(paths.CASES_DIR.glob("*.json"))
    if not files:
        print("error: no case files found", file=sys.stderr)
        return 1
    ok = True
    for path in files:
        try:
            loaded = case_files.load(path)
            print(f"{paths.display(path)}: {len(loaded)} cases, valid")
        except (case_files.CaseError, OSError) as exc:
            print(f"{paths.display(path)}: invalid: {exc}")
            ok = False
    return 0 if ok else 1


def cmd_run(args: argparse.Namespace) -> int:
    cases = case_files.load(args.cases)
    model = pricing.model_id(args.model)
    if args.dry_run:
        return _dry_run(args, cases, model)
    if args.max_usd is None or args.out is None:
        print("error: a live run needs --max-usd and --out (or use --dry-run)", file=sys.stderr)
        return 2
    runner.ensure_fresh(args.out)
    ledger = SpendLedger(args.max_usd, args.ledger)
    client = GlossClient()
    print(f"ceiling ${args.max_usd:.2f}, ${ledger.spent_before:.4f} already spent against it",
          file=sys.stderr)
    run_info, rows = runner.execute(args.experiment, args.cases, cases, model, args.trials,
                                    ledger, args.workers, args.out, client, _command(args))
    _print_summary(args.out, run_info, rows, ledger)
    return 0


def _command(args: argparse.Namespace) -> str:
    """The run's command with local paths (--out, --ledger) left out, since results are shared."""
    return (f"python -m gloss_eval {args.experiment} --cases {paths.display(args.cases)} "
            f"--model {args.model} --trials {args.trials} --max-usd {args.max_usd} "
            f"--workers {args.workers}")


def _dry_run(args: argparse.Namespace, cases: list[dict], model: str) -> int:
    jobs = runner.plan(args.experiment, cases, model, args.trials)
    arms = runner.ARMS[args.experiment]
    per_call = worst_case_cost(model)
    print(f"experiment: {args.experiment}")
    print(f"model: {model}")
    print(f"grid: {len(cases)} cases x {len(arms)} arms x {args.trials} trials = "
          f"{len(jobs)} requests")
    for arm in arms:
        first = next(job for job in jobs if job.arm == arm)
        print(f"first request of arm {arm}: case {first.case['id']}")
        print(f"  system prompt: {len(first.system)} characters")
        print("  user turn:")
        for line in first.user_turn.splitlines():
            print(f"    {line}")
    print(f"worst case for the grid: ${per_call * len(jobs):.4f} ({len(jobs)} x "
          f"${per_call:.4f}, each {WORST_CASE_INPUT_TOKENS[model]} input + {MAX_TOKENS} output tokens)")
    print("dry run: nothing sent")
    return 0


def _print_summary(out_dir: Path, run_info: dict, rows: list[dict],
                   ledger: SpendLedger) -> None:
    for arm in runner.ARMS[run_info["experiment"]]:
        bought = [r for r in rows if r["arm"] == arm and r["error"] != REFUSED]
        print(f"{arm}: {sum(r['passed'] for r in bought)}/{len(bought)} passed")
    print(f"cost ${run_info['total_cost_usd']:.4f}; ${ledger.spent:.4f} of "
          f"${ledger.ceiling_usd:.2f} spent against the ceiling")
    if run_info["refused_by_ceiling"]:
        print(f"{run_info['refused_by_ceiling']} trials not bought: refused by the spend ceiling")
    print(f"wrote {out_dir / 'trials.jsonl'}, {out_dir / 'report.md'}, {out_dir / 'run.json'}")


def cmd_replay(args: argparse.Namespace) -> int:
    result = replay(args.dir)
    if result.cases_changed:
        print("note: the case file has changed since the run; scored with the current checks")
    print(f"rescored {len(result.rows)} rows; rebuilt {args.dir / 'report.md'}")
    if result.changed:
        print(f"{len(result.changed)} rows changed verdict:")
        for line in result.changed:
            print(f"  {line}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
