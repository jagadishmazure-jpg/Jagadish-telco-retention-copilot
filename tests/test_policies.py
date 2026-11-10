"""Non-LLM policies."""

from conftest import customer

from retention import policies as P


def test_blanket_discount_respects_eligibility():
    assert P.blanket_discount(customer()) == "loyalty_discount"
    assert P.blanket_discount(customer(discount_last_12m=True)) == "none"


def test_rules_playbook_order():
    assert P.rules(customer(dropped_call_pct=4.0)) == "network_callback"
    assert P.rules(customer(device_age_months=30)) == "device_upgrade"
    assert P.rules(customer()) == "contract_bonus"
    assert P.rules(customer(contract="24_month")) == "loyalty_discount"


def test_uplift_best_says_none_when_nothing_pays_back():
    class Flat:
        def ranked(self, c):
            return [("none", 0.0), ("data_boost", -5.0)]

    assert P.uplift_best(customer(), model=Flat()) == "none"
