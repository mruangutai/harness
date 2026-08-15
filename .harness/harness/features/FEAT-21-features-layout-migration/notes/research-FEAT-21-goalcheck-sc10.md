# SC-10 re-verification at `b1d3925` — FEAT-21 goal-check cycle 2

**SC-10 is met.** The parity case is bidirectional: I mutated each rendering *alone*, five times,
and case 20 reddened every time — including the three gate-side mutations that cycle 1's hand-written
mirror was blind to. Scope: SC-10 only. The other thirteen criteria stand as verified at `d033b9d` in
`runs/2026-08-14-2-goalcheck-product/`; nothing here re-opens them.

## Tree provenance

Working tree HEAD is `835692a`. `b1d3925` is an ancestor of it, and
`git diff --stat b1d3925 HEAD -- .claude/skills/harness/bin/` is **empty** — the entire `bin/` tree,
not just the one changed file, is byte-identical between the pinned sha and the tree I measured. Every
measurement below therefore holds at `b1d3925`.

## The reading — does SC-10 require every cause to travel the real gate?

**No.** Recorded explicitly, because a reading was made rather than assumed.

SC-10 (`BRIEF.md:126-129`) binds two properties: the two renderings "name the same reader set and the
same cause for the same input", and the test "reddens if either rendering is changed alone". It
quantifies over *inputs*, not over the module's cause enum. "A CANNOT_VERIFY report for each cause
value the module defines" is T-01 `intent:` text, not criterion text — and the same `intent:` also says
"do not go through a fixture tree", which the prior run's `must_fix` explicitly displaced by sanctioning
the fixture-tree route as one of two acceptable remedies. The intent block was written before that
remedy existed; it cannot both forbid the fixture tree and demand exhaustive cause coverage through it.
That is criterion/intent **wording drift** — the Q3 class filed last cycle — not a coverage gap, and the
criterion is what is graded. The remedy side closes the same argument independently: the `must_fix`'s
*other* sanctioned remedy — move the composition into `layout_migration.py` so both call sites share one
owner — runs no gate at all, so a reading that demanded every cause travel the real gate would have made
both sanctioned remedies non-compliant on arrival.

Consequence, stated so it is not silently assumed: no `check-state.sh` hook is needed, and no DEC-174
carve-out change is on the table for SC-10.

**What the uncovered cause actually costs.** `no-rows` is one of five causes `cause_text` defines
(`layout_migration.py:284-300`). Its wording *is* pinned on the module side —
`test-layout-migration.py:266-274` (case 16) drives it via a reader-table override and asserts the exact
phrase "no reader rows for this surface". It is **not** pinned at the gate call site: `case_x` in
`test-check-state.py:1587` covers mixed, a generic CANNOT VERIFY, two absence cases and the unimportable
case, never no-rows specifically. The residual is small and nameable: the gate's CANNOT_VERIFY branch
(`check-state.sh:1319-1323`) is a single f-string interpolating `cause_text` with **no per-cause
branching**, so the only defect this misses is a cause-specific post-filter that does not exist and
would have to be deliberately added. The test's comment near `:396` claims the gap is carried by
`case_x` and `cause_text` unit coverage; per P-09 I read the assertions rather than the comment — half
that claim (the `cause_text` half) is true, the `case_x` half is not.

## What I ran

1. **T-01's `verify:`, its own text.** Cross-checked verbatim against `plan.yaml:248-253` — exact match
   including the `|` literal block. Executed the same runner and the same two greps (the runner call was
   made through a python `subprocess` capture rather than a `>"$u"` shell redirect; see Q2). Result:
   runner **exit 0**, `PASS test-layout-migration.py` present, a case label containing "parity" present.
   T-01's verify still holds for this file.
2. **The hand-written mirror is gone.** `git show b1d3925:.claude/skills/harness/bin/test-layout-migration.py
   | grep -c _inv27_text` -> **0**. Re-derived, not adopted.
3. **The gate really is the gate.** `_CHECK_STATE = os.path.join(HERE, "check-state.sh")` is invoked via
   `subprocess.run(..., cwd=tmp, env CLAUDE_PROJECT_DIR=tmp)` and the INV-27 lines are filtered out of
   real stdout; the CI side is `lm.render(lm.scan(tmp))` over the same tree. The gate consumes
   `blame_text`/`cause_text` directly and assembles its own line — it does **not** call `render()`, which
   is what makes "either rendering changed alone" a reachable mutation on both sides.
