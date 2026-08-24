# FEAT-35 re-review — cycle c3 — pin `a2a373b`

Scope per dispatch: re-check SC-01/02/04 (fresh, not carried forward) and full RE-GRADE of SC-06 at
`a2a373b1ef351f94b0a4310bea928f1384727a08`. SC-03, SC-05, SC-07 not graded here. c0/c1/c2 verdicts
describe superseded text and are **not** carried forward.

## Verdict: PASS with one MED finding (SC-06 calibration text)

## SC-01, SC-02, SC-04 — re-run at both pins, in-memory (no temp files)

Ran `test-orchestrator-playbook.py`'s case functions directly against `git show <rev>:.claude/skills/harness/SKILL.md`
text for both revisions (dynamic import, no subprocess, no disk writes).

| case | asserts | `a2a373b` | `569d417` |
|---|---|---|---|
| case1 (SC-01) | absence "Receive the team digest" | PASS | **FAIL** (found) |
| case2 (SC-01) | absence "Loop until DONE" | PASS | **FAIL** (found) |
| case3 (SC-01) | presence "NEVER WAIT FOR A LEAD" | PASS | **FAIL** (not found) |
| case4 (SC-02) | presence "context-watch.py" | PASS | **FAIL** (not found) |
| case5 (SC-02) | presence "orchestrator_context_warn_tokens" | PASS | **FAIL** (not found) |
| case6 (SC-02) | token present AND never paired with refuse/refused/blocked/prevented on the same line | PASS | **FAIL** (token absent, so the presence half fails — this is the designed discriminator per the script's own docstring, not a vacuous pass) |
| case7 (SC-04) | absence "Record your phase in" | PASS | **FAIL** (found) |
| case8 (SC-04) | presence "Record your status in" | PASS | **FAIL** (not found) |

All 9 assertions pass at `a2a373b`, all 9 fail at `569d417` — genuine discrimination, re-demonstrated
live, not trusted from an earlier cycle.

Independent text confirmation (not just the script):
- SC-01: `a2a373b` line 45 carries `**NEVER WAIT FOR A LEAD. END YOUR TURN.**`; grep for the two
  retired literals returns nothing anywhere in the 527-line file.
- SC-02: `orchestrator_context_warn_tokens` occurs exactly once, `a2a373b:100`; the refusal words
  "refuses"/"blocked" occur two physical lines later at `a2a373b:102`, never sharing a line with the
  token — confirmed by direct grep line numbers, matching case6's per-line design.
- SC-04: `a2a373b:454-456` — "There is no `phase:` key... a `phase:` write is REFUSED." At `569d417:344`
  the instruction SC-04 names is present verbatim: "Record your phase in `feature.json` `phase:`".

**SC-01, SC-02, SC-04: PASS**, method `automated` (script re-run at both pins), evidence `unit`.

## SC-06 — full re-grade at `a2a373b`

Both of `a2a373b`'s edits vs its parent `e0ae671` land inside step 5 (`SKILL.md:99-148` region);
confirmed by `git diff e0ae671 a2a373b -- .../SKILL.md`. Full 527-line file read end to end for the
outside-the-loop sweep, not just the diff hunks.

**Steps 3–7 agree on what happens while a dispatch is in flight — PASS:**
- Step 3, `SKILL.md:45-46`: "**NEVER WAIT FOR A LEAD. END YOUR TURN.**" — never poll, never sleep,
  never invent activity. `:50-56` — the single-flight refusal on return is expected, explicitly NOT
  permission to resume waiting.
- Step 4, `SKILL.md:91-92,95`: "You resume because a dispatch completed, not because you chose to
  look" — "A completion you were told about is a CLAIM until an artifact on disk confirms it."
- Step 5, `SKILL.md:99-148`: runs post-wake, before the next dispatch decision (step 2); its own
  two-Bash-call self-id mechanism is two calls in the *same* turn, not a wait for anything external —
  no tension with steps 3/4/7.
- Step 6, `SKILL.md:149-154`: record-only, silent on waiting — consistent by omission.
- Step 7, `SKILL.md:156-157`: "Each wake advances the plan by exactly one step: assess, record,
  dispatch the next thing, end your turn again. **There is no waiting anywhere in this loop.**" —
  direct restatement of step 3's rule.

**Outside-the-loop sweep, whole file:**
- `SKILL.md:469` ("never mid-dispatch and never with a child in flight") reinforces, does not
  contradict.
- `SKILL.md:166` — the orphaned "stop the loop — it is reported, not enforced (DEC-134)." fragment
  is present, unchanged by this pin's diff (outside the two edited regions) — this is the already-
  ticketed A-2, not re-raised here.
- No `sleep`/`poll`/`stay alive` instruction anywhere outside the explicit prohibition at line 45-46.

**New step-5 calibration text — the substantive finding:**

Quote, `SKILL.md:99-107`:
> "...you decide whether to finish this phase or hand it to a fresh orchestrator. **The threshold
> ADVISES and never refuses** — nothing is blocked by it and the decision is yours (DEC-198).
> **Crossing it is normal and expected**... **Approaching roughly TWICE the threshold is where
> handing off stops being optional** — and a seam you reach at 2x with the note written beats a
> phase you fail to finish at 3x."

(a) Agrees with the rest of the loop on mechanism: "hand off when a seam is near" (`:103-104`)
matches the established handoff path at `SKILL.md:467-471` ("A handoff triggered by CONTEXT uses
that same note... at the next STEP boundary... never with a child in flight"). No mechanical
contradiction.

(b) Stays advisory in *mechanism* — nothing in `context-watch.py` or any validator enforces the 2x
point, and SC-02's own literal-word check still passes cleanly (no refuse/blocked/prevented on that
line, confirmed). But the **language** does not stay advisory: "stops being optional" three sentences
after "the decision is yours (DEC-198)" **in the same paragraph** directly narrows that claim, and
DEC-198's own text (`DECISIONS.md:6611+`) is unconditional — "Crossing it ADVISES and never refuses.
It is informational, not a gate. No branch stops, no dispatch is denied, nothing is blocked on it" —
with no 2x carve-out anywhere in the decision record. REQ-04 itself says "decide, **advisorily**,"
and the BRIEF's own constraint (`BRIEF.md:57`) bounds this: "Turning it into a gate is out of bounds."
This text does not create a *mechanical* gate, but it reads as a **rhetorical mandate** past 2x that
the decision it cites does not license — an internal contradiction inside step 5 itself, not just a
style nit. **MED severity**: nothing breaks functionally (an orchestrator can still choose either
way), but a future reader — orchestrator or editor — has grounds to treat 2x as a hard rule DEC-198
never authorized.

**Nonce example rewrite** (`SKILL.md:113-124`) — coherent and executable as instructional prose: the
comments are explicit and imperative ("INVENT the 8 characters NOW — do not copy them from here", "the
SAME nonce you just invented, retyped"), consistent with the `SKILL.md:130-134` prohibition on
copying the example verbatim (the c1 incident, `notes/review-harness-code-reviewer-c2.md` context).
Minor/info-only: the `<...>` placeholder syntax uses raw `<`/`>` inside a fenced `sh` block; if copied
un-substituted the shell would throw an ambiguous-redirect syntax error rather than silently running —
a fail-loud outcome, not a new fail-open, so not flagged as more than info.

**SC-06: PASS**, method `inspection`, evidence: steps 3-7 agree (cited above); one MED finding on the
step-5 calibration text's rhetorical overreach past DEC-198, which does not break the loop's mechanism
but should be tightened.

## Unit gate

`run-unit-tests.sh` (no args → `all`, both UNIT_SCRIPTS and INTEGRATION_SCRIPTS, 44 files) at the pin:
**exit 0**, `EXIT_STATUS=0` printed by the runner. `test-orchestrator-playbook.py` ran (confirmed
inside the suite and independently standalone): `ALL PASS`, exit 0, all 9 cases green against the
on-disk file (byte-identical to the pin — worktree `HEAD` = `a2a373b`, `git status` shows `SKILL.md`
clean).

## Not re-filed (per dispatch)

#804, #803, #805, #806, #808, #810 and the six INV-26 board-lag rows are untouched by this pin's diff
and not re-raised. `SKILL.md:166`'s orphaned fragment (A-2) confirmed still present, unchanged.
