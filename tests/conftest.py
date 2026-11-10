import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))


@pytest.fixture(scope="session")
def metrics():
    return json.loads((ROOT / "results/metrics.json").read_text())


@pytest.fixture(scope="session")
def q():
    from retention.data import queue

    return queue()


@pytest.fixture(scope="session")
def model():
    from retention.data import uplift_model

    return uplift_model()


def customer(**kw):
    base = {"id": "x", "plan": "postpaid_basic", "contract": "month_to_month", "tenure_months": 20,
            "monthly_charge": 30.0, "data_gb": 8.0, "dropped_call_pct": 1.0, "tickets_90d": 0,
            "late_payments_12m": 0, "device_age_months": 20, "autopay": True, "discount_last_12m": False,
            "age_band": "30-44", "region": "Eastmere", "note": "Last call: checked the data allowance."}
    return {**base, **kw}


class FakeLLM:
    def __init__(self, replies):
        self.replies, self.seen = list(replies), []

    def create_chat_completion(self, messages, **kw):
        self.seen.append([dict(m) for m in messages])
        text = self.replies.pop(0) if self.replies else "no idea"
        return {"choices": [{"message": {"content": text}}], "usage": {"prompt_tokens": 10, "completion_tokens": 5}}
