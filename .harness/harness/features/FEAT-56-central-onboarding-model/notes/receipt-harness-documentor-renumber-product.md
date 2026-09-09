# Receipt — harness-documentor — renumber-product (FEAT-56, post-merge integration)

**PASS. FEAT-56's two decisions are now DEC-221 and DEC-222; main's DEC-220 (BUG-1309) keeps its
number and its body untouched. Every one of the 15 live citations was classified by subject before
being rewritten — two of them were NOT on the handed list and are real findings (below).**

`grep -cE '^## DEC-22[012] '` → `1`, `1`, `1`. The surviving `## DEC-220` is
`Build entry opens the mirror and leaves a local receipt; Ship is post-merge terminal finalization only`
— main's, verbatim. Index regenerated (`gen-decisions-index.py --stdout | diff -` prints nothing);
both new rulings hand-written; `check-decision-anchors.py` → `examined 39 anchor(s), 0 failed`, exit 0.

## Per-hit citation table — every hit, and which DEC-220 it meant

Subject test: **main's** DEC-220 = Build entry / mirror / build_entry receipt / Ship finalization.
**Ours** = fleet registration, `harness.json` on a default branch, `fleet.yaml`, central per-segment tree
(→ DEC-221) or the two-skill split (→ DEC-222).

| file:line | was | subject read in place | action |
|---|---|---|---|
| `DECISIONS.md:7021` | `## DEC-220` heading | ours — fleet registration + one product-resident file | **→ DEC-221** |
| `DECISIONS.md:7055` | `## DEC-221` heading | ours — onboarding is two skills | **→ DEC-222** |
| `DECISIONS.md:7084` | DEC-220 in `**Because:**` | ours — "fixed what registration *is*" | **→ DEC-221** |
| `DECISIONS.md:7089` | `**Record:** refs DEC-220, …` | ours — self-ref of the entry above | **→ DEC-221**; DEC-06/120/174 left, unrelated |
| `DECISIONS.md:6989` | `## DEC-220` heading | **main's** — Build entry / mirror / Ship | **left, untouched** |
| `DECISIONS.md:7009-7020` | main's body + `Record:` | main's | **left**; only a missing blank line added before our heading |
| `BUILD.md:377` | DEC-221 | ours — "onboarding is two skills" | **→ DEC-222** |
| `BUILD.md:388` | DEC-220 | ours — interview run in the control-plane clone | **→ DEC-221** |
| `BUILD.md:407` | DEC-220 | ours — config read from the remote ref, never from disk | **→ DEC-221** |
| **`BUILD.md:795`** | DEC-220 | ours — "Amended by DEC-220: … the only artifact that lands in a product repository is its own `harness.json`" | **→ DEC-221 · NOT ON THE HANDED LIST** |
| `BUILD.md:959` | DEC-221 | ours — `harness-init` configures a checkout | **→ DEC-222** |
| `BUILD.md:960` | DEC-221 | ours — `harness-add-repo` registers a repository | **→ DEC-222** |
| `SPEC.md:140` | DEC-221 | ours — first BRIEF is `/harness-plan`'s | **→ DEC-222** |
| `SPEC.md:444` | DEC-220 | ours — "three things, in order" | **→ DEC-221** |
| `SPEC.md:462` | DEC-221 | ours — "Onboarding is two skills" | **→ DEC-222** |
| `org.html:329` | DEC-221 | ours — `harness-add-repo` row | **→ DEC-222** (citation string only; not regenerated, not restyled) |
| `org.html:347` | footer "through DEC-221" | high-water mark | **→ DEC-222** |
| `README.md:192` (1st) | DEC-221 | ours — "two skills, neither of them a command" | **→ DEC-222** |
| **`README.md:192` (2nd)** | DEC-220 | ours — "…then creates its central tree …, in that order (DEC-220)" | **→ DEC-221 · NOT ON THE HANDED LIST** (the line carries two citations) |
| `.harness/README.md:9` | `(DEC-220, DEC-221)` | both ours | **→ `(DEC-221, DEC-222)`** |
| `DECISIONS-INDEX.md:220` | main's row | main's | **left**; regenerated identically |
| `tests/unit/test-no-distribution.py:84` | DEC-221 | ours — the split | **NOT MINE — escalated, see below** |
| `tests/integration/test-onboarding-split.py:5` | DEC-221 | ours — the split | **NOT MINE — escalated, see below** |
| 7 × `features/FEAT-56-…/notes/*`, `runs/*`, `plan.yaml`, `BRIEF.md:115`, BUG-1309 notes | mixed | **record under DEC-188** | **left, deliberately** |

