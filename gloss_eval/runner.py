"""Running a grid of (case, arm, trial) requests through the spend ceiling.

Three experiments:

    marks      arms "unmarked" and "marked": the same system prompt; the sentence is sent plain,
               or with the selection wrapped in « » at its real position.
    guidance   arms "no-guidance", "rule", "rule+example", "second-example" and "turn-clause":
               a ladder of guidance for a pronoun attached to an auxiliary (see `guidance`); the
               sentence is always sent marked.
    phrases    arms "no-clause", "own-meaning+exception", "own-meaning", "words-outside",
               "three-examples" and "adverb-examples": one clause each on a single plain word
               (see `phrases`); the sentence is always sent marked.

In all three, a single-word selection whose case carries an `earlier` passage sends it, as the app
does (see `request.user_turn`).

Every trial becomes one row of `trials.jsonl`, written as soon as the trial finishes so a crash
loses nothing already bought. The fields of a row:

    experiment     "marks", "guidance" or "phrases"
    arm            one of the experiment's arms
    case_id        the case's id
    trial          1-based trial number within the (case, arm) cell
    model          the model id the request named
    selection      the case's selection
    sentence       the case's sentence, unmarked
    user_turn      the user message exactly as sent, earlier passage included
    translation    the `translation` field exactly as returned (null when there is no answer)
    leaked_marks   whether that raw translation carried « or »
    tool_input     the whole tool input the model returned (null when there is no answer)
    failures       the checks the answer failed, or the reason there is no answer
    passed         true only for an answer that failed no check
    input_tokens   billed input tokens
    output_tokens  billed output tokens
    cost_usd       what the call cost at the prices in `pricing`
    error          null, the request's error, or "refused: spend ceiling" for a call never sent
    at             when the trial finished, UTC ISO 8601

A phrases row also carries the fixed phrase the model reported, because whether the phrase
reaches the reader is part of that experiment:

    phrase         the `expression` field as returned, or null when none was reported
    phrase_meaning the `expressionMeaning` field as returned, or null

A recorded run whose case file has since had a check amended also carries, in every row,
`failures_as_first_scored`: the failures under the checks in force when the row was scored.

A failed request is a failed trial: the app would have shown the reader nothing. A call refused
by the ceiling is neither a pass nor a failure, because nothing was asked; the report counts
those separately.
"""

from __future__ import annotations

import hashlib
import json
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Protocol

from . import __version__, guidance, paths, phrases, pricing, report
from .client import NoToolCall
from .ledger import REFUSED, SpendLedger
from .marks import has_marks
from .request import marked_turn, system_prompt, user_turn
from .scoring import failures

ARMS = {
    "marks": ("unmarked", "marked"),
    "guidance": guidance.ARMS,
    "phrases": phrases.ARMS,
}


class Client(Protocol):
    def ask(self, model: str, system: str, user: str) -> tuple[dict, int, int]: ...


class OutputExists(FileExistsError):
    pass


@dataclass(frozen=True)
class Job:
    experiment: str
    arm: str
    case: dict
    trial: int
    model: str
    system: str
    user_turn: str


def system_prompts(experiment: str) -> dict[str, str]:
    """The system prompt each arm of `experiment` sends."""
    shipped = system_prompt()
    if experiment == "guidance":
        return guidance.build_all(shipped)
    return {arm: shipped for arm in ARMS[experiment]}


def arm_turn(experiment: str, arm: str, case: dict) -> str:
    """The user turn `arm` sends for `case`. The marks arms send the app's turn; the guidance
    arms send it without the haber clause, except the arm that tests that clause; the phrases
    arms send the app's turn with their own single-word clause."""
    selection, sentence, earlier = case["selection"], case["sentence"], case.get("earlier")
    if experiment == "phrases":
        return marked_turn(selection, sentence, earlier, single_word=phrases.clause(arm))
    if arm == "unmarked":
        return user_turn(selection, sentence, earlier)
    with_clause = experiment == "marks" or arm in guidance.HABER_CLAUSE_ARMS
    return marked_turn(selection, sentence, earlier, with_haber_clause=with_clause)


def plan(experiment: str, cases: list[dict], model: str, trials: int) -> list[Job]:
    """Every request of the grid, case by case, so a ceiling stop leaves whole cases unbought
    rather than every case short of trials. A phrases case that repeats a clause's own example
    stops the plan here, before anything is sent."""
    if experiment == "phrases":
        phrases.refuse_example_cases(cases)
    systems = system_prompts(experiment)
    jobs = []
    for case in cases:
        for arm in ARMS[experiment]:
            turn = arm_turn(experiment, arm, case)
            for trial in range(1, trials + 1):
                jobs.append(Job(experiment, arm, case, trial, model, systems[arm], turn))
    return jobs


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _row(job: Job, **fields) -> dict:
    row = {
        "experiment": job.experiment,
        "arm": job.arm,
        "case_id": job.case["id"],
        "trial": job.trial,
        "model": job.model,
        "selection": job.case["selection"],
        "sentence": job.case["sentence"],
        "user_turn": job.user_turn,
        "translation": None,
        "leaked_marks": False,
        "tool_input": None,
        "failures": [],
        "passed": False,
        "input_tokens": 0,
        "output_tokens": 0,
        "cost_usd": 0.0,
        "error": None,
    }
    if job.experiment == "phrases":
        row["phrase"] = None
        row["phrase_meaning"] = None
    row.update(fields)
    row["at"] = _now()
    return row


