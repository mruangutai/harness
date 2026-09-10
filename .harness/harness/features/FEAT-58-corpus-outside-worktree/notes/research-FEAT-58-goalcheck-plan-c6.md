# Goal-check — cycle 6, post-fix — FEAT-58-corpus-outside-worktree

**Does this plan deliver the operator's stated intent? YES.** All ten axes answered affirmatively
from the artifact text. The five things done means are DELIVERED by production tasks, not merely
tested for; the seven binding items each hold their own REQ and at least one automated SC; the three
weight-bearing proofs and the two-route D-2 denial survived cycle 6 undisturbed; all four cycle-6
answers landed WHOLE, Q4 with its four constraints verified separately.

**Two med defects want one-clause fixes before signature, both inside N-06 PART 1, and neither
re-opens a settled ruling.** Nothing was dropped or silently demoted from the ledger.

## Findings

| id | sev | lands on | the concrete change |
|---|---|---|---|
| GC6-01 | med | `plan.yaml:1946-1949` (N-06 PART 1); mirrored in `BRIEF.md:219-222` SC-06 | Gate on the MISSING side always; gate on the UNEXPECTED side only INSIDE a linked worktree. Report unexpected names non-gating elsewhere, in the same message |
| GC6-02 | med | `plan.yaml:1918-1920` (N-06 PART 1 derivation) | Spell the pathspec `git ls-files -- '.harness/*/features/*'`, or list the resolved corpus directory. Add one clause asserting the derivation over the real index is non-empty |
| GC6-03 | low | `BRIEF.md:395` | Replace the propagated stale `bash-write-guard.sh:512` anchor with the verified door range. The DoD note's copy is REPORTED only — operator's file |
| GC6-04 | low | `plan.yaml:23-25` (`lanes:`) | `notes/migration-record.md`, "written by the tier that runs the migration", is the last vestige of the struck convergence task; no task produces it. `lanes:` is unwritable — one clarifying sentence in D-07, or leave it recorded here |

**GC6-01, and it is the axis-9 answer.** PART 1 refuses on set INEQUALITY in both directions. Inside
a worktree the unexpected side IS the D-1 violation and must gate. At the owner root and in a fresh
clone the unexpected side is ordinary working state — a feature directory on disk that is not yet in
the index — so the repository's canonical pre-commit gate (`check-state.sh`, its own header `:24`)
exits 2 before any invariant, ahead of the very commit that is its remedy. That is the exit-8
deadlock class the operator ruled on at cycle 6 (PL-02), and it is the standing-red-through-nobody's-
edit shape N-12 argues against by name at `plan.yaml:2763-2768`. Measured in the reviewed worktree:
the two sets AGREE today, 88 on disk and 88 first-level names from the index, so the risk is latent,
not live. N-13 PART 1 clause 4 does print the missing and unexpected NAMES, so the test's own red is
diagnosable — the defect is the shipped gate's verdict, not the test's attribution.

**GC6-02, measured at git 2.50.1 in the worktree.** `git ls-files -- '.harness/*/features'` → **0**
paths; `'.harness/*/features/'` → **0**; `'.harness/*/features/*'` → **3360**; literal
`.harness/harness/features` → **3360**. `intent:` is the literal dispatch prompt, so an executor
copying the spelled pathspec builds an EMPTY expected set. The failure is loud rather than silent —
N-13 PART 1 clause 1 reddens on it — which is why this is med. The operator's Q1 ruling is untouched:
its substance (first-level directory names from `git ls-files`, used twice) is right; only the
pathspec spelling is unexecutable. N-06 PART 4's canned-index unit case cannot catch it.

## The ten axes

1. **Five things done means — all DELIVERED.** (1) one directory: REQ-01/SC-01, delivered by D-08's
   derivation + N-02 check 1 + N-04's `post-checkout`. (2) prior features on disk: REQ-02/SC-02,
   delivered by N-02 checks 3/4a (the link) + N-03 PART 1 (`.gitignore`). (3) active feature only:
   REQ-03/SC-04-06, delivered by N-06 PART 1's edit at `check-state.sh:118-120`. (4) no shared
   branch: REQ-04/SC-07, delivered by N-07 PART 1 predicate + PART 2 consumer swap. (5) clone and CI
   as today: REQ-05/SC-12, delivered by N-02's scope guard (`plan.yaml:1418-1430`), graded by N-09.
2. **Seven binding items — clean, read from the REQ TEXT** (`BRIEF.md:50-68`), not the table. D-1→
   REQ-01, D-2→REQ-02, D-3→REQ-03, D-4→REQ-04, D-5→REQ-05, M-1→REQ-06, M-2→REQ-07; each REQ distinct,
   none folded, none deferred. All fifteen criteria are `verify: automated evidence: integration` —
   nothing graded by inspection.
3. **The three that carry the weight — each CAN report RED, from the task text.** (a) merge
   regression, `plan.yaml:1657-1682`: step 1 asserts a non-zero S count first (anti-vacuity), step 3
   asserts porcelain 0 and per-path S membership, clause 4 keeps the pre-change reproduction in file
   and asserts the two runs DIFFER; "returns BLOCKED, never weakened" at `:1681-1682`. (b)
   equivalence, `:2091-2111`: exit status EXCLUDED at `:2093-2095`, clause 4 perturbs a record and
   asserts inequality. (c) no-repair, `:1514-1532`: own file, BEFORE/AFTER manifest plus skip-bit set
   per break, `.git/info/sparse-checkout` included, RED PROOF by routing one break through `--repair`.
