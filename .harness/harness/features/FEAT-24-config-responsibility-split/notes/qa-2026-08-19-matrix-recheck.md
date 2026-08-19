# QA — test_matrix re-check — FEAT-24 — diff `ada8e99..0fa6315`, measured at HEAD `0fa6315`

## VERDICT: FAIL

Both of the dispatch's named blockers (T-05's missing INV-26 cases, the unclosed
`validate=True/False` fail-open) ARE confirmed closed at HEAD by direct re-run — that half of the
dispatch's premise holds. But two findings surfaced by this re-check, one of them from a
correction-under-advisor-review, keep `must_fix` non-empty:

1. **The unpinned `aGV!sbG8=` case (Task E)** — the only assertion that discriminates T-01's
   `validate` fail-open is named by no `verify:` block, so its deletion is invisible to every gate
   this feature runs. This is exactly the defect class FEAT-24 exists to remove, one level up from
   T-05's own marker positive-control.
2. **SC-02's `ready` key is unmet, not met** — mutation-proved below (Task D, corrected). My first
   pass credited `test-factory-config.py:626`'s `board_station` case, but that function is a
   key-agnostic passthrough (`stations[key]`); it is not the revertable site. Mutating the real
   call site, `factory_decompose.py:399`, to a hardcoded `"Ready"` reddens **nothing** in the suite.
   SC-02 is **4/5**, matching the dispatch's own prediction — my first-pass "5/5" was wrong and is
   corrected in place below rather than silently dropped.

`must_fix`: both items above. `matrix_ok: true` (per-`change_type` kind coverage, independent of
these two findings — reported below). `severity_max: medium` — a demanded pin missing and a
success-criterion measurement gap, neither of which is "the behaviour is wrong," but both of which
are real per this feature's own bar, so `PASS` with either standing would be the same fail-open
shape this feature exists to close.

Working tree matches the pin exactly: `git rev-parse HEAD` = `0fa6315`, no drift.

## Task A — T-05 verify, run verbatim

Cross-checked the dispatch's copy of T-05's `verify:` against `plan.yaml` byte-for-byte — identical,
no mismatch, `BLOCKED` not warranted.

Ran it live:
```
T-05 GREEN
FINAL_RC=0
```

Marker counts on `check-state.sh`, independent of the verify's own slice:
- `grep -c "INV-26 BEGINS"` = **1**
- `grep -c "INV-26 ENDS"` = **1**

One each, as the operator claimed — the two-`BEGINS` failure mode the dispatch warned about
(a mis-slice that still passes the `derive_station` positive control) does not apply here.

## Task B — are the three declared-station cases discriminating?

Source: `test-check-state.py:1596-1625`. The board fixture (`_renamed`) declares
`backlog: "Icebox"`, `building: "WIP"`, `done: "Shipped"` — all three differ from the DEC-192
literals (`Backlog`/`Building`/`Done`). This is not literally the `Col-A`/`Col-B`/`Col-D` naming
plan.yaml's intent prose used as illustration, but it satisfies the actual requirement it was
illustrating: non-DEC-192 values that a hardcoded literal cannot match.

The assertion shape is `_no_finding(out)` — "the run produced zero INV-26 findings" — rather than a
direct string-equality read of the declared value. This is a materially different shape from the
prose's "assert the violation text names the declared value," but I mutation-proved it discriminates
correctly (Task C below): a reverted `done` literal makes the `done` case's own card status
(`"Shipped"`) mismatch the hardcoded expectation (`"Done"`), producing a violation and reddening
`_no_finding`. Ruling: **discriminating**, by measurement, despite the prose/implementation shape
mismatch — noting the mismatch as a minor finding, not a defect.

## Task C — mutation proof, `revert only done`

Ran in a disposable worktree (`git worktree add /Users/molchairuangutai/GitHub/harness/.claude/worktrees/qa-feat24-recheck 0fa6315`,
removed after) per DEC-153 — `check-domain.sh` denies `harness-qa` writes to `check-state.sh` even
inside a worktree unless the path is given as an absolute path under `.claude/worktrees/`; a
worktree-relative argv string resolves against `CLAUDE_PROJECT_DIR` and gets treated as a main-
checkout write (learned live, not previously documented).

**Mutation applied and confirmed via diff** — `check-state.sh:1184`,
`"done": _st26["done"]` → `"done": "Done"`.

Result:
```
FAIL - INV-26 expects the declared station for status: backlog
    VIOLATION  INV-26 FEAT-X T-01 (issue #41): plan says done, so the card should
    read Done — the board reads Shipped.
ok - INV-26 expects the declared station for status: building
FAIL - INV-26 expects the declared station for status: done
```