Blank line restored at `DECISIONS.md:7021` — main's `Record:` tail ran straight into our heading with
no separator, unlike every other entry boundary.

## Index

`DECISIONS-INDEX.md:221-222`. Regeneration alone left both rows `⚠ RULING PENDING`; both rulings were
restored verbatim from `git show bb39d5c4^1:` (the pre-merge feature-branch index), so wording is
unchanged from what was signed — only the numbers moved. `refs` on the DEC-222 row recomputed to
`DEC-221` automatically. Anchors moved `@6989→@7022` / `@7023→@7056` by regeneration, never by hand.

## Escalation — two stale citations in files no doc grant covers

Both are one-line comment/docstring edits, both cite **our** split, both must read DEC-222:

- `tests/unit/test-no-distribution.py:84` — `    # split (DEC-221) the four canonical doors live under .omp/commands, and` → `DEC-222`.
- `tests/integration/test-onboarding-split.py:5` — `(fresh-checkout configuration only) and \`harness-add-repo\` (fleet-member registration only, DEC-221).` → `DEC-222`.

Neither is in the documentor domain; not edited, not worked around. **Both suites run green as-is**
(`ALL PASS` / `EXIT=0`) — no test asserts the number, so this is a correctness-of-record issue, not a gate.

## Gates

| gate | result |
|---|---|
| `gen-decisions-index.py --stdout \| diff -` | zero bytes of output — that emptiness is the pass |
| `check-decision-anchors.py` | `examined 39 anchor(s), 0 failed`, exit 0 |
| `tests/integration/test-check-decision-anchors.py` | 8/8 `ok`, exit 0 (both checkers exist; ran both) |
| `tests/integration/test-gen-decisions-index.py` | 14/14 `ok`, exit 0 — this is the suite that asserts the ruling length band |
| `tests/unit/test-no-distribution.py` | `ALL PASS`, exit 0 |
| `tests/integration/test-onboarding-split.py` | `EXIT=0`, exit 0 |
| `check-plan-routes.py` | **exactly 1 violation**, unchanged — see note |

**`check-plan-routes.py` path note.** The absolute path in the dispatch
(`/Users/…/harness/.claude/skills/…`) scans the **main checkout's** features and prints
`0 violation(s) across 4 plan(s)`, exit 0 — it never sees this worktree. The worktree copy prints
`1 violation(s) across 5 plan(s)`, exit 1. The single counted violation is the branch-manifest
deviation (`check-plan-routes.py:898-900` is what increments the counter):

```
DEVIATION /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-56-central-onboarding-model/.harness/team-config.yaml differs from /Users/molchairuangutai/GitHub/harness/.harness/team-config.yaml; routes were resolved against the owner manifest because that is what the hook consults
```

All twenty task rows print `OK`. My edits touch no plan and no manifest, so this is the accepted
pre-merge baseline, unmoved. No seventh failure of any kind appeared.

## Working tree

Mine: `.harness/README.md`, `.harness/harness/docs/{BUILD,SPEC,DECISIONS,DECISIONS-INDEX}.md`,
`.harness/harness/docs/org.html`, `README.md`, and this receipt. Nothing committed.

