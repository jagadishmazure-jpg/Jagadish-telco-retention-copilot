"""Retention offers Halvorsk Mobile's retention desk may make, their cost, eligibility and limits."""

from __future__ import annotations

# cost: what the offer costs the operator over 12 months, in the operator's currency units.
OFFERS = {
    "none": {"cost": 0.0, "desc": "no offer; thank the customer and log the call"},
    "loyalty_discount": {"cost_share": 0.15, "desc": "15% off the monthly charge for 12 months"},
    "device_upgrade": {"cost": 120.0, "desc": "early device upgrade with a 24-month contract"},
    "data_boost": {"cost": 48.0, "desc": "extra 20 GB a month for 12 months"},
    "network_callback": {"cost": 30.0, "desc": "a network engineer calls back and checks coverage at home"},
    "contract_bonus": {"cost": 60.0, "desc": "one-off bill credit for moving from month-to-month to a 12-month contract"},
}
NAMES = list(OFFERS)
MAX_COST = 220.0  # per customer, per year; anything above needs a supervisor
FORBIDDEN_PROMISES = ["free forever", "100% off", "lifetime discount", "waive all charges", "cancel the contract fee"]


def cost(offer: str, customer: dict) -> float:
    o = OFFERS[offer]
    return round(o.get("cost", 0.0) + o.get("cost_share", 0.0) * customer["monthly_charge"] * 12, 2)


def eligible(offer: str, customer: dict) -> tuple[bool, str]:
    """Business rules. Protected attributes (age band, region) are never read here."""
    if offer not in OFFERS:
        return False, f"unknown offer {offer!r}"
    if offer == "loyalty_discount" and customer["discount_last_12m"]:
        return False, "already had a loyalty discount in the last 12 months"
    if offer == "device_upgrade" and customer["device_age_months"] < 18:
        return False, "device younger than 18 months"
    if offer == "contract_bonus" and customer["contract"] != "month_to_month":
        return False, "already on a fixed-term contract"
    if offer == "data_boost" and customer["plan"] == "prepaid":
        return False, "not available on prepaid"
    if cost(offer, customer) > MAX_COST:
        return False, f"cost above the {MAX_COST:g} per-customer limit"
    return True, "ok"


def menu() -> str:
    return "\n".join(f"- {k}: {v['desc']}" for k, v in OFFERS.items())
