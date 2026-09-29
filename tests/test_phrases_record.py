"""The proof that the phrases record is what this package sends and scores.

The 900 rows in results/2026-09-29-phrases-haiku were sent by the app's private harness, not by
this package. So every row is rebuilt here from cases/phrases.json and must match what was
recorded, byte for byte: the user turn, the system prompt, the tool schema. Every row is scored
again under the published checks, and under the checks in force when it was first scored, and
must land on the recorded verdict both times. No row is skipped.
"""

from __future__ import annotations

import json
import shutil
from collections import Counter

import pytest

from gloss_eval import __main__ as cli
from gloss_eval import paths, phrases, pricing, runner
from gloss_eval.cases import checks_as_first_written, load
from gloss_eval.replay import read_rows
from gloss_eval.scoring import failures

RUN_DIR = paths.REPO_ROOT / "results" / "2026-09-29-phrases-haiku"
RUN = json.loads((RUN_DIR / "run.json").read_text(encoding="utf-8"))
ROWS = read_rows(RUN_DIR / "trials.jsonl")
CASES = {c["id"]: c for c in load(paths.CASES_DIR / "phrases.json")}
ROUND_OF = {arm: int(n) for n, arms in RUN["rounds"].items() for arm in arms}


def _first_difference(built: str, recorded: str) -> str:
    at = next((i for i, (a, b) in enumerate(zip(built, recorded)) if a != b),
              min(len(built), len(recorded)))
    return f"first difference at character {at}: built {built[at:at + 60]!r}, " \
           f"recorded {recorded[at:at + 60]!r}"


def test_the_record_is_the_whole_grid_once():
    assert len(ROWS) == RUN["requests_planned"] == 900
    keys = Counter((r["case_id"], r["arm"], r["trial"]) for r in ROWS)
    grid = {(cid, arm, t) for cid in CASES for arm in phrases.ARMS for t in range(1, 6)}
    assert set(keys) == grid and set(keys.values()) == {1}
    assert {r["experiment"] for r in ROWS} == {"phrases"}
    assert {r["model"] for r in ROWS} == {RUN["model"]} == {pricing.model_id("haiku")}
    assert not any(r["error"] for r in ROWS)


def test_every_user_turn_rebuilds_byte_for_byte():
    for n, row in enumerate(ROWS, 1):
        case = CASES[row["case_id"]]
        assert row["selection"] == case["selection"] and row["sentence"] == case["sentence"]
        built = runner.arm_turn("phrases", row["arm"], case)
        assert built == row["user_turn"], (
            f"row {n} ({row['case_id']} / {row['arm']} / trial {row['trial']}) does not rebuild: "
            + _first_difference(built, row["user_turn"]))


def test_the_system_prompt_and_tool_schema_are_the_ones_sent():
    systems = runner.system_prompts("phrases")
    for arm in phrases.ARMS:
        assert runner.sha256_text(systems[arm]) == RUN["prompt_sha256"][arm]
        assert RUN["prompt_sha256"][arm] == RUN["sent_system_prompt_sha256"]
    assert runner.sha256_file(paths.SYSTEM_PROMPT) == RUN["sent_system_prompt_sha256"]
    assert runner.sha256_file(paths.TOOL_SCHEMA) == RUN["sent_tool_schema_sha256"]
    assert RUN["tool_schema_sha256"] == RUN["sent_tool_schema_sha256"]


def test_the_case_file_is_the_one_the_record_names():
    assert RUN["cases_file"] == "cases/phrases.json"
    assert runner.sha256_file(paths.CASES_DIR / "phrases.json") == RUN["cases_sha256"]


def test_the_record_names_the_arms_as_the_package_does():
    assert RUN["private_arm_names"] == phrases.PRIVATE_NAMES
    assert {int(n): tuple(a) for n, a in RUN["rounds"].items()} == phrases.ROUNDS
    assert RUN["verified_with_package_version"] == "0.2.0"


def test_every_row_rescores_to_its_recorded_verdict():
    for row in ROWS:
        failed = failures(CASES[row["case_id"]], row["translation"])
        assert failed == row["failures"], (row["case_id"], row["arm"], row["trial"])
        assert row["passed"] is (not failed)


