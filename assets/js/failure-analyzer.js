/* CI/CD failure analysis prototype for the portfolio.
 *
 * Deterministic rules only: no AI model, no network calls, no API keys.
 * It reads a pipeline log, finds the failing step and the first error line,
 * matches the log against known failure patterns and returns a category,
 * a short summary and suggested troubleshooting steps for a human to review.
 * Runs in the browser and in Node (tests/failure-analyzer.test.js).
 */
(function (root, factory) {
  if (typeof module === "object" && module.exports) module.exports = factory();
  else root.FailureAnalyzer = factory();
})(typeof self !== "undefined" ? self : this, function () {
  "use strict";

  // Ordered: the first rule whose pattern matches wins, so specific rules come first.
  var RULES = [
    {
      id: "tf-state-lock", category: "Infrastructure as Code", label: "Terraform state lock",
      pattern: /Error acquiring the state lock|state blob is already locked|ConditionalCheckFailed/i,
      summary: "Terraform could not lock the remote state, so another run (or a crashed one) still holds the lease.",
      steps: [
        "Check whether another pipeline run or engineer is applying the same workspace right now.",
        "If the holder is gone, note the Lock ID and release it with `terraform force-unlock <LOCK_ID>` after team agreement.",
        "Add a pipeline concurrency limit per environment so two applies cannot overlap."
      ]
    },
    {
      id: "tf-auth", category: "Infrastructure as Code", label: "Azure authentication for Terraform",
      pattern: /AADSTS\d+|AuthorizationFailed|does not have authorization to perform action|building AzureRM Client/i,
      summary: "The pipeline identity could not authenticate to Azure or lacks the RBAC role for this action.",
      steps: [
        "Check the service connection or workload identity federation subject matches this branch or environment.",
        "Confirm the identity has the least-privilege role on the target scope (for example Contributor on the resource group).",
        "Look for an expired client secret if the connection is not using federation."
      ]
    },
    {
      id: "image-pull", category: "Deployment", label: "Image pull failure on AKS",
      pattern: /ImagePullBackOff|ErrImagePull|manifest unknown|unauthorized: authentication required/i,
      summary: "Pods could not pull the container image, so the rollout never became ready.",
      steps: [
        "Confirm the image tag in the Helm values exists in ACR (`az acr repository show-tags`).",
        "Check that the AKS kubelet identity has AcrPull on the registry.",
        "Because the upgrade used `--atomic`, Helm has rolled back; redeploy once the tag is fixed."
      ]
    },
    {
      id: "helm-timeout", category: "Deployment", label: "Helm upgrade timed out",
      pattern: /timed out waiting for the condition|context deadline exceeded|UPGRADE FAILED/i,
      summary: "The Helm release did not become healthy before the timeout.",
      steps: [
        "Inspect the new pods: `kubectl describe pod` and `kubectl logs --previous` for crash loops or failing probes.",
        "Compare readiness probe settings with the app start-up time.",
        "Check resource requests against free node capacity (pending pods)."
      ]
    },
    {
      id: "vuln-gate", category: "Security gate", label: "Vulnerability scan blocked the build",
      pattern: /(CRITICAL|HIGH):\s*[1-9]|Total: \d+ \((?:[^)]*)(HIGH|CRITICAL): [1-9]|CVE-\d{4}-\d+/,
      summary: "The image or dependency scan found HIGH or CRITICAL vulnerabilities above the gate threshold.",
      steps: [
        "Open the scan report and list each CVE with its package and fixed version.",
        "Upgrade the base image or package to the fixed version and rebuild.",
        "If no fix exists, record a time-boxed exception with a security owner; do not lower the gate."
      ]
    },
    {
      id: "secret-leak", category: "Security gate", label: "Secret detected in the change",
      pattern: /leaks? found|gitleaks.*(found|detected)|secret detected|Finding:.*(key|token|password)/i,
      summary: "Secret scanning found a credential-like value in the commit.",
      steps: [
        "Treat the value as exposed: rotate it at the source first.",
        "Remove it from the code and history, and move it to Key Vault or pipeline secrets.",
        "If it is a false positive, add a reviewed allow-list entry rather than disabling the scan."
      ]
    },
    {
      id: "test-failure", category: "Build & test", label: "Unit tests failed",
      pattern: /FAILED \(|AssertionError|\d+ failed|Tests? failed|FAIL:/i,
      summary: "One or more automated tests failed, so the pipeline stopped before packaging.",
      steps: [
        "Run the failing test locally with the same version of the runtime.",
        "Read the assertion: compare expected and actual values to see whether code or test data changed.",
        "Check whether the test is flaky (passes on re-run) before changing code; quarantine flaky tests with an owner."
      ]
    },
    {
      id: "dependency", category: "Build & test", label: "Dependency could not be resolved",
      pattern: /No matching distribution found|Could not resolve|ERESOLVE|404 Not Found.*(package|npm|pypi)|unable to find package/i,
      summary: "A package version could not be downloaded or resolved from the feed.",
      steps: [
        "Check that the pinned version exists in the feed (Azure Artifacts, npm or PyPI).",
        "Confirm the pipeline can reach the feed and has a valid feed credential.",
        "Use a lock file so builds resolve the same versions every time."
      ]
    },
    {
      id: "disk-quota", category: "Agent / runner", label: "Build agent ran out of resources",
      pattern: /No space left on device|OOMKilled|exit code 137|out of memory/i,
      summary: "The build agent ran out of disk or memory.",
      steps: [
        "Clean the workspace and Docker cache between runs, or use a fresh hosted agent.",
        "Check for large artefacts or layers produced by this change.",
        "Size self-hosted agents for the heaviest job, or split the job."
      ]
    }
  ];

  var STEP_PATTERNS = [
    /##\[section\]Starting:\s*(.+)/,           // Azure Pipelines
    /^\s*Run\s+(.+)$/,                         // GitHub Actions
    /^\s*Step\s+\d+\/\d+\s*:\s*(.+)$/i,        // Docker build
    /^\s*>\s*Task\s*:\s*(.+)$/                 // generic
  ];
  var ERROR_LINE = /(##\[error\]|\berror\b|\bfailed\b|\bfatal\b|Error:|FAIL)/i;
  var EXIT = /(?:exit(?:ed)? (?:with )?code|exit status)\s*'?(\d+)/i;

  function analyse(log) {
    var text = String(log || "");
    var lines = text.split(/\r?\n/);
    var step = null, errorLine = null, errorIndex = -1, exitCode = null;

    lines.forEach(function (line, i) {
      STEP_PATTERNS.forEach(function (re) {
        var m = line.match(re);
        if (m && errorIndex < 0) step = m[1].trim();
      });
      if (errorIndex < 0 && ERROR_LINE.test(line) && !/0 failed|0 errors?/i.test(line)) {
        errorLine = line.replace(/^.*##\[error\]/, "").trim();
        errorIndex = i;
      }
      var e = line.match(EXIT);
      if (e) exitCode = Number(e[1]);
    });

    var rule = null, matched = null;
    for (var r = 0; r < RULES.length && !rule; r++) {
      for (var i = 0; i < lines.length; i++) {
        if (RULES[r].pattern.test(lines[i])) { rule = RULES[r]; matched = lines[i].trim(); break; }
      }
    }

    if (!text.trim()) {
      return { status: "empty", summary: "Paste a pipeline log to analyse.", steps: [] };
    }
    if (!rule) {
      return {
        status: "unknown", category: "Unclassified", label: "No known pattern matched",
        failingStep: step, errorLine: errorLine, exitCode: exitCode, matchedLine: null,
        summary: "None of the rules recognise this failure, so no fix is suggested. An engineer should read the log from the first error line.",
        steps: ["Start at the first error line shown above and the step that ran just before it.",
                "Re-run once to rule out a transient agent or network issue.",
                "If it is a new failure type, add a rule for it after the root cause is known."]
      };
    }
    return {
      status: "matched", ruleId: rule.id, category: rule.category, label: rule.label,
      failingStep: step, errorLine: errorLine, exitCode: exitCode, matchedLine: matched,
      summary: rule.summary, steps: rule.steps.slice()
    };
  }

  // Synthetic logs written for this demo; they do not come from any real system.
  var SAMPLES = [
    { id: "tests", title: "Unit tests (GitHub Actions)", log: [
      "Run python -m unittest -v",
      "test_health (test_app.HealthTests) ... ok",
      "test_slots_capacity (test_app.SlotTests) ... FAIL",
      "======================================================================",
      "FAIL: test_slots_capacity (test_app.SlotTests)",
      "AssertionError: 12 != 10 : capacity must not exceed clinic limit",
      "----------------------------------------------------------------------",
      "Ran 14 tests in 0.21s",
      "FAILED (failures=1)",
      "Error: Process completed with exit code 1."].join("\n") },
    { id: "terraform", title: "Terraform apply (Azure Pipelines)", log: [
      "##[section]Starting: Terraform apply (dev)",
      "Acquiring state lock. This may take a few moments...",
      "##[error]Error: Error acquiring the state lock",
      "Error message: state blob is already locked",
      "Lock Info:",
      "  ID:        6f1c2a9e-0000-4a1b-9c3d-example",
      "  Operation: OperationTypeApply",
      "  Who:       pipeline@agent-02",
      "##[error]Bash exited with code '1'."].join("\n") },
    { id: "helm", title: "Helm deploy to AKS (Azure Pipelines)", log: [
      "##[section]Starting: Helm upgrade staging",
      "helm upgrade --install demo ./chart --atomic --timeout 5m",
      "Warning  Failed  kubelet  Failed to pull image \"demoacr.azurecr.io/clinic-slots:1.4.2\": manifest unknown",
      "Warning  Failed  kubelet  Error: ImagePullBackOff",
      "Error: UPGRADE FAILED: release demo failed, and has been rolled back due to atomic being set: timed out waiting for the condition",
      "##[error]Helm exited with code '1'."].join("\n") },
    { id: "trivy", title: "Image scan gate (GitHub Actions)", log: [
      "Run aquasecurity/trivy-action",
      "demo-api:sha-1a2b3c (debian 12.5)",
      "Total: 3 (HIGH: 2, CRITICAL: 1)",
      "libssl3  CVE-2024-0000  CRITICAL  fixed in 3.0.14-1",
      "zlib1g   CVE-2023-0000  HIGH      fixed in 1:1.2.13",
      "Error: Process completed with exit code 1."].join("\n") }
  ];

  return { analyse: analyse, RULES: RULES, SAMPLES: SAMPLES };
});
