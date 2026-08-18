# Code review — FEAT-20-migration-detector — pre-merge delta + CI reachability (PR #376)

**VERDICT: PASS.** T-A: the `ea476fd..045dcd9` delta touches zero of the 8 reviewable source files —
bookkeeping only, measured. T-B: CI gate reachability is empirically confirmed for the actual merge
candidate, not just argued from the file — a real run of PR #376 at `head_sha 045dcd9` executed the
Layout gate step to completion with genuine non-zero evidence and the required `integration` context
went green. One new, low-severity, forward-looking finding: the Layout gate step carries no
self-referential test protecting its own presence, unlike its neighbour (falsely) claims to.

Reviewed: `ea476fd..045dcd9`. `human_commits_in_scope: []` — `git log --grep="harness:human"` over
the range returns nothing.

## T-A — the delta is bookkeeping-only, measured

`git diff --name-only ea476fd..045dcd9 | wc -l` → **32 paths**: 12 under `.harness/expertise/*.md`
(distillation), 18 under `.harness/features/FEAT-20-migration-detector/` (`STATE.md`, `feature.json`,
14 `notes/*`, 2 `observations/*` — ship-review and close-out artifacts), plus
`.harness/logs/2026-08-14.md` and `.harness/notes/map-336-phase1-handoff-2026-08-14.md`.

`git diff --stat ea476fd..045dcd9 -- '*.py' '*.sh' '*.yml' docs/harness/DECISIONS.md
docs/harness/DECISIONS-INDEX.md` returns **empty** — confirmed with an extension/path filter, not by
eyeballing the name-status list. None of `layout_migration.py`, `test-layout-migration.py`,
`check-state.sh`, `test-check-state.py`, `.github/workflows/tests.yml`, `DECISIONS.md`,
`DECISIONS-INDEX.md`, `plan.yaml`/`BRIEF.md` appear. There is nothing here for Stage 1 or Stage 2 to
review; my `c0` review at `ea476fd` still covers every source line that exists at `045dcd9`.

## T-B — CI gate reachability, established from outside the step

### Trigger
`on: push: branches: [main]` + bare `pull_request:` (no `branches:`/`paths:` filter under either —
grepped, confirmed absent). This fires on a PR to any base branch and on every push to `main`. PR
#376's actual metadata: `baseRefName: main`, confirming this PR is in scope.

### Job shape
One job, `integration`, `runs-on: ubuntu-latest`. Grepped the whole file for `if:`/`continue-on-error`
at the job or step level — **zero matches**. No `needs:` (only one job, nothing to depend on). Steps
run strictly sequentially: checkout → install PyYAML/jsonschema → Unit suite → Integration suite →
Validate feature execution state → Plan-route gate → **Layout gate**.

### Does an earlier failure short-circuit the Layout gate?
**Structurally yes, by GitHub Actions' documented default** — with no `if: always()` and no
`continue-on-error` on any step, a failing step halts the job and every step after it is skipped, the
job conclusion is `failure`. This is inferred from the file's config (confirmed absence of overrides),
not demonstrated live — I am read-only and did not push a failing commit to prove it experimentally.
**This is not a gap**: since `integration` is the sole required context (below), a job that fails
before reaching the Layout gate still fails the required check and blocks merge exactly as a Layout
gate failure would. The short-circuit changes *which* diagnostic the operator sees, never whether the
merge is blocked.

### Is `integration` actually required, or merely present?
**Directly measured, not inferred from the file's own comments**:
`gh api repos/mruangutai/harness/branches/main/protection` returns
`required_status_checks.contexts: ["integration"]`, `enforce_admins: {enabled: true}`. This confirms
the workflow comment's claim independently of the comment itself. The same API call also returns
`required_status_checks.strict: false` ("require branches to be up to date before merging" is off) —
noted rather than silently dropped: the required check that gates this merge ran against PR #376's
head at run time, and if `main` had advanced since, GitHub would not force a re-run before allowing
merge. This is not a silent hole, because `on: push: branches: [main]` re-executes the identical
Layout gate against the merged tree immediately after merge — so any skew between the checked commit
and the merged result fails **noisy and post-merge**, on `main`'s own required check, not silently.

### Empirical proof the Layout gate is reached on this exact merge candidate
`gh pr view 376` → the `integration` check's run (`31849390611`) has
`head_sha: 045dcd988aedb1b58e84b85df38bcc7c392638cf` — **exactly the review SHA** — `event:
pull_request`, `conclusion: success`. Pulling the job's step list
(`gh api .../jobs/94922196739`) shows all ten steps `completed`/`success`, including `Layout gate`.
Pulling the raw log for that step shows genuine output, not a vacuous pass:

```
features: CLEAN — evidence legacy
docs: CLEAN — evidence legacy
examined 20 feature dir(s), 1 doc root(s), 7 reader file(s)
layout: 2 surface(s) clean, 0 mixed, 0 cannot-verify
layout gate examined 20 feature dir(s), 1 doc root(s), 7 reader file(s); checker exit 0
```

This is the strongest form of reachability evidence available: not a simulation, the actual production
run of the actual merge candidate, with real non-zero examined counts (so it did not pass by finding
nothing).

### Dependency risk (PyYAML/jsonschema/python version) — checked, cleared
`layout_migration.py`'s imports: `glob, os, re, sys, collections.namedtuple` — stdlib only. It does not
import `yaml` or `jsonschema`, so a failure of the "Install PyYAML and jsonschema" step cannot present
as an ambiguous Layout-gate-specific error; and if that install step failed, the job would halt long
before reaching Layout gate at all (see short-circuit above), not silently continue with a degraded
Layout gate. Python-version pinning is absent (no `actions/setup-python`) — this is pre-existing,
already documented in the file's own comments as an accepted, owner-decided risk, not something this
diff introduced; not re-filed.

### New finding (low) — the Layout gate step has no mechanical protection against future deletion
`tests.yml`'s own comment at the Layout gate step reads: *"Nothing in the repository asserts this step
is present or unneutered."* I checked this rather than took the comment's word for it: `git grep -n
"Layout gate"` across the tree at `045dcd9` returns only the step itself, feature bookkeeping prose,
and `plan.yaml` — **zero test files reference it**. `test-check-plan-routes.py` (the file the
neighbouring Plan-route gate's comment cites as its own protection) contains no reference to
`tests.yml` at all; its `case_25` is about feature-status values, unrelated. That neighbouring claim is
the pre-existing, already-ticketed issue #279 (a false claim of protection) — not re-filed here. What
*is* new here: the Layout gate makes no such false claim — it is honest — but the underlying gap is
the same shape and real for this specific step: a future PR could delete or neuter the Layout gate step
(e.g. replace its body with `exit 0`), the `integration` context would still go green because nothing
mechanically checks for the step's presence or content, and CI would silently stop verifying layout
migration forever. This was disclosed but never ruled: `notes/handoff-build.md:25` records "Nothing in
the repository asserts the `Layout gate` step exists — re-derived twice, by T-03's squad" — known to
the build squad, but absent from the ship review's B-1..B-11 backlog and from this run's already-ruled
list. Stage-2 quality finding, not a spec violation — no `REQ`/`SC` in the brief requires the step to
self-protect, so `spec_violations: []` stands; this does not gate the current merge. Rated low, not
med, matching how the ship review rated the sibling gap (#279): it requires a future PR to exploit, is
now disclosed twice in-repo, and its sibling gap already has a tracking path a fix could generalize to
cover both steps.

## Open questions

- Q1 (non-blocking): should a follow-up (e.g. widening #279, or a new ticket) add a mechanical
  assertion — a case in `test-check-plan-routes.py` or a sibling — that both the Plan-route gate and
  the Layout gate steps are present, named exactly, and unneutered in `tests.yml`? Currently neither
  step is actually protected against silent deletion; only the Plan-route gate's comment claims to be
  (falsely, per #279), and the Layout gate's own absence of protection has now been disclosed twice
  (`handoff-build.md:25`, here) without being ruled.

```yaml
VERDICT: PASS
DIGEST:
  headline: "ea476fd..045dcd9 is bookkeeping-only (32 paths, zero of the 8 source files touched — measured by extension filter); CI gate reachability for the Layout gate is empirically confirmed on the actual PR #376 run at 045dcd9 (real non-zero evidence, exit 0, required integration context green), with one new low-severity finding: the step has no mechanical protection against a future PR deleting or neutering it, disclosed but never ruled."
  severity_max: low
  findings: 1
  must_fix: []
  spec_violations: []
  reviewed: "ea476fd..045dcd9"
  human_commits_in_scope: []
  open_questions:
    - { id: Q1, question: "Neither the Plan-route gate (falsely claimed, #279) nor the Layout gate (honestly disclosed as unprotected, handoff-build.md:25) has a test asserting its presence/unneutered state in tests.yml. Worth a mechanical assertion covering both, generalizing #279's fix?", blocking: false }
  files_touched: [.harness/features/FEAT-20-migration-detector/notes/review-harness-code-reviewer-premerge.md]
  expertise_update: []
artifact: .harness/features/FEAT-20-migration-detector/notes/review-harness-code-reviewer-premerge.md
```
