# BRIEF — FEAT-14 feature.json with an enforced schema

## Problem

A feature's execution-state file has no enforced key set, so every orchestrator that could not find
a home for a sentence put it there. FEAT-01 carried 10 top-level keys; FEAT-11 carries 32 — all ten
of SPEC §11.3's plus 22 more, on a one-task feature planned and shipped in a single day. Across the
fourteen feature dirs on disk at `06ae963` the union is 75 distinct top-level keys, and on the twelve-feature
union the grilling measured, 41 of them appear nowhere outside a feature directory, so nothing can
read them. The rot is not agent-only: the main session
added three of FEAT-11's keys on 2026-08-10, one of them `operator_rulings_2026_08_10` — a
date-stamped key no schema could declare and no reader will look for, duplicating content already in
`plan.yaml`'s `approval.rulings`. Inside `runs[]` it is worse: entries carry mapping keys like
`"3 must_fix at med"` and `"flips to met"` — prose typed where a field name goes. The cost is paid
by every reader: an orchestrator resuming a feature reads a file where nothing distinguishes state
something depends on from a sentence someone had nowhere else to put, and `cost_usd` survives on 75
run entries a year after cost tracking was removed with zero readers left.

## Goal

A feature's execution state becomes a closed, machine-checked record. It holds exactly the keys
something reads, an agent that invents a key is stopped at the moment it writes one, and the prose
it wanted to record is pointed at the home that already exists for that class of prose. This
reverses ten features of growth in one pass and makes the next ten impossible.

## Requirements

- REQ-01: A feature's execution-state file holds only keys with a demonstrated reader; a key nothing
  reads cannot be present.
- REQ-02: Writing an undeclared key into that file fails loudly — refused before it lands on the
  route that can refuse, reported immediately after the write on the routes that cannot — and the
  failure names the offending key. On no route does it pass silently.
- REQ-03: The failure message redirects rather than merely refusing: it names the destination for
  the class of content that was being written.
- REQ-04: No catch-all prose field is introduced, at the top level or nested.
- REQ-05: Every existing feature's execution state conforms to the closed key set, and what was
  removed is recoverable from a durable receipt rather than lost in a diff.
- REQ-06: If the validation dependency is missing, the system says so loudly and refuses; it never
  degrades to a silent pass.
- REQ-07: Every existing consumer of execution state keeps working across the format change — the
  state check, the plan-route check, the GitHub mirror, and the factory's claim and decompose tools.
- REQ-08: An agent told to instantiate execution state from a template finds one.
- REQ-09: The closed key set, the rejected alternatives and the new dependency are recorded where
  future readers look, so the reversal is not re-litigated as loss.

## Constraints

- **PRECONDITION — the build waits, and only the main session can clear the wait.**
  **FEAT-16-factory-per-repo-board and FEAT-17-guard-boundaries** were both `status: in_progress` at
  `a29ad06` and are writing execution state live. T-04 does not start until BOTH have returned for
  signature, and **no feature may cross from signature into build** between T-04 and T-08. "Idle" is
  not "signed": a signature is the moment a feature starts BUILDING. **This precondition has no owner
  inside the plan** — only the main session sees across features — so the main session is named here
  as its owner. An earlier draft named FEAT-12, FEAT-13 and FEAT-15; **that roster is stale and is not
  the condition.** The condition is the rule, not the names: any flow live when T-04 runs counts.
  **Membership in the migration set is no longer asserted here.** T-04 and T-08 resolve
  `.harness/features/*/feature.yaml` by glob when they run; whichever features that returns are the
  ones converted, and a directory with `runs/` but no feature file is skipped by name, never crashed
  on. **This is the strongest evidence in the feature that the operator's build-waits ruling was
  right: during a single afternoon of planning on 2026-08-10 the corpus mutated twice — FEAT-13 lost
  its `feature.yaml`, `plan.yaml`, `BRIEF.md`, `STATE.md` and `notes/`, leaving only `runs/`, while
  FEAT-15 gained a `feature.yaml`** — so any file list written at plan time is wrong before the build
  begins. **FEAT-15's new file also corroborates the schema before it ships:** written by another
  flow to FEAT-14's discipline, it carries exactly ten top-level keys because `github` and `factory`
  — both optional under this feature's eleven-key set — are legitimately absent, and its `pr` is the
  string `none`, matching the census below. That is evidence the eleven-key schema is workable with
  the two optional blocks omitted, not evidence of a ten-key schema.
  **A flow that STARTS during the window counts too.** The precondition is not a one-time reading of
  three feature directories: no feature may cross from signature into build between T-04 and T-08.
  A running orchestrator converting under a live writer produces a half-migrated file no reader
  understands. FEAT-14's own execution-state file is inside the migration scope, which is the same
  hazard turned inward: this feature's orchestrator must not be mid-write during its own conversion,
  and after T-07 it must not re-create its own file under the old name at a run boundary.
  **For the record, this precondition is run 01's Q5 — the live-writer question — widened from two
  flows to three by the operator's own measurement that found FEAT-15; it is NOT run 01's Q3, the
  baseline/HEAD question the operator already closed by measurement and instructed us not to
  re-raise.**
