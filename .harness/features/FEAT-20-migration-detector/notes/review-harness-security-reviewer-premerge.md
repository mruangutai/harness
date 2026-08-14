# Security pre-merge delta audit — FEAT-20-migration-detector — `ea476fd..045dcd9`

## Verdict: PASS (S1 scoped OUT; S2/S3 clean sweeps on the wider span)

## S1 — the merge-candidate delta, measured

`git diff --name-status ea476fd..045dcd9` touches 22 files: 12 `.harness/expertise/*.md`
(distillation writes), and 10 items under `.harness/features/FEAT-20-migration-detector/` +
`.harness/logs/` + `.harness/notes/` — `STATE.md`, `feature.json`, review/answer/handoff notes, the
ship-review doc (`.md` + `.html`), and two observations logs. **Zero of the eight source files this
feature shipped are touched** — no `layout_migration.py`, `check-state.sh`, `tests.yml`,
`run-unit-tests.sh`, or either test file appears in this delta. This is bookkeeping-and-distillation
only: close-out notes, expertise distillation, ship-review authoring. Scoping OUT per S1's own
instruction — no mechanism changed, so there is nothing here for this role to exploit-model against.

One item checked and dismissed, not gating: `ship-review-2026-08-14.html` is a new artifact type for
this feature (an HTML file alongside the `.md`). Read its content — it is a static rendering of the
same ship-review markdown (headings, tables), no `<script>`, no external resource fetch, no
inline event handler, nothing that executes if opened. Not a finding; noted per P-12 so a later
reviewer doesn't have to re-check it.

## S2 — full-diff secrets sweep, `88b1182..045dcd9` (all files)

`git diff 88b1182..045dcd9 | grep -iE 'token|secret|api[_-]?key|password|ghp_|AKIA|aws_|bearer|authorization:|-----BEGIN|https?://[^ ]*@'`

All hits are one of:
- The English word "token" in prose — expertise entries about grep-token sweeps (P-08/P-12/G-07 in
  `harness-code-reviewer.md`), a CSS comment "Token-level theming: components style through the
  tokens" in a documentation/design fixture, and DEC-194 prose describing "the pinned literal NOT
  APPLICABLE" as a leading token of a string match.
- My own prior finding text (`review-harness-security-reviewer-c0.md`'s "Secrets sweep" section and
  its now-distilled P-14 entry) quoting itself, since c0's note is part of this diff span.

No credential-shaped string, no embedded-auth URL, no private key marker, no `ghp_`/`AKIA` pattern.
Widened past S1's file list per the dispatch's own instruction (docs/config/bookkeeping included) —
clean.

## S3 — `.github/workflows/tests.yml` supply-chain surface, scoped to lines added in `88b1182..045dcd9`

`git diff 88b1182..045dcd9 -- .github/workflows/tests.yml` shows exactly one added block: the
"Layout gate" step (55 lines), unchanged since `ea476fd` — **confirmed by
`git diff ea476fd..045dcd9 -- .github/workflows/tests.yml` returning empty**, so this feature's
merge candidate carries zero net workflow change beyond what was already audited at `ea476fd`.

Measured against S3's four questions, on the added lines only:
- **Third-party actions:** none. The added step contains no `uses:` line at all — it is a single
  `run:` block invoking the repo's own `python3 .claude/skills/harness/bin/layout_migration.py .`
  plus shell (`grep`/`sed`/`awk`) over that script's own stdout. No action reference, so pinned-vs-tag
  is not applicable to this delta.
- **Elevated `permissions:`:** none added — grep confirms no `permissions:` line in the added block.
- **`pull_request_target`:** none added — grep confirms no occurrence.
- **Untrusted interpolation into shell:** the only `${{ }}` reference is
  `CLAUDE_PROJECT_DIR: ${{ github.workspace }}`, a runner-trusted context value, not PR/branch/commit
  content. Every other shell variable (`out`, `summary`, `examined`, `feature_dirs`, `doc_roots`,
  `reader_files`, `zero`) is derived from the local script's own stdout, not from
  `github.event.*`/`secrets.*`. This matches what c0 already established for this same block at
  `ea476fd` — restated here because the dispatch asked for it measured at `045dcd9`, not relayed.

No new supply-chain surface. Pre-existing workflow lines (the earlier "route gate" step, checkout,
matrix setup) were not touched by this feature at any point in `88b1182..045dcd9` and are out of
scope per the dispatch's own instruction.

## Already-ruled items — not re-filed

Q1 (cwd-shadow import, issue #365/B-1), Q2 (false safety comment, panel R-4), and the ReDoS timing
closure are unchanged by this delta (none of the files they concern were touched) and are not
re-opened here.

```yaml
VERDICT: PASS
DIGEST:
  headline: "ea476fd..045dcd9 is bookkeeping/distillation only (12 expertise files + FEAT-20 notes/state, zero of the 8 source files); full-span secrets sweep and the workflow's added-lines-only supply-chain check both come back clean, and the CI diff is byte-identical to what c0 already audited at ea476fd."
  in_scope: true
  scope_reason: "S1 measured the delta and found no source-code surface, which is itself the scope answer, not an absence of review; S2/S3 were run per dispatch regardless of S1's outcome and both are clean."
  severity_max: info
  findings: 0
  must_fix: []
  threat_model:
    - { boundary: "ea476fd..045dcd9 file delta", stride: "n/a", mitigated: true }
    - { boundary: "tests.yml Layout gate step, lines added 88b1182..045dcd9", stride: "T|E", mitigated: true }
    - { boundary: "full-diff secrets/credential sweep 88b1182..045dcd9", stride: "I", mitigated: true }
  open_questions: []
  files_touched: []
  expertise_update: []
artifact: .harness/features/FEAT-20-migration-detector/notes/review-harness-security-reviewer-premerge.md
```