def run_trial(job: Job, client: Client, ledger: SpendLedger) -> dict:
    """One request. Never raises: whatever happens becomes a row, so one bad call cannot stop
    a run that has already spent money."""
    reserved = ledger.claim(job.model)
    if reserved is None:
        return _row(job, error=REFUSED, failures=[REFUSED])
    try:
        tool_input, tokens_in, tokens_out = client.ask(job.model, job.system, job.user_turn)
    except NoToolCall as exc:
        cost = pricing.cost_usd(job.model, exc.input_tokens, exc.output_tokens)
        ledger.settle(job.model, reserved, cost)
        return _row(job, error=str(exc), failures=["request failed"], cost_usd=cost,
                    input_tokens=exc.input_tokens, output_tokens=exc.output_tokens)
    except Exception as exc:  # noqa: BLE001  recorded in the row, never swallowed
        ledger.settle(job.model, reserved, 0.0)
        return _row(job, error=f"{type(exc).__name__}: {exc}", failures=["request failed"])
    cost = pricing.cost_usd(job.model, tokens_in, tokens_out)
    ledger.settle(job.model, reserved, cost)
    raw = tool_input.get("translation")
    translation = raw if isinstance(raw, str) else ""
    failed = failures(job.case, translation)
    extra = {}
    if job.experiment == "phrases":
        extra = {"phrase": _reported(tool_input, "expression"),
                 "phrase_meaning": _reported(tool_input, "expressionMeaning")}
    return _row(job, translation=translation, leaked_marks=has_marks(translation),
                tool_input=tool_input, failures=failed, passed=not failed,
                input_tokens=tokens_in, output_tokens=tokens_out, cost_usd=cost, **extra)


def _reported(tool_input: dict, field: str) -> str | None:
    """A text field of the answer as returned, or None when it is missing or blank."""
    value = tool_input.get(field)
    return value if isinstance(value, str) and value.strip() else None


def run_grid(jobs: list[Job], client: Client, ledger: SpendLedger, trials_path: Path,
             workers: int) -> list[dict]:
    rows: list[dict] = []
    with trials_path.open("x", encoding="utf-8") as out, \
            ThreadPoolExecutor(max_workers=workers) as pool:
        futures = [pool.submit(run_trial, job, client, ledger) for job in jobs]
        for done, future in enumerate(as_completed(futures), 1):
            row = future.result()
            out.write(json.dumps(row, ensure_ascii=False) + "\n")
            out.flush()
            rows.append(row)
            print(f"\r  {done}/{len(jobs)} trials, ${ledger.spent_here:.4f}",
                  end="", file=sys.stderr, flush=True)
    print(file=sys.stderr)
    return rows


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def ensure_fresh(out_dir: Path) -> None:
    if (out_dir / "trials.jsonl").exists():
        raise OutputExists(f"{out_dir / 'trials.jsonl'} already exists; choose another --out")


def execute(experiment: str, cases_path: Path, cases: list[dict], model: str, trials: int,
            ledger: SpendLedger, workers: int, out_dir: Path, client: Client,
            command: str) -> tuple[dict, list[dict]]:
    """Run the whole grid into `out_dir`. Returns the run record (as written to run.json) and
    the rows."""
    ensure_fresh(out_dir)
    jobs = plan(experiment, cases, model, trials)
    out_dir.mkdir(parents=True, exist_ok=True)
    started = _now()
    rows = run_grid(jobs, client, ledger, out_dir / "trials.jsonl", workers)
    run_info = {
        "command": command,
        "experiment": experiment,
        "model": model,
        "trials": trials,
        "cases_file": paths.display(cases_path),
        "cases_sha256": sha256_file(cases_path),
        "prompt_sha256": {arm: sha256_text(s) for arm, s in system_prompts(experiment).items()},
        "tool_schema_sha256": sha256_file(paths.TOOL_SCHEMA),
        "started_at": started,
        "finished_at": _now(),
        "requests_planned": len(jobs),
        "total_cost_usd": round(sum(r["cost_usd"] for r in rows), 6),
        "max_usd": ledger.ceiling_usd,
        "spent_before_usd": round(ledger.spent_before, 6),
        "refused_by_ceiling": sum(1 for r in rows if r["error"] == REFUSED),
        "package_version": __version__,
        "prices": pricing.price_table(),
    }
    (out_dir / "run.json").write_text(json.dumps(run_info, indent=2) + "\n", encoding="utf-8")
    (out_dir / "report.md").write_text(report.build(rows, run_info, cases), encoding="utf-8")
    return run_info, rows
