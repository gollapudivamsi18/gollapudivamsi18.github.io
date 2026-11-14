/* Floating portfolio assistant: a small button bottom-right that opens a compact
 * chat panel. Text questions, voice input (Web Speech API, where supported) and
 * optional spoken replies. Answers come only from assets/data/knowledge.json via
 * AssistantCore. Nothing is stored or sent anywhere: the transcript lives in the
 * page and is gone on reload. The knowledge base loads on first open. */
(function () {
  "use strict";
  if (!window.AssistantCore) return;

  var ICON = {
    chat: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M21 12a8 8 0 0 1-11.6 7.1L4 20.5l1.4-4.6A8 8 0 1 1 21 12z"/><path d="M8.5 11h.01M12 11h.01M15.5 11h.01"/></svg>',
    bot: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="4" y="8" width="16" height="11" rx="3"/><path d="M12 4v4M9 13h.01M15 13h.01M9.5 16.5h5"/></svg>',
    speaker: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M11 5L6 9H3v6h3l5 4z"/><path d="M15.5 8.5a5 5 0 0 1 0 7M18.5 5.5a9 9 0 0 1 0 13"/></svg>',
    minimize: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" aria-hidden="true"><path d="M6 12h12"/></svg>',
    close: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" aria-hidden="true"><path d="M6 6l12 12M18 6L6 18"/></svg>',
    mic: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="9" y="3" width="6" height="11" rx="3"/><path d="M5 11a7 7 0 0 0 14 0M12 18v3"/></svg>',
    send: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12h14M13 6l6 6-6 6"/></svg>'
  };

  // Build the widget ------------------------------------------------------------
  var fab = document.createElement("button");
  fab.type = "button";
  fab.className = "ai-fab";
  fab.setAttribute("aria-label", "Open the portfolio assistant");
  fab.setAttribute("aria-expanded", "false");
  fab.setAttribute("aria-controls", "ai-panel");
  fab.innerHTML = ICON.chat + '<span class="ping" aria-hidden="true"></span>';

  var panel = document.createElement("section");
  panel.className = "ai-panel";
  panel.id = "ai-panel";
  panel.hidden = true;
  panel.setAttribute("role", "dialog");
  panel.setAttribute("aria-label", "Portfolio assistant");
  panel.innerHTML =
    '<div class="ai-head"><span class="avatar">' + ICON.bot + '</span>' +
    '<div class="who"><strong>Portfolio Assistant</strong><small>AI · answers from resume &amp; project notes</small></div>' +
    '<button type="button" class="icon-btn" data-act="voice" aria-pressed="false" aria-label="Spoken replies off" title="Spoken replies">' + ICON.speaker + '</button>' +
    '<button type="button" class="icon-btn" data-act="min" aria-label="Minimize assistant" title="Minimize">' + ICON.minimize + '</button>' +
    '<button type="button" class="icon-btn" data-act="close" aria-label="Close and clear conversation" title="Close">' + ICON.close + '</button></div>' +
    '<div class="ai-log" role="log" aria-live="polite" aria-label="Conversation"></div>' +
    '<div class="ai-foot"><form class="ai-form" autocomplete="off">' +
    '<label class="sr-only" for="ai-input">Your question</label>' +
    '<input id="ai-input" type="text" maxlength="300" placeholder="Ask about AKS, CI/CD, SRE…">' +
    '<button type="button" class="icon-btn mic" aria-pressed="false" aria-label="Ask by voice" title="Ask by voice">' + ICON.mic + '</button>' +
    '<button type="submit" class="icon-btn send" aria-label="Send" disabled>' + ICON.send + '</button>' +
    '</form><p class="ai-status" aria-live="polite"></p></div>';

  document.body.appendChild(panel);
  document.body.appendChild(fab);

  var log = panel.querySelector(".ai-log");
  var form = panel.querySelector("form");
  var input = panel.querySelector("#ai-input");
  var micBtn = panel.querySelector(".mic");
  var sendBtn = panel.querySelector(".send");
  var voiceBtn = panel.querySelector('[data-act="voice"]');
  var status = panel.querySelector(".ai-status");

  var synth = window.speechSynthesis || null;
  var Recognition = window.SpeechRecognition || window.webkitSpeechRecognition || null;
  var speakOn = false;       // spoken replies are opt-in
  var recognizer = null, listening = false;
  var convo = null, loading = null;

  function setStatus(t) { status.textContent = t || ""; }

  // Messages ------------------------------------------------------------------------
  var LINKS = [
    [/Projects page/g, "projects.html"],
    [/Resume page/g, "resume.html"],
    [/linkedin\.com\/in\/vamsikrishna-gollapudi/g, "https://www.linkedin.com/in/vamsikrishna-gollapudi"],
    [/github\.com\/gollapudivamsi18/g, "https://github.com/gollapudivamsi18"]
  ];
  function appendWithLinks(el, text) {
    var parts = [{ t: text }];
    LINKS.forEach(function (pair) {
      var next = [];
      parts.forEach(function (p) {
        if (p.href) { next.push(p); return; }
        var last = 0, m, re = new RegExp(pair[0].source, "g");
        while ((m = re.exec(p.t))) {
          if (m.index > last) next.push({ t: p.t.slice(last, m.index) });
          next.push({ t: m[0], href: pair[1] });
          last = m.index + m[0].length;
        }
        if (last < p.t.length) next.push({ t: p.t.slice(last) });
      });
      parts = next;
    });
    parts.forEach(function (p) {
      if (p.href) {
        var a = document.createElement("a");
        a.href = p.href;
        a.textContent = p.t;
        if (/^https:/.test(p.href)) { a.target = "_blank"; a.rel = "noopener"; }
        el.appendChild(a);
      } else {
        el.appendChild(document.createTextNode(p.t));
      }
    });
  }
  function addMessage(who, text, suggestions) {
    var div = document.createElement("div");
    div.className = "msg " + who;
    appendWithLinks(div, text);
    log.appendChild(div);
    var old = log.querySelectorAll(".suggestions");
    for (var i = 0; i < old.length; i++) old[i].remove();
    if (suggestions && suggestions.length) {
      var wrap = document.createElement("div");
      wrap.className = "suggestions";
      suggestions.forEach(function (s) {
        var b = document.createElement("button");
        b.type = "button";
        b.textContent = s.label;
        b.addEventListener("click", function () { handle({ topic: s.id }, s.label); });
        wrap.appendChild(b);
      });
      log.appendChild(wrap);
    }
    log.scrollTop = log.scrollHeight;
  }

  function speak(text) {
    if (!speakOn || !synth) return;
    synth.cancel();
    var u = new SpeechSynthesisUtterance(text.replace(/\n- /g, ". ").replace(/\n\d+\. /g, ". "));
    var voices = synth.getVoices();
    var v = voices.filter(function (x) { return /^en[-_]IN$/i.test(x.lang); })[0] ||
            voices.filter(function (x) { return /^en[-_]/i.test(x.lang); })[0];
    if (v) { u.voice = v; u.lang = v.lang; } else { u.lang = "en-IN"; }
    synth.speak(u);
  }

  function handle(question, shown) {
    if (!convo) return;
    addMessage("user", shown || question);
    var reply = convo.ask(question);
    addMessage("bot", reply.text + (reply.hasMore ? "\n\nAsk “tell me more” for detail." : ""), reply.suggestions);
    speak(reply.text);
  }

  function greet() {
    addMessage("bot", "Hi! I'm an AI assistant for Vamsikrishna's portfolio, not Vamsikrishna himself. I answer from his resume and project notes: Azure DevOps, SRE, Azure infrastructure, Windows and Linux administration. What would you like to know?",
      convo ? convo.suggest(null) : []);
  }

  function loadKb() {
    if (loading) return loading;
    setStatus("Loading…");
    loading = fetch("assets/data/knowledge.json", { cache: "no-cache" })
      .then(function (r) { if (!r.ok) throw new Error(r.status); return r.json(); })
      .then(function (kb) {
        convo = new window.AssistantCore.Conversation(kb);
        sendBtn.disabled = false;
        setStatus("");
        greet();
      })
      .catch(function () {
        loading = null;
        setStatus("");
        addMessage("bot", "Sorry, my notes could not be loaded. The Resume page has the same information.");
      });
    return loading;
  }

  // Open / minimize / close ---------------------------------------------------------
  function open() {
    panel.hidden = false;
    fab.setAttribute("aria-expanded", "true");
    fab.setAttribute("aria-label", "Minimize the portfolio assistant");
    loadKb();
    setTimeout(function () { input.focus(); }, 30);
  }
  function minimize() {
    panel.hidden = true;
    fab.setAttribute("aria-expanded", "false");
    fab.setAttribute("aria-label", "Open the portfolio assistant");
    if (listening && recognizer) recognizer.abort();
    fab.focus();
  }
  function closeAndClear() {
    if (synth) synth.cancel();
    minimize();
    log.innerHTML = "";
    if (convo) { convo.reset(); greet(); }
    setStatus("");
  }
  fab.addEventListener("click", function () { if (panel.hidden) open(); else minimize(); });
  panel.querySelector('[data-act="min"]').addEventListener("click", minimize);
  panel.querySelector('[data-act="close"]').addEventListener("click", closeAndClear);
  panel.addEventListener("keydown", function (e) { if (e.key === "Escape") { e.stopPropagation(); minimize(); } });
  document.querySelectorAll("[data-open-assistant]").forEach(function (el) {
    el.addEventListener("click", function (e) { e.preventDefault(); open(); });
  });

  form.addEventListener("submit", function (e) {
    e.preventDefault();
    var q = input.value.trim();
    if (!q) { setStatus("Type a question first."); return; }
    input.value = "";
    setStatus("");
    handle(q);
  });

  voiceBtn.addEventListener("click", function () {
    if (!synth) { setStatus("This browser can't speak replies. Text answers still work."); return; }
    speakOn = !speakOn;
    voiceBtn.setAttribute("aria-pressed", String(speakOn));
    voiceBtn.setAttribute("aria-label", speakOn ? "Spoken replies on" : "Spoken replies off");
    if (!speakOn) synth.cancel();
    setStatus(speakOn ? "Spoken replies on." : "Spoken replies off.");
  });

  // Voice input -----------------------------------------------------------------------
  if (!Recognition) {
    micBtn.disabled = true;
    micBtn.title = "Voice input isn't supported in this browser";
  } else {
    micBtn.addEventListener("click", function () {
      if (listening) { recognizer.stop(); return; }
      recognizer = new Recognition();
      recognizer.lang = "en-IN";
      recognizer.interimResults = true;
      recognizer.maxAlternatives = 1;
      var finalText = "";
      recognizer.onstart = function () {
        listening = true;
        micBtn.classList.add("listening");
        micBtn.setAttribute("aria-pressed", "true");
        micBtn.setAttribute("aria-label", "Stop listening");
        setStatus("Listening… ask your question.");
      };
      recognizer.onresult = function (ev) {
        var interim = "";
        for (var i = ev.resultIndex; i < ev.results.length; i++) {
          if (ev.results[i].isFinal) finalText += ev.results[i][0].transcript;
          else interim += ev.results[i][0].transcript;
        }
        input.value = (finalText + interim).trim();
      };
      recognizer.onerror = function (ev) {
        setStatus({
          "not-allowed": "Microphone permission was denied. You can type instead.",
          "service-not-allowed": "Voice input is blocked in this browser. Please type.",
          "no-speech": "I didn't hear anything. Try again or type.",
          "audio-capture": "No microphone found. Please type.",
          "network": "Voice input needs a network connection here. Please type."
        }[ev.error] || "Voice input stopped. Please type instead.");
      };
      recognizer.onend = function () {
        listening = false;
        micBtn.classList.remove("listening");
        micBtn.setAttribute("aria-pressed", "false");
        micBtn.setAttribute("aria-label", "Ask by voice");
        var q = input.value.trim();
        if (finalText.trim() && q && convo) { input.value = ""; setStatus(""); handle(q); }
        else if (status.textContent.indexOf("Listening") === 0) setStatus("");
      };
      try { recognizer.start(); } catch (err) { setStatus("Couldn't start voice input. Please type."); }
    });
  }
})();
