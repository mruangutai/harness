# Apply — cycle 6 operator rulings — FEAT-58-corpus-outside-worktree

**All four rulings landed, none declined. Plan is +1 task, +2 decisions, +1 criterion; ledger
41 → 45 with nothing removed. The three weight-bearing proofs and the two-route D-2 denial are
verified undisturbed at source.** `status: plan`, `approval.status: pending`, BRIEF `## Approval`
untouched, SC-09's amended clause byte-identical (the only `-` line the BRIEF diff carries near it
is a coverage-table cell).

## Per finding

| finding | verdict | remedy chosen | landed at |
|---|---|---|---|
| PL-04 (Q4, the CLASS) | landed | new real-data task on N-08's model + the decision that records why | `N-13`, `D-16`, `D-11` extended, `SC-16` |
| PL-01 (Q1) | landed | remedy (a): ONE `git ls-files` derivation over `.harness/*/features/`, used twice | `N-06` PART 1 |
| PL-02 (Q2) | landed | preflight gates on structural exits 3–7 only; exit 8 reported, non-gating | `D-12` choice + because, `N-06` PART 3 (+ new test case (d)) |
| PL-03 (Q3) | landed | assert the payload is not a `permissionDecision: deny`; strike "exit 0" | `N-10` PART 7 (c), `D-17` |
| VL-07 pointer | landed | prefix corrected to `.harness/notes/dod-worktree-corpus-2026-09-10.md:136-143` | `panel.findings[VL-07].resolved_by` |

`panel` refreshed: PL-01..PL-04 now carry `disposition: resolved …` + `resolved_by`, and `note`
gained one appended cycle-6 paragraph. **Every other loaded value in the block is unchanged** —
proven field-by-field, not by eye: the transform diffed old against new and reported exactly
`PL-01..PL-04 {disposition, resolved_by}`, `VL-07 {resolved_by}`, `panel {note}`. Severities,
summaries, `summary_caveat`, `fix_order`, readers, `lands_on`, `prior_cycle` all byte-identical.

## Remedy (b), rejected — and this is the feature's own premise

Restricting **both** sets to `feature.json`-carrying directories would make the audit silently
ignore ten directories that exist, are tracked and hold real recorded history — a narrowing that
reports clean over a subset, which is the exact defect this feature exists to remove. Recorded in
`N-06` PART 1 so a later reader cannot re-propose it as a simplification. The ten are filed as
**#1640**, are NOT this feature's to fix, and this audit is expected to REPORT them accurately
meanwhile: no suppression, no allow-list, no exemption.

## The two executability questions the lead asked me to settle

1. **No pinned census number, anywhere.** `N-13` and `SC-16` assert the ABSENCE of an
   expected-versus-reached mismatch at the reviewed commit plus a non-vacuity floor (reached > 70),
   never `89` or `79`. Precedent followed: SC-11's host baseline is already labelled measured and
   NOT a fixture expectation.
2. **A permitted route for the disposable dirty tree EXISTS, and I verified it at source.** The
   DoD's `bash-write-guard.sh:512` anchor has drifted; the creation door is now at
   `bash-write-guard.sh:624-741`. It refuses a relative destination, a destination it cannot parse,
   a destination outside `WORKTREES_SEGMENT` (`.claude/worktrees`), and any `--force`. It PERMITS
   an absolute path under `<owner_root>/.claude/worktrees/harness/`. `N-13` therefore specifies
   `git worktree add --detach <ABSOLUTE probe path> HEAD` — detached, so git's one-branch-one-tree
   rule is never engaged — for a probe id chosen at run time (a corpus feature id matching
   `feature-worktree.py:46`'s `_ID_RE` whose worktree path is free), which is what `worktree-state.py`'s
   own scope guard requires for the preflight to engage at all. Teardown runs from a `finally`,
   from the OWNER ROOT and never from inside the probe, never with `--force`.

## Ledger — 41 → 45, four added, **none removed**

1. real owner root: no expected-versus-reached mismatch refusal, run proceeds past the choke point,
   reached > 70 → `tests/integration/test-check-state-realdata.py` (N-13 PART 1)
2. dirty disposable worktree: exit 8 reported, invariants still run → same file (N-13 PART 2)
3. same probe, structural break (skip-bits cleared, exit 4): refuses with no invariant line — the
   positive control without which row 2 proves nothing → same file (N-13 PART 2)
4. fixture-level twin of row 2: dirty tree does not gate → `tests/integration/test-check-state-verify-gate.py` case (d) (N-06 PART 3)

One row changed EVIDENCE FORM without moving: N-10 PART 7 (c) now asserts the deny payload's
absence instead of `exit 0`.

## Counts

tasks **12** (`N-01 … N-13`, `N-11` retired, id left as a gap) · decisions **17** (`D-16`, `D-17`
added; `D-15` was the prior last) · criteria **15** (`SC-16` added; `SC-15` struck and its id left
as a gap). `check-plan-routes.py` on this plan: **0 violations**; every DEVIATION line is the
DEC-174 carve-out working (D-07).

## Coverage — verbatim, as it now stands in `BRIEF.md`

| Item | What | REQ | SC |
|---|---|---|---|
| **D-1 (DoD)** | Exactly one feature directory materialised | REQ-01 | SC-01 |
| **D-2 (DoD)** | Every other feature readable on disk | REQ-02 | SC-01, SC-02 |
| **D-3 (DoD)** | Audit: active feature only, no corpus, refuses | REQ-03 | SC-04, SC-05, SC-06, SC-14, SC-16 |
| **D-4 (DoD)** | No two features claim one branch | REQ-04 | SC-07 |
| **D-5 (DoD)** | Fresh clone and CI unchanged | REQ-05 | SC-12 |
| **M-1 (DoD)** | One idempotent `--verify`/`--repair`, verify never repairs, and a named gate calls `--verify` | REQ-06 | SC-09, SC-10, SC-16 |
| **M-2 (DoD)** | It runs from `post-checkout`, `post-merge`, `post-rewrite` | REQ-07 | SC-11 |
| — | Corpus path gitignored; writes through it refused | REQ-08 | SC-02, SC-03 |
| — | The live FEAT-02 / FEAT-03 collision, on real data | REQ-09 | SC-08 |
| — | Nothing altered outside the active feature | REQ-10 | SC-13 |

Every binding item still carries its own REQ and at least one SC; two rows gained `SC-16` and no
row lost anything.

## Undisturbed — re-read at source AFTER the edits, at these ranges

- merge regression, `MUST FAIL TODAY` verbatim + host baseline explicitly not a fixture
  expectation — `plan.yaml:1657-1666`
- equivalence, **exit status EXCLUDED** from the comparison — `plan.yaml:2091-2095`
- `--verify`-does-not-repair in its own file + the RED PROOF clause — `plan.yaml:1514-1532`
- D-2 two-**route** denial (Write/Edit via `check-domain.sh`, Bash via `bash-write-guard.sh:855`)
  **and its paired positive control** — `plan.yaml:1572-1586` (was `:1252-1258`; the range moved
  because earlier tasks grew, the text did not change)

## Open

- **Q1, non-blocking.** `N-13` PART 1's owner-root clause can legitimately red if a feature
  directory exists on disk carrying only uncommitted content at the moment of the run — that is the
  audit working, not a defect, and the clause is specified to print the missing/unexpected NAMES so
  a reader can tell the two apart. Worth watching on the first real run.
- **Q2, non-blocking.** The DoD note's own `bash-write-guard.sh:512` anchor is stale (creation door
  now `:624-741`). The note is the operator's; not edited here.
