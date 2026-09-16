# Handoff — BUG-1305-run-state-clobber, plan → signature/build — written at c369fb1f, seq-1

## Next

Present BRIEF.md and plan.yaml to the operator for one batched signature review (DEC-176), carrying
the five open `panel.findings` and the four rulings listed in STATE.md Open Questions. Sign with
`plan-merge.py sign-approval`, plus `--overrule PF-ID:<reason>` for any open finding the operator
accepts. Nothing below the main session may sign either artifact. After signature, run
`gh-sync.py open <feature-dir>` — INV-26 is red until it does.

## Trust

- All three INV-32 readers (`should-not-exist`, `scope`, `goalcheck`) resolve `ran` under the
  checker's own indexing expression — plan.yaml `panel.readers` — verified-at c369fb1f
- No open panel finding exceeds `med`, so INV-32 needs no risk acceptance to pass — plan.yaml
  `panel.findings` — verified-at c369fb1f
- `check-plan-routes.py` exit 0; every surface is `main-session-direct` under DEC-174 — plan.yaml
  `lanes.rows` — pm-reported, not re-run by me — UNVERIFIED
- The `run_uid` mechanism refuses the modal B-11 collision and refuses no owner — notes/research-BUG-1305-goalcheck-plan-c3.md — verified-at c369fb1f
- End-to-end mint delivery cannot be observed before merge: a main-session-direct probe runs under
  the main checkout's pre-change hook — runs/planpanel-c2-validator/digest.md — UNVERIFIED

## Dead ends

- Session identity as a denial input: refuses a resumed owner — notes/research-BUG-1305-goalcheck-plan-c2.md — verified-at c369fb1f
- Marker-acquisition refusal keyed on an empty prior: unreachable by a foreign run, fires on the
  recovering owner — runs/planpanel-c1-validator/digest.md — verified-at c369fb1f
- Corpus-wide marker backfill (T-10, retired): reddens every live tree on day one — runs/planpanel-c1-validator/digest.md — verified-at c369fb1f
- Reversing the unparseable-prior refusal (#1106 gap b): weakens a protection this feature
  strengthens — BRIEF.md `## Constraints` — verified-at c369fb1f

## Working set

- .harness/harness/features/BUG-1305-run-state-clobber/BRIEF.md
- .harness/harness/features/BUG-1305-run-state-clobber/plan.yaml
- .harness/harness/features/BUG-1305-run-state-clobber/notes/research-BUG-1305-goalcheck-plan-c3.md
- .harness/harness/features/BUG-1305-run-state-clobber/runs/planpanel-c2-validator/digest.md
- .harness/harness/features/BUG-1305-run-state-clobber/notes/receipt-harness-dev-ops-diag-c1.md

## Done when

Scope: operator signs BRIEF and plan, then the mirror opens
Authority: approval:.claude/worktrees/harness/BUG-1305-run-state-clobber/.harness/harness/features/BUG-1305-run-state-clobber/BRIEF.md#Approval
