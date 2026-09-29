from __future__ import annotations

import json

import pytest

from gloss_eval import paths
from gloss_eval.cases import CaseError, load, validate

GOOD = {"id": "invented", "selection": "gato", "sentence": "El gato duerme.",
        "mustInclude": ["cat"]}


def _with(**changes) -> dict:
    case = {**GOOD, **changes}
    return {k: v for k, v in case.items() if v is not None}


@pytest.mark.parametrize("name, count", [("marks.json", 19), ("haber.json", 16)])
def test_the_shipped_case_files_validate(name, count):
    assert len(load(paths.CASES_DIR / name)) == count


def test_a_good_case_validates():
    validate([GOOD, _with(id="with-passage", earlier="Un perro ladra.")])


def test_only_single_word_cases_carry_a_passage():
    for name in ("marks.json", "haber.json"):
        for case in load(paths.CASES_DIR / name):
            single = len(case["selection"].split()) == 1
            assert ("earlier" in case) == single, case["id"]


@pytest.mark.parametrize("case, message", [
    (_with(selection=None), "'selection' must be a non-empty string"),
    (_with(sentence=""), "'sentence' must be a non-empty string"),
    (_with(selection="perro"), "occurs 0 times"),
    (_with(sentence="El gato ve al gato."), "occurs 2 times"),
    (_with(sentence="El «gato» duerme."), "reserved as span marks"),
    (_with(mustInclude=None), "declares no checks"),
    (_with(mustInclude=[]), "'mustInclude' must be a non-empty list"),
    (_with(mustExclude="dog"), "'mustExclude' must be a non-empty list"),
    (_with(mustIncludeAny=["cat", ""]), "only non-empty strings"),
    (_with(mustNotBe=""), "'mustNotBe' must be a non-empty string"),
    (_with(expectExpression="el gato"), "unknown field(s): expectExpression"),
    (_with(earlier=""), "'earlier' must be a non-empty string"),
    (_with(earlier=["Un perro."]), "'earlier' must be a non-empty string"),
    (_with(earlier="Un «perro» ladra."), "earlier passage contains « or »"),
])
def test_each_rule_rejects_a_bad_case(case, message):
    with pytest.raises(CaseError) as err:
        validate([case])
    assert message in str(err.value)
    assert f"[{case.get('id')}]" in str(err.value)


def test_duplicate_ids_are_rejected():
    with pytest.raises(CaseError, match=r"\[invented\] duplicate id"):
        validate([GOOD, dict(GOOD)])


def test_a_file_that_is_not_a_list_is_rejected(tmp_path):
    path = tmp_path / "cases.json"
    path.write_text(json.dumps(GOOD), encoding="utf-8")
    with pytest.raises(CaseError, match="non-empty JSON list"):
        load(path)
