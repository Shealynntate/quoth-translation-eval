"""The Markdown report for a run, built from its trial rows and its run record.

Counts only. Trials refused by the spend ceiling were never asked, so they are left out of every
rate and reported as a separate count; a failed request is a failed trial.
"""

from __future__ import annotations

from collections import Counter

from .guidance import ARMS as GUIDANCE_ARMS
from .ledger import REFUSED

ARM_ORDER = ("unmarked", "marked", *GUIDANCE_ARMS)


def _bought(rows: list[dict]) -> list[dict]:
    return [r for r in rows if r["error"] != REFUSED]


def _percent(passes: int, trials: int) -> str:
    if not trials:
        return "n/a"
    return f"{(200 * passes + trials) // (2 * trials)}%"


def _cell(rows: list[dict]) -> str:
    bought = _bought(rows)
    return f"{sum(r['passed'] for r in bought)}/{len(bought)}"


def _one_line(text: str) -> str:
    return " ".join(text.split())


def _answer_key(row: dict) -> str:
    if row["error"]:
        return f"(no answer: {_one_line(row['error'])})"
    return f'"{_one_line(row["translation"])}"'


def build(rows: list[dict], run_info: dict) -> str:
    arms = [a for a in ARM_ORDER if any(r["arm"] == a for r in rows)]
    case_ids = sorted({r["case_id"] for r in rows})
    lines = ["# Gloss eval report", ""]
    lines += _run_section(rows, run_info)
    lines += _totals_section(rows, arms)
    lines += _per_case_section(rows, arms, case_ids)
    lines += _answers_section(rows, arms, case_ids)
    return "\n".join(lines) + "\n"


def _run_section(rows: list[dict], run_info: dict) -> list[str]:
    bought = _bought(rows)
    refused = len(rows) - len(bought)
    errors = sum(1 for r in bought if r["error"])
    leaks = sum(1 for r in bought if r["leaked_marks"])
    lines = [
        "## Run",
        "",
        f"- Experiment: {run_info['experiment']}",
        f"- Model: `{run_info['model']}`",
        f"- Cases: `{run_info['cases_file']}` (sha256 `{run_info['cases_sha256'][:12]}`)",
        f"- Trials per case and arm: {run_info['trials']}",
        f"- Started: {run_info['started_at']}; finished: {run_info['finished_at']} (UTC)",
        f"- Cost: ${run_info['total_cost_usd']:.4f} (ceiling ${run_info['max_usd']:.2f}, "
        f"${run_info['spent_before_usd']:.4f} already spent against it before this run)",
        f"- Command: `{run_info['command']}`",
        f"- Package version: {run_info['package_version']}",
        "",
    ]
    if refused:
        lines.append(f"**{refused} of {len(rows)} planned trials were not bought**: the spend "
                     "ceiling refused them before they were sent. They are excluded from every "
                     "count below.")
    else:
        lines.append(f"All {len(rows)} planned trials were bought.")
    lines.append("")
    lines.append(f"Failed requests (counted as failed trials): {errors}.")
    lines.append(f"Answers that carried « or » (scored with the marks removed): {leaks}.")
    lines.append("")
    return lines


def _totals_section(rows: list[dict], arms: list[str]) -> list[str]:
    lines = ["## Totals", "", "| Arm | Passes | Trials | Rate |", "|---|---:|---:|---:|"]
    for arm in arms:
        bought = _bought([r for r in rows if r["arm"] == arm])
        passes = sum(r["passed"] for r in bought)
        lines.append(f"| {arm} | {passes} | {len(bought)} | {_percent(passes, len(bought))} |")
    lines.append("")
    return lines


def _per_case_section(rows: list[dict], arms: list[str], case_ids: list[str]) -> list[str]:
    lines = ["## Per case", "", "| Case | " + " | ".join(arms) + " |",
             "|---|" + "---:|" * len(arms)]
    for cid in case_ids:
        cells = [_cell([r for r in rows if r["case_id"] == cid and r["arm"] == arm])
                 for arm in arms]
        lines.append(f"| {cid} | " + " | ".join(cells) + " |")
    lines.append("")
    return lines


def _answers_section(rows: list[dict], arms: list[str], case_ids: list[str]) -> list[str]:
    lines = ["## Answers", ""]
    for cid in case_ids:
        case_rows = [r for r in rows if r["case_id"] == cid]
        lines += [f"### {cid}", "", f"Selection: \"{case_rows[0]['selection']}\"", ""]
        for arm in arms:
            bought = _bought([r for r in case_rows if r["arm"] == arm])
            if not bought:
                continue
            lines.append(f"{arm}:")
            lines.append("")
            tally = Counter(_answer_key(r) for r in bought)
            example = {_answer_key(r): r for r in bought}
            for answer, count in tally.most_common():
                row = example[answer]
                verdict = "pass" if row["passed"] else "fail: " + "; ".join(row["failures"])
                lines.append(f"- {count} x {answer}: {verdict}")
            lines.append("")
    return lines
