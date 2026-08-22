# Handoff — FEAT-31, build → validate — written at b2f7c73, seq-2

## Next

**Dispatch T-05 to harness-eng-lead and T-09 to harness-product-lead, as two separate runs in
one message.** Both are blocked ONLY on the operator's T-04 (`plan.yaml`: T-05 `depends_on:
[T-04]`, T-09 `depends_on: [T-03, T-04]`), so confirm T-04 has landed first — the check is
`orchestrator_context_warn_tokens` present in `.claude/skills/harness/templates/harness.json`
`budgets`, which read ABSENT at b2f7c73. If it is still absent, do not dispatch; the feature is
waiting on the operator, not on you. After T-05 and T-09 return, sequence the qa segment
(validator squad, `gates.qa_gate: blocking`), then SIMPLIFY, then pin `review_sha`, then the
review panel, then pm's goal-check on all 14 SCs.

## Trust

- Ten of eighteen tasks are done: T-01, T-02, T-03, T-06, T-07, T-08, T-11, T-13, T-16, T-18 — `plan.yaml` statuses and issues #642/#643/#644/#647/#648/#649/#652/#654/#660/#662 closed — verified-at b2f7c73
- Both standing `context-watch.py` defects are FIXED, not merely claimed: discovery now returns 105 rows, matching an independent glob count of 105 orchestrator sidecars — `runs/fix1-eng/digest.md` plus my own recomputation — verified-at b2f7c73
- SC-01's live half is DISCHARGED: `verify-context-watch-live.py a7783f0ec41e6a8c6` prints tool and independent recomputation both at current 696,472 / peak 696,472 / entries 669, and that peak matches `BRIEF.md:43` to the token — verified-at b2f7c73
- Unit 76 of 76 and integration 10 of 10, both exit 0, zero MISCONFIGURED — `run-unit-tests.sh --kind unit|integration` — verified-at b2f7c73
- The operator's T-17 is UNBLOCKED: T-16 landed the library with `.claude/settings.json` zero-diff (D-24 holds), and T-18 landed the `detect` path — key-by-key diff of `harness.json` showed exactly one key changed — verified-at b2f7c73
- `run-unit-tests.sh` has THREE writers, not the two on the record: T-07 (landed, one entry appended, nothing removed, order preserved) plus the operator's T-17 and T-12 — `git diff` of the arrays — verified-at b2f7c73
- Q-CHECKCOUNT is CLOSED and benign: 78 static `check(` sites versus 76 executed, and the two unexecuted are lines 668-669 inside case J's `INCONCLUSIVE` branch, dead precisely because the mutation applied — `sys.settrace` line trace — verified-at b2f7c73
- cycles_used is 4 of 10; runs 9 of 20 and runs are INFORMATIONAL only (INV-22, `harness.json` `_max_total_runs_rationale`) — `feature.json` — verified-at b2f7c73
- Three of ten requirements are exclusively main-session-direct — REQ-04 (T-15), REQ-09 (T-14), REQ-10 (T-10, T-14) — so the goal-check CANNOT pass until the operator's six tasks land — `plan.yaml` `traces:` — verified-at b2f7c73
- Two board cards read Building while their issues are closed and the plan says done (T-01 #642, T-02 #643); `gh-sync close-task` re-run twice did not move them — `check-state.sh` INV-26 — verified-at b2f7c73
- The `bash-write-guard.sh` heredoc hazard on the record is FALSE: a read-only `python3` heredoc containing `>` and `>=` runs clean; the real defect is `sed -i` with a shell-VARIABLE target refused as out-of-domain — direct test, twice — verified-at b2f7c73
- 14 SCs exist, SC-01..SC-11 and SC-13..SC-15 — there is NO SC-12 — `BRIEF.md` grep — verified-at b2f7c73
- Q-HOOKCTX (hook stderr reaching the model as context) remains the operator's to settle and gates SC-13's design — `STATE.md` — UNVERIFIED
- Whether the one-argument footer's mixed scope (Q-FOOTERSCOPE) fails SC-10 step 2 — `runs/fix1-eng/digest.md` — UNVERIFIED

## Dead ends

- Do NOT re-verify T-01 by its own `verify:` block — line 2 greps `no orchestrator` against a nonexistent dir, which a tool that finds nothing ANYWHERE satisfies identically; it passed while both defects stood, and I recorded `done` off it once already — `notes/finding-discovery-depth-orchestrator.md` — verified-at b2f7c73
- Do NOT trust any `verify:` floor expressed as an absolute case count (Q-VACUOUSFLOOR). T-16's `-ge 22` was already satisfied at 29 before T-16 wrote a line. Verify by case NAME — `runs/build2-eng/digest.md` — verified-at b2f7c73
- Do NOT run `feature-worktree.py behind` from inside this worktree — `dest_for()` re-inserts the path and exits 3 on a tree that is fine. Run it from the PRIMARY checkout, where it exits 0 — verified-at b2f7c73
- Do NOT dispatch or touch T-04, T-10, T-12, T-14, T-15, T-17 — main-session-direct under DEC-174, the operator's alone — `plan.yaml` `execution_mode:` — verified-at b2f7c73
- Do NOT expect a ui-reviewer finding: all 21 planned files are Python, shell, JSON or markdown, so it self-scopes out — `plan.yaml` `files:` union — verified-at b2f7c73
- Do NOT re-raise Q-DEC90, Q-BRIEF231, Q-D21, Q-ANCHOR, Q-GUARD, Q-HOOKCTX, Q-COLLECT, Q-RUTSH, Q-VACUOUSFLOOR as new — `STATE.md ## Open Questions` — verified-at b2f7c73

## Working set

- `.harness/harness/features/FEAT-31-orchestrator-context-watch/STATE.md`
- `.harness/harness/features/FEAT-31-orchestrator-context-watch/runs/fix1-eng/digest.md`
- `.harness/harness/features/FEAT-31-orchestrator-context-watch/runs/build2-eng/digest.md`
- `.harness/harness/features/FEAT-31-orchestrator-context-watch/plan.yaml`
- `.harness/harness/features/FEAT-31-orchestrator-context-watch/notes/finding-discovery-depth-orchestrator.md`
