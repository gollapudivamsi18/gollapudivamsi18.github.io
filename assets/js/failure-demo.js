/* UI for the CI/CD failure analysis prototype (homepage, #failure-demo).
 * Uses FailureAnalyzer (deterministic rules). Builds all output with
 * textContent, so pasted logs are never interpreted as HTML. */
(function () {
  "use strict";
  var root = document.getElementById("failure-demo");
  if (!root || !window.FailureAnalyzer) return;
  var A = window.FailureAnalyzer;
  var select = document.getElementById("fa-sample");
  var log = document.getElementById("fa-log");
  var run = document.getElementById("fa-run");
  var out = document.getElementById("fa-out");

  A.SAMPLES.forEach(function (s) {
    var o = document.createElement("option");
    o.value = s.id; o.textContent = s.title;
    select.appendChild(o);
  });
  var custom = document.createElement("option");
  custom.value = "custom"; custom.textContent = "My own log (paste below)";
  select.appendChild(custom);

  function load(id) {
    var s = A.SAMPLES.filter(function (x) { return x.id === id; })[0];
    log.value = s ? s.log : "";
    if (!s) log.focus();
  }
  select.addEventListener("change", function () { load(select.value); });
  log.addEventListener("input", function () {
    var s = A.SAMPLES.filter(function (x) { return x.id === select.value; })[0];
    if (s && log.value !== s.log) select.value = "custom";
  });
  load(A.SAMPLES[0].id);

  function el(tag, cls, text) {
    var e = document.createElement(tag);
    if (cls) e.className = cls;
    if (text != null) e.textContent = text;
    return e;
  }

  // Render `code` spans written with backticks in rule steps, safely.
  function withCode(parent, text) {
    String(text).split("`").forEach(function (part, i) {
      parent.appendChild(i % 2 ? el("code", null, part) : document.createTextNode(part));
    });
    return parent;
  }

  function render(r) {
    out.textContent = "";
    if (r.status === "empty") { out.appendChild(el("p", "fa-empty", r.summary)); return; }

    var head = el("div", "fa-result-head");
    head.appendChild(el("span", "fa-cat " + (r.status === "matched" ? "hit" : "miss"), r.category));
    head.appendChild(el("strong", null, r.label));
    out.appendChild(head);

    var dl = el("dl", "fa-facts");
    [["Failing step", r.failingStep], ["First error", r.errorLine], ["Exit code", r.exitCode], ["Matched rule", r.matchedLine]]
      .forEach(function (pair) {
        if (pair[1] == null || pair[1] === "") return;
        dl.appendChild(el("dt", null, pair[0]));
        dl.appendChild(el("dd", null, String(pair[1])));
      });
    out.appendChild(dl);

    out.appendChild(el("p", "fa-summary", r.summary));
    out.appendChild(el("p", "fa-label", "Suggested troubleshooting"));
    var ol = el("ol", "fa-steps");
    r.steps.forEach(function (s) { ol.appendChild(withCode(el("li"), s)); });
    out.appendChild(ol);

    var review = el("div", "fa-review");
    review.appendChild(el("p", null, "Human review required: nothing runs until an engineer approves."));
    var btns = el("div", "fa-review-btns");
    var ok = el("button", "btn btn-sm fa-approve", "Approve plan");
    var no = el("button", "btn btn-ghost btn-sm", "Reject");
    ok.type = no.type = "button";
    var note = el("p", "fa-note");
    note.setAttribute("role", "status");
    ok.addEventListener("click", function () {
      note.textContent = "Approved in this page only. Nothing is executed; the fix would go through a normal pull request and pipeline run.";
      ok.disabled = no.disabled = true;
    });
    no.addEventListener("click", function () {
      note.textContent = "Rejected. The engineer investigates manually from the first error line.";
      ok.disabled = no.disabled = true;
    });
    btns.appendChild(ok); btns.appendChild(no);
    review.appendChild(btns); review.appendChild(note);
    out.appendChild(review);
  }

  run.addEventListener("click", function () { render(A.analyse(log.value)); });
})();
