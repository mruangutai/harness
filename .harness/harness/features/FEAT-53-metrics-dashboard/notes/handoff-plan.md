# Handoff — FEAT-53-metrics-dashboard, plan → build — written at 9bb833f1, seq-8

## Next

Do not dispatch a build segment and do not fix the open panel finding. The plan is unsigned and the
cycle-2 panel returned FAIL at high, so the next act is the operator's: read
`notes/ship-review-2026-09-01-plan-c2.md` and rule on four things — the high finding `PF-45518258`
(one `depends_on` line on `T-16`), the cycle-time origin (Option A changes `D-14`/`T-06`/`D-21`,
Option B rewords `REQ-03`), backlog rows `B-11`..`B-14`, and opening the DEC-5 prototype at
`notes/prototypes/FEAT-53/`. Once ruled, one pm dispatch through `harness-product-lead` applies the
consolidated answers file; only the main session signs (`plan-merge.py sign-approval`).

## Trust

- plan.yaml carries 22 tasks, 21 decisions, `status: plan`, `approval.status: pending`, and `panel:`
  at `cycle: 2` with 13 findings — 8 cycle-1 dispositioned (2 resolved, 6 overruled), 5 cycle-2 open
  — re-loaded with `yaml.safe_load` myself — verified-at 9bb833f1
- `D-03` names Flask and rejects FastAPI+uvicorn, a Node server and stdlib ThreadingHTTPServer by
  name; no line in plan.yaml, BRIEF.md or DESIGN.md still asserts a stdlib server, and the only
  surviving `stdlib` matches are D-03's own reject list, T-12's replacement note and the spliced
  comment block — grepped myself — verified-at 9bb833f1
- The cycle-2 high finding is a graph property, invisible to every declared verify in the plan:
  `T-16` (`depends_on: [T-12, T-15]`) commits the bundle, `T-21` (`depends_on: [T-14, T-15]`) mounts
  the chart, nothing rebuilds after — `runs/2026-09-01-08-validator/digest.md` — verified-at 9bb833f1
- `check-state.sh` flags nothing about the ~250-line comment block spliced into plan.yaml between
  the last task and `panel:`; `safe_load` is unaffected and no sanctioned verb can remove it — ran it
  myself — verified-at 9bb833f1
- The DEC-5 prototype renders a tracked zero beside a never-tracked feature on identical input, 37/37
  smoke checks — `runs/2026-09-01-07-product/digest.md` — UNVERIFIED by me: I did not execute the
  prototype, and nobody has opened it in a browser

## Dead ends

- Do not open a pre-signature fix cycle for a panel finding at high or worse: DEC-207 routes it to
  the operator's one batched review pass, and only `approval.rulings` records an overrule —
  `DECISIONS.md:6366-6373` — verified-at 9bb833f1
- Do not reopen `D-20` (client build) or `D-08`/`T-18` (charting alpha, Shape B built this
  increment): confirmed as drafted by the operator, and both cycle-2 readers re-walked them and
  raised nothing — `notes/answers-2026-09-01-plan-signature.md` — verified-at 9bb833f1
- Do not run `plan-merge.py` from inside this worktree: it vendors `.claude/skills`, so its copy
  predates `set-panel` and exits 2 with `invalid choice`. Run the main checkout's copy by absolute
  path — same tool, same lock — `runs/2026-09-01-09-product/digest.md` — verified-at 9bb833f1
- Do not expect a `review_sha` or a code grade for any plan-phase validator run: DEC-207 grades a
  specification and `code_grade: n_a` is correct — verified-at 9bb833f1

## Working set

- .harness/harness/features/FEAT-53-metrics-dashboard/notes/ship-review-2026-09-01-plan-c2.md
- .harness/harness/features/FEAT-53-metrics-dashboard/notes/answers-2026-09-01-plan-signature.md
- .harness/harness/features/FEAT-53-metrics-dashboard/plan.yaml
- .harness/harness/features/FEAT-53-metrics-dashboard/runs/2026-09-01-08-validator/digest.md
- .harness/harness/features/FEAT-53-metrics-dashboard/BRIEF.md
