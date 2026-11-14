// Tests for the assistant engine. Run: node tests/assistant.test.js
// Uses only Node's built-in assert; exits non-zero on the first failure.
"use strict";
const assert = require("assert");
const path = require("path");
const fs = require("fs");
const { Conversation } = require(path.join(__dirname, "..", "assets", "js", "assistant-core.js"));

const kb = JSON.parse(fs.readFileSync(path.join(__dirname, "..", "assets", "data", "knowledge.json"), "utf8"));
let passed = 0;
function test(name, fn) {
  fn();
  passed += 1;
  console.log("ok -", name);
}

test("routes recruiter questions to the right topic", () => {
  const cases = {
    "Is he open to hybrid roles?": "availability",
    "What is his notice period": "availability",
    "Which certifications does he have?": "certifications",
    "Tell me about his Kubernetes experience": "aks",
    "How does he handle incidents and error budgets?": "sre",
    "What CI/CD tools has he used?": "azure-devops",
    "Has he done Terraform?": "terraform",
    "What does he do at Nexamatic?": "nexamatic",
    "What did he do at UST Global?": "ust",
    "Windows Server and Active Directory": "windows",
    "Any RHEL experience?": "linux",
    "What projects are in the portfolio?": "projects",
    "Explain the DevSecOps demo with Trivy": "devsecops-demo",
    "How can I contact him on LinkedIn?": "contact",
    "Are you a real person?": "assistant",
    "What is his education?": "education",
    "Azure Migrate and Site Recovery work": "migration",
    "Is he a frontend developer?": "identity",
    "Does he do UI/UX design?": "identity",
    "Explain the Terraform hub and spoke demo": "hub-spoke-demo",
    "How does the burn-rate alerting project work?": "sre-demo",
  };
  for (const [q, id] of Object.entries(cases)) {
    const r = new Conversation(kb).ask(q);
    assert.strictEqual(r.topic, id, `"${q}" -> ${r.topic}, expected ${id}`);
  }
});

test("follow-ups continue the current topic and walk through extra detail", () => {
  const c = new Conversation(kb);
  const first = c.ask("Tell me about his SRE work");
  assert.strictEqual(first.topic, "sre");
  assert.ok(first.hasMore);
  const second = c.ask("tell me more");
  assert.strictEqual(second.topic, "sre");
  assert.notStrictEqual(second.text, first.text);
  const third = c.ask("go on");
  assert.strictEqual(third.topic, "sre");
  const fourth = c.ask("more");
  assert.match(fourth.text, /everything I have/);
});

test("pronoun follow-up stays on topic", () => {
  const c = new Conversation(kb);
  c.ask("What about Kubernetes?");
  const r = c.ask("How did he do that?");
  assert.strictEqual(r.topic, "aks");
});

test("a new subject switches topic even mid-conversation", () => {
  const c = new Conversation(kb);
  c.ask("Tell me about his SRE work");
  assert.strictEqual(c.ask("And his certifications?").topic, "certifications");
});

test("suggestion chips select a topic directly", () => {
  const c = new Conversation(kb);
  assert.strictEqual(c.ask({ topic: "aks-demo" }).topic, "aks-demo");
});

test("unknown questions get the honest fallback, not a guess", () => {
  const r = new Conversation(kb).ask("What is his favourite cricket team?");
  assert.strictEqual(r.topic, null);
  assert.match(r.text, /won't guess/);
});

test("identity: never presented as a frontend or UI/UX professional", () => {
  const all = JSON.stringify(kb);
  assert.ok(!/(is|as) an? (frontend|front-end|ui\/ux|web) (developer|designer|engineer)/i.test(all.replace(/not seeking[^.]*\./gi, "")));
  const r = new Conversation(kb).ask("Is he a web designer?");
  assert.match(r.text, /^No\./);
});

test("only the four retained projects are described", () => {
  const ids = kb.topics.map((t) => t.id);
  for (const gone of ["banking-demo", "migration-demo", "server-ops-demo", "patching-demo"]) {
    assert.ok(!ids.includes(gone), `${gone} should be removed`);
  }
  assert.match(new Conversation(kb).ask("What projects are in the portfolio?").text, /four featured projects/);
});

test("small talk", () => {
  const c = new Conversation(kb);
  assert.match(c.ask("Hello").text, /AI assistant for Vamsikrishna/);
  assert.match(c.ask("thanks").text, /welcome/);
  assert.strictEqual(c.ask("").topic, null);
});

test("knowledge base integrity", () => {
  const ids = new Set(kb.topics.map((t) => t.id));
  assert.strictEqual(ids.size, kb.topics.length, "duplicate topic ids");
  for (const t of kb.topics) {
    assert.ok(t.answer && t.keywords.length, `topic ${t.id} incomplete`);
    for (const r of t.related) assert.ok(ids.has(r), `topic ${t.id} links to missing ${r}`);
  }
  const all = JSON.stringify(kb);
  // Never claim past jobs were remote, never invent a Naukri URL, no skill percentages.
  assert.ok(!/naukri\.com\//i.test(all), "Naukri URL must not be invented");
  assert.ok(!/\d+% (proficien|expert|skill)/i.test(all), "no skill percentages");
  assert.ok(!/worked remotely|remote role at|fully remote at/i.test(all), "past roles must not be called remote");
});

console.log(`\n${passed} test groups passed`);
