# Operator answers — FEAT-12 — 2026-08-10

Relayed by the main session. The operator ruled on the blocking question and on the
non-blocking ones in one pass.

## Q1 — kaya: working tree only, or commit and push? **BLOCKING**

**Commit and PUSH to kaya's `master`, path-scoped.** pm's recommendation, taken.

The reasoning is the one pm gave and the main session re-measured: `factory_workspace.py:125`
clones from the REMOTE, so a working-tree-only deletion is restored by the next factory checkout
and the ticket's destination is never reached.

**"Path-scoped" is load-bearing, not a style note.** Measured at 2026-08-10:
**kaya's working tree carries 63 uncommitted files.** They are not this feature's work and must not
be swept into the removal commit. Stage the deletion paths explicitly — never `git commit -a`, never
`git add .`, never `git add -A`. If the 63 include anything under `.claude/skills/harness*` or
`.claude/commands/harness*`, STOP and raise it rather than deciding.

The operator's standing "do not push, do not open a PR" applies to THIS repo and is silent on kaya.
This answer authorizes a push to `mruangutai/kaya-ai` `master` for the deletion commit **only**.

## Correction to the plan — T-08's agent count is wrong

The plan removes `.claude/agents/harness-*.md` from kaya. **kaya tracks ZERO harness agent files** —
`git ls-files '.claude/agents/harness*'` returns nothing. The 16 agent files were the `~/.claude/`
global copies, which the operator deleted on 2026-08-10, ahead of this ticket.

Measured in kaya at 2026-08-10: **55** tracked skill files, **8** tracked command files, **0** agent
files, **117** tracked files under `.harness/` which are KEPT.

Do not let a task whose verify is "count equals zero" pass merely because the target never existed.
Either drop the agent clause or make its absence explicit in the receipt. This is exactly the Q4
shape the orchestrator flagged.

## Q8 — the dev-ops SHARP EDGE comment in both team-config files

**Fold it into T-11.** Remove the clauses that name `deploy` as a thing dev-ops owns and as a
user-gated action. DEC-85's rationale stands independent of the deleted script, so keep whatever
sentence carries that rationale and cut only the references to the script.

## Q7 — `plan.yaml:63`, D-02's `because` truncated by an inline `#206`

**Repair it on the next pm touch.** Do not spend a cycle now. The operator signs the raw text, which
is complete; only machine readers see the truncation. Use the `>-` block D-03 already has.

## Q9 — T-13's builder hazard

**Use `git rm`, not `rm`.** Noted and adopted, which also removes the deleted-but-indexed hazard the
orchestrator described.

## Q4 — the count-equals-zero absence shape

**Not this feature's to fix.** The operator agrees it is a harness-wide latent defect and agrees it
is inert here. Do not widen scope. It needs asserting `git grep`'s own exit code, and it belongs to
the harness owner as separate work.

## One bad reference in the BRIEF input, disclosed

The grilling artifact `.harness/notes/grilling-end-distribution-2026-08-10.md` cites **DEC-161** in
its Facts section. **DEC-161 does not exist** — `DECISIONS.md` states in two places that it had
already been deleted. The main session wrote that error. Nothing downstream depends on it. Do not
cite DEC-161 anywhere in this feature's artifacts.

## Also true since your run started

`#202` landed while you were planning. `check-docs.sh` no longer exists, the `<!-- stale: -->`
mechanism is struck, and DEC-188 records the replacement rule: a decision the tree flatly
contradicts is struck from the record and removed from every gate. Your plan already does this
correctly. There is no propagation checker to run and nothing substitutes for it.
