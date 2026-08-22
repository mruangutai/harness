# STATE

## Current

- feature: FEAT-31-orchestrator-context-watch
- run: .harness/harness/features/FEAT-31-orchestrator-context-watch/runs/plan5-product
- squad: product
- status: Building — plan amended to 18 tasks, AWAITING THE OPERATOR'S RE-SIGNATURE
- phase: build (recorded HERE; DEC-192 deleted `phase` from feature.json. Q5 filed as issue #635.)

**THE AMENDMENT LANDED AND IS INDEPENDENTLY VERIFIED. `plan.yaml` is 18 tasks / 26 decisions,
`safe_load` clean, `approval:` BYTE-IDENTICAL (`sed -n '4,7p' | shasum -a 256` = `6128e42047a1ec37…`),
`check-plan-routes.py` 0 violations across 18 tasks.** The run is recorded `ESCALATE` — its lead's
returned verdict — and the escalation is procedural, not a rejection of the work.

**What happened, recorded as it happened.** harness-product-lead was force-closed with its pm still
in flight. The pm SURVIVED its lead, kept working unsupervised, and completed all four jobs by 17:57.
Nothing was re-dispatched: exactly one pm ever wrote `plan.yaml` (#628 respected). The orchestrator
confirmed the pm was alive from its sidecar transcript rather than guessing, and verified the result
mechanically — parse, task count, approval hash, route check — before accepting it.

**THE BUILD BLOCKER IS CLEARED.** PR #658 is MERGED (`d065b3b`, `mergedAt 2026-08-22T00:30:27Z`).
Measured at `2cf792f` in THIS worktree: `run-unit-tests.sh --kind unit` exits **0** with
`PASS test-harness-yaml-corpus.py` and zero MISCONFIGURED lines; `--kind integration` exits **0**.
Worktree 0 behind origin/main, 19 ahead. A red suite is evidence again.

| task | verdict | evidence at 2cf792f |
|---|---|---|
| T-01 | PASS | both verify lines exit 0 |
| T-02 | PASS | was FAIL on the red corpus test; re-verified green post-merge (15/15, suite exit 0) |
| T-03 T-11 | PASS (done) | T-11 re-run: integration array 14, absent from detect 0; unit 19, wrongly 0 |
| T-06 T-07 T-08 T-13 | not dispatched | UNBLOCKED now |
| T-04 T-10 T-12 T-14 | pending | operator's own, main-session-direct |
| T-15 T-16 T-17 T-18 | pending (new) | T-15 SC-07 msd; T-16 SC-13 library team; T-17 SC-13 cutover msd; T-18 test_kinds team |

### SEQUENCING RULING — T-18 → T-17 → T-12. This is an orchestrator's call, not an open question.

Derived independently by the orchestrator and by pm. **T-17 appends `test-context-watch-hook.py` to
`INTEGRATION_SCRIPTS` in `run-unit-tests.sh` — the same file T-12 edits.** Until T-18 adds the
matching path to `test_kinds.integration.detect`, `absent from detect` is 1, which **reds T-11's
already-recorded PASS** and makes T-12's `--check-kinds` report KIND-DRIFT (exit 2), failing
`tests.yml`'s two required steps for EVERY kind. Reordering is an execution-time adjustment and is
the orchestrator's authority; the missing `depends_on` edge on T-12 is a plan-level nicety that
rides the re-signature and is NOT a precondition for starting.

**T-04, T-10 and T-14 have NO interaction with the new tasks.** `check-state.sh` belongs to SC-14
only (BRIEF:233-234) and D-18 already ruled the `harness.json` TEMPLATE untouched by test-kind
registration. T-12 is the single point of contact.

### The two context-watch.py defects STILL STAND at 2cf792f

1. **Zero orchestrators found.** No-argument run prints "no orchestrators found". Discovery walks
   `<root>/<session>/subagents` (`:201-211`); dirs at that depth **0**, at the real
   `<root>/<project>/<session>/subagents` depth **37**, holding **2004** sidecars, **104**
   `harness-orchestrator`. `transcript_dir_for_cwd()` is defined at `:46` and referenced NOWHERE
   else. The clause is now corrected (`plan.yaml:227-250`), so the fix has a plan that agrees with itself.
2. **`current` reads 0 for a loaded agent.** `current = sizes[-1] if sizes else 0` (`:181`).

### Premises the next cycle must not re-derive

- **The base sha question is SETTLED and the miss was the orchestrator's.** `2cf792f` is
  `Merge branch 'main' into feat/…`, authored and committed by **Mike Ruangutai at 17:31:08** — the
  operator's own hand, which is why no guard refused it; a governed agent cannot move HEAD. The
  orchestrator read HEAD as `294a1a7` at the start of its run, dispatched at ~17:33 with that pin
  already ~2 minutes stale, and caught it by re-measuring at 17:41. **Pin at dispatch time, not at
  turn start.** No receipt is invalidated: pm re-measured everything at `2cf792f`.
- **SC-13's matcher DELIVERS, measured two independent ways.** Orchestrator: of **36** orchestrator
  transcripts that crossed 200,000, **36** had a `Write`/`Edit`/`Bash` call AFTER the crossing — zero
  would never be warned. pm: `Write|Edit|Bash` covers 3079/3280 = 93.9% of tool_use events; `Edit`
  appears zero times; the dispatch tool is `Agent`, not `Task`. Residual is LATENCY (the warning
  arrives on the next such call), not a hole. Closes the probe's one open question.
- **SC-07 needs NO `check-domain.sh` edit — this falsifies BRIEF.md:231-237.** `check-domain.sh:815`
  already calls `feature_schema.problems_for_text`, so the rule table is `feature-schema.json` +
  `feature_schema.py` and the library write IS the cutover. `runs.items` is
  `additionalProperties: false`, `required: [id, squad, verdict]`; 390 runs entries across 31 files
  carry exactly those keys, so a schema `required` denies all 31. Only a positional rule satisfies
  both halves of SC-07 (D-23).
- **T-14's verify baseline was FALSE.** `check-state.sh | grep -c 'handoff-'` is **3**, not the
  commented 0, and `|| true` made the line incapable of failing either way. Now asserted on the
  ` VIOLATION ` prefix. `test-check-state.py` prints NO summary line at all — 90 `^ok` lines.
- **The ship-door freshness gate CANNOT SEE this worktree.** `feature-worktree.py behind --repo
  harness --id FEAT-31` exits **3**, `no worktree at .../.claude/worktrees/harness/FEAT-31`, because
  `dest_for()` (`feature-worktree.py:56-59`) inserts a `<repo>` segment this worktree's path lacks.
  The same `dest_for` serves `remove`.
- `check-state.sh`: **0** FEAT-31 problems; its single VIOLATION is FEAT-26's unapproved BRIEF.
- MISCONFIGURED cannot coexist with exit 0 (`run-unit-tests.sh:52-53` prints then `exit 2`).
- `iterations` mixes 395 foreign-context `advisor_message` entries but changes peak and current in
  **0 of 74** transcripts — backlog, not gate.

## Open Questions

<The channel from subagents to the user. A non-empty entry is an ACTIVE ROUTING
SIGNAL, not a note: the orchestrator asks the user, writes the answers to
.harness/harness/features/<FEAT>/notes/answers-<runid>.md, and re-delegates with that path. Clear
each entry when it is answered.>

- **Q-SIGN, BLOCKING, THE ONLY THING GATING THE RESTART.** The signed plan grew 14 → 18 tasks, three
  of the four new ones `main-session-direct`, and two things a machine reads changed: D-21 gained 299
  characters no loader could previously see, and the discovery clause now specifies the OPPOSITE
  depth to the one the signature covered. Does the operator re-sign? `approval:` was NOT touched and
  is byte-identical. Not the orchestrator's decision to make.
- **Q-D21, non-blocking.** `D-21`'s `choice` was silently truncated 299 chars because ` ##` opens a
  YAML comment in a plain scalar — invisible to `safe_load` and so to every gate, pre-existing at the
  signature. pm repaired it by quoting. Worth a corpus check for the same shape in other plans.
- **Q-DEC90, non-blocking.** `DEC-90` is STRUCK (`DECISIONS-INDEX.md:109`, 2026-08-21) but
  `BRIEF.md:247` cites it as a live `BLOCKS` constraint. BRIEF.md is approved; only the operator edits it.
- **Q-BRIEF231, non-blocking.** `BRIEF.md:231-237` says SC-07 changes `check-domain.sh`'s write
  route. Measured false — see above. The BRIEF asserts something the tree contradicts.
- **Q-ANCHOR, non-blocking.** 8 lines of DECISIONS.md anchor rot: T-10/T-12/T-14 and D-19/D-20/D-22
  cite `4851-4854`/`4856-4859`, correct at `7299669`, now `4859-4862`/`4864-4867`. `lanes.resolved_at`
  is still `7299669` (`plan.yaml:10`) while the new tasks resolve at `2cf792f`.
- **Q-GUARD, non-blocking, HARNESS DEFECT.** `bash-write-guard.sh` blocked two READ-ONLY `python3`
  heredocs because `>len(val)` and `>=` inside Python source parsed as shell redirects. No file was
  being written. Reachable by any agent writing a comparison in an inline script.
- **Q-HOOKCTX, non-blocking until T-17.** Unverified: that hook stderr reaches the model as CONTEXT
  rather than only as a tool-result error string. If false, SC-13 is not met by this design.
- **Q-COLLECT, non-blocking, RECURRED AND WORSENED.** A lead was force-closed with its member in
  flight; the member outlived it and wrote a signed artifact with no lead to assess it. An
  orchestrator cannot collect a member it did not spawn. Mitigation used: confirm liveness from the
  sidecar transcript, never re-dispatch, verify the artifact mechanically.
