# FEAT-30 archreview S-B — is `run-unit-tests.sh` inside DEC-174's enforcement carve-out

**BLUF: T-08 is correctly laned `team`/`harness-dev-ops`. `run-unit-tests.sh` and
`.harness/harness.json`'s `test_kinds` are outside DEC-174's enforcement category as it
currently stands — not "close but arguable," genuinely outside on the evidence below. I would
sign this.**

## 1. DEC-174 text (`.harness/harness/docs/DECISIONS.md:4655`, index row `DECISIONS-INDEX.md:192`)

Original table names the category **"hooks, validators, gate scripts"** with examples
`check-domain.sh`, `bash-write-guard.sh`, `validate-digest.py`, `check-state.sh` — all four police
an agent's *live actions* mid-run (write domain, bash guard, digest shape, state invariants).

**am.4 (2026-08-19, one day before this dispatch), quoted exactly:**
> "The category governs. The parenthetical is examples, and it is now stale."
> "So the enforcement layer is: `check-domain.sh`, `bash-write-guard.sh`, `validate-digest.py`,
> `check-state.sh`, `check-plan-routes.py`, and the test file of each. A script that becomes a
> gate joins the list on the day it becomes one, and this entry is amended when that happens —
> the category decides, the list records."

am.4 promoted `check-plan-routes.py` because DEC-183 made it a required-CI-job step *after*
DEC-174 was written, so the original list could not have named it.

**Load-bearing fact: am.4's own prose already discusses `run-unit-tests.sh` by name**
(`tests.yml:97`'s comment, quoted inline in am.4: *"run-unit-tests.sh runs its TEST, never the
checker"*) — the author had it in view, the category is declared non-exhaustive and
self-amending on exactly this trigger, and still did not add it. That reads as a considered
omission, not an oversight.

## 2. `run-unit-tests.sh` characterised

- **Not a hook.** `.claude/settings.json` lists exactly 7 hook registrations
  (`inject-expertise.sh`, `check-domain.sh` PreToolUse+PostToolUse, `branch-create-gate.sh`,
  `bash-write-guard.sh`, `dispatch-guard.sh`, `validate-digest.py --hook`). `run-unit-tests.sh`
  is not among them — confirmed by grep.
- **Is a required-CI-job step**, same job as `check-plan-routes.py`: `.github/workflows/tests.yml:75-84`
  ("Unit suite" / "Integration suite"), inside job `integration`, the one branch-protection
  context. Wired in on 2026-08-06 (`git log --diff-filter=A`), i.e. after DEC-174 was signed
  (2026-08-03) but the script itself dates to 2026-07-31 — created before DEC-174, wired into CI
  after.
- **What it does**: runs each `test-*.py` under `bin/` via `python3`, reports PASS/FAIL, and
  carries a drift detector (`run-unit-tests.sh:41-56`) that exits 2 ("MISCONFIGURED") if any
  `test-*.py` file isn't registered in `UNIT_SCRIPTS`/`INTEGRATION_SCRIPTS`. That drift check is
  the closest thing to a "validator" in the file — but it validates the test suite's own
  completeness, not the harness's write/digest/state/plan-route control plane. It has **no
  dedicated test file of its own** in either array (unlike the five DEC-174 scripts, each of
  which has "the test file of each" explicitly enumerated).
- Of the 30 scripts it runs, only 5 test the actual DEC-174 enforcement scripts
  (`test-check-domain.py`, `test-bash-write-guard.py`, `test-validate-digest.py`,
  `test-check-state.py`, `test-check-plan-routes.py`) — already named individually. The other 25
  test ordinary application logic (`factory_cli`, `gh_board`, `layout_migration`, etc.).
  `run-unit-tests.sh` is a generic runner that happens to execute those five among many; it does
  not itself decide any harness-control-plane pass/fail.

## 3. `.harness/harness.json` `test_kinds` characterised

- Read by `upgrade-config.py` (config-merge tool, project always wins) and by `check-state.sh:843`
  for **INV-20, warn-level only** — flags a `cmd: null` kind against a codebase surface map, never
  blocks. No PreToolUse/SubagentStop hook reads it. It is config in the DEC-100 sense
  (`test_matrix` maps `config` → `[]`, TDD-exempt) — the field this task edits is exactly that
  shape, not an enforcement mechanism.

## 4. Precedent (evidence, not authority)

Grepped every `plan.yaml` under `.harness/harness/features/*` for tasks whose `files:` include
`run-unit-tests.sh` or `harness.json`. Dominant pattern, all post-DEC-174 (2026-08-03):
`team`/`harness-backend-dev` or `team`/`harness-dev-ops` for registering new test files and
editing `harness.json`'s `test_kinds.cmd` — FEAT-10 (7 tasks), FEAT-12, FEAT-19, FEAT-23, FEAT-27,
FEAT-29, all shipped. A minority (FEAT-18 T-02, FEAT-20 T-01) laned the same shape as
`main-session-direct`, so practice is not uniform — but `team` is the majority precedent and was
never flagged as a DEC-174 violation across six shipped features.

## 5. `check-plan-routes.py` cannot catch a mislane here

`.harness/team-config.yaml:166,210-211` grants `harness-dev-ops` (and `harness-backend-dev`)
`.claude/skills/harness/bin/**` and `.harness/harness.json` directly (`upsert: true`).
`check-plan-routes.py` only checks whether a declared `execution_mode` matches team-config domain
grants (`resolve_agents`, `LEGAL_MAIN_SESSION_TOKEN` logic) — it has **no DEC-174 awareness** (no
match on "enforcement" anywhere in the file). A `team` lane on these two paths resolves clean
regardless of the carve-out question. **No automated check can catch a mislane here at all** —
this is exactly why it needed an archreview.

## Recommendation

**Outside the category. T-08 is correctly `team`.** What breaks under each reading:

- **As laned (outside)**: the residual risk is real but general-CI-shaped, not DEC-174's specific
  circularity — a bug landed in the drift detector or SCRIPTS arrays by a team agent could
  degrade the suite meant to catch it, mitigated the same way any team-laned code is (review, a
  human reading the diff at merge), same protection every other `team` task gets.
- **If forced inside** (`main-session-direct` required): six shipped features' worth of
  `team`-laned test-registration and `harness.json` edits would retroactively read as violations,
  and every future feature that adds a `bin/test-*.py` file — a near-constant event — loses team
  execution for a mechanical one-line array append, with no textual support in DEC-174/am.4 for
  drawing the line there.
- **Split** (harness.json inside, runner outside, or the reverse): no textual basis — am.4
  enumerates whole scripts, not sub-surfaces of one file. I would not sign a split without a new
  decision entry drawing that line explicitly.

## Open question

am.4 discussed `run-unit-tests.sh` by name and did not add it to the enumerated five, under a rule
that says a script "joins the list on the day it becomes one." Worth a short amendment (am.5, or a
line in DEC-174's table) recording that omission as deliberate, so this exact question does not
recur on the next feature that touches this file — non-blocking, T-08 does not need to wait on it.
