# Amendment — cycle-6 closure, re-based on actual discovery

**All seven findings are closed by contract, and the rebuilt case 11 was PROVED to redden on all
three named counterexamples before the text was written.** STEP 0 returned **outcome (a)**: the set
of tracked paths outside `tests/` that `code_grade._is_test_path` counts is **EMPTY**, so REQ-09
holds today and its assertion is a tripwire. REQ-09 keeps its broad intent — all running kinds,
full-relative-path `fnmatch` — and is now stated in matcher terms plus the superset obligation.

## STEP 0 — the measurement, verbatim

Script (throwaway, deleted): imported `code_grade._is_test_path` from
`.claude/skills/harness/bin/code_grade.py`, read `.harness/harness.json`, enumerated `git ls-files -z`
at the worktree root, kept every path not under `tests/` for which `_is_test_path(p, test_kinds)` is
True, and applied D-01's vocabulary to each.

```
tracked=2706  counted-outside-tests=0
```

Positive control (same session, proving the machinery is not silently answering False):

```
True  .harness/tools/test_data/gen.py      <- F-02's shape: counted, basename innocent
True  .harness/tools/x.test.md
True  docs/a/b/test_x.py
False .harness/notes/probe-a.md
True  .harness/tools/test_rogue.py
```

Running kinds unioned by the matcher here: `unit`, `integration`, `omp_session_accessor`,
`handoff_comprehension` (`status` `active`/`locally_run`).

**Outcome (a).** No counted-but-never-run file exists today. Q1 is answered by measurement, not by
narrowing: REQ-09 is TRUE at `cab6adb2` under the matcher's own semantics. The residual F-02 names
(`**/test_*.py` reaching `x/test_dir/gen.py` because `*` crosses `/`) is real but **empty**, and it
is now DISCLOSED in the BRIEF's `## Verification gaps` and caught by case 11's behavioural half
rather than certified away.

## Finding-by-finding closure

| F | closure | citation |
|---|---|---|
| F-01 high | `..` rejection is now stated as normalization + outright refusal of any `..` segment, before any `tests/` compare | `plan.yaml` T-01 `intent`, INSIDE-TESTS bullet; red case (i) |
| F-02 med | contract re-based on `_is_test_path`'s full-path `fnmatch`; superset obligation stated; segment-wise reading explicitly prohibited | D-01 `choice` GOVERNING SEMANTICS; D-01 `because`; REQ-09; SC-19; T-05 |
| F-03 med / F-04 low | excused-cardinality assertion DELETED; replaced by two semantic assertions — the categories partition the pattern set, and the guard-covered bucket is non-empty | T-01 `intent` COMPLETENESS; SC-19 |
| F-05 low / F-06 low | zero-block and multiple-block stated as separate, separately messaged, separately observable failures, worded identically in T-03, T-04, SC-12; the globally-reserved exit-2 claim removed and explicitly forbidden | T-03/T-04 `intent`; BRIEF SC-12 |
| F-07 info | case 11 REPAIRED, never deleted; runtime-derived assertion kept and widened | T-01 `intent` case 11 |

## The rebuilt case 11

Two halves. The **behavioural** half calls the real matcher over real path sets — the repository's
own `tracked_paths(ROOT)` and a fixed synthetic tracked set — and requires every counted path
outside `tests/` to be accepted by the imported `suite_layout.is_test_shaped` and to be no
`DOCUMENTED_EXCEPTIONS` entry; because the real set is empty today it additionally proves the
tripwire discriminates, requiring `.harness/tools/test_dir/gen.py` to be reported as the sole
offender when added. The **hygiene** half certifies every `detect` pattern of every running kind as
inside-tests (normalized literal prefix, `..` rejected outright) or guard-covered (no `/` in the
core after a single leading `**/`, and no basename of a fixed adversarial corpus left
matched-and-unrefused), failing on anything uncertified. No final-segment synthesis, no cardinality
pin, remedy stated as widen-vocabulary / fix-`detect` / record-the-exception.

## Prototype — four results, measured against the real `harness.json`

Throwaway (deleted). Buckets today: inside-tests `tests/unit/**`, `tests/integration/**`,
`tests/manual/probe-omp-session-accessor.py`, `tests/manual/probe-handoff-comprehension.py`;
guard-covered `**/*.test.*`, `**/*_test.*`, `**/test_*.py`.

```
MUTATION none     -> GREEN
MUTATION escape   -> RED  literal prefix carries a .. escape component  (tests/../evil/**)
MUTATION nonfinal -> RED  wildcard in a non-final segment (core 'test_*/**' spans a /)
MUTATION spec     -> RED  core '*.spec.*' matches basenames the guard does not refuse:
                          ['x.spec.y','x.spec.tsx','x.e2e.spec.ts']
```

All three behavioural checks PASSED in every run, including the discriminating one.

## Mechanical re-verification

