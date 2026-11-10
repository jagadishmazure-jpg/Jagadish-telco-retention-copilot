"""Run one copilot configuration over the call queue; append to data/runs/<config>.jsonl (resumable).

    python scripts/run_copilot.py --config gemma4-e2b.hybrid [--limit N] [--threads 8]

Needs llama-cpp-python==0.3.36 and the GGUF from scripts/fetch_models.sh. Run detached (nohup).
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from retention.copilot import CONFIGS, LIMITS, run  # noqa: E402
from retention.data import queue, uplift_model  # noqa: E402

RUNS = ROOT / "data" / "runs"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True, choices=list(CONFIGS))
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--threads", type=int, default=8)
    ap.add_argument("--only", nargs="*", default=None)
    ap.add_argument("--models-dir", type=Path, default=ROOT / "models")
    a = ap.parse_args()
    RUNS.mkdir(parents=True, exist_ok=True)
    out = RUNS / f"{a.config}.jsonl"
    done = {json.loads(x)["id"] for x in out.read_text().splitlines()} if out.exists() else set()
    todo = [c for c in queue() if c["id"] not in done and (a.only is None or c["id"] in a.only)][: a.limit or None]
    if not todo:
        print("nothing to do", a.config)
        return 0
    from llama_cpp import Llama

    spec = json.loads((ROOT / "scripts/models.json").read_text())
    f = next(m["file"] for m in spec["gguf"] if m["label"] == CONFIGS[a.config]["model"])
    llm = Llama(str(a.models_dir / f), n_ctx=LIMITS["n_ctx"], n_threads=a.threads, seed=0, verbose=False)
    model = uplift_model()
    with out.open("a", encoding="utf-8") as fh:
        for c in todo:
            r = run(c, llm, a.config, model)
            fh.write(json.dumps(r) + "\n")
            fh.flush()
            print(c["id"], r["offer_raw"], r["offer"], r["issues"], r["seconds"], flush=True)
    print("done", a.config, flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
