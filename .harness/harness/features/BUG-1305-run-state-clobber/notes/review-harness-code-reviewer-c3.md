# BUG-1305 · cycle-14 delta code review (C3) — review_sha 5ed929bd

Scope: `1b11bc18..5ed929bd` only (`.claude/skills/harness/bin/check-domain.sh`,
`tests/integration/test-check-domain.py`, plus STATE.md/feature.json bookkeeping). All
source read via `git show 5ed929bd:<path>`; confirmed the worktree copy is byte-identical
to the pin for both the guard and the test file (no intervening commit touches either —
`git log 5ed929bd..HEAD` shows only a `feature.json` repin).

## VERDICT: FAIL — one must_fix (high), inside-delta:test-only

## Stage 1 — spec compliance

**(a) All three patterns covered, no fourth swept in.** `check-domain.sh:2045-2048` gates
entry into the new branch on `RE_RUN_DIGEST.match OR RE_STATE_YAML.match OR
RE_HANDOFF.match` — exactly the three named classes, no more. `RE_STATE_MD`,
`RE_FEATURE_JSON`, `RE_CLAUDE_MD` and `RE_PLAN_YAML` are absent from this condition, so an
`Edit` targeting them still falls through to the untouched `elif _tool != "Write" or not
target: sys.exit(0)` at line 2074 — that fallthrough is unchanged context, not part of
this diff, and is correctly out of scope. Confirmed: no fourth class silently added or
removed.

**(b) No fail-open remnant.** Inside the new branch, `if _content is None:` (line 2057)
has exactly two sub-branches (state.yaml-specific message vs. generic message), and
**both** end in `sys.exit(2)` (lines 2071-2072) — there is no path back to `sys.exit(0)`
for a `None` reconstruction on any of the three classes. `_UNREADABLE_EDIT` (non-UTF-8)
also exits 2 (line 2056). The prior fail-open (`sys.exit(0)` on `None`) is fully removed.