4. **Bidirectional mutation proof.** `bin/` copied to a scratch dir. Baseline: case 20 = **10 assertions,
   0 FAIL** (the copy also fails three case-1 assertions because case 1 scans the real repository root,
   which a copy outside the repo cannot see — a location artefact, same as the lead's; my verdict is
   scoped to case 20's own assertions). Every mutation was asserted to have applied (exactly one
   occurrence replaced, re-read after write) before its result was believed. The live tree was never
   touched.

| # | Side changed alone | Mutation | case-20 FAILs |
|---|---|---|---|
| M1 | gate (`check-state.sh` MIXED branch) | drop the last blamed reader from `blame_text` output | 1 |
| M2 | gate (`check-state.sh` CANNOT_VERIFY branch) | drop the last blamed reader from `_named` | 2 |
| M3 | gate (`check-state.sh` CANNOT_VERIFY branch) | replace `cause_text(...)` with a constant | 4 |
| M4 | CI (`layout_migration.render`) | drop the last reader from the `readers:` clause | 3 |
| M5 | CI (`layout_migration.render`) | replace the cause clause with a constant | 4 |

M1-M3 are exactly the direction cycle 1 proved blind (`sc_status` SC-10 at `d033b9d`: "the same drop
inside check-state.sh leaves case 20 at 0 FAIL"). They now redden. M4-M5 change only `render()`, which
no call site shares, so they are CI-only by construction. Both directions hold, on both properties
(reader set and cause clause).

## Residual weaknesses, recorded rather than hidden

- The CLEAN case asserts `gate_named == ci_named` where both are empty — a true statement that two
  broken renderings would also satisfy. It is a control, not a discriminator. M1-M5 carry the case's
  actual detection power.
- MIXED asserts the reader set only, never a cause — correct, MIXED reports carry no cause.
- Five of six covered cases redden under at least one mutation; the `no-rows` gate-side residual is
  sized above.

## Open questions

- **Q1 (non-blocking, wording):** T-01's `intent:` still says "construct SurfaceReport values directly -
  do not go through a fixture tree", which the sanctioned remedy displaced and the shipped code
  contradicts. The task is `status: done` and I do not edit `plan.yaml`; recorded so a later reader does
  not treat the intent block as the live instruction. Same class as last cycle's Q3.
- **Q3 (non-blocking, out of scope by dispatch):** SC-12 requires everything this feature changes to
  land in exactly two commits. `b1d3925` is a **third** commit touching a source file
  (`test-layout-migration.py`, 61+/64-). SC-12 was graded met at `d033b9d`, before that commit existed,
  and this dispatch does not re-open it — so this is flagged for the operator, not re-graded. Fixing
  SC-10 is what created the collision; the same collision was noted in commit `649b36b`'s subject.
- **Q2 (non-blocking, design consequence — intended?):** `bash-write-guard.sh` blocked `... >"$u"` from
  T-01's own `verify:` with `redirect targets "xx", outside your domain`. I read the guard rather than
  guessing: `mask_quoted` (`bash-write-guard.sh:155-179`) blanks the *contents* of every quoted span to
  `x`s by design, deliberately keeping the redirect visible so a quoted target still blocks —
  documented as failing safe. So this is **not** a variable-resolution bug; it is the designed
  fail-closed path, and it applies to **any quoted redirect target**, literal or variable. The
  consequence worth the operator's ruling: a plan `verify:` written with a quoted redirect is
  unrunnable as written by the role that authored it, and the only workarounds are an unquoted target
  or another tool. I ran the identical runner and the identical two greps through a python subprocess.

## What is NOT in scope here

Q2-Q5 from `runs/2026-08-14-2-goalcheck-product/digest.md` (SC-02 self-reference, the three wording
drifts, the SC-06 regression-case suggestion, STATE.md's Q-D) remain with the operator, untouched.
SC-12 counts commits and `b1d3925` is a third work commit in this feature — that is a **cycle-2 fact
about a criterion verified at `d033b9d`**, outside this dispatch's scope; flagged, not re-graded.
