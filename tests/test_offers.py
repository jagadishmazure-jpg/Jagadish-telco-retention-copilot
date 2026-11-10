"""Offer rules: cost, eligibility and limits. Protected attributes are never read."""

import pytest
from conftest import customer

from retention.offers import MAX_COST, NAMES, cost, eligible, menu


def test_discount_cost_scales_with_the_monthly_charge():
    assert cost("loyalty_discount", customer(monthly_charge=40.0)) == 72.0
    assert cost("none", customer()) == 0.0


@pytest.mark.parametrize("offer,kw", [("loyalty_discount", {"discount_last_12m": True}),
                                      ("device_upgrade", {"device_age_months": 6}),
                                      ("contract_bonus", {"contract": "24_month"}),
                                      ("data_boost", {"plan": "prepaid"})])
def test_each_eligibility_rule(offer, kw):
    assert eligible(offer, customer())[0] and not eligible(offer, customer(**kw))[0]


def test_cost_limit_blocks_expensive_discounts():
    ok, why = eligible("loyalty_discount", customer(monthly_charge=130.0))
    assert not ok and str(int(MAX_COST)) in why


def test_unknown_offer_is_refused():
    assert eligible("free_phone_for_life", customer()) == (False, "unknown offer 'free_phone_for_life'")


def test_eligibility_ignores_age_band_and_region():
    for o in NAMES:
        assert eligible(o, customer(age_band="18-29", region="Northridge")) == eligible(
            o, customer(age_band="65+", region="Westvale"))


def test_menu_lists_every_offer():
    assert all(f"- {o}:" in menu() for o in NAMES)