4. **Two-route D-2 denial — intact.** `plan.yaml:1572-1584` (Write/Edit via `check-domain.sh` on
   stdin, Bash via `bash-write-guard.sh:855`, each through its registered entrypoint) with the paired
   POSITIVE control at `:1585-1586`. Confirmed undisturbed by D-14 at `:514-516`.
5. **Positive controls — mandatory and per path.** N-05 GROUP 2 `:1785-1823`: per-path named
   assertions, `.agents`/`.claude` both spellings plus realpath equality, the three non-features
   `.harness` subtrees each its own clause, `.harness/corpus` as islink + realpath, exit status
   forbidden at `:1787`. `REQUIRED_PATHS` at `:1283-1301`. Derivation proven DERIVED by GROUP 3
   `:1832-1855`, three new tracked things and clause 4's no-source-edit assertion.
6. **Cycle-6 answers — all four landed WHOLE.** Q4/PL-04: (i) read-only, `:2805-2807` + D-16
   `:583-585`; (ii) disposable probe only, `:2841-2850`, teardown from the owner root in a `finally`,
   never `--force`; (iii) addition not substitution, `:2803-2804` + D-11 `:372-378`; (iv) cost rule
   intact — D-11's synthetic-`git init` rule unamended, N-01's fixture rule and its <100-tracked-file
   bound unchanged. Q1/PL-01: one derivation used twice `:1916-1932`; NO `feature.json` restriction
   anywhere (grepped over every task) and NO suppression — `:1939-1942` states the ten are #1640 and
   expected to be reported. Q2/PL-02: D-12 `:392-405` and N-06 PART 3 `:2002-2018` gate on 3-7 only,
   exit 8 reported and non-gating, `--verify` still reports the dirty tree. Q3/PL-03: N-10 PART 7(c)
   `:2622-2636` asserts the printed output is NOT a deny payload, forbids exit status, carries N-07
   PART 4(b)'s warning; the convention is D-17 `:613-633`, a decision and not a task comment.
7. **Coverage — nothing lost.** Chain re-read at source: 42 → 41 (c5, one removal NAMED, the hardlink
   row) → 41 (N-11 fold, one owner moved, none removed) → **45** (c6, four added). The four added rows
   exist in the plan: N-13 PART 1, N-13 PART 2 clauses 3 and 4, N-06 PART 3 case (d). The evidence-form
   change is visible — N-10 PART 7(c), `exit 0` → deny-payload absence
   (`notes/research-FEAT-58-apply-c6.md:60-61`, and in the task text at `:2626-2633`). Earlier
   demotions still visible in the evidence column: `BRIEF.md:333-342` names both, D-13 `:444-451`.
   **No dropped or silently-demoted assertion.**
8. **Shape — twelve coherent surfaces.** No `change_type` demands a kind it cannot satisfy: the three
   `cross_module` tasks (N-02, N-06, N-10) and both `feature` tasks each carry a `tests/unit/` file in
   `files:`; N-09 is `scaffolding` with zero production files (VL-05's remedy, `:2320-2325`). **N-13 is
   a coherent surface, not a bag of leftovers**: one file, one subject — the shipped audit read against
   the real tree — both parts graded by SC-16.
9. **N-13's new risk — graded honestly.** The task DOES distinguish an audit defect from a legitimately
   uncommitted directory: clause 4 prints the missing and unexpected NAMES (`:2827-2829`). What it does
   NOT do is stop the shipped gate refusing in that state — GC6-01. Beyond that, N-13 does not become
   the standing-red shape: no census figure is a passing condition anywhere (`:2808-2810`), the
   non-vacuity clause is a floor (>70) and never an equality, the probe id is chosen at run time with
   an announced SKIP when none is free (`:2880-2885`), and PART 1 is the same audit the pre-commit gate
   already runs at the owner root.
10. **What the DoD kills — nothing crept back.** Grepped: no migration/convergence task among the
    twelve; no corpus-root anchor or corpus API (D-09 `:36-42` records the rejection); no fifteen-reader
    ledger (only D-09's record of why it is empty); no reflink/clonefile mechanism (Non-goals
    `BRIEF.md:346-349`, and the only `clonefile` mention is N-01's exclusion rationale); no byte-count
    criterion — N-01's `--self-check` asserts the absence of `du`/byte/size idioms and the three
    sanctioned measurement modes (`:1341-1352`); no incremental sweep cache (D-01 `:87-99` deletes the
    index and forbids a cache; N-07 `:2135-2138` repeats it). The single residue is GC6-04.

## Pointer notes, no change asked of the operator

- The dispatch cites SC-09's operator text at `BRIEF.md:227-234`; it is at **`:234-247`**, the amended
  clause at **`:241-246`**. Verified matching `notes/answers-operator-c6.md:55-60` clause for clause,
  and the only `-` line the BRIEF diff carries near it is a coverage-table cell — measured on the diff,
  not taken from the apply note.
- The DoD note's `bash-write-guard.sh:512` anchor is STALE (door at `:611-741`). Reported, never edited.
  N-13 `:2846` and the apply note say `:624-741`, a subset of the verified range — re-derive instruction
  is present at the site, so this is not a finding.
- The ten record-less feature directories are #1640 and are NOT this feature's defect; the audit
  reporting them is correct behaviour. Not graded as a fault here.
