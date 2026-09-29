from __future__ import annotations

import json

import pytest

from gloss_eval import paths
from gloss_eval.marks import boundary_starts, has_marks, mark_span, strip_marks


def _case(file: str, case_id: str) -> dict:
    cases = json.loads((paths.CASES_DIR / file).read_text(encoding="utf-8"))
    return next(c for c in cases if c["id"] == case_id)


@pytest.mark.parametrize("file, case_id, expected", [
    ("marks.json", "rey-tan-grande-speech-tag",
     "—El amor que me ha hecho concebir es «tan grande —dijo el rey»— que si todas las hojas de "
     "los árboles fueran lenguas, no bastarían para explicarle."),
    ("marks.json", "caperucita-dijo-el-lobo",
     "—Soy vuestra nieta, «Caperucita roja, dijo el lobo» imitando la voz de la niña."),
    ("marks.json", "baronet-tono-resuelto-tag",
     "—Ahora, caballeros«—dijo el baronet en tono resuelto»,—creo que he hablado bastante sobre "
     "lo poco que sé."),
    ("marks.json", "fria-sangre-fria-absorb",
     "—Se trata de un crimen, Watson... de un crimen refinado, alevoso, a sangre «fría»."),
    ("marks.json", "tras-uno-tras-otro-particle", "Y los volvió a colgar uno «tras» otro."),
    ("marks.json", "le-dio-absorb-beso", "Perla «le dio» un beso en la boca."),
    ("marks.json", "marido-se-vistio-subject",
     "«El marido se vistió rápidamente y echó a correr», como un insensato."),
    ("haber.json", "haberlo-sabido", "—Nadie podía «haberlo» sabido."),
])
def test_marks_real_cases(file, case_id, expected):
    case = _case(file, case_id)
    assert mark_span(case["sentence"], case["selection"]) == expected


def test_a_short_selection_is_not_marked_inside_a_word():
    sentence = _case("marks.json", "delantal-absorb-plata")["sentence"]
    assert sentence[sentence.find("a") - 1:sentence.find("a") + 2] == "las"
    assert boundary_starts(sentence, "a") == [88]
    assert mark_span(sentence, "a").endswith("dio comienzo «a» su tarea.")


def test_a_selection_opening_on_a_glued_dash_falls_back_to_the_raw_match():
    case = _case("marks.json", "baronet-tono-resuelto-tag")
    assert boundary_starts(case["sentence"], case["selection"]) == []
    assert "«—dijo" in mark_span(case["sentence"], case["selection"])


def test_selection_not_found_raises():
    with pytest.raises(ValueError, match="not found"):
        mark_span("Y los volvió a colgar.", "tras")


def test_strip_marks_restores_the_sentence():
    case = _case("marks.json", "rey-tan-grande-speech-tag")
    marked = mark_span(case["sentence"], case["selection"])
    assert strip_marks(marked) == case["sentence"]
    assert has_marks(marked) and not has_marks(strip_marks(marked))
