"""What was measured: every copilot config ran the whole queue once, guardrails held, docs match."""

import json
import subprocess
import sys

from conftest import ROOT

from retention.copilot import CONFIGS


def run(*args):
    return subprocess.run([sys.executable, *args], cwd=ROOT, capture_output=True, text=True, check=False)


def test_every_config_ran_the_whole_queue_once(q, metrics):
    ids = sorted(c["id"] for c in q)
    for c in CONFIGS:
        rows = [json.loads(x) for x in (ROOT / f"data/runs/{c}.jsonl").read_text().splitlines()]
        assert sorted(r["id"] for r in rows) == ids, c
        assert metrics["llm"][c]["n"] == len(ids)


def test_nothing_that_failed_the_guard_reached_the_desk_unchanged():
    for c in CONFIGS:
        for line in (ROOT / f"data/runs/{c}.jsonl").read_text().splitlines():
            r = json.loads(line)
            assert r["escalated"] == bool(r["issues"])


def test_results_replay_and_gate_pass():
    r = run("scripts/run_eval.py", "--check")
    assert r.returncode == 0, r.stdout


def test_measured_files_match_the_manifest():
    r = run("scripts/manifest.py", "--check")
    assert r.returncode == 0, r.stdout


def test_models_file_pins_every_model():
    for m in json.loads((ROOT / "scripts/models.json").read_text())["gguf"]:
        assert "/resolve/main/" not in m["url"] and len(m["sha256"]) == 64 and m["license"] == "Apache-2.0"


def test_numbers_and_example_output_in_the_docs_are_current():
    r = run("scripts/check_numbers.py")
    assert r.returncode == 0, r.stdout
    r = run("scripts/render_docs.py", "--check")
    assert r.returncode == 0, r.stdout + r.stderr
