from __future__ import annotations

from gloss_eval.marks import has_marks
from gloss_eval.scoring import failures


def test_must_include_passes_and_fails():
    case = {"mustInclude": ["said", "king"]}
    assert failures(case, "so great, said the king") == []
    assert failures(case, "so great") == ['missing "said"', 'missing "king"']


def test_must_include_any_needs_one_alternative():
    case = {"mustIncludeAny": ["however", "yet"]}
    assert failures(case, "however, the looks grew fixed") == []
    assert failures(case, "yet the looks grew fixed") == []
    assert failures(case, "the looks grew fixed") == ['missing any of "however" / "yet"']


def test_must_exclude_catches_an_absorbed_word():
    case = {"mustExclude": ["silver"]}
    assert failures(case, "put on an apron") == []
    assert failures(case, "put on a silver apron") == ['absorbed "silver" from outside the selection']


def test_must_not_be_is_a_whole_answer_match():
    case = {"mustNotBe": "one after another"}
    assert failures(case, "after") == []
    assert failures(case, "  One after Another ") == ['is exactly the rejected gloss "one after another"']
    assert failures(case, "one after another, again") == []


def test_matching_is_case_insensitive():
    assert failures({"mustInclude": ["Holmes"]}, "like the best, MR. HOLMES") == []
    assert failures({"mustExclude": ["blood"]}, "Cold-Blooded") != []


def test_a_substring_matches_inside_a_longer_word():
    assert failures({"mustInclude": ["horse"]}, "fear of scaring the horses") == []
    assert failures({"mustExclude": ["red"]}, "we were bored") != []


def test_a_pinned_space_stops_the_collision():
    case = {"mustExclude": [" red"]}
    assert failures(case, "we were bored") == []
    assert failures(case, "a red coat") != []


def test_no_accent_folding():
    assert failures({"mustInclude": ["café"]}, "cafe") == ['missing "café"']


def test_marks_are_stripped_before_scoring():
    case = {"mustNotBe": "cold"}
    assert failures(case, "«cold»") == ['is exactly the rejected gloss "cold"']
    assert failures({"mustInclude": ["cold-"]}, "«cold»-blooded") == []


def test_leaked_marks_are_detected_on_the_raw_answer():
    assert has_marks("«cold»")
    assert has_marks("cold»")
    assert not has_marks("cold")
