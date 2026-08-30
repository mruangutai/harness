# QA delta-mutation review — FEAT-43 cycle 29 (`73c636d`)

**BLUF:** The three-callsite fix and its AST guard are mutation-sensitive at exactly the granularity
the authorization (`Q13-cycle-29-substring-gate.md`) demanded — each of the three individual callsite
reverts is caught, alone, by the named guard case, and the vacuity the guard exists to close is
reproduced against real (not synthetic) sweep output. The `re.search` strengthening a peer code
reviewer proposed as a `should_fix` is verified independently, on both claimed halves, and costs
nothing at full-suite level. Four of five regate measurements CONFIRM exactly; **`check-state.sh`
CONTRADICTS** (exit 1, not 0) — one `VIOLATION` in a run `state.yaml` written by a live sibling
process, unrelated to this diff. Tree byte-identical to the pin; HEAD unmoved.

## 1. Callsite-level mutation sensitivity — three mutations, one per callsite, each restored and verified clean

Ran `python3 .claude/skills/harness/bin/test-validate-feature-json.py` (no args — full module,
direct interpreter invocation) after each single-line revert, then restored the line byte-for-byte
and confirmed `git status --porcelain -- .claude/skills/harness/bin/test-validate-feature-json.py`
was empty before touching the next line.

**Mutation A — line 335 (positive, `case_migrated_depth_discovery_...`).** Reverted to
`"1 file(s)" in r.stderr, r.stderr)`.
Run: exit **1**. Named failure: `FAIL no bare rendered-count substring compare outside
reports_exactly_one_file offending line(s): [335]` — exactly the expected case name, alone (`1
FAILURE(S)`). Restored; `git status --porcelain` on the file: empty.

**Mutation B — line 360 (negative, `case_root_resolves_...`, the callsite that actually broke CI at
the merge).** Reverted to `"1 file(s)" not in r.stderr, r.stderr)`.
Run: exit **1**, **two** named failures: `case_root_resolves: CLAUDE_PROJECT_DIR alone does not
redirect the sweep (...)` **and** `no bare rendered-count substring compare outside
reports_exactly_one_file offending line(s): [360]`. This is not "a different case failed instead" —
it is both: the guard fires as designed, *and* the live tree currently holds a feature-directory
count whose rendered form re-trips the original substring bug on its own (the tree presently sweeps
to a two-digit count ending in `1`; see §2), so the functional assertion the guard exists to protect
fails independently at the same time. Reported as observed, not folded into a single "as expected"
line. Restored; `git status --porcelain` on the file: empty.

**Mutation C — line 371 (positive, second half of `case_root_resolves_...`).** Reverted to
`"1 file(s)" in r2.stderr, r2.stderr)`.
Run: exit **1**. Named failure: `no bare rendered-count substring compare outside
reports_exactly_one_file offending line(s): [371]` — exactly the expected case name, alone (`1
FAILURE(S)`). The case this callsite belongs to (`case_root_resolves: HARNESS_PROJECT_DIR +
team-config.yaml IS honoured`) still shows `PASS` in this run's own output, because the tmp fixture
in that half of the test genuinely does resolve to exactly one file — confirming the guard is the
*only* thing that catches this particular revert, exactly the "invisible regression" scenario the
guard's docstring names. Restored; `git status --porcelain` on the file: empty.

**Verdict on item 1:** all three callsites are individually mutation-sensitive via the guard, and the
guard is the sole detector for two of the three (A and C) — corroborating the authorization's
premise that a helper-level control alone would miss a callsite regression.

## 2. The vacuity, demonstrated on real (not synthetic) stderr

Ran the actual CLI against the real repository root — `env HARNESS_PROJECT_DIR="$PWD" python3
.claude/skills/harness/bin/validate-feature-json.py` from the worktree root — which models exactly
the failure condition the positive assertions guard against: the sweep resolving to the real
checkout (many feature directories) rather than the tmp fixture (one). Captured stderr, first line:

```
scanning .../.harness/*/features/*/feature.{json,yaml,yml} — 41 file(s)
```

Against this real string:
- `"1 file(s)" in stderr` → **`True`** — the old bare substring assertion is satisfied. This is the
  exact vacuous pass the cycle exists to close: the positive assertion would report "the sweep found
  exactly one file" while it in fact found 41.
- `reports_exactly_one_file(stderr)` → **`False`** — the new predicate correctly rejects it.

Not a fallback reproduction — this is a real, live sweep of the actual worktree, run standalone
(not through the test harness), with real stderr captured and both predicates evaluated against the
identical string.

