"""The request the app sends for one lookup: its user turn and its forced tool.

The system prompt, the two shape clauses, the earlier-passage line and the tool schema are read
from `prompt/` rather than written here, so those files are the single record of what is asked.
"""

from __future__ import annotations

import json
import re
import unicodedata
from functools import cache

from . import paths
from .marks import mark_span

MAX_TOKENS = 300
TOOL_NAME = "report_translation"
TOOL_DESCRIPTION = "Report the structured translation."

PROCLITICS = frozenset(("me", "te", "se", "nos", "os", "le", "les", "lo", "la", "los", "las"))

HABER_FORMS = frozenset((
    "he", "has", "ha", "hemos", "habéis", "han",
    "había", "habías", "habíamos", "habíais", "habían",
    "hube", "hubiste", "hubo", "hubimos", "hubisteis", "hubieron",
    "habré", "habrás", "habrá", "habremos", "habréis", "habrán",
    "habría", "habrías", "habríamos", "habríais", "habrían",
    "haya", "hayas", "hayamos", "hayáis", "hayan",
    "hubiera", "hubieras", "hubiéramos", "hubierais", "hubieran",
    "hubiese", "hubieses", "hubiésemos", "hubieseis", "hubiesen",
))

#: The second pronoun each first pronoun can take in a cluster ("se lo", "me las").
SECOND_CLITICS = {
    "se": frozenset(("lo", "la", "los", "las", "le", "les")),
    "me": frozenset(("lo", "la", "los", "las")),
    "te": frozenset(("lo", "la", "los", "las")),
    "nos": frozenset(("lo", "la", "los", "las")),
    "os": frozenset(("lo", "la", "los", "las")),
}

#: Haber as infinitive or gerund with one or two pronouns attached. The accented stems cover the
#: written accent the word takes once pronouns attach (habérselo, habiéndole); the unaccented ones
#: stay because older printings drop accents.
HABER_WITH_PRONOUN = re.compile(
    r"(haber|habér|habiendo|habiéndo)(me|te|se|nos|os|lo|la|le|los|las|les){1,2}")

#: A word is a maximal run of letters; digits, punctuation and spaces separate words.
WORD_RUN = re.compile(r"[^\W\d_]+")


@cache
def system_prompt() -> str:
    return paths.SYSTEM_PROMPT.read_text(encoding="utf-8")


@cache
def clitic_clause() -> str:
    return paths.CLITIC_TURN.read_text(encoding="utf-8")


@cache
def haber_clause() -> str:
    return paths.HABER_TURN.read_text(encoding="utf-8")


@cache
def earlier_line() -> str:
    """The earlier-passage line, with `{}` where the passage goes."""
    return paths.EARLIER_TURN.read_text(encoding="utf-8")


def tool_definition() -> dict:
    """The one tool the model is forced to call. Only `translation` is scored, but every field
    description is an instruction the model follows, so the schema is sent whole."""
    schema = json.loads(paths.TOOL_SCHEMA.read_text(encoding="utf-8"))
    return {"name": TOOL_NAME, "description": TOOL_DESCRIPTION, "input_schema": schema}


def _trim_punctuation(token: str) -> str:
    """Unicode punctuation (category P) off both ends; accents and letters untouched."""
    start, end = 0, len(token)
    while start < end and unicodedata.category(token[start]).startswith("P"):
        start += 1
    while end > start and unicodedata.category(token[end - 1]).startswith("P"):
        end -= 1
    return token[start:end]


def _clitic_tokens(surface: str) -> list[str]:
    return [t for t in (_trim_punctuation(raw).lower() for raw in surface.split()) if t]


def is_clitic_verb_candidate(surface: str) -> bool:
    """True when `surface` has the shape pronoun(s) + verb group, as in "le dio".

    A shape test, not a verdict: "la casa" passes too. It only decides whether the user turn
    carries the clitic clause, and that clause tells the model what to do when the shape is not
    a verb after all.
    """
    tokens = _clitic_tokens(surface)
    if not 2 <= len(tokens) <= 4 or tokens[0] not in PROCLITICS:
        return False
    leading = 2 if tokens[1] in SECOND_CLITICS.get(tokens[0], frozenset()) else 1
    rest = tokens[leading:]
    if not rest or rest[0] in PROCLITICS:
        return False
    if len(rest) == 1:
        return True
    if len(rest) == 2:
        return rest[0] in HABER_FORMS and rest[1] not in PROCLITICS
    return False


def is_enclitic_auxiliary(selection: str) -> bool:
    """True when `selection` is one word: haber with pronouns attached, as in "haberlo"."""
    word = unicodedata.normalize("NFC", selection).strip().lower()
    return HABER_WITH_PRONOUN.fullmatch(word) is not None


def is_single_token_lookup(selection: str) -> bool:
    """True when `selection` is at most one word, counted the way the app counts words."""
    return len(WORD_RUN.findall(selection)) <= 1


def user_turn(selection: str, sentence: str, earlier: str | None = None,
              with_haber_clause: bool = True) -> str:
    """The user turn for `selection` in `sentence`, curly quotes included.

    Its lines, in order:

    1. The instruction naming the selection.
    2. At most one shape clause. The clitic clause, for a pronoun-plus-verb span, tells the model
       to treat the span as one verb. The haber clause, for a single word made of haber and an
       attached pronoun, tells it to leave out the participle that follows. The two shapes cannot
       both hold. `with_haber_clause=False` builds the turn without the haber clause, so an
       experiment can measure what the clause adds.
    3. The sentence, as given (marked or not), unless it is just the selection again.
    4. The passage before the sentence, only for a single-word selection. A lone word often has
       too little in its own sentence to settle its sense. A multi-word span never carries one:
       the passage was measured overruling the span, when a name inside the selection came back
       as the similar name the passage used.

    The wording and order are part of the request the app sends, so tests pin them byte for byte.
    """
    turn = f"Translate this Spanish text into English: “{selection}”"
    if is_clitic_verb_candidate(selection):
        turn += "\n" + clitic_clause()
    if with_haber_clause and is_enclitic_auxiliary(selection):
        turn += "\n" + haber_clause()
    if sentence and sentence != selection:
        turn += f"\nIt appears in this sentence: “{sentence}”"
    if earlier and is_single_token_lookup(selection):
        turn += "\n" + earlier_line().format(earlier)
    return turn


def marked_turn(selection: str, sentence: str, earlier: str | None = None,
                with_haber_clause: bool = True) -> str:
    return user_turn(selection, mark_span(sentence, selection), earlier, with_haber_clause)
