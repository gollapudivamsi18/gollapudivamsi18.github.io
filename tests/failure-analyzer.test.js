// Tests for the CI/CD failure analysis prototype. Run: node tests/failure-analyzer.test.js
"use strict";
const assert = require("assert");
const path = require("path");
const A = require(path.join(__dirname, "..", "assets", "js", "failure-analyzer.js"));
let passed = 0;
function test(name, fn) { fn(); passed += 1; console.log("ok -", name); }

test("each synthetic sample is classified by the expected rule", () => {
  const expected = { tests: "test-failure", terraform: "tf-state-lock", helm: "image-pull", trivy: "vuln-gate" };
  for (const s of A.SAMPLES) {
    const r = A.analyse(s.log);
    assert.strictEqual(r.status, "matched", s.id);
    assert.strictEqual(r.ruleId, expected[s.id], `${s.id} -> ${r.ruleId}`);
    assert.strictEqual(r.exitCode, 1, `${s.id} exit code`);
    assert.ok(r.failingStep, `${s.id} failing step`);
    assert.ok(r.steps.length >= 3, `${s.id} steps`);
  }
});

test("extracts the Azure Pipelines step and quoted exit code", () => {
  const r = A.analyse("##[section]Starting: Build\n##[error]No space left on device\n##[error]Bash exited with code '137'.");
  assert.strictEqual(r.ruleId, "disk-quota");
  assert.strictEqual(r.failingStep, "Build");
  assert.strictEqual(r.exitCode, 137);
});

test("other rules: auth, helm timeout, secrets, dependency", () => {
  assert.strictEqual(A.analyse("Error: building AzureRM Client: AADSTS700016").ruleId, "tf-auth");
  assert.strictEqual(A.analyse("Error: UPGRADE FAILED: timed out waiting for the condition").ruleId, "helm-timeout");
  assert.strictEqual(A.analyse("WRN leaks found: 1").ruleId, "secret-leak");
  assert.strictEqual(A.analyse("ERROR: No matching distribution found for requests==9.9.9").ruleId, "dependency");
});

test("unknown and empty logs are not guessed", () => {
  const u = A.analyse("Run ./deploy.sh\nsomething odd happened\nexit status 3");
  assert.strictEqual(u.status, "unknown");
  assert.strictEqual(u.exitCode, 3);
  assert.match(u.summary, /no fix is suggested/);
  assert.strictEqual(A.analyse("   ").status, "empty");
});

test("a passing run with '0 failed' is not reported as an error line", () => {
  const r = A.analyse("Run pytest\n12 passed, 0 failed\nError: Process completed with exit code 1.");
  assert.match(r.errorLine, /Process completed/);
});

console.log(`\n${passed} test groups passed`);
