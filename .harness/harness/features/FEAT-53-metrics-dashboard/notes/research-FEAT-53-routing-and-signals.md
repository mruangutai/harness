# Research — FEAT-53 — routing, and the four signals the plan rests on

**BLUF.** The dashboard is control-plane harness source and must live under
`.claude/skills/harness/bin/dashboard/`. `web/src/**` is not merely unconventional here — it is
*structurally unreachable*: in the harness base only control-plane targets can be granted
(`harness_boundary.select_base`, harness branch returns `is_control_plane_target`), so every
product-side glob in `team-config.yaml` — `web/src/**`, `src/**`, `tests/**`, `evals/**`,
`supabase/migrations/**` — resolves NOBODY in this checkout. Measured, all at
`e8e1b78be3379d4a669aa7e28aef8f76eb942471`.

**That SHA is provenance, not a baseline to copy.** It is the HEAD of the pre-rename FEAT-51
worktree, which no longer exists; this feature now builds in `.claude/worktrees/harness/FEAT-53` on
`feat/FEAT-53`, at `38dd36222258240b5dab251eb48ef869fde35447` when this line was written. Every
resolution above was re-derived in the FEAT-53 worktree and is unchanged. `lanes.resolved_at` in
`plan.yaml` must be re-derived against the live worktree HEAD rather than copied from here.

## Resolution table (`check-domain.sh --resolve`, worktree FEAT-53)

| path | owner |
|---|---|
| `.claude/skills/harness/bin/**` (incl. `dashboard/client/src/App.tsx`, nested `package.json`, `tsconfig.json`) | harness-backend-dev, harness-dev-ops |
| `.harness/harness.json` | harness-dev-ops |
| `.harness/harness/docs/METRICS.md` | harness-documentor |
| `.harness/harness/features/FEAT-53-metrics-dashboard/touchpoints.jsonl` | harness-orchestrator |
| `web/src/**`, `src/**`, `tests/**`, `docs/**`, `.gitignore`, `.claude/commands/**`, `.claude/skills/harness/templates/**`, `.harness/team-config.yaml`, `.harness/metrics/trend.jsonl`, root `package.json`/`tsconfig.json` | NOBODY |

Note the root `package.json` is `shared:` (owned by nobody) but the *nested*
`bin/dashboard/client/package.json` resolves to backend-dev/dev-ops — the shared entries are
root-anchored, so the client manifest is routable.

**Consequence:** `harness-frontend-dev` can write nothing in this repository today. Its only source
grant is a product-side glob. T-01 widens it to the client subtree; without T-01 the client work
routes to backend-dev, which is the wrong specialist for `.tsx` + Astryx.

**Distribution:** there is no copy-out step to preserve — `deploy.sh` and `/harness-deploy` were
removed and `test-no-distribution.py` keeps them removed. The authored skill tree *is* the
distribution (DEC-202), so shipping under `bin/dashboard/` is what "part of the Harness distribution"
means, and shipping under `web/src/**` would make it this repo's own application (REQ-02 failure).

## Signal 1 — cycle-time start EXISTS, contrary to the grilling

The grilling records "no structured approval timestamp exists anywhere today". Falsified:
`plan.yaml` carries `approval.date` (`YYYY-MM-DD`), written by `plan-merge.py sign-approval`.
Measured over `.harness/harness/features/*/plan.yaml`: **41 of 54 features carry a populated
`approval.date`**; the 13 without are pre-`plan.yaml` features and two `abandoned` ones. So
cycle-time start = `approval.date`, day granularity, and a feature without one is
unavailable-with-reason (REQ-11), never zero.

## Signal 2 — commit attribution is far sparser than assumed

`git log --pretty=%s` over 975 first-parent-visible subjects:

| shape | count |
|---|---|
| no `[harness:...]` prefix at all | 753 |
| feature id (`FEAT-41`, `BUG-1128`) | 128 |
| bare task id (`t-01`) | 52 |
| `human` | 8 |
| free-form (`replan`, `review-pin`, `sc-04,sc-13`, comma lists) | ~34 |

**77% of commits carry no prefix.** KPI 6 therefore cannot be a two-bucket split; it needs named
unattributed buckets (`no-prefix`, `human`, `unresolvable-step-id`) as first-class output. A bare
`t-NN` is only resolvable with the owning feature's `plan.yaml` in hand, so the join is
branch/feature-scoped, not global. SC-14 already demands this shape.

## Signal 3 — escaped defects have a project-agnostic source

Every onboarded project uses the same `.harness/<repo>/features/` layout and the same
`BUG-NN-<slug>` id convention (`harness-brief`). Measured here: **8 of 54 feature units are `BUG-*`**,
and **2** commits are `Revert `. `fix:` appears in 58 subjects but most are within-feature fixes, so
including them would inflate the number — excluded, and the exclusion is part of the stated rule.

## Signal 4 — grading is already a JSON contract

`code-grade.py --json <paths...>` prints `{records:[{path,line,qualname,cyclomatic,cognitive,abc,
grade,driver,bar,result,severity}], passing, ungraded}` (`code-grade.py:134-159`). Per-record `bar`
(3 test paths, 4 otherwise) is in the payload, so DESIGN CAP-03 needs no second source. It resolves
the git root from **cwd**, so the KPI must invoke it with cwd set to the viewed project (REQ-02).

## Test-registration coupling (ordering hazard, resolved in the plan)

`run-unit-tests.sh` exits 2 on any on-disk `test-*.py` absent from its two arrays, and exits 2 when
an `INTEGRATION_SCRIPTS` name is absent from `harness.json` `test_kinds.integration.detect`. A name
listed in an array whose file does not exist yet FAILS the suite. An extra *declared* detect literal
with no file and no array entry is inert. Hence T-03 pre-declares the two integration literals in
`harness.json` (dev-ops-only file), and each creating task registers its own file in the bash array
it owns — no window in which the suite is red.

## Open

- `@astryxdesign/core` version is pinned nowhere (DESIGN Q1). Node v26.0.0 / npm 11.12.1 are present
  on this machine; neither is asserted for any other machine.
