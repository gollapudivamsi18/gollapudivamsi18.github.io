/* Browser UI for the portfolio assistant: chat log, text input, voice input
 * (Web Speech API speech recognition), spoken replies (speech synthesis),
 * stop, mute and clear. Nothing is stored: the transcript lives in the page
 * and is gone on reload. No network calls except loading knowledge.json. */
(function () {
  "use strict";
  var root = document.getElementById("assistant");
  if (!root || !window.AssistantCore) return;

  var log = root.querySelector(".log");
  var form = root.querySelector("form");
  var input = root.querySelector("#assistant-input");
  var micBtn = root.querySelector("#assistant-mic");
  var muteBtn = root.querySelector("#assistant-mute");
  var stopBtn = root.querySelector("#assistant-stop");
  var clearBtn = root.querySelector("#assistant-clear");
  var status = root.querySelector(".assistant-status");

  var synth = window.speechSynthesis || null;
  var Recognition = window.SpeechRecognition || window.webkitSpeechRecognition || null;
  var muted = true;          // spoken replies are opt-in
  var recognizer = null;
  var listening = false;
  var convo = null;

  function setStatus(text) { status.textContent = text || ""; }

  function addMessage(who, text, suggestions) {
    var div = document.createElement("div");
    div.className = "msg " + who;
    if (who === "bot") div.setAttribute("aria-label", "Assistant");
    // Text only (no HTML injection): links are rendered for known site pages.
    appendWithLinks(div, text);
    log.appendChild(div);
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

  var LINKS = [
    [/Projects page/g, "projects.html"],
    [/Resume page/g, "resume.html"],
    [/linkedin\.com\/in\/vamsikrishna-gollapudi/g, "https://www.linkedin.com/in/vamsikrishna-gollapudi"],
    [/github\.com\/gollapudivamsi18/g, "https://github.com/gollapudivamsi18"],
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

  function speak(text) {
    if (muted || !synth) return;
    synth.cancel();
    var u = new SpeechSynthesisUtterance(text.replace(/\n- /g, ". ").replace(/\n\d+\. /g, ". "));
    var voices = synth.getVoices();
    var voice = voices.filter(function (v) { return /^en[-_]IN$/i.test(v.lang); })[0] ||
                voices.filter(function (v) { return /^en[-_]/i.test(v.lang); })[0];
    if (voice) { u.voice = voice; u.lang = voice.lang; } else { u.lang = "en-IN"; }
    u.rate = 1;
    u.onstart = function () { stopBtn.disabled = false; };
    u.onend = u.onerror = function () { stopBtn.disabled = true; };
    synth.speak(u);
  }

  function handle(question, shownText) {
    if (!convo) return;
    addMessage("user", shownText || question);
    var reply = convo.ask(question);
    var text = reply.text + (reply.hasMore ? "\n\n(Ask “tell me more” for detail.)" : "");
    addMessage("bot", text, reply.suggestions);
    speak(reply.text);
  }

  form.addEventListener("submit", function (e) {
    e.preventDefault();
    var q = input.value.trim();
    if (!q) { setStatus("Type a question first."); return; }
    input.value = "";
    setStatus("");
    handle(q);
  });

  muteBtn.addEventListener("click", function () {
    if (!synth) { setStatus("This browser cannot speak replies. Text answers still work."); return; }
    muted = !muted;
    muteBtn.setAttribute("aria-pressed", String(!muted));
    muteBtn.textContent = muted ? "Voice replies: off" : "Voice replies: on";
    if (muted) { synth.cancel(); stopBtn.disabled = true; }
    setStatus(muted ? "Spoken replies turned off." : "Spoken replies turned on.");
  });

  stopBtn.addEventListener("click", function () {
    if (synth) synth.cancel();
    stopBtn.disabled = true;
    setStatus("Stopped speaking.");
  });

  clearBtn.addEventListener("click", function () {
    if (synth) synth.cancel();
    log.innerHTML = "";
    if (convo) convo.reset();
    greet();
    setStatus("Conversation cleared.");
  });

  // Voice input --------------------------------------------------------------
  if (!Recognition) {
    micBtn.disabled = true;
    micBtn.title = "Voice input is not supported in this browser";
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
        micBtn.textContent = "Stop listening";
        setStatus("Listening… speak your question.");
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
        var msg = {
          "not-allowed": "Microphone permission was denied. You can allow it in the browser's site settings, or type instead.",
          "service-not-allowed": "Voice input is blocked in this browser. Please type instead.",
          "no-speech": "I didn't hear anything. Try again, or type your question.",
          "audio-capture": "No microphone was found. Please type instead.",
          "network": "Voice recognition needs a network connection in this browser. Please type instead."
        }[ev.error] || "Voice input stopped (" + ev.error + "). Please type instead.";
        setStatus(msg);
      };
      recognizer.onend = function () {
        listening = false;
        micBtn.classList.remove("listening");
        micBtn.setAttribute("aria-pressed", "false");
        micBtn.textContent = "Speak";
        var q = input.value.trim();
        if (finalText.trim() && q) { input.value = ""; setStatus(""); handle(q); }
      };
      try {
        recognizer.start();   // the browser shows its own microphone permission prompt
      } catch (err) {
        setStatus("Could not start voice input. Please type instead.");
      }
    });
  }

  function greet() {
    addMessage("bot", "Hello. I'm Vamsikrishna's Portfolio AI Assistant, an AI that answers from his resume and project notes, not Vamsikrishna himself. What would you like to know?",
      convo ? convo.suggest(null) : []);
  }

  fetch("assets/data/knowledge.json", { cache: "no-cache" })
    .then(function (r) { if (!r.ok) throw new Error(r.status); return r.json(); })
    .then(function (kb) {
      convo = new window.AssistantCore.Conversation(kb);
      root.querySelectorAll("[data-needs-kb]").forEach(function (el) { el.disabled = false; });
      greet();
    })
    .catch(function () {
      addMessage("bot", "Sorry, the assistant's notes could not be loaded. The rest of the page has the same information, and the Resume page has the full details.");
    });
})();
