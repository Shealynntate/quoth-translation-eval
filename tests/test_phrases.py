"""The six phrases arms: their clauses, their gate, the example guard, and a run through them."""

from __future__ import annotations

import json

import pytest

from gloss_eval import __main__ as cli
from gloss_eval import paths, phrases, runner
from gloss_eval.cases import CaseError, checks_as_first_written, load, validate
from gloss_eval.ledger import SpendLedger
from gloss_eval.request import (
    haber_clause,
    is_plain_single_word,
    marked_turn,
    single_word_clause,
    system_prompt,
    word_count,
)

HAIKU = "claude-haiku-4-5-20251001"

#: Each clause exactly as the app's harness sent it.
CLAUSES = {
    "own-meaning+exception": (
        "This selection is a single word. Translate that word alone, in the sense it has in this "
        "sentence. If it is part of a fixed phrase, report the phrase in the expression fields and "
        "keep the translation to the word's own meaning: \"larga\" in \"a la larga\" is \"long\", "
        "never \"in the long run\". The exception is a word that has no meaning of its own outside "
        "its phrase, like \"balde\" in \"en balde\": its translation is the phrase's meaning."
    ),
    "own-meaning": (
        "This selection is a single word. Translate that word alone, in the sense it has in this "
        "sentence. If it is part of a fixed phrase, report the phrase in the expression fields and "
        "keep the translation to the word's own meaning: \"larga\" in \"a la larga\" is \"long\", "
        "never \"in the long run\"."
    ),
    "words-outside": (
        "This selection is a single word. The words around it are outside the selection and must "
        "not appear in the translation, even when they form a fixed phrase with it. Translate the "
        "word itself and report the phrase separately in the expression fields: \"larga\" in \"a "
        "la larga\" is \"long\", never \"in the long run\" or \"the long run\"."
    ),
    "three-examples": (
        "This selection is a single word. Translate that word alone, in the sense it has in this "
        "sentence. If it is part of a fixed phrase, report the phrase in the expression fields and "
        "keep the translation to the word's own meaning: \"larga\" in \"a la larga\" is \"long\", "
        "never \"in the long run\"; \"pelo\" in \"le tomó el pelo\" is \"hair\", never \"teased\"; "
        "\"metió\" in \"metió la pata\" is \"put\", never \"blundered\"."
    ),
    "adverb-examples": (
        "This selection is a single word. The words around it are outside the selection and must "
        "not appear in the translation, even when they form a fixed phrase with it. Translate the "
        "word itself: \"larga\" in \"a la larga\" is \"long\", never \"in the long run\". A short "
        "phrase that works as an adverb is no different: \"prisa\" in \"de prisa\" is \"haste\", "
        "never \"quickly\", and \"último\" in \"por último\" is \"last\", never \"finally\". The "
        "one exception is a word whose own meaning has nothing to do with its phrase's, like "
        "\"balde\" in \"en balde\": its translation is the phrase's meaning. Whenever the word is "
        "part of a fixed phrase, the expression fields must carry that phrase and its meaning."
    ),
}

PHRASE_CASES = load(paths.CASES_DIR / "phrases.json")
FRIA = next(c for c in PHRASE_CASES if c["id"] == "fria-a-sangre-fria")


def test_the_arms_and_their_private_names():
    assert phrases.ARMS == ("no-clause", "own-meaning+exception", "own-meaning", "words-outside",
                            "three-examples", "adverb-examples")
    assert tuple(phrases.PRIVATE_NAMES) == phrases.ARMS
    assert tuple(phrases.CLAUSE_EXAMPLES) == phrases.ARMS
    assert sum(phrases.ROUNDS.values(), ()) == phrases.ARMS


def test_each_clause_file_is_the_text_sent():
    assert phrases.clause("no-clause") is None
    for arm, text in CLAUSES.items():
        assert phrases.clause(arm) == text
        raw = (paths.PHRASE_CLAUSES_DIR / f"{arm}.txt").read_bytes()
        assert raw == text.encode("utf-8") and not raw.endswith(b"\n")
    assert sorted(p.stem for p in paths.PHRASE_CLAUSES_DIR.glob("*.txt")) == sorted(CLAUSES)


def test_the_shipped_clause_is_words_outside():
    assert single_word_clause() == phrases.clause(phrases.SHIPPED_ARM) == CLAUSES["words-outside"]


