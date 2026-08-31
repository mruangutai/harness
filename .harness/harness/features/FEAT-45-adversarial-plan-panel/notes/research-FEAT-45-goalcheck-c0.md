# Goal-check — FEAT-45-adversarial-plan-panel — SC-01..SC-17 at `c745d3a`

**BLUF. The GOAL is not yet met, though every task is done.** 12 of 17 criteria are met, three are
carved out to the operator's first live `/harness-plan`, and two are open: **SC-05 is falsified by
the delivered behaviour** (the gate is silent on both a resolved and an overruled finding, so the two
dispositions read identically in its output — the criterion's own falsifier), and **SC-03's second
direction is unproven** (supersession rests on a `{{cycle}}`-token-presence proxy, no behavioural
test). Neither blocks the panel from running; both are one-fix items in different lanes.

Provenance: `HEAD` is `b051cdf`, `c745d3a` is its ancestor, and
`git diff --name-only c745d3a HEAD` touches only FEAT-45 bookkeeping notes — no source file moved
after the pin. Working tree clean; nothing written outside this note.

## The table

| SC | State | Method actually run | Evidence |
|---|---|---|---|
| SC-01a `should-not-exist` (REQ-02) | met | `test-plan-panel.py` case 1a | `plan-panel.yaml:21` prompt carries "what here should not be built at all?" |
| SC-01b `scope` (REQ-04) | met | `test-plan-panel.py` case 1b | `plan-panel.yaml:42-43` "which tasks serve no live requirement, and what does the feature actually need to ship?" |
| SC-01c goal-check (REQ-03) | met | `test-plan-panel.py` case 1c | `.claude/skills/harness/SKILL.md:93-94` "does this plan deliver the operator's stated intent?" |
| SC-01 falsifier: no reader's question missing | met | three separate per-reader assertions above, never a file-global match | 24/24 in `test-plan-panel.py` |
| SC-01 falsifier: no out-of-squad harness persona | met | cases 4c/4d against `.harness/team-config.yaml` Validation members | `code-reviewer` is a Validation member; `fable-advisor` is SC-14's permitted non-harness exception |
| SC-02a `scope` output | met | `check-domain.sh --resolve .harness/harness/features/FEAT-45-adversarial-plan-panel/notes/review-harness-code-reviewer-planpanel-c0.md` | rc=0, prints `harness-code-reviewer` |
| SC-02b playbook goal-check note | met | `check-domain.sh --resolve .harness/harness/features/FEAT-45-adversarial-plan-panel/notes/research-FEAT-45-goalcheck-plan-c0.md` | rc=0, prints `harness-pm` |
| SC-02 `should-not-exist` | n/a — `outputs: []`, SC-14's scope, correctly excluded | enumerated then skipped | `plan-panel.yaml:18` |
| SC-03a `scope` writer carries `{{cycle}}` | met | `test-plan-panel.py` case 3 | `plan-panel.yaml:39` `...planpanel-c{{cycle}}.md` |
| SC-03b goal-check note carries `c<cycle>` | met | `test-plan-panel.py` case 3 | `SKILL.md:95-96` |
| SC-03c validator-lead digest | met | read | not a declared step output; run-scoped by run id per `SKILL.md:110-111` ("a new run directory") |
| SC-03d **superseded record survives a re-run** | **unmet-unproven** | grepped both new test files for `supersed\|overwrit\|survives` | no match. Only the token-presence proxy exists |
| SC-04 | met | `_inv32_run` over three fixtures + the D-13 marker mutant applied to the refusing fixture | open `high` → `VIOLATION INV-32: ... remains open without an operator overrule`; resolved → no INV-32 line; overruled → no INV-32 line. Mutant (INV-32 region cut between `# INV-32 BEGIN (FEAT-45 T-07)` / `END`): real gate `INV-32 present = True`, mutant `False`, no traceback |
| SC-05 attribution/date half | met | fixtures with `who: ""` and with `date` absent | both give `VIOLATION INV-32: ... ruling for PF-bbbbbbbb is unattributed or has an invalid date.` (`check-state.sh` INV-32 line 26) |
| SC-05 **"names which is which"** | **unmet-behaviour** | fixture: two `high` findings, `PF-aaaaaaaa` resolved + `PF-bbbbbbbb` overruled | check-state prints **zero** lines mentioning `FEAT-INV32` or `PF-`. Both dispositions read identically (silence) — the criterion's stated falsifier |
| SC-06 | met | `test-plan-panel.py` case 5 + `git ls-tree c745d3a:.omp/agents` / `:.claude/agents` | 16 and 16. Content checked: `git diff --name-status <base> c745d3a -- .omp/agents .claude/agents` shows only `M harness-validator-lead.md` — no add, no delete, membership unchanged |
| SC-07 | met | `_inv32_basic_checks[0]`, re-run directly | `panel_marker=False` → rc 1, `INV-32: FEAT-INV32 plan is approved with no complete panel result recorded.` |
| SC-08 | met | `run-unit-tests.sh --kind unit` | EXIT=0, 1461 lines, no `^FAIL`/`not ok`, ` 0 fail`. Runner NAMES both added files: `PASS test-panel-findings.py` (9/9), `PASS test-plan-panel.py` (24/24); both are in `UNIT_SCRIPTS` (`run-unit-tests.sh:30`) |
| SC-09 | met | `git show c745d3a07c2accd8395c9df7a25d911d40dc2c09:.harness/harness/docs/DECISIONS.md` and `...:DECISIONS-INDEX.md` | DEC-206 "wrapped non-harness reader" @7416, DEC-207 "plan-phase gate" @7445, each naming its precedent and citing FEAT-45 as origin. Index identity: `diff <(gen-decisions-index.py --stdout) <(git show <sha>:...INDEX.md)` → identical, tree untouched |
| SC-10 | met | `git show c745d3a07c2accd8395c9df7a25d911d40dc2c09:.claude/commands/harness-plan.md` | `Target state` bullet: "under DEC-176 all findings enter the ONE batched review pass rather than opening a separate pre-signature fix dispatch"; the whole file diff at the pin is 1 line |
| SC-11 | deferred-to-live-run | `verify: uat` — not agent-settleable | criterion's own words: "**On a live plan, the operator judges** each of the three readers to have earned its spawn" |
| SC-12 | deferred-to-live-run | `verify: uat` | "**On a live plan** whose panel raises nothing at `high`, **the operator** reaches the signature with no extra step" |
| SC-13 identity stability | met | `run-unit-tests.sh --kind unit` → `test-panel-findings.py` | case2 normalization-only ⇒ same id; case3 one-character change ⇒ different id; case4 different readers ⇒ different ids |
| SC-13 stale overrule refused | met | fixture with ruling on `PF-cafebabe` absent from findings | `VIOLATION INV-32: FEAT-INV32 STALE OVERRIDE PF-cafebabe: a reworded finding gets a NEW content-hash id...` |
| SC-14 | met | `test-plan-panel.py` cases 4a/4b | persona `fable-advisor` ∉ the 16 `.omp/agents/harness-*.md`; `outputs: []` (`plan-panel.yaml:15,18`) |
| SC-15 (two separate checks) | met | `test-plan-panel.py` cases 8a and 8b, persona read from the team file | `.omp/agents/harness-validator-lead.md:15` `- fable-advisor`; `sync-agent-adapters.py:74` `"fable-advisor"` in `SPAWNS["harness-validator-lead"]` |
| SC-16 | deferred-to-live-run | `verify: uat` | criterion's own words: "**On the first live `/harness-plan` after this ships**, `harness-validator-lead`'s dispatch ... is not refused at preflight and the reader returns" |
| SC-17 | met | `test-check-state.py` case `INV-32 plan panel fixtures, including inv32-red` (ok) + direct fixture runs | reader absent, no skip entry → rc 1, "reader should-not-exist never ran or was not recorded"; reader `status: skipped` + persona + reason → named in output, **zero** `VIOLATION` lines; refusing direction demonstrated against the D-13 marker mutant inside `_inv32_mutant_is_discriminating` |

## Count — sums to 17

| State | Count | Ids |
|---|---|---|
| met | 12 | SC-01, 02, 04, 06, 07, 08, 09, 10, 13, 14, 15, 17 |
| unmet-behaviour | 1 | SC-05 |
| unmet-unproven | 1 | SC-03 |
| deferred-to-live-run | 3 | SC-11, SC-12, SC-16 |

## The two open rows

- **SC-05 — `unmet-behaviour`, engineering lane.** `check-state.sh`'s INV-32 region emits nothing for
  a resolved finding and nothing for an overruled one, so its output cannot tell them apart. The
  *record* does distinguish them (`disposition: resolved` + `resolved_by` versus an
  `approval.rulings` entry carrying `who`/`date`), so **REQ-08 is delivered** — it is the criterion's
  demand on the *check's output* that fails. Closes by: emit one informational line per non-open
  finding naming its disposition (`resolved by T-NN` / `overruled by <who> on <date>`), and add the
  two-high fixture to `test-check-state.py`'s INV-32 case.
- **SC-03 — `unmet-unproven`, test/QA lane.** The behaviour is almost certainly right: distinct
  rendered paths per cycle cannot collide. But no test renders two cycles. Closes by: one case that
  renders the `scope` output at `cycle=0` and `cycle=1` and asserts the two paths differ and both
  are grantable — a behavioural assertion instead of a `{{cycle}}`-substring proxy.

## Advisories (not gating, not graded)

- **SC-04's failing-first demonstration is not standing.** `_inv32_mutant_is_discriminating`
  (`test-check-state.py:3078`) feeds the marker mutant only `panel_marker=False` and `readers=missing`
  — SC-07's and SC-17's fixtures. SC-04's own refusing fixture (open `high` finding) is absent from
  that tuple. I discharged the criterion's obligation here, at goal-check, before acceptance, using
  D-13's mandated marker mutant; the result is in the table. Adding `_inv32_plan(finding=open_finding)`
  to that tuple is a one-line change that makes it permanent.
- **SC-04/05/07/13/17 declare `evidence: unit`, but their assertions live in `test-check-state.py`,
  which is in `INTEGRATION_SCRIPTS`** (`run-unit-tests.sh:31`). The tests exist, run and pass; only
  the declared kind and the actual kind disagree. Not a proof failure — recorded so it is not
  rediscovered.

## GOAL versus tasks — two different claims

**Tasks: done.** All 12 plan tasks `status: done`, qa gate PASS, reviewer panel cycle 1 PASS. Not
re-litigated here.

**Goal: not yet met.** The goal is a *standing* panel that reads every drafted plan, withholds on a
`high`, and records an overrule durably. Everything that can be established from disk is established:
the team file resolves, three readers each carry their own question, every write path is granted,
INV-32 refuses a signed plan with no panel record, with an unresolved `high`, with a stale overrule,
and with an unrecorded reader — each demonstrated to redden only because of the region this feature
added. Two things stop it short. One is real and small: the gate is mute about a finding's
disposition, so the record the operator will read afterwards is legible only from `plan.yaml`, not
from the check. The other is structural and known: **nothing in this repository has ever spawned this
panel.** SC-16 says so in its own text, and it is the criterion the c1 fix cycle added precisely
because ten green tasks had graded text on disk. Until the operator runs one live `/harness-plan`,
what has shipped is a correct, well-fixtured *specification of a panel* — and the feature's goal is
that the panel runs.
