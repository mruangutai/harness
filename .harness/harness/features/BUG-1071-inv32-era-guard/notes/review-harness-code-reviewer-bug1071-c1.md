# Code review — BUG-1071 era-guard remedies — cycle 1 — review_sha 6b65ecc (base 75daa3bb)

All reads/commands run in the worktree at absolute paths (the main checkout holds a stale
copy at identical relative paths — confirmed by a first-pass `_read`/`_grep` silently
resolving there; redone with absolute paths throughout). Working tree HEAD is 093574a, one
commit past the pin, but `git diff 6b65ecc..093574a --stat` touches only `feature.json` and
`review_sha` — no source drift, safe to read on disk.

## BLUF

Stage 1: clean, no scope creep, no omission — every changed file serves F1 or F2. F1 closes
cleanly with **no reachable new hazard**: verified no script or template writes
`approval.status: approved` without a co-located `date:` field, and all 32 currently-approved
plans now carry one. F2's five-row semantics table is implemented exactly as declared —
verified live against all five states, not read off the comment. But F2's *migration path* has
a real, reproduced regression: `/harness-init --upgrade` — the exact remedy the guard's own
message names — does **not** fix the condition it's prescribed for on any already-onboarded
project with genuine pre-panel history; it silently converts that project's config to `null`
("no pre-panel era"), which grades every historical plan forever, identical to the corpus-wide
failure F2 was filed to end. **HIGH, one must_fix.**

## Stage 1 — spec compliance: PASS

Diff is exactly `check-state.sh`, `test-check-state.py`, both `harness.json` copies, and the
FEAT-40 backfill — matches issue://1071 + cycle-0's F1/F2 + `handoff-plan.md`'s Working Set
plus the two named remedies. No file outside that set is touched. `#1072`
(`templates/team-config.yaml` parse failure) is filed separately and correctly left alone —
confirmed it still fails identically pre- and post-diff (`upgrade-config.py` prints the same
"THE SHIPPED TEMPLATE... does not parse" notice in my repro below, unrelated to this change).

## Stage 2 — code quality

### F-A (HIGH, must_fix) — `/harness-init --upgrade` does not close F2 for a legacy project; it recreates it silently

`check-state.sh:195-231` (era resolution) + `upgrade-config.py:187-207` (merge). Reproduced live
with a from-scratch fixture (schema_version 1, no `panel_era_start`, one plan
`approval.date: 2024-01-15`, no `panel:` block — a genuinely pre-panel historical approval):

- **Before** `--upgrade`: 2 violations — `INV-32: .harness/harness.json has no
  \`panel_era_start\`... Run /harness-init --upgrade... then set it to the date...` **and**
  `INV-32: FEAT-LEGACY-OLD plan is approved with no complete panel result recorded.`
