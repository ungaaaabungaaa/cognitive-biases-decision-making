"""Command-line interface: ``cogbias <command>`` (or ``python -m cogbias``)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import pandas as pd

from cogbias import analysis, catalogue, debiasing, simulation, tasks


def cmd_catalogue(args):
    if args.bias:
        b = catalogue.get_bias(args.bias)
        print(f"{b.name}  [{b.category}]\n")
        print("Definition:  " + b.definition)
        print("Mechanism:   " + b.mechanism)
        print("Classic:     " + b.classic_demo)
        print("\nConsequences:")
        for c in b.consequences:
            print("  - " + c)
        print("\nDebiasing:")
        for d in b.debiasing:
            print("  - " + d)
        print("\nReferences:")
        for r in b.references:
            print("  - " + r)
        return
    for cat, items in catalogue.categories().items():
        print(f"\n{cat}")
        for b in items:
            flag = " (modelled)" if b.modelled else ""
            print(f"  {b.id:<20} {b.name}{flag}")


def cmd_simulate(args):
    res = simulation.run_all(n=args.n, seed=args.seed, profile=args.profile)
    rows = analysis.scorecard(res)
    if args.json:
        print(json.dumps(rows, indent=2))
    else:
        print(f"Population: {args.n} {args.profile} agents (seed {args.seed})\n")
        print(analysis.format_scorecard(rows))
    if args.out:
        long = pd.concat(res.values(), ignore_index=True)
        long.to_csv(args.out, index=False)
        print(f"\nwrote {len(long)} rows to {args.out}")


def cmd_debias(args):
    rows = debiasing.evaluate(n=args.n, seed=args.seed)
    if args.json:
        print(json.dumps(rows, indent=2))
        return
    print(f"{'intervention':<30}{'bias':<20}{'metric':<26}{'before':>8}{'after':>8}{'change':>9}")
    for r in rows:
        print(f"{r['intervention']:<30}{r['bias']:<20}{r['metric']:<26}{r['before']:>8}{r['after']:>8}{-r['reduction']:>+9.0%}")
    print("\nEvidence:")
    for r in rows:
        print(f"  {r['intervention']}: {r['evidence']}")


def cmd_analyze(args):
    df = pd.read_csv(args.csv)
    rows = analysis.scorecard_from_long(df)
    if args.json:
        print(json.dumps(rows, indent=2))
    else:
        print(analysis.format_scorecard(rows))


def cmd_figures(args):
    from cogbias import figures

    paths = figures.make_all(args.out, n=args.n, seed=args.seed)
    for p in paths:
        print(p)


def _ask(prompt: str, valid=None, numeric=False):
    while True:
        raw = input(prompt).strip()
        if numeric:
            try:
                return float(raw)
            except ValueError:
                print("  please enter a number")
                continue
        if valid is None or raw.lower() in valid:
            return raw.lower()
        print(f"  please answer one of: {', '.join(valid)}")


def cmd_quiz(args):
    """Interactive terminal version of the experiment with immediate debriefs."""
    import random

    rng = random.Random(args.seed)
    all_tasks = tasks.load_tasks()
    records = []
    print("\nCOGNITIVE BIAS SELF-ASSESSMENT\nAnswer honestly; there are no trick questions, only tricky ones.\n")
    for tid, t in all_tasks.items():
        print("=" * 70)
        print(f"{t['title'].upper()}   ({catalogue.get_bias(t['bias']).name})")
        print("=" * 70)
        sc = t["scoring"]["type"]
        cond = None
        if t["design"] == "between":
            cond = rng.choice(list(t["conditions"]))
            spec = t["conditions"][cond]
        else:
            spec = t
        intro = spec.get("intro", t.get("intro", ""))
        print(intro + "\n")
        if "anchor" in spec:
            print(f"  Random number: {spec['anchor']}\n")
            hl = _ask(f"Is the true value higher or lower than {spec['anchor']}? [higher/lower] ", ["higher", "lower"])
        if sc == "choice":
            opts = spec.get("options", t.get("options"))
            for i, o in enumerate(opts, 1):
                print(f"  {i}. {o['text']}")
            k = int(_ask(f"\n{t.get('question', 'Your choice')} [1-{len(opts)}] ", [str(i) for i in range(1, len(opts) + 1)]))
            resp = opts[k - 1]["id"]
            result = tasks.score_choice(t, resp)
        elif sc == "multi":
            for o in t["options"]:
                print(f"  [{o['id']}]")
            raw = input(f"\n{t['question']} (comma-separated) ").lower()
            resp = [x.strip() for x in raw.split(",") if x.strip()]
            result = tasks.score_multi(t, resp)
        elif sc == "numeric":
            resp = _ask(f"{spec.get('question', t.get('question'))} ", numeric=True)
            result = tasks.score_numeric(t, resp, cond)
        elif sc == "calibration":
            answers, confs = [], []
            for it in t["items"]:
                print(f"\n  {it['q']}\n   a) {it['a']}\n   b) {it['b']}")
                answers.append(_ask("  answer [a/b] ", ["a", "b"]))
                confs.append(_ask("  confidence 50-100%: ", numeric=True) / 100)
            resp = None
            result = tasks.score_calibration(t, answers, confs)
        print("\n-- Debrief --")
        print(t["debrief"])
        print("Your result:", json.dumps(result))
        records.append({"task_id": tid, "bias": t["bias"], "condition": cond, "response": resp, **result})
        print()
    print("=" * 70)
    print("SUMMARY")
    for r in records:
        print(f"  {r['task_id']:<15} {json.dumps({k: v for k, v in r.items() if k not in ('task_id', 'bias')})}")
    if args.out:
        pd.DataFrame(records).to_csv(args.out, index=False)
        print(f"\nsaved to {args.out}")


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="cogbias", description="Cognitive biases in decision-making: models, simulation, analysis.")
    sub = p.add_subparsers(dest="command", required=True)

    s = sub.add_parser("catalogue", help="list biases, or describe one")
    s.add_argument("bias", nargs="?")
    s.set_defaults(func=cmd_catalogue)

    s = sub.add_parser("simulate", help="simulate a population and score each bias")
    s.add_argument("--n", type=int, default=1000)
    s.add_argument("--seed", type=int, default=42)
    s.add_argument("--profile", choices=["typical", "rational"], default="typical")
    s.add_argument("--out", help="write the long-format responses to this CSV")
    s.add_argument("--json", action="store_true")
    s.set_defaults(func=cmd_simulate)

    s = sub.add_parser("debias", help="evaluate debiasing interventions")
    s.add_argument("--n", type=int, default=1000)
    s.add_argument("--seed", type=int, default=42)
    s.add_argument("--json", action="store_true")
    s.set_defaults(func=cmd_debias)

    s = sub.add_parser("analyze", help="score a CSV of responses (simulated, quiz or web export)")
    s.add_argument("csv")
    s.add_argument("--json", action="store_true")
    s.set_defaults(func=cmd_analyze)

    s = sub.add_parser("figures", help="regenerate the figures in docs/images")
    s.add_argument("--out", default="docs/images")
    s.add_argument("--n", type=int, default=2000)
    s.add_argument("--seed", type=int, default=42)
    s.set_defaults(func=cmd_figures)

    s = sub.add_parser("quiz", help="take the experiment in the terminal")
    s.add_argument("--seed", type=int, default=None)
    s.add_argument("--out", help="save your responses to this CSV")
    s.set_defaults(func=cmd_quiz)
    return p


def main(argv=None):
    args = build_parser().parse_args(argv)
    try:
        args.func(args)
    except KeyboardInterrupt:
        print("\ninterrupted")
        sys.exit(130)


if __name__ == "__main__":
    main()
