"""The Markdown report for a run, built from its trial rows and its run record.

Counts only. Trials refused by the spend ceiling were never asked, so they are left out of every
rate and reported as a separate count; a failed request is a failed trial.

When the cases carry a `group`, the report also counts each group per arm, and how many answers
in the phrase-word group reported the phrase. When the rows carry `failures_as_first_scored`,
because a check was amended after they were scored, it gives the phrase-word counts both ways.
"""

from __future__ import annotations

from collections import Counter

from .cases import GROUPS
from .guidance import ARMS as GUIDANCE_ARMS
from .ledger import REFUSED
from .phrases import ARMS as PHRASES_ARMS

ARM_ORDER = ("unmarked", "marked", *GUIDANCE_ARMS, *PHRASES_ARMS)

GROUP_TITLES = {"phrase-word": "Phrase words", "exception": "Exceptions",
                "plain-word": "Plain words"}


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


def build(rows: list[dict], run_info: dict, cases: list[dict] | None = None) -> str:
    arms = [a for a in ARM_ORDER if any(r["arm"] == a for r in rows)]
    case_ids = sorted({r["case_id"] for r in rows})
    groups = {c["id"]: c["group"] for c in cases or [] if "group" in c}
    lines = ["# Gloss eval report", ""]
    lines += _run_section(rows, run_info)
    lines += _totals_section(rows, arms)
    if groups:
        lines += _groups_section(rows, arms, groups)
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
        f"- Started: {run_info['started_at'] or 'not recorded'}; finished: "
        f"{run_info['finished_at']} (UTC)",
        f"- Cost: ${run_info['total_cost_usd']:.4f} (ceiling ${run_info['max_usd']:.2f}, "
        f"${run_info['spent_before_usd']:.4f} already spent against it before this run)",
    ]
    if run_info["command"]:
        lines.append(f"- Command: `{run_info['command']}`")
    if run_info["package_version"]:
        lines.append(f"- Package version: {run_info['package_version']}")
    for key, label in (("measured_by", "Measured by"), ("request_check", "Requests"),
                       ("ceiling_note", "Ceiling")):
        if run_info.get(key):
            lines.append(f"- {label}: {run_info[key]}")
    lines.append("")
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


def _groups_section(rows: list[dict], arms: list[str], groups: dict[str, str]) -> list[str]:
    present = [g for g in GROUPS if g in groups.values()]
    first_scored = any("failures_as_first_scored" in r for r in rows)
    header = [GROUP_TITLES[g] for g in present]
    if first_scored:
        header.append("Phrase words, as first scored")
    header.append("Phrase words reporting the phrase")
    lines = ["## By group", "", "| Arm | " + " | ".join(header) + " |",
             "|---|" + "---:|" * len(header)]
    for arm in arms:
        in_arm = _bought([r for r in rows if r["arm"] == arm])
        cells = [_cell([r for r in in_arm if groups.get(r["case_id"]) == g]) for g in present]
        words = [r for r in in_arm if groups.get(r["case_id"]) == "phrase-word"]
        if first_scored:
            passes = sum(1 for r in words if not r["failures_as_first_scored"] and not r["error"])
            cells.append(f"{passes}/{len(words)}")
        cells.append(f"{sum(1 for r in words if r.get('phrase'))}/{len(words)}")
        lines.append(f"| {arm} | " + " | ".join(cells) + " |")
    lines.append("")
    if first_scored:
        lines.append("A check was amended after these answers were first scored. Every other "
                     "count in this report uses the checks as published.")
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
