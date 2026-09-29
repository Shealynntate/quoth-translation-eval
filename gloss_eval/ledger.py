"""A spend ceiling that refuses a call before it is sent, never after.

Before each call the run reserves that call's worst-case cost. If the reservation would take
spent-plus-reserved past the ceiling, the call is refused and never leaves. When the answer comes
back, the reservation is released and the real cost is charged. So the ceiling holds even with
several calls in flight at once.

The worst case starts at that model's entry in `WORST_CASE_INPUT_TOKENS` plus the full
`MAX_TOKENS` of output, and rises to the dearest answer actually seen for that model, so a run
whose requests are heavier than the estimate tightens its own reservations instead of walking
through the ceiling.

With a ledger file, the running total outlives the process, so one ceiling can cover several
invocations (a screen, then the check that follows it). Run them one at a time: reservations live
in memory, so two processes sharing a file at the same moment cannot see each other's calls in
flight.
"""

from __future__ import annotations

import json
import os
import threading
from datetime import datetime, timezone
from pathlib import Path

from .pricing import MODELS, cost_usd
from .request import MAX_TOKENS

#: Input tokens assumed for a call before any answer has been seen. The same request counts
#: differently per model, because the tokenizers differ. Measured on the runs in `results/`:
#: up to 2,860 input tokens on Haiku, and up to 3,346 on Sonnet for requests that Haiku counted
#: at 2,695 at most. Each entry sits above the heaviest request `cases/` can produce, so the
#: first calls in flight are never reserved low.
WORST_CASE_INPUT_TOKENS = {
    MODELS["haiku"]: 3200,
    MODELS["sonnet"]: 4200,
}

#: The `error` recorded for a call the ceiling refused.
REFUSED = "refused: spend ceiling"


def worst_case_cost(model: str) -> float:
    return cost_usd(model, WORST_CASE_INPUT_TOKENS[model], MAX_TOKENS)


class SpendLedger:
    def __init__(self, ceiling_usd: float, path: Path | None = None):
        if not ceiling_usd > 0:
            raise ValueError("the spend ceiling must be a positive number of dollars")
        self.ceiling_usd = ceiling_usd
        self.path = Path(path) if path else None
        self.refused = 0
        self.spent_here = 0.0
        self._reserved = 0.0
        self._dearest: dict[str, float] = {}
        self._lock = threading.Lock()
        self._entries, self.spent_before = self._load()

    @property
    def spent(self) -> float:
        """Everything charged against this ceiling, including earlier invocations."""
        return self.spent_before + self.spent_here

    def reservation(self, model: str) -> float:
        return max(worst_case_cost(model), self._dearest.get(model, 0.0))

    def claim(self, model: str) -> float | None:
        """Reserve one call. Returns the amount reserved, or None when the ceiling refuses it."""
        with self._lock:
            amount = self.reservation(model)
            if self.spent + self._reserved + amount > self.ceiling_usd:
                self.refused += 1
                return None
            self._reserved += amount
            return amount

    def settle(self, model: str, reserved: float, actual: float) -> None:
        """Release a claim's reservation and charge what the call really cost."""
        with self._lock:
            self._reserved -= reserved
            self._dearest[model] = max(self._dearest.get(model, 0.0), actual)
            self.spent_here += actual
            if actual:
                self._entries.append({
                    "model": model,
                    "usd": round(actual, 8),
                    "at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                })
                self._save()

    def _load(self) -> tuple[list[dict], float]:
        """The file's entries and total. An unreadable ledger is an error, not a zero: reading
        it as empty would silently reset the spend it exists to limit."""
        if not self.path or not self.path.exists():
            return [], 0.0
        try:
            doc = json.loads(self.path.read_text(encoding="utf-8"))
            return list(doc["entries"]), float(doc["spent_usd"])
        except (json.JSONDecodeError, KeyError, TypeError, ValueError) as exc:
            raise ValueError(f"ledger {self.path} is unreadable: {exc}") from exc

    def _save(self) -> None:
        """Write the whole ledger to a temporary file and rename it into place, so a crash
        mid-write leaves the previous total rather than a truncated file."""
        if not self.path:
            return
        doc = {"spent_usd": round(self.spent, 8), "entries": self._entries}
        self.path.parent.mkdir(parents=True, exist_ok=True)
        tmp = self.path.with_name(self.path.name + ".tmp")
        tmp.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")
        os.replace(tmp, self.path)