## 3. The `re.search` claim, verified independently (not taken on the reviewer's word)

Peer claim (from `review-harness-code-reviewer-delta-c29.md`, non-blocking `open_question` Q1):
`re.search` over `_rendered_count_substring_compares`'s left-operand check is strictly stronger than
`re.fullmatch` at zero false-fire cost.

**Half 1 — `search` catches a realistic revert-with-suffix that `fullmatch` misses.**
```python
>>> re.fullmatch(r"\d+ file\(s\)", "1 file(s) swept")
None
>>> re.search(r"\b\d+ file\(s\)", "1 file(s) swept")
<re.Match object; span=(0, 12), match='1 file(s)'>
```
Confirmed: a bare-substring revert carrying incidental trailing text (`"1 file(s) swept" in
r.stderr`) would slip past today's `fullmatch`-based guard silently. `search` catches it.

**Half 2 — zero false-fire cost, verified by walking this file's own AST, not by inspection.** Walked
every `Compare` node in the live `test-validate-feature-json.py` with `ast.In`/`ast.NotIn` ops,
testing each string-literal left operand against both regexes:
```
fullmatch hits over the WHOLE FILE Compare nodes: []
search hits over the WHOLE FILE Compare nodes: []
```
Both empty — confirming the reviewer's structural point independently: the control literals
(`"41 file(s) swept"`, `"21 file(s) swept")`, etc. in
`case_reports_exactly_one_file_rejects_substring_match`) are **`Call` arguments** to
`reports_exactly_one_file(...)`, never `Compare` left operands, so neither regex ever sees them
regardless of strictness — the walker's own node-type filter, not the regex choice, is what excludes
them.

**Full-suite proof, in a disposable `/tmp` copy (never the repo file).** Copied every `.py`/`.json`
file from `.claude/skills/harness/bin` into a fresh `mktemp -d` directory, patched only the copy's
`_rendered_count_substring_compares` regex from `re.fullmatch(r"\d+ file\(s\)", ...)` to
`re.search(r"\b\d+ file\(s\)", ...)`, and ran the copy's own `test-validate-feature-json.py` end to
end with `HARNESS_PROJECT_DIR` pointed at the real worktree:
```
$ python3 test-validate-feature-json.py   (patched /tmp copy)
...
ALL PASS
EXIT=0
```
Confirms the strengthening is free at suite level, not merely at the walker level in isolation. The
repo's own `test-validate-feature-json.py` was never touched for this step (`git status --porcelain`
on it stayed empty throughout — verified before and after).

## 4. Regate — five measurements, each independently run, each judged CONFIRM/CONTRADICT

| # | Measurement | Command | Exit | Observed | Verdict |
|---|---|---|---|---|---|
| 1 | `--kind unit` gate | `.claude/skills/harness/bin/run-unit-tests.sh --kind unit` | **0** | zero `FAIL` lines across the full run (grepped the complete log for `FAIL`: none) | **CONFIRMS** exit 0, zero failures |
| 2 | Five focused FEAT-43 suites | `python3 test-code-grade.py` / `test-code-grade-cli.py` / `test-gate-policy.py` / `test-check-plan-routes.py` / `test-validate-digest.py` (run individually, `.claude/skills/harness/bin`) | **0** each | `PASS test-code-grade`; `PASS test-code-grade-cli`; `ok` lines through gate-policy; `ALL PASS` (check-plan-routes); `18/18 ... ALL PASSED.` (validate-digest) | **CONFIRMS** all five exit 0 |
| 3 | Engine self-grade | `python3 code-grade.py code_grade.py --json` | **0** | parsed JSON: `len(records) == 53`, `sum(grade<4) == 0`, `ungraded == []` | **CONFIRMS** 53 functions, 0 below grade 4 |
| 4 | Range gate `6d6d1ce..HEAD` | `python3 code-grade.py --base 6d6d1ce --head HEAD --json` | **0** | `len(records) == 206`; blocking (`grade < bar and grade != 2`) `== 0`; `grade == 2` count `== 12`; `ungraded == []` | **CONFIRMS** 206 gated, 0 blocking |
| 5 | `check-state.sh` | `bash .claude/skills/harness/bin/check-state.sh` | **1** | 580 `note` lines, **one** `VIOLATION`: `.../runs/2026-08-30-05-validate-delta-c29-validator/state.yaml: non-checkpoint top-level key(s) ['cycle', 'derived_base', 'panel_scope', 'pin', 'prior_pin']` (DEC-154 — `state.yaml` carries only identifiers/enums/counters/paths/sequence markers, not run narrative) | **CONTRADICTS** the exit-0 claim |

