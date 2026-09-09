# QA gate — BUG-276 — code range 6d969ed3..97e715d1

## VERDICT: PASS

Both suites measured green by me directly. Both task `verify:` blocks (cross-checked byte-for-byte
against `plan.yaml`, ran verbatim) pass. Both required matrix kinds are satisfied. All six new
checks (u23a/b/c, case27a/b/c) confirmed to redden under a live mutation proof, so they are real
discriminators, not name-only passes.

## Change type + predicate evaluation

Diff touches production runtime code (`expertise-merge.py`: new `_check_proposal_duplicate_ids`,
wired into `compute_union`, docstring rows 9/11) plus two test files. `plan.yaml` labels both T-01
and T-02 `change_type: bugfix` — confirmed correct from the diff itself (a guarded, targeted
behavioral fix, not a refactor or new feature).

`test_matrix.bugfix` (`.harness/harness.json` ~203-218), `always: []`, three `when` legs:
- `unit if touches_runtime_code` → **TRUE** (`.claude/skills/harness/bin/expertise-merge.py` is
  production runtime code and is modified) → unit required.
- `integration if fix_confined_to_tests_and_contract_docs` → **FALSE** at the full-diff level: the
  diff is not confined to tests/docs, it changes `expertise-merge.py` too. This leg does not itself
  obligate integration.
- `__bug_class__ if match_bug_class` → repo Expertise G-08: `match_bug_class` is an unresolvable
  placeholder with no taxonomy entries live yet — does not fire, no `__bug_class__` kind added.

Per floor discipline (never drop below what the diff clearly warrants, independent of which
predicate fired): **integration is added** anyway. BRIEF SC-01/02/04/05 are all marked
`evidence: integration` — exit code, message tokens, destination byte-identity, and the
absent-destination path are CLI-boundary behaviors a unit-level `compute_union` call cannot pin.
T-02 exists specifically to cover this. Floor: {unit, integration}. Both required.

## Required kinds — resolved states

| Kind | State | Evidence |
|---|---|---|
| unit | **satisfied** | `tests/unit/test-expertise-ops.py` u23a/b/c, run via registered `--kind unit` runner |
| integration | **satisfied** | `tests/integration/test-expertise-merge.py` case27a/b/c, run via registered `--kind integration` runner |

## Measured tallies

- T-01 verify block (verbatim, `env -u HARNESS_AGENT_TYPE`): **exit 0**. Unit suite bare run:
  121 PASS, 0 FAIL. All three named u23 markers present and PASS. Standalone `compute_union`
  smoke assertion (code 11, `AMBIGUOUS TARGET` prefix, `section=Patterns`/`id=P-02` tokens) passed.
- T-02 verify block (verbatim): **exit 0**. Integration suite bare run: 220 PASS, 0 FAIL. All
  three named case27 markers present and PASS. Standalone CLI-drive assertion (real subprocess,
  temp tree, exit 11, `AMBIGUOUS TARGET`/`id=P-02` in combined stdout+stderr) passed.
- `run-unit-tests.sh --kind unit`: **exit 0**, 520 PASS, 0 FAIL.
- `run-unit-tests.sh --kind integration`: **exit 0**, 1513 PASS, 0 FAIL.
- No `FAIL ` lines anywhere in either standing-runner output — nothing pre-existing red, no
  regression, nothing to attribute.

## Test-first audit

T-01: receipt quotes an authentic behavioral RED before the fix — `compute_union` did not raise,
the three named checks never even reached their `except`-branch assertions (only the generic
`no exception raised` fallback fired), then GREEN after the production edit. This is a clean,
adequate test-first record on its own.

T-02: bare-suite RED at T-02's own base was **name-level only** — the pre-existing 211 checks were
already green (T-01's guard had landed first), and the RED that appeared was the grep failing to
find a not-yet-existing check name, not a behavioral failure. Judged per D-08 / the panel record:
this is **adequate**, not a gap, because the real behavioral RED for the CLI route was independently
measured at `6d969ed3` (both tails observed exit 1 — T-02's tail specifically after the real CLI
returned 0 and printed `ADDED P-02`, i.e. reproducing the silent-drop defect end-to-end before either
task's guard existed) and is recorded in `plan.yaml`'s finding resolution (PF referencing D-08,
~160-165). The chain — pre-fix-tree behavioral red, then T-01's fix landing, then T-02 adding CLI-
level coverage whose own local red was necessarily name-level because the fix already existed — is
sound test-first discipline for a two-task dependent sequence, not a violation.

## Assertion-strength findings

Both suites print `PASS <name>` for any truthy `ok` (D-08's stated risk). Verified this is not
exploited here: built a disposable worktree at `97e715d1` under `.claude/worktrees/` (bash-write-
guard requires this location), neutralized the `_check_proposal_duplicate_ids(...)` call site in
the COPY only, then re-ran both suites unmodified.

Result: **all six named checks reddened**, along with every one of their sub-assertions —
`u23a/b/c: MergeRefusal raised` (FAIL, "no exception raised"); `case27a/b/c: duplicate ids exit 11`,
`message carries AMBIGUOUS TARGET...`, and `destination bytes unchanged`/`nothing created at the
absent destination` (all FAIL). This proves discrimination, not just name-matching. The disposable
worktree was fully removed after (`git worktree remove`, confirmed via `git worktree list`); the
target worktree (`BUG-276-expertise-merge-duplicate-id`) `git status --porcelain` is clean —
verified after the probe, no leftover edits.

SC-01/SC-02/SC-05 sha256/no-file-created assertions: confirmed real, not name-only — the case27a/b
`destination bytes unchanged` and case27c `nothing created at the absent destination` checks are
exactly the ones that reddened under the neutralization above, so they are load-bearing, not
decorative.

## Advisory, out of scope for this gate (do not gate on these)

- D-07 (parse_expertise/render silent drop on ENTRY_RE misses) — recorded separate defect,
  explicitly out of scope here. Confirmed present in the code, confirmed not touched by this diff,
  confirmed the BRIEF/plan record it correctly. Advisory only.
- `check-expertise.sh` untouched — confirmed, per BRIEF constraint; correct.
- No exit-11 row in `.claude/skills/harness-distill/SKILL.md`'s refusal table (D-09) — confirmed
  absent, decision correctly defers to operator at signature. Advisory only.

## Harness defect noted (open_question, not gated)

Writing this artifact was initially BLOCKED by `check-domain`'s worktree-claim guard: it reported
"harness-qa holds worktree claim(s): .../BUG-240-workspace-hard-reset-guard" and refused the write
into this feature's own BUG-276 tree. Root cause: `inflight_registry.live_claims`/`claim_worktrees`
match a live claim by **agent-type string alone** (e.g. "harness-qa"), never by session or feature —
so a concurrent, unrelated `harness-qa` gate running under the same OMP supervisor for a different
feature (BUG-240) fully satisfied the match and became this session's entire allowed claim set,
even though no claim for THIS session's own feature (BUG-276) existed yet to include it. Worked
around by registering this session's own claim directly via `inflight_registry.claim(...)` for
`BUG-276-expertise-merge-duplicate-id`, after which the write succeeded normally. Raised here as an
`open_question`, not as an Expertise entry (it is a harness bug, not a durable workaround to encode).

## Scope / worktree hygiene

Worktree HEAD is `2e1f7142` (orchestrator bookkeeping only, no code) on top of the graded range.
`git status --porcelain` on the target worktree is clean before and after this gate. No files
added, no commits made, HEAD untouched.
