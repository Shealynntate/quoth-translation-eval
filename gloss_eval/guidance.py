"""Five requests that differ only in how they guide a pronoun attached to an auxiliary.

The failure: in "Nadie podía haberlo sabido", the selection "haberlo" is haber plus a pronoun,
and the participle "sabido" is outside it. The model tends to gloss "having known it", pulling
the participle in. The arms climb a ladder of guidance, one rung each:

    no-guidance      the system prompt with its two clitic sentences removed
    rule             the clitic rule sentence alone
    rule+example     the rule plus one worked example (prompt/system.txt as it is)
    second-example   the above plus a second worked example
    turn-clause      prompt/system.txt, plus a clause in the user turn that is sent only when
                     the selection is haber with a pronoun attached, so no other lookup changes

The first four arms send the user turn without that clause; `turn-clause` sends it as the app
does. Every arm sends the sentence marked and, for a single word, the earlier passage.

The system prompts are built from prompt/system.txt by exact-string surgery. Each sentence is
located by exact match, and if one has been reworded, building fails with a drift error rather
than quietly measuring prompts that no longer differ the way their names say.
"""

from __future__ import annotations

ARMS = ("no-guidance", "rule", "rule+example", "second-example", "turn-clause")

#: Arms whose user turn carries the haber clause.
HABER_CLAUSE_ARMS = frozenset(("turn-clause",))

#: The sentence the clitic guidance follows. Inserting after it is how `rule+example` is rebuilt
#: from `no-guidance`, which proves the removal took out exactly what the insertion puts back.
ANCHOR = "Never absorb meaning from outside the span — no tense, subject, or verb that follows."

RULE = (
    "When the selected span is, or ends with, a verb carrying an attached clitic pronoun, the "
    "pronoun is part of the span but the verb it anticipates is not — gloss only that verb and "
    "its pronoun, showing any gap with an ellipsis."
)

EXAMPLE = 'So «haberla» standing before a participle is "having … it", never "having discovered it".'

SECOND_EXAMPLE = (
    'Likewise «haberle» is "having … him", never "having … told him": the participle stays out '
    "of the gloss, with the ellipsis or without it."
)


class PromptDrift(ValueError):
    pass


def _require_once(prompt: str, sentence: str, what: str) -> None:
    count = prompt.count(sentence)
    if count != 1:
        raise PromptDrift(
            f"prompt/system.txt has drifted: the {what} occurs {count} times, expected once:\n"
            f"  {sentence}"
        )


def _insert_after(prompt: str, anchor: str, addition: str) -> str:
    return prompt.replace(anchor, f"{anchor} {addition}", 1)


def build(arm: str, shipped: str) -> str:
    """The system prompt for `arm`, derived from `shipped` (the text of prompt/system.txt)."""
    if arm not in ARMS:
        raise ValueError(f"unknown arm {arm!r}; use one of {', '.join(ARMS)}")
    _require_once(shipped, ANCHOR, "anchor sentence")
    _require_once(shipped, RULE, "clitic rule sentence")
    _require_once(shipped, EXAMPLE, "clitic example sentence")
    guidance = f" {RULE} {EXAMPLE}"
    _require_once(shipped, ANCHOR + guidance, "anchor, rule and example in sequence")
    if SECOND_EXAMPLE in shipped:
        raise PromptDrift("prompt/system.txt has drifted: it already carries the second example")

    no_guidance = shipped.replace(guidance, "", 1)
    if arm == "no-guidance":
        return no_guidance
    if arm == "rule":
        return _insert_after(no_guidance, ANCHOR, RULE)
    rebuilt = _insert_after(no_guidance, ANCHOR, f"{RULE} {EXAMPLE}")
    if rebuilt != shipped:
        raise PromptDrift("prompt/system.txt has drifted: removing and re-inserting the clitic "
                          "guidance does not reproduce it")
    if arm == "second-example":
        return _insert_after(shipped, EXAMPLE, SECOND_EXAMPLE)
    return shipped


def build_all(shipped: str) -> dict[str, str]:
    return {arm: build(arm, shipped) for arm in ARMS}