**Discriminator, per the dispatch's own framing**: the `backlog` case's `FAIL` detail line names
**T-01**, the fixture's `done`-status task — not T-02, the `pending`/backlog task the case is
labeled for. Its own concern (the `pending`→`Icebox` card) is silently correct throughout; nothing
in the printed detail concerns it. This is **harmless fixture coupling**, not a mislabeled case: the
`backlog` case's assertion (`_no_finding` over the whole run) is a blanket "nothing went wrong"
check, and the fixture happens to also carry a `done` task because INV-26 requires at least one
non-`pending` task before it will judge a `pending` card at all (`test-check-state.py:1603-1604`
comment). Confirmed the reverse holds too: **`revert only backlog`**
(`"pending": _st26["backlog"]` → `"pending": "Backlog"`) reddens **only** the `backlog` case —
`building` and `done` both stay green. So the coupling runs one direction only (a `done` bug leaks
into the `backlog` case; a `backlog` bug does not leak anywhere), and the `backlog` case still
correctly and exclusively catches a `backlog`-specific bug per the operator's own table.

**Decoupling fix, one fixture change**: give the `backlog` case's first (started) task a `building`
status instead of `done` (mirrors the dedicated `building` case's shape). That trades the collision
with `done` for a new collision with `building` rather than removing it — INV-26's design (a `pending`
card can only be judged beside *some* started task) makes full decoupling from every other key
structurally unreachable with a single non-pending task. Not a `must_fix`: the case still meets its
own bar (fails when its own key is reverted; per the operator's table nothing else in the tree
depends on it being pure).

Reverted both mutations: `git status --porcelain` on the worktree — **clean**, before removal
(`git worktree remove --force`). Mutation applied and reverted with evidence at each step, not
inferred.

## Task D — SC-02 re-scored at HEAD, swept across the whole tree, corrected under review

**First pass (wrong, corrected below):** I initially credited `test-factory-config.py:626`
(`(29) board_station returns the per-repo ready option...`, `"Todo"` vs declared `"Ready"`) as
`ready`'s discriminating test, scoring SC-02 5/5. On review this does not hold:
`factory_config.board_station` is `stations[key]` — a key-agnostic dict lookup with no per-key
branch to revert. It cannot serve as evidence that the real, revertable *call site* reads from the
board rather than a literal.

**Mutation-proved the actual call site instead.** In a second disposable worktree
(`.claude/worktrees/qa-feat24-recheck2`, removed after), mutated
`factory_decompose.py:399` — `ready_option = factory_config.board_station(fleet, args.repo,
"ready")` → `ready_option = "Ready"` (a hardcoded literal, confirmed via diff) — and ran
`test-factory-decompose.py`. Result: **every `ready`-named case stays `ok`** — `(2) both stations
set to the fleet's ready option`, `(7) resume: the item's station is set to the ready option`,
`(T-03) the station set to A's own ready option (Ready), never B's (Other-Ready)` — none reddens.
Reverted (`cp` from `.bak`, `git status --porcelain` clean before `git worktree remove --force`).

So `ready`'s only production consumer (`factory_decompose.py:399`) has **no test that catches it
being reverted to a literal**. `test-factory-decompose.py:412-413`'s case (2) asserts `== "Ready"`
against a fixture whose own `ready` value is literally `"Ready"` (`:196,224`) — non-discriminating,
confirmed live rather than by re-reading source, and it is the reason the mutation above survived.

