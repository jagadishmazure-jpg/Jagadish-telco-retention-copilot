"""One customer from the call queue end to end, without a model: what the desk sees, what each policy
offers, the measured copilot reply and what the guard did with it.

    python examples/demo.py [customer-id]
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from retention import policies as P  # noqa: E402
from retention.copilot import SHOWN  # noqa: E402
from retention.data import queue, uplift_model  # noqa: E402


def main(cid: str | None = None) -> None:
    q = queue()
    c = next(x for x in q if x["id"] == cid) if cid else q[0]
    print(f"customer {c['id']}")
    print("  " + ", ".join(f"{k}={c[k]}" for k in SHOWN[:6]))
    print("  " + ", ".join(f"{k}={c[k]}" for k in SHOWN[6:]))
    print(f"  note: {c['note']}")
    m = uplift_model()
    print("uplift shortlist: " + "; ".join(f"{o} {v:+.0f}" for o, v in m.ranked(c)[:3]))
    for name, f in (("blanket discount", P.blanket_discount), ("rules playbook", P.rules)):
        print(f"{name}: {f(c)}")
    print(f"uplift model: {P.uplift_best(c, model=m)}")
    runs = ROOT / "data/runs/gemma4-e2b.hybrid.jsonl"
    rec = next((json.loads(x) for x in runs.read_text().splitlines() if json.loads(x)["id"] == c["id"]), None)
    if rec:
        print(f"copilot (measured): {rec['offer_raw']}; guard issues: {rec['issues'] or 'none'}; desk sees: {rec['offer']}")
        print(f"  talk track: {rec['talk_track']}")
    t = c["_truth"]
    best = max(t["net"], key=t["net"].get)
    print(f"hidden truth: driver={t['driver']}, best offer={best} ({t['net'][best]:+.1f}), "
          f"copilot offer value {t['net'][rec['offer']] if rec else 0:+.1f}")


if __name__ == "__main__":
    main(*sys.argv[1:2])
