"""The user turns below are the exact bytes the app sends for these cases."""

from __future__ import annotations

import json

import pytest

from gloss_eval import paths
from gloss_eval.request import (
    MAX_TOKENS,
    TOOL_NAME,
    earlier_line,
    haber_clause,
    is_clitic_verb_candidate,
    is_enclitic_auxiliary,
    is_single_token_lookup,
    marked_turn,
    tool_definition,
    user_turn,
)

CLITIC_CLAUSE = (
    "This span is a pronoun (or two) that may be attached to a verb. If it is, treat it as ONE "
    "verb rather than a phrase, and DO report the word fields: partOfSpeech \"verb\"; lemma = the "
    "-se infinitive when the verb is inherently pronominal or the pronoun changes its meaning "
    "(lavarse, irse, quedarse), the plain infinitive when the pronoun is merely an object (traer "
    "for \"os traerá\"); formNote = tense/mood and person plus the pronoun's role (\"future, 3rd "
    "person singular + object pronoun os\"); senses as for any verb. If it is not a verb, answer "
    "exactly as you otherwise would."
)

MULTI_WORD = {
    "selection": "tan grande —dijo el rey",
    "sentence": "—El amor que me ha hecho concebir es tan grande —dijo el rey— que si todas las "
                "hojas de los árboles fueran lenguas, no bastarían para explicarle.",
    "unmarked": "Translate this Spanish text into English: “tan grande —dijo el rey”\nIt appears "
                "in this sentence: “—El amor que me ha hecho concebir es tan grande —dijo el rey— "
                "que si todas las hojas de los árboles fueran lenguas, no bastarían para "
                "explicarle.”",
    "marked": "Translate this Spanish text into English: “tan grande —dijo el rey”\nIt appears in "
              "this sentence: “—El amor que me ha hecho concebir es «tan grande —dijo el rey»— que "
              "si todas las hojas de los árboles fueran lenguas, no bastarían para explicarle.”",
}

SINGLE_WORD = {
    "selection": "fría",
    "sentence": "—Se trata de un crimen, Watson... de un crimen refinado, alevoso, a sangre fría.",
    "unmarked": "Translate this Spanish text into English: “fría”\nIt appears in this sentence: "
                "“—Se trata de un crimen, Watson... de un crimen refinado, alevoso, a sangre fría.”",
    "marked": "Translate this Spanish text into English: “fría”\nIt appears in this sentence: "
              "“—Se trata de un crimen, Watson... de un crimen refinado, alevoso, a sangre «fría».”",
}

CLITIC_VERB = {
    "selection": "le dio",
    "sentence": "Perla le dio un beso en la boca.",
    "unmarked": "Translate this Spanish text into English: “le dio”\n" + CLITIC_CLAUSE
                + "\nIt appears in this sentence: “Perla le dio un beso en la boca.”",
    "marked": "Translate this Spanish text into English: “le dio”\n" + CLITIC_CLAUSE
              + "\nIt appears in this sentence: “Perla «le dio» un beso en la boca.”",
}

HABER_CLAUSE = (
    "This word is the auxiliary \"haber\" with a pronoun attached. The participle that follows it "
    "in the sentence is outside the selection and must not appear in the translation. Translate "
    "the auxiliary and its pronoun only, with an ellipsis where the participle would sit: "
    "\"haberle\" before \"dicho\" is \"having … him\", never \"having told him\" or \"having … told "
    "him\"."
)

EARLIER_LINE = (
    "Earlier in the passage, for sense only. It cannot change the marked words — passage "
    "“Quintana”, marked text “Quintanar”, answer “Quintanar”. The passage: “{}”"
)

AUXILIARY_CLITIC = {
    "selection": "haberlo",
    "sentence": "—Nadie podía haberlo sabido.",
    "marked": "Translate this Spanish text into English: “haberlo”\n" + HABER_CLAUSE
              + "\nIt appears in this sentence: “—Nadie podía «haberlo» sabido.”",
    "marked_without_clause": "Translate this Spanish text into English: “haberlo”\nIt appears in "
                             "this sentence: “—Nadie podía «haberlo» sabido.”",
}