| key | discriminating test | status |
|---|---|---|
| building | `test-gh-board.py:194` `derive_station returns the declared building station` (`Col-B`) | met — pre-existing, unchanged |
| review | `test-gh-board.py:196` `derive_station returns the declared review station` (`Col-R`) | met — pre-existing, unchanged (though `test-factory-land.py:309,492`'s own review-station case is separately non-discriminating, `"Review"` vs fixture `"Review"` at `:58,95` — not blocking since `review` is covered elsewhere) |
| ready | none — `board_station`'s case is not per-key-revertable; the real call site's own tests do not discriminate (mutation-proven) | **unmet** |
| backlog | `test-check-state.py:1610` T-05 case (`Icebox`) | met — new this diff, mutation-proven (Task C) |
| done | `test-check-state.py:1624` T-05 case (`Shipped`) | met — new this diff, mutation-proven (Task C) |

SC-02: **4/5, unmet on `ready`.** This matches the dispatch's own stated prediction ("plausibly 4/5,
not 5/5") — my first pass over-credited a generic accessor test as if it covered the specific call
site, exactly the P-05/P-12-shaped error the harness-qa Expertise warns about (credit only what
exercises the real caller). Corrected here under advisor review rather than left standing.

## Task E — the unpinned ok-line

Confirmed: `file_at_ref: non-alphabet character in otherwise valid-length base64 raises`
(`test-factory-gh.py:960`, the `aGV!sbG8=` case) exists in the tree and is the discriminating case
for T-01 item 3's `validate=True`/`validate=False` fail-open. Grepped `plan.yaml` for this exact
string — **zero matches**, confirming it is pinned by no `verify:` block anywhere.

**Ruling: the requirement demands the pin.** T-01 item 3 requires "a content field that is absent or
does not base64-decode are all raises... A caller must never be able to mistake 'not there' for
'empty file'." The only case T-01's own `verify:` currently names for this
(`file_at_ref: undecodable content raises rather than returning empty`) cannot discriminate the mode
(both `validate=True` and `validate=False` raise on `"not-valid-base64!!!"`, confirmed in my prior
artifact). The `aGV!sbG8=` case is the only one that can — and it is the only assertion T-01's own
verify does not check for by name. Deleting it would be invisible to two independent replays: T-01's
targeted `verify:` (its `grep -E "^FAIL"` line only catches an assertion that *ran and failed*, not
one that never ran) and the full-suite run (nothing asserts an ok-line count, so fewer lines produces
no signal). This is the exact shape T-05's own marker positive-control was built to prevent, applied
one level up.

**Exact line to add**, in `plan.yaml`'s T-01 `verify:` block, immediately after the
`undecodable content raises` line:
```
has "file_at_ref: non-alphabet character in otherwise valid-length base64 raises" || { echo "T-01: the fail-open discriminator case did not pass or did not run"; exit 1; }
```
Not routed through `matrix_ok` (a pin gap is not a kind shortfall) — routed as a `must_fix`. Not
`matrix_ok: false` either, per the same rule I applied last run. This is `must_fix` because the
underlying behavior IS closed and correct — only the pin against silent deletion is missing — but
"only the pin is missing" is still a `must_fix` in a feature whose subject is exactly gates that
cannot see a deletion; see VERDICT above for why this keeps the gate at `FAIL` rather than `PASS`
with an advisory note.

## T-01 verify, run verbatim

Cross-checked against `plan.yaml:306-316` — identical, no mismatch.
```
T-01 GREEN
FINAL_RC=0
```

## Full suite

`run-unit-tests.sh --kind all`: `rc=0`, `FAIL` line count = **0**, `ok`/`PASS` line count = **1578**
(prior pin measured 1365 at `b0604c3`; part of the 213-line increase is a counting-method change —
this run's `grep -cE "^(ok|PASS)"` adds one line per `PASS <file>` summary line the prior grep did
not count — plus T-05's five new cases and the fixes landed since. Not reconciled line-by-line; the
`rc=0`/zero-`FAIL` pair is the load-bearing signal, not the raw count delta).

## Matrix — per change_type kind coverage, independently re-derived

| change_type | tasks | required kind | satisfied? |
|---|---|---|---|
| api | T-01 | unit (+ integration, `touches_db_or_external: true` per prior ruling) | yes — T-01 verify green, `test-factory-integration.py` exercises it live |
| cross_module | T-02–T-05 | unit/integration per task | yes — T-02/T-03/T-04 pre-ruled green and unchanged since; T-05 now green (Task A) |
| config | T-06–T-09 | per prior ruling, pre-ruled green | yes — measured, not typed: `git diff --stat b0604c3..0fa6315 -- .harness/harness.json .harness/factory/fleet.yaml .claude/skills/harness/bin/test-no-distribution.py .claude/skills/harness/templates/harness.json` is empty, confirming no code changed under these tasks since the prior pin |
| docs | T-10 | doc-check kind | yes — pre-ruled green, unchanged |

`matrix_ok: true` — the kind floor is satisfied for every task. This is independent of the two
`must_fix` items below, which are adequacy/pin gaps inside already-`matrix_ok` kinds, not kind
shortfalls.

`must_fix` (2): (1) pin the `aGV!sbG8=` case into T-01's `verify:` block (Task E — exact line given
above). (2) add a discriminating `ready` case at `factory_decompose.py:399`'s actual call site
(Task D) — e.g. a case asserting the board's declared `ready` value flows through when it differs
from `"Ready"`, mirroring T-05's non-DEC-192-literal fixture pattern. Both routed to the plan owner
(main-session/pm — plan.yaml amendment) and/or `harness-backend-dev` for the test addition; neither
is `matrix_ok: false`.

## SC evidence map (updated)

| SC | test | status |
|---|---|---|
| SC-02 | see Task D table | **unmet, 4/5** — `ready` has no discriminating test at its real call site, mutation-proven (matches the dispatch's own prediction; corrects my first-pass 5/5) |
| SC-03 | `test-gh-board.py` literal-grep + T-05's marker-sliced grep on `check-state.sh` (Task A, `T-05 GREEN`) | **met, both halves** (was unmet for check-state.sh half; now closed) |
| SC-12 | T-05's `INV-26 reports a violation...` / `INV-26 completes the gate...` cases | **met** (was unmet; now closed, confirmed live) |
| all others | unchanged from prior artifact (`qa-2026-08-19-matrix-gate.md`) | met, not re-run this pass — no code changed under them |

## Open questions

- `{ id: Q1, question: "Should T-01's verify: block in plan.yaml gain the aGV!sbG8= pin (Task E), and should plan.yaml amendments of this shape route through pm or be made directly given DEC-174 does not cover plan.yaml itself?", blocking: false }`
- Carried forward from the prior artifact, still open, not re-litigated per the dispatch's instruction not to re-open it: `{ id: Q2, question: "Should qa dispatches for this repo stop assuming test-file write access, or should the manifest grant qa a scoped test-file path?", blocking: false }`
