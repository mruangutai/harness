# Security review — FEAT-12 end-copy-distribution — review_sha `d543809`

Diff basis: `git diff --stat 687fd3e..d543809 -- <the 22 files in dispatch's THE FILE SET>` —
matched the given file set exactly (22 files, confirmed by comparing the `--stat` output against
the dispatch's list). `687fd3e` is the commit immediately preceding `8782ee1 FEAT-12 signed`
(`git log --oneline 278de74..d543809`), i.e. the tree before any FEAT-12 work. qa's digest
independently restricted to FEAT-12's 11 commits and reported the same 45-path total (27 task
files + 18 bookkeeping); my 22-file code/prose subset is consistent with that.

## VERDICT: PASS (findings, none blocking)

## Q1 — the guard removal, residual posture

**Answer: none.** A workspace built from `mruangutai/kaya-ai`'s current state — whether the
operator's existing local clone or a future factory `workspace_root` clone — runs with zero
harness guard hooks. Established three independent ways:

1. `cd /Users/molchairuangutai/GitHub/kaya-ai && python3 -c "import json; d=json.load(open('.claude/settings.json')); ..."` —
   printed the 4 surviving hooks (`work-tracking-nudge.sh`, `pre-commit-tests.sh`,
   `pr-issue-gate.sh`, `branch-issue-gate.sh`), all non-harness; `[c for c in cmds if 'harness' in c]`
   → `[]`. `git log --oneline -3 HEAD` and `git log --oneline -3 origin/master` both show
   `7d2f946 Remove the copied harness: this repo is worked on remotely, not enrolled` as HEAD —
   local and remote match, T-05's push landed.
2. `Read` of `.claude/skills/harness/bin/factory_workspace.py` in full (untouched by this diff —
   `git diff --stat 687fd3e..d543809 -- .../factory_workspace.py` is empty) — its only actions are
   `git clone`/`fetch`/`checkout`/`reset --hard`. No call installs, merges or writes
   `.claude/settings.json`.
3. `grep -ln "merge-settings\|settings.json\|check-domain\|bash-write-guard\|dispatch-guard\|validate-digest\|inject-expertise" .claude/skills/harness/bin/factory_*.py` → no matches across
   `factory_claim.py`, `factory_cli.py`, `factory_config.py`, `factory_decompose.py`,
   `factory_gh.py`, `factory_land.py`, `factory_workspace.py`. Nothing in the factory tooling
   re-wires guards after a clone.

**Whether a future factory dispatch would even be *rooted* at that guard-less checkout — the thing
that would turn "no guards in kaya's settings.json" into "no guards for the session touching
kaya" — is not established in code.** `grep -rln "factory_workspace" .claude/skills/harness/bin`
shows only `factory_land.py`, `factory_config.py` and test files consume the module; no agent
`.md` or skill `.md` references it (`grep -rn "factory_workspace" .claude/skills/harness/*.md
.claude/agents/*.md` → no hits), and `grep -rn '"claude"\|subprocess.*claude'
.claude/skills/harness/bin/*.py` finds no session-spawn call anywhere. Session-launch-at-checkout
is not built yet (FEAT-10 increment 1 shipped the git-level tools only). So I cannot confirm the
"factory's own guards" alternative in the dispatch's three-way question is even reachable code
today, and I am not rating this as if it were.

