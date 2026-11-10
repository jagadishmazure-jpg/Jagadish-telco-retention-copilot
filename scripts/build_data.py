"""Generate the synthetic customer base, past campaign and call queue into data/ (deterministic).

    python scripts/build_data.py          # write
    python scripts/build_data.py --check  # fail if committed files differ from a fresh build (CI)
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from retention.data import DATA, build  # noqa: E402


def main() -> int:
    files = build()
    if "--check" in sys.argv:
        bad = [f for f, t in files.items() if not (DATA / f).exists() or (DATA / f).read_text() != t]
        print("data", "DIFFERS: " + ", ".join(bad) if bad else "matches a fresh build")
        return 1 if bad else 0
    DATA.mkdir(exist_ok=True)
    for f, t in files.items():
        (DATA / f).write_text(t)
    print("wrote", ", ".join(files))
    return 0


if __name__ == "__main__":
    sys.exit(main())