- **PRECONDITION — the `unit` suite must be green before T-03 lands, and it is.** Measured
  2026-08-10: `run-unit-tests.sh --kind unit` exits **0**, 10 scripts PASS, 0 FAIL, 0 SKIP — run from
  a detached worktree at `96d5d5c` (main HEAD) with a clean tree, because the session's working tree
  carried uncommitted edits to the runner and to three of its test files and a working-tree green
  would not be the green CI evaluates. The `--kind unit` flag itself exists at `96d5d5c`
  (`run-unit-tests.sh:23`), so MF-6 puts a flag on the required `integration` job that the committed
  runner accepts. **This green is not a permanent property**: it is green for the suite as it stands
  *before* this feature's own tests exist, and T-01/T-02 add suites that need a real `jsonschema`.
  Re-check it immediately before T-03 lands; if it has gone red for a pre-existing reason, record
  that as a baseline with its sha exactly as the `check-state.sh` baseline below is recorded, rather
  than landing a required check that is red on arrival.
- **PRECONDITION — `jsonschema` must be importable on the build machine before T-06 lands. It IS,
  and this precondition is DISCHARGED.** `jsonschema` **4.26.0 is installed** to the user
  site-packages, verified 2026-08-11. The earlier reading — no `jsonschema`, `ModuleNotFoundError` at
  `96d5d5c` — is superseded. It still matters why: the fail-closed shape phase deliberately governs
  the main-session-direct tasks **T-04, T-07 and T-08, which write `feature.json` themselves**, so
  once T-06 lands every one of those writes would be DENIED with exit 2 on a machine without the
  package. Re-confirm with `python3 -c "import jsonschema"` before T-06 is dispatched rather than
  trusting this line, because the build machine may not be the machine that was measured. T-03
  installs it in CI only; T-02 declares it in `harness-init` and `CLAUDE.md` only. Neither installs
  it here.
- **All measurements in this brief and its plan were taken at pinned ref `3569a20`** for the reader
  census, and **re-verified at `06ae963` (main HEAD, 2026-08-10) with a CLEAN working tree** for the
  on-disk corpus, the value census and the survivor grep. `bin/` carries no uncommitted change at
  `06ae963` (`git status --porcelain .claude/skills/harness/bin/` is empty), so FEAT-12's in-flight
  edits have landed and the census figures are from committed code, not a dirty tree.
  **`check-plan-routes.py` reports 0 violations across 12 plans, re-measured at `a29ad06`** (the
  earlier reading said five live plans at `06ae963`; the corpus grew). The version checked is against
  FEAT-12's landed version, which differs from `3569a20` by 8 insertions and 8 deletions in that
  file. That is the right version to check against, because the build waits for FEAT-12.
  `.harness/team-config.yaml` is byte-identical between `3569a20` and `06ae963`, so the plan's
  `lanes:` resolution is unaffected by the move.
- **BASELINE — `check-state.sh` already exits 1 before this feature changes anything, and the
  baseline is CAPTURED at build time, not written here.** Two readings, both stated as history and
  neither binding: at `06ae963`, four violations (FEAT-13's BRIEF unapproved, FEAT-14's BRIEF
  unapproved, `FEAT-12: phase is 'build' but notes/handoff-plan.md is missing`, and
  `FEAT-15-domain-product-base: has runs/ but no feature.yaml`); on 2026-08-10, **seven**, of which
  only FEAT-14's unapproved BRIEF survives from the first reading. A list frozen at plan time is
  therefore falsified within a day, and freezing one would fail the build on a condition it was
  written to tolerate. T-04 captures the live violation set to
  `notes/baseline-check-state.txt` **before its first write** — the only honest capture point,
  because from T-06 the gate reads `feature.json` while the corpus is still YAML — and T-08 asserts
  the set has not GROWN and carries no new text against that capture. Every "green check-state" claim
  in this feature is relative to the captured baseline, never absolute. Matching stays
  FEATURE-SPECIFIC, never wildcard: a new unapproved BRIEF appearing during the wait must read as
  NEW. Message text changes at T-06 (`no feature.yaml` becomes `no feature.json`, and INV-18 gains a
  template name), so both sides are keyed on the stem that survives the rename.
- **DEC-174 carve-out is live.** `check-state.sh`, `check-domain.sh`, `bash-write-guard.sh` and
  `validate-digest.py` are edited directly by the main session, never dispatched. This feature
  touches **three** of the four — `check-state.sh`, `check-domain.sh` and `validate-digest.py`, all
  in T-06; `bash-write-guard.sh` is untouched. Signing this does not widen the carve-out: DEC-174
  already names all four. What is new is concentration — three enforcement scripts edited in one
  task, in one build.
