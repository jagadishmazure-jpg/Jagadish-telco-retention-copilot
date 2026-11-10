"""The fixed datasets: a past randomised campaign (train), a holdout base (test) and today's call queue."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

from .models import Uplift
from .simulate import campaign, customers, public

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
N_TRAIN, N_TEST, QUEUE = 12000, 2000, 150


def build() -> dict[str, str]:
    train, test = customers("train", N_TRAIN), customers("test", N_TEST)
    camp = campaign(train)
    model = Uplift().fit(train, camp)
    queue = [c["id"] for c in sorted(test, key=lambda c: -model.churn(c))[:QUEUE]]
    dump = lambda rows: "".join(json.dumps(r, separators=(",", ":")) + "\n" for r in rows)  # noqa: E731
    # Training customers are stored without their hidden truth: the models only ever learn from the
    # account data and the observed campaign outcome.
    return {"train.jsonl": dump([public(c) for c in train]), "campaign.jsonl": dump(camp), "test.jsonl": dump(test),
            "queue.json": json.dumps({"ids": queue, "rule": f"top {QUEUE} test customers by predicted churn"}, indent=1) + "\n"}


def load(name: str, data: Path = DATA) -> list[dict]:
    return [json.loads(x) for x in (data / name).read_text().splitlines() if x.strip()]


@lru_cache(maxsize=4)
def uplift_model(keywords: bool = False) -> Uplift:
    return Uplift(keywords).fit(load("train.jsonl"), load("campaign.jsonl"))


def queue(data: Path = DATA) -> list[dict]:
    ids = json.loads((data / "queue.json").read_text())["ids"]
    by = {c["id"]: c for c in load("test.jsonl", data)}
    return [by[i] for i in ids]