**On item 5:** the violating file lives under `runs/2026-08-30-05-validate-delta-c29-validator/`, a
run directory this task never touched and does not own — the roster shows a sibling
(`Feat43RemediationToDecision.Feat43DeltaC29`, a `harness-validator-lead`) currently `running` and
"Checkpointing wave 1 return and wave 2 dispatch" at dispatch time, which is exactly the kind of
concurrent write that would place narrative-shaped keys in a run checkpoint mid-flight. Not caused
by, or fixable within, this diff (`test-validate-feature-json.py` only) — raised as an
`open_question`, not a `must_fix` against this change.

## 5. Tree integrity

```
$ git -C <worktree> log --oneline -1
73c636d test: replace the count substring predicate at all three callsites and guard them   (pin, unmoved)

$ git -C <worktree> status --porcelain -- .claude/skills/harness/bin/test-validate-feature-json.py
(empty — target file carries no modification)

$ git -C <worktree> status --porcelain
 M .harness/harness/features/FEAT-43-code-risk-grading/feature.json          (pre-existing, present before this run)
?? .harness/.../answers/Q13-cycle-29-substring-gate.md                       (pre-existing)
?? .harness/.../notes/receipt-*-validate-substring-c29-*.md (x4)             (pre-existing)
?? .harness/.../notes/review-harness-code-reviewer-delta-c29.md              (pre-existing)

$ git -C /Users/molchairuangutai/GitHub/harness status --porcelain
(only pre-existing untracked feature/log/notes dirs — no tracked modification)
```

All three checks match the state observed at the start of this run — nothing in the worktree or the
main checkout was left touched by the mutation/restore cycles or the regate.

## What this review did NOT cover

- The eight already-closed FEAT-43 defects, main's own content, and any canonical/project-wide suite
  beyond `--kind unit` — all explicit non-goals per the dispatch.
- No commit or stage of any kind was performed; no permanent edit survives (§1's three mutations were
  each restored and verified byte-identical before the next).
- Did not re-litigate the code reviewer's second `should_fix` (adding this file/function to
  `test-code-grade.py`'s `SELF_GRADED_FILES` tracking) — out of scope for a mutation-test/regate pass;
  it is a coverage-registration decision, not something my runs can confirm or contradict.
- Did not investigate or attempt to fix the `check-state.sh` `VIOLATION` — it belongs to a live
  sibling's run state, not to this diff, and touching another agent's in-flight run directory was
  never in scope here.
- Did not run any project-wide formatter, linter, or `--kind integration`/`--kind all` sweep — outside
  this dispatch's stated scope (`--kind unit` only).

```yaml
VERDICT: PASS
DIGEST:
  headline: All three callsite mutations are individually caught by the named AST guard (restored and verified clean each time); the vacuity is reproduced against real sweep stderr, not synthetic; the re.search strengthening is verified independently on both claimed halves and costs nothing at full-suite level. Four of five regate measurements CONFIRM exactly (--kind unit exit 0/0 failures, five focused suites all exit 0, self-grade 53/0-below-4, range gate 206 gated/0 blocking); check-state.sh CONTRADICTS (exit 1, one VIOLATION in a run state.yaml owned by a currently-running sibling agent, unrelated to this diff).
  suite: pass
  matrix_ok: true
  severity_max: info
  failures: 0
  coverage_gaps: []
  sc_evidence: []
  must_fix: []
  should_fix:
    - "check-state.sh exits 1 (one VIOLATION: runs/2026-08-30-05-validate-delta-c29-validator/state.yaml carries non-checkpoint narrative keys per DEC-154) — not caused by this diff, but the orchestrator's regate claim of 'exit 0' does not hold at the moment this ran; likely a live sibling checkpoint write in flight. severity: info as far as this diff is concerned; worth a rerun of check-state.sh once that sibling settles before treating the state gate as green."
  open_questions:
    - { id: Q1, question: "check-state.sh's single VIOLATION targets a run directory (runs/2026-08-30-05-validate-delta-c29-validator) owned by a currently-running sibling (Feat43RemediationToDecision.Feat43DeltaC29). Should the orchestrator re-run check-state.sh after that sibling's checkpoint settles, to confirm the state gate is genuinely clean before ship?", blocking: false }
  files_touched: []
  expertise_update: []
artifact: .harness/harness/features/FEAT-43-code-risk-grading/notes/qa-delta-c29.md
```