def test_each_clause_names_the_examples_the_guard_holds():
    for arm, (words, examples) in phrases.CLAUSE_EXAMPLES.items():
        text = phrases.clause(arm) or ""
        for word in words:
            assert f'"{word}"' in text, (arm, word)
        for phrase in examples:
            assert phrase in text, (arm, phrase)


def test_an_unknown_arm_is_refused():
    with pytest.raises(ValueError):
        phrases.clause("w3")


@pytest.mark.parametrize("selection, count", [
    ("fría", 1), ("fría", 1), ("¡tras!", 1), ("señor Holmes", 2), ("1920", 0), ("½", 0),
    ("", 0), ("a sangre fría", 3),
])
def test_word_count(selection, count):
    assert word_count(selection) == count


@pytest.mark.parametrize("selection, expected", [
    ("fría", True), ("Sin", True), ("fría", True), ("haberlo", False), ("le dio", False),
    ("a sangre", False), ("", False), ("—", False),
])
def test_the_gate_is_one_plain_word(selection, expected):
    assert is_plain_single_word(selection) is expected


def test_every_published_case_passes_the_gate():
    assert all(is_plain_single_word(c["selection"]) for c in PHRASE_CASES)


def test_the_clause_is_the_second_line_of_the_turn():
    for arm in phrases.ARMS:
        turn = runner.arm_turn("phrases", arm, FRIA)
        lines = turn.split("\n")
        assert lines[0] == "Translate this Spanish text into English: “fría”"
        if arm == "no-clause":
            assert lines[1].startswith("It appears in this sentence: ")
        else:
            assert lines[1] == CLAUSES[arm]
        assert "sangre «fría»" in lines[-2] and lines[-1].startswith("Earlier in the passage")
        assert len(lines) == (3 if arm == "no-clause" else 4)


def test_no_clause_is_the_turn_experiments_one_and_two_sent():
    for case in PHRASE_CASES:
        assert (runner.arm_turn("phrases", "no-clause", case)
                == runner.arm_turn("marks", "marked", case))


def test_other_shapes_keep_their_own_clause_and_never_get_a_second():
    haber = load(paths.CASES_DIR / "haber.json")[0]
    for arm in phrases.ARMS:
        turn = runner.arm_turn("phrases", arm, haber)
        assert turn == runner.arm_turn("marks", "marked", haber)
        assert haber_clause() in turn
    multi = "se puso un delantal"
    sentence = "Limpióse el rostro; se puso un delantal de plata."
    for arm in phrases.ARMS:
        assert (marked_turn(multi, sentence, single_word=phrases.clause(arm))
                == marked_turn(multi, sentence))


def test_every_arm_sends_the_shipped_system_prompt():
    assert set(runner.system_prompts("phrases").values()) == {system_prompt()}


def test_the_guard_refuses_a_case_that_repeats_an_example():
    larga = {"id": "larga", "selection": "larga", "sentence": "Lo supo a la larga.",
             "mustIncludeAny": ["long"]}
    prisa = {"id": "prisa-case", "selection": "vino", "sentence": "Vino de prisa.",
             "mustIncludeAny": ["came"]}
    with pytest.raises(phrases.ExampleInCase, match="'larga'"):
        phrases.refuse_example_cases([larga])
    phrases.refuse_example_cases([larga], ("no-clause",))
    with pytest.raises(phrases.ExampleInCase, match="adverb-examples"):
        phrases.refuse_example_cases([prisa])
    phrases.refuse_example_cases([prisa], phrases.ARMS[:-1])
    capitalised = {**larga, "selection": "Larga", "sentence": "Lo supo A LA LARGA."}
    assert phrases.example_in_case(capitalised, "own-meaning") == "larga"


def test_the_guard_stops_a_run_before_anything_is_sent(tmp_path, fake_client, capsys):
    cases = [{"id": "larga", "selection": "larga", "sentence": "Lo supo a la larga.",
              "mustIncludeAny": ["long"]}]
    path = tmp_path / "cases.json"
    path.write_text(json.dumps(cases), encoding="utf-8")
    with pytest.raises(phrases.ExampleInCase):
        runner.plan("phrases", cases, HAIKU, 1)
    code = cli.main(["phrases", "--cases", str(path), "--model", "haiku", "--trials", "1",
                     "--dry-run"])
    assert code == 1 and "an example the" in capsys.readouterr().err


