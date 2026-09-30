from cogbias import tasks
from cogbias.catalogue import BIASES, get_bias


def test_tasks_load_and_reference_known_biases():
    t = tasks.load_tasks()
    assert len(t) >= 7
    ids = {b.id for b in BIASES}
    for task in t.values():
        assert task["bias"] in ids
        assert task["debrief"]


def test_scoring():
    t = tasks.load_tasks()
    assert tasks.score_choice(t["linda"], "teller")["correct"]
    assert not tasks.score_choice(t["linda"], "teller_feminist")["correct"]
    assert tasks.score_choice(t["asian_disease"], "gamble")["risky"]
    assert tasks.score_multi(t["wason"], ["8", "red"])["correct"]
    assert tasks.score_multi(t["wason"], ["8", "blue"])["false_alarms"] == 1
    r = tasks.score_numeric(t["un_africa"], 45, "high")
    assert r["pulled_toward_anchor"] and r["error"] == 17
    c = tasks.score_calibration(t["trivia"], ["b", "a"], [0.9, 0.9])
    assert c["accuracy"] == 1.0 and abs(c["overconfidence"] + 0.1) < 1e-9


def test_catalogue_lookup():
    assert get_bias("anchoring").modelled
    assert all(b.references for b in BIASES)
