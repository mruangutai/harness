# Fix segment — cycle 6 goal-check findings — FEAT-58-corpus-outside-worktree

**All four graded items LANDED, none declined. Nothing re-adjudicated, nothing else touched.**
`plan.yaml` written only through `plan-merge.py amend` (two invocations, one field each);
`status: plan`, `approval.status: pending`, BRIEF `## Approval` `status: pending`, the `lanes:`
block and the `panel` block untouched. `check-plan-routes.py plan.yaml` → **0 violations, exit 0**
(12 TASK `DEVIATION` lines, the DEC-174 carve-out working; one `MANIFEST` line, uncounted).

## What landed

| id | where it now reads | the change |
|---|---|---|
| GC6-02 | `plan.yaml:1922-1938` (N-06 `intent`, PART 1) | pathspec re-spelled `.harness/*/features/*` with the three measurements inline, reduction rule verbatim as it stood; **new clause** `:1932-1938` making a non-empty derivation over the real index a passing condition in its own right — an empty derivation is a refusal, never a silent pass, and it is a floor, not a census figure |
| GC6-01 | `plan.yaml:1961-1978` (N-06 `intent`, PART 1) + `BRIEF.md:219-226` (SC-06) | gate on the MISSING side always; gate on the UNEXPECTED side only inside a linked worktree (`harness_boundary.worktree_owner(root)`, the predicate PART 1 already uses); elsewhere unexpected names are REPORTED in the same message and NON-GATING. Count form `reached N of M expected feature directories`, sorted missing + unexpected names, remedy tail `Fix: <act> or Use <command>`, exit 2 before any downstream site when it gates, and the unchanged-when-equal clause all kept |
| GC6-03 | `BRIEF.md:400` | creation-door anchor `bash-write-guard.sh:512` → `:611-741`; no `:512` occurrence survives in the BRIEF |
| GC6-04 | `plan.yaml:278-281` (D-07 `choice`) | one sentence: `lanes:` is frozen and unwritable, its `migration-record.md` row is a vestige of the migration task the DoD struck, no task produces that file, D-07's table is the live record. `because:` and `dec:` untouched; the lane table is not restated |

**The DoD note is byte-unchanged** — `git diff --stat` names two files only, and
`.harness/notes/dod-worktree-corpus-2026-09-10.md` is not one of them. Its stale `:512` copy is
**reported upward, never fixed by an agent**; it is the operator's file.

## Measurements I took (do not re-derive)

- Pathspec, git 2.50.1, worktree root, `git ls-files -- <pathspec> | wc -l`:
  `.harness/*/features` → **0**, `.harness/*/features/` → **0**, `.harness/*/features/*` → **3360**.
  The dispatch quoted 3383; the reviewed worktree measures **3360**, which is also the goal-check's
  figure. Only non-emptiness is load-bearing, and the intent asserts non-emptiness, never a count.
- Creation door confirmed live in `:611-741` (`_refuse_worktree` on an absent and on a relative
  destination, then the realpath comparison block) before rewriting the BRIEF anchor.

## The undisturbed set — checked, not claimed

`plan.yaml` was 2887 lines and is now **2915**. The two amends account for **exactly +28**
(N-06 `intent` +24: 6 lines → 17 and 5 lines → 18; D-07 `choice` +4). Every protected region sits at
its predicted offset with its content intact, which is what rules out any other edit:

- no-repair proof `:1514-1532` → **`:1518-1536`** (own file `test-worktree-state-norepair.py`,
  BEFORE/AFTER, `RED PROOF` routing one break through `--repair`).
- two-route D-2 denial `:1572-1586` → **`:1576-1590`** ("(c) THE REFUSAL, on BOTH GOVERNED WRITE
  ROUTES, per D-02" through "PAIRED POSITIVE CONTROL, not optional").
- merge regression `:1657-1682` → **`:1661-1686`** ("IT MUST FAIL TODAY" … "Assert the two runs
  DIFFER" … "returns BLOCKED").
- equivalence `:2091-2111` → **`:2119-2139`** ("EXIT 0 IS EXPLICITLY NOT PROOF … exit status is
  EXCLUDED").
- SC-09's amended clause shifted +5 by my SC-06 edit and is byte-identical, now **`BRIEF.md:239-252`**
  (amended clause proper `:246-251`); `structural exits only (3 through 7)` present verbatim.
- Cycle-6 rulings: Q1 substance (one derivation used twice, no `feature.json` restriction, no
  suppression, remedy (b) rejected, #1640 reported) untouched word for word around my re-spelling;
  Q2 exit-8 reported/non-gating in both D-12 and SC-09; Q3 deny-payload-absence in N-10 PART 7(c);
  Q4's four constraints in N-13/D-11/D-16.
- Structure: 12 tasks (`N-11` still the deliberate gap), 17 decisions, 5 `lanes:` rows with the
  `migration-record.md` row still present exactly as it was.

## Ledger — **45**, unchanged

Measured by re-reading the chain at source rather than trusting a total: 36 (c3 in) → 42 → 41
(c5, one named removal) → 41 (N-11 fold, one owner moved) → **45** (c6, four added). The four c6
rows are present in the plan text — N-13 PART 1, N-13 PART 2 (two clauses), N-06 PART 3 case (d) —
and the BRIEF's ledger paragraph still reads `41 → 45`. **No row of this segment's four edits is a
ledger row**: two are wording inside one task's `intent`, one is a decision note, one is an anchor.
Nothing added, nothing removed, nothing demoted.

## Open, for the tier above — not edited here

- `.harness/notes/dod-worktree-corpus-2026-09-10.md:145` still says `bash-write-guard.sh:512`.
  Operator's file; the BRIEF no longer propagates it.
- N-13 `:2846` and `notes/research-FEAT-58-apply-c6.md` cite the door as `:624-741`, a subset of the
  verified `:611-741` (the comment block `:611-613` carries the a29ad06 measurement). Both carry a
  re-derive instruction at the site, so this is a pointer note, not a finding.
- The `lanes:` `migration-record.md` row remains structurally present because no write route can
  remove it. D-07 now records why; deleting it would need a route that does not exist.
