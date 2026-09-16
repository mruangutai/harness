# QA gate — BUG-1699 c2 exact tip

## Verdict

FAIL — GC-01 / SC-11 is repaired at exact head `0274000f47a4c3ab3011b4ddaef295ac50c2f275`, but the required configured integration matrix exits 1. The manifest divergence is proven external to c2; it remains a non-green required matrix command, so this QA gate cannot pass.

## Scope and delta

- Checked `HEAD` exactly equals `0274000f47a4c3ab3011b4ddaef295ac50c2f275` and `tests/unit/test-gh-board.py` is clean at that tip.
- `git diff --name-status d7310f865e03534c233085e5f0a768eb9eca4687..0274000f...` contains only `M tests/unit/test-gh-board.py` and the c2 developer receipt. The code commit is `968b791b`.
- The exit decision now follows every assertion at `tests/unit/test-gh-board.py:467-471`; this covers the active/terminal projection checks at `:427-466` required by GC-01.

## Independent fail-first / mutation proof

Disposable linked worktrees were restored after the proof.

| Subject | Deliberate false assertion location | Result |
|---|---|---|
| pre-fix `d7310f8` | immediately after former exit block (`test-gh-board.py:408-412`) | prints `FAIL c2 QA negative control...`; `EXIT:0` |
| repaired `0274000` | equivalent late location after the former exit block | prints the same false assertion and `1 FAIL`; `EXIT:1` |
| restored repaired tip | unmodified focused runner | `all pass`; exit 0 |

This is the SC-11/GC-01 fail-first evidence: the actual former late-assertion precondition fails open before the repair and is load-bearing after it.

## Executed verification

| Gate | Result |
|---|---|
| `python3 tests/unit/test-gh-board.py` | exit 0, `all pass` |
| Signed T-01 command, verbatim from `plan.yaml:130` | exit 0; unit runner and all six named integration scripts passed |
| `.agents/skills/harness/bin/run-unit-tests.py --kind unit` | exit 0; 40 files |
| `.agents/skills/harness/bin/run-unit-tests.py --kind integration` | exit 1 solely in `test-check-plan-routes.py`; all BUG-1699-owned named checks, including all seven signed T-01 scripts, passed |

## Matrix disposition

T-01 is `cross_module` (`plan.yaml:113`), whose configured floor is unit plus integration (`.harness/harness.json:174-178`). Unit is satisfied. Integration is externally divergent, not a BUG-1699 c2 regression: the runner's six assertion failures are `test-check-plan-routes.py` cases 04, 05, 15, 17, 19d, and 19d2, each reporting the same manifest deviation. Concrete comparison shows only `/Users/molchairuangutai/GitHub/harness/.harness/team-config.yaml:171` has an additional frontend dashboard-client grant compared with this worktree's `.harness/team-config.yaml:171`; `git diff --quiet d7310f8..0274000 -- .harness/team-config.yaml` succeeds. The worktree copy's last path commit at the original pin is `da63e38d`, which is an ancestor of `d7310f8`. Thus the divergence predates and lies outside the c2 fix delta. Nevertheless, the required configured integration command is red; matrix_ok is false until its control-plane/worktree manifest divergence is reconciled and the command is rerun green.

## Phase-1 delta and findings

Phase 1 required a focused SC-11 runner test whose deliberately false late assertion returns non-zero, plus a green run and the cross-module unit/integration floor. Phase 2 found all c2-owned expectations covered. No coverage gaps.

- kind: form
  finding: The configured integration command exits 1 because its control-plane route test compares the worktree manifest with a newer control-plane manifest. The failure is external to c2 by the path/range evidence above, but it leaves the required matrix command red.

```yaml
VERDICT: FAIL
DIGEST:
  headline: GC-01 is repaired, but the required integration matrix remains red on external manifest divergence.
  suite: fail
  failures: 6
  matrix_ok: false
  kinds:
    - { kind: unit, state: satisfied, cmd: ".agents/skills/harness/bin/run-unit-tests.py --kind unit", named_tests: 40 }
    - { kind: integration, state: missing, cmd: ".agents/skills/harness/bin/run-unit-tests.py --kind integration (exit 1: test-check-plan-routes manifest divergence)", named_tests: 7 }
  coverage_gaps: []
  sc_evidence:
    - { id: SC-11, test: "tests/unit/test-gh-board.py:427-471" }
  fail_first:
    - { sc: SC-11, evidence: "qa-fix-c2.md:22-26; pre-fix d7310f8 late false assertion EXIT:0, repaired 0274000 equivalent assertion EXIT:1" }
  open_questions: []
  files_touched: [".harness/harness/features/BUG-1699-lifecycle-cards/notes/qa-fix-c2.md"]
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-1699-lifecycle-cards/.harness/harness/features/BUG-1699-lifecycle-cards/notes/qa-fix-c2.md
```
