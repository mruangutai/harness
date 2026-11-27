# repanel-product cycle 2 — reader fan-in (lead)

Re-read of T-01 and T-03 as applied in cycle 1. Three readers ran in one wave on the same text.
- **scope** (harness-code-reviewer) returned FAIL with 4 findings: 3 high substance and 1 med substance. Its note is `notes/review-harness-code-reviewer-plan-c2.md`.
- **should-not-exist** (fable-advisor) returned PASS with 1 finding: low, proportionality, scope task. It has no write grant, so I transcribed its block from its return.
- **design** (harness-ui-reviewer) self-scoped out with no findings. Its note is `notes/review-harness-ui-reviewer-plan-c2.md`.

Every severity, kind and summary below is the reader's own, unchanged. I assigned no PF- ids.

## Re-read verdicts on the cycle-1 findings

| cycle-1 id | reader | verdict | pointer |
|---|---|---|---|
| PF-ccd4ca98 | scope | closed | plan.yaml T-03 intent (:333), BRIEF SC-05 (:41); tests/unit/test-feature-record.py:1408–1418 |
| PF-e7dd0045 | scope | NOT closed (restated below) | plan.yaml T-03 verify :298–321; bin/validate-digest.py:462–483 |
| PF-d91cba6c | scope | closed (it closes the migration only; (61.b) was already vacuous, so the probe must not be claimed as proof of cleanup) | plan.yaml :225–227, :249; bin/check_state/ctx.py:360–372, :391 |
| PF-aaf45b29 | scope | closed | plan.yaml :234; research note :69; bin/feature-record.py:124–126, 230, 708 |
| PF-7999938a | scope | NOT bounded (restated below). The authorization half was not reviewed: it is the operator's | plan.yaml :120, :337, :339; bin/canonical_reader_audit.py:212–229, 771–782 |
| PF-b3de0ad1 | should-not-exist | closed. One checkout-root token; fixtures are fixed at creation | plan.yaml T-03 comparison paragraph (:341) |
| RG-A2 (goal-check advisory) | scope | no, the exemption is not bounded (a new finding below) | plan.yaml :311–314, :329 |

The goalcheck reader is not re-run in cycle 2 (SC-09). It ran once, in run plan-product, and was re-graded after the cycle-1 apply. It is carried in the roster below with that provenance.

```yaml
DIGEST:
  readers:
    - reader: scope
      status: ran
      persona: harness-code-reviewer
      reason: cycle-2 re-read of T-01/T-03; VERDICT FAIL, 4 findings, note notes/review-harness-code-reviewer-plan-c2.md
    - reader: should-not-exist
      status: ran
      persona: fable-advisor
      reason: resolved and ran; VERDICT PASS, PF-b3de0ad1 closed, 1 finding transcribed by the lead (no write grant)
    - reader: design
      status: ran
      persona: harness-ui-reviewer
      reason: Mode A self-scoped out, no user-facing surface; PASS, 0 findings, note notes/review-harness-ui-reviewer-plan-c2.md
    - reader: goalcheck
      status: ran
      persona: harness-pm
      reason: ran once at plan exit in run plan-product and re-graded there after the cycle-1 apply; not re-run in cycle 2 (SC-09); note notes/research-FEAT-2581-feature-record-package-goalcheck-plan.md
  findings:
    - reader: scope
      summary: PF-e7dd0045 — T-03 still accepts CLI and replay PASS markers without measured evidence bound to the review pin.
      severity: high
      kind: substance
      scope: none
      why: plan.yaml:298–321 checks some metadata and reruns grade, but a receipt with no CLI/replay records can pass. Six script hashes need not name six distinct paths, and the verifier compares the implementation pin to HEAD without independently binding HEAD to the authoritative review SHA (bin/validate-digest.py:462–483).
    - reader: scope
      summary: PF-7999938a — D-02 still does not bound the rendered-output delta; authorization remains with the operator.
      severity: high
      kind: substance
      scope: none
      why: D-02 and T-03 cover the named wrapped errors and --list rows, and the CLI ledger keeps the copied-bin traceback. But plan.yaml:337 filters already text-decoded gate streams by module substring, losing other changed frame context or line-ending bytes. The audit prints its live bin Python-file count (bin/canonical_reader_audit.py:212–229,771–782); T-01 changes that count and T-03 captures the audit only at the pin (plan.yaml:339).
    - reader: scope
      summary: T-01’s pre-commit gate rejects the mutation output SC-03 requires it to preserve.
      severity: high
      kind: substance
      scope: none
      why: plan.yaml:254 requires both whole-suite commands to exit zero with no FAIL line. SC-03 requires preservation of the four deliberate mutation FAIL lines, and bin/run_pool.py:107–113 relays them on exit zero. T-03 also records the measured integration compiler failure rather than requiring that environment to pass the whole suite.
    - reader: scope
      summary: RG-A2 — T-03 does not bound baseline_failing to the measured set.
      severity: med
      kind: substance
      scope: none
      why: plan.yaml:311–314 subtracts every self-declared baseline_failing path before comparing coverage. An extra baseline failure can therefore hide loss of a previously passing file. plan.yaml:329 measures only tests/integration/test-typescript-typecheck.py.
    - reader: should-not-exist
      summary: "PF-d35d903d's facts changed: the bun run now stays for SC-10 regardless, so the open operator decision covers only the bun-spawned ledger class and feat2581-bun-preload.js, not the run itself."
      severity: low
      kind: proportionality
      scope: task
      why: "plan.yaml T-03 case-identity paragraph: 'this junit run stays even if the operator drops the bun leg from the CLI ledger (PF-d35d903d)'. Dropping the leg saves no execution, only the zero-records cli_identity gate for the bun-spawned class and the preload script; the operator should rule on that narrower trade, not run-versus-no-run as cycle 1 framed it."
```
