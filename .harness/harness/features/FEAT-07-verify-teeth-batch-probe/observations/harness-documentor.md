# Observations — harness-documentor — FEAT-07

- 2026-08-04 (T-06, SPEC §8.1): added `task: T-NN|none` and `task_verify: pass|fail|n/a` to the
  eng-devs bullet (`docs/harness/SPEC.md:1054-1055`) and the dev-ops bullet (`:1062-1068`). All six
  T-06 verify clauses measured 0 before the edit; after: eng-devs `task_verify` = 1 (>=1), dev-ops
  `task_verify` = 2 (>=1), whole-file `task_verify` = 3 (>=2), eng-devs `` `task: `` = 1 (>=1),
  dev-ops `` `task: `` = 2 (>=1), whole-file `` `task: `` = 3 (>=2). `git diff` is exactly two
  hunks; the four awk anchors still match at 1054/1056/1062/1069 and each label is unique in the
  file. `check-docs.sh` exit 0, 45 patterns across 180 files (179 before this log existed — G-04
  again: the observations log itself enters check-docs scope, so run the checker AFTER writing it).
  `no-task` is absent from SPEC.md (grep exit 1, no output).
- 2026-08-04: the dev-ops asymmetry prose was written from the validator's control flow, not from
  the plan's paraphrase. With `task: none`, `validate-digest.py:539` (`_unbound` → `continue`)
  accepts an OMITTED `task_verify`, and `:587-592` (D-08(b)) also accepts `task_verify: n/a`
  alongside PASS — `n/a` is in `harness_yaml.PLACEHOLDER_UNSET:302`. The plan's intent named only
  the omission case; both are legal, so SPEC now says "may omit `task_verify` or report it `n/a`".
- 2026-08-04: convention tension left un-edited on purpose. Elsewhere in §8.1 an `n/a` member is
  listed on an enum iff `n/a` is compatible with `VERDICT: PASS` (dev-ops `suite` lists it; eng-devs
  `suite` does not). By that rule `task_verify` would read `pass|fail` for both personas, since both
  are in `GATE_FIELDS` for it (`validate-digest.py:92-93`) and `SCHEMAS` gives it only
  `{"pass","fail"}` (`:149`, `:160`). T-06's intent mandates the three-member spelling, so
  `pass|fail|n/a` is written and the inconsistency is reported as a gap rather than resolved.
- 2026-08-04 (T-09, DEC-175/176/177): PRECONDITION `gen-decisions-index.py --stdout | diff -
  docs/harness/DECISIONS-INDEX.md` **exited 0** before any edit, and `git status --short` showed the
  index clean — so there was NO pre-existing drift to absorb and no differing rows to report. Last
  DEC in `DECISIONS.md`'s tail before the edit: **DEC-174 @4680**, so DEC-175/176/177 were free.
  After: DEC-175 @4738, DEC-176 @4833, DEC-177 @4855. Verify clause 1 exit 0; clause 2 = 3;
  `check-docs.sh` exit 0 (45 patterns, 180 files).
- 2026-08-04 (T-09): the dispatch's commit→task mapping was INVERTED and I did not repeat it.
  `0a34989` is **T-05** (trailer `[harness:t-05]`, touches `harness-zero-micro-management/SKILL.md`);
  `7da58c6` is **T-07 AND T-08** ("Two tasks, one commit", both edit `.claude/commands/harness.md`).
  DEC-176 and DEC-177 therefore both cite `7da58c6`. P-01 caught it.
- 2026-08-04 (T-09): PLAN intent `:900` says entry (1) should cite "T-05/DEC-176's neighbourhood",
  but the intent's own enumeration makes DEC-176 the BATCHING rule — T-05 gets no DEC number among
  the three. Cited the file+commit (`harness-zero-micro-management/SKILL.md`, `0a34989`) instead; a
  `DEC-176` string in DEC-175's body would also have entered that row's generated `refs:` graph and
  made the wrong reading machine-visible.
- 2026-08-04 (T-09): the generator is safe to run repeatedly but it rewrites every row, so the check
  that catches a tripped parser is a diff of the index against a scratchpad copy taken BEFORE the
  edit: it must show exactly N added lines and no modified row. It did (3 added, 0 modified).
  Order that works: append entries → run generator (new rows appear as `⚠ RULING PENDING`) → edit
  ONLY the text after ` :: ` → run generator again → diff. Keep `SUPERSEDES/CORRECTS/INVERTS` and
  `**Amendment` off the start of any title or bold run, or a live decision's row gains a false
  "SUPERSEDED BY" marker (`gen-decisions-index.py:24-36,144-203`).
- 2026-08-04 (T-09): "four rows" vs "three combinations" is NOT a contradiction — BRIEF `:124-134`
  tabulates four persona/field combos accepted at `4091b36`, of which three are closed here and the
  fourth (`dev-ops suite: fail` + PASS) is deliberate residue (D-03). Both numbers are written into
  DEC-175 so a future reader does not re-derive the gap as a bug. Fixtures for all four exist in
  `test-validate-digest.py:1178,1183,1197,1214`.
- 2026-08-04 (T-09): DEC-175's present-tense behaviour claims are backed by a run, not by reading —
  `python3 .claude/skills/harness/bin/test-validate-digest.py` exits **0**, ALL PASSED, and the
  REQUIRED-`task` claim has its own fixture (`:1165` "dev omitting task entirely is rejected").
- 2026-08-04 (T-09): near-miss worth keeping. "`GATE_FIELDS` is consulted only inside the placeholder
  branch" is true of `4091b36` and FALSE of the current file — T-01's REQ-11 work added a second
  consultation at `validate-digest.py:548` (missing-field message path). Written in the present tense
  it would have made the authority entry contradict a one-line grep. Rule: a diagnosis of the OLD
  behaviour gets the old commit and the past tense; final anchors and final line counts are only
  valid after the last body edit, so regenerate the index AFTER the last prose change (DEC-176/177
  moved @4833→@4837 and @4855→@4859 on the fix).
- 2026-08-04 (T-09 follow-up): DECISIONS-INDEX rows carry a **30-word ruling cap** enforced only by
  `test-gen-decisions-index.py:406-408` (`test_committed_index_is_complete_and_within_budget`), plus
  a 20-non-whitespace-char floor (`:404`) and a 260-line file budget (`:378`). None of it is stated
  in the index's own header, and neither `gen-decisions-index.py` nor `check-docs.sh` sees it — so an
  over-long ruling passes generator-diff and check-docs and only reddens `run-unit-tests.sh`.
  Measure with the gate's counter, not your own: the count is
  `len(strip_ruling_prose(ruling).split())` — a naive whitespace split, so a standalone em dash is a
  token and backticked spans are one token each. DEC-175's ruling read 32 by that counter (31
  non-dash words); dropping the trailing "(`dev-ops` `suite` excluded — residue)" parenthetical
  landed it at 27. Rule: after editing any index ruling, run `run-unit-tests.sh`, not just the
  generator diff.

## SC-07 / S1 artifact — state-binding rule on the SPEC §8.1 eng-devs bullet (2026-08-04)

**Artifact placement:** the dispatch named
`.harness/features/FEAT-07-verify-teeth-batch-probe/notes/sc07-fix-spec-eng-devs.md`, and
`check-domain.sh` BLOCKED the write — `notes/**` is not in harness-documentor's grant
(`team-config.yaml`; permitted in-feature path is `features/*/observations/harness-documentor.md`).
Not worked around; the artifact is inlined here and raised as Q1.

**Done.** §8.1's eng-devs bullet now carries the same two-part rule the dev-ops bullet already
stated, inline, in §8.1's parenthetical style. One file changed. dev-ops and every other §8.1
bullet are byte-identical.

**The amended bullet, in full (`docs/harness/SPEC.md:1054-1059`):**

```
- **eng devs** (frontend / backend / ai / data): `tests_added: <n>`, `suite: pass|fail`,
  `blocked_on: <text|none>`, `task: T-NN|none`, `task_verify: pass|fail|n/a` (binds only when
  `task` names a real `T-NN`: `n/a` means the task's `verify:` was refused or never ran, and both
  `fail` and `n/a` are REJECTED alongside `VERDICT: PASS` — every PLAN task carries a `verify:`,
  so "not applicable" is never the honest answer. The one exception is `task: none`, a dispatch
  carrying no PLAN task, which may omit `task_verify` or report it `n/a` and still return PASS)
