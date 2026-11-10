"""Offer policies that need no language model, all scored on the same call queue."""

from __future__ import annotations

from .models import Uplift
from .offers import eligible


def no_offer(c: dict, **_) -> str:
    return "none"


def blanket_discount(c: dict, **_) -> str:
    """What many desks do: offer the discount to everyone at risk (if the rules allow it)."""
    return "loyalty_discount" if eligible("loyalty_discount", c)[0] else "none"


def rules(c: dict, **_) -> str:
    """A hand-written playbook from account data."""
    for offer, cond in (("network_callback", c["dropped_call_pct"] >= 3.0 or c["tickets_90d"] >= 3),
                        ("device_upgrade", c["device_age_months"] >= 24),
                        ("contract_bonus", c["contract"] == "month_to_month"),
                        ("loyalty_discount", True)):
        if cond and eligible(offer, c)[0]:
            return offer
    return "none"


def uplift_best(c: dict, model: Uplift, **_) -> str:
    """Best eligible offer by predicted net value, or none if no offer is predicted to pay back."""
    o, v = model.ranked(c)[0]
    return o if v > 0 else "none"
