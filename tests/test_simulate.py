"""The simulator is deterministic and its hidden truth is internally consistent."""

import subprocess
import sys

from conftest import ROOT

from retention.offers import NAMES, cost
from retention.simulate import DRIVERS, INJECTION, campaign, customers, make_customer, public


def test_same_id_gives_the_same_customer_and_ids_differ():
    assert make_customer("test-00007") == make_customer("test-00007")
    assert make_customer("test-00008") != make_customer("test-00007")


def test_committed_data_matches_a_fresh_build():
    r = subprocess.run([sys.executable, "scripts/build_data.py", "--check"], cwd=ROOT, capture_output=True,
                       text=True, check=False)
    assert r.returncode == 0, r.stdout


def test_public_view_hides_every_hidden_field():
    c = make_customer("test-00001")
    assert "_truth" in c and not any(k.startswith("_") for k in public(c))


def test_every_driver_occurs_and_base_churn_is_plausible():
    cs = customers("sample", 1500)
    assert {c["_truth"]["driver"] for c in cs} == set(DRIVERS)
    mean = sum(c["_truth"]["p_churn"] for c in cs) / len(cs)
    assert 0.15 < mean < 0.4


def test_net_value_follows_the_documented_formula():
    c = make_customer("test-00042")
    t = c["_truth"]
    for o in NAMES:
        want = (t["p_churn"] - t["p_offer"][o]) * t["value"] - cost(o, c) * (1 - t["p_offer"][o])
        assert abs(t["net"][o] - want) < 0.01
    assert t["net"]["none"] == 0


def test_no_offer_keeps_a_customer_who_is_leaving_the_country():
    leaver = next(c for c in customers("sample", 400) if c["_truth"]["driver"] == "relocation")
    assert all(p == leaver["_truth"]["p_churn"] for p in leaver["_truth"]["p_offer"].values())


def test_offers_to_settled_customers_backfire():
    settled = next(c for c in customers("sample", 400) if c["_truth"]["driver"] == "none")
    t = settled["_truth"]
    assert all(t["p_offer"][o] > t["p_churn"] for o in NAMES if o != "none")


def test_matching_offer_beats_a_mismatched_one():
    dev = next(c for c in customers("sample", 400) if c["_truth"]["driver"] == "device")
    p = dev["_truth"]["p_offer"]
    assert p["device_upgrade"] < p["network_callback"]


def test_notes_carry_a_callback_number_and_injection_is_flagged():
    cs = customers("sample", 600)
    assert all("Callback number 07" in c["note"] for c in cs)
    inj = [c for c in cs if c["_truth"]["injected"]]
    assert 0.05 < len(inj) / len(cs) < 0.15 and all(INJECTION in c["note"] for c in inj)


def test_campaign_is_randomised_and_deterministic():
    cs = customers("sample", 1200)
    a, b = campaign(cs), campaign(cs)
    assert a == b
    counts = [sum(r["offer"] == o for r in a) for o in NAMES]
    assert min(counts) > 150
