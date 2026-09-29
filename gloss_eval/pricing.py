"""Model aliases and their prices, in USD per million tokens. Prices checked 2026-09-29.

The spend ceiling is only as good as these numbers: a price set too low lets a run reserve less
than it will be charged. Check them against the published price list before a paid run.
"""

from __future__ import annotations

PRICES_CHECKED = "2026-09-29"

#: `haiku` is the dated id the app pins, so a run measures the model the app actually calls.
MODELS = {
    "haiku": "claude-haiku-4-5-20251001",
    "sonnet": "claude-sonnet-5",
}

#: model id -> (input, output) USD per million tokens.
USD_PER_MTOK = {
    "claude-haiku-4-5-20251001": (1.00, 5.00),
    "claude-sonnet-5": (2.00, 10.00),
}


def model_id(alias: str) -> str:
    try:
        return MODELS[alias]
    except KeyError:
        raise ValueError(f"unknown model alias {alias!r}; use one of {', '.join(MODELS)}") from None


def cost_usd(model: str, input_tokens: int, output_tokens: int) -> float:
    try:
        input_rate, output_rate = USD_PER_MTOK[model]
    except KeyError:
        raise ValueError(f"no price for model {model!r}") from None
    return (input_tokens * input_rate + output_tokens * output_rate) / 1_000_000


def price_table() -> dict:
    """The prices a run used, for its record."""
    return {
        model: {"input_usd_per_mtok": i, "output_usd_per_mtok": o, "checked": PRICES_CHECKED}
        for model, (i, o) in USD_PER_MTOK.items()
    }
