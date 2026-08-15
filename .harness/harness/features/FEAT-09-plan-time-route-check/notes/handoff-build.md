# Handoff — FEAT-09, build → validate — trimmed to shape at 4918d06, seq-3

Trimmed by the validate-phase orchestrator: it was 63 lines against INV-17's 60 cap. The cap
is only enforced once `phase:` moves PAST the seam, so it sat unflagged for the whole build
phase — exactly when a successor reads it. Substance preserved; claims I re-verified are
re-tagged to the current sha.

## Next

Build is COMPLETE. All four tasks DONE, source frozen. Remaining, in order:

1. **FOUR-WIDE panel — code, qa, security, ui. No pre-emptive skips** (user ruling,
   `feature.yaml validate_panel`). It matters here specifically: this feature adds a resolve
   mode to the guard deciding which agent may write which path. Diff size does not argue it away.
2. pm goal-check, all 12 SCs. 3. Distillation. 4. CEO briefing.

The pin is TAKEN: `review_sha 4918d06`, once, after the source completed. Scope every reviewer
from base `47ed11f`.

## Trust

- `glob_to_re`/`matches` were MOVED, not modified — both hash identically either side, one
  definition of each survives — verified-at 6792331
- `--resolve` structurally cannot read stdin: `payload=$(cat)` is in the `else` branch. An open
  pipe answers in 0.21s where the pre-change tree hung past 10s — my own probe — 6792331
- Hook path unchanged: out-of-domain exits 2, in-domain exits 0 — my own payload FILES — 6792331
- The rebase replay claim is no longer UNVERIFIED: byte-identical on all four source files,
  re-checked by the successor — verified-at 3c245c3
- Suite is **13 PASS**, and that is the correct post-FEAT-08 number, not 12 or 14. `PLAN.md:312`
  predicts 14 and is stale prose — no `verify:` asserts a count — verified-at 4918d06
- `check-domain.sh` — the write-permission guard — sat committed with ZERO independent review
  for the whole park. A window that EXISTED; name it as such in the briefing — verified-at 4918d06

## Dead ends

- Do NOT re-probe the hook with an inline escaped-quote payload: it yields a false exit 0 that
  looks like a regression. The measurement was broken, not the code — build payload FILES —
  verified-at 6792331
- Do NOT resume the cost reconciliation. The subsystem is deleted on purpose —
  `feature.yaml rulings.qE_no_cost_line` — verified-at 4918d06
- **Write NO cost line in the briefing and invent no figure.** The mandate is gone from the
  playbook. Note once that the harness no longer meters spend (DEC-178)
- Do NOT re-pin `review_sha` again, and do NOT skip a panel step — user ruling
- Do NOT "fix" the `:190-197` anchor in the new source comments as a builder defect. `PLAN.md:210`
  carries the same wrong anchor — the approved plan is the origin — verified-at 4918d06

## Working set

- `.harness/features/FEAT-09-plan-time-route-check/feature.yaml` (pin, rulings, backlog)
- `.harness/features/FEAT-09-plan-time-route-check/STATE.md`
- `.harness/features/FEAT-09-plan-time-route-check/BRIEF.md` (the 12 SCs)
- `.harness/features/FEAT-09-plan-time-route-check/runs/t02-eng/digest.md`

**Carry verbatim into the briefing, unsoftened (user instruction):** this collision is exactly
the failure FEAT-09 exists to prevent — and the checker this feature builds would not have
caught it, because the collision is in a tool the plan uses, not a path a task writes.