def test_the_published_cases_pass_the_guard():
    phrases.refuse_example_cases(PHRASE_CASES)


def test_the_phrases_case_file():
    groups = [c["group"] for c in PHRASE_CASES]
    assert len(PHRASE_CASES) == 30
    assert (groups.count("phrase-word"), groups.count("exception"),
            groups.count("plain-word")) == (16, 6, 8)
    assert all("earlier" in c for c in PHRASE_CASES)
    amended = [c for c in PHRASE_CASES if "amended" in c]
    assert [c["id"] for c in amended] == ["hizo-hizo-caso"]


def test_the_amended_check_and_its_first_form():
    hizo = next(c for c in PHRASE_CASES if c["id"] == "hizo-hizo-caso")
    first = checks_as_first_written(hizo)
    assert hizo["mustIncludeAny"] == ["made", "did", "make", "paid", "pay"]
    assert first["mustIncludeAny"] == ["made", "did", "make"]
    assert first["mustExclude"] == hizo["mustExclude"] + ["paid", "pay"]
    assert {k: v for k, v in first.items() if not k.startswith("must")} == {
        k: v for k, v in hizo.items() if not k.startswith("must")}


@pytest.mark.parametrize("change, message", [
    ({"group": "other"}, "'group' must be one of"),
    ({"amended": {"date": "2026-01-01", "reason": "x"}}, "exactly date, reason and before"),
    ({"amended": {"date": "", "reason": "x", "before": {"mustInclude": ["cat"]}}},
     "'amended.date' must be a non-empty string"),
    ({"amended": {"date": "d", "reason": "x", "before": {"note": "n"}}},
     "'amended.before' must hold only checks"),
    ({"amended": {"date": "d", "reason": "x", "before": {"mustInclude": []}}},
     "'mustInclude' must be a non-empty list"),
])
def test_bad_group_or_amendment_is_rejected(change, message):
    case = {"id": "invented", "selection": "gato", "sentence": "El gato duerme.",
            "mustInclude": ["cat"], **change}
    with pytest.raises(CaseError) as err:
        validate([case])
    assert message in str(err.value)


def test_a_phrases_run_records_the_reported_phrase(tmp_path, fake_client):
    def answer(system, user):
        if "«fría»" in user:
            return {"translation": "cold", "expression": "A sangre fría",
                    "expressionMeaning": "in cold blood", "senses": []}
        return {"translation": "an answer", "expression": " ", "senses": []}

    path = paths.CASES_DIR / "phrases.json"
    client = fake_client(answer=answer)
    run_info, rows = runner.execute("phrases", path, PHRASE_CASES, HAIKU, 1, SpendLedger(5.0), 4,
                                    tmp_path, client, "test")
    assert len(rows) == len(client.calls) == 30 * 6
    fria = [r for r in rows if r["case_id"] == "fria-a-sangre-fria"]
    assert all(r["phrase"] == "A sangre fría" and r["phrase_meaning"] == "in cold blood"
               and r["passed"] for r in fria)
    others = [r for r in rows if r["case_id"] != "fria-a-sangre-fria"]
    assert all(r["phrase"] is None and r["phrase_meaning"] is None for r in others)
    report = (tmp_path / "report.md").read_text(encoding="utf-8")
    assert "## By group" in report
    assert "| words-outside | 1/16 | 0/6 | 0/8 | 1/16 |" in report
    assert run_info["prompt_sha256"] == {
        arm: runner.sha256_text(system_prompt()) for arm in phrases.ARMS}


def test_a_phrases_dry_run_sends_nothing(tmp_path, monkeypatch, capsys):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.setattr(paths, "ENV_FILE", tmp_path / "absent.env")
    code = cli.main(["phrases", "--cases", str(paths.CASES_DIR / "phrases.json"), "--model",
                     "haiku", "--trials", "5", "--dry-run", "--out", str(tmp_path / "out")])
    out = capsys.readouterr().out
    assert code == 0
    assert "30 cases x 6 arms x 5 trials = 900 requests" in out
    assert out.count("first request of arm ") == 6
    assert out.count("This selection is a single word.") == 5
    assert "$4.2300" in out and "dry run: nothing sent" in out
    assert not (tmp_path / "out").exists()
