"""Scoring and statistics."""

from retention.evaluate import boot_diff, oracle, policy_metrics
from retention.metrics import wilson
from retention.offers import NAMES, eligible
from retention.simulate import customers


def test_oracle_is_eligible_and_never_beaten():
    for c in customers("sample", 200):
        o = oracle(c)
        assert eligible(o, c)[0]
        assert all(c["_truth"]["net"][o] >= c["_truth"]["net"][x] for x in NAMES if eligible(x, c)[0])


def test_no_offer_policy_scores_zero_and_counts_nothing():
    q = customers("sample", 50)
    m = policy_metrics(q, ["none"] * 50)
    assert m["net_value"] == 0 and m["offers_made"]["k"] == 0 and m["offer_spend"] == 0


def test_offers_to_leavers_are_counted_as_waste():
    q = [c for c in customers("sample", 500) if c["_truth"]["driver"] == "relocation"][:5]
    m = policy_metrics(q, ["network_callback"] * 5)
    assert m["offers_to_leavers"] == 5 and m["net_value"] < 0


def test_boot_diff_is_deterministic_and_counts_wins():
    a, b = [1.0, 2.0, 0.0, 3.0], [0.0, 2.0, 1.0, 0.0]
    d = boot_diff(a, b)
    assert d == boot_diff(a, b) and d["diff"] == 3.0 and d["better"] == 2 and d["worse"] == 1


def test_wilson_interval_known_value():
    lo, hi = wilson(10, 20)
    assert round(lo, 3) == 0.299 and round(hi, 3) == 0.701
