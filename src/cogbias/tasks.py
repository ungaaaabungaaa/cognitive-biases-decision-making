"""Loader and scorer for the experimental tasks in ``experiments/tasks/*.json``.

The JSON files are the single source of truth: the terminal quiz, the tests,
and the web experiment (via ``scripts/build_web_tasks.py``) all read them.
"""

from __future__ import annotations

import json
from pathlib import Path

TASK_DIR = Path(__file__).resolve().parents[2] / "experiments" / "tasks"

TASK_ORDER = ["asian_disease", "un_africa", "cab_problem", "linda", "wason", "trivia", "sunk_cost"]


def load_tasks(task_dir: Path | str = TASK_DIR) -> dict[str, dict]:
    tasks = {}
    for path in sorted(Path(task_dir).glob("*.json")):
        with open(path, encoding="utf-8") as fh:
            t = json.load(fh)
        tasks[t["id"]] = t
    return {k: tasks[k] for k in TASK_ORDER if k in tasks} | {k: v for k, v in tasks.items() if k not in TASK_ORDER}


def score_choice(task: dict, response: str) -> dict:
    sc = task["scoring"]
    if sc["type"] == "choice" and "correct" in sc:
        return {"correct": response == sc["correct"]}
    if sc["type"] == "choice":
        return {"risky": response == sc["risky_option"]}
    raise ValueError("not a choice task")


def score_multi(task: dict, responses: list[str]) -> dict:
    sc = task["scoring"]
    if sc["type"] != "multi":
        raise ValueError("not a multi-select task")
    correct = set(sc["correct"])
    chosen = set(responses)
    return {"correct": chosen == correct, "hits": len(chosen & correct), "false_alarms": len(chosen - correct)}


def score_numeric(task: dict, response: float, condition: str | None = None) -> dict:
    sc = task["scoring"]
    if sc["type"] != "numeric":
        raise ValueError("not a numeric task")
    answer = task.get("answer")
    out = {"error": None if answer is None else float(response) - float(answer)}
    if condition and "anchor" in task["conditions"].get(condition, {}):
        anchor = task["conditions"][condition]["anchor"]
        out["pulled_toward_anchor"] = abs(response - anchor) < abs(answer - anchor)
    return out


def score_calibration(task: dict, answers: list[str], confidences: list[float]) -> dict:
    items = task["items"]
    correct = [a == it["correct"] for a, it in zip(answers, items)]
    n = len(correct)
    acc = sum(correct) / n if n else 0.0
    conf = sum(confidences) / n if n else 0.0
    return {"accuracy": acc, "mean_confidence": conf, "overconfidence": conf - acc, "n": n}