- Ran `upgrade-config.py <fixture> --templates .../templates` — the sanctioned, documented
  remedy the violation message itself names. Result: `panel_era_start` is merged in as `null`
  (the template's value), because `merge()`'s contract is "template fills gaps," and the
  template's gap-filler for a brand-new project is `null`.
- **After** `--upgrade`: 1 violation — the config-shape violation is gone (key now present),
  but `INV-32: FEAT-LEGACY-OLD plan is approved with no complete panel result recorded.`
  **survives unchanged**, and will survive every future run, because `null` means "grade
  everything" (`case_inv32_null_era_grades_everything` pins exactly this), and a panel cannot
  be retroactively run on a 2024 approval.

The declared table's `null` row ("no pre-panel era; every approved plan graded") is correct
*for a project onboarded after FEAT-45* — the case the test suite exercises
(`case_inv32_null_era_grades_everything`, `test-check-state.py:3247`). No test exercises the
compound case: an *already-onboarded* project with real pre-panel history running the upgrade
path. The one message that told the operator to also set a real date
(`check-state.sh:216-219`) disappears the moment `--upgrade` runs, and the surviving per-plan
message never mentions `panel_era_start` — an operator staring at 30 "no complete panel
result" lines post-upgrade has nothing pointing them back at the one config key that would
fix all of them. This is the exact failure mode F2 was filed to end
("An invariant that fires on 100% of a corpus and admits nothing does not enforce a rule"),
reappearing one layer down, in the migration this repository will never personally exercise
again (its own `panel_era_start` is already hand-set correctly) but every *other* onboarded
project — the stated audience for this file (commit message: "COPIED INTO EVERY ONBOARDED
PROJECT") — will hit on its first `--upgrade`.
Not caught by the shipped suite because every `_inv32_run(..., era=...)` case writes
`panel_era_start` directly; none drives it through `upgrade-config.py`'s actual merge.

**See "Re-adjudication (loop-back)" below — this finding's severity moved from HIGH to MED
after checking two in-band pointers this pass did not weigh, plus a third found while
verifying them. `must_fix` no longer carries F-A.**

### F1 — undated approval now `bad`: no new hazard found (carry-forward, re-verified)

Grepped every writer of `approval:` (`gh-sync.py:948-950`, `factory_decompose.py:342-344`
read `status` only, never write it; `check-domain.sh:537` `approval_guard` only *denies*
writes, never authors one). The only writer is the main session by hand, and
`templates/plan.yaml:38-40` places `date:` directly under `status:` with no path to write one
without the other via any script. Queried every `approval.status: approved` plan.yaml in the
tree (30 features): all 30 now carry a `date`. `2938a5c` (2026-08-25) is confirmed as the
commit that flipped FEAT-40's `status: approved` — the backfilled `date` is an exact match to
that commit's author date. Cycle 0's Q2 suggested grandfathering only *new* signatures; the
shipped remedy instead backfills the one legacy gap and closes unconditionally — a different
mechanism than suggested, but it fully retires the fail-open (verified: zero undated approved
plans remain) rather than narrowing it, so it satisfies F1's intent.

**LOW, non-blocking** — the backfill comment states `approved_by: operator` is "sourced from
the commit that signed it," but `2938a5c`'s diff (`git show 2938a5c`) changes only `status:`;
no `approved_by` field is present there to source. The value is well-grounded (the commit
message says "the operator set out loud," and `operator` matches 20 sibling plans'
convention) but is an inference from the commit's prose, not a literal field the comment
implies was copied. Cosmetic overstatement of provenance; the value itself is correct.

### F2 semantics table — verified against code, all five rows, live

- **no harness.json**: repro (dir exists, file absent) → `.harness/harness.json missing` +
  per-plan graded (no exemption) — matches "no pre-panel era; INV-1 already names it."
- **key absent**: repro → one `VIOLATION: ...has no panel_era_start...` regardless of plan
  count (verified with 2 approved plans, exactly 1 config-line) + plans graded.
- **null**: `case_inv32_null_era_grades_everything` (shipped) + my repro — no config
  violation, plans graded.
- **YYYY-MM-DD**: `case_inv32_era_comes_from_project_config`, `..._boundary_is_exact` — same
  plan is exempt/graded purely on the configured date.
- **unparseable JSON**: repro confirms `except Exception: _era_raw = None` lands on the
  *null* branch as the comment claims, but the **outcome** is still fail-closed (grade
  everything, not exempt) — it reuses null's code path while landing on null's OUTCOME, which
  is the safe direction; no defect.
- **fires exactly once**: hoisted read at `check-state.sh:195` is outside the
  `for feat, doc in plan_docs.items()` loop (`:239`) — confirmed by definition-site reading,
  and empirically with a 2-plan fixture producing exactly 1 config-violation line.
- **dependency order**: `read`, `H`, `json`, `re` all defined at lines 44/63/66, all before
  line 195 — confirmed by grep + read, not by the suite passing.

### Third fail-open-inside-fail-closed instance — none found

Traced every branch in the new era-resolution block (`:195-231`): every path that cannot
resolve a value ends at `_era_start = None`, which is the *maximal-scrutiny* direction (grade
everything), never the lenient one. The one genuine exemption (`_era_start is not None and
signed < _era_start`) is gated behind a `re.fullmatch` on the config value with no coercion
path (JSON bool/int values fall to the `else: bad` branch, not silently truthy). No new
instance of the class cycle 0 named.

### Verification run myself (not accepted from the author)

- `python3 test-check-state.py`: **155 ok / 0 FAIL, exit 0** — exact match to claim.
- `bash check-state.sh` (real tree): **exit 0, 0 VIOLATION, 32 INV-32 notes, 0 of them
  VIOLATION-tagged** (all 32 are `note`-level, i.e., all currently-graded/exempt correctly)
  — exact match to claim.
- `code-grade.py --base 75daa3bb --head 6b65ecc`: 9 Python functions touched, 8 grade
  4/5 PASS, 1 grade 2 (`case_inv32_era_guard_is_load_bearing`, `test-check-state.py:3196`,
  CYCLOMATIC 6/COGNITIVE 7/ABC 30.3) — same function, same grade, already reasoned in cycle 0
  (self-contained mutation-test helper, complexity earns its keep). Unchanged in substance
  this cycle (only gained an `era=` kwarg at its two call sites). `code_grade: grade_2`, med,
  non-blocking, reasoning carries forward.

## Re-adjudication (loop-back)

Sent back to re-weigh F-A's severity against two in-band pointers I did not weigh in cycle 1.
Verified both at source, plus a third found while checking them. My original artifact above
is left unmodified; this section supersedes only F-A's rating and the DIGEST.

**Pointer 1 — `check-state.sh:216-219`, the pre-upgrade key-absent VIOLATION.** Read the full
string (not a paraphrase): `"INV-32: .harness/harness.json has no `panel_era_start`, so no
panel era can be resolved. Run /harness-init --upgrade (upgrade-config.py) to merge the key
in, then set it to the date the adversarial panel became available here, or null if this
project never predated it."` Confirmed: it carries the complete two-step instruction, exactly
as claimed. **CONFIRMED.**

**Pointer 2 — `upgrade-config.py:202-206`, the merge run's own stdout.** Confirmed by reading
`merge()` (`upgrade-config.py:59-81`): it accumulates dotted paths of every template key the
project lacked into `added`, and the caller prints `f"  + {a}"` for each, unconditionally
whenever `added` is non-empty. Verified with an in-memory harness (`merge()` called directly
against `templates/harness.json` and a bare `{schema_version:1, test_kinds:{}}` project dict
— no disk writes, respecting my read-only role): `panel_era_start` is in `added`, so the
upgrade run's own terminal output includes the line `  + panel_era_start`, at the exact
moment the null is written. **CONFIRMED**, and stronger than claimed — the same `added` list
also contains `_panel_era_start_note` (see pointer 3).

**Pointer 3 — found while verifying pointer 2, not in the dispatch.**
`templates/harness.json:5` carries `_panel_era_start_note`, a full-sentence explanation
placed immediately beside `panel_era_start` in the template: what the key means, that INV-32
never grades a plan signed before it, that `null` means "no pre-panel era," and an explicit
citation of this bug ("BUG-1071 panel finding F2"). Because it's a template key the project
also lacks, `merge()` copies it into the project's `.harness/harness.json` in the same pass —
so after `--upgrade`, the project's own config file carries this explanation **verbatim,
permanently, immediately adjacent to the `null` an operator is told (by pointer 1) to go
change.** This is the strongest of the three: pointers 1 and 2 are transient (a VIOLATION
line that disappears once fixed; a stdout scroll easy to skim past), but pointer 3 sits
inside the file itself, for as long as the project exists, exactly where an operator following
pointer 1's instruction ("set it to the date...") would be looking when they open the file to
do it.

**A fourth check, not asked for but load-bearing for the "wall of 30 lines" framing**: is the
key-absent VIOLATION (pointer 1) actually separated in time from the per-plan wall, or do they
co-occur? Read `check-state.sh:1966-1970`: both the era-resolution block and the per-plan loop
push into the *same* `bad` list, in execution order (era resolution at `:195-231` runs before
the per-plan loop at `:239` in the same function), and `bad` is printed in append order as
`VIOLATION` lines with a shared nonzero exit. So on the **first** `check-state.sh` run against
an unupgraded legacy project — the state every such project is in until someone runs
`--upgrade` — the two-step instruction line prints **immediately before** the wall of 30
per-plan violations it explains, in the same invocation, not in some earlier run the operator
might have missed. The "wall with nothing pointing back" scenario requires the operator to
have run `--upgrade` (removing the config-shape line) *before* ever running `check-state.sh`
against that project's real legacy plans at all — narrower than the original framing assumed,
since for most already-onboarded projects the two messages arrive together on day one.

**What the three pointers still do not cover — stated concretely, held as a residual, not as
grounds for HIGH.** An operator who runs `/harness-init --upgrade` for an unrelated reason
(e.g., a routine schema-version bump, run before the project had any legacy approved plans on
disk, or run non-interactively with stdout unread — a real pattern for scripted onboarding)
sees pointer 2/3 at the moment of merge but does not act on it; who then, later, encounters
the per-plan wall in isolation (config-shape violation gone, so pointer 1 no longer fires);
and who never opens `.harness/harness.json` despite it containing pointer 3. That combination
is not impossible, but it now requires missing three independent, converging signals rather
than one absent signal — nothing FORCES a value (correct, unchanged from cycle 1: no schema
validation rejects `null` on a project with pre-existing approved plans), and the per-plan
message genuinely never names `panel_era_start` (confirmed again at `check-state.sh:279`,
unchanged). That residual is real and worth a follow-up (the per-plan message could name the
key it depends on, or `--upgrade` could refuse to default-null when approved plans already
predate the run), but it is no longer the "operator has nothing pointing them back" case my
cycle-1 finding described — three separate mechanisms now demonstrably do, two of which
co-occur with the wall on the very first encounter and one of which is permanent.

**Direction of failure and reversibility, weighed as asked.** The defect can only leave the
gate RED — a legacy project that gets nulled sees *more* VIOLATIONs (the per-plan wall was
already firing pre-upgrade; upgrading doesn't add new failures, it just fails to remove the
class that a correctly-set date would have removed), never a false PASS. It cannot ship
silently. The remedy is a single key in one file, with no data loss and no corruption —
setting `panel_era_start` retroactively is fully effective; nothing about the null write is
destructive or hard to reverse. Weighed against this repo's own bar (`med` = "wrong behaviour
in an unlikely case, or real maintainability cost"; `high` = "wrong behaviour in a realistic
case"): given three converging in-band pointers, two of which fire together with the wall on
the very first run for the common case, the surviving gap is the unlikely case, not the
realistic one.

**Verdict on the claim: CHANGED.** F-A moves from HIGH to MED. It stays a real finding — the
migration path has a genuine, reproduced gap, and the per-plan message's silence on
`panel_era_start` is worth fixing — but it no longer gates. Filed as a should-fix
follow-up, not a blocker on this feature. `must_fix` no longer contains F-A.

```yaml
VERDICT: PASS
DIGEST:
  headline: "CHANGED: F-A HIGH -> MED. Held cycle-1 was that no pointer exists back to panel_era_start; re-checked check-state.sh:216-219 and upgrade-config.py's added/print path plus a third pointer I found while verifying (_panel_era_start_note merges verbatim into the project's harness.json beside the null) — three converging in-band signals, two of which co-occur with the violation wall on the same run for the common already-onboarded case. A narrower residual (upgrade run for an unrelated reason, unread stdout, config file never reopened, per-plan message still silent on the key name) survives and is worth a should-fix follow-up, but is the unlikely case now, not the realistic one this repo's HIGH bar names."
  stage1: PASS
  stage2: PASS
  severity_max: med
  findings: 4
  must_fix: []
  spec_violations: []
  reviewed: "75daa3bb..6b65ecc"
  human_commits_in_scope: []
  code_grade:
    - { qualname: "case_inv32_era_guard_is_load_bearing", path: ".claude/skills/harness/bin/test-check-state.py", line: 3196, result: grade_2, severity: med, driver: abc, reasoned: true }
  open_questions:
    - { id: Q1, question: "Should-fix follow-up (non-blocking): the per-plan INV-32 'no complete panel result recorded' message (check-state.sh:279) never names panel_era_start, so an operator who reaches it without having read the upgrade-time stdout or reopened harness.json has no in-message pointer. Worth a small follow-up to name the key directly in that message.", blocking: false }
  files_touched: []
  expertise_update: []
artifact: .harness/harness/features/BUG-1071-inv32-era-guard/notes/review-harness-code-reviewer-bug1071-c1.md
```
