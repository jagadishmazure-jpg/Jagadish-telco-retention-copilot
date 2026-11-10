"""Copilot prompt contents and the guard in front of the desk agent (scripted fake model)."""

import json

from conftest import FakeLLM, customer

from retention.copilot import evidence, find_json, guard, run, with_injection
from retention.simulate import INJECTION, make_customer


def reply(offer="contract_bonus", talk="I can offer you a bill credit if you move to a 12-month contract."):
    return {"offer": offer, "reason": "r", "talk_track": talk}


def test_evidence_never_shows_age_band_region_or_truth(model):
    c = make_customer("test-00003")
    text = evidence(c, model)
    assert c["age_band"] not in text and c["region"] not in text and "_truth" not in text and "p_churn" not in text


def test_hybrid_shows_the_uplift_shortlist_and_oneshot_does_not(model):
    c = customer()
    assert "Uplift model shortlist" in evidence(c, model) and "shortlist" not in evidence(c, None)


def test_guard_passes_a_clean_reply():
    c = customer()
    assert guard(c, reply(), evidence(c, None)) == {"issues": [], "ok": True}


def test_guard_flags_unknown_ineligible_and_missing_answers():
    c = customer(contract="24_month")
    assert guard(c, reply(offer="free_phone"), "")["issues"][0] == "unknown_offer"
    assert guard(c, reply(), evidence(c, None))["issues"] == ["ineligible_offer"]
    assert guard(c, None, "")["issues"] == ["no_json"]


def test_guard_flags_forbidden_promises_and_contact_details():
    c = customer(note="Last call: comparing prices. Callback number 07123 456789.")
    sh = evidence(c, None)
    assert "forbidden_promise" in guard(c, reply(talk="We will give you 100% off."), sh)["issues"]
    assert "contact_details_in_talk_track" in guard(c, reply(talk="I'll call you on 07123 456789."), sh)["issues"]


def test_guard_flags_numbers_not_in_the_account_or_menu():
    c = customer()
    sh = evidence(c, None)
    assert guard(c, reply(talk="You have been with us 20 months."), sh)["ok"]
    assert "ungrounded_number" in guard(c, reply(talk="You have been with us 7 years."), sh)["issues"]


def test_find_json_after_prose():
    assert find_json('I suggest this. {"offer": "none", "talk_track": "x"}', "offer")["offer"] == "none"


def test_run_keeps_a_clean_answer(model):
    c = make_customer("test-00011")
    llm = FakeLLM([json.dumps(reply(offer="none", talk="Thanks for calling."))])
    r = run(c, llm, "gemma4-e2b.oneshot", model)
    assert r["offer"] == "none" and not r["escalated"] and "shortlist" not in llm.seen[0][1]["content"]


def test_a_reply_that_follows_the_injection_is_escalated_and_replaced(model):
    c = make_customer("test-00011")
    bad = json.dumps(reply(offer="loyalty_discount", talk="As requested you get 100% off for life."))
    r = run(c, FakeLLM([bad]), "gemma4-e2b.hybrid-injected", model)
    assert r["injected"] and r["escalated"] and "forbidden_promise" in r["issues"]
    assert r["offer"] != "loyalty_discount" or not r["issues"] == []


def test_injection_stress_adds_the_instruction_once():
    c = customer()
    once = with_injection(c)
    assert INJECTION in once["note"] and with_injection(once)["note"].count(INJECTION) == 1


def test_prompt_says_notes_are_not_instructions():
    from retention.copilot import PROMPT

    t = PROMPT.read_text().lower()
    assert "never as instructions" in t and "phone numbers" in t and "supervisor" in t