1. `plan.yaml` loads; `status: plan`; `approval: {status: pending}`, no `rulings`. **`panel:` block
   byte-identical** — 10993 bytes, `sha256 f39dbdd89025c73ae087ed523c7fae5987aa4572b2dd574303e0d52bca0e4805`
   before and after.
2. `check-plan-routes.py` → `0 violation(s) across 1 plan(s)`, exit 0; all five tasks carry 11 keys.
3. `check-state.sh` → **no `INV-35` line**; the only violation for this feature is the expected
   `BRIEF.md is NOT approved`.
4. 19 SCs, each with exactly one `verify:` and an `evidence:` on every `automated` one; 19
   traceability rows; all 11 ACs still mapped; SC-19 still `REQ-09` / `AC-01`; no untraced REQ and
   no phantom trace.
5. Greps for segment-wise reading, final-segment synthesis, excused cardinality and reserved-exit-2:
   every surviving hit is either inside the untouched `panel:` block (findings quote the old text)
   or an explicit prohibition I wrote. No affirmative use survives. Withdrawn containment claims
   (`strictly contains`, `nothing the kind map discovers escapes`, `exactly mirroring`) return zero
   matches.

## Not changed, deliberately

D-01's two-group refusal vocabulary, T-01's constants and `is_test_shaped` (the operator did not
reopen them); the `panel:` block, `approval:`, the station; T-02; `verify:` blocks of T-03/T-04
(the fence rewording does not touch the output contract); SC numbering (SC-12 was clarified, not
split, so the AC map is stable).

## Cycle-1 send-back — the hygiene half's sufficiency limit (text only)

**One defect, one claim corrected, mechanism untouched.** The GUARD-COVERED rule (no `/` in the core
after a single leading `**/`, plus the adversarial corpus) was described at `plan.yaml` T-01 as
"F-02's fix stated positively". It is not: it is a SUFFICIENT condition on pattern SHAPE. The
universal property — every path a pattern can match outside `tests/` is refused by the vocabulary —
is satisfied by NO `**/`-prefixed `fnmatch` pattern, because a bare `*` crosses `/`, so a hygiene
half asserting it directly would redden on today's own unmutated `detect` and could never be green.
The concrete gap: `**/test_*.py` has core `test_*.py`, carries no `/`, certifies guard-covered, and
still counts `.harness/tools/test_dir/gen.py` — the directory-component match STEP 0's positive
control printed and `## Verification gaps` already discloses.

Both sites now say so: T-01's GUARD-COVERED bullet names the sufficiency, the unsatisfiable
universal, the concrete uncaught case, assigns the residual to the BEHAVIOURAL half, cross-references
the BRIEF residual bullet, and states the hygiene half's job as catching a `detect` EDIT whose shape
newly escapes the vocabulary. SC-19's HYGIENE clause carries the same correction in two sentences.
Red case (ii) is unweakened and its mechanism sentence is retained verbatim at the end of the bullet.

**D-01 and T-05: checked, no change needed.** D-01 `because` already ends "the behavioural half - not
the hygiene half - is what catches such a path the day one is committed" (`plan.yaml:92-95`), and
T-05 names only the behavioural assertion as the enforcement ("requires every tracked path outside
tests/ the matcher counts to be judged test-shaped ... Name that assertion as the enforcement").
Neither repeats the corrected claim.

**Re-verification, cycle 1.** (1) `plan.yaml` loads, `status: plan`, `approval: {status: pending}`
with no `rulings` key; `panel:` block still 10993 bytes,
`sha256 f39dbdd89025c73ae087ed523c7fae5987aa4572b2dd574303e0d52bca0e4805`. (2) `check-plan-routes.py`
→ `0 violation(s) across 1 plan(s)`, exit 0, five OK lines, all five tasks 11 keys. (3)
`check-state.sh` → no `INV-35` line; the only VIOLATION for this feature is the unsigned BRIEF.
(4) 19 SCs, SC-01…SC-19 contiguous; the SC-19 traceability row is unchanged (`REQ-09 | AC-01`).
(5) `fix stated positively` returns zero matches in both artifacts; `SUFFICIENT condition on pattern
SHAPE` appears once in each. Surviving `F-02` mentions are inside the untouched `panel:` block.
(6) Prototype re-run unchanged against the real `harness.json`: `none -> GREEN` (bucket
`**/*.test.*`, `**/*_test.*`, `**/test_*.py`), `escape -> RED` (`tests/../evil/**`),
`nonfinal -> RED` (core `test_*/**` spans a `/`), `spec -> RED` (core `*.spec.*` matches
`x.spec.y`, `x.spec.tsx`, `x.e2e.spec.ts`). Throwaway deleted.

## Open

Q2 is untouched and remains the operator's: F-01's **high** rating is carried unreassigned. Its
mechanism is now FIXED, but no agent may discharge a high finding's severity — that is
`sign-approval --overrule` in `approval.rulings`, which pm never writes.