**(c) Fail-closed-on-`None`, not deny-by-path** — confirmed, and the two shapes sit
side by side in the same `if not _post:` chain for direct contrast:
- `check-domain.sh:2042-2044` — `RE_RUN_IDENTITY` is **deny-by-path**: any `Edit` whose
  target matches is unconditionally forced to `targets = [(..., "", ...)]` regardless of
  whether reconstruction would have succeeded (comment at 2039-2041: "denied by path
  alone").
- `check-domain.sh:2045-2073` — the three new classes are **fail-closed-on-`None`**:
  reconstruction is attempted; only `_content is None`/`_UNREADABLE_EDIT` refuses (exit 2,
  lines 2056/2072); a successful unique-match reconstruction falls through to
  `targets = [(_norm(target), _content, ...)]` at line 2073 and continues into the same
  content-shape checks a Write would get. This is the correct shape — deny-by-path here
  would over-refuse legitimate same-run checkpoint edits.

**Routing-message sufficiency — SUFFICIENT.** Verbatim from the pin:
- state.yaml: `"check-domain: BLOCKED — state.yaml run identity and its witness cannot
  be verified because this Edit cannot be reconstructed from the tool payload (Issue
  1305). Write the complete file instead."`
- digest.md/handoff (generic): `"check-domain: BLOCKED — this protected run artifact
  cannot be verified because the Edit cannot be reconstructed from the tool payload.
  Write the complete file instead."`

An agent holding only this stderr text learns, in one sentence: what was blocked, why
(payload cannot be reconstructed), and the concrete next action ("Write the complete file
instead" — capitalized Write, unambiguously pointing at the Write tool rather than a
retried Edit). No `inside-delta:message-wording` finding.

## Finding 1 — must_fix, HIGH, inside-delta:test-only

**The fail-closed-`None` branch is proven in-suite for `RE_STATE_YAML` only; the same
branch for `RE_RUN_DIGEST` and `RE_HANDOFF` is proven by source-reading alone.**

The branch is a single shared `elif` (check-domain.sh:2045-2073) — one `_edit_reconstructed_content`
call and one `if _content is None: ... sys.exit(2)` for all three classes — so at the
source level the three are symmetric and correctly implemented (Stage-1 (a)/(b)/(c)
above hold). But every new/updated red/green case in this diff targets `state.yaml`
only:
- `test-check-domain.py:3830-3851` (bug1106 unmatched/non-unique cases) — both use
  `_bug1124_state_fixture()`.
- `test-check-domain.py:4769-4826` (`_bug1305_absent_prior_edit_case`,
  `_bug1305_unmatched_edit_case`, `_bug1305_omp_edit_cases`) — all four cases use
  `_bug1124_state_fixture()`.

Grepping the entire test file for the literal string the generic (non-state.yaml) branch
emits — `"protected run artifact"` — returns **zero matches** anywhere in
`test-check-domain.py`. No test fires an `Edit` with an unmatched/absent/non-unique
`old_string`, or an omp-shaped `file_path`-only payload, against a `digest.md` or a
`notes/handoff-*.md` fixture. The pre-existing digest.md Edit-route tests
(`test-check-domain.py:3790-3809`) only cover *successful* reconstruction (replace-shaped
refused, append-shaped allowed) — never the `None` branch.

**Why this gates, given the code is symmetric:** BUG-1305 cycle 13 exists specifically
because a prior panel accepted "the `None` fall-through is benign for these three
patterns" as source-level reasoning, and that reasoning is now on record as invalid — the
dispatch for this very cycle voids it by name and forbids reconstructing an equivalent
argument. My own source-level confirmation of symmetry for digest.md/handoff.md is the
same *kind* of evidence (reading the branch and reasoning it must behave identically) that
this feature's own history says is not sufficient for these three artifact classes. Two of
the three named classes ship with zero red/green suite proof of the fix that was the
entire point of cycle 13.

**Remedy (mechanical, test-only):** add two cases mirroring
`_bug1305_unmatched_edit_case`/`_bug1305_omp_edit_cases` but targeting
`_feat50_digest_fixture()` (digest.md) and a `notes/handoff-<slug>.md` fixture built the
way `_handoff_grammar_cases`/line-4168's fixture already do; assert `returncode == 2` and
`"Write the complete file instead" in stderr` (or the literal `"protected run artifact"`
string to specifically pin the generic-message branch). Add alongside
`_bug1305_edit_reconstruction_cases` or as new entries in `run_bug1106_edit_route_cases`.

## Stage 2 — quality of the delta lines

No correctness, duplication, or dead-branch defects beyond Finding 1. One **info**, not
gating: `check-domain.sh:2058-2071` duplicates the `print(...)` call shape across the
`if RE_STATE_YAML.match(...)`/`else` split, varying only the message body — could be one
`print` keyed on a conditional message string. Not worth a cycle on its own.

## Grading

**Delta-scoped grading** (`base 1b11bc18`, `head 5ed929bd` — the cycle-13 diff itself):
re-ran `code-grade.py` myself → **PASSING 5**, per-function grades **5, 5, 5, 4, 5**
(driver `abc` for the one grade-4 record, `_bug1305_omp_edit_cases`). This **agrees
exactly** with the measured result cited in the dispatch. `check-domain.sh` contributes
no graded records — it is a `.sh` file (shell scripts are ungraded per policy) even
though its body is embedded Python.

**Canonical-range grading** (the range `validate-digest.py` independently derives and
binds `code_grade` to: `merge-base(default branch, review_sha)..review_sha` =
`4b0d04e974244fc3766267e1ebe9d444b27c7df8..5ed929bd73b366acd9a63134797e58ab6dbe5281`):
re-ran the grader over that range → **PASSING 55, FAILING 6**, all six at **grade 2,
severity med** (none grade 1, none grade 3-in-production — nothing blocks). All six
predate the `1b11bc18..5ed929bd` delta this dispatch assigned me (none is among the
functions this diff touches) and are `outside-delta` for routing purposes; I read each
one to give the reason the tool requires rather than defer it, since a grade-2 record
still gates the digest until reasoned:

| Function | Location | Driver | Reason |
|---|---|---|---|
| `_write_while_sweep_reads_fifo` | test-check-domain.py:1044 | cognitive 16 | FIFO-synchronization helper: a bounded busy-wait/retry loop (ENXIO vs. real error), a deadline check, and `finally`-block cleanup of both the writer fd and the subprocess — real, load-bearing IPC-race complexity, not padding. Pre-existing (unrelated FEAT-41 quarantine-sweep test), untouched by this delta. |
| `run_bug1305_digest_repair_cases` | test-check-domain.py:3880 | abc 37.3 | Five independent, structurally identical fixture→fire→assert blocks appended to one `results` list — cyclomatic stays at 4; ABC is driven by the sheer count of sequential fixture/assertion calls, the dominant convention this whole file uses for grouping related cases (compare `run_bug1305_marker_cases` and siblings). No nested branching. |
| `_bug1305_identity_refusal_cases` | test-check-domain.py:5060 | cyclomatic+abc | Five setup calls feeding a `return [...]` of five tuples, each tuple's boolean a compound (3-4 clause) refusal-message assertion — the compound conditions inflate cyclomatic/ABC, not control flow; same collector shape used throughout the `_bug1305_*` suite. |
| `case_bug1305_run_identity_invariant` | test-check-state.py:4560 | cyclomatic+abc | Two nested closures (`build`, `write_run`) plus two independent `TemporaryDirectory` scenario blocks (a "clobbers detected" tree and a "stays silent" tree), each closed out with a compound `all(...)`/tuple-membership assertion. A defensible split (one function per scenario tree) exists, but it is a design change outside this delta's mandate — not remedied here. |
| `case_uid_mint_and_injection` | tests/unit/test-run-identity.py:64 | abc 38.7 | Sequential `check(...)` calls covering shape/uniqueness/injection/idempotence/missing-file behavior of `mint_uid`/`inject_uid` — one scenario per line, no nesting; ABC driven by call count. |
| `case_seed_conflict_guards` | tests/unit/test-run-identity.py:86 | abc 26.1 | Two `TemporaryDirectory` blocks, each a sequence of `record_seed`/`conflict`/`check` calls exercising one seed-conflict rule per line; same shape as `case_uid_conflicts` (grade 4 with fewer checks) one tier up. |

None of the six is a correctness concern; none is production code (all bar 3, test
convention). `code_grade: grade_2` is the value this digest reports, matching the
mechanical result over the canonical range — it does not change the delta-scoped result
above, which is what Stage 1/2 of this review actually judged.

```yaml
VERDICT: FAIL
DIGEST:
  headline: Fix is structurally sound and fail-closed for all three classes at the source, but only RE_STATE_YAML's None-branch has in-suite red/green proof — RE_RUN_DIGEST/RE_HANDOFF's identical branch is unproven in-suite.
  severity_max: high
  findings: 1
  must_fix: ["digest.md/handoff-*.md None-reconstruction (unmatched/absent/omp-payload) has zero suite coverage; add cases mirroring the state.yaml ones — see Finding 1"]
  spec_violations: []
  code_grade: grade_2
  reviewed: "1b11bc18..5ed929bd"
  human_commits_in_scope: []
  open_questions: []
  files_touched: []
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-1305-run-state-clobber/.harness/harness/features/BUG-1305-run-state-clobber/notes/review-harness-code-reviewer-c3.md
```