- **THE LANDING UNIT IS ONE PULL REQUEST.** Every task lands on one branch and merges as a single
  PR. This is not a preference: `check-state.sh` is red by construction between T-06 and T-08, and
  the four repointed readers are red between T-05 and T-08. On one PR those windows exist only in
  the working tree and the required `integration` context is evaluated once, at the end. Landing
  incrementally would leave that required context red across both windows and the branch could not
  merge.
- JSON over YAML was settled by the operator on 2026-08-09 and reaffirmed at grilling. Not reopened.
- `jsonschema` over a hand-rolled stdlib checker was settled at grilling: a checker and a schema that
  can disagree is the two-copies drift this org keeps finding. Not reopened.
- `state.yaml` is out of scope — it already has a closed key set (`check-state.sh` `CHECKPOINT_KEYS`,
  DEC-154).
- `check-docs.sh` is named in issue #204 step 7. **It no longer exists** — struck under #202. It must
  not be planned.
- There is no `requirements.txt` and no `pyproject.toml` in this repo. The dependency is declared
  where PyYAML is: `harness-init`'s prerequisite gate and the CI workflow.

## The survivor list — the boundary the operator signs

The schema **starts** at SPEC §11.3's ten keys (`docs/harness/SPEC.md:1742`) with
`additionalProperties: false`, and the burden of proof is on keeping anything beyond them. The
census (`notes/research-FEAT-14-reader-census.md`) returns:

**(a) keys with a CODE reader** — `key -> file:line -> the expression that consumes it`:

- `runs[].id|squad|verdict` -> `bin/check-state.sh:184-190` -> `entry.get("id"/"squad"/"verdict")`
- `review_sha` -> `bin/check-state.sh:195` -> `val("review_sha")` against `PLACEHOLDER_UNSET`
- `cycles_used` -> `bin/check-state.sh:203` -> `val("cycles_used")` against the FAIL-run count
- `max_total_runs` -> `bin/check-state.sh:249` -> `_as_budget(val("max_total_runs"))`
- `phase` -> `bin/check-state.sh:450` -> `str(_doc.get("phase",""))` — **this reader is DELETED, not
  repointed**: `phase` collapses into `status` and T-12 rebuilds INV-17 around the six values
- `status` -> `bin/check-plan-routes.py:427` -> `str(doc.get("status","")).split()[0] in SHIPPED_STATUSES`
- `github` -> `bin/gh-sync.py:247-260` and `bin/check-state.sh:729-737` -> `load_recorded`'s
  `milestone/parent/parent_origin/attached/issues`; INV-21's `gblk.get("issues"/"parent")`
- `factory` -> `bin/factory_decompose.py:94-138`, `bin/factory_claim.py:116-131`,
  `bin/check-state.sh:758-798` -> `doc.get("factory")` then `repo/parent/parent_origin/issues/items/edges`

**(b) keys kept only because a SKILL.md/SPEC.md line instructs an agent to consume them: EMPTY.**
Every prose site naming a field names one of the ten (`harness/SKILL.md:15,23,26,61,271`,
`harness-orchestrator.md:52`, `commands/harness.md:18`). Nothing instructs any agent to read
`mission`, `effort`, `briefing`, `tasks`, `baseline`, `gate_status`, `receipts` or `posture`. The
grilling listed those as "likely genuine"; the check does not support it.

**So the boundary does not fork.** Code-readers and prose-readers give the same answer:
**eleven top-level keys** — the ten, minus `phase`, plus `github` and `factory`. `factory` is read and written by
the factory tooling and appears in zero feature files today; omitting it would invalidate the
factory's own writes.

**Recorded, not acted on:** four of the ten — `feature_id`, `branch`, `pr`, `max_total_cycles` —
have neither a code reader nor a prose consumer at `3569a20`. They survive because the ruling starts
at the ten and puts the burden of proof only on keys beyond them. Written down so a later reader does
not mistake their presence for evidence that something reads them.

## Required versus merely allowed — the verdict

`additionalProperties: false` says nothing about presence, so this brief settles it:

**Required: eight.** `feature_id`, `branch`, `pr`, `status`, `review_sha`, `cycles_used`,
`max_total_cycles`, `runs`. **`phase` is not among them, because `phase` no longer exists** — it
collapsed into `status` (see "One field, six values" below).
**Optional: three.** `max_total_runs` (SPEC §11.3 says omit to inherit `harness.json`), `github`
(only present once a feature is mirrored), `factory` (only once it is decomposed).

Measured at `a29ad06` across all **17** files on disk: every one of the eight required keys is
present on every file, and `max_total_runs` is the only optional key ever absent. **The migration
backfills nothing.** An earlier draft priced a `phase` backfill onto FEAT-01 and FEAT-02; with
`phase` deleted that backfill does not happen and its analysis is void.

