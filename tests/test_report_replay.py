from __future__ import annotations

import json

from gloss_eval import __main__ as cli
from gloss_eval import paths, report, runner
from gloss_eval.cases import load
from gloss_eval.ledger import SpendLedger

HAIKU = "claude-haiku-4-5-20251001"
RUN_INFO = {
    "experiment": "marks", "model": HAIKU, "cases_file": "cases/marks.json",
    "cases_sha256": "0" * 64, "trials": 2, "started_at": "2026-01-01T00:00:00+00:00",
    "finished_at": "2026-01-01T00:01:00+00:00", "total_cost_usd": 0.01, "max_usd": 1.0, "spent_before_usd": 0.0,
    "command": "python -m gloss_eval marks", "package_version": "0.1.0",
}


def _row(case_id, arm, trial, translation, passed, failures=(), error=None):
    return {"experiment": "marks", "arm": arm, "case_id": case_id, "trial": trial,
            "model": HAIKU, "selection": "fría", "sentence": "a sangre fría.", "user_turn": "",
            "translation": translation, "leaked_marks": False, "tool_input": None,
            "failures": list(failures), "passed": passed, "input_tokens": 0,
            "output_tokens": 0, "cost_usd": 0.0, "error": error, "at": ""}


ROWS = [
    _row("a-case", "unmarked", 1, "cold-blooded", False, ['absorbed "blood"']),
    _row("a-case", "unmarked", 2, "cold", True),
    _row("a-case", "marked", 1, "cold", True),
    _row("a-case", "marked", 2, "cold", True),
    _row("b-case", "unmarked", 1, None, False, ["request failed"], "TimeoutError: slow"),
    _row("b-case", "unmarked", 2, "cold", True),
    _row("b-case", "marked", 1, "cold", True),
    _row("b-case", "marked", 2, None, False, ["refused: spend ceiling"],
         "refused: spend ceiling"),
]


def test_report_totals_and_cells():
    text = report.build(ROWS, RUN_INFO)
    assert "| unmarked | 2 | 4 | 50% |" in text
    assert "| marked | 3 | 3 | 100% |" in text
    assert "| a-case | 1/2 | 2/2 |" in text
    assert "| b-case | 1/2 | 1/1 |" in text
    assert "**1 of 8 planned trials were not bought**" in text
    assert "Failed requests (counted as failed trials): 1." in text
    assert '- 2 x "cold": pass' in text
    assert '- 1 x "cold-blooded": fail: absorbed "blood"' in text
    assert "- 1 x (no answer: TimeoutError: slow): fail: request failed" in text


def test_report_rounds_rates_to_whole_percent():
    rows = [_row("c", "marked", t, "x", t == 1) for t in (1, 2, 3)]
    assert "| marked | 1 | 3 | 33% |" in report.build(rows, RUN_INFO)
    rows = [_row("c", "marked", t, "x", t <= 2) for t in (1, 2, 3)]
    assert "| marked | 2 | 3 | 67% |" in report.build(rows, RUN_INFO)


def _recorded_run(tmp_path, fake_client):
    answers = {"«fría»": "cold-blooded", "«tras»": "one after another"}

    def answer(system, user):
        hit = next((v for k, v in answers.items() if k in user), "an answer")
        return {"translation": hit, "senses": []}

    path = paths.CASES_DIR / "marks.json"
    runner.execute("marks", path, load(path), HAIKU, 2, SpendLedger(5.0), 4, tmp_path,
                   fake_client(answer=answer), "test")
    return tmp_path


def test_replay_reproduces_the_recorded_verdicts(tmp_path, fake_client, capsys):
    out = _recorded_run(tmp_path, fake_client)
    original = (out / "report.md").read_text(encoding="utf-8")
    (out / "report.md").unlink()
    assert cli.main(["replay", str(out)]) == 0
    assert (out / "report.md").read_text(encoding="utf-8") == original
    assert "changed verdict" not in capsys.readouterr().out


def test_replay_flags_a_tampered_row(tmp_path, fake_client, capsys):
    out = _recorded_run(tmp_path, fake_client)
    rows = [json.loads(line) for line in (out / "trials.jsonl").read_text("utf-8").splitlines()]
    target = next(r for r in rows if r["case_id"] == "fria-sangre-fria-absorb")
    assert target["passed"] is False
    target["passed"] = True
    (out / "trials.jsonl").write_text(
        "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")
    assert cli.main(["replay", str(out)]) == 1
    printed = capsys.readouterr().out
    assert "1 rows changed verdict" in printed
    assert (f"fria-sangre-fria-absorb / {target['arm']} / trial {target['trial']}: "
            "recorded pass, now fail") in printed


def test_replay_names_a_missing_case_file(tmp_path, fake_client, capsys):
    out = _recorded_run(tmp_path, fake_client)
    run_info = json.loads((out / "run.json").read_text(encoding="utf-8"))
    run_info["cases_file"] = "cases/gone.json"
    (out / "run.json").write_text(json.dumps(run_info), encoding="utf-8")
    assert cli.main(["replay", str(out)]) == 1
    err = capsys.readouterr().err
    assert "case file named in run.json was not found at" in err
    assert err.rstrip().endswith("cases/gone.json")
