# Handoff — FEAT-13, plan → build — written at f424609, seq-1

## Next

Do NOTHING until the operator signs. The plan phase ends at his signature, which only the main
session writes: `approval.status` in `plan.yaml` and `## Approval` in `BRIEF.md`, both `pending`
today. On signature, the build phase opens with T-01 — one task, `change_type: cross_module`,
`execution_agent: harness-backend-dev` — dispatched to `harness-eng-lead`, then the qa segment
(`--kind unit` and `--kind integration`, both blocking), then T-02 which `depends_on: [T-01]`.
Create the feature branch first; none exists and none was created here.

## Trust

- All nine source and test files in scope are byte-identical between this working tree and
  `origin/main` at 278de74 — `git diff --quiet origin/main -- <each>` — verified-at f424609
- The baseline is GREEN and T-01's chained `verify:` runs in 6.31s against a 60s bar — unit 0.73s
  over 10 scripts, `test-factory-integration.py` 5.58s, both exit 0 — verified-at f424609
- `unit` and `integration` are the only kinds `cross_module` requires and both have active runners
  in `harness.json` `test_kinds` — verified-at f424609
- Issue #216's real board item on project 3 is `PVTI_lAHOAAases4BfZ9Zzg2AMPA`, and that query
  returned it for a CLOSED issue — one live read-only GraphQL call, feature.yaml `q2_board_item_id`
  — verified-at f424609
- `factory_land.py:31` `_find_item_id(owner, ...)` takes the BOARD owner, and `owner` at the `:92`
  call site is `fleet["board"]["owner"]` — the new helper needs `args.repo`, a wrong value in easy
  reach — verified-at f424609
- The literal `factory_gh.project_items` occurs 1/1/2 times in decompose/land/claim today, matching
  T-01's `verify:` zero/zero/one structure exactly; the one comment mention in decompose (`:304`)
  is the BARE token and does not match the pattern — verified-at f424609
- `check-plan-routes.py` returns 0 violations and `plan.yaml` `safe_load`s with `feature:` matching
  the directory name — verified-at f424609

## Dead ends

- Do not reopen T-01's task shape: ONE task, ruled by eng-lead on FEAT-11's precedent —
  `runs/2026-08-10-02-eng/digest.md` — verified-at f424609
- Do not fix `land`'s closed-issue failure: already filed as issue #238 and ruled out of scope —
  `.harness/notes/grilling-board-read-lookups-2026-08-10.md` `## Out of scope` — source: operator
- Do not touch the claim poll at `factory_claim.py:238` or `project_items` and its `totalCount`
  guard — same artifact, `## Settled` — source: operator
- Do not assign test authoring to `harness-qa`: defect #218 means it escalates rather than writes;
  T-01's `intent:` already puts authoring with the eng specialist — source: operator dispatch
- Do not run a live board MUTATION for proof. T-02 is a read: two `rate_limit` readings around one
  lookup, no snapshot, no restore — `plan.yaml` T-02 `intent:` — verified-at f424609

## Working set

- `.harness/features/FEAT-13-single-issue-board-lookup/plan.yaml`
- `.harness/features/FEAT-13-single-issue-board-lookup/BRIEF.md`
- `.harness/features/FEAT-13-single-issue-board-lookup/feature.yaml`
- `.harness/notes/grilling-board-read-lookups-2026-08-10.md`
- `.harness/features/FEAT-13-single-issue-board-lookup/runs/2026-08-10-02-eng/digest.md`
