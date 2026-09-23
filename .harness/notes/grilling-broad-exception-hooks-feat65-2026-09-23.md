# Grilling — broad-exception sweep, wave 4 part 2: the eleven hooks (FEAT-65) — 2026-09-23

Continues `grilling-broad-exception-wave4-2026-09-22.md`, whose Destination, posture ruling and
out-of-scope list stand unchanged. This sitting settles the two fog items that artifact left and
the shape questions FEAT-64's build surfaced.

## Destination
The eleven hook scripts `harness-hooks.ts` invokes carry zero `except Exception` / bare `except`
(77 sites at main `4e8c73c0` → 0); every hook's own-failure posture is spelled once through
`harness_boundary.hook_guard`, unchanged in verdict per hook; `BROAD_CATCH_CEILINGS` becomes
`harness_boundary.py: 2` and nothing else; DEC-234's five bootstrap prologues are back in step.

## Mission
mission: plan
reason: cause known and diff bounded (11 files, 77 sites, 4 tasks), but it changes an enforcement surface every hook runs under — wires hook_guard, deletes eleven operator-visible lines, retires rule-level absorbs, edits DEC-234's copied prologues — so rule 3 (no new enforcement surface) fails.
confirmed-by: operator — main-session-direct under DEC-174, as FEAT-64.

## Settled
- Own-failure line → **one template, only the name slot varies**:
  `<name>: the hook failed internally (<Type>: <msg>) — passing through; this is not a pass, nothing was checked.`
  (or `hook_guard`'s BLOCKED form for check-domain's boundary-load path). Each hook's current
  pass-through sentence is deleted; every deletion is a ledgered byte divergence (old / new /
  this ruling); tests that pin the old sentence are re-pinned to the template. The operator's
  expected action on seeing it: know enforcement was off for that action, then fix the hook.
- inflight_registry's process-identity probes (`/proc/<pid>/stat` + `/proc/stat`; `ps -o lstart=`)
  → **narrow to the probes' real classes, keep the `None`**: `(OSError, ValueError, IndexError,
  StopIteration)` and `(OSError, subprocess.SubprocessError, ValueError)`; liveness still falls to
  the 24-hour backstop; no new typed error.
- DEC-234 prologue copies → **narrow the four gate copies** (`branch-create-gate`, `gh-close-gate`,
  `merge-gate`, `plan-sign-gate`) to `(ModuleNotFoundError, ValueError)` byte-identical to
  run-unit-tests' copy (its FEAT-64 comment moved verbatim), **plus a lock test** that the five
  prologues are byte-identical so they cannot drift a third time.
- Task shape → **four tasks**: T-01 check-domain (24 sites, 8 suites); T-02 validate-digest (18,
  2 suites); T-03 the nine small hooks (35 sites, one suite each) incl. the four prologue copies;
  T-04 census (ceilings → `harness_boundary.py: 2` only), prologue lock, receipts, divergence
  ledger. All `main-session-direct`, `cross_module`.
- check-domain's rule-level absorbs ("a bug in this rule must not flip the verdict", e.g. :710,
  :1375) → **delete them; a rule defect reaches the outer `hook_guard`** (pass-through, loud). The
  "never blocks on its own bug" intent survives because pass-through never blocks; the comments
  move to the ledger as the ruling that retired them. No second designed idiom; ceiling stays 2.
- Mission → plan, main-session-direct (above).

## Not yet specified
- Which of check-domain's 24 sites are the outer own-failure idiom (→ `hook_guard`), which are
  boundary silences with real classes (→ narrowed), and which are rule-level absorbs (→ deleted).
  The classification is pm's per-site table from the receipts; the three treatments are settled.
- Whether `validate-digest`'s three "internal error validating … — passing through" sites
  (:2164, :2385, :2541) collapse to one `hook_guard` or stay three call sites of it — depends on
  its `main` shape, which pm reads.

## Out of scope
- Any change to a hook's fail-open/closed verdict (wave-4 ruling; separate later ruling).
- Editing `.omp/extensions/harness-hooks.ts`.
- The grader / review-skill extension (the wave after this one).
- #1882 identity-less claim binding and #1898 pm-child-without-claim: host/registry defects,
  their own lanes.
- Turning any environment-related silence into a finding.

## Facts I verified (so pm does not re-derive them)
- Hook broad catches at main `4e8c73c0` by AST (`except Exception` or bare `except:`): 77 —
  check-domain 24, validate-digest 18, dispatch-guard 9, bash-write-guard 6, merge-gate 5,
  branch-create-gate 4, gh-close-gate 3, inflight_registry 3, inject-expertise 2,
  plan-sign-gate 2, feature-record 1. `BROAD_CATCH_CEILINGS` carries exactly these eleven
  entries plus `check-state.py: 0` and `harness_boundary.py: 2`.
- The operator's branch `skills/optimization-pass` carries a 10th dispatch-guard broad catch
  (`bc8829ba`, not on main). When it lands after FEAT-65, the census will refuse it; that catch
  must be narrowed in the same landing (ceiling will be 0). Not FEAT-65's file to edit.
- `harness_boundary.hook_guard(main, name, fail="open"|"closed")` exists since FEAT-64
  (`c8dd3479`), tested in `tests/unit/test-harness-boundary.py` (returns main's result; open → 0 +
  line; closed → 2 + BLOCKED; KeyboardInterrupt/SystemExit escape); called by no hook
  (`hook_guard_is_called_by_no_hook_in_FEAT-64` pins that — FEAT-65 deletes/inverts that case).
- Prologue state: run-unit-tests (FEAT-64) and check-state (FEAT-63) copies read
  `except (ModuleNotFoundError, ValueError)`; the four gate copies still `except Exception` —
  DEC-234's "all five together" is currently breached.
- inflight_registry's third broad site (`feature_root`, :317) wraps
  `harness_boundary.worktree_for_feature` → falls back to owner root; its real classes are
  `AmbiguousWorktree` and `OSError`.
- check-domain's own-failure posture at main: pass-through exit 0 everywhere except the
  boundary-module load (:162, :354 — `BLOCKED … exit 2`), the manifest-parse block (:179), and the
  rule-level absorbs listed above.
- validate-digest's own-failure sites: :2164, :2385, :2541 print `check-digest: internal error … —
  passing through` / `unreadable hook payload … — passing through`, exit 0.
- Test suites per hook: check-domain ×8 (`tests/integration/test-check-domain*.py`),
  validate-digest ×2, one suite per remaining hook/gate; plus `tests/unit/omp-hooks.test.ts` for
  the TS side (not edited).
- Small lanes closed before this sitting: #1895 (`main-session` persona → dev) so FEAT-65's
  direct build run closes through `close-run`; #1897 (board_lifecycle GhError) merged `4e8c73c0`.