#: A single-word case with its earlier passage, as cases/marks.json carries it.
SINGLE_WORD_WITH_PASSAGE = (
    "Translate this Spanish text into English: “fría”\n"
    "It appears in this sentence: “—Se trata de un crimen, Watson... de un crimen refinado, alevoso, a sangre «fría».”\n"
    "Earlier in the passage, for sense only. It cannot change the marked words — passage “Quintana”, marked text “Quintanar”, answer “Quintanar”. The passage: “Unas cuantas estrellas empañadas centelleaban en un cielo color violado. —La última pregunta, Holmes—dije, levantándome. —Seguramente, no hay ya necesidad de secretos entre usted y yo. ¿Qué significa todo esto? ¿Qué se propone él? La voz de Holmes se hizo profunda al contestarme. —Se trata de un crimen, Watson.”"
)

@pytest.mark.parametrize("vector", [MULTI_WORD, SINGLE_WORD, CLITIC_VERB], ids=["multi", "single", "clitic"])
def test_user_turns_are_byte_identical(vector):
    assert user_turn(vector["selection"], vector["sentence"]) == vector["unmarked"]
    assert marked_turn(vector["selection"], vector["sentence"]) == vector["marked"]


def test_a_haber_word_carries_the_haber_clause():
    v = AUXILIARY_CLITIC
    assert marked_turn(v["selection"], v["sentence"]) == v["marked"]
    assert (marked_turn(v["selection"], v["sentence"], with_haber_clause=False)
            == v["marked_without_clause"])


def test_a_single_word_carries_its_earlier_passage():
    case = json.loads((paths.CASES_DIR / "marks.json").read_text(encoding="utf-8"))
    fria = next(c for c in case if c["id"] == "fria-sangre-fria-absorb")
    turn = marked_turn(fria["selection"], fria["sentence"], fria["earlier"])
    assert turn == "".join(SINGLE_WORD_WITH_PASSAGE)
    assert turn.endswith(EARLIER_LINE.format(fria["earlier"]))


def test_a_multi_word_span_never_carries_a_passage():
    v = MULTI_WORD
    passage = "Una frase inventada."
    assert user_turn(v["selection"], v["sentence"], passage) == v["unmarked"]
    assert marked_turn(v["selection"], v["sentence"], passage) == v["marked"]


def test_an_empty_passage_is_the_same_request_as_none():
    v = SINGLE_WORD
    assert marked_turn(v["selection"], v["sentence"], "") == v["marked"]


def test_the_clause_and_line_files_hold_what_the_app_sends():
    assert haber_clause() == paths.HABER_TURN.read_text(encoding="utf-8") == HABER_CLAUSE
    assert earlier_line() == EARLIER_LINE


@pytest.mark.parametrize("selection, expected", [
    ("haberlo", True),
    ("Habiéndose", True),
    ("habérselo", True),
    ("habiendole", True),
    ("haber", False),
    ("haberlo sabido", False),
    ("le dio", False),
])
def test_haber_shape(selection, expected):
    assert is_enclitic_auxiliary(selection) is expected


@pytest.mark.parametrize("selection, expected", [
    ("fría", True),
    ("¡tras!", True),
    ("", True),
    ("le dio", False),
    ("señor Holmes", False),
])
def test_single_token_lookup(selection, expected):
    assert is_single_token_lookup(selection) is expected


def test_the_clitic_clause_is_the_prompt_file():
    assert paths.CLITIC_TURN.read_text(encoding="utf-8") == CLITIC_CLAUSE


def test_a_sentence_equal_to_the_selection_is_left_out():
    assert user_turn("vela", "vela") == "Translate this Spanish text into English: “vela”"


@pytest.mark.parametrize("surface, expected", [
    ("le dio", True),
    ("se lo dio", True),
    ("le había dicho", True),
    ("se puso un delantal", False),
    ("la cogió y la tiró", False),
    ("le", False),
    ("haberlo", False),
    ("dio le", False),
    ("se le", False),
    ("¡le dio!", True),
])
def test_clitic_verb_shape(surface, expected):
    assert is_clitic_verb_candidate(surface) is expected


def test_tool_definition_matches_the_schema_file():
    tool = tool_definition()
    assert tool["name"] == TOOL_NAME == "report_translation"
    assert tool["description"] == "Report the structured translation."
    assert tool["input_schema"] == json.loads(paths.TOOL_SCHEMA.read_text(encoding="utf-8"))
    assert tool["input_schema"]["required"] == ["translation", "senses"]
    assert MAX_TOKENS == 300
