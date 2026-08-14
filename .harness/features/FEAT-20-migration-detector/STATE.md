# STATE

## Current

- feature: FEAT-20-migration-detector
- run: review panel closed; pm goal-check next
- squad: validator (done) → product (next)
- status: validating

**All four tasks DONE, both validator gates PASSED, nothing gates the ship.** Task commits
`14ca661` T-01, `d3207e7` T-02, `2c35398` T-03, `396f1ad` T-04; every `verify:` re-run in this
session rather than read from a receipt. Issues #361-#364 closed, parent #360 derived to `Review`.

**`review_sha` is `ea476fd`** — the panel ran there. An earlier line in this file pinned `11cb644`
and the panel flagged the disagreement; the pin moved when the qa artifact and the build handoff
were committed, and qa measured the two trees identical across all eight source files, so the
verdict is unaffected. **This is the reconciliation; `ea476fd` is the pin.**

**Blocking qa gate: PASS.** Matrix union `{unit, integration}`, both green, and both registration
greps fired — the part that matters, since a suite exiting 0 without running the new file is this
feature's own subject. T-03's `config` row requires zero kinds, so it is satisfied, not
unsatisfiable. One in-run send-back repaired `notes/qa-c0.md`, which is why `cycles_used` is 3.

**Review panel: PASS, `must_fix` empty, `severity_max: med`, zero send-backs.** `gates.review` is
`advisory_unless_high`, so nothing at `med` gates. Three of the four reviewers produced falsification
evidence rather than assurance: code-reviewer built a live mutant and proved it live before claiming
four cases survive it, security timed the regexes against a 400k-char adversarial string, qa
re-executed both kinds in a throwaway worktree instead of relaying the earlier gate.

**The one residual worth the operator's attention, now named rather than general.** The suite is
correct-today, not pinned-against-regression, and the panel converted that into two specific
surviving mutations. R-1 (med): `check-state.sh:1302-1318` dispatches INV-27's wording across four
`if/elif` branches on `_srep.cause` with **no trailing `else`** — confirmed by me at source — and
only one of the four causes is rendered by any test, so deleting the `no-rows` branch leaves every
suite green while session entry reports a clean tree over a surface nobody verified. That is issue
#148's shape at the call site D-02 called the higher-value one. R-2 (med): `_evidence()`'s count
feeds only the printed `examined` line, never the verdict; the deletion survives four cases but
fails noisily at CI, which is why it ranks below R-1 despite equal severity.

**Budget: `cycles_used` 3 of 10. `len(runs)` 6 of 20** — well inside the informational tripwire, and
a floor, since T-01 and T-02 were main-session-direct and are not runs.

**Next: pm's goal-check against all 15 SCs through product-lead, then close-out (ship-refresh and
distillation in one turn, two dispatches), then the CEO briefing.**

## Open Questions

None blocking. Five ride to the briefing:

- **Q1, security, pre-existing and RCE-shaped.** `check-state.sh`'s heredoc runs `cd "$root"` before
  `python3 -`, so `sys.path[0]` is the scanned root ahead of `PYTHONPATH`; a planted `harness_yaml.py`
  or `layout_migration.py` at `CLAUDE_PROJECT_DIR` executes at every session entry. Byte-identical at
  `88b1182`, so **not** this feature's regression — but it wants its own ticket.
- **Q2, plan-level, pm's to settle.** `plan.yaml:663-665` and DEC-194 both assert every finding names
  the reader path, while T-01 specifies two CANNOT_VERIFY causes — `no-evidence` and `no-rows` — that
  have no reader to name. The **approved plan** is internally inconsistent, so a docs-only correction
  would leave the plan still contradicting the code. Not mine to edit.
- **Q3, the mutation dispatch, now with a first target.** Delete any one of INV-27's three unrendered
  cause branches and confirm the suites stay green. Recommended before units 3-7 lean on the detector.
- **Q4, harness defect.** `bash-write-guard` blocks shell redirects whose target is a shell variable
  and blocks redirects into the scratchpad path, not only repo paths — it cost the code reviewer a
  detour through the Write tool, and it refused the verbatim `verify:` clauses for T-01 and T-02,
  which redirect to `$(mktemp)`. Belongs to the harness owner.
- **Harness defect, carried from the build phase.** The playbook says to record the phase in
  `feature.json` `phase:`, but `feature-schema.json` sets `additionalProperties: false` and defines
  no `phase`. Recorded here instead.
