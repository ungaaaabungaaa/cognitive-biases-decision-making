/* Cognitive Bias Lab: runs the tasks bundled in tasks.js, scores them, and shows debriefs.
   No dependencies, no network, works from file://. */
(function () {
  "use strict";
  const TASKS = window.COGBIAS_TASKS;
  const BIASES = window.COGBIAS_BIASES;
  const $ = (sel) => document.querySelector(sel);
  const screens = { intro: $("#screen-intro"), task: $("#screen-task"), debrief: $("#screen-debrief"), summary: $("#screen-summary") };
  const state = { i: 0, records: [], conditions: {} };

  function show(name) {
    Object.entries(screens).forEach(([k, el]) => el.classList.toggle("hidden", k !== name));
    window.scrollTo({ top: 0, behavior: "smooth" });
  }
  function esc(s) { return String(s).replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c])); }
  function pick(arr) { return arr[Math.floor(Math.random() * arr.length)]; }

  // ---------------------------------------------------------------- rendering
  function header(task) {
    const pct = Math.round((state.i / TASKS.length) * 100);
    return `<div class="progress"><div style="width:${pct}%"></div></div>
      <p class="kicker">Task ${state.i + 1} of ${TASKS.length}</p><h2>${esc(task.title)}</h2>`;
  }

  function renderTask(task) {
    let cond = null, spec = task;
    if (task.design === "between") {
      cond = pick(Object.keys(task.conditions));
      spec = Object.assign({}, task, task.conditions[cond]);
    }
    state.conditions[task.id] = cond;
    let html = header(task) + `<p>${esc(spec.intro || task.intro || "")}</p>`;
    const type = task.scoring.type;

    if (type === "choice") {
      const opts = spec.options || task.options;
      html += `<p><strong>${esc(spec.question || task.question || "Which do you choose?")}</strong></p><div class="options">` +
        opts.map((o) => `<label class="option"><input type="radio" name="choice" value="${esc(o.id)}"><span>${esc(o.text)}</span></label>`).join("") + "</div>";
    } else if (type === "multi") {
      html += `<p><strong>${esc(task.question)}</strong></p><div class="cards">` +
        task.options.map((o) => `<div class="playing ${["blue", "red"].includes(o.id) ? o.id : ""}" data-id="${esc(o.id)}">${["blue", "red"].includes(o.id) ? "" : esc(o.text)}</div>`).join("") + "</div>";
    } else if (type === "numeric") {
      if (spec.anchor !== undefined) {
        html += `<div class="anchor">${spec.anchor}</div>
          <div class="row"><span>Is the true value higher or lower than ${spec.anchor}?</span>
          <label><input type="radio" name="hl" value="higher"> higher</label><label><input type="radio" name="hl" value="lower"> lower</label></div>`;
      }
      html += `<p><strong>${esc(spec.question || task.question)}</strong></p>
        <div class="row"><input type="number" id="num" min="${task.scoring.min}" max="${task.scoring.max}" step="1"> <span class="muted">(${task.scoring.min}-${task.scoring.max})</span></div>`;
    } else if (type === "calibration") {
      html += task.items.map((it, k) => `<div class="trivia-item"><p><strong>${k + 1}. ${esc(it.q)}</strong></p>
        <div class="options"><label class="option"><input type="radio" name="q${k}" value="a"><span>${esc(it.a)}</span></label>
        <label class="option"><input type="radio" name="q${k}" value="b"><span>${esc(it.b)}</span></label></div>
        <div class="row"><span>Confidence:</span><input type="range" name="c${k}" min="50" max="100" step="5" value="75" oninput="this.nextElementSibling.textContent=this.value+'%'"><output>75%</output></div></div>`).join("");
    }
    html += `<p class="muted" id="err"></p><button class="primary" id="submit">Submit</button>`;
    screens.task.innerHTML = html;
    screens.task.querySelectorAll(".playing").forEach((c) => c.addEventListener("click", () => c.classList.toggle("selected")));
    $("#submit").addEventListener("click", () => submit(task, cond, spec));
    show("task");
  }

  // ---------------------------------------------------------------- scoring
  function submit(task, cond, spec) {
    const type = task.scoring.type;
    const err = $("#err");
    let response, result;
    if (type === "choice") {
      const el = screens.task.querySelector("input[name=choice]:checked");
      if (!el) return (err.textContent = "Please choose an option.");
      response = el.value;
      result = "correct" in task.scoring ? { correct: response === task.scoring.correct }
                                          : { risky: response === task.scoring.risky_option };
    } else if (type === "multi") {
      response = [...screens.task.querySelectorAll(".playing.selected")].map((c) => c.dataset.id);
      if (!response.length) return (err.textContent = "Select at least one card.");
      const correct = new Set(task.scoring.correct), chosen = new Set(response);
      result = { correct: chosen.size === correct.size && [...chosen].every((x) => correct.has(x)),
                 hits: [...chosen].filter((x) => correct.has(x)).length,
                 false_alarms: [...chosen].filter((x) => !correct.has(x)).length };
    } else if (type === "numeric") {
      const v = parseFloat($("#num").value);
      if (Number.isNaN(v)) return (err.textContent = "Please enter a number.");
      if (spec.anchor !== undefined && !screens.task.querySelector("input[name=hl]:checked")) return (err.textContent = "Answer higher/lower first.");
      response = v;
      result = { error: v - task.answer };
      if (spec.anchor !== undefined) result.pulled_toward_anchor = Math.abs(v - spec.anchor) < Math.abs(task.answer - spec.anchor);
    } else if (type === "calibration") {
      const answers = [], confs = [];
      for (let k = 0; k < task.items.length; k++) {
        const el = screens.task.querySelector(`input[name=q${k}]:checked`);
        if (!el) return (err.textContent = `Please answer question ${k + 1}.`);
        answers.push(el.value);
        confs.push(parseFloat(screens.task.querySelector(`input[name=c${k}]`).value) / 100);
      }
      const correct = answers.map((a, k) => a === task.items[k].correct);
      const acc = correct.filter(Boolean).length / correct.length;
      const conf = confs.reduce((s, c) => s + c, 0) / confs.length;
      response = answers.join("");
      result = { accuracy: acc, mean_confidence: conf, overconfidence: conf - acc, n: correct.length };
    }
    state.records.push({ task_id: task.id, bias: task.bias, condition: cond, response, result });
    renderDebrief(task, cond, response, result);
  }

  // ---------------------------------------------------------------- debrief
  function verdict(task, cond, result) {
    const ref = task.reference || {};
    switch (task.bias) {
      case "framing": {
        const other = cond === "gain" ? "loss" : "gain";
        const rate = cond === "gain" ? ref.gain_risky_rate : ref.loss_risky_rate;
        return { cls: "mid", text: `You chose the ${result.risky ? "gamble" : "sure option"} in the ${cond} frame. ${Math.round(rate * 100)}% of the original participants chose the gamble in this frame, vs ${Math.round((cond === "gain" ? ref.loss_risky_rate : ref.gain_risky_rate) * 100)}% in the ${other} frame. Would your choice survive the other wording?` };
      }
      case "anchoring": {
        const med = cond === "low" ? ref.median_low : ref.median_high;
        return result.pulled_toward_anchor
          ? { cls: "bad", text: `Your estimate was pulled toward the random anchor (error ${result.error > 0 ? "+" : ""}${result.error.toFixed(0)} points). The original ${cond}-anchor group's median was ${med}%; the truth is ${task.answer}%.` }
          : { cls: "good", text: `Your estimate was not pulled toward the anchor (error ${result.error > 0 ? "+" : ""}${result.error.toFixed(0)} points). Truth: ${task.answer}%.` };
      }
      case "base_rate_neglect": {
        const e = result.error;
        return Math.abs(e) <= 10
          ? { cls: "good", text: `You answered close to the Bayesian answer (${task.answer}%).` }
          : { cls: "bad", text: `You answered ${e > 0 ? "+" : ""}${e.toFixed(0)} points from the Bayesian answer of ${task.answer}%. The modal answer in the probability format is ${ref.modal_answer_probability}%: the base rate got ignored.` };
      }
      case "overconfidence": {
        const oc = result.overconfidence;
        return { cls: oc > 0.1 ? "bad" : oc < -0.1 ? "mid" : "good",
          text: `Accuracy ${Math.round(result.accuracy * 100)}%, mean confidence ${Math.round(result.mean_confidence * 100)}%: ${oc > 0.1 ? "overconfident" : oc < -0.1 ? "under-confident" : "well calibrated"} by ${Math.round(Math.abs(oc) * 100)} points (typical: +${Math.round(ref.typical_overconfidence * 100)}).` };
      }
      default:
        return result.correct
          ? { cls: "good", text: `Correct. Only about ${Math.round((ref.correct_rate ?? 1 - ref.fallacy_rate) * 100)}% of participants get this right.` }
          : { cls: "bad", text: `That is the intuitive but incorrect answer, shared by about ${Math.round((ref.fallacy_rate ?? 1 - ref.correct_rate) * 100)}% of participants.` };
    }
  }

  function renderDebrief(task, cond, response, result) {
    const b = BIASES[task.bias];
    const v = verdict(task, cond, result);
    let extra = "";
    if (task.bias === "framing") {
      const other = cond === "gain" ? "loss" : "gain";
      extra = `<p><strong>The same problem in the ${other} frame:</strong></p><ul>` +
        task.conditions[other].options.map((o) => `<li>${esc(o.text)}</li>`).join("") + "</ul>";
    }
    screens.debrief.innerHTML = `<p class="kicker">Debrief · ${esc(b.name)}</p><h2>${esc(task.title)}</h2>
      <div class="result ${v.cls}">${esc(v.text)}</div>
      <p>${esc(task.debrief)}</p>${extra}
      <details><summary>What is going on: ${esc(b.name)}</summary><p><strong>Definition.</strong> ${esc(b.definition)}</p>
        <p><strong>Mechanism.</strong> ${esc(b.mechanism)}</p></details>
      <details open><summary>How to guard against it</summary><ul>${b.debiasing.map((d) => `<li>${esc(d)}</li>`).join("")}</ul></details>
      <details><summary>References</summary><ul>${b.references.map((r) => `<li>${esc(r)}</li>`).join("")}</ul></details>
      <p class="muted">Source paradigm: ${esc(task.paradigm)}</p>
      <button class="primary" id="next">${state.i + 1 < TASKS.length ? "Next task" : "See my scorecard"}</button>`;
    $("#next").addEventListener("click", () => { state.i++; state.i < TASKS.length ? renderTask(TASKS[state.i]) : renderSummary(); });
    show("debrief");
  }

  // ---------------------------------------------------------------- summary
  function renderSummary() {
    const rows = state.records.map((r) => {
      const task = TASKS.find((t) => t.id === r.task_id);
      const v = verdict(task, r.condition, r.result);
      const label = v.cls === "good" ? "resisted" : v.cls === "bad" ? "susceptible" : "see note";
      return `<tr><td>${esc(BIASES[r.bias].name)}</td><td><span class="pill ${v.cls}">${label}</span></td><td class="muted">${esc(v.text)}</td></tr>`;
    }).join("");
    const bad = state.records.filter((r) => verdict(TASKS.find((t) => t.id === r.task_id), r.condition, r.result).cls === "bad").length;
    screens.summary.innerHTML = `<p class="kicker">Scorecard</p><h2>Your results</h2>
      <p>You showed the intuitive (biased) response on <strong>${bad}</strong> of ${state.records.length} tasks. That is normal: these effects
      were chosen because they catch most people, including experts. Awareness alone does not remove them, but the techniques in each
      debrief measurably do (see the <code>cogbias debias</code> simulation in the repository).</p>
      <table><thead><tr><th>Bias</th><th>Result</th><th>Note</th></tr></thead><tbody>${rows}</tbody></table>
      <div class="row"><button class="primary" id="download">Download responses (CSV)</button><button id="restart">Start over</button></div>
      <p class="muted">The CSV can be scored with <code>cogbias analyze your_file.csv</code>; pool several people's files to see the group effects.</p>`;
    $("#download").addEventListener("click", downloadCSV);
    $("#restart").addEventListener("click", () => { state.i = 0; state.records = []; show("intro"); });
    show("summary");
  }

  function downloadCSV() {
    const pid = "web-" + Math.random().toString(36).slice(2, 8);
    const lines = ["participant_id,task_id,bias,condition,response,correct,error,overconfidence"];
    for (const r of state.records) {
      const q = (v) => v === undefined || v === null ? "" : `"${String(Array.isArray(v) ? v.join("|") : v).replace(/"/g, '""')}"`;
      lines.push([pid, r.task_id, r.bias, r.condition ?? "", q(r.response), r.result.correct ?? "", r.result.error ?? "", r.result.overconfidence ?? ""].join(","));
    }
    const blob = new Blob([lines.join("\n")], { type: "text/csv" });
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = `cogbias_${pid}.csv`;
    a.click();
  }

  $("#start").addEventListener("click", () => { state.i = 0; state.records = []; renderTask(TASKS[0]); });
})();
