"""Loading and validating case files.

A case is one selection in one sentence, plus the checks its English must pass:

    id              unique name
    selection       the span a reader selected, verbatim from the sentence
    sentence        the sentence it sits in
    mustInclude     substrings that must all appear
    mustIncludeAny  substrings of which at least one must appear
    mustExclude     substrings that must not appear
    mustNotBe       a whole answer that is rejected
    note            free text (source and what the case is built to catch)
    earlier         the passage before the sentence, sent with a single-word selection as the
                    app sends it
    group           what kind of word the case tests, for experiments that compare kinds:
                    "phrase-word" (a word with its own sense inside a fixed phrase),
                    "exception" (a word with no sense outside its phrase) or "plain-word"
    amended         the record of a check changed after answers had been scored: the date, the
                    reason, and under "before" the checks as they were first written

A case needs at least one check. Validation is strict because a malformed case does not crash a
run, it silently measures something else: a selection that occurs twice may be marked at the
wrong place, and a misspelled field is a check that never runs.
"""

from __future__ import annotations

import json
from pathlib import Path

from .marks import SPAN_CLOSE, SPAN_OPEN, mark_span

REQUIRED = ("id", "selection", "sentence")
LIST_CHECKS = ("mustInclude", "mustIncludeAny", "mustExclude")
CHECKS = (*LIST_CHECKS, "mustNotBe")
KNOWN = frozenset((*REQUIRED, *CHECKS, "note", "earlier", "group", "amended"))
GROUPS = ("phrase-word", "exception", "plain-word")
AMENDED_FIELDS = frozenset(("date", "reason", "before"))


class CaseError(ValueError):
    pass


def load(path: Path) -> list[dict]:
    """The cases in `path`, validated. Raises `CaseError` naming the first bad case."""
    try:
        cases = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise CaseError(f"not valid JSON: {exc}") from exc
    if not isinstance(cases, list) or not cases:
        raise CaseError("expected a non-empty JSON list of cases")
    validate(cases)
    return cases


def validate(cases: list[dict]) -> None:
    seen: set[str] = set()
    for n, case in enumerate(cases):
        if not isinstance(case, dict):
            raise CaseError(f"entry {n} is not an object")
        cid = case.get("id", f"entry {n}")
        _validate_case(case, cid)
        if cid in seen:
            raise CaseError(f"[{cid}] duplicate id")
        seen.add(cid)


def _validate_case(case: dict, cid: str) -> None:
    for field in REQUIRED:
        value = case.get(field)
        if not isinstance(value, str) or not value:
            raise CaseError(f"[{cid}] '{field}' must be a non-empty string")
    unknown = sorted(set(case) - KNOWN)
    if unknown:
        raise CaseError(f"[{cid}] unknown field(s): {', '.join(unknown)}")
    selection, sentence = case["selection"], case["sentence"]
    if SPAN_OPEN in sentence or SPAN_CLOSE in sentence:
        raise CaseError(f"[{cid}] sentence contains « or », which are reserved as span marks")
    earlier = case.get("earlier")
    if "earlier" in case and (not isinstance(earlier, str) or not earlier):
        raise CaseError(f"[{cid}] 'earlier' must be a non-empty string")
    if earlier and (SPAN_OPEN in earlier or SPAN_CLOSE in earlier):
        raise CaseError(f"[{cid}] earlier passage contains « or », which are reserved as span marks")
    count = sentence.count(selection)
    if count != 1:
        raise CaseError(f"[{cid}] selection occurs {count} times in the sentence, not once")
    _validate_checks(case, cid)
    if "group" in case and case["group"] not in GROUPS:
        raise CaseError(f"[{cid}] 'group' must be one of {', '.join(GROUPS)}")
    if "amended" in case:
        _validate_amended(case["amended"], cid)
    mark_span(sentence, selection)


def _validate_amended(amended: object, cid: str) -> None:
    if not isinstance(amended, dict) or set(amended) != AMENDED_FIELDS:
        raise CaseError(f"[{cid}] 'amended' must hold exactly date, reason and before")
    for field in ("date", "reason"):
        if not isinstance(amended[field], str) or not amended[field]:
            raise CaseError(f"[{cid}] 'amended.{field}' must be a non-empty string")
    before = amended["before"]
    if not isinstance(before, dict) or not before or set(before) - set(CHECKS):
        raise CaseError(f"[{cid}] 'amended.before' must hold only checks")
    _validate_checks(before, f"{cid} as first written")


def checks_as_first_written(case: dict) -> dict:
    """`case` with the checks it had before any amendment."""
    if "amended" not in case:
        return case
    return {**{k: v for k, v in case.items() if k not in CHECKS}, **case["amended"]["before"]}


def _validate_checks(case: dict, cid: str) -> None:
    declared = [f for f in CHECKS if f in case]
    if not declared:
        raise CaseError(f"[{cid}] declares no checks")
    for field in LIST_CHECKS:
        if field not in case:
            continue
        value = case[field]
        if not isinstance(value, list) or not value:
            raise CaseError(f"[{cid}] '{field}' must be a non-empty list")
        if not all(isinstance(v, str) and v for v in value):
            raise CaseError(f"[{cid}] '{field}' must hold only non-empty strings")
    if "mustNotBe" in case:
        value = case["mustNotBe"]
        if not isinstance(value, str) or not value:
            raise CaseError(f"[{cid}] 'mustNotBe' must be a non-empty string")
    if "note" in case and not isinstance(case["note"], str):
        raise CaseError(f"[{cid}] 'note' must be a string")
