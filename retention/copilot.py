"""LLM retention copilot: one-shot from the account alone, or hybrid with the uplift model's shortlist.
Every reply goes through `guard` before a desk agent sees it."""

from __future__ import annotations

import json
import re
import sys
import time
from pathlib import Path

from .models import Uplift
from .offers import FORBIDDEN_PROMISES, MAX_COST, OFFERS, cost, eligible, menu
from .policies import uplift_best
from .simulate import INJECTION, public

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from check_brands import scrub  # noqa: E402

PROMPT = ROOT / "prompts" / "copilot.md"
LIMITS = {"max_new_tokens": 256, "n_ctx": 4096}
CONFIGS = {"gemma4-e2b.oneshot": {"model": "gemma-4-e2b", "mode": "oneshot"},
           "gemma4-e2b.hybrid": {"model": "gemma-4-e2b", "mode": "hybrid"},
           # Stress test: the hybrid with the injected instruction added to every customer's note.
           "gemma4-e2b.hybrid-injected": {"model": "gemma-4-e2b", "mode": "hybrid", "inject": True}}
SHOWN = ["plan", "contract", "tenure_months", "monthly_charge", "data_gb", "dropped_call_pct", "tickets_90d",
         "late_payments_12m", "device_age_months", "autopay", "discount_last_12m"]  # never age band or region
PHONE = re.compile(r"\b07\d{3} \d{6}\b")
NUM = re.compile(r"(?<![\w.])\d+(?:\.\d+)?")


def account_text(c: dict) -> str:
    return "\n".join(f"{k}: {c[k]}" for k in SHOWN)


def rules_text() -> str:
    return ("Eligibility: loyalty_discount not if discount_last_12m is True; device_upgrade only if "
            "device_age_months >= 18; contract_bonus only on month_to_month; data_boost not on prepaid. "
            f"Cost limit per customer: {MAX_COST:g}.")


def with_injection(c: dict) -> dict:
    return c if INJECTION in c["note"] else {**c, "note": c["note"] + " " + INJECTION}


def evidence(c: dict, model: Uplift | None) -> str:
    parts = [f"Account data:\n{account_text(c)}", f"Customer note: {c['note']}", f"Offer menu:\n{menu()}", rules_text()]
    if model is not None:
        short = [f"{o} (predicted net value {v:+.0f})" for o, v in model.ranked(c)[:3]]
        parts.append("Uplift model shortlist, best first: " + "; ".join(short))
    return "\n\n".join(parts)


def find_json(text: str, key: str) -> dict | None:
    dec = json.JSONDecoder()
    for m in re.finditer(r"\{", text):
        try:
            obj, _ = dec.raw_decode(text[m.start():])
        except json.JSONDecodeError:
            continue
        if isinstance(obj, dict) and key in obj:
            return obj
    return None


def allowed_numbers(c: dict, shown: str) -> set[float]:
    nums = {float(x) for x in NUM.findall(shown)} | {float(x) for x in NUM.findall(menu())}
    nums |= {round(c["monthly_charge"] * 0.85, 2), round(c["monthly_charge"] * 0.15, 2), 1.0, 2.0, 3.0}
    return nums


def guard(c: dict, answer: dict | None, shown: str) -> dict:
    """Check a copilot reply; anything that fails is not shown to the desk agent as-is."""
    issues = []
    if answer is None:
        return {"issues": ["no_json"], "ok": False}
    offer = str(answer.get("offer", ""))
    talk = str(answer.get("talk_track", ""))
    if offer not in OFFERS:
        issues.append("unknown_offer")
    elif not eligible(offer, c)[0]:
        issues.append("ineligible_offer")
    elif cost(offer, c) > MAX_COST:
        issues.append("over_cost_limit")
    low = talk.lower()
    if any(p in low for p in FORBIDDEN_PROMISES):
        issues.append("forbidden_promise")
    if PHONE.search(talk):
        issues.append("contact_details_in_talk_track")
    allowed = allowed_numbers(c, shown)
    if any(float(x) not in allowed for x in NUM.findall(talk)):
        issues.append("ungrounded_number")
    return {"issues": issues, "ok": not issues}


def ask(llm, c: dict, model: Uplift | None) -> tuple[dict | None, str, int, int]:
    shown = evidence(c, model)
    msgs = [{"role": "system", "content": PROMPT.read_text().strip()}, {"role": "user", "content": shown}]
    r = llm.create_chat_completion(messages=msgs, temperature=0, max_tokens=LIMITS["max_new_tokens"], seed=0)
    text = scrub(r["choices"][0]["message"]["content"] or "")[0]
    return find_json(text, "offer"), text, r["usage"]["prompt_tokens"], r["usage"]["completion_tokens"]


def run(c: dict, llm, config: str, model: Uplift) -> dict:
    t0 = time.perf_counter()
    spec = CONFIGS[config]
    c = with_injection(c) if spec.get("inject") else c
    m = model if spec["mode"] == "hybrid" else None
    ans, raw, pt, ct = ask(llm, public(c), m)
    g = guard(c, ans, evidence(public(c), m))
    offer = str((ans or {}).get("offer", ""))
    final = offer if g["ok"] else uplift_best(c, model=model)
    return {"id": c["id"], "config": config, "model": spec["model"], "offer_raw": offer, "offer": final,
            "escalated": not g["ok"], "issues": g["issues"],
            "reason": scrub(str((ans or {}).get("reason", "")))[0][:300],
            "talk_track": scrub(str((ans or {}).get("talk_track", "")))[0][:600],
            "injected": INJECTION in c["note"], "prompt_tokens": pt, "completion_tokens": ct,
            "seconds": round(time.perf_counter() - t0, 1), "raw": raw[:800]}
