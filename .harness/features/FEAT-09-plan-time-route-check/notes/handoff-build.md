# Handoff — FEAT-09, build → validate — written at 2a242df, seq-2

## Next

You are PARKED until the coordinator signals FEAT-08 merged and this worktree rebased. Then,
in this order — do not re-derive it:

1. **RE-PIN `review_sha` to post-rebase HEAD BEFORE dispatching any reviewer** (INV-6). The
   rebase rewrites all four commit hashes; a pin to a vanished commit makes every reviewer's
   diff claim unfalsifiable. Say in the briefing that the pin was re-taken and why.
2. **T-02 via eng-lead** (`PLAN.md:167-233`). APPEND `"test-check-plan-routes.py"` to the
   `SCRIPTS` array — it will ALREADY have `test-cost-report.py` removed by FEAT-08. Re-read
   `run-unit-tests.sh:6` in the tree and add one element to what is actually there. Never
   rewrite from memory: a remembered 13-entry array reverts FEAT-08 and reddens both features.
3. **DECISIONS entry + regenerated index** via product-lead → documentor (`docs/**`,
   `team-config.yaml:116`). Cite `feature.yaml rulings.q2_brief_override` so the goal-check does
   not read it as a BRIEF breach. Index is GENERATED: `gen-decisions-index.py --stdout | diff -`
   must exit 0 after.
4. **FOUR-WIDE panel — code, qa, security, ui. No pre-emptive skips** (user ruling,
   `feature.yaml validate_panel`). It matters here specifically: this feature adds a resolve mode
   to the guard deciding which agent may write which path. Diff size does not argue it away.
5. pm goal-check, all 12 SCs. 6. Distillation. 7. CEO briefing.

## Trust

- `glob_to_re`/`matches` were MOVED, not modified — both hash identically either side
  (`2025f71963fd`, `59e448ad0fdb`), one definition of each survives — verified-at 1185d7f
- `--resolve` structurally cannot read stdin: `payload=$(cat)` is in the `else` branch,
  `check-domain.sh:36-41` — verified-at 1185d7f
- Open pipe answers in 0.21s where the pre-change tree hung past 10s — my own probe — 1185d7f
- **Suite is 13 PASS, NOT 14.** SC-10's registered-test clause is exercised by NOTHING yet, and
  T-03/T-04's durable cases 10-12 do not exist — `feature.yaml segment_1_receipts.deferred` —
  verified-at 2a242df
- Hook path unchanged: out-of-domain exits 2, in-domain exits 0 — my own payload files — 1185d7f
- SC-11 holds: `git diff ae2443d -- .claude/agents/harness-pm.md` is 0 bytes — verified-at 1185d7f
- FEAT-08 touches none of the four committed files, so the rebase replays them byte-identical —
  coordinator's claim — **UNVERIFIED by me; re-check at the rebase**
- `check-domain.sh` — the write-permission guard — has sat committed with ZERO independent review
  since 2a242df. A window that existed; name it as such in the briefing — verified-at 2a242df

## Dead ends

- Do NOT re-probe the hook with an inline escaped-quote payload: it yields a false exit 0 that
  looks like a regression. The measurement was broken, not the code — build payload FILES —
  verified-at 1185d7f
- Do NOT resume the cost reconciliation. The 0.54 residual was measured across two
  differently-shaped samples of mine, and the subsystem is being deleted on purpose —
  `feature.yaml cost_metering_deleted` — verified-at 2a242df
- **Write NO cost line in the briefing and invent no figure.** The mandate is gone from the
  playbook (grep returns nothing in the merged text) — `feature.yaml rulings.qE_no_cost_line` —
  verified-at 2a242df. Note once that the harness no longer meters spend (DEC-178).
- Do NOT re-run the panel before the re-pin, and do NOT skip a panel step — source: user ruling

## Working set

- `.harness/features/FEAT-09-plan-time-route-check/feature.yaml` (rulings, receipts, next_steps)
- `.harness/features/FEAT-09-plan-time-route-check/STATE.md`
- `.harness/features/FEAT-09-plan-time-route-check/PLAN.md` (T-02 at `:167-233`)
- `.harness/features/FEAT-09-plan-time-route-check/BRIEF.md` (the 12 SCs)

**Carry this verbatim into the briefing, unsoftened (user instruction):** this collision is
exactly the failure FEAT-09 exists to prevent — and the checker this feature builds would not
have caught it, because the collision is in a tool the plan uses, not a path a task writes.