def test_every_row_rescores_to_its_first_verdict_under_the_checks_then_in_force():
    for row in ROWS:
        case = CASES[row["case_id"]]
        in_force = checks_as_first_written(case) if ROUND_OF[row["arm"]] == 1 else case
        assert failures(in_force, row["translation"]) == row["failures_as_first_scored"], (
            row["case_id"], row["arm"], row["trial"])


def test_only_the_amended_case_changed_verdict():
    moved = {r["case_id"] for r in ROWS
             if bool(r["failures"]) != bool(r["failures_as_first_scored"])}
    assert moved == {"hizo-hizo-caso"}
    assert set(RUN["amended_checks"]) == {c for c in CASES if "amended" in CASES[c]}


def test_the_answer_fields_agree_with_the_tool_input():
    for row in ROWS:
        tool = row["tool_input"]
        assert row["translation"] == (tool.get("translation") or "")
        for field, key in (("phrase", "expression"), ("phrase_meaning", "expressionMeaning")):
            value = tool.get(key)
            reported = value if isinstance(value, str) and value.strip() else None
            assert row[field] == reported, (row["case_id"], row["arm"], row["trial"], field)


def test_costs_follow_the_price_table():
    for row in ROWS:
        assert row["cost_usd"] == pytest.approx(
            pricing.cost_usd(row["model"], row["input_tokens"], row["output_tokens"]), abs=1e-12)
    assert round(sum(r["cost_usd"] for r in ROWS), 6) == RUN["total_cost_usd"]


def _group_passes(arm: str, group: str, field: str = "failures") -> int:
    return sum(1 for r in ROWS if r["arm"] == arm and CASES[r["case_id"]]["group"] == group
               and not r[field])


def test_the_published_counts():
    published = {"no-clause": 35, "own-meaning+exception": 52, "own-meaning": 50,
                 "words-outside": 60, "three-examples": 46, "adverb-examples": 46}
    first = {"no-clause": 32, "own-meaning+exception": 47, "own-meaning": 46,
             "words-outside": 55, "three-examples": 42, "adverb-examples": 46}
    exceptions = {"own-meaning": 29, "adverb-examples": 29}
    reported = {"no-clause": 22, "own-meaning+exception": 20, "own-meaning": 18,
                "words-outside": 22, "three-examples": 21, "adverb-examples": 33}
    for arm in phrases.ARMS:
        assert _group_passes(arm, "phrase-word") == published[arm], arm
        assert _group_passes(arm, "phrase-word", "failures_as_first_scored") == first[arm], arm
        assert _group_passes(arm, "exception") == exceptions.get(arm, 30), arm
        assert _group_passes(arm, "plain-word") == 40, arm
        words = [r for r in ROWS if r["arm"] == arm
                 and CASES[r["case_id"]]["group"] == "phrase-word"]
        assert sum(1 for r in words if r["phrase"]) == reported[arm], arm
    assert not any(r["leaked_marks"] for r in ROWS)


def test_the_two_word_adverbs_passed_once_in_120():
    adverbs = {"nuevo-de-nuevo", "completo-por-completo", "pie-de-pie", "fin-por-fin"}
    rows = [r for r in ROWS if r["case_id"] in adverbs]
    assert len(rows) == 120 and sum(r["passed"] for r in rows) == 1


def test_words_outside_per_phrase_word():
    per_case = Counter(r["case_id"] for r in ROWS if r["arm"] == "words-outside" and r["passed"])
    words = [c for c in CASES if CASES[c]["group"] == "phrase-word"]
    full = sorted(c for c in words if per_case[c] == 5)
    assert len(full) == 12
    assert sorted(c for c in words if per_case[c] == 0) == [
        "completo-por-completo", "fin-por-fin", "nuevo-de-nuevo", "pie-de-pie"]
    first = Counter(r["case_id"] for r in ROWS
                    if r["arm"] == "words-outside" and not r["failures_as_first_scored"])
    assert sorted(c for c in words if first[c] == 5) == [c for c in full if c != "hizo-hizo-caso"]


def test_replay_changes_no_verdict_and_rebuilds_the_report(tmp_path, capsys):
    copy = tmp_path / RUN_DIR.name
    shutil.copytree(RUN_DIR, copy)
    assert cli.main(["replay", str(copy)]) == 0
    printed = capsys.readouterr().out
    assert "rescored 900 rows" in printed and "changed verdict" not in printed
    assert "case file has changed" not in printed
    assert (copy / "report.md").read_bytes() == (RUN_DIR / "report.md").read_bytes()
