# PLAN — FEAT-08 Remove cost tracking

## Anchors — re-verified, not inherited

Every line number below was re-read at **`ae2443d`** (`git rev-parse --short HEAD`), the same SHA the
dispatch cites. Re-verified unchanged: `run-unit-tests.sh:6` and its drift detector `:9-24`;
`check-state.sh:248`, `:258-271`, `:302`, `:337-350` (`cost` at `:344`), `:357`, `:361`, `:369-373`,
`:401`; `validate-digest.py:171-180` (`cost_usd` in `SCHEMAS["orchestrator"]` at `:177`) and `:661`;
`.harness/harness.json:136`, `:137`, `:232-240`; `templates/harness.json:138`, `:139`, `:234-242`;
`DECISIONS-INDEX.md:168`; `render-brief.py:11`. Re-measured: 67 of 67 run `state.yaml` carry `cost:`;
89 `cost_usd`/`max_cost_usd` lines across 7 `feature.yaml`; the sweep grep returns 18 files.

**One divergence from the dispatch, and it changes a task.** The dispatch states that whatever marks
the DEC-148 row "lives in `DECISIONS.md` and is regenerated — never hand-edited into the index." That
is true of the `— SUPERSEDED BY DEC-NN` clause and **false of the ruling prose**, which is the half
carrying the wrong claim. `gen-decisions-index.py`'s own docstring (`:8-10`): "Everything left of
' :: ' on a row is generated; everything right of it is hand-written and preserved verbatim across
regeneration" — and the code confirms it: `prose, had_ok_stale =
strip_trailing_clauses(existing_rows[key])` (`:319`) takes the ruling from the **existing index row**,
not from `DECISIONS.md`. A plan that routed this fix through `DECISIONS.md` alone would leave
`:168`'s false sentence verbatim while the generator diff exited 0 — the requirement failing
silently. D-05 and T-09 are written to the measured behaviour.

## Lanes — resolved here, not discovered at build time

Resolved against `.harness/team-config.yaml` at `ae2443d`, with CLAUDE.md's DEC-174 policy overlay
sitting **on top of** the grants (a grant does not authorise a team run for a carve-out file).

| Surface | Lane | Authority |
|---|---|---|
| `check-state.sh`, `validate-digest.py` and their tests | **main-session-direct** (DEC-174 carve-out) | `CLAUDE.md` — overrides the grants below |
| `cost-report.py`, `test-cost-report.py`, `run-unit-tests.sh`, both `harness.json` | `harness-backend-dev` / `harness-dev-ops` | `team-config.yaml:155`, `:197` |
| `docs/**` and `.harness/README.md` | `harness-documentor` | `team-config.yaml:116`, `:118` |
| `.claude/agents/*.md`, `.claude/skills/harness/SKILL.md`, `.claude/skills/harness-team/SKILL.md`, `.claude/skills/harness/teams/*.yaml` | **main-session-direct** (declared step) | granted to nobody; `.claude/agents/**` deliberately unowned (`team-config.yaml:35-40`) |

## Segments — dependency-ordered

| Segment | Tasks | Why this boundary |
|---|---|---|
| **S1 — loosen the gates** | T-01, T-02 | Both are one-directional hazards. Loosening first is free; removing a producer first is a hard, self-inflicted outage (D-01, D-02) |
| **S2 — remove the machinery** | T-03, T-04 | Both depend on T-02 and on nothing else |
| **S3 — the unowned rule surfaces** | T-05, T-06, T-07, T-08 | All depend on T-01 and on **nothing else**, so they share a segment with the riskiest of them (T-06, D-08). A failure in T-06 wastes none of T-05/T-07/T-08 |
| **S4 — the record** | T-09, T-10, T-11, T-12 | Docs describe the shipped state, so they run last |

## Decisions

- D-01: **`cost_usd` is REMOVED from `SCHEMAS["orchestrator"]` rather than kept with a declared
  literal, and the removal lands in S1 — before any rule surface stops producing it.** Two parts.
  *Ordering:* probed at `ae2443d`, an orchestrator payload omitting `cost_usd` is rejected
  `VERDICT: BLOCKED (contract violation) — missing 'cost_usd'`, exit 1; a payload carrying an unknown
  extra key returns `digest ok`, exit 0. The hazard is one-directional. If T-05/T-06 stopped telling
  the orchestrator to emit the field while the schema still required it, **every orchestrator return
  in the repo would be BLOCKED by the live `SubagentStop` hook — including this feature's own build
  and validate runs.** *Removal over a literal:* the dispatch offers a declared literal such as
  `not-metered`, and issue #58 lists the schema field under "surfaces to remove". Goal constraint 1
  says no rule surface asks an agent to carry a cost figure; a REQUIRED field named `cost_usd` is
  exactly such a surface, and `not-metered` would be a permanent piece of vestigial ceremony every
  orchestrator must type forever. The measured extra-key tolerance is what makes removal safe: an
  in-flight return still carrying `cost_usd: "12.83"` is **ignored, not rejected**, so there is no
  transition window and no literal is needed. Trade-off: an orchestrator running from a stale
  cached rule surface will keep emitting a field nobody reads, silently — accepted, because the
  alternative is rejecting it loudly for a value it was told to produce.
- D-02: **`check-state.sh` is loosened in S1, before the config strip (T-04) and before the meter
  deletion (T-03) — and THREE checks come out, not one.** The dispatch names INV-11 at `:369-373`.
  Re-reading the file found a second, unnamed hazard of the same shape: `:258-259` is
  `bad.append("harness.json has no cost_model.rates — runs cannot be costed…")`, a **hard violation**,
  not a warning. Deleting the `cost_model` block from `.harness/harness.json` (T-04) while that check
  lives makes the repo a check-state violation immediately, and `check-state.sh` gates `/harness`
  entry. The third is `:261-271`, the `verified_on` staleness `warn.append`, which reads the same
  deleted block. All three come out in T-02, ahead of both. Trade-off: T-02 leaves a short window in
  which nothing enforces that a completed run was metered — harmless, because the whole point is that
  nothing should.
- D-03: **`cost` STAYS in `check-state.sh`'s `CHECKPOINT_KEYS` (`:344`) — allowed, never required.**
  Forced by the ruling that historical figures are left in place, not chosen. Re-measured at
  `ae2443d`: all 67 run `state.yaml` files carry a `cost:` block, and `:401` flags any top-level key
  not in that set, so removing the entry converts 67 historical runs into 67 violations in one edit.
  Recorded as a decision because it is exactly the tidy-up a future scan will propose: the entry looks
  dead after this feature and is not. T-02 adds a comment at `:344` saying so.
- D-04: **`warn_at_fraction` is removed with the budgets block; it is not an open question.**
  Re-measured at `ae2443d`, `grep -rn warn_at_fraction` over `.claude/`, `docs/` and both configs
  returns exactly three hits: `cost-report.py:406` (its only consumer), `templates/harness.json:238`,
  `.harness/harness.json:236`. It has **no referent against `max_total_cycles`** — nothing reads it in
  a cycle path. With its only consumer deleted it is a config key no code reads, which is the
  orphaned-config shape REQ-09 exists to prevent. Trade-off: if a future cycle-warning threshold is
  wanted, it must be re-added deliberately rather than inherited by accident — which is the point.
- D-05: **The DEC-148 index row is fixed by editing the RULING PROSE in `DECISIONS-INDEX.md`
  directly, and the new decision does NOT declare `**Supersedes DEC-148**`.** Rationale, measured
  rather than assumed (see `## Anchors`): the ruling prose right of ` :: ` is hand-written and
  preserved verbatim by the generator, so an index edit survives regeneration and a `DECISIONS.md`
  supersession marker would **not** remove the false sentence. Against the marker specifically:
  DEC-148 made two changes and only one dies here — its relay half was superseded by DEC-159
  independently of this feature, and DEC-159's body carries no supersession declaration, so a blanket
  `— SUPERSEDED BY DEC-178` would claim this feature killed both halves and erase the DEC-159 lineage.
  The rewritten prose therefore keeps the halves distinguishable in one sentence and names DEC-159 for
  the relay half and DEC-178 for the watchdog. **The trap T-09 must avoid:** `strip_trailing_clauses`
  (`gen-decisions-index.py:252-269`) strips a trailing `— SUPERSEDED BY DEC-\d+` from the existing row
  before re-adding generated clauses, so any DEC reference placed as a **trailing em-dash clause**
  would be deleted on the next regeneration and never re-added. The DEC references go **mid-sentence**.
- D-06: **The ship-review briefing loses its cost line and nothing replaces it.** Settled here rather
  than raised as a question, because the mechanical premise the grilling left open is false:
  `render-brief.py:11` is a prose comment about why briefings are not hand-authored in HTML, re-read
  at `ae2443d` — there is no actual-vs-budget renderer in that file, and **`render-brief.py` needs no
  edit**. What remains is a scoping choice, and the load-bearing reason to replace nothing is that
  every candidate replacement (a run count, a wall-clock duration) is a **new** measurement this
  feature has not built, and inventing one inside a removal is how removals grow. The briefing keeps
  `cycles_used`/`max_total_cycles`, which is a real bound. Trade-off, named because it is a real loss:
  after this, the briefing gives the user no size signal at all beyond cycles, and cycles count only
  rework — a healthy 16-run feature and a healthy 4-run feature both report the same number. The perf
  review's row 10 (count and budget RUNS) is the lever that would fix it and is out of scope; it is
  filed to the backlog by T-09 rather than dropped.
- D-07: **`BUILD.md` and `SPEC.md` retrospective measurement rows keep their history and gain an
  inline removal marker; they are not deleted.** `BUILD.md:191`, `:224`, `:225`, `:333` and `:578` are
  a dated task ledger, a dated baseline table and a validation-evidence matrix — deleting them would
  rewrite the record of what was measured, which constraint 3 forbids in spirit. But `:224`/`:225`'s
  "How to measure" column and `:333`'s B3 row read as **live instructions** to run a script that will
  not exist, which is REQ-08. The resolution is an inline `(cost-report.py removed — DEC-178)` marker
  on each, so the row stays true as history and false as instruction is impossible. Trade-off: the
  files get slightly noisier, and a reader skimming the baseline table sees a marker rather than a
  clean row.
- D-08: **Every rule-surface task carries a per-line disposition table (line → remove/keep → why),
  not a pattern.** The dominant failure mode of this feature is **over-removal**, because the same
  greps that find money lines also find protected prose about context expense and cycle budgets in
  the same files: `harness/SKILL.md:21` ("a feature dir costs ~100k tokens"), `:127` ("cost a working
  day"), `:229` ("Cost grows with the square of session length"), `:24`/`:69`/`:110` (the cycle
  budget), and `harness-team/SKILL.md:20`/`:108`/`:154`/`:160`/`:194`/`:265`. A task instructing
  "remove the cost references" gets one of these wrong. T-06 is the riskiest for exactly this reason
  and drives S3's segment boundary. Trade-off: the tasks are long, and the tables go stale if an
  earlier task in the same segment shifts line numbers — mitigated by S3's tasks touching disjoint
  files.
- D-09: **T-01 and T-02 each ship their production edit and their test-fixture edit as ONE task, in
  the main-session lane** — the FEAT-07 D-02 shape. DEC-174's compensating control is a human reading
  the diff, and a diff only vouches for itself if it contains the test that proves it. Splitting them
  also opens a red-suite window: `test-validate-digest.py` and `test-check-state.py` are both in
  `run-unit-tests.sh:6`'s `SCRIPTS` list, so a half-landed change reddens **every other task's**
  `verify:` for an unrelated reason. Trade-off: the main session does work `team-config.yaml:155`
  grants to a member; the deviation is recorded here because the PLAN template requires it.

## Tasks

- T-01: Remove `cost_usd` from the orchestrator digest schema, and its fixtures
  segment: S1
  execution_mode: main-session-direct — reason: DEC-174 carve-out. `validate-digest.py` is named in
    CLAUDE.md's carve-out list; `test-validate-digest.py` rides with it under D-09. Direct edit, tests
    run explicitly, a human reads the diff. **Never a team run** — the gates cannot vouch for
    themselves.
  change_type: logic
  depends_on: none
  traces: REQ-04, D-01
  files: `.claude/skills/harness/bin/validate-digest.py`,
    `.claude/skills/harness/bin/test-validate-digest.py`
  intent: >
    Three edits in `validate-digest.py`, each independently required.
    (1) `SCHEMAS["orchestrator"]` (`:177`): delete the `"cost_usd": str,` entry. Leave `"feature"`,
        `"status"`, `"runs"`, `"cycles_used"` and `"briefing"` exactly as they are — `cycles_used` is
        the kept budget (D-01 does not touch it). After this the orchestrator schema has five
        required fields, not six.
    (2) The comment block at `:171-176`: it currently reads "`runs`/`cycles_used`/`cost_usd` are the
        budget accounting it logs." Rewrite to name `runs`/`cycles_used` only, and add one clause
        stating that a return still carrying `cost_usd` is IGNORED rather than rejected (unknown keys
        are ignored — measured), so the next reader does not re-add the field to "be safe".
    (3) The `F12` note at `:661`: it enumerates the `str`-typed fields as "(`team`, `branch`,
        `blocked_on`, `cost_usd`, `briefing`)". Remove `cost_usd` from that list. Leave the rest of
        the sentence and the `NULLABLE` guidance untouched — this is a comment accuracy fix, not a
        behaviour change.
    In `test-validate-digest.py`, the two orchestrator fixtures at `:749` and `:765` carry
    `cost_usd: "12.83"` and `cost_usd: "4.10"`. Do NOT simply delete both lines. Make them prove
    BOTH halves of SC-04: one fixture drops the field entirely (the new contract — must be ACCEPTED,
    and would be REJECTED at `ae2443d`, which is what makes the case discriminating), and one KEEPS
    `cost_usd: "12.83"` with a comment saying it is the backward-compatibility pin — a return written
    to the old contract must still validate, and this fixture goes red if a later edit re-adds the
    field to a required set or introduces an unknown-key rejection.
  verify: >
    `python3 .claude/skills/harness/bin/test-validate-digest.py` exits 0; AND
    `grep -c cost_usd .claude/skills/harness/bin/validate-digest.py` returns 0; AND
    the WHOLE unit suite `.claude/skills/harness/bin/run-unit-tests.sh` exits 0 (this task touches
    `bin/` — the whole-suite clause is mandatory, per SC-11).

- T-02: Remove INV-11, the `cost_model.rates` violation and the rate-staleness warning from
  `check-state.sh`; keep `cost` whitelisted
  segment: S1
  execution_mode: main-session-direct — reason: DEC-174 carve-out. `check-state.sh` is named in
    CLAUDE.md's carve-out list; `test-check-state.py` rides with it under D-09.
  change_type: logic
  depends_on: none
  traces: REQ-02, REQ-06, D-02, D-03
  files: `.claude/skills/harness/bin/check-state.sh`,
    `.claude/skills/harness/bin/test-check-state.py`
  intent: >
    Per-line disposition in `check-state.sh` — REMOVE:
    (a) `:369-373` — the INV-11 rule itself (`if complete and "cost" not in sdoc:` and its
        `bad.append`, including the "run bin/cost-report.py --yaml and record it" message) and the
        two-line comment above it. The `complete = ...` assignment at `:367` is used by nothing else
        in that loop after this — delete it too only if a grep confirms no other use in the loop body;
        otherwise leave it.
    (b) `:248-250` — the INV-11 comment header block.
    (c) `:258-260` — `if cj and not (cj.get("cost_model") or {}).get("rates"): bad.append(...)`. This
        is a HARD violation (D-02): it fails the whole check once T-04 deletes `cost_model`.
    (d) `:261-271` — the `verified_on` staleness `warn.append` block, its `import datetime` and its
        two exception branches. All of it reads the same deleted config block.
    (e) After (c) and (d), the `cfg = read(os.path.join(H, "harness.json"))` / `json.loads` block at
        `:252-257` may have no remaining consumer. It also carries the ".harness/harness.json is not
        valid JSON" check, which is worth keeping on its own merit — **keep the JSON-validity
        `bad.append` and delete only the cost-specific consumers**, or delete the whole block if a
        grep shows `cj` is used nowhere else. State which in the receipt.
    (f) `:357` and `:361` — comments and an error-message string naming INV-11 ("INV-11 (an unmetered
        completed run) silently never fired"; "state.yaml does not parse, so INV-11/15/16 cannot be
        checked"). Rewrite so neither names a dead invariant. `:361` is a live user-facing message:
        it must still name the invariants that DO abort (15/16), just not 11.
    (g) `:302` — the comment "aborting INV-11/13/15/16/18/21 and INV-10". Drop `11` from the list.
    KEEP, and this is the load-bearing half:
    (h) `:344` — `"cycles_used", "cost",` in `CHECKPOINT_KEYS`. **`cost` stays** (D-03). Add an
        inline comment on that line: `# "cost" is HISTORICAL-ONLY (DEC-178): no longer produced, but
        all 67 pre-FEAT-08 run state.yaml files carry it and :401 flags any key not in this set.`
        Without the comment this reads as a dead entry to the next reader who tidies it.
    (i) Every `cycles_used`, `max_cycles` and `max_total_cycles` path — untouched (SC-05).
    (j) `:33` and `:482` — the words "costs no recovery path" and "the check costs nothing" are
        English, not money. Untouched.
    In `test-check-state.py`: `:21` and `:27` are shared fixture strings carrying
    `"cost_model": {"rates": {"sonnet": 1}}` purely to satisfy the check being deleted; `:100` uses
    `'{"cost_model": {"rates": {}}}'` for case_d (an INV-9 hooks test, unrelated to cost, whose
    fixture was shaped to avoid tripping the rates violation). Remove the `cost_model` key from all
    three so the fixtures stop asserting a dead requirement, and confirm case_d still passes for its
    own reason. If any assertion in the file greps for the rates-violation message string, delete
    that case. Add one new case: a `state.yaml` with `status: complete` and **no** `cost:` key
    produces zero violations (INV-11 is gone), and a `state.yaml` WITH a `cost:` block also produces
    zero (D-03's whitelist retention) — one case pinning both directions.
  verify: >
    `python3 .claude/skills/harness/bin/test-check-state.py` exits 0; AND
    `.claude/skills/harness/bin/check-state.sh` exits 0 with zero violations against the repo as it
    stands (67 historical `state.yaml` with `cost:` blocks still present — this is SC-03's command);
    AND `grep -n 'INV-11' .claude/skills/harness/bin/check-state.sh` returns nothing; AND
    `grep -n 'CHECKPOINT_KEYS' -A 12 .claude/skills/harness/bin/check-state.sh | grep -c '"cost"'`
    returns 1; AND the WHOLE unit suite `run-unit-tests.sh` exits 0 (touches `bin/`, SC-11).

- T-03: Delete the meter and its test, and drop it from the unit-suite script list — in one change
  segment: S2
  execution_mode: team — `harness-backend-dev` or `harness-dev-ops` (`team-config.yaml:155`, `:197`)
  change_type: logic
  depends_on: T-02
  traces: REQ-01, D-02
  files: `.claude/skills/harness/bin/cost-report.py` (delete),
    `.claude/skills/harness/bin/test-cost-report.py` (delete),
    `.claude/skills/harness/bin/run-unit-tests.sh` (edit)
  intent: >
    All three edits land together or the runner breaks. `run-unit-tests.sh:6` lists
    `"test-cost-report.py"` in `SCRIPTS`, and `:9-24` is a drift detector that **exits 2** when a
    `test-*.py` exists under `BIN_DIR` that is not in the list. Deleting `cost-report.py` alone leaves
    an orphaned test; deleting both without editing `:6` makes the runner fail on a missing file.
    Delete `.claude/skills/harness/bin/cost-report.py` (439 lines) and
    `.claude/skills/harness/bin/test-cost-report.py` (94 lines) with `git rm`, and remove exactly the
    string `"test-cost-report.py" ` from the `SCRIPTS` array at `:6` — leaving the other twelve
    entries and their order unchanged. Change nothing else in `run-unit-tests.sh`; the drift detector
    itself stays.
    `context_per_turn_tokens` and `warn_at_fraction` disappear with this file: their only consumers
    are `cost-report.py:338`, `:366` and `:406`. `context_per_turn_tokens` needs no config edit — it
    exists in neither `harness.json` (verified at `ae2443d`). `warn_at_fraction` DOES exist in both
    configs and is T-04's, not this task's.
  verify: >
    `test ! -e .claude/skills/harness/bin/cost-report.py && test ! -e
    .claude/skills/harness/bin/test-cost-report.py` succeeds; AND
    `grep -c 'test-cost-report' .claude/skills/harness/bin/run-unit-tests.sh` returns 0; AND the
    WHOLE unit suite `.claude/skills/harness/bin/run-unit-tests.sh` exits 0 — which is the only thing
    that proves the drift detector is satisfied rather than tripped (exit 2), and is mandatory here
    per SC-11.

- T-04: Strip the `cost_model` block and the two USD budgets from both configs
  segment: S2
  execution_mode: team — `harness-dev-ops` (`team-config.yaml:197`)
  change_type: config
  depends_on: T-02
  traces: REQ-02, REQ-09, D-02, D-04
  files: `.harness/harness.json`, `.claude/skills/harness/templates/harness.json`
  intent: >
    The same removals in both files; the line numbers differ by two because the template has an extra
    `_per_feature_rationale`. **Remove** from `.harness/harness.json`: `_cost_model_note` (`:136`),
    the entire `cost_model` object (`:137-231`, which contains `rates`, `verified_on` and
    `_modifier_note` at `:194`), `_budgets_note` (`:232`), and inside `budgets` (`:233-240`) the three
    keys `per_feature_usd` (`:234`), `per_run_usd` (`:235`), `warn_at_fraction` (`:236`) and
    `_per_feature_rationale` (`:237`).
    **Remove** from `.claude/skills/harness/templates/harness.json`: `_cost_model_note` (`:138`), the
    `cost_model` object (`:139-233`), `_budgets_note` (`:234`), and inside `budgets` (`:235-242`)
    `per_feature_usd` (`:236`), `per_run_usd` (`:237`), `warn_at_fraction` (`:238`) and
    `_per_feature_rationale` (`:239`).
    **KEEP in both**, byte-identical: `max_total_cycles` and `_max_total_cycles_rationale`. The
    `budgets` object survives with exactly those two keys — it is not deleted, because
    `max_total_cycles` lives in it. `_budgets_note` goes because its text is entirely about spend
    ("max_cycles bounds RETRIES, these bound SPEND"); if a note is wanted for the surviving key, the
    `_max_total_cycles_rationale` already is one, so do not write a replacement.
    `warn_at_fraction` is removed under D-04: its only consumer was `cost-report.py:406`, deleted in
    T-03, and it has no referent against `max_total_cycles`.
    Touch no other key. `test_matrix`, `test_kinds`, `gates`, `log_retention_days` and `github` are
    out of scope.
  verify: >
    `python3 -c "import json,sys; [json.load(open(p)) for p in ['.harness/harness.json',
    '.claude/skills/harness/templates/harness.json']]"` exits 0 — both still parse as valid JSON; AND
    `grep -c -e cost_model -e per_feature_usd -e per_run_usd -e warn_at_fraction -e _budgets_note
    .harness/harness.json .claude/skills/harness/templates/harness.json` prints `<path>:0` for BOTH
    files — with two file arguments `grep -c` emits one `path:count` line per file, so the expected
    output is two lines, not a bare number, and the command exits 1 when every count is zero (the
    count lines are the evidence, never the exit status); AND
    `grep -c max_total_cycles .harness/harness.json
    .claude/skills/harness/templates/harness.json` prints `<path>:2` for BOTH files (the key and its
    rationale) — again two `path:count` lines; AND
    `.claude/skills/harness/bin/check-state.sh` exits 0 — this is the command that
    fails if T-02 did not land first (D-02); AND the WHOLE unit suite
    `.claude/skills/harness/bin/run-unit-tests.sh` exits 0 (this task touches both `harness.json`
    files, so the whole-suite clause is mandatory per SC-11 — `test-upgrade-config.py` and
    `test-team-catalog.py` read these files).

- T-05: Remove the cost budget from the orchestrator agent definition
  segment: S3
  execution_mode: main-session-direct — reason: `.claude/agents/**` is granted to nobody
    (`team-config.yaml:35-40`); a declared main-session step, not a carve-out
  change_type: docs
  depends_on: T-01
  traces: REQ-03, D-01, D-08
  files: `.claude/agents/harness-orchestrator.md`
  intent: >
    Per-line disposition (anchors re-read at `ae2443d`):
    | Line | Do | Why |
    | `:3` frontmatter `description` — "the feature-wide cycle and cost budgets" | EDIT → "the
      feature-wide cycle budget" | the description is injected at every spawn |
    | `:44` heading "## The two budgets are yours alone" | EDIT → "## The cycle budget is yours
      alone" | there is one budget now |
    | `:46-47` "`cycles_used`/`max_total_cycles` and `cost_usd`/`max_cost_usd` live in
      `feature.yaml`" | EDIT → drop the second pair | |
    | `:48-49` "After every lead returns, run:" + the fenced `cost-report.py --yaml --into` block
      (`:50-52`) | REMOVE the sentence and the whole fenced block | the script is gone |
    | `:54-57` "the lead cannot (no Bash, DEC-116)… INV-16 rejects (DEC-156)" | REMOVE | every clause
      is about the deleted command's invocation |
    | `:57-58` "**Cycles are a hard bound** — exhausting `max_total_cycles` means stop and go up as
      `BLOCKED`." | **KEEP verbatim** | this is the surviving budget (SC-05) |
    | `:58-61` "**Cost is informational** (DEC-134)… never fabricate a figure to stay under it." |
      REMOVE | |
    | `:74` return template `runs: [{ id, squad, verdict, cost_usd }]` | EDIT → `runs: [{ id, squad,
      verdict }]` | |
    | `:76` `cost_usd: "<spend so far, or pending>"` | REMOVE the line | must not precede T-01 (D-01) |
    Leave `cycles_used: <n>` at `:75`, `briefing:` at `:77` and every other DIGEST field untouched.
    The section should read as one coherent paragraph about the cycle budget afterwards, not as a
    two-budget section with one budget deleted out of it.
  verify: >
    `grep -c -e cost_usd -e max_cost -e cost-report -e 'INV-11'
    .claude/agents/harness-orchestrator.md` returns 0; AND
    `grep -c max_total_cycles .claude/agents/harness-orchestrator.md` returns at least 2 (the
    surviving hard-bound sentence and the `feature.yaml` reference); AND
    `.claude/skills/harness/bin/check-docs.sh` exits 0.

- T-06: Remove the money budget from the orchestrator playbook, keeping the cycle budget and the
  context-expense prose
  segment: S3
  execution_mode: main-session-direct — reason: `.claude/skills/harness/SKILL.md` is granted to nobody
  change_type: docs
  depends_on: T-01
  traces: REQ-03, REQ-10, D-01, D-06, D-08
  files: `.claude/skills/harness/SKILL.md`
  intent: >
    **This is the riskiest task in the feature and the reason S3 is a segment (D-08):** the same greps
    that find money lines find protected prose in this file. Per-line disposition, anchors re-read at
    `ae2443d`:
    | Line | Do | Why |
    | `:3` frontmatter "own the budgets" | EDIT → "own the cycle budget" | injected at spawn |
    | `:21` "a feature dir costs ~100k tokens before the first decision (DEC-150)" | **KEEP** | context
      expense, not money — LEAVE LIST |
    | `:24` "`budgets.max_total_cycles`, never your own guess" | **KEEP** | surviving budget |
    | `:60` "cycles_used from the lead's reported SEND-BACKS … only rework counts (DEC-157) — cost —
      values, never narrative" | EDIT → remove the stray `— cost —` clause only; keep the whole
      `cycles_used`/DEC-157 sentence and the "values, never narrative" clause | this line is 90% cycle
      rules; a careless delete removes DEC-157 |
    | `:69-71` "the cycle budget exhausts — `max_total_cycles` outranks 'until done'" | **KEEP**;
      then REMOVE only the trailing sentence "Cost does not stop the loop — it is reported, not
      enforced (DEC-134)." | |
    | `:95-99` "## The two budgets — one hard, one informational (DEC-134)" heading and its two-line
      lead-in naming `bin/cost-report.py --yaml` and INV-11 | REWRITE → "## The cycle budget" plus a
      one-line lead-in: it lives in `feature.yaml`, maintained only by you, from the lead's report | |
    | `:101-104` the two-row budget table | EDIT → keep the `cycles_used`/`max_total_cycles` row
      verbatim, delete the `cost_usd`/`max_cost_usd` row | |
    | `:106-110` "**A cycle is REWORK ONLY (DEC-157)** … `budgets.max_total_cycles`." | **KEEP
      verbatim** | the surviving budget's whole rationale |
    | `:112-113` "**Cost never stops work** … honest-approximate beats precise-invented" | REMOVE | |
    | `:127` "Inferring one such question cost a working day" | **KEEP** | English, not money |
    | `:142` "not a budget sink" | **KEEP** | figurative |
    | `:229` "Cost grows with the square of session length" | **KEEP** | context expense (DEC-148's
      surviving observation) |
    | `:264` briefing step 2, "the **cost line** against the feature budget" | REMOVE that clause only
      — the list keeps every other item (lead summaries, open questions, goal-check, UAT, proposed
      backlog) | D-06: nothing replaces it |
    | `:285` red-flag row "We are over the cost budget, better stop/hide it" | REMOVE the row | |
    Read the resulting `## The cycle budget` section end to end: it must read as a section written
    about one budget, not as a two-budget section with a row deleted.
  verify: >
    `grep -n -e cost_usd -e max_cost -e cost-report -e 'INV-11' .claude/skills/harness/SKILL.md`
    returns nothing; AND `grep -c -e 'costs ~100k tokens' -e 'cost a working day' -e 'Cost grows with
    the square' .claude/skills/harness/SKILL.md` returns 3 — the over-removal guard, and the clause
    that makes this `verify:` discriminating in both directions; AND
    `grep -c -e 'DEC-157' -e 'max_total_cycles' .claude/skills/harness/SKILL.md` is unchanged from its
    pre-edit value (capture it before editing and state both numbers in the receipt); AND the WHOLE
    unit suite `.claude/skills/harness/bin/run-unit-tests.sh` exits 0; AND
    `.claude/skills/harness/bin/check-docs.sh` exits 0.
    **Why the whole suite here:** `test-team-catalog.py` reads this exact live file —
    `:44` sets `SKILL_MD = <REPO>/.claude/skills/harness/SKILL.md`, check (5) at `:133` requires a
    line carrying both `build` and `DEC-118`, and check (8) at `:192` requires `test_matrix` present
    plus `qa`+`validator`+`loop_back` inside an 8-line window. This task's rewrite of `:95-113` is
    large enough to reflow either passage, and no other clause in this `verify:` would notice.

- T-07: Remove the lead-facing metering instructions from the team skill
  segment: S3
  execution_mode: main-session-direct — reason: `.claude/skills/harness-team/SKILL.md` is granted to
    nobody
  change_type: docs
  depends_on: T-01
  traces: REQ-03, REQ-10, D-08
  files: `.claude/skills/harness-team/SKILL.md`
  intent: >
    Per-line disposition, anchors re-read at `ae2443d`:
    | Line | Do | Why |
    | `:20` "defeats the context budget the org exists to protect" | **KEEP** | payload prose — LEAVE
      LIST |
    | `:108` "the run looks correct while costing several times the wall-clock" | **KEEP** | English |
    | `:154` "counting runs instead is how a healthy feature exhausts its budget" | **KEEP** | the
      cycle budget |
    | `:160` "rather than spending the budget to prove it" | **KEEP** | figurative |
    | `:194` "rework at your tier costs one member spawn" | **KEEP** | English |
    | `:213-217` "**Do not try to run `cost-report.py` if you are a lead — you have no `Bash`.**…
      Set `cost: pending_orchestrator` and let the orchestrator fill it after you return:" | REWRITE
      → the DEC-116 rule that leads hold `Read, Glob, Grep, Agent` and no `Bash` **must survive** —
      it is a live tier rule with nothing to do with cost. Keep one sentence stating it and its
      reason (they cannot do a member's work); delete every clause about metering and the
      `pending_orchestrator` placeholder |
    | `:219-223` the fenced "ORCHESTRATOR ONLY" `cost-report.py --yaml --into` block and its comment
      about a shadowed second `cost:` key | REMOVE entirely | |
    | `:225-226` "A complete run left without a `cost:` block is an INV-11 violation — an unmetered
      run is indistinguishable from a free one (DEC-99, DEC-116)." | REMOVE | INV-11 is gone (T-02) |
    | `:228-231` "**Timestamps, same cause.** No `Bash` means no clock…" | **KEEP verbatim** | it
      depends on the no-`Bash` rule this task must preserve; check it still has an antecedent after
      the `:213-217` rewrite |
    | `:265` "Pasting burns the budget the org exists to protect" | **KEEP** | context budget |
  verify: >
    `grep -n -e cost_usd -e max_cost -e cost-report -e 'INV-11' -e 'pending_orchestrator'
    .claude/skills/harness-team/SKILL.md` returns nothing; AND
    `grep -c 'DEC-116' .claude/skills/harness-team/SKILL.md` is at least 1 (the no-`Bash` tier rule
    survived the rewrite); AND `grep -c -e 'context budget the org exists to protect' -e 'Timestamps,
    same cause' .claude/skills/harness-team/SKILL.md` returns 2 — the over-removal guard; AND the
    WHOLE unit suite `.claude/skills/harness/bin/run-unit-tests.sh` exits 0; AND
    `.claude/skills/harness/bin/check-docs.sh` exits 0.
    **Why the whole suite here:** `test-validate-digest.py` reads this exact live file. Its
    `TEMPLATES` list (`:23-29`) names
    `<REPO>/.claude/skills/harness-team/SKILL.md`, anchor `## Reporting up`, and
    `extract_fenced_block` (`:32-47`) pulls the normative return template out of it and runs it
    through the validator (DEC-123). The `:213-231` rewrite in this task sits in the same document;
    a structural edit that disturbs that anchor or its fence makes the extractor raise, and no
    grep clause above would see it.

- T-08: Remove the per-team spend caps from the two team definitions
  segment: S3
  execution_mode: main-session-direct — reason: `.claude/skills/harness/teams/*.yaml` is granted to
    nobody
  change_type: config
  depends_on: T-01
  traces: REQ-02, REQ-09
  files: `.claude/skills/harness/teams/build.yaml`, `.claude/skills/harness/teams/review.yaml`
  intent: >
    Delete exactly one line from each file: `max_cost_usd: 60` at `build.yaml:40` and
    `max_cost_usd: 20` at `review.yaml:16`. Their default source — `harness.json`
    `budgets.per_run_usd` — is deleted by T-04, so leaving them would leave two keys pointing at a
    removed default. Both files are surrounded by dense comments about DEC-118 (single-squad teams)
    and DEC-50/INV-6 (SHA pinning): change none of them. Do not touch `inputs:`, `lead:`, `steps:` or
    `steps_from:`. Both files must still parse as YAML afterwards.
  verify: >
    `grep -c max_cost_usd .claude/skills/harness/teams/build.yaml
    .claude/skills/harness/teams/review.yaml` prints `<path>:0` for BOTH files — with two file
    arguments `grep -c` emits one `path:count` line per file, so the expected output is two lines,
    not a bare number, and the command exits 1 when every count is zero (the count lines are the
    evidence, never the exit status); AND
    `python3 -c "import yaml,sys;[yaml.safe_load(open(p)) for p in
    ['.claude/skills/harness/teams/build.yaml','.claude/skills/harness/teams/review.yaml']]"` exits 0;
    AND `python3 .claude/skills/harness/bin/test-team-catalog.py` exits 0 — the test that reads these
    files; AND the WHOLE unit suite `.claude/skills/harness/bin/run-unit-tests.sh` exits 0; AND
    `.claude/skills/harness/bin/check-state.sh` exits 0.
    **The whole-suite clause is reasoned, not boilerplate.** `test-harness-yaml-corpus.py` scans the
    LIVE shipped teams tree, not a fixture: `:111-112` sets
    `TEAMS_ROOT = .claude/skills/harness/teams` and `ROOTS = [".harness", TEAMS_ROOT]`, `scan_roots`
    (`:134`) calls `scan(os.path.join(REPO, r))` on it, and `:123` asserts `TEAMS_EXPECTED = 2`. It is
    a unit test guarding the two files this task edits, reached by no other clause here. Deleting one
    scalar line breaks neither the YAML parse nor the file count — which is precisely why an
    unguarded regression on this surface would ship unnoticed (SC-11, and the FEAT-07 defect shape).

- T-09: Record DEC-178, correct the DEC-148 index row, and regenerate the index
  segment: S4
  execution_mode: team — `harness-documentor` (`team-config.yaml:116`)
  change_type: docs
  depends_on: T-01, T-02, T-03, T-04, T-05, T-06, T-07, T-08
  traces: REQ-07, REQ-08, D-05, D-06, D-07
  files: `docs/harness/DECISIONS.md`, `docs/harness/DECISIONS-INDEX.md`
  intent: >
    **(A) Append DEC-178 to `docs/harness/DECISIONS.md`.** The highest existing entry is DEC-177
    (verified at `ae2443d`), so the number is DEC-178. Title shape: `## DEC-178 — Cost tracking is
    removed entirely: the meter, the budgets, the invariant and every reporting surface`. The body
    must state, at minimum:
    (1) the reason for the removal — a snapshot-delta meter that cannot see depth-0 main-session work
        (FEAT-06: 9 of 10 tasks; FEAT-07: 8 of 10, finishing at $702.82 against a $550
        orchestrator-computed budget), feeding a budget DEC-134 already made non-blocking;
    (2) **that DEC-148's context watchdog is knowingly DROPPED with the file** — not preserved as a
        standalone script and not folded into `check-state.sh` — **with its reason**: its
        behavioural consequence is already hard-coded by DEC-159, which makes one-phase-per-
        orchestrator mandatory regardless of any measurement, so the diagnostic no longer decides
        anything. This clause exists so a future scan does not re-propose the watchdog, and it is
        SC-09's target;
    (3) that DEC-148's OTHER half (the relay rule) was superseded by DEC-159 independently of this
        feature, so DEC-148 is only PARTIALLY superseded here;
    (4) that historical `cost_usd`/`max_cost_usd` in shipped `feature.yaml` and every `cost:` block in
        a run `state.yaml` are deliberately LEFT IN PLACE as the only surviving record, and that
        `cost` therefore stays in `check-state.sh`'s `CHECKPOINT_KEYS` — allowed, never required
        (D-03), naming the 67-of-67 measurement so the entry is self-justifying;
    (5) that nothing replaces the briefing's cost line (D-06), and that the perf review's row 10
        (count and budget RUNS) is the remaining lever and is filed to the backlog rather than built
        here;
    (6) that `cost_usd` came out of the orchestrator digest schema rather than being kept as a
        declared literal, and that unknown DIGEST keys are ignored so in-flight returns still
        validate (D-01).
    **The body must NOT contain a line starting `**Supersedes DEC-148**`** — D-05. That regex
    (`gen-decisions-index.py:33-36`) would append `— SUPERSEDED BY DEC-178` to the DEC-148 row and
    claim this feature killed both halves.
    **(B) Rewrite the DEC-148 ruling prose in `docs/harness/DECISIONS-INDEX.md:168`** — the text right
    of ` :: `, which the generator preserves verbatim (D-05, measured). It currently reads: "The
    dominant cost term is context length × turn count, so `cost-report.py` flags any agent exceeding
    `budgets.context_per_turn_tokens` and the orchestrator ends its run at a phase boundary." Replace
    with a ruling that (i) keeps the surviving observation (the dominant cost term is context length ×
    turn count), (ii) states the watchdog was dropped with `cost-report.py` **naming DEC-178
    mid-sentence**, and (iii) states the relay half is now carried by DEC-159, **also mid-sentence**.
    **No DEC reference may sit in a trailing `— SUPERSEDED BY DEC-NN` clause** — `strip_trailing_clauses`
    (`:252-269`) deletes exactly that shape on every regeneration and nothing re-adds it (D-05).
    **(C) Hand-write the DEC-178 row's ruling** in `DECISIONS-INDEX.md` in the same change. A new
    entry has no existing row, so the generator emits the `⚠ RULING PENDING` sentinel — SC-09 fails if
    it ships.
    **(D) Regenerate**, then diff. Everything left of ` :: ` on every row is the generator's.
  verify: >
    `.claude/skills/harness/bin/gen-decisions-index.py --stdout | diff -
    docs/harness/DECISIONS-INDEX.md` exits 0 (this is the clause that proves the hand-written prose
    survives regeneration); AND `grep -n 'DEC-148' docs/harness/DECISIONS-INDEX.md | grep -c -e
    'cost-report.py' -e 'context_per_turn_tokens'` returns 0; AND
    `grep -c 'RULING PENDING' docs/harness/DECISIONS-INDEX.md` returns 0; AND
    `grep -c '^## DEC-178' docs/harness/DECISIONS.md` returns 1; AND
    `python3 .claude/skills/harness/bin/test-gen-decisions-index.py` exits 0; AND the WHOLE unit
    suite `.claude/skills/harness/bin/run-unit-tests.sh` exits 0 (this task touches
    `DECISIONS-INDEX.md`, so the whole-suite clause is mandatory per SC-11); AND
    `.claude/skills/harness/bin/check-docs.sh` exits 0.

- T-10: Remove the cost model from SPEC
  segment: S4
  execution_mode: team — `harness-documentor` (`team-config.yaml:116`)
  change_type: docs
  depends_on: T-01, T-02, T-03, T-04
  traces: REQ-08, D-06, D-07
  files: `docs/harness/SPEC.md`
  intent: >
    Per-site disposition, anchors re-read at `ae2443d`:
    | Site | Do |
    | `:1422-1425` §10.3 briefing step 3, "the **cost line** — spend so far against the feature
      budget, from `bin/cost-report.py` (§11.3). Cost is the post-build signal (DEC-99), and a signal
      the operator never sees is not being monitored." | REMOVE the cost-line clause and both
      sentences. Keep every other item in the step: lead summaries, open questions, escalations,
      proposed next steps, goal-check, UAT, Expertise curation (D-06) |
    | `:1708-1709` the `feature.yaml` example block, `cost_usd: 12.83` and `max_cost_usd: 50` | REMOVE
      both lines. Keep `cycles_used: 2` and `max_total_cycles: 10` |
    | `:1711-1712` the `runs:` example rows carrying `cost_usd: 7.39` / `cost_usd: 5.44` | EDIT →
      drop the `cost_usd` field from both rows, keep `id`, `squad`, `verdict` (must match T-05's
      return template) |
    | `:1715-1724` "**The two budgets have different teeth (DEC-134).**" through "the user, seeing
      every cost line, decides." | REWRITE → keep the `max_total_cycles` half **verbatim** (hard,
      rework-only, DEC-157, default in `harness.json`, per-feature raises are user decisions); delete
      the `max_cost_usd` half entirely, including the $9-overrun anecdote and the divergence rule.
      Retitle to "**The cycle budget has teeth (DEC-157)**" or similar — one budget, not two |
    | `:1751-1760` §11.4 the whole `cost:` block in the `state.yaml` example, from `cost:  # written
      by bin/cost-report.py --yaml` through the `by_agent:` entry | REMOVE the block |
    | `:1762-1774` "**The five token classes are recorded separately…**" and "**Claude Code computes
      cost natively**… `--cross-check` compares its total against `ccusage`" | REMOVE both
      paragraphs — they document the deleted script's pricing model |
    | `:1900-1904` the `max_cost_usd: 15` line in the team-YAML schema example and its four comment
      lines about `budgets.per_run_usd` | REMOVE (T-08 deletes the real keys) |
    | `:1964-1969` "**A lead host cannot meter or timestamp its own run.**… returned `cost:
      unavailable` and tripped INV-11 (DEC-116)." | REWRITE → the DEC-116 no-`Bash` tier rule
      SURVIVES (same constraint as T-07); delete the metering, `pending_orchestrator` and INV-11
      clauses, keep the clock/monotonic-marker half |
    | `:2167-2169` §15.5 "Cost moved to post-build monitoring: `bin/cost-report.py` computes per-agent
      spend, `harness.json` carries `budgets`, and the CEO briefing carries a cost line" | This is a
      RETROSPECTIVE passage about why DEC-99 moved cost out of the org-existence question. Under D-07
      keep the history and add an inline `(removed — DEC-178)` marker so it stops reading as a live
      description |
    Change no §11.5 property that does not name cost, and touch no `cycles_used` or `max_cycles` text.
  verify: >
    `grep -n -e cost-report -e max_cost_usd -e 'INV-11' docs/harness/SPEC.md` — every remaining hit,
    if any, is on a line also containing `DEC-178` (the D-07 removal marker); zero hits is also a
    pass; AND `grep -c -e max_total_cycles -e 'DEC-157' docs/harness/SPEC.md` is unchanged from its
    pre-edit value (capture before editing, state both in the receipt); AND the WHOLE unit suite
    `.claude/skills/harness/bin/run-unit-tests.sh` exits 0; AND
    `.claude/skills/harness/bin/check-docs.sh` exits 0.
    **Why the whole suite here:** TWO unit tests read this live file. `test-team-catalog.py:45` sets
    `SPEC_MD = <REPO>/docs/harness/SPEC.md`; check (7) at `:167` matches the §13 `**build**` row and
    compares its conducted-by cell to `build.yaml`'s lead, and check (9) at `:219` parses the
    `**ship-feature**` and `★ **review**` rows into panel sets. `test-validate-digest.py:24-26` lists
    `docs/harness/SPEC.md` anchored at `### 10.4 The team digest` in `TEMPLATES` and validates the
    extracted block. This task rewrites eight sites across SPEC including table rows and fenced
    examples; the grep clauses above are absence checks and would see none of these break.

- T-11: Mark the deleted meter in BUILD's historical tables
  segment: S4
  execution_mode: team — `harness-documentor` (`team-config.yaml:116`)
  change_type: docs
  depends_on: T-03
  traces: REQ-08, D-07
  files: `docs/harness/BUILD.md`
  intent: >
    Under D-07 these are dated records, not live documentation: the ledger is titled "Task ledger —
    snapshot 2026-07-26", the metrics table "Baseline — 2026-07-29", and §"Task 14" is a validation
    matrix with `✅`/`❌` evidence. **Delete none of them.** Add an inline
    `(cost-report.py removed — DEC-178)` marker to each of the four sites whose text would otherwise
    read as a live instruction:
    | `:191` | ledger row 3, "`bin/cost-report.py` + `cost_model` + INV-11" — marker after the row's
      status text |
    | `:224` | baseline row "Context per turn", whose **How to measure** column reads
      `bin/cost-report.py --since <feature start>` — marker in that column |
    | `:225` | baseline row "Cost per feature", **How to measure** `bin/cost-report.py --yaml --since
      <date>` — marker in that column |
    | `:333` | matrix row B3, "Runs `cost-report.py` after each run (INV-11) — **never invents a
      number**" — marker after the behaviour text, before the `[✅ …]` evidence, which stays verbatim |
    | `:578` | the already-struck-through "~~**Cost instrumentation — do this first.**~~ **DONE
      (DEC-114).**" paragraph — append one sentence: the instrumentation was removed by DEC-178, and
      why in one clause |
    Do not restate the reason at each site; one clause at `:578` plus the short marker elsewhere.
  verify: >
    `grep -n 'cost-report' docs/harness/BUILD.md` — every hit is on a line also containing `DEC-178`;
    AND `grep -c 'DEC-114' docs/harness/BUILD.md` is unchanged from its pre-edit value (the history is
    preserved, not deleted — capture before editing and state both numbers in the receipt); AND
    `.claude/skills/harness/bin/check-docs.sh` exits 0.

- T-12: Update `.harness/README.md`, the layout authority for `.harness/`
  segment: S4
  execution_mode: team — `harness-documentor` (`team-config.yaml:118`, same lane as `docs/**`)
  change_type: docs
  depends_on: T-02, T-03, T-04
  traces: REQ-08
  files: `.harness/README.md`
  intent: >
    CLAUDE.md names this file as the layout authority for `.harness/`, and it is outside the 18-file
    sweep because none of its four hits match that grep's patterns. Per-line disposition, anchors
    re-read at `ae2443d`:
    | `:17` | the `harness.json` row lists "`test_matrix`, `test_kinds`, `gates`, `cost_model`,
      `budgets`, `log_retention_days`" — REMOVE `cost_model`; KEEP `budgets`, which still holds
      `max_total_cycles` after T-04 |
    | `:26` | the `features/<FEAT>/feature.yaml` row, "branch, PR, `review_sha`,
      `cycles_used`/`max_total_cycles`, cost, run list" — REMOVE the bare "cost" item; keep the rest
      verbatim |
    | `:46` | "feature-wide cycle and cost budgets" (the orchestrator's ownership) — EDIT →
      "feature-wide cycle budget" |
    | `:86` | "without a cost block" — this is an INV-11 description; REMOVE the clause, and if the
      surrounding sentence exists only to describe INV-11, remove the sentence |
    Change nothing about `cycles_used`, `max_total_cycles`, `runs/`, `expertise/` or `observations/`.
  verify: >
    `grep -n -i cost .harness/README.md` returns nothing; AND
    `grep -c max_total_cycles .harness/README.md` is unchanged from its pre-edit value; AND
    `.claude/skills/harness/bin/check-state.sh` exits 0; AND
    `.claude/skills/harness/bin/check-docs.sh` exits 0.

## Unit-test coverage audit — every task, re-derived not assumed

The FEAT-07 defect is a task that edits a file some `bin/test-*.py` reads, whose `verify:` never
invokes that test. Method: `grep -ln` each edited path across all thirteen `bin/test-*.py`, then open
every hit and separate a **live-tree read** from a fixture written under `mkdtemp`. Result — five
tasks need the whole-suite clause, seven have no unit test on their surface, and the twelfth (T-09)
already invoked its test.

| Task | Live-tree unit test on the edited file | Clause |
|---|---|---|
| T-01 | `test-validate-digest.py` (the file itself) | whole suite — already present |
| T-02 | `test-check-state.py`; `test-team-catalog.py` check (10) `:237` reads `test-check-state.py` for INV-6 fixtures | whole suite — already present |
| T-03 | `test-team-catalog.py` check (6) `:151` lists every file in `bin/` | whole suite — already present |
| T-04 | `test-check-state.py` and `test-upgrade-config.py` — both build fixture `harness.json` trees rather than reading the real one, but the shape they assert is the template this task edits. (`test-gh-sync.py` also writes a `harness.json`, but only `{"github": …}` — no cost surface, so it is not a hit) | whole suite — already present |
| T-05 `.claude/agents/*.md` | **none** — no test reads `.claude/agents/`; the only `agents` hits in `test-harness-yaml.py` and `test-validate-digest.py` are the word in comments | grep + `check-docs.sh` |
| T-06 `harness/SKILL.md` | `test-team-catalog.py` `:44`, checks (5) `:133` and (8) `:192` | **whole suite — ADDED** |
| T-07 `harness-team/SKILL.md` | `test-validate-digest.py` `TEMPLATES` `:26-28` | **whole suite — ADDED** |
| T-08 `teams/*.yaml` | `test-harness-yaml-corpus.py` `:111-112`, `:123`, `:134` | **whole suite — ADDED** |
| T-09 `DECISIONS*.md` | `test-gen-decisions-index.py` `:23-24` | named test + whole suite — already present |
| T-10 `SPEC.md` | `test-team-catalog.py` `:45`, checks (7) `:167` and (9) `:219`; `test-validate-digest.py` `TEMPLATES` `:24-25` | **whole suite — ADDED** |
| T-11 `BUILD.md` | **none** — `grep -l 'BUILD.md' bin/test-*.py` returns nothing | `check-docs.sh` |
| T-12 `.harness/README.md` | **none** — the one hit, `test-harness-yaml.py:84`, is the literal grant glob `.harness/README.md` read out of `team-config.yaml`, not a read of the README's content | `check-state.sh` + `check-docs.sh` |

Two negatives worth asserting rather than assuming. `test-harness-yaml-corpus.py` scans `.harness`
for YAML only, so neither `.harness/harness.json` (T-04) nor `.harness/README.md` (T-12) enters it.
And `test-check-state.py:4` states it runs against fixture trees with `CLAUDE_PROJECT_DIR` pointed at
each, "never against the real repo state" — so T-04's config edit reaches it only through the shape
its fixtures assert, which is why T-04 keeps both the whole-suite clause and the live
`check-state.sh` run.

## Verify receipts — what each task must record

Every task's receipt names its `verify:` command **verbatim** and pastes that command's own output,
not a self-reported verdict. Three tasks (T-06, T-10, T-11) carry an "unchanged from its pre-edit
value" clause; those receipts must state **both** numbers, captured before and after, because an
unchanged count is only evidence if the baseline was measured rather than recalled.

## Approval

status: approved
approved-by: Mike Ruangutai
date: 2026-08-05