**Nested blocks are closed too**, which is where the worst rot is. `runs[]` items close to
`id|squad|verdict` — 75 entries carry a dead `cost_usd`, 14 carry an unread `note`, and several
carry prose as a key. `github` closes to the five keys `gh-sync.py` reads and writes; the
`closed`/`open`/`filed`/`perf_row_10`/`q18_ruled` sub-keys found on disk are agent inventions with
no reader. `factory` closes to the six keys `factory_decompose.py` normalizes.

## Values, not just keys — the migration is not key-dropping alone

Presence was not enough to check. A value census — **re-run over all 17 files at `a29ad06`** with
`harness_yaml.load_file`, the same loader T-04 uses, not the more permissive `yaml.safe_load` (the
two differ on duplicate top-level keys; all loaded clean under both) — plus the operator's
2026-08-11 ruling, settle the value side of the migration:

- **One field, six values — `phase` and `status` collapse into `status`.** Ruled by the operator on
  2026-08-11. The values are the GitHub board's own column names, capitalized exactly as the board
  spells them: `Backlog | Plan | Ready | Building | Review | Done`. This is a **replacement, not a
  mapping layer** — the old values are read once, by the migration, and no old-to-new table survives
  anywhere in the code, the schema, or a fixture. Both GitHub boards already carry the six options,
  applied and verified 2026-08-11; T-04 opens by **reading** the boards to confirm the six exist and
  mutates neither.
  **What each column means:** `Backlog` filed, not yet planned · `Plan` BRIEF and `plan.yaml` being
  authored, not yet signed · `Ready` plan signed, waiting to be dispatched · `Building` build running
  · `Review` validating, **or waiting on the operator** · `Done` merged and closed, **or abandoned**.
  **The cost is named and accepted, not free:** `Review` cannot distinguish a running review panel
  from waiting on the operator, and `Done` cannot distinguish shipped from given up on. One record on
  disk is affected by the second — FEAT-01.
  **The old vocabulary, measured at `a29ad06` across all 17 files, is the migration's input and
  nothing else:** `awaiting_user` 5, `shipped` 4, `in_progress` 3, `in_review` 2, `abandoned` 1,
  `shipping` 1, `complete` 1. The old and new vocabularies share **not a single value**, which is
  what makes this a replacement rather than a normalization — all 17 files change.
  **`blocked` is NOT in the vocabulary.** An earlier draft kept it as legal-but-unused; the six
  columns have no Blocked column, the tree carries the value **zero** times (verified at `a29ad06`),
  and a blocked feature is waiting on the operator, which is `Review`. That is stated explicitly here
  rather than left implied.
- **Casing is load-bearing, not cosmetic.** The corpus is uniformly lowercase `snake_case` today.
  `check-plan-routes.py` compares `str(doc.get("status","")).split()` token-for-token, so casing
  flows straight into that comparison and the comparison is **case sensitive**. No lowercase alias is
  accepted: a normalizing step would itself be the mapping layer the ruling forbids, and the value on
  the board and the value on disk must be byte-identical or the replacement has not happened.
- **`pr` is the string `none` in every file**, never an integer. It has no reader anywhere.
  **Verdict: `pr` is `integer or null`** and the migration rewrites `none` to `null` — JSON has a
  native null and the placeholder string was a YAML-era workaround.
- `branch` (`none` in 3) and `review_sha` (`none` in 3) stay `type: string` with the literal `none`
  permitted: `check-state.sh` INV-6 already treats `none` as unset via `PLACEHOLDER_UNSET`, and
  changing those two to null would alter a gate script's input for no gain.
- **`runs[]` required keys — censused, and they pass.** All **150** run entries across the corpus at
  `06ae963` carry all three of `id`, `squad`, `verdict`; zero entries are missing any, and zero
  entries are non-mappings. So `id|squad|verdict` can be `required` with no backfill.

**Two live gates change what they examine, and each gets a task rather than a note.** This is the
class of defect this project keeps finding — a required gate that silently starts examining
something else — so neither is left to CI to discover.

- **`check-plan-routes.py`'s finished-feature skip is `SHIPPED_STATUSES = ("shipped", "abandoned")`.**
  Neither value will exist. Its own documented rule is that a feature it cannot classify is **checked
  rather than skipped**, so left alone every finished feature is route-checked forever. **T-11**
  repoints it at `Done`, which also absorbs abandoned — the behaviour that tuple already had.
  Measured: at `a29ad06` the checker reports **0 violations across 12 plans**; with the tuple emptied
  — the exact state T-04 leaves it in — it reports **35 violations across 16 plans**. That window
  opens at T-04 and closes at T-11, inside one PR.
