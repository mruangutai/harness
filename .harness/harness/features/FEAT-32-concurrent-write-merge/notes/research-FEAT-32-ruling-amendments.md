# FEAT-32 — the seven rulings, applied to plan.yaml

**All seven landed. The plan grew from 13 tasks / 8 decisions to 15 / 10; `approval.status` is still
`pending`.** Route check exits 0, 0 violations. Two rulings changed the plan's *content* materially
(R3 added a mechanism, R4 added two tasks); the rest were corrections.

## The one ruling whose premise did not hold

**R5(a) — the vacuum is real but arrives by a different road.** The ruling says T-05's flock rewire
makes `test-expertise-merge.py` cases 4/5/6 pass *vacuously*. Measured at `c32f332`: those three
assertions are `check("caseN: lock file is gone", not os.path.exists(path + ".lock"))` at `:203`,
`:221`, `:237`, and D-02's lock is a **sibling** `.lock` file never removed on release — so as
written they go **RED**, not vacuous. The vacuum appears only if one of the two forbidden
workarounds is taken (move the lock somewhere the test does not look). **The ruling's conclusion is
unaffected** and is applied verbatim: the three are replaced with "a following apply still exits 0",
a new `case10` stale-lock-recovery case is added (fork, `SIGKILL`, assert exit 0 **and** the entry on
disk), and T-05's verify carries a red proof that mutates `USE_FLOCK` by name and requires the suite
to fail.

## R3 — a mechanism that holds, plus a recorded impossibility

**The wait is impossible.** `validate-digest.py:845` at `c32f332` is `if d.get("stop_hook_active"):
return 0`; the docstring at `:815-818` gives the reason (blocking a re-run that a stop hook already
blocked is an infinite loop with no operator escape). So a `SubagentStop` refusal fires at most once.

The discriminating question was not *how to wait* but *which harm needs a wait* — and neither does:

| Harm | Mechanism | Bound |
|---|---|---|
| the LOSS (#551 occ. 1) | `PreToolUse` single-flight refusal (D-06) | **unbounded** — a PreToolUse refusal has no once-only limit |
| the FALSE REPORT (occ. 3–6) | `SubagentStop` refusal naming each in-flight child (D-09) | **once** — the same strength every other digest contract in that file has |

**Residual, recorded not papered over:** a second identical return ships, and an orphaned child of an
interrupted parent (DEC-131) has no parent left to refuse. #551 narrows; it does not close.

This needed the dispatcher edge on disk, so **D-06's registry generalised**: persona → *list* of
claims, each carrying its dispatcher; a claim is recorded for **every** `harness-*` dispatch and
refused only for `SINGLE_FLIGHT_AGENTS`. New `live_children(root, dispatcher)` is what D-09 stands on.

## R4 — the signer, resolved on behaviour

**The main session wins; `.claude/skills/harness/SKILL.md:34-35` is the artifact that already says so.**
The evidence is behavioural, not documentary: DEC-120 puts the user channel at the main session
alone, so it is the only tier that can hold a signature the user actually gave. Losers, both
corrected in T-15: `templates/plan.yaml:25-26` ("Written by the ORCHESTRATOR only" — self-refuting,
since it cites DEC-120 in the same sentence) and `agents/harness-pm.md:28` ("that is the
orchestrator's, because only it can reach the user" — flatly false).

Measured at `c32f332`: `grep -n approval check-domain.sh` → **one** line, `:858`, a comment.
`check-domain.sh --resolve` on a plan.yaml → `harness-orchestrator`, `harness-pm`. `team-config.yaml:18`
grants the **heading form only**, so `plan.yaml`'s `approval:` mapping is granted to **nobody**. Three
disagreements plus one gap, enforced by nothing.

T-14 puts the denial on the **domain** path, not SHAPE — the main session is exempt by the mechanism
(`check-domain` exits 0 with no `agent_type`), not by a second carve-out. It compares the **loaded**
`approval` value, so a whitespace reflow is allowed and plan-merge.py's own output is not
undeniable-by-luck.

## DEC-197 exposure sweep

The five files T-10 creates are all registered, so none is exposed. **Two pre-existing files that
this feature's `evidence: integration` claims rest on ARE**: `test-validate-digest.py` (SC-08) and
`test-check-domain.py` (SC-17). Both sit in `INTEGRATION_SCRIPTS` and are absent from
`integration.detect` — verified identical in the worktree and on `main` — so the runner treats them
as integration while the qa matrix reads them as unit. **Fixed inside T-10**, which now appends seven
paths, not five, and cites DEC-197 rather than re-deriving it. Six further files carry the same
defect and are deliberately untouched (see open question Q2).

## Not changed, and why

- **DEC-90 / SPEC §15.1** — already struck and rewritten on `main` (`16b30c6`); T-13's item 5 is
  rewritten into an explicit *do not touch this*. No task edits either.
- **Execution modes** — every one re-checked against DEC-174 am.4 ("the category decides, the list
  records") and the sibling precedent. **None moved.** T-10 stays `team`/`harness-dev-ops` (registration
  DATA, matching the `test_kinds` precedent); T-02/T-03/T-04/T-05/T-06 stay `team` (libraries and
  CLIs — "a module a gate imports is not itself a gate"); T-01/T-07/T-08/T-09 stay
  `main-session-direct`. The two new tasks follow: T-14 `main-session-direct` (check-domain.sh is a
  *named* enforcement script and am.4 pulls its test in with it), T-15 `main-session-direct` (DEC-179
  — all three files resolve NOBODY).
- **R7** — `#627`, `#560`, `#605` were already out in the BRIEF but only `#627` appeared in
  `plan.yaml`. D-08 now names all three, with the trap spelled out: the claim registry *is* the
  mechanism #560 and #605 want, so a build agent will be tempted to add a persona to the literal.

## Open questions

- **Q1 (blocking-ish, not mine to fix):** this worktree is behind `main`. `DECISIONS.md:1153` here is
  DEC-90's original heading with no strike record, the index's last row is DEC-196, and `SPEC.md:2221`
  still reads "there is no lock file anywhere". Every DEC-90/DEC-197/SPEC §15.1 claim above was read
  in `/Users/molchairuangutai/GitHub/harness` (main), never in the worktree. T-13's intent now tells
  its executor to *report* rather than act if the branch it lands on has no strike record.
- **Q2 (non-blocking):** six files remain in `INTEGRATION_SCRIPTS` and absent from
  `integration.detect` — `test-check-expertise.py`, `test-gen-decisions-index.py`,
  `test-bash-write-guard.py`, `test-harness-yaml.py`, `test-upgrade-config.py`,
  `test-merge-settings.py`. No criterion here rests on them, so T-10 leaves them. Every
  `evidence: integration` claim in any *other* feature resting on one of those six is false.
- **Q3 (non-blocking):** SC-14's baseline (179 / 93 lines) was observed at `5d9b428` and is stale —
  FEAT-30 added two files to the runner's arrays after it. The criterion now binds only on exit 0 and
  the absence of `FAIL` lines, and says so. Nobody re-observed the counts; a suite run was out of
  scope for a planning round.
