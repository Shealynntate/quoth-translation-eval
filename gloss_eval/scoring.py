"""Pass or fail for one answer, by plain substring checks. No model judges anything.

Matching is case-insensitive `in` on the `translation` field, with no accent folding and no
word boundaries. Substrings are what let a stem cover its inflections ("disobey" catches
"disobeyed"), and they are also the known weakness: a check can collide with a word it sits
inside ("red" inside "bored", "so" inside "sorry"). The case files pin such checks with a space
or punctuation ("so ", "so,", "old ") instead of switching to word boundaries, which would break
the stems.

Span marks are stripped before scoring, because the checks judge the English, and a leaked mark
is reported on its own (see `marks.has_marks`).
"""

from __future__ import annotations

from .marks import strip_marks


def failures(case: dict, translation: str) -> list[str]:
    """Every check `translation` fails, as readable sentences. Empty means the case passed."""
    text = strip_marks(translation).strip()
    low = text.lower()
    out: list[str] = []
    for needle in case.get("mustInclude", []):
        if needle.lower() not in low:
            out.append(f'missing "{needle}"')
    any_of = case.get("mustIncludeAny", [])
    if any_of and not any(n.lower() in low for n in any_of):
        out.append("missing any of " + " / ".join(f'"{n}"' for n in any_of))
    for needle in case.get("mustExclude", []):
        if needle.lower() in low:
            out.append(f'absorbed "{needle}" from outside the selection')
    rejected = case.get("mustNotBe")
    if rejected is not None and low == rejected.strip().lower():
        out.append(f'is exactly the rejected gloss "{rejected}"')
    return out
