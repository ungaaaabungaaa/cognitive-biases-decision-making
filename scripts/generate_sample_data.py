"""Regenerate data/sample_responses.csv (simulated, seed-fixed)."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import pandas as pd  # noqa: E402

from cogbias import simulation  # noqa: E402

if __name__ == "__main__":
    res = simulation.run_all(n=300, seed=42)
    long = pd.concat(res.values(), ignore_index=True)
    out = ROOT / "data" / "sample_responses.csv"
    long.to_csv(out, index=False)
    print(f"wrote {len(long)} rows to {out}")
