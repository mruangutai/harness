# STATE

## Current

- feature: FEAT-40-harness-writes-done
- run: PLAN PHASE COMPLETE and CORRECTED. The blocking premise was FALSE — the suite is GREEN, so
  the suite-quarantine task and its decision are deleted and the plan is 10 tasks. Three operator
  rulings applied (the environment marker is dropped, DEC-203's register is settled, and the
  acceptance-test correction was already on disk). Awaiting the operator's signature on BRIEF.md and
  plan.yaml. cycles_used 3/10, 3 runs vs informational bound 20.
- squad: none
- status: Plan

<!-- THE RED BASELINE WAS AN ARTIFACT OF STALE RUNTIME STATE, not of the code. Measured by me at
     a60bc49, one suite at a time with nothing else running and no environment variable set:
     --kind unit 355 PASS / 0 FAIL / exit 0, and --kind integration 0 FAIL / exit 0 / 26 of 26,
     including test-post-merge-sweep.py and test-hooks-install.py. My predecessor's eight-script
     red does not reproduce.

     THE DISCRIMINATOR, proven causally rather than inferred: test-validate-digest.py's [hook]
     cases call the real check-digest hook through subprocess.run with NO env= override, so it
     reads the LIVE .harness/.inflight-claims.json. That file is untracked and gitignored
     (.gitignore:40) — which is exactly why the main checkout and CI were green while this
     worktree was red. A --kind all run that was still in flight when I arrived (25 minutes old)
     had left six harness-backend-dev claims behind. The hook's refusal fires ONCE per claim, so
     re-running the script drained them 6, 4, 2, 1, 0 and the fourth run passed 14/14 with ZERO
     code changes. Nothing was repaired; stale state simply ran out.

     Residue: one stale harness-pm claim remains in that registry. It is harmless to the suite but
     should be cleared with `python3 .agents/skills/harness/bin/inflight_registry.py release-all`
     — outside my domain, so I did not run it. Full detail in notes/handoff-plan.md. -->

## Open Questions

- BLOCKING, OPERATOR — the five non-blocking questions carried since run 1 are still unruled: the
  sweep's `gh-sync: FAILED` literal, the prototype gate, REQ-06 narrowed to what a Bash gate can
  see, DEC-200 citing the struck three, and whether `close-task` survives. The operator asked to
  rule on all five in one pass, so they gate the signature together.
- BLOCKING, MAIN SESSION — BRIEF.md's `## Approval` is still unsigned and check-state.sh reports it
  as a violation. plan.yaml's `approval.status` is `pending`, which is correct and untouched: the
  task set changed this run, so it stays pending until the operator signs. No agent may write it.
- RESOLVED this run — the red-suite premise was false. The quarantine task and its decision are
  gone, the five tasks that depended on them no longer do, and their verifies now assert a plainly
  green suite (`test $rc -eq 0`) instead of FAIL-set equality against a baseline file.
- RESOLVED this run — the environment marker. D-06 now records that refusing every `gh issue close`
  unconditionally reaches issue 842 constraint 5's OUTCOME by a simpler route than the mechanism it
  names, and that no marker exists to forge.
- RESOLVED this run — DEC-203's register. T-03 now carries the operator's ruling: shorter AND
  plainer than the three entries it replaces, measured against their combined word count.
- NOT A DEFECT — the acceptance-test correction needed no edit. BRIEF.md:108-111 and :219-222 and
  plan.yaml's acceptance task already describe #728 as thirteen children, #818-#830, all at
  `Review` and therefore all open, and already frame it as the open-child skip plus children-first
  ordering.
