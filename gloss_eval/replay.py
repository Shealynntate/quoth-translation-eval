"""Re-score a recorded run offline and rebuild its report.

The recorded answers are evidence and are never rewritten; only report.md is regenerated. Scoring
uses the checks in the case file as it is now, so an edited check shows up here as a changed
verdict, and every changed verdict is listed so an edit cannot quietly move a published number.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from . import cases as case_files
from . import paths, report
from .marks import has_marks
from .runner import sha256_file
from .scoring import failures


@dataclass
class Replay:
    rows: list[dict]
    changed: list[str]
    cases_changed: bool


def read_rows(trials_path: Path) -> list[dict]:
    with trials_path.open(encoding="utf-8") as fh:
        return [json.loads(line) for line in fh if line.strip()]


def rescore(row: dict, case: dict | None) -> dict:
    """`row` scored again. Rows without an answer keep their recorded failures."""
    if row["error"]:
        return {**row, "passed": False}
    if case is None:
        raise ValueError(f"case {row['case_id']!r} is no longer in the case file")
    failed = failures(case, row["translation"])
    return {**row, "failures": failed, "passed": not failed,
            "leaked_marks": has_marks(row["translation"])}


def replay(out_dir: Path) -> Replay:
    run_info = json.loads((out_dir / "run.json").read_text(encoding="utf-8"))
    cases_path = paths.REPO_ROOT / run_info["cases_file"]
    if not cases_path.exists():
        raise FileNotFoundError(f"the case file named in run.json was not found at {cases_path}")
    by_id = {c["id"]: c for c in case_files.load(cases_path)}
    recorded = read_rows(out_dir / "trials.jsonl")
    rows, changed = [], []
    for old in recorded:
        new = rescore(old, by_id.get(old["case_id"]))
        if new["passed"] != old["passed"]:
            changed.append(f"{old['case_id']} / {old['arm']} / trial {old['trial']}: recorded "
                           f"{_verdict(old['passed'])}, now {_verdict(new['passed'])}")
        rows.append(new)
    (out_dir / "report.md").write_text(report.build(rows, run_info), encoding="utf-8")
    return Replay(rows, changed, sha256_file(cases_path) != run_info["cases_sha256"])


def _verdict(passed: bool) -> str:
    return "pass" if passed else "fail"
