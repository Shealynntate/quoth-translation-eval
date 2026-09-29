"""Six requests that differ only in one clause, sent when the selection is a single plain word.

The failure: a tap on one word inside a fixed phrase comes back with the phrase's meaning.
"fría" in "a sangre fría" answers "cold blood" where the word alone means "cold". The arms:

    no-clause               the request as experiments 1 and 2 sent it, with no clause
    own-meaning+exception   translate the word alone, one worked example, and the exception
                            for a word that means nothing outside its phrase
    own-meaning             the above without the exception
    words-outside           the neighbouring words are outside the selection, one worked example
                            (the clause the app sends from version 1.0.1)
    three-examples          own-meaning with two more worked examples, a noun and a verb
    adverb-examples         words-outside with examples of a preposition and one word that make
                            an adverb, the exception, and a demand that the phrase be reported

Each clause is the second line of the user turn, and only when `request.is_plain_single_word`
passes: one word, and neither haber with a pronoun attached nor a pronoun-plus-verb span, which
carry their own clauses. Every other request is byte for byte the one `no-clause` sends. The
system prompt is prompt/system.txt in every arm, and every arm sends the sentence marked and the
earlier passage.

The texts are read from prompt/phrase_clauses/, one file per arm, so each file is exactly what
that arm sent.
"""

from __future__ import annotations

import unicodedata
from functools import cache

from . import paths

ARMS = ("no-clause", "own-meaning+exception", "own-meaning", "words-outside", "three-examples",
        "adverb-examples")

#: Public arm name -> the name the app's private harness gave it. This is the one place the two
#: sets of names meet; the recorded run.json carries the same table.
PRIVATE_NAMES = {
    "no-clause": "control-u1",
    "own-meaning+exception": "w1",
    "own-meaning": "w2",
    "words-outside": "w3",
    "three-examples": "w4",
    "adverb-examples": "w5",
}

#: The round each arm was measured in. The second round was designed after the first round's
#: answers had been read.
ROUNDS = {
    1: ("no-clause", "own-meaning+exception", "own-meaning", "words-outside", "three-examples"),
    2: ("adverb-examples",),
}

#: The arm whose clause the app ships, as prompt/single_word_turn.txt.
SHIPPED_ARM = "words-outside"

#: Arm -> (the words its clause glosses, the phrases it names). A case whose selection is one of
#: those words, or whose sentence holds one of those phrases, would be scored against an answer
#: its own request handed the model, so `refuse_example_cases` stops the run before anything is
#: sent.
CLAUSE_EXAMPLES: dict[str, tuple[tuple[str, ...], tuple[str, ...]]] = {
    "no-clause": ((), ()),
    "own-meaning+exception": (("larga", "balde"), ("a la larga", "en balde")),
    "own-meaning": (("larga",), ("a la larga",)),
    "words-outside": (("larga",), ("a la larga",)),
    "three-examples": (("larga", "pelo", "metió"), ("a la larga", "tomó el pelo", "metió la pata")),
    "adverb-examples": (("larga", "prisa", "último", "balde"),
                        ("a la larga", "de prisa", "por último", "en balde")),
}


class ExampleInCase(ValueError):
    pass


@cache
def clause(arm: str) -> str | None:
    """The clause `arm` adds to a single-word user turn, or None for `no-clause`."""
    if arm not in ARMS:
        raise ValueError(f"unknown arm {arm!r}; use one of {', '.join(ARMS)}")
    if arm == "no-clause":
        return None
    return (paths.PHRASE_CLAUSES_DIR / f"{arm}.txt").read_text(encoding="utf-8")


def _folded(text: str) -> str:
    return unicodedata.normalize("NFC", text).strip().lower()


def example_in_case(case: dict, arm: str) -> str | None:
    """The first of `arm`'s worked examples that `case` repeats, or None."""
    words, phrases = CLAUSE_EXAMPLES[arm]
    selection, sentence = _folded(case["selection"]), _folded(case["sentence"])
    return (next((w for w in words if selection == w), None)
            or next((p for p in phrases if p in sentence), None))


def refuse_example_cases(cases: list[dict], arms: tuple[str, ...] = ARMS) -> None:
    """Raise, before anything is sent, if a case would be scored against its arm's own example."""
    for arm in arms:
        for case in cases:
            hit = example_in_case(case, arm)
            if hit:
                raise ExampleInCase(
                    f"case {case['id']!r} contains {hit!r}, an example the {arm} clause gives the "
                    "answer to; it would measure copying, not the clause")
