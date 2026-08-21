# STATE

## Current

- feature: FEAT-31-orchestrator-context-watch
- run: .harness/harness/features/FEAT-31-orchestrator-context-watch/runs/build-eng
- squad: eng
- status: Building — build-eng returned ESCALATE, blocked on a red unit suite
- phase: build (recorded HERE. **DEC-192 DELETED the `phase` field** from feature.json, so the
  playbook's "record your phase in feature.json" contradicts a signed decision. Closes Q2 — a stale
  playbook line, not a gap.)

**FOUR OF EIGHT TEAM-LANE TASKS ARE BUILT AND VERIFIED. The build is stopped by a defect that
PREDATES the signature: the unit suite was ALREADY RED at e5f88c4.**

`cycles_used` stays **3** — the lead reported ZERO send-backs and T-02's FAIL was first-pass, not
routed back (DEC-157). Runs 6, budget 20.

| task | verdict | evidence |
|---|---|---|
| T-01 | PASS | `context-watch.py` created; both verify lines exit 0 |
| T-03 | PASS | `budgets.orchestrator_context_warn_tokens: 200000` |
| T-11 | PASS | `integration.detect` 8 entries absent -> 0; before exit 1, after exit 0 |
| T-02 | FAIL | 15 cases + two applied-mutant red proofs pass; verify line 2 red from the corpus |
| T-06 T-07 T-08 T-13 | not dispatched | their verify invokes the red unit runner |

### THE BLOCKER — the suite was red before any work began

`run-unit-tests.sh --kind unit` exits 1 because `test-harness-yaml-corpus.py` walks the repo for
`*.yaml` and hits **this feature's own** planning artifact,
`notes/recovered-draft-14task-does-not-parse.yaml:85:37 — mapping values are not allowed in this
context`. Established, not inferred: that file is **unchanged since e5f88c4** and the corpus test was
already in `UNIT_SCRIPTS` there. Committed deliberately at **ae89da4**, whose message says it does
not parse.

**Headline: T-02, T-06, T-07 and T-13's `verify:` blocks were UNSATISFIABLE AT SIGNATURE.** All four
invoke the unit runner. No fix cycle can clear it from inside the eight tasks' `files:` lists.

Two fixes, not equivalent. **Renaming the draft** closes the INSTANCE and is in the orchestrator's
domain. **Excluding `features/*/notes/` from the scanner** closes the CLASS — every future feature
saving a draft YAML hits this — but that file is plausibly enforcement layer under DEC-174, so it is
the operator's. I deliberately did NOT apply the instance fix: the ruling is needed either way and a
rename would make the class look closed. Recommendation: exclude feature `notes/`, then rename as
tidying.

### TWO MUST-FIX DEFECTS IN context-watch.py, found independently by the orchestrator

Neither is a plan-compliance failure — T-01 is faithful to its intent. Both in
`notes/finding-discovery-depth-orchestrator.md`.

1. **The tool finds ZERO orchestrators by default.** `discover_orchestrator_rows` scans
   `<root>/<session>/subagents`; the real layout is `<root>/<project>/<session>/subagents`. **0**
   matches at the coded depth against **1999** real, **103** of them `harness-orchestrator`.
   `plan.yaml:198-199` specifies the shallow depth while `:195-196` implies the deep one — the plan
   contradicts itself. Blocks **SC-01** and **SC-10**'s no-argument UAT. `transcript_dir_for_cwd()`
   already computes the missing level; `main()` never calls it.
2. **`current` reports 0 for a loaded orchestrator.** `current = sizes[-1]` and `sizes` appends 0 for
   any line lacking `message.usage`. Agent `a7783f0ec41e6a8c6` reports `current=0` while holding
   **696,472** — its last line is a `user` message. 3 of 25 sampled rows. Defeats **REQ-01** and
   SC-10's question 2.
3. **`entries` is ambiguous and will fail T-13**, which demands all three agree — the tool counts ALL
   parsed lines (1046), a usage-based count gives 669.

