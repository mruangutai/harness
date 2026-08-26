# Handoff — FEAT-34-worktree-act3-enforced, validate → operator — at 513c4a4, seq-4

Supersedes handoff-build.md (seq-3). Validate is COMPLETE as a phase: simplify, panel and
goal-check all ran and all returned. Nothing is dispatchable; four acts are the operator's.

## Next

BRIEFING IS WRITTEN AND RENDERED: notes/ship-review-2026-08-24-validate.md (+ .html).
Four operator acts, and NONE is dispatchable to a squad. (1) Fix INV-29's `--id` derivation in
check-state.sh AND add the group (f.3) message assertion in test-check-state.py — both files
together, both DEC-174 main-session-direct. (2) Adopt SC-17 (paste-ready,
notes/research-goal-check-2026-08-24.md). (3) Amend SC-06 plus a verification gap. (4) Rule on
SC-08's disposition. THEN: re-run the suite, re-pin review_sha at the new commit, re-run the panel
against it. Do NOT reuse this pin after any commit.

## Trust

- All 13 tasks `status: done`; approval `approved`; amendments 1/2/3 signed — plan.yaml:8,
  BRIEF.md:444-459 read by me — verified-at 513c4a4
- HEAD == review_sha == 513c4a4 and NOTHING under .claude/ was modified this phase; the pin the
  panel and goal-check graded is intact — `git status --porcelain -- .claude/` empty — verified-at 513c4a4
- THE DEFECT IS REAL, all four links read by me at the pin, not inherited: worktree_terminal.py:248-251
  sets resolved_id to the LANDED name, :271-275 emits it as feature_id with path still SHORT;
  check-state.sh:1326-1329 composes --id from feature_id; feature-worktree.py:56-59 joins it and
  :207-214 exits 3; post-merge-sweep.sh:150 uses basename(path) — verified-at 513c4a4
- T-10's verify cannot go red: the loop discards via `|| true` and the tail greps 3 skill files, not
  16 agents, then pipes to `wc -l` — plan.yaml:750 read by me — verified-at 513c4a4
- BRIEF.md:246 and :359 read NOT YET RE-SIGNED against :449 — read by me — verified-at 513c4a4
- SC-08 is `verify: automated`, NOT uat; `grep -i uat` over BRIEF.md+plan.yaml = 2 hits, both
  Verification-gaps entries, neither an SC — verified-at 513c4a4
- cycles_used 6/10, runs 16/20. No cycle charged this phase: no squad produced the defect, so there
  is no lead to route to and no rework to charge (DEC-157) — verified-at 513c4a4
- SC-06 unsatisfiable by git's hook semantics — pm's own throwaway-repo probe,
  runs/2026-08-24-05-product/digest.md — verified-at 513c4a4 by pm, NOT re-run by me

## Dead ends

- Do NOT dispatch the M1 fix to any squad — check-state.sh and test-check-state.py are DEC-174
  enforcement layer and main-session-direct; the guard denies a squad edit — verified-at 513c4a4
- Do NOT fix SC-06 in code — no implementation can satisfy it; a squash-landed feature is invisible
  at hook-fire time and the completing commit never re-fires. Criterion change only — verified-at 513c4a4
- Do NOT re-grade SC-01 or SC-05 as not_met to "capture" the defect — they are met AS WRITTEN, and
  rewording a criterion until it fails leaves the blind spot standing. SC-17 is the answer — verified-at 513c4a4
- Do NOT re-run the two mutation red proofs (INV-29 classify_all, INV-30 status-only) — both already
  run and reverted byte-identically — verified-at 513c4a4
- Do NOT cite 15.6s as the integration suite's cost — falsified; 235-236s sole-runner twice, cause
  unattributed — verified-at 513c4a4
- Do NOT run two suites at once — concurrent run-unit-tests.sh produces transient failures that are
  indistinguishable from real ones — verified-at 513c4a4
- Do NOT trust a carried residual's stated premise — Q6 arrived INVERTED; two more claims failed
  re-derivation this phase — verified-at 513c4a4
- At distillation DROP harness-backend-dev observations line 5 (D-10 falsified it) — UNVERIFIED

## Working set

- .harness/harness/features/FEAT-34-worktree-act3-enforced/notes/ship-review-2026-08-24-validate.md
- .harness/harness/features/FEAT-34-worktree-act3-enforced/runs/2026-08-24-04-validator/digest.md
- .harness/harness/features/FEAT-34-worktree-act3-enforced/runs/2026-08-24-05-product/digest.md
- .harness/harness/features/FEAT-34-worktree-act3-enforced/notes/research-goal-check-2026-08-24.md
- .claude/skills/harness/bin/check-state.sh
