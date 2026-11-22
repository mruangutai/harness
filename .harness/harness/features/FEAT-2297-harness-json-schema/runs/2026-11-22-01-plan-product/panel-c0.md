# FEAT-2297 reader fan-in — cycle 0

All three readers ran; no mission downgrade finding. PM applies task-scoped findings without another reader cycle. Source notes: ../../notes/review-harness-code-reviewer-plan-c0.md and ../../notes/review-harness-ui-reviewer-plan-c0.md. The should-not-exist reader is read-only; its full findings are transcribed below from terminal output.

Host assessment: prefer the existing config-independent governed-command recognizers over a new repair-command allowlist. Source confirms gh-close denies(cmd), branch _branch_name(cmd), and merge command recognition do not require config. Deny governed actions with the loader diagnosis; irrelevant commands may pass without loading config. This reconciles code-reviewer's acceptance of repair reachability with should-not-exist's smaller design, without weakening missing/invalid-config refusal for governed actions. PM must preserve compound-command coverage. Resolve sequencing by producing local cumulative proof before external merge; earlier PR preparation is optional but not a reason to delay local proof. Smoke's actual current validity is researchable, not operator-only; do not broaden its explicitly excluded migration/removal scope. Generated shared TS fixture may satisfy the one-builder requirement with regeneration/census proof, without per-test Python process spawning.

```yaml
DIGEST:
  severity_max: high
  readers:
    - reader: scope
      status: ran
      persona: harness-code-reviewer
      reason: Pending plan scope and architecture reviewed; source note notes/review-harness-code-reviewer-plan-c0.md.
    - reader: should-not-exist
      status: ran
      persona: fable-advisor
      reason: Independent critique completed; seven task-scoped findings transcribed from terminal result.
    - reader: design
      status: ran
      persona: harness-ui-reviewer
      reason: Self-scoped out after review; no visual or interaction surface, DESIGN and prototype unnecessary subject to operator override.
  findings:
    - reader: harness-code-reviewer
      summary: T-10 offline cumulative proof unnecessarily waits for the external Kaya merge.
      severity: med
      kind: substance
      scope: none
      why: T-10 waits for operator-gated T-09 although the remote landing does not change the affected test population; gather local proof first and retain SC-08 as a mandatory independent ship gate.
    - reader: should-not-exist
      summary: "T-03's gate_policy repair-command recognizer solves a Bash lockout the gates need not create; scope invalid-config denial to each gate's governed command shapes instead."
      severity: high
      kind: proportionality
      scope: task
      why: All three gates recognize governed actions purely from command text; denying only matched shapes with the loader diagnosis is fail-closed, restores repair access naturally and avoids a shell-allowlist mechanism plus deny-all-Bash blast radius.
    - reader: should-not-exist
      summary: "No task dispositions harness-factory-smoke's remote config, which fail-closed product_config will start validating."
      severity: med
      kind: substance
      scope: task
      why: Fleet retains the fixture, removal is out of scope and only Kaya is migrated; an invalid board could break check-product-configs without a recorded disposition. Remote content was unverified by this offline reader.
    - reader: should-not-exist
      summary: "T-10's pinned-SHA reduction checker is one-shot release tooling installed as a permanent integration test."
      severity: med
      kind: proportionality
      scope: task
      why: Integration detect globs would retain a fixed-base release checker and negative-control self-tests indefinitely, including shallow-clone fragility; the durable receipt can instead be produced by feature tooling.
    - reader: should-not-exist
      summary: Routing omp-hooks.test.ts fixtures through the Python builder CLI buys nothing the advisory TS reader can feel.
      severity: low
      kind: proportionality
      scope: task
      why: Advisory fallback cannot feel schema drift; a checked-in builder-generated fixture meets the one-builder choice without adding bun-to-python-jsonschema runtime dependency.
    - reader: should-not-exist
      summary: Creating CHANGELOG.md with a single entry invents a third change-record convention.
      severity: low
      kind: proportionality
      scope: task
      why: DECISIONS.md and notes/changes-config-contract.md already record this change; a new one-entry changelog adds maintenance or rots.
    - reader: should-not-exist
      summary: "The fixture census's six --scope flags encode this plan's task boundaries into permanent machinery."
      severity: info
      kind: proportionality
      scope: task
      why: Those partitions exist only for T-02 through T-07 gates; post-ship the whole census suffices and file moves otherwise need partition maintenance.
    - reader: should-not-exist
      summary: "T-09's dependency on T-08 serializes the only human-latency step behind the entire test-reduction grind."
      severity: info
      kind: proportionality
      scope: task
      why: Payload needs T-01 and T-03 rather than docs; earlier publication could overlap review latency, and compare-and-swap handles staleness.
```
