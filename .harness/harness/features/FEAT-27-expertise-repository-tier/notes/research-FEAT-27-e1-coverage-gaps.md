# E1 ruling — the two coverage gaps behind the T-02/T-03 qa PASS

**Ruling, up front.** Gap (a) is a **split**: the behaviour is committed at requirement level
(REQ-05) and operationalized by no criterion — closing it adds a *new criterion under an existing
requirement*. Gap (b) is **new outright**: no REQ and no SC names agent-name validation, and T-02's
own intent tells the implementer not to overstate what it buys. **Recommendation: one follow-up task
this cycle covering both, because the operator's signature is required either way and the cheaper
ask is "adopt one small criterion" rather than "decline one under a hard constraint."**

## Gap (a) — the `[ -r ]` guard. Split.

Anchors, quoted:

- REQ-05: "A spawn is never blocked or degraded by the injection hook, **including** when no
  repository tier exists." `including` is non-exhaustive, and *degraded* is a second failure mode
  beside *blocked*. qa's mutant emits two `Permission denied` lines, an `integer expected` error and
  a phantom repository header with no body. That is degradation on the requirement's own words. **The
  behaviour is inside approved scope.**
- SC-06: "With no repository tier present, and with a payload whose `agent_type` is missing or
  unparseable, the hook exits 0, emits no repository header, and emits no error — the spawn path is
  unchanged for every agent that has not distilled yet." **I tested the trailing clause against your
  reading and it is not broader.** It is an em-dash gloss on the two enumerated conditions, not an
  independent expansion, and its own subject is "every agent that has **not distilled yet**" — an
  agent with an unreadable-but-present repository file *has* distilled, so the clause excludes it
  twice over. SC-06 does not reach the fourth condition. **The split stands.**
- T-02 intent 1b settles the task level, and it is the strongest evidence for "new": "Use a plain
  shell glob with **nullglob semantics or** an `[ -r "$f" ]` guard inside the loop, so a
  non-matching glob never emits a literal star as a filename." The specified duty is the
  *non-matching-glob* case only, and the plan offers `nullglob` as an equally conforming alternative
  — `nullglob` gives **zero** unreadable-file protection. A conforming implementation could
  therefore lack the property entirely. Unreadable-file robustness is a byproduct of the
  implementer's choice, not a plan commitment.

Why nothing reddens today, verified at source rather than re-run: `inject-expertise.sh:75-77` is the
segment filter `case "$segment" in ''|*[!a-z0-9-]*) continue ;;`, and an unexpanded glob word carries
a literal `*`, so it fails that filter independently. The `[ -r ]` guard's *specified* duty is
double-covered; its *unspecified* duty is uncovered. That asymmetry is the whole gap.

**So: not a delivery gap — no approved SC is unmet, and REQ-05 will trace to shipped, correct code
at goal-check. It is a regression-pinning gap, and adopting the criterion that closes it is the
operator's.**

## Gap (b) — the `^harness-[a-z0-9-]+$` suffix rule. New. Your reading confirmed.

T-02 intent 1c, verbatim: "Note precisely what this buys, and **do not overstate it** in any comment:
it is name hygiene for the value interpolated into paths and headers. **It does not filter which
directories under `.harness/` are injected**." Intent 1d repeats the frame: "for the same
interpolation-hygiene reason **and no other**." No REQ and no SC mentions agent-name validation at
all; REQ-01 is about receiving the tier, REQ-05 about not blocking. The plan itself authored case 12
with those four values, so the vacuity is a plan artifact, not a build shortfall. **New criterion.**

One correction to qa's framing, which makes (b) cheaper than reported: its unique catch is thinner
than "bad suffix" in general — the pre-T-02 `harness-*` prefix check, the quoted `"$agent.md"`
expansion and the 1d segment filter absorb nearly everything. What survives is **path traversal with
a valid prefix**, and case 12 already carries the value: `harness-qa/../../etc` interpolates to
`$root/.harness/expertise/harness-qa/../../etc.md` = `$root/.harness/etc.md`. Case 12 is vacuous only
because the fixture never writes a file at the traversal target. Writing one makes the existing value
discriminate. That is a fixture addition, not a new case.

