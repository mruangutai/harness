# Distillation receipt — harness-ai-dev — FEAT-45-adversarial-plan-panel

BLUF: 3 craft Patterns added, 1 repository Gotcha added. All three lead-relayed candidates
accepted (none rejected). No observation log existed for me this feature — material is my
two altitude receipts (plan-side + build-side) plus a repo-wide staleness check against
HEAD d7f31bb.

## Candidate disposition

- **C1** (missing top-level YAML key in the should-not-exist reader prompt) — **ACCEPT**,
  craft Pattern (P-06). Generalizes past this repo: any prompt whose return is
  machine-parsed by a non-harness persona needs its top-level wrapping key named, not just
  per-field shape, or the shape is free to vary run-to-run indistinguishably from a
  malformed return. Checked at HEAD: `plan-panel.yaml:21-22` now names `findings` as the
  sole top-level key — the fold-in landed, but the underlying craft lesson (verify this in
  future prompt specs) still holds regardless of this instance's fix, so kept as a forward
  rule rather than dropped as stale.
- **C2** (decision prose overcommitting to a specific digest algorithm nothing downstream
  observes) — **ACCEPT**, craft Pattern (P-07). Restates the "no more specific than
  necessary" principle as an operational check: does anything outside the module actually
  observe the mechanism, or only its behavior? Not repo-specific — applies to any decision
  text for any implementation detail.
- **C3** (build-side re-flag of the same plan-side gap, correctly reported as a re-flag
  citing the earlier receipt rather than a new discovery) — **ACCEPT**, craft Pattern
  (P-08). The practice of checking an earlier pass's receipt and grant-map disposition
  before reporting a match as "new" is a durable auditing habit, true in any repo with
  multi-pass review.

## Self-derived addition beyond the three relayed

- Repository Gotcha (G-02): the underlying duplication C3 re-flagged —
  `plan-panel.yaml`'s closing comment and `.omp/agents/harness-validator-lead.md`'s
  "Hosting plan-panel" section stating the same FEAT-45-specific transcription mechanics
  with no test cross-checking them — is a fact true of *this* repository (named files,
  named sections, confirmed still present at HEAD d7f31bb via grep: both still carry
  `unrated`/`PF-`/`severity_max` language). It turns on a path/invariant unique to this
  repo, so it belongs in the repository tier, not craft. Kept `appliable: false` residual
  detail out (that belongs to a backlog row, not Expertise) and stated only the durable
  operational rule: update both together, because nothing else will catch drift.

No candidates rejected.

## Section counts

### Craft — `.harness/expertise/harness-ai-dev.md` (150-line budget)

| Section | Before | After |
|---|---|---|
| Patterns | 5 | 8 |
| Gotchas | 3 | 3 |
| Outcomes | 0 | 0 |
| Open | 0 | 0 |

### Repository — `.harness/harness/expertise/harness-ai-dev.md` (40-line budget)

| Section | Before | After |
|---|---|---|
| Patterns | 0 | 0 |
| Gotchas | 1 | 2 |
| Outcomes | 0 | 0 |
| Open | 0 | 0 |

No cap approached in either tier; no displacement needed.

## Ops applied verbatim

```yaml
expertise_update:
  - op: add
    file: .harness/expertise/harness-ai-dev.md
    section: Patterns
    id: P-06
    entry: "WHEN a prompt's return will be machine-parsed by a persona with no harness return-shape convention DO name the top-level wrapping key explicitly, not just the per-entry field shape — an unspecified top-level shape varies run to run and is indistinguishable from a malformed return."
  - op: add
    file: .harness/expertise/harness-ai-dev.md
    section: Patterns
    id: P-07
    entry: "WHEN a decision's prose commits to a specific implementation mechanism (e.g. an algorithm) that no downstream consumer observes or tests DO state only the behavioral contract — committing to the mechanism forces reopening a signed decision later for a change nothing outside the module can detect."
  - op: add
    file: .harness/expertise/harness-ai-dev.md
    section: Patterns
    id: P-08
    entry: "WHEN your finding matches a gap an earlier pass already raised DO check its receipt and the grant map before reporting it as new — if it was correctly flag-only for unresolved ownership, re-report it as a re-flag citing that receipt, not a fresh discovery."
  - op: add
    file: .harness/harness/expertise/harness-ai-dev.md
    section: Gotchas
    id: G-02
    entry: "WHEN editing plan-panel.yaml's closing comment or harness-validator-lead.md's 'Hosting plan-panel' section DO update both — no test cross-checks their duplicated transcription mechanics (unrated-gating, PF- id ownership), so one can drift silently while the other stays authoritative."
```

Applied via `expertise-merge.py apply` against both files (exit 0 both times; `ADDED
P-06/P-07/P-08` and `ADDED G-02` respectively, all other existing ids `PRESERVED`). No
whole-file write performed. `check-expertise.sh` intentionally not run (orchestrator's
job). Nothing committed.

## Verification

- `grep` against `.claude/skills/harness/teams/plan-panel.yaml` at HEAD confirmed C1's
  fold-in landed (top-level `findings` key now named) and C3's underlying duplication
  (`unrated`/`PF-`/`severity_max` restated in the closing comment) is still present —
  informed the "kept as forward rule" and "repo gotcha still current" calls above.
- Both merge-tool invocations exited 0 with the expected `ADDED`/`PRESERVED` ids; final
  file reads above confirm the rendered content matches the ops.
