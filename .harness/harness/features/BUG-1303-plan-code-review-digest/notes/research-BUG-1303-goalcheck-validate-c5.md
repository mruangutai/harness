# Goal-check — BUG-1303 — SC-01..SC-08 at review_sha `e2c800f1`

**8 of 8 met. 0 send-backs.** Graded at pin `e2c800f14560d272357beb5c0628389a3433ddd2`;
`<base>` = `git merge-base main e2c800f1` = `63404ef06cd798c6d933b52336bf73de7b248028`.
The earlier pin `59c5de97` is superseded: SC-06 was PARTIAL there
(`notes/review-harness-code-reviewer-c4.md:141-149`) and is met here. All content evidence read
with `git show e2c800f1:<path>`, never a plain file read.

## Per-criterion

- **SC-01 — met.** `automated / integration`. `python3 tests/integration/test-validate-digest.py`
  → exit 0, `grep -c '^FAIL '` = 0, final line `ALL PASSED.`, 19.5s, 184 output lines.
- **SC-02 — met.** `automated / integration`. Suite line 181:
  `ok [documented contract discrimination] omitted field reported, present field accepted`.
  Both directions are separate conjuncts of `_discrimination_ok` (`test-validate-digest.py:466-475`)
  over the *same* `documented_contract_gaps` the live grading uses (`:340`), so neither is ever-green.
  *Advisory, not a gap:* the two directions share one report line — a diagnosability cost, not an
  ever-greenness one, and the criterion's stated purpose is the latter.
- **SC-03 — met, both halves plus the fragment clause.** `automated / integration`.
  Derivation is real, not retyped: `_derive_plan_mode_code_grade` (`:394-427`) probes
  `validator._pending_plan_review_error` across every `validator.CODE_GRADE_VALUES` member and keeps
  the single non-rejected one, erroring out on zero-or-many rather than defaulting. The literal `n_a`
  is gone from the check. Composites, not substrings: `"reviewed: " + validator._PLAN_REVIEW_PREFIX`
  (`:436`) and `^\s*code_grade\s*:.*\b<derived>\b` (`:445-446`, first non-space token). Per source:
  - `.claude/agents/harness-code-reviewer.md` — `reviewed: plan:` ok (:173); `code_grade: … n_a` ok (:174); artifact fragment ok (:175)
  - `.omp/agents/harness-code-reviewer.md` — ok (:176); ok (:177); fragment ok (:178)
  - `.claude/skills/harness-code-review/SKILL.md` — ok (:179); ok (:180); fragment n/a by design (agent files only)
- **SC-04 — met.** `inspection`. `git diff --name-only 63404ef0..e2c800f1` = 40 files;
  `grep -c '^\.claude/skills/harness/bin/'` = **0**, so neither `validate-digest.py` nor any bin file
  is in the range (the one `validate-digest.py` substring hit is `tests/integration/test-validate-digest.py`).
  "still pass unmodified" is structural: that test file's range diff is **299 insertions, 0 deletions**
  (hunks `@@ -241,0 +242,298 @@` and `@@ -3904,0 +4203 @@`) — no pre-existing case body touched — and
  SC-01's run is green.
- **SC-05 — met, per item.** `automated / integration`. Roster derived at `:524` from
  `sorted(validator.ALIAS)`, required fields from `validator.SCHEMAS` (`:385-391`); 16 named
  per-persona `ok` lines (suite :157-172), one each for `harness-ai-dev, -backend-dev,
  -code-reviewer, -data-engineer, -dev-ops, -documentor, -eng-lead, -frontend-dev, -orchestrator,
  -pm, -product-lead, -qa, -security-reviewer, -ui-reviewer, -validator-lead, -visual-designer` —
  no aggregate. Grading is block-scoped (`documented_block`, `:333`), which the seven personas
  sharing two files require. Four synthetic branches, all in **one** call of
  `documented_contract_results` (`_synthetic_contract_results`, `:478-493`), each asserted by name in
  `_completeness_ok` (`:500-511`) and reported green at suite :182:
  - unmapped roster persona (`unmapped`, and `empty` with an empty list) → named failure, ok
  - mapped source absent from disk (`absent.md`) → named failure, ok
  - documented block unlocatable (`unlocatable.md`) → named failure, ok
  - required field present only OUTSIDE the block (`outside.md`) → named failure, ok
  - control (`control.md`) → the sole pass; `controls == ["control: control.md"]` asserted exactly.
- **SC-06 — met AT THE NEW PIN; prior result superseded.** `inspection`. Entry:
  `git show e2c800f1:.harness/harness/docs/DECISIONS.md:6792` — DEC-216, ruling as required.
  Index row: `DECISIONS-INDEX.md:216`, hand-written ruling after ` :: ` present. Idempotence
  re-graded at this pin against the *pinned* blob: `gen-decisions-index.py --stdout | diff -q -`
  → silent, exit 0, both vs the worktree file and vs `git show e2c800f1:…`. At `59c5de97` this clause
  was FALSE (DEC-217 tags `[tests,qa,state]` vs generated `[tests,docs,digest,plan]`); MF-1 landed the
  regenerated row and `DECISIONS-INDEX.md:217` now reads `[tests,docs,digest,plan]` with the ruling
  text after ` :: ` unchanged.
- **SC-07 — met.** `inspection`. At `e2c800f1`, `.claude/skills/harness-code-review/SKILL.md:157` is
  the pinned-SHA instruction (`Diff base..review_sha … never ..HEAD`); the plan-phase form sits
  directly adjacent at `:166` citing DEC-207, with the literal `reviewed: plan:<path-to-plan.yaml>`
  at `:171` and the red-flag row at `:189`.
- **SC-08 — met.** `inspection`. `python3 .claude/skills/harness/bin/sync-agent-adapters.py --check`
  → rc 0. Body compare at the pin, `# Harness: Code Reviewer` onward: `diff -q` clean, 77 lines each
  side. Standing wiring confirmed at `check-omp-port.py:156-166`.

REQ coverage: REQ-01/02 ← SC-03+SC-05, REQ-03 ← SC-04, REQ-04 ← SC-01/02/05, REQ-05 ← SC-06. No REQ
untraced.

## Contract measurements — re-verified, one deviation

All five orchestrator measurements reproduce: digest suite exit 0 / 0 FAIL / `ALL PASSED.`;
`test-config-shape-matrix.py` 19/19; `run-unit-tests.sh --kind integration` rc 0, 0 `^FAIL `, 46 files;
index diff silent rc 0; `check-state.sh` rc 0 (two unrelated `note` lines: FEAT-43 INV-23, BUG-1081
INV-28). **Deviation, wall time only:** the integration pool took **88.1s**, not 60.9s — concurrent
sibling load, no verdict changes.

## Working tree

`git -C <worktree> status --porcelain` → `M .harness/harness/features/BUG-1303-plan-code-review-digest/feature.json`.
**That is outside `notes/` and is not mine** — I made no edit to it; it is the live orchestrator
registry file. Nothing else is dirty; my only write is this note.