## Recommendation — one task this cycle. Both costs.

State it is derived from: T-01, T-04, T-05, T-06 unbuilt; three are `main-session-direct` and pending
with the operator. Shipping is not on the table either way, so "delay" is not a cost here. Both
options need the operator: authoring T-07 amends a signed `plan.yaml`; backlogging is the operator
declining a criterion under a hard constraint. The variable is *when* the signature is asked for.

**This cycle (recommended).** Costs: one more plan task; one build+qa cycle of budget; one more item
in the amendment the operator signs; and a real risk that gap (a)'s criterion cannot be made to
redden reliably (see mechanism below) — mitigate by writing the task's acceptance as *the new cases
redden against a guard-removed mutant, proven*, and permitting the task to drop (a) to a recorded
non-criterion if it cannot. Buys: the guard is pinned before **T-04 puts the first real files into
`.harness/harness/expertise/`** — the tier stops being empty inside this same feature, so the
odd-file path stops being hypothetical during this cycle, not later.

**Backlog.** Costs: the hook fires on every `SubagentStart` including nested spawns, so a future
regression here degrades every spawn at once and silently; and reopening later means reconstructing
this entire chain in a fresh context — this judgment segment already cost one. Buys: a smaller
amendment now, and the option to decline (b), whose unique catch is genuinely thin.

**There is no free option.** The honest asymmetry is that adopting is cheap and reversible while
declining is cheap and *not* revisited — backlog items under a shipped feature rarely come back.

## Sketch — T-07, if adopted. Not written into the plan.

- **Lane, derived not asserted:** T-02 is `change_type: logic`, `execution_mode: team`,
  `execution_agent: harness-dev-ops`; the `lanes:` row for `.claude/skills/harness/bin/**` is
  `team` / `harness-dev-ops`. T-07 touches only `.claude/skills/harness/bin/test-inject-expertise.py`
  — same surface, so **`team` / `harness-dev-ops`**. `inject-expertise.sh` is not one of DEC-174's
  four enforcement scripts, so the carve-out does not fire. `change_type: logic` (`test_matrix` has
  no tests-only type; `logic` → `unit`, matching T-02).
- **Verify:** T-02's shape verbatim — `run-unit-tests.sh --kind unit`, require
  `^PASS test-inject-expertise.py$`, no `^FAIL `.
- **Case 13 — unreadable repository-tier file.** Assert the hook exits 0, emits **no** repository
  header for that segment, and writes nothing to stderr.
  **Mechanism, and it is the load-bearing part:** *not* `chmod 000` — a no-op as root, and git does
  not preserve mode. Use a **dangling symlink** created at test time by `os.symlink` inside the
  per-case tempdir: `.harness/kaya/expertise/harness-qa.md` → a nonexistent target. The glob matches
  it, `test -r` follows the link and fails for every uid including root, and nothing is checked in,
  so mode preservation is irrelevant. Keep a `chmod 000` variant only as a second sub-case guarded
  by `os.geteuid() != 0`. The task must *prove* the mutant reddens, not assume it.
- **Case 12 strengthening.** Write a distinguishable-bodied file at `$root/.harness/etc.md` and
  assert its body never appears for `agent_type: "harness-qa/../../etc"`. Assert only what 1c claims
  — the interpolated value cannot escape its intended path shape. Do not claim directory filtering.
- **Traces:** REQ-05 for case 13. Case 12 traces nothing today — which is exactly the operator's
  decision to make, and if they decline it, drop it and keep case 13.

## Open questions for the operator

- Q1: adopt the unreadable-file criterion under REQ-05 (blocking the amendment, not the ship).
- Q2: adopt the agent-name discriminator, which no REQ currently carries (non-blocking).