Separately, `check-domain.sh` — read via `plan.yaml`'s own lanes table, not edited (DEC-174) —
explicitly passes paths **outside `CLAUDE_PROJECT_DIR` through ungoverned**
(`.harness/features/FEAT-12-end-copy-distribution/plan.yaml`, lanes row for
`/Users/molchairuangutai/GitHub/kaya-ai/**`: *"outside CLAUDE_PROJECT_DIR, so check-domain.sh
passes it through ungoverned"*). So even a harness-rooted session touching kaya-ai by absolute
path was never governed by harness's own domain check, before or after this feature — that half
of the guard question is a FEAT-10 factory-model boundary, not something FEAT-12 changed.

**Disposition: `med`, not a regression this feature is obligated to fix, but a real sequencing
gap it creates.** `SPEC.md` §3.3 (rewritten in this diff) states the design intent plainly: *"the
first factory run against it clones it under `workspace_root`; nothing is installed into it"* —
so the guard-less clone is asserted as intended baseline, not an oversight. The BRIEF frames
stripping the stale copy as correct (a stale gate is worse than none). I agree with both. What is
not addressed anywhere in the BRIEF, plan or SC list: **T-06 (this same feature) makes kaya
fleet-reachable in the same commit range that T-03/T-05 strip its only guards**, and nothing — no
task, no SC, no gate — requires `/harness-init` (the documented re-wiring mechanism,
`.claude/skills/harness-init/SKILL.md`, still calling `merge-settings.py` unchanged by this diff)
to run again before a team or factory dispatch first touches kaya. Today, right now, a session
rooted at `/Users/molchairuangutai/GitHub/kaya-ai` runs with none of bash-write-guard,
check-domain, dispatch-guard or digest validation. `merge-settings.py`'s own "all 8 prerequisites
present" contract (`.claude/skills/harness/bin/merge-settings.py:315`) is now false for that repo
and nothing in the tree records that as a known, accepted precondition next to kaya's `fleet.yaml`
entry.

**Not a `must_fix`**: the remedy (schedule an init/re-wire step) is a step the signed plan and its
approved `SPEC.md` rewrite deliberately did not include — adding it unilaterally would be adding
scope the operator's approval didn't grant, not fixing a defect in what was built. Raised as an
open question instead.

## Q2 — `.claude/settings.json.harness-bak` on kaya's `origin/master`

**Confirmed gone**, reached over the network. `cd /Users/molchairuangutai/GitHub/kaya-ai && git
fetch origin master --quiet && git ls-tree -r --name-only origin/master | grep -i
"harness-bak\|settings.json"` → returns only `.claude/settings.json`, no `.harness-bak` entry.
Local working tree matches: `ls -la .claude/settings.json.harness-bak` → "No such file or
directory". D-06's reversal at signature landed as claimed.

## Q3 — the registry.json deletion and the directory-probe residue

**Unchanged, confirmed by diff, not by re-derivation.** `git diff 687fd3e..d543809 --
.claude/skills/harness/bin/check-plan-routes.py` and `...wayfind.py` and
`...test-check-plan-routes.py` show comment-only edits — the file-probe logic in
`check-plan-routes.py`'s `discover_plans()` and the `KNOWN_DIRECTORY_PROBE`-equivalent exception in
`test-check-plan-routes.py` case_20/case_21 are byte-identical except for the prose explaining
*why* `$HOME/.harness/` exists (re-attributed from "`deploy.sh` writes registry.json there" to
"the 2026-08-10 backup archives sit there"). `ls -la ~/.harness/` confirms the new attribution:
two `.tgz` backup archives, no `registry.json`. The exposure is real, pre-existing, explicitly
out of this feature's scope per the dispatch, and I am not re-scoping it.

## Q4 — standard lens: secrets, injection, exposure

- `test-no-distribution.py` (`Read` in full): all `subprocess.run` calls use list-form argv
  (`["git", "-C", ROOT, "ls-files"]`), no `shell=True`, `ROOT` derived from `__file__`, never from
  input. No injection surface.
- `factory_config.py`'s `workspace_path`/`repo_entry` and `factory_workspace.py`'s clone-URL
  construction (`f"https://github.com/{args.repo}.git"`, list-form `subprocess.run`, no shell) take
  `fleet.yaml`'s `name` field, which is `main-session-direct`-lane-only per this feature's own
  `plan.yaml` lanes table — operator-authored config, not external input. No shell interpolation
  either way. Unchanged by this diff (`factory_workspace.py` has an empty diff in range;
  `factory_config.py`'s diff is docstring-only — `git diff 687fd3e..d543809 --
  .../factory_config.py` shown above). Not a new finding; actor already controls the value.
- `upgrade-config.py`, `run-unit-tests.sh`, `test-upgrade-config.py`: diffs are user-facing message
  text and a test-registration line only (`git diff` output inspected directly). No logic change.
- Re-swept the full 22-file set (not just the prose subset), including the two deletions
  (`deploy.sh`, 287 lines; `harness-deploy.md`, 121 lines): `git diff 687fd3e..d543809 -- <all 22
  paths> | grep -iE "token|secret|password|api[_-]?key|credential|ssh|bearer|-----BEGIN"` — every
  hit is either the test's own `TOKEN_RE`/`token sweep` identifier (source-scan terminology, not a
  secret) or the word "credential" inside unrelated `DECISIONS-INDEX.md` commentary. No secrets,
  no PII, no hits inside `deploy.sh`'s or `harness-deploy.md`'s deleted content.
- `.harness/team-config.yaml`'s added documentor receipt-path grant (`receipt-harness-documentor-*.md`)
  is present in this diff range but reads as issue #216's fix, not FEAT-12's own change — noted,
  not treated as a FEAT-12 finding (adds a scoped grant, not a widening of an untrusted surface).

## Already-found items (per dispatch instruction)

Items 1 and 2 (settled by qa with mutants): agree with disposition, not relitigated. Items 3 and 4
(open, low, pm's / no test): agree, not relitigated — neither has a security dimension.

## Findings summary

| # | Severity | Item |
|---|---|---|
| 1 | med | kaya-ai's guard posture is genuinely zero right now (verified), and this feature makes it fleet-reachable (T-06) in the same range that strips its only guards (T-03/T-05), with no task/SC/gate requiring `/harness-init` re-wiring before first dispatch. Intended per `SPEC.md` §3.3's own rewrite; the gap is that the precondition is unrecorded. |
| — | info | `check-domain.sh` cannot govern any path outside `CLAUDE_PROJECT_DIR` by design (confirmed via `plan.yaml`'s lanes table) — a FEAT-10 factory-model boundary fact, not FEAT-12's to fix. Worth an Expertise entry under a future distillation dispatch; not written now (`expertise_update: []`). |

No `must_fix`. `severity_max: med`.