**The arithmetic is CORRECT and independently confirmed.** Tool and an inline recomputation importing
nothing from it agree to the token on a live orchestrator: `current=peak=186,041`. Top-level equals
the sum over non-advisor iterations in 409 of 418 multi-iteration entries.

### Premises the next cycle must not re-derive

- **DEC-197 @6362** exists and closes Q-B; T-11 cited it at a re-checked anchor.
- `upgrade-config.py` **DOES** propagate a new budgets key — probe printed
  `+ budgets.orchestrator_context_warn_tokens`. **T-05 settled in advance.**
- INV-17 checks heading PRESENCE only (`check-state.sh:509`, membership `:614`) inside the
  `SEAM_NOTES` loop (`:592`) — T-10 and T-14's premises hold.
- The BRIEF's headline transcript (1,497,025 -> 750,837) has **aged out** of the 30-day window;
  `746878` matches nothing across all 76 files. Fixture tests unaffected.
- Backlog not gate: `iterations` mixes 395 foreign-context `advisor_message` entries, picked by the
  plan's rule in 325/395 — but that changes peak and current in **0 of 74** transcripts.
- Lead's catch: `run-unit-tests.sh:3` is `cd "${CLAUDE_PROJECT_DIR:-$(pwd)}"`, so a runner pointed at
  the main checkout tests a tree where new files do not exist — exit 0, proving nothing.
- Mirror clean: milestone **#20**, sub-issues **#642–#655** on adopted parent **#598**, 8 cards
  `Building`, plan.yaml written FIRST; diff exactly **8/8** lines and `approval:` sha256
  `e4cc9491d96635a6…` byte-identical to `git show e5f88c4:`.

## Open Questions

<The channel from subagents to the user. A non-empty entry is an ACTIVE ROUTING
SIGNAL, not a note: the orchestrator asks the user, writes the answers to
.harness/harness/features/<FEAT>/notes/answers-<runid>.md, and re-delegates with that path. Clear
each entry when it is answered.>

- **Q-BLOCK, BLOCKING.** The unit suite is red on this feature's own unparseable plan draft, and was
  red at signature. Exclude `features/*/notes/` from `test-harness-yaml-corpus.py` (closes the class,
  likely main-session-direct), or rename the draft (closes the instance, orchestrator's domain)?
  Four tasks cannot verify until this is settled.
- **Q-SC, BLOCKING before the ship decision.** **SC-07 and SC-13 have no implementing task** — no
  file, no mention of their substance in any of the 14 tasks. `D-02` calls the plan "HALF-WRITTEN BY
  DESIGN" and names them for a second planning run that never covered them. Ship the measurement half
  and defer, send pm back to append tasks, or amend the BRIEF?
  See `notes/finding-sc-coverage-orchestrator.md`.
- **Q-MSD, BLOCKING.** Four `main-session-direct` tasks are the operator's own hands under DEC-174:
  **T-14** then **T-10** (`depends_on: [T-14]`), **T-04** (unblocks T-05 and T-09), **T-12**
  (`depends_on: [T-11]`, done).
- Q-DEFECT, non-blocking routing question. The two `context-watch.py` defects are faithful to a
  self-contradicting plan clause. Fix as a T-01 fix cycle under the SCs' authority, or have pm
  correct `plan.yaml:198-199` first?
- Q1, non-blocking, unchanged. An orchestrator cannot collect a lead that outlives its turn — no
  message tool, no terminating wait, foreground `sleep` blocked. Mitigation is ORDERING: dispatch
  early, spend the wait on read-only verification. It paid for the mirror and both defect findings.
- Q-A, non-blocking, DEFAULT ADOPTED in D-22, overrulable in one read. Is `test_kinds` enforcement
  layer under DEC-174? Adopted: data entries `team`/dev-ops (T-11), the check and its test
  `main-session-direct` (T-12).
- Q-LEAD-2, non-blocking, from the lead. T-02's signed `verify:` carries bare-comment expectations
  the lead had to supply as asserted commands. Should pm amend the plan so they live in the signed
  block?
