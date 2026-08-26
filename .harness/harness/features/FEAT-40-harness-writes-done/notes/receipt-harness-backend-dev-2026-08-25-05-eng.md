# Receipt — harness-backend-dev — 2026-08-25-05-eng — FEAT-40 Q-second verification

BLUF: all three claimed sites are real at HEAD `86ea3ad`, but all three are comment/docstring
prose, never an executable condition or an error string a test asserts on. No test in
`test-check-state.py` or `test-gh-sync.py` matches the literal strings `DEC-192`, `Item-closed`,
or `deliberately left OPEN` — the matching assertions in those files test *behavior* (accept sets,
status-string case sensitivity), which none of the three fixes touch. `check-state.sh` is
DEC-174-carved main-session-direct in this feature, so T-08 is the *only* task in `plan.yaml`
allowed to write it at all — folding sites 2 and 3 into T-08 is not optional, it's the only legal
vehicle. Site 1 belongs to T-04 (cmd_status/cmd_ship live together in gh-sync.py, and D-01 is the
premise this line contradicts). DEC-192 itself is NOT YET struck at HEAD — T-03 is still `status:
pending` — so today these lines cite a live decision correctly; the finding is prospective
("after T-03 lands"), confirmed correctly framed that way by the dispatcher.

## Site 1 — gh-sync.py:898

Real, verbatim, inside `cmd_status`'s docstring (not `cmd_ship`):
> `      Done is GitHub's native Item-closed workflow; Abandoned has no column, D-03/DEC-192).`

(b) Comment only — inside a docstring, not an executable string, not asserted by any test. But it
is not merely a stale citation: D-01 in this plan's own `decisions:` block says the opposite of
what this line claims — "ship writes the done station... GitHub's Auto-close issue workflow
closes the issue *behind it*", i.e. post-T-04 the harness writes Done, GitHub's workflow is the
consequence, not the writer. This line still describes the pre-T-04 world.

(c) T-04 (`.claude/skills/harness/bin/gh-sync.py` is in T-04's `files:`; T-04's own `intent:`
rewrites `cmd_ship`, and D-01/D-07 are exactly the decisions that supersede this line). T-04's
`verify:` greps for specific PASS lines and specific literals (`gh-sync: FAILED`, `def
audit_findings`) — none reference DEC-192/DEC-203 text, so folding a comment fix in does not
touch the verify surface. T-05 also touches gh-sync.py but its scope is `parent_origin`/abandon,
not station-write semantics — worse fit.

(d) ~2-3 lines (reword the Done clause to reflect D-01/D-07, swap DEC-192 → DEC-203 once T-03 lands).

## Site 2 — check-state.sh:1416-1419 ("THE TERMINAL EXEMPTION")

Real, verbatim:
> `            # THE TERMINAL EXEMPTION. The ship closes the parent, GitHub's Item-closed`
> `            # workflow lands it in Done, and the derivation would still say Review — so`
> `            # without this every shipped feature is a permanent false violation. Case`
> `            # sensitive on purpose: \`done\` is not \`Done\` (DEC-192).`

(b) Comment only, inside INV-26. "The ship closes the parent" is also now the pre-T-04 premise
(D-01 reverses this: ship *writes Done*, it does not close). No test asserts this text (checked
`test-check-state.py` — matches at 1610/1662/2729 are comments/docstrings testing behavior, not
this string).

(c) T-08 is the *only* task with `check-state.sh` in `files:` in this feature (DEC-174 carve-out —
main-session-direct only). T-08's `verify:` checks `INV-31` presence/absence and a clean full run
(`all state invariants hold.|VIOLATION|note`, no `Traceback`, no `INV-31` string on second call) —
none of that greps INV-26's prose, so folding this in is safe against T-08's own verify. But T-08's
stated `intent:` is narrowly "add INV-31"; touching INV-26 prose is adjacent scope in the same
file, not what T-08 was written to cover — worth a one-line note in T-08's dispatch rather than
silent scope creep, since check-state.sh's DEC-174 carve-out means no other task can absorb it.

(d) ~2 lines (swap "ship closes the parent... GitHub's Item-closed workflow lands it in Done" for
"ship writes Done directly"; DEC-192 → DEC-203).

## Site 3 — check-state.sh:1479-1486 (D-24 comment)

Real, verbatim (renumbered from claimed 1479 — content is unchanged, header comment starts at 1479):
> `                # D-24, on the operator's ruling 4 of 2026-08-23 (FEAT-33 T-22). Under D-23`
> `                # a done task's sub-issue is deliberately left OPEN so it can hold its`
> `                # column through the whole Review phase: GitHub's native \`Item closed\``
> `                # workflow lands a closed issue's card in the done column by itself, which`
> `                # is the measured reason board 3 has never held a card at Review. So a done`

(b) Comment only — the executable code below it (`_accept = {_want}`, widened by `|=
{review, building}` only when `status(task)==done and feature.status==Review`) is a permissive
accept-set, not a condition that *depends on* the "deliberately left OPEN" premise being true, so
behavior is unaffected either way. But the premise itself is now directly falsified, not just by a
struck decision id: gh issue view confirms #818 and #830 are `CLOSED` at HEAD (checked live via
`gh issue view 818/830 --repo mruangutai/harness --json number,state`), consistent with the plan's
own claim (T-03 intent) that all 13 of FEAT-34's sub-issues (#818-#830) were closed AND sitting at
Review at `cc84b29` — the opposite of "GitHub's native workflow lands a closed issue's card in the
done column by itself." I did not independently re-derive the board *station* for those issues
(would need `board_lifecycle.py`/project API reads beyond this run's scope); the CLOSED state is
independently confirmed, the station claim rests on the plan's own recorded measurement.

(c) T-08 only, same DEC-174 reasoning as site 2. Same verify-safety analysis applies — T-08's
verify doesn't grep this text.

(d) ~5-8 lines — this one needs an actual rewrite, not a word swap: the reasoning it states
(closed→auto-moves-to-done, hence must keep OPEN) is the thing DEC-138 amendment 8 (T-03) strikes,
so the comment must state the *new* reasoning (accept set is permissive because ship now writes
Done directly and a closed card can legitimately still sit at Review) rather than just relabel the
decision id.

## Open question for the plan owner

None of the three needs a *new* task — T-04 and T-08 are the correct, already-scoped homes, and
T-08 is the *only* legal one for the check-state.sh sites under the DEC-174 carve-out already in
this plan. Whether to land these three comment fixes as explicit dispatch line-items inside T-04
and T-08 (so they're not silently dropped when those tasks execute) is a plan-owner call, not mine.
