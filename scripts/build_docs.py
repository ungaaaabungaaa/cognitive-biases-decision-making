"""Render docs/BIAS_CATALOGUE.md from the Python catalogue so docs and code never drift."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from cogbias.catalogue import categories  # noqa: E402
from cogbias.debiasing import INTERVENTIONS  # noqa: E402


def main() -> None:
    lines = ["# Bias catalogue", "",
             "Generated from `src/cogbias/catalogue.py` by `scripts/build_docs.py`. "
             "Each entry gives the definition, the mechanism in dual-process terms, the classic demonstration, "
             "real-world consequences, evidence-based debiasing strategies and primary references.", ""]
    for cat, items in categories().items():
        lines += [f"## {cat}", ""]
        for b in items:
            lines += [f"### {b.name}", "", f"**Definition.** {b.definition}", "",
                      f"**Mechanism.** {b.mechanism}", "", f"**Classic demonstration.** {b.classic_demo}", "",
                      "**Consequences**", ""] + [f"- {c}" for c in b.consequences] + ["", "**Debiasing**", ""] \
                     + [f"- {d}" for d in b.debiasing] + ["", "**References**", ""] + [f"- {r}" for r in b.references]
            if b.modelled:
                lines += ["", f"*Quantitative model:* `cogbias.models` / `cogbias.simulation` (`{b.id}`)."]
            lines += [""]
    lines += ["## Interventions implemented in the simulator", "",
              "| Intervention | Targets | What you do | Evidence |", "|---|---|---|---|"]
    for iv in INTERVENTIONS:
        lines.append(f"| {iv.name} | {iv.targets.replace('_', ' ')} | {iv.description} | {iv.evidence} |")
    (ROOT / "docs" / "BIAS_CATALOGUE.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("wrote docs/BIAS_CATALOGUE.md")


if __name__ == "__main__":
    main()
