from __future__ import annotations

import json

import pytest

from gloss_eval import __main__ as cli
from gloss_eval import paths, runner
from gloss_eval.cases import load
from gloss_eval.client import NoToolCall
from gloss_eval.ledger import SpendLedger, worst_case_cost
from gloss_eval.request import system_prompt
from gloss_eval.guidance import build_all

HAIKU = "claude-haiku-4-5-20251001"
ROW_FIELDS = {
    "experiment", "arm", "case_id", "trial", "model", "selection", "sentence", "user_turn",
    "translation", "leaked_marks", "tool_input", "failures", "passed", "input_tokens",
    "output_tokens", "cost_usd", "error", "at",
}


def _run(experiment, case_file, out_dir, client, trials=2, ceiling=5.0):
    path = paths.CASES_DIR / case_file
    return runner.execute(experiment, path, load(path), HAIKU, trials, SpendLedger(ceiling),
                          4, out_dir, client, "test")


def _lines(path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]


def test_a_marks_run_writes_every_row_with_the_documented_fields(tmp_path, fake_client):
    client = fake_client()
    run_info, rows = _run("marks", "marks.json", tmp_path, client)
    written = _lines(tmp_path / "trials.jsonl")
    assert len(written) == len(rows) == 19 * 2 * 2 == len(client.calls)
    assert all(set(row) == ROW_FIELDS for row in written)
    assert {r["arm"] for r in written} == {"unmarked", "marked"}
    assert all(("«" in r["user_turn"]) == (r["arm"] == "marked") for r in written)
    assert {system for _, system, _ in client.calls} == {system_prompt()}
    assert run_info["requests_planned"] == 76 and run_info["refused_by_ceiling"] == 0
    assert run_info["cases_file"] == "cases/marks.json"
    assert (tmp_path / "report.md").exists() and (tmp_path / "run.json").exists()


def test_a_guidance_run_sends_each_arm_its_own_prompt(tmp_path, fake_client):
    client = fake_client()
    _, rows = _run("guidance", "haber.json", tmp_path, client)
    assert len(_lines(tmp_path / "trials.jsonl")) == 16 * 5 * 2
    prompts = build_all(system_prompt())
    assert all("«" in user for _, _, user in client.calls)
    by_system = {system for _, system, _ in client.calls}
    assert by_system == set(prompts.values())
    assert all(set(r) == ROW_FIELDS for r in rows)


def test_scoring_and_costs_land_in_the_row(tmp_path, fake_client):
    client = fake_client(answer=lambda s, u: {"translation": "«cold»", "senses": []},
                         tokens=(2000, 100))
    _, rows = _run("marks", "marks.json", tmp_path, client, trials=1)
    row = next(r for r in rows if r["case_id"] == "fria-sangre-fria-absorb")
    assert row["passed"] and row["failures"] == [] and row["leaked_marks"]
    assert row["translation"] == "«cold»"
    assert row["cost_usd"] == pytest.approx(0.0025)
    assert row["tool_input"] == {"translation": "«cold»", "senses": []}


def test_a_client_exception_becomes_an_error_row(tmp_path, fake_client):
    def flaky(system, user):
        if "Perla" in user:
            raise ConnectionError("reset by peer")
        return {"translation": "an answer", "senses": []}

    _, rows = _run("marks", "marks.json", tmp_path, fake_client(answer=flaky), trials=1)
    failed = [r for r in rows if r["error"]]
    assert len(failed) == 2
    assert all(r["error"] == "ConnectionError: reset by peer" and not r["passed"]
               and r["failures"] == ["request failed"] and r["cost_usd"] == 0 for r in failed)
    assert len(rows) == 38


def test_a_reply_without_a_tool_call_is_still_charged(tmp_path, fake_client):
    def no_tool(system, user):
        raise NoToolCall("max_tokens", 2400, 300)

    _, rows = _run("marks", "marks.json", tmp_path, fake_client(answer=no_tool), trials=1)
    assert all(r["error"].startswith("no tool_use block") for r in rows)
    assert rows[0]["cost_usd"] == pytest.approx(0.0039)


def test_a_tiny_ceiling_refuses_calls_and_the_run_completes(tmp_path, fake_client):
    client = fake_client()
    ceiling = worst_case_cost(HAIKU) * 3.5
    run_info, rows = _run("marks", "marks.json", tmp_path, client, trials=1, ceiling=ceiling)
    refused = [r for r in rows if r["error"] == "refused: spend ceiling"]
    assert len(rows) == 38
    assert len(client.calls) == 38 - len(refused)
    assert run_info["refused_by_ceiling"] == len(refused) > 0
    assert sum(r["cost_usd"] for r in rows) <= ceiling
    report = (tmp_path / "report.md").read_text(encoding="utf-8")
    assert f"{len(refused)} of 38 planned trials were not bought" in report


def test_out_refuses_to_overwrite(tmp_path, fake_client):
    _run("marks", "haber.json", tmp_path, fake_client(), trials=1)
    before = (tmp_path / "trials.jsonl").read_text(encoding="utf-8")
    with pytest.raises(runner.OutputExists):
        _run("marks", "haber.json", tmp_path, fake_client(), trials=1)
    assert (tmp_path / "trials.jsonl").read_text(encoding="utf-8") == before
    code = cli.main(["marks", "--cases", str(paths.CASES_DIR / "haber.json"), "--model",
                     "haiku", "--trials", "1", "--max-usd", "1", "--out", str(tmp_path)])
    assert code == 1


def test_a_live_run_needs_a_ceiling(tmp_path):
    code = cli.main(["marks", "--cases", str(paths.CASES_DIR / "haber.json"), "--model",
                     "haiku", "--trials", "1", "--out", str(tmp_path / "new")])
    assert code == 2
    assert not (tmp_path / "new").exists()


def test_a_dry_run_needs_no_key_and_writes_nothing(tmp_path, monkeypatch, capsys):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.setattr(paths, "ENV_FILE", tmp_path / "absent.env")
    code = cli.main(["guidance", "--cases", str(paths.CASES_DIR / "haber.json"), "--model",
                     "haiku", "--trials", "5", "--dry-run", "--out", str(tmp_path / "out")])
    out = capsys.readouterr().out
    assert code == 0
    assert "16 cases x 5 arms x 5 trials = 400 requests" in out
    assert out.count("first request of arm ") == 5
    assert out.count("“—Nadie podía «haberlo» sabido.”") == 5
    assert out.count("This word is the auxiliary") == 1
    assert "$1.8800" in out
    assert not (tmp_path / "out").exists()


def test_both_marks_arms_carry_the_passage_for_a_single_word():
    cases = load(paths.CASES_DIR / "marks.json")
    for case in cases:
        for arm in ("unmarked", "marked"):
            turn = runner.arm_turn("marks", arm, case)
            assert ("Earlier in the passage" in turn) == ("earlier" in case), (case["id"], arm)


def test_the_marks_arms_send_the_haber_clause_as_the_app_does():
    case = load(paths.CASES_DIR / "haber.json")[0]
    for arm in ("unmarked", "marked"):
        assert "This word is the auxiliary" in runner.arm_turn("marks", arm, case)
