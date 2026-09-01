# UI re-review — FEAT-50-run-artifact-integrity — fix-cycle recheck

**Pin note (non-blocking):** dispatched pin `7505b87681c8d8007a2677381313581f61faf1b0` does not
resolve in the worktree. `git rev-parse HEAD` returns `7505b8739fd19a68601a27898d880fc719962712`,
which shares the `7505b87` prefix and its commit message is `fix: close FEAT-50 review findings` —
the expected fix-cycle commit. Treated as the intended object per G-15.

## Census (measured, not predicted)

`git diff --stat 9f2a0702bda6de929d42506f5aced2496669a2dc..HEAD`: 37 files, +5753/-42. Extension
breakdown: `.sh` ×2, `.py` ×7, `.md` ×26 (1 skill doc, 2 decision docs, 23 feature-tracking
notes/BRIEF/STATE), `.json` ×1 (`feature.json`), `.yaml` ×1 (`plan.yaml`). **Zero** files matching
html/css/scss/tsx/jsx/vue/svelte/less. No rendered UI surface exists in this diff — consistent with
repository Expertise P-01 (harness ships no build step).

Per dispatch, the one adjacent operator-facing surface in scope is hook stderr text: the refusal
messages the two fixed guards print. Treated as in-remit per project Expertise P-06.

## Refusal-message audit (Mode B, live-verified)

Ran the actual guard code (not just read it) via the repo's own regression harnesses, capturing
verbatim stderr:

- `bash-write-guard.sh` shared-domain checkout refusal (`python3 test-bash-write-guard.py` →
  `run_feat50_checkout_binding`, 6/6 incl. mutation-kill "red" case):
  `bash-write-guard: BLOCKED — <abs-path> is a feature artifact whose write belongs in worktree
  <abs-worktree-path>. Write it there, not in the main checkout.` — **names the offending path, the
  destination checkout, and the remedy action.** Actionable.
- `check-domain.sh` checkout refusal (`test-check-domain.py` → `run_feat50_artifact_integrity`,
  10/10 incl. mutation-kill cases):
  `check-domain: BLOCKED — <abs-path> is a feature artifact whose write belongs in worktree
  <abs-worktree-path>.` + `Write this artifact in <abs-worktree-path>, not the main checkout.` —
  same three elements, on two lines. Actionable.
- `check-domain.sh` digest-clobber refusal (non-empty-prior case): `... run digest already holds a
  recorded digest; this Write would replace rather than extend it. Write this cycle's digest into a
  run directory of its own.` — names the fact and the remedy. Actionable.
- `check-domain.sh` digest-unreadable refusal (OSError case, live-triggered by making the digest
  path a directory): `check-domain: BLOCKED — <rel-path>: run digest already exists but cannot be
  read safely; refusing a Write that could destroy its recorded content.` — names the offending path
  and the fact, but **states no remedy action**, unlike its clobber sibling three lines above it in
  the same function and unlike both checkout-guard messages. Per Expertise G-13, a message stating
  only the triggering fact is the most common completeness gap in text-only interfaces.

## Verdict rationale

Two of three prior findings (#1 checkout binding, #3 digest-clobber OSError) live-verified fixed and
correctly reflected in operator-facing text; the checkout-guard messages fully satisfy the
dispatch's actionability bar (path + checkout + remedy). Finding #2 (code_grade) is outside this
role's lens — left to the code reviewer. The one gap found (digest-unreadable message lacks an
explicit next step) is a genuine but low-severity wording completeness note: it is an edge-case
OSError path (permission/IO failure, not a routine flow), the write is still correctly refused
(exit 2, confirmed live), and the missing text is "investigate why the file can't be read," which
is inherently open-ended rather than a single prescribable action the guard could name. Does not
gate.

## Accessibility / theme parity

N/A — plain stderr text, no colour-only state encoding, no rendered theme. (G-02)

```yaml
VERDICT: PASS
DIGEST:
  headline: No rendered UI in this diff (measured 0 UI-extension files of 37); the two adjacent hook-refusal-message fixes are live-verified actionable — path, checkout, and remedy all named — with one low-severity wording gap on the digest-unreadable message that does not gate.
  mode: B
  in_scope: true
  severity_max: low
  findings: 1
  must_fix: []
  states_unspecified: []
  contract_violations: []
  a11y: ["n/a — plain stderr text, no colour-only encoding, no rendered theme"]
  open_questions: []
  files_touched: []
  expertise_update: []
artifact: .harness/harness/features/FEAT-50-run-artifact-integrity/notes/review-harness-ui-reviewer-feat50-recheck.md
```
