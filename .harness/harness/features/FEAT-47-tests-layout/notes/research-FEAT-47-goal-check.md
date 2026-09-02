# Goal-check — FEAT-47 tests-layout — pinned `43fd04b9`

Graded at `review_sha 43fd04b9fc1aa191d37d7408221f7d5df67e3507` over base
`388884494430857f5c383ee41540260e7e4e199e` (two commits: `139f6afe` the move, `43fd04b9` the review
fixes). Working tree clean but for the two review-pin metadata files. Read-only; nothing edited.

## BLUF

**All ten success criteria are met, and REQ-07 is not.** Every SC has evidence re-derived in this
session at the pinned sha, not inherited: the strict verdict-line census exits 0 over 66 files, the
migration conservation law exits 0 against a base of 65 with `bin/` holding zero `test-*.py`, the
child-process probe was re-run in full for the first time, and the four layout-violation cases and
the sole-implementation sweep both pass. The gap is one live Expertise entry that still presents the
deleted mechanism as current — the same class of finding the pinned reviewer raised as F-1
must_fix, repaired in three of the four files it named and missed in a fourth nobody looked at.

## The unmet requirement — REQ-07

`.harness/harness/expertise/harness-pm.md:17` at `43fd04b9`, gotcha **G-08**: *"…DO account for two
run-unit-tests.sh gates: a per-kind one-directional KIND-DRIFT cross-check against harness.json
detect, and a file-presence check flagging any on-disk test file in neither script array."*

Both named gates were deleted by this feature. The file is repository-tier Expertise for this
checkout, injected into every `harness-pm` spawn as current craft, and it sits inside the
`.harness/*/expertise/*.md` glob T-07 declared — T-07 rewrote **P-01** in this same file and left
G-08 standing. It is not a record path REQ-07 exempts.

Nothing catches it: `RESIDUE_TOKENS` is a literal sweep for `UNIT_SCRIPTS`, `INTEGRATION_SCRIPTS`
and `check-kinds`, and G-08 spells the mechanism out in prose ("script array", "KIND-DRIFT") without
any of the three tokens. SC-07 is written to those tokens, so **SC-07 greens while REQ-07 fails** —
the criterion cannot see its own requirement's residue. That is a disclosure worth carrying into
#979, not a reason to soften the verdict.

Remedy: rewrite G-08 to the directory-is-kind mechanism (`suite_layout.violations()` /
`run-unit-tests.sh --check-layout`), inside `.harness/harness/expertise/harness-pm.md`. One entry,
one edit. Then re-run `tests/manual/suite-census.py residue --ref <new sha>` (unchanged result — it
never saw this line) and re-read the file: the sweep is not the check here, a reader is.

**Advisory, operator's call, not graded:** `.harness/expertise/harness-dev-ops.md:3` P-02 counsels
keeping "an explicit list" and "a glob-based drift detector" separate because collapsing to
glob-and-run "silently disables drift detection". Phrased as cross-repo craft, so it asserts nothing
false about this tree, but it is advice against exactly what DEC-213 chose. Not a REQ-07 breach.

## SC outcomes — every verdict re-derived at `43fd04b9`

| SC | Verdict | Method | Evidence |
|---|---|---|---|
| SC-01 | met | automated | `suite-census.py verdict-lines --strict` exit 0; all 23 `tests/unit` rows `expected==actual`, per-file `exit=0`. Set equality is structural: `run-unit-tests.sh:25` builds `SCRIPTS` from the `tests/unit/test-*.py` glob itself |
| SC-02 | met | automated | same run, all 43 `tests/integration` rows matched, per-file `exit=0`; `run-unit-tests.sh:26` |
| SC-03 | met | automated | `test-check-domain.py:1861-1874` asserts each verdict individually (3 seats × 2 dirs granted, 3 seats denied `tests/unit`, qa denied `bin/*.sh`); replicated live via `check-domain.sh --resolve` over 6 seats × 3 paths |
| SC-04 | met | automated | `tests/integration/test-run-unit-tests-layout.py` 9/9 PASS, exit 0 — empty-unit, empty-integration, duplicate, planted, plus clean-tree and argv refusals |
| SC-05 | met | automated | `tests/unit/test-suite-layout.py` 21/21 PASS, exit 0 — discovery floor, sweep, both positive controls, 3-shape red proof, `runner delegates layout once` |
| SC-06 | met | automated | `.harness/harness.json` `unit`/`integration` `detect` byte-equal to `templates/harness.json`; `unit detect excludes .claude` and its integration twin assert the appendix cannot return |
| SC-07 | met **as written** | inspection | `residue --ref 43fd04b9` exit 0, exactly the three declared exemptions `covered`, no fourth mention; DEC-213 present; DEC-187 and DEC-197 rewritten to the new mechanism; `gen-decisions-index.py --stdout` byte-identical to the committed index. Blind to REQ-07's residue above |
| SC-08 | met | automated | only `omp_session_accessor` (`status: locally_run`) names `tests/manual/`; `unit`/`integration` are the sole `active` kinds; asserted by `manual tests are not actively detected` |
| SC-09 | met | inspection | **`suite-census.py children` re-run in full at this tree** (66 rows — the prior evidence was a 3-file spot check at an earlier tree). Every one of 43 integration files spawns ≥1 child; all 23 unit files spawn 0, or only `git` (`test-code-grade` 118, `test-no-distribution` 4, `test-suite-layout` 1), `fake-gh`/`fake-gh-fail` (`test-gh-board` 3), `bun` (`test-omp-hooks` 1) — all declared fixtures |
| SC-10 | met | inspection | `migration --base 38888449 --floor 58 --deleted test-run-unit-tests-kinds.py` exit 0, `base test count: 65`; `git ls-tree -r 43fd04b9 .claude/skills/harness/bin/ \| grep -c '/test-.*\.py$'` = **0** |

**Files with no baseline row, named here rather than failed** (SC-01's own rule): 7 —
`test-check-fixture-secrets.py` 16, `test-plan-sign-gate.py` 58, `test-quarantine.py` 36,
`test-run-pool.py` 13, `test-run-unit-tests-layout.py` 9, `test-suite-independence.py` 7,
`test-suite-layout.py` 21. Four arrived with siblings; three this feature wrote.

## REQ coverage

REQ-01, 02, 03, 04, 05, 06, 08 — met; traced through the pinned review's stage-1 table and
independently re-derived above (REQ-02 by the runner's globs, REQ-04 by the conservation law,
REQ-05 by SC-04's nine cases, REQ-08 by the `locally_run` registration). **REQ-07 — not met**, above.

## A false red future graders must not repeat

My first strict census reported `test-plan-merge.py expected=285 actual=273 exit=1`. It is not a
defect: with `HARNESS_AGENT_TYPE=harness-pm` in the environment, `plan-merge.py cmd_sign_approval`
refuses itself per DEC-120 and 12 cases fail. `env -u HARNESS_AGENT_TYPE python3
tests/integration/test-plan-merge.py` exits 0 at exactly 285 lines, and the clean full census exits
0. `.harness/harness/expertise/harness-qa.md` G-07 already records this; strip the agent env before
citing any suite figure at this sha.

## Open

- REQ-07's repair is one Expertise entry; it lands, then re-pin. Nothing else blocks.
- SC-01's and SC-02's verdict-line evidence and SC-09's probe are point measurements at this sha, as
  the BRIEF's Verification gaps already disclose. Any later commit — including the REQ-07 fix —
  leaves them true of `43fd04b9` and unre-derived. The fix touches no test file, so only the sha
  moves.
- No `verify: uat` criterion exists, so there is no UAT script and no user-executed gate here.
