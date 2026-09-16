# Security review — BUG-1724-run-end-tokens

BLUF: PASS. T-01 is security-relevant because host task-result data now causes a ledger mutation and is surfaced in diagnostics/advisories, but the pinned six-file change introduces no exploitable security defect.

## Scope evidence

- `.omp/extensions/harness-hooks.ts`: in scope. `event.details.results[*].tokens` crosses the host-event boundary. The new code accepts only non-negative integer JavaScript numbers, builds list-form argv (no shell), uses the already-resolved existing feature path, stamps before the read-only spend call, and does not log raw result content.
- `.claude/skills/harness/bin/feature-record.py`: in scope. The new verb mutates `feature.json`; argparse requires a non-negative Python integer, open-run selection requires exactly one started/unended run, diagnostics expose only run ids already in that feature ledger, and the existing locked/schema-validated atomic writer retains mutation authority.
- `.claude/skills/harness/SKILL.md`: in scope only as an operator-facing command contract; it removes routine token transcription and retains the explicit measured-value override. It adds no executable interpolation, secret, or deserialization surface.
- `tests/unit/omp-hooks.test.ts`: in scope as evidence only; fixtures contain no credentials and exercise host input validation, argv ordering, no-token behavior, and on-disk mutation.
- `tests/unit/test-omp-hooks.py`: scoped out of the delta: unchanged in the reviewed task range and remains only a bounded test runner.
- `tests/unit/test-feature-record.py`: in scope as evidence only; fixtures contain no credentials and exercise sole-open-run authority, byte-preserving refusal, diagnostics, and non-negative integer parsing.

No new dependency, authentication/authorization decision, network request/SSRF path, unsafe deserialization, secret material, or user-controlled shell command is introduced. The surface has prior security-sensitive mechanisms (feature-root resolution and atomic/schema-checked feature writes); this delta reuses rather than weakens them.

## Threat model

- Tampering: a malformed or adversarial host result could try to write an arbitrary/negative/fractional token value. Mitigated by shape/integer/non-negative checks and fixed list-form argv; the CLI independently parses a non-negative integer.
- Tampering / elevation: a task result could be attributed to the wrong or ambiguous run. Mitigated by the one-open-run invariant and exit-2 refusal without a write. The hook intentionally treats this accounting failure as non-blocking; it does not grant execution or ledger mutation authority beyond the failed stamp.
- Injection: feature path or token text could be interpreted as shell syntax or flags. Mitigated because `spawnSync` receives argv, the path occupies the value after `--file`, and token text is generated from an accepted number after `--tokens`.
- Information disclosure: diagnostics/advisories could reveal task payloads or secrets. Mitigated: only aggregate token counts and existing conflicting run ids are emitted; raw result bodies are neither persisted nor logged.
- Denial of service: unbounded result arrays require linear work, but the array is host-produced task metadata already materialized in memory; the change adds one bounded pass and one subprocess call per completed task event, with no attacker capability delta identified.

```yaml
VERDICT: PASS
DIGEST:
  headline: "T-01 safely validates and attributes host token totals before mutating the feature ledger; no exploitable security finding."
  in_scope: true
  scope_reason: "The diff consumes host task-result input, constructs a subprocess argv, resolves a feature ledger path, mutates feature.json, and emits aggregate diagnostics; all six files were censused, and the executable boundary is constrained by integer validation, list-form argv, existing feature-root resolution, sole-open-run refusal, and atomic schema-validated writes."
  severity_max: none
  findings: []
  must_fix: []
  threat_model:
    - { boundary: "host task-result details -> token aggregation -> feature-record argv", stride: T, mitigated: true }
    - { boundary: "feature-record CLI -> exactly one open feature.json run", stride: E, mitigated: true }
    - { boundary: "feature ledger -> refusal diagnostics and SPEND advisory", stride: I, mitigated: true }
    - { boundary: "host-supplied results array -> synchronous aggregation", stride: D, mitigated: true }
  open_questions: []
  files_touched: [".harness/harness/features/BUG-1724-run-end-tokens/notes/review-harness-security-reviewer-c0.md"]
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-1724-run-end-tokens/.harness/harness/features/BUG-1724-run-end-tokens/notes/review-harness-security-reviewer-c0.md
```