- **`check-state.sh`'s INV-17 goes DARK if `phase` is simply deleted.** `PHASE_ORDER` is read at
  line 437, `phase` at 450, and line 451 is `if _phase not in PHASE_ORDER: continue`. With `phase`
  gone, `_phase` is `""` on all 17 features, never in `PHASE_ORDER`, so the loop `continue`s on every
  one: **the invariant stops firing entirely and nothing reddens.** A gate that examines nothing
  reports no violations and passes every check anyone would run. **T-12** rebuilds it around the six
  values, and its criterion asserts a violation is **raised**, never that the script exits clean.
  **The handoff filenames stay lowercase literals** (`plan`, `build`, `validate`) rather than being
  derived from the status values: deriving them yields `notes/handoff-Plan.md` against a
  `notes/handoff-plan.md` on disk, which **passes on this machine's case-insensitive filesystem and
  fails on Linux CI** — the invariant would look healthy locally and go dark on the machine that
  gates the merge. The residual loss is stated rather than hidden: `validate` and `ship` both fold
  into `Review`, so the validate seam is demanded at the `Done` boundary instead. One seam moves
  later; none is dropped.

**Out of scope, decided rather than overlooked: `validate-digest.py`'s orchestrator `status` enum**
(`in_progress, in_review, shipped, blocked, awaiting_user`). It is a **return contract for one run**,
not a feature's lifecycle position — different objects, different lifetimes. The discriminating fact:
that enum carries `blocked` and the six columns have no `Blocked`, so collapsing it would either
invent a seventh column nobody authorized or delete a token the `SubagentStop` hook routes on. It is
raised as a non-blocking open question at signature.

Without this section the migration would drop keys correctly and still fail its own validator — on
**all 17** files, on `status` alone.

## Where the prose goes instead — no new field

Settled at grilling; the schema's rejection message must carry it:

| What was being recorded | Destination |
|---|---|
| An operator ruling | that feature's `plan.yaml` `approval.rulings` |
| Run narrative, findings, corrections | that run's digest |
| Current state, open questions | `STATE.md` |
| Measurements, research, receipts | `notes/` |

## The enforcement point — the feature's real decision

Three candidates, and "loud failure" means something different in each:

| Where | What "loud" means there | Verdict |
|---|---|---|
| `bash-write-guard.sh` (PreToolUse) | the write is denied before it lands | **rejected** — it guards Bash-route writes, not the Write tool the orchestrator actually uses, and DEC-171 am.1's fail-closed shape would put schema logic behind a bootstrap escape |
| `check-state.sh` | a pre-commit sweep reddens after the bad write is already on disk | **rejected as the primary point** — detection after the fact, and it is fully inside the DEC-174 carve-out |
| `check-domain.sh`'s existing write-payload path + a new `bin/validate-feature-json.py` in the required `integration` CI job | the write is denied at the moment it is attempted, and a bypass is caught red on the PR | **recommended** |

The recommendation exploits something already built: `check-domain.sh:506` (`SWEEP_GLOBS`) and
`:636` already inspect `.harness/features/*/feature.yaml` **write payloads** for the 200-line budget.
One validator implementation lives in `bin/feature_schema.py`, an importable module in the house's
existing shape (`harness_yaml.py`, `gh_issues.py`, `factory_*.py` are modules; `gh-sync.py`,
`check-plan-routes.py` are CLIs), with a thin `bin/validate-feature-json.py` wrapper for the CLI
callers — CI, the migration tasks and the corpus sweep. `check-domain.sh` already exports
`PYTHONPATH` and imports `harness_yaml` in-process, so the carve-out edit is an **import and a
call**, not a subprocess: no per-write interpreter launch (the 104.7 ms `check-domain.sh:92`
measured and T-13 removed), no temporary file, and the unavailable-checker case is an ordinary
`except ImportError` branch rather than a subprocess that failed to launch. Three enforcement layers
is scope creep; the operator signs one boundary.

**Fail-closed here has NO bootstrap escape, and that is deliberate rather than an omission.**
`check-domain.sh`'s bootstrap grant (`harness_yaml.require_or_bootstrap`) is reached only inside
`if _run_domain:` — a governed `harness-*` agent, PRE mode. The shape phase, which is where this
check lives, runs for **every** writer including the main session (the no-`agent_type` carve-out is a
flag, `_governed`, not an exit — it used to be a bare `sys.exit(0)` and that silently disabled the
shape gate). So the schema check governs the migration's own main-session writes, with no escape
available to them. No escape is needed: the remedy for a checkout missing the dependency is
`pip install jsonschema`, a Bash command, which no gate denies — unlike the missing-parser case,
where the escape exists because the gate cannot read its own manifest without it. The check also
depends on **stdlib `json` plus `jsonschema` only, never PyYAML**, so the user-ruled `_no_parser`
fail-open on the `state.yaml` branch does not apply to it and must not be copied onto it.