```

The dev-ops opener "(asymmetric to `suite`: …)" was deliberately NOT imported: the eng-devs `suite`
enum is `pass|fail` with no `n/a`, so there is no asymmetry to name and the clause would be false
here — importing it would inject a wrong claim into a NORMATIVE bullet, the defect class being
fixed. What transferred: the `n/a`-means-refused-or-never-ran gloss, the
rejected-alongside-`VERDICT: PASS` rule (one clause covering both `fail` and `n/a`, since the
eng-devs rule rejects both), and dev-ops' own phrasing "a dispatch carrying no PLAN task".

**Verification caveat, stated first: all seven commands pass on the UNEDITED file.** They are a
regression guard, not proof the fix landed — proof is the bullet text above. Two exit non-zero on
success by design (`grep -c` prints `0`, exits `1`, which is the pass condition for `no-task`).

**Line-anchor drift — advisory, NOT edited.** The insert shifts everything below `:1055` down 4
lines, so the dev-ops bullet moved `:1062-1068` → `:1066-1072`. Every surviving citation of the old
anchors is a historical feature record (`PLAN.md:995,997,1025,1030,1126`, four `runs/*/digest.md`,
`notes/receipt-*`, `notes/research-*`, the observations entry at the top of this file,
`.harness/notes/grilling-perf-batch-1-2026-08-04.md:87`, `.harness/logs/2026-08-04.md:58`) — records
of what was true when written, not rewritten. **No file under `docs/` or `.claude/` cites a shifted
anchor**: `grep -rn 'SPEC\.md.*:10[5-9][0-9]' docs/ .claude/ --include='*.md'` returned nothing.

**Gap left open on purpose (out of this dispatch's three clauses).** With `task: none`,
`validate-digest.py:587-600` rejects ANY non-placeholder `task_verify` — `pass` included. The enum
`pass|fail|n/a` plus a `task: none` exception still lets a dev write `task: none` +
`task_verify: pass` and be rejected by a conditional no surface states. The new bullet's exposure
here is IDENTICAL to dev-ops', so no divergence was introduced; a fourth clause was not added.

**Diff shape:** one hunk, `@@ -1052,7 +1052,11 @@`, replacing only the eng-devs line's tail. No
dev-ops context line appears as `+`/`-`. `git diff --stat -- docs/harness/SPEC.md` = 1 file,
5 insertions, 1 deletion.

- 2026-08-04 (S-01, SPEC §8.1 dev-ops bullet): the bullet said `n/a` alone "is REJECTED alongside
  `VERDICT: PASS`" while `GATE_FAIL_VALUES` also carries `"dev-ops": {"task_verify": "fail"}`
  (`.claude/skills/harness/bin/validate-digest.py:110`). Extended the parenthetical to "both `fail`
  and `n/a` are REJECTED" — one idea added; the `asymmetric to \`suite\`` opener, the `task: none`
  exception sentence and the "never the honest answer" sentence are untouched.
  **Wrap trap (new, generalizes G-04's shape):** the change detector is `grep -c`, which counts
  PHYSICAL lines, and SPEC.md is hard-wrapped — the pre-edit count was 0 because `fail` sat on
  1068 and `REJECTED` on 1069, not because the idea was absent. The fix was to re-flow the two
  lines so `fail ... REJECTED ... VERDICT: PASS` lands on ONE line (now 1069). Rule: when a
  line-counting detector must go >=1, place the token pair on a single physical line and re-run
  the grep before assuming the prose is wrong.
  **Observed:** detector 1 (dev-ops fail/REJECTED) = 1, exit 0 (was 0); dev-ops `task_verify` = 2;
  eng-devs fail/REJECTED = 1 (UNCHANGED); `no-task` = 0 (grep exit 1, no match); index
  `gen-decisions-index.py --stdout | diff` exit 0; `check-docs.sh` exit 0, 45 patterns across
  186 files; `run-unit-tests.sh` exit 0, ALL PASSED. No DECISIONS.md propagation entry was
  demanded, so the pre-authorized FAIL path was not taken.
  **Diff shape:** `git diff -U0 -- docs/harness/SPEC.md` shows TWO hunks / 7 insertions /
  3 deletions, but only the second (`@@ -1064,2 +1068,2 @@`, 2 in / 2 out) is mine — the first
  (`@@ -1055 +1055,5 @@`, the eng-devs bullet) was already in the uncommitted working tree at my
  spawn, proven by the pre-edit detector on the eng-devs range reading 1, not 0. Lesson: on a
  dirty tree, `git diff --stat` alone does NOT bound your own edit; read the hunk headers.
  Post-edit widths 1066-1072 = 80/76/96/98/88/77/57, inside the file's observed max of 100;
  lines 1070-1072 were not re-flowed.
  **Gap flagged, not edited:** `run-unit-tests.sh` asserts `dev-ops suite: fail + PASS stays
  accepted` (D-03) while the same pair is rejected for an eng dev. §8.1's dev-ops bullet says only
  "(TDD-exempt work reports `n/a`)" and never states that its `suite` is ungated, so a dev-ops
  author reasoning by analogy from the eng-devs bullet is misled. Outside this dispatch's one
  authorized edit.
