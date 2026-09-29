"""The « » span marks: placing them in a sentence, and finding them in an answer.

The marks tell the model where the selection sits, so it does not have to locate the span
itself. Case validation refuses any sentence that already contains « or », which is what makes a
mark in an answer provably a leak rather than quoted text.
"""

from __future__ import annotations

SPAN_OPEN = "«"
SPAN_CLOSE = "»"


def boundary_starts(sentence: str, selection: str) -> list[int]:
    """Start indices where `selection` sits on token boundaries in `sentence`.

    A plain `str.find` is wrong for short selections. In "se puso un delantal de plata y dio
    comienzo a su tarea", the first "a" is the last letter of "delantal"; marking it there would
    ask about a letter instead of the preposition before "su tarea".
    """
    starts, start = [], 0
    while True:
        i = sentence.find(selection, start)
        if i < 0:
            return starts
        end = i + len(selection)
        before_ok = i == 0 or not sentence[i - 1].isalnum()
        after_ok = end == len(sentence) or not sentence[end].isalnum()
        if before_ok and after_ok:
            starts.append(i)
        start = i + 1


def mark_span(sentence: str, selection: str) -> str:
    """`sentence` with the first token-aligned occurrence of `selection` wrapped in « ».

    When no occurrence is token-aligned, the first raw occurrence is marked instead. That happens
    for a selection that opens on a dialogue dash glued to the previous word, as in the case
    `baronet-tono-resuelto-tag`, where the dash follows a letter.
    """
    starts = boundary_starts(sentence, selection)
    if starts:
        i = starts[0]
    else:
        i = sentence.find(selection)
        if i < 0:
            raise ValueError(f"selection not found in sentence: {selection!r}")
    end = i + len(selection)
    return sentence[:i] + SPAN_OPEN + selection + SPAN_CLOSE + sentence[end:]


def strip_marks(text: str) -> str:
    """`text` with every « and » removed."""
    return "".join(ch for ch in text if ch not in (SPAN_OPEN, SPAN_CLOSE))


def has_marks(text: str) -> bool:
    """True when `text` carries a « or ».

    In an answer this is a leak the substring checks cannot see: the English can pass every
    check and still be unusable as shown.
    """
    return SPAN_OPEN in text or SPAN_CLOSE in text
