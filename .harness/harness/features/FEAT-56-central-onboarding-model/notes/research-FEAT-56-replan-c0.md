# FEAT-56 replan — revised BRIEF and nine added tasks

**BLUF.** The revision fits in **9 new tasks (T-09..T-17), exactly at the ceiling, nothing cut.**
BRIEF now states the two-artifact split plus OMP reachability; 13 SCs (5 marked already-met, SC-09
struck, 2 new uat, 1 mechanical door criterion, 1 automated split assertion); 5 new decisions
(D-07..D-11). `check-plan-routes.py` exits 0, every new task's `verify` was run verbatim and
observed RED, and every named path was resolved with `check-domain.sh --resolve` one file at a time.
Approval stays pending on both fragments; T-01..T-08 stay `done`.

**My measured door-port figure is 12 files, not the advisor's 4-5 and not the earlier pm's 14** —
enumeration in §6. The earlier 14 counted four doc files and `check-instruction-paths.py`, all of
which I measured as needing nothing.

**Three corrections to inherited claims, each re-derived:**

1. The dispatch's `harness.md:12` router site is wrong. At `12f74ea8` `harness.md:14-17` **already**
   routes a registered fleet member with an empty `features/` to `/harness-plan`. The stale sites are
   `harness-plan.md:18`, `harness-grilling.md:7` and `:13` — plus `harness.md:12-14`, which routes
   *four* conditions to `/harness-init` where only the first (`no .harness/ here`) is still its job.
   T-12's intent says so and tells the doer to re-derive.
