# Receipt — harness-pm, plan-product, FEAT-10-software-factory

BLUF: BRIEF.md and plan.yaml are written and both end `pending`. **Cycle 2 (send-back): eleven
tasks, nine decisions, eleven success criteria** — DESIGN.md C-3's CLI contract is now implemented
by a task, and Q3 is ruled. Every gate that can pass with an unsigned brief passes;
`check-state.sh` exits 1 on exactly one violation, the missing signature, which only the user can
clear. Cycle-1 observations were taken at `914b6fd`; cycle-2 re-verification is in §9 below and
was run after every edit.

Filename note: the dispatch asked for `notes/receipt-harness-pm-plan-product.md`.
`check-domain.sh` BLOCKED that write — harness-pm's grants under `notes/` are
`research-*.md` and `uat-*.md` only. Written here instead rather than worked around.

## 1. check-state.sh

```
$ bash .claude/skills/harness/bin/check-state.sh
check-state EXIT:1
  VIOLATION  FEAT-10-software-factory/BRIEF.md is NOT approved — halt that flow and surface to the user.
```

Baseline before this run, same command, same tree: `EXIT:1`, one violation —
`FEAT-10-software-factory has STATE.md but no BRIEF.md`. Writing BRIEF.md replaced that
violation with the pending-signature one. No other violation exists; every remaining line is a
`note`. INV-4 does not fire: `plan.yaml` loads and every task carries `change_type`.

## 2. check-docs.sh

```
$ bash .claude/skills/harness/bin/check-docs.sh
check-docs EXIT:0
checked 62 superseded pattern(s) across 262 file(s).
no stale statements found.
```

File count rose 260 -> 261 when BRIEF.md was written and 261 -> 262 when this receipt was, so
both were scanned. No `<!-- ok-stale -->` marker
was needed: the brief cites effort tickets by number and paraphrases their findings rather than
quoting superseded wording. This was checked by running the checker after writing, not predicted.

## 3. plan.yaml loads under harness_yaml.load_plan

```
$ python3 -c "... harness_yaml.load_plan('.harness/features/FEAT-10-software-factory/plan.yaml') ..."
OK feature=FEAT-10-software-factory tasks=10 decisions=7 approval=pending
EXIT:0
```

## 4. check-plan-routes.py (mandated by harness-spec-driven, required in CI by DEC-183)

```
$ python3 .claude/skills/harness/bin/check-plan-routes.py .harness/features/FEAT-10-software-factory/plan.yaml
check-plan-routes EXIT:0
0 violation(s) across 1 plan(s)
```

One informational line, expected and correct:
`DEVIATION T-08 check-state.sh, test-check-state.py granted to harness-backend-dev, harness-dev-ops
but declared main-session-direct` — that is the DEC-174 carve-out being taken deliberately.

## 5. Every task verify:, run in this tree

All ten were executed by loading `plan.yaml` and running each `verify:` string verbatim.

```
--- T-01  EXIT:1        --- T-06  EXIT:1
--- T-02  EXIT:1        --- T-07  EXIT:1
--- T-03  EXIT:1        --- T-08  EXIT:1
--- T-04  EXIT:1        --- T-09  EXIT:1
--- T-05  EXIT:1        --- T-10  EXIT:1
```

Ten of ten fail before the work exists, which is the point: each one is discriminating. Three
drafts were rejected during this run because they passed at `914b6fd` and would therefore have
proved nothing — the bare `run-unit-tests.sh --kind unit` for T-02 through T-07 (exit 0 today,
`10/10 checks passed`), the bare `--kind integration` for T-08 (exit 0 today, `ALL PASS`), and the
index-diff plus check-docs pair for T-09 (exit 0 today). Each was replaced with a clause naming
the artifact the task creates. The runner output is redirected to a file and grepped rather than
piped, so the runner's own exit status survives.

## 6. Target repositories named in Constraints

```
$ gh repo view mruangutai/harness --json name,visibility,owner
{"name":"harness","owner":{"login":"mruangutai"},"visibility":"PUBLIC"}          EXIT:0

$ gh repo view mruangutai/kaya-ai --json name,visibility,defaultBranchRef
{"defaultBranchRef":{"name":"master"},"isPrivate":true,"name":"kaya-ai","visibility":"PRIVATE"}   EXIT:0
$ gh api repos/mruangutai/kaya-ai/actions/workflows --jq '.total_count,(.workflows[]?|.name)'
2 / CI / web CI

$ gh repo view mruangutai/rental-property-automation --json name,visibility,defaultBranchRef
{"defaultBranchRef":{"name":"main"},"name":"rental-property-automation","visibility":"PRIVATE"}   EXIT:0
```

Excluded and why: `mruangutai/pilot-implentio-app` exists and is personally owned, but it is
Implentio product work, which effort #181 puts out of scope.

Board and token facts:

```
$ gh project list --owner mruangutai
3  Harness   open  PVT_kwHOAAases4BfZ9Z
2  kaya-ai   open  PVT_kwHOAAases4Bc7h3          EXIT:0

$ gh auth status
Token scopes: 'gist', 'project', 'read:org', 'repo', 'workflow'

$ gh api user --jq '{plan: .plan, type: .type}'
{"plan":null,"type":"User"}
```

`gh api user` returns `plan: null` for an account of `type: User`. Why it is null is NOT
established — do not read it as a scope limitation. So which auto-add cap binds (Free 1 /
Pro 5, measured in #183) is unverified. The design uses no auto-add workflow at all (D-03), so
nothing in the plan depends on the answer.

## 7. Routing resolved by running the guard, not by reading the config

```
$ bash .claude/skills/harness/bin/check-domain.sh --resolve <path>
.claude/skills/harness/bin/factory_gh.py      -> harness-backend-dev, harness-dev-ops
.claude/skills/harness/bin/run-unit-tests.sh  -> harness-backend-dev, harness-dev-ops
.claude/skills/harness/bin/check-state.sh     -> harness-backend-dev, harness-dev-ops
.harness/factory/fleet.yaml                   -> NOBODY
docs/harness/DECISIONS.md                     -> harness-documentor
docs/harness/DECISIONS-INDEX.md               -> harness-documentor
.harness/harness.json                         -> harness-dev-ops
```

`.harness/factory/fleet.yaml` resolving to NOBODY is what makes T-01 a declared main-session step
under DEC-179, distinct from T-08's DEC-174 carve-out. `lanes.resolved_at: 914b6fd`.

## 8. Why T-10 is in the plan

`harness-verification-rules` resolves each required kind by two signals, and one of its four
states is **misconfigured** — "`cmd` is null/absent · no test files matched" — which returns
`BLOCKED`, not a pass. `test_kinds.integration.cmd` is non-null and its runner does execute
`test-check-state.py` (that file is in `INTEGRATION_SCRIPTS`), but its `detect` glob
`tests/integration/**` matches zero files here, so the kind resolves as misconfigured and SC-06
could never come back satisfied. T-10 widens `detect` so the runner's result counts. That is the
mechanism, checked against the rule text, not assumed.

## Open, for the user

Two answers are needed before T-01 can be executed, and neither is mine: which repository becomes
the first factory member, and which board is the control plane. T-01's intent instructs the
executor to stop rather than invent either.

**Signing is not blocked on a plan edit.** Verified by grepping plan.yaml for every concrete
value: the only occurrences are T-01's structure template, where each open value is an
angle-bracket placeholder, and T-01's explicitly labelled cross-check facts block. `owner:
mruangutai` is the one fixed value. Every other task refers to the fleet abstractly — "the fleet's
`ready` option", "resolve the repository with repo_entry". So Q1 lands at `repos[].name` and
`repos[].default_branch`; Q2 lands at `board.number` and `board.station_field`; the designer's
three station display words land at `board.stations.{ready,building,review}`. All are written into
`.harness/factory/fleet.yaml` at T-01 execution time, after signature, with no `plan.yaml` edit.

## 9. Cycle 2 — the C-3 gap and the Q3 ruling

**C-3 discharged as D-08 plus a new T-11.** The stream split, the four-value exit vocabulary and
the exception trap are implemented ONCE in a new `factory_cli.py` module rather than restated six
times, because the trap is the load-bearing part and it is only unit-testable in isolation. T-11
specifies `EXIT_*` constants, `message`/`fail`/`refuse`/`nothing_to_do`/`lost_race`, `payload`, and
`run(tool, fn, expected=())`. `expected` is a caller-passed tuple, which is what keeps
`factory_cli` free of any import of `FleetError` or `GhError` and therefore free of a cycle. T-02,
T-04, T-05, T-06 and T-07 now name their `factory_cli.run(...)` wrapper in the intent and depend on
T-11; T-03 is a library with no entry point, so its share is the `GhError` message shape and the
rule that it never writes to stdout.

The trap is tested in BOTH directions, which is the case a wrapper written over `BaseException`
fails: an unexpected `KeyError` exits **2 and not 1**, and a deliberate `sys.exit(1)` still exits
**1 and not 2**. Without the second, `no work available` would become an error.

The grammar is asserted **at the raise site**, not only at the wrapper: T-02 and T-03 now fix the
`FleetError` and `GhError` message shape as `{what failed}: {value} — {what next}`, and their tests
assert every message carries an em dash and a concrete value and contains neither the class name
nor `Traceback`. Wrapping alone would have printed a conformant prefix around a bare class name.

**Q3 ruled: adopt, recorded as D-09.** The decisive evidence is in this plan, not in DESIGN.md —
T-08's INV-24 collects `(factory.repo, issue number)` across all features and flags a collision
naming both, an invariant nobody writes for a case they think cannot arise. T-04 step 5 now derives
`feature:<FEAT>` from the plan's `feature` value, T-04 step 6 fixes the issue body to C-4's order,
and `factory_claim.py` reports `feature` in its payload. The read side is deliberately **tolerant**:
an issue with no `feature:` label claims normally with `feature: null`. `gh-sync.py` creates issues
labelled `harness` and nothing else, they can sit on the same board, and a strict read would fail
them through the very trap C-3 adds.

**One defect fixed while discharging it, worth calling out as an addition.** `ensure_labels` is new
on `factory_gh` in T-03. Primary evidence, `gh-sync.py:355-359`: "LIVE SMOKE FINDING #1: GitHub
rejects an issue create naming a label the repo does not define — new repos ship `bug` but not
`harness`/`chore`." Without it T-04 could not create a single issue, before the feature label was
ever proposed. `gh label create --force` is idempotent and exists at `gh 2.92.0` (`--help`,
verified). Unlike `gh-sync.py`, which swallows the error there because a mirror must never gate a
flow, this one raises `GhError` — that is D-02.

**SC-10 tightened, SC-11 added.** SC-10 previously said "exits non-zero with a loud message", which
an unhandled `GhError` exiting 1 satisfies while violating C-3's central rule. It now requires
**exactly 2 and never 1**, empty stdout, and one stderr line naming an actionable value, and it
extends to an unexpected exception in any entry point. SC-11 carries the other half of C-3: for
each of the five tools with a command line, the whole of stdout parses as one JSON document with
nothing interleaved, and the nothing-to-do and refusal paths leave stdout empty.

**SC-11 forced two contract corrections rather than being written around.** A first draft had
`payload()` fall back to `str(obj)` and had `factory_config --show` print a board line plus a line
per repo — which is not one JSON document, so SC-11 was false by construction for that tool, and
the fallback branch let any tool print arbitrary text to stdout while claiming compliance. Both are
now closed: `payload()` accepts only a dict or a list and raises `TypeError` otherwise, and
`--show` emits one object with `board` and `repos` keys. The single-`json.loads` case is asserted
in all five tools' tests, not three — under-fixturing, not wrong behaviour, is what would have made
SC-11 come back `not_met` after signature.

**T-10 was re-checked and is unchanged, deliberately.** Seven criteria rest on the `unit` kind, so
the same misconfiguration that justifies T-10 for `integration` would have silently blocked them:

```
$ python3 -c "... test_kinds['unit'] ..."
unit        detect= tests/unit/**|**/*.test.*|**/*_test.*|**/test_*.py|.claude/skills/harness/bin/test-*.py
            cmd= run-unit-tests.sh --kind unit        hits: 16
integration detect= tests/integration/**              cmd= run-unit-tests.sh --kind integration   hits: 0
```

`unit` already matches every `bin/test-*.py`, so it needs no widening. Checked rather than assumed.

### Re-verification after the cycle-2 edits

```
$ bash .claude/skills/harness/bin/check-state.sh                       EXIT:1
  VIOLATION  FEAT-10-software-factory/BRIEF.md is NOT approved — halt that flow and surface to the user.
  (the ONLY violation; every other line is a note, unchanged from cycle 1)

$ bash .claude/skills/harness/bin/check-docs.sh                        EXIT:0
  checked 62 superseded pattern(s) across 264 file(s). no stale statements found.

$ python3 -c "... harness_yaml.load_plan(...) ..."                     EXIT:0
  OK feature=FEAT-10-software-factory tasks=11 decisions=9 approval=pending
  ids: T-01 T-11 T-02 T-03 T-04 T-05 T-06 T-07 T-08 T-09 T-10

$ python3 .claude/skills/harness/bin/check-plan-routes.py <plan>       EXIT:0
  0 violation(s) across 1 plan(s); OK T-11 granted to harness-backend-dev, harness-dev-ops;
  the one DEVIATION line is still T-08's DEC-174 carve-out, taken deliberately.
```

T-11 appears second in the file because that is where it executes — T-02 through T-07 depend on it.
Ordering is by `depends_on`, not by id.

Every task `verify:` re-run verbatim by loading the edited plan (the only block that changed is
T-11's, which is new):

```
--- T-01 EXIT:1   --- T-11 EXIT:1   --- T-02 EXIT:1   --- T-03 EXIT:1
--- T-04 EXIT:1   --- T-05 EXIT:1   --- T-06 EXIT:1   --- T-07 EXIT:1
--- T-08 EXIT:1   --- T-09 EXIT:1   --- T-10 EXIT:1
```

Eleven of eleven fail before the work exists, which is the point: each is discriminating. T-11's
fails because `test-factory-cli.py` does not exist, so the `PASS test-factory-cli.py` grep finds
nothing — a bare `run-unit-tests.sh --kind unit` exits 0 today and would have proved nothing.
