from __future__ import annotations

import threading

import pytest

from gloss_eval.ledger import SpendLedger, worst_case_cost
from gloss_eval.pricing import cost_usd

HAIKU = "claude-haiku-4-5-20251001"
WORST = worst_case_cost(HAIKU)


def test_worst_case_is_3200_in_and_the_full_max_tokens_out():
    assert WORST == pytest.approx(cost_usd(HAIKU, 3200, 300))
    assert WORST == pytest.approx(0.0047)


def test_a_ceiling_is_required():
    with pytest.raises(ValueError):
        SpendLedger(0)


def test_the_call_that_would_cross_the_ceiling_is_refused():
    ledger = SpendLedger(WORST * 1.5)
    assert ledger.claim(HAIKU) == pytest.approx(WORST)
    assert ledger.claim(HAIKU) is None
    assert ledger.refused == 1


def test_settling_charges_the_real_cost_and_releases_the_reservation():
    ledger = SpendLedger(WORST * 1.5)
    reserved = ledger.claim(HAIKU)
    ledger.settle(HAIKU, reserved, 0.003)
    assert ledger.spent == pytest.approx(0.003)
    # 0.003 spent plus one more worst case is 0.0077, beyond the 0.00705 ceiling.
    assert ledger.claim(HAIKU) is None
    roomy = SpendLedger(WORST * 2.5)
    roomy.settle(HAIKU, roomy.claim(HAIKU), 0.003)
    assert roomy.claim(HAIKU) == pytest.approx(WORST)


def test_the_reservation_rises_after_an_expensive_answer():
    ledger = SpendLedger(1.0)
    ledger.settle(HAIKU, ledger.claim(HAIKU), WORST * 3)
    assert ledger.reservation(HAIKU) == pytest.approx(WORST * 3)
    ledger.settle(HAIKU, ledger.claim(HAIKU), 0.001)
    assert ledger.reservation(HAIKU) == pytest.approx(WORST * 3)


def test_the_total_persists_across_ledgers_sharing_a_file(tmp_path):
    path = tmp_path / "run.ledger.json"
    first = SpendLedger(0.01, path)
    first.settle(HAIKU, first.claim(HAIKU), 0.004)
    second = SpendLedger(0.01, path)
    assert second.spent_before == pytest.approx(0.004)
    assert second.claim(HAIKU) == pytest.approx(WORST)
    assert second.claim(HAIKU) is None
    second.settle(HAIKU, WORST, 0.002)
    assert SpendLedger(0.01, path).spent_before == pytest.approx(0.006)


def test_an_unreadable_ledger_is_an_error_not_a_zero(tmp_path):
    path = tmp_path / "broken.ledger.json"
    path.write_text("{not json", encoding="utf-8")
    with pytest.raises(ValueError, match="unreadable"):
        SpendLedger(1.0, path)


def test_concurrent_claims_never_exceed_the_ceiling():
    ledger = SpendLedger(WORST * 10.5)
    granted: list[float] = []
    start = threading.Barrier(40)

    def claim():
        start.wait()
        amount = ledger.claim(HAIKU)
        if amount is not None:
            granted.append(amount)

    threads = [threading.Thread(target=claim) for _ in range(40)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    assert len(granted) == 10
    assert sum(granted) <= ledger.ceiling_usd
    assert ledger.refused == 30