2. **DEC-06 is not being reversed, and DEC-113 never recorded `deploy.sh`'s deletion.** DEC-113
   (`DECISIONS.md:1825`) governs crew overrides. `deploy.sh` was deleted in commit `45859123`
   (FEAT-12, issue #259) and **no** `DECISIONS.md` entry records it. So DEC-06's premise
   (`:95-97`, "deploy distributes skills and agents but not `.claude/commands/`") expired for a
   reason nothing had written down. Its *conclusion* — skill, not command — is what `harness-add-repo`
   conforms to. Recorded as D-10, and the stale `(DEC-113)` citation in BRIEF's Problem is fixed.
3. `check-instruction-paths.py`'s `harness-*` prefix predicate is at **`:31`**, not `:29`, and
   `harness-add-repo` satisfies it — so the `MAIN_SESSION_ONLY` entry is what removes it from the
   anchor scan. **T-09 therefore lands BEFORE T-10**: `_skill_docs` builds its list from
   `os.listdir`, so a tuple entry for a directory that does not exist yet is a no-op, while the
   reverse order reddens `check-instruction-paths.py` — which `check-state.sh` runs at every door
   and before every commit — on an otherwise-correct tree.

## Lane split (all resolved per file, §4)

| Route | Tasks |
|---|---|
| `main-session-direct` (NOBODY) | T-10 add-repo skill · T-11 harness-init cut · T-12 instruction surface (12 files) · T-13 door move · T-15 agent definitions |
| `team` / `harness-dev-ops` | T-09 `MAIN_SESSION_ONLY` · T-14 generator + `check-omp-port` assertion |
| `team` / `harness-documentor` | T-16 docs + new DECISIONS entry + index |
| `team` / `harness-qa` | T-17 test reconciliation + `test-onboarding-split.py` |

The OMP port spans lanes and is **two tasks**: T-13 (`.omp/commands/**`, `.claude/commands/**` —
NOBODY) then T-14 (`bin/**`, `tests/**` — team), ordered by `depends_on`. T-13 precedes T-14
deliberately: nothing in the tree reads either command directory at `12f74ea8` (verified across
`tests/`, `bin/`, `.github/workflows/`) except `test-no-distribution.py:77-83`, which the adapters
keep true — so no gate can redden in the intermediate state.

## Evidence

### 2. Task and approval state

```
17 [('T-04', 'done'), ('T-01', 'done'), ('T-02', 'done'), ('T-03', 'done'), ('T-05', 'done'),
    ('T-06', 'done'), ('T-07', 'done'), ('T-08', 'done'), ('T-09', 'ready'), ('T-10', 'ready'),
    ('T-11', 'ready'), ('T-12', 'ready'), ('T-13', 'ready'), ('T-14', 'ready'), ('T-15', 'ready'),
    ('T-16', 'ready'), ('T-17', 'ready')] {'status': 'pending'}
decisions: ['D-01'..'D-06', 'D-07', 'D-08', 'D-09', 'D-10', 'D-11']
```

### 3. `check-plan-routes.py <plan>` — exit 0

```
MANIFEST /Users/molchairuangutai/GitHub/harness/.harness/team-config.yaml
OK T-09 granted to harness-backend-dev, harness-dev-ops
OK T-10: declared main-session-direct (.claude/skills/harness-add-repo/SKILL.md ungranted)
OK T-11: declared main-session-direct (.claude/skills/harness-init/SKILL.md ungranted)
OK T-12: declared main-session-direct (12 paths ungranted)
OK T-13: declared main-session-direct (.omp/commands x4, .claude/commands x4 ungranted)
OK T-14 granted to harness-backend-dev, harness-dev-ops, harness-qa
OK T-15: declared main-session-direct (.omp/agents x2, .claude/agents x2 ungranted)
OK T-16 granted to harness-documentor
OK T-17 granted to harness-backend-dev, harness-dev-ops, harness-qa
0 violation(s) across 1 plan(s)          EXIT=0
```

### 4. `check-domain.sh --resolve`, one call per file

```
.claude/skills/harness-add-repo/SKILL.md            NOBODY      .claude/skills/harness-init/SKILL.md         NOBODY
.claude/skills/harness-grilling/SKILL.md            NOBODY      .claude/commands/harness.md                  NOBODY
.claude/commands/harness-plan.md                    NOBODY      .claude/commands/harness-ship.md             NOBODY
.claude/commands/harness-grilling.md                NOBODY      .omp/commands/harness.md                     NOBODY
.omp/commands/harness-plan.md                       NOBODY      .omp/commands/harness-ship.md                NOBODY
.omp/commands/harness-grilling.md                   NOBODY      templates/README.md                          NOBODY
templates/harness.json                              NOBODY      templates/team-config.yaml                   NOBODY
templates/BRIEF.md                                  NOBODY      templates/PLAN.md, templates/DESIGN.md       NOBODY
references/github-mirror.md                         NOBODY      .omp|.claude/agents/harness-dev-ops.md       NOBODY
.omp|.claude/agents/harness-visual-designer.md      NOBODY
bin/sync-command-adapters.py  bin/check-omp-port.py  bin/check-instruction-paths.py   harness-backend-dev harness-dev-ops
tests/integration/test-sync-command-adapters.py  tests/integration/test-check-omp-port.py
tests/unit/test-no-distribution.py  tests/integration/test-hooks-install.py
tests/integration/test-post-merge-sweep.py  tests/integration/test-layout-migration.py
tests/integration/test-onboarding-split.py                      harness-backend-dev harness-dev-ops harness-qa
.harness/harness/docs/{DECISIONS,DECISIONS-INDEX,SPEC,BUILD}.md  org.html  README.md  .harness/README.md
                                                                harness-documentor
```

Every `execution_mode` agrees: no NOBODY path sits in a `team` task, and no granted-only path sits
in a `main-session-direct` one. (`check-plan-routes.py` prints `declared main-session-direct` rather
than `DEVIATION` for all five msd tasks, which is the DEC-174 carve-out's expected output.)

### 5. Every new `verify` run verbatim against the tree — all nine RED

```
T-09 exit=1 RED    T-10 exit=1 RED    T-11 exit=1 RED
T-12 exit=1 RED    T-13 exit=1 RED    T-14 exit=2 RED
T-15 exit=1 RED    T-16 exit=1 RED    T-17 exit=2 RED
```

Run by loading `plan.yaml` and handing each `verify` string to `bash -c` unchanged.
`exit=2` on T-14 and T-17 is the interpreter reporting the deliverable file absent — the weakest
form of red, so both tasks carry an explicit red-capability proof in `intent` (T-14's orphan-door
case, T-17's run against the pre-T-11 blob) rather than resting on it.

Per-conjunct discrimination, checked individually rather than trusting the chain's first failure
(the `&&` chain hides later clauses — an already-green conjunct proves nothing):

```
harness-init/SKILL.md   Track A 2   Track B 2   factory/fleet.yaml 2   The approval gate 1
                        then the BRIEF 1   Design pass 1   harness-visual-designer 1
                        'steps? [4-9]' 6   'before step 2' 2   'skip to step 2' 1
                        'through step 2' 3   'brief is pending' 1
check-omp-port.py       'omp/commands' 0     <- T-14's new second conjunct is red today
```

Two verify defects found and fixed this way:
- T-11 originally banned the bare string `step 2`. **Wrong**: renumbering the three survivors to
  1/2/3 creates a legitimate `step 2`, so a correct rewrite would have failed. Replaced with the
  four stale phrases by name plus `steps? [4-9]`.
- `proceed to step 2` **wraps across a line break** at `:155-156`, so a line-oriented grep never
  matched it and the conjunct was always-green. Now flattened through `tr` first.
- T-14 originally asserted only that `check-omp-port.py` exits 0 — which it already does. A doer
  could have shipped the generator and skipped the port edit. Added the `omp/commands` presence
  conjunct, `tests/integration/test-check-omp-port.py` to `files`, and intent item 4 requiring a
  temp-root case that deletes a door and asserts `check()` names it.

Seven dangling step references in `harness-init`'s **surviving** regions, all enumerated in T-11's
intent: `:65`, `:83`, `:155-156`, `:159-160`, `:194`, `:205`, `:212`. `:194` is substantive, not a
renumbering — "will fail if the brief is pending (step 7)" inside surviving step 9, and there is no
brief and no approval gate in this skill after D-09.

### 6. The OMP door port — my own measurement: **12 files**

Canonical + adapter surface, 8:
`.omp/commands/{harness,harness-plan,harness-ship,harness-grilling}.md` (new canonical) and the same
four names under `.claude/commands/` rewritten as banner-prefixed generated adapters.

Gate surface, 3: `bin/sync-command-adapters.py` (new), `bin/check-omp-port.py` (door block),
`tests/integration/test-sync-command-adapters.py` (new). Plus `tests/integration/test-check-omp-port.py`
for the redden-on-missing-door case = **12**.

Test reconciliation, 1: `tests/unit/test-no-distribution.py:77-83` — the only place in the whole
tree that reads a command directory.

**Why not 14.** The earlier figure counted `bin/check-instruction-paths.py` and four doc files.
Measured: `scope()` at `:45-59` scans `.omp/agents`, `.claude/agents`, `.claude/skills/harness-*`,
`references/` and `templates/` — **neither command root**, before or after, so nothing there breaks
and nothing is required. And `grep -rn 'commands/'` over `SPEC.md`, `BUILD.md`, `org.html`,
`README.md`, `.harness/README.md`, `AGENTS.md`, `CLAUDE.md` returns **zero** — no document spells a
command path; they name doors by slash, which does not change. The only doc work is the new
`DECISIONS.md` entry and its index row, folded into T-16 because it is shared with the split.
**Why not 4-5:** that figure omitted the adapter side and the test that makes the assertion
falsifiable.

**Canonical root, stated:** `.omp/commands/` (D-11). OMP reads slash commands from its config root's
`commands/` directory (`omp://config-usage.md`, scope-specific loading: `Slash commands:
commands/*.md`), and `.omp/config.yml` sets `disabledProviders: [claude]`, so a door authored only
under `.claude/commands` is discovered by Claude Code and nothing else. A symlinked
`.claude/commands` was considered and rejected: no test in this repository can exercise Claude Code's
own discovery, so the symlink's correctness would be unverifiable, whereas duplicated files with a
diff-clean check are certain to work in both surfaces.

## Open questions

- **Q1 (non-blocking, for the operator at signature):** ~20 documents spell `/harness-init` as if it
  were a slash command; it resolves in neither surface and never did. Declared a non-goal here so it
  is not mistaken for delivered work. Own chore, or fold into a later feature?
- **Q2 (non-blocking):** no gate can prove a door is *discovered* by a provider. SC-13 proves the
  four doors exist at the neutral root with identical text and that a Claude-only door reddens the
  check; whether an OMP session resolves `/harness-plan` from `.omp/commands/` is an operator
  observation in a live session, recorded in the UAT notes rather than gated.
- **Q3 (non-blocking, harness defect):** no `DECISIONS.md` entry records `deploy.sh`'s deletion, so
  DEC-06's expired premise has no successor entry to point at and BRIEF cited DEC-113 for it by
  mistake. D-10 records the reasoning; whether the log itself should carry a strike on DEC-06's
  premise is the harness owner's call.

## Files

- `BRIEF.md` — revised in place (Problem, Goal, REQ-01..REQ-10, Constraints, Non-goals, 13 SCs,
  Verification gaps). `## Approval` untouched at `status: pending`.
- `plan.yaml` — T-09..T-17 and D-07..D-11 added through `plan-merge.py apply`; T-10/T-11/T-14
  refined through `plan-merge.py amend --expect-sha256`. `approval:` and `panel:` untouched.
- `notes/research-FEAT-56-replan-proposal.md` — the exact proposal document that was applied, kept
  as the record of what `plan-merge.py` merged.