Foreign, left untouched: **`tests/integration/test-check-state-records.py`** (modified — the
Engineering squad's concurrent task, explicitly out of scope) and
**`notes/receipt-harness-dev-ops-rehome-eng.md`** (untracked — sibling dev-ops' own receipt).
`BRIEF.md:115` still cites DEC-220 for our model; frozen for this integration and not mine, so left.

## Gates — second pass (test-check-plan-routes baseline)

**PASS. `tests/integration/test-check-plan-routes.py` reports exactly SIX failures, exit 1 — the
accepted baseline, unmoved. All six are one cause: the branch manifest deviates from the owner
manifest, so the checker exits 1 where the case asserts exit 0. None is caused by the renumber; the
renumber touched no plan, no manifest and no task row (all twenty task rows print `OK`).**

Suite path confirmed at the expected location (`tests/integration/test-check-plan-routes.py`,
104503 bytes). Run: `env -u HARNESS_AGENT_TYPE python3 tests/integration/test-check-plan-routes.py`
→ trailer `6 FAILURE(S): ['case_04_all_granted_exits_0',
'case_05_ungranted_declared_main_session_exits_0', 'case_15_deviation_plan_still_exits_0',
'case_17_midpattern_wildcard_grant_exits_0', 'case_19d_explicit_path_unaffected_by_the_root_guard',
'case_19d2_explicit_path_with_no_tasks_still_exits_0']`, `EXIT=1`. Failure count = **6**.

| case | what it asserts (read at the callsite, not from the name) | class |
|---|---|---|
| `case_04_all_granted_exits_0` | `test-check-plan-routes.py:122` — `r.returncode == 0` on an all-granted plan. Got 1; stdout is `OK T-01 granted to …` plus the DEVIATION line | **(a) baseline** |
| `case_05_ungranted_declared_main_session_exits_0` | `:130` — `r.returncode == 0` on a declared main-session-direct path. Got 1; the task line itself is `OK` | **(a) baseline** |
| `case_15_deviation_plan_still_exits_0` | `:185` — `r.returncode == 0` when a *plan-level* deviation is reported. Got 1 — but the manifest DEVIATION is a second, separate line | **(a) baseline** |
| `case_17_midpattern_wildcard_grant_exits_0` | `:208` — `r.returncode == 0` on a mid-pattern wildcard grant. Got 1; sibling cases `…_no_violation` / `…_reports_ok` both PASS | **(a) baseline** |
| `case_19d_explicit_path_unaffected_by_the_root_guard` | `:564-566` — `returncode == 0 **and** "OK T-01 granted to" in stdout`. The OK line is present; only the exit code fails | **(a) baseline** |
| `case_19d2_explicit_path_with_no_tasks_still_exits_0` | `:569-571` — `returncode == 0 and "scanning " not in stdout`. `scanning` absent; only the exit code fails | **(a) baseline** |

**The single cause, proved not ours.** Every failing run prints
`DEVIATION <worktree>/.harness/team-config.yaml differs from /Users/…/harness/.harness/team-config.yaml`.
`git status --porcelain .harness/team-config.yaml` is empty and the worktree copy is byte-identical to
HEAD — nobody on this branch edited it. The difference against the owner manifest is one line:
`cli_min_version: "2.1.217"` present in main, absent here. The same inequality existed **pre-merge**:
at `bb39d5c4^1` the branch manifest differed from main's by two lines (`cli_min_version` and the
`receipt-harness-pm-*.md` grant); the merge picked up the grant line and left the version floor out.
Same mechanism, one fewer differing line — so six failures with the *same* cause, not a coincidental count.

**Advisory, not a gate, not mine to fix:** merge commit `bb39d5c4` resolved
`.harness/team-config.yaml` *without* `cli_min_version: "2.1.217"`, which its second parent
(`origin/main`) carried. Landing this branch as-is would delete that line from main. Raised as Q1.

**Working tree, second pass.** `git status --porcelain` names 14 paths, unchanged in membership from
my first pass: the six renumber files (`.harness/README.md`, `README.md`,
`.harness/harness/docs/{BUILD,SPEC,DECISIONS,DECISIONS-INDEX}.md`, plus `org.html` — seven with it),
`plan.yaml`, three receipts (mine, `receipt-harness-pm-renumber-product.md`,
`receipt-harness-dev-ops-rehome-eng.md`), two observations logs (`harness-documentor.md`,
`harness-pm.md`), and the two sibling-owned foreign paths, both left untouched:
**`tests/integration/test-check-state-records.py`** (modified — Engineering squad) and
**`.harness/harness/features/FEAT-56-central-onboarding-model/notes/receipt-harness-dev-ops-rehome-eng.md`**
(untracked — sibling dev-ops). No file I did not touch changed since my last run. Nothing committed.