**What "at the moment of the write" can actually mean, per route.** `check-domain.sh` already runs
in two modes (its own header, measured under issue #132): `PreToolUse` on the **Write** route
measures the payload and BLOCKS with exit 2 — the only mode that can prevent; `PostToolUse` on
**Write, Edit and Bash** reads what landed on disk and exits 2, whose stderr reaches the agent —
detection, not prevention, because an Edit payload carries no whole-file content and arbitrary shell
cannot be predicted. Schema validation inherits exactly that split. So an orchestrator using Write
is refused before the bad key lands; one using Edit or `sed -i` is told immediately after, before
the next reader loads the file. The CI job is the backstop for a session where the hook is not
registered at all. This brief does not promise pre-write denial on every route, because the
mechanism cannot give it.

**Two budget consequences of JSON**, both inside this feature: the 20-comment-line half of the
`feature.yaml` budget becomes unreachable and is struck, and the 200-line half needs raising to 300
— reduced to eleven keys, FEAT-10 dumps to ~173 JSON lines at 32 runs (the 173 was measured on the
twelve-key form, before `phase` was dropped; one key is one line) and JSON costs ~5 lines per run,
so it breaches at ~38.

## The missing template — fixed by both

`check-state.sh:487` (INV-18) and `.claude/skills/harness/SKILL.md:23` both instruct instantiation
from a template that does not exist. This ships `templates/feature.json` **and** rewords both
instructions to name the file, because shipping the template alone leaves two instructions whose
target a reader still has to guess at.

## Citations are preserved; instructions are renamed — the rule, and why it is one rule

The survivor grep run at `06ae963` returns **23 files under `.claude`**, 5 under `docs/harness`, none
under `.github`, and one each in `harness.json` and `team-config.yaml`. Three of the 23 sit in no
task's `files:` list, and they do not all deserve the same treatment. The rule, applied uniformly:

> **A file whose job is to RECORD WHY something exists keeps its citations verbatim. A file whose job
> is to INSTRUCT gets renamed, because a reader acts on an instruction.**

| File | Job | Disposition |
|---|---|---|
| `bin/validate-digest.py` (1 occurrence) | a present-tense comment saying where state lives | **rename** — it becomes false at T-08. **DEC-174 carve-out file**, so main-session-direct |
| `bin/test-validate-digest.py` (2) | synthetic `artifact:` fixture paths | **rename** — they are test inputs, not a record of anything that happened |
| `bin/test-harness-yaml-corpus.py` (4) | the docstring justifying the gate, citing `FEAT-03/feature.yaml:97`, `FEAT-04/feature.yaml:77`, `FEAT-05/feature.yaml:55` and a dated claim about 2026-08-03 | **preserve, and mark historical** |

Renaming the third would assert that files existed under a name they never had on 2026-08-03, and
that the evidence for the gate is retrievable at paths `git show` will not produce. PRINCIPLES rule
15 forbids exactly that. The record is left standing and a marker line is added so a reader is not
misled into thinking the names are current.

**How this differs from `harness-spec-driven/SKILL.md` (T-07), which IS renamed — and the honest cost.**
It does not differ in *kind*: that anecdote is also a citation of a past incident on FEAT-03. It
differs in *job*. `harness-spec-driven/SKILL.md` is a rule preloaded into every planning spawn; its
`feature.yaml:41` example is scaffolding for the lesson "cite the field, never the line", and the
lesson is identical with either filename. Its second occurrence — "Write `feature.yaml
github.parent` instead" — is a forward instruction that would send every future planner to a
nonexistent file if left alone. Splitting that one file's two occurrences would give it a third
treatment, produce a sentence that contradicts itself mid-line, and add a second allow-list entry.
**The cost is stated plainly: renaming the SKILL.md anecdote does make its `feature.yaml:41` cite a
file state that never existed under that name.** It is accepted because nothing about a failure is
made to look better — rule 15's target — and because the alternative buys accuracy in a teaching
example at the price of an incoherent instruction. `test-harness-yaml-corpus.py` gets the opposite
call because its citations ARE the evidence, not an illustration of it.

## Success Criteria

- SC-01: Every feature's execution-state file on disk validates against the schema, and no file
  carries a key outside the eleven, and no file carries a `phase` key at all.
  verify: automated        evidence: unit
- SC-02: A file carrying an undeclared top-level key, an undeclared `runs[]` item key, or an
  undeclared `github`/`factory` sub-key is rejected — each of the three nesting levels has its own
  failing fixture, and each fixture's rejection message names the offending key.
  verify: automated        evidence: unit
- SC-03: A file missing any one of the eight required keys is rejected, and a file missing only
  `max_total_runs`, `github` or `factory` is accepted — one fixture per key, eleven fixtures, not a
  count comparison. A file carrying `phase` alongside all eight required keys is rejected as an
  undeclared key.
  verify: automated        evidence: unit
- SC-04: On the **Write** route, a payload carrying an invented key on a feature's execution-state
  path is DENIED before it lands — demonstrated by running `check-domain.sh` in `PreToolUse` mode on
  that payload and reading exit 2, not by reading the source.
  verify: automated        evidence: integration
- SC-05: On the **Edit** and **Bash** routes, where no payload can be inspected, the same invented
  key on disk produces exit 2 from the `PostToolUse` sweep with the key named — demonstrated by
  writing the bad file and running the sweep, and asserting it is not exit 0.
  verify: automated        evidence: integration
- SC-06: Every migrated file carries a `status` that is one of `Backlog | Plan | Ready | Building |
  Review | Done` — **byte-identical, case included** — and a `pr` that is an integer or null. No file
  retains any old value (`in_progress`, `in_review`, `awaiting_user`, `shipped`, `abandoned`,
  `shipping`, `complete`), no file retains a `phase` key, and no file retains the string `none` as
  `pr`. Asserted **per file against the migration table**, never as a count, and the lowercase
  spelling of a legal value is asserted REJECTED.
  verify: automated        evidence: unit
- SC-07: With `jsonschema` uninstallable in the environment, the validator exits **exactly 3** — the
  checker-could-not-run code, distinct from 1, which is a verdict about a file — with a message
  naming the missing package and the install command; it never exits 0 and never prints a skip.
  Demonstrated by running it with the import forced to fail.
  verify: automated        evidence: unit
- SC-08: `check-state.sh` over the converted corpus reports **no violation outside the baseline
  captured by T-04 before the migration's first write** — the count may only fall, never rise, and no
  new violation text appears. It is NOT "exits 0": it exits 1 today for reasons this feature does not cause.
  Additionally its INV-18, INV-21, INV-22, INV-23 and factory invariants still fire on a
  deliberately broken fixture, and INV-17 stays quiet on FEAT-01 and FEAT-02 via T-12's named
  two-element exemption set — the format change neither silently disabled a check nor invented a
  violation, and INV-17 stays quiet on FEAT-15 via T-12's **plan-keyed** exemption — all five of its
  tasks are `execution_mode: main-session-direct` under DEC-174, so no seam was crossed and no note
  was owed — while **emitting an exemption note naming it**, so the silence is proven granted rather
  than assumed. The exempt set the check asserts against is **computed from the plans, never a
  hardcoded roster** — the format change neither silently disabled a check nor invented a
  violation. (INV-17's own firing is SC-18's, which is stronger than "still fires".)
  verify: automated        evidence: integration
- SC-09: `gh-sync.py`, `factory_claim.py`, `factory_decompose.py` and `check-plan-routes.py` each
  read and (where they write) round-trip the converted format, proven by their own existing suites
  passing plus a new case per tool reading a `feature.json` fixture.
  verify: automated        evidence: unit
- SC-10: Every key dropped and every value normalized in every feature is recorded in that feature's
  `notes/` receipt with its original value, and every feature file present at build time has a
  receipt beside it with none left over. Spot-checked by an
  operator against the feature that lost the most keys (FEAT-11, 20 keys).
  verify: inspection
- SC-11: No `notes:` field, and no other free-text catch-all, exists at any level of the schema;
  the rejection message for an undeclared key names a destination from the redirection table.
  verify: inspection
- SC-12: `.claude/skills/harness/templates/feature.json` exists and itself validates against the
  schema, and both instructions that point at a template (`check-state.sh` INV-18 message and
  `harness/SKILL.md:23`) name it by filename.
  verify: automated        evidence: unit
- SC-13: No reference to `feature.yaml` survives anywhere the harness reads or **instructs** from —
  `bin/`, `.github/`, `.claude/skills/`, `.claude/agents/`, `.claude/commands/`, `templates/`,
  `team-config.yaml`, `harness.json`, `docs/harness/` — with exactly two carve-outs, both of which
  RECORD rather than instruct: decision records in `docs/harness/DECISIONS*` describing this change,
  and the module docstring of `bin/test-harness-yaml-corpus.py`, which cites three files by
  `path:line` as they stood on 2026-08-03 (see "Citations are preserved" below). The second carve-out
  is pinned to an exact occurrence count, so a NEW `feature.yaml` reference in that file still fails.
  verify: automated        evidence: integration
- SC-14: THREE decisions each have their own entry in `docs/harness/DECISIONS.md` — the new
  `jsonschema` dependency, the closed key set, and the collapse of `phase` and `status` into one
  board-column vocabulary — and `DECISIONS-INDEX.md` matches
  `gen-decisions-index.py --stdout` byte for byte — the index row is generated, never hand-written.
  verify: automated        evidence: integration
- SC-15: The operator, reading the eleven-key file for a mature feature, can tell within one screen
  what state the feature is in — the file reads as execution state, not as a record of what agents
  had on their minds.
  verify: uat
- SC-16: **A checker that cannot run DENIES.** With the schema checker unavailable in the
  environment, an otherwise-VALID execution-state payload on the Write route yields **exit 2** from
  `check-domain.sh` in `PreToolUse` mode — not exit 1, which is non-blocking and would let the write
  land — and the message names the **real target path**, never a temporary file. Demonstrated by
  running the hook with the import forced to fail and reading the exit code, not by reading the
  source. A sweep over many files emits the unavailability message once, not once per file.
  verify: automated        evidence: integration
- SC-17: `check-plan-routes.py` skips a feature because its `status` is `Done` and for no other
  reason — the literals `shipped` and `abandoned` appear nowhere in the file — and over the migrated
  corpus it reports **0 violations across a plan count that is at least 1**. The expected count is
  **10**: of the 17 features, seven are `Done` (FEAT-01, FEAT-02, FEAT-03, FEAT-04, FEAT-05, FEAT-10
  and FEAT-15 — signed plan, PR #263 merged),
  FEAT-01 carries no plan file, so six of the 16 plan files are skipped. FEAT-09 stays in the
  checked set (`shipping` -> `Review`). A plan count of 0 is a FAILURE, not a clean run: CI asserts
  the count is non-zero precisely because a checker that examines nothing passes everything. The six
  board values and the lowercase `done` are each asserted for skip-or-check individually, not by a
  count.
  verify: automated        evidence: unit
- SC-18: **INV-17 still FIRES.** A constructed feature at `status: Review` with
  `notes/handoff-build.md` absent RAISES a violation naming `handoff-build`, and a feature at
  `status: Done` outside the exemption set missing `notes/handoff-validate.md` RAISES one too. In the
  opposite direction, FEAT-01 and FEAT-02 — `Done`, zero handoff notes, in the named exemption set —
  raise NO handoff violation, and a feature at `status: Plan` with no notes raises nothing.
  **The plan-keyed exemption is asserted in all three directions, from seven cases in total:**
  (a) a `Done` feature whose `plan.yaml` has a non-empty `tasks:` list in which **every** task is
  `execution_mode: main-session-direct`, holding no handoff notes, raises NO handoff violation **and
  emits an exemption note naming it and the suppressed stems** — a silent exemption fails this
  criterion; (b) the squad-built `Done` feature missing `handoff-validate.md` above still RAISES;
  (c) a `Done` feature whose plan carries **no `execution_mode` key at all**, and one whose `tasks:`
  list is **empty or absent**, each RAISE — the exemption is keyed on the plan's declared modes,
  never on the notes' absence, and "every task is main-session-direct" must not pass vacuously over
  an empty list. **No assertion here is "check-state.sh exits 0"** — a dead
  invariant produces exactly that exit, so a clean exit is not evidence here. Additionally
  `check-state.sh`'s **executable code** — comments stripped — contains no `PHASE_ORDER`, no read of
  a `phase` key, and builds no `handoff-<Capitalized>.md` path, which would pass on a
  case-insensitive filesystem and fail on Linux CI. **Comments may name all three**: the task
  requires a comment recording what replaced `PHASE_ORDER` and why the stems are decoupled, so a
  check over the raw file would forbid the very sentence it depends on.
  verify: automated        evidence: integration

## Verification gaps

- `functional`, `component`, `ui`, `eval` and `typecheck` have `cmd: null` in
  `.harness/harness.json` — no runner. **No SC above rests on any of them**, and this feature
  touches none of those surfaces (no UI, no LLM behaviour, no database path). No gap applies.
- New test files must be registered in `run-unit-tests.sh`'s `UNIT_SCRIPTS` array, not
  `INTEGRATION_SCRIPTS`: the `integration` kind's `detect` globs name only `test-check-state.py` and
  `test-factory-integration.py`, so a new file registered there would match no detect glob and the
  qa gate would see it as covering nothing. SC-04, SC-05, SC-08, SC-13, SC-14, SC-16 and SC-18 name
  `integration` because the command that proves them is `run-unit-tests.sh --kind integration`,
  which is what the required CI job runs; their assertions live in `test-check-state.py` and
  `test-check-domain.py`, both listed in the runner's `INTEGRATION_SCRIPTS`.
- **The required CI job does not run the new unit suite as it stands, and T-03 fixes that.**
  `tests.yml`'s `integration` job runs `--kind integration` only, so SC-01, SC-02, SC-03, SC-06,
  SC-07, SC-09, SC-12 and SC-17 — every criterion resting on the unit kind — would have
  no mechanical runner on the one context branch protection requires. That is DEC-183's own failure
  shape. T-03 adds a unit-suite step to the SAME `integration` job (never a new job: the required
  context is that job's id) and amends the standing comment in `tests.yml` that says the unit kind
  "would have caught none of the defects that motivated this" — true when written, false once
  REQ-06's proof lives there.
- **`check-state.sh` is red between T-06 and T-08 by construction** — the globs name `feature.json`
  while the corpus is still `feature.yaml`, so INV-18 fires for every feature still on YAML. That
  window is accepted and stated in T-06; the branch is not committed until T-08 returns
  `check-state.sh` to its captured pre-migration baseline. Nothing else in this feature relies on `check-state.sh` in between.

## Approval

status: approved
approved-by: operator
date: 2026-08-11
