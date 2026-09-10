# Fold — N-11 retired into N-10 — FEAT-58-corpus-outside-worktree

**Both rulings applied. Tasks 12 → 11 (`N-01 … N-12`, `N-11` a deliberate gap), decisions 15
unchanged, criteria 14 unchanged, assertion ledger 41 with ONE row's owner moved and none removed.**
`plan.yaml` written only through `plan-merge.py` (`amend` ×17 fields, `delete-items` ×1);
`panel`, `lanes`, `approval` (`pending`) and `status: plan` untouched; `BRIEF.md ## Approval`
untouched. `check-plan-routes.py plan.yaml` → **0 violations, exit 0** (11 TASK `DEVIATION` lines,
the DEC-174 carve-out working; the `MANIFEST` line is the header, not a finding).

## Ruling A — the extra strike is now recorded, not undone

`D-14.choice` opens "THE HARDLINK HALF IS STRUCK, AND THE STRIKE REACHES BOTH OF ITS GATES" and
names the `check-domain.sh:1907-1922` change (measured glob `:1916`) as out. `D-14.because` carries
the three links: (i) that gate entered scope in the scan-site design as the hardlink hole and
nothing else, so it falls with SC-15; (ii) keeping it leaves a widened guard with **no criterion and
no test** whose only failure path is the uncaught `corpus_root()` raise VL-01 measured — exit 1,
declared NON-blocking by `check-domain.sh:14`, so the write proceeds; (iii) the only fix for that
path is the error conversion Q1 forbids. `D-14.choice` also states that **no requirement loses
coverage**: REQ-08 rests on the surviving two-**route** denial (D-02's Write/Edit route through
`check-domain.sh` plus the Bash route through `bash-write-guard.sh:855`), carried by **N-03** and
graded by **SC-02 and SC-03**. My cycle-5 open question is closed in my favour.

`BRIEF.md` did **need** the extension — its strike paragraph carried the three original reasons but
never said the `:1916` gate came out, and credited REQ-08 to SC-02/SC-03 without naming the task.
Both added (`BRIEF.md:118-128`); the three original reasons are unchanged.

## Ruling B — the fold

`N-10` now carries `branch-create-gate.sh` and `tests/integration/test-corpus-denials.py`
(`files:` 9 entries), a literal `|` `verify:` running all three test files (each command carried
verbatim from its source task, `&&`-joined), and the surviving N-11 work as PART 6 and PART 7.
`change_type: cross_module` is now **honest**: N-10 holds `tests/unit/test-feature-corpus.py` and
two integration files, so the matrix's `unit` kind is satisfied by a test that exists — the exact
gap that made the label dishonest on the post-strike N-11.

Old → new part mapping (recorded citations name the pre-c5 lettering):

| was | is now |
|---|---|
| N-11 PART 1 — branch-gate widening, shape (c) only, no-refusal-arm + its comment | **N-10 PART 6** |
| N-11 PART 2 — the marker, plus the POSIX-sh/`python3`/NAMES-not-import rationale | **N-10 PART 3** (marker section) + PART 6's closing sentence |
| N-11 PART 3 (c)/(d) — the two denial-gate cases | **N-10 PART 7 (c)/(d)**, lettering kept |
| N-11 **PART 5 (c)/(d)** as the panel cited it | **N-10 PART 7 (c)/(d)** |
| N-11 PART 4, PART 5 (a)/(b) | struck at cycle 5 (D-14); not moved |

**The trap survived the move.** PART 7 (c) asserts `branch-create-gate.sh` still **ALLOWS** a legal
flow Y present at the owner root and absent from the worktree, verbatim, **before** (d) and with the
stated reason ("this site's narrowing does not fail OPEN, it fails CLOSED WRONGLY"), its pinned
pre-change reproduction (pre-change it DENIES) intact. Verified programmatically: ALLOW's offset
precedes DENY's in the stored intent.

**Marker arithmetic re-derived.** N-10 marks **SEVEN lines across FIVE scripts** (was six across
four): `board_lifecycle.py` 1, `check-plan-routes.py` 2, `layout_migration.py` 2,
`validate-feature-json.py` 1, `branch-create-gate.sh` 1. Census total unchanged at **30** =
N-06 21 (`check-state.sh`) + 1 (`check-domain.sh`, comment only) + N-07 1 (`merge-gate.py`) + N-10 7.
N-12's per-file counts are untouched; only its file→task attribution moved.

`N-11` deleted with the mandated reason string; **no surviving id renumbered**. `depends_on` edges
re-derived: N-12 `[N-06, N-07, N-10]`, N-09 loses N-11; no dangling edge remains (checked over all
11 tasks). N-10's `depends_on` stays `[N-01]` — the struck `check-domain.sh` half was the only
reason a serialisation edge to N-06 was ever needed.

## Every `N-11` string accounted for — 23 in `plan.yaml`, 2 in `BRIEF.md`

- **Rewritten to the new owner (17):** `D-02.because` 1 · `D-07.choice` 2 (the
  `branch-create-gate.sh` row → N-10; the `check-domain.sh` row's clause) · `D-14.choice` 6 (the
  citation mapping) · `N-06.intent` 3 · `N-10.intent` 3 · `N-12.intent` 2.
- **Deliberately preserved as history, with the new owner annotated in `D-14.choice` rather than in
  their own words (6):** `panel.findings[0]` (VL-01) `lands_on` 1 + `summary` 3, and
  `panel.prior_cycle.findings[0]` (F-01) `evidence` 2. The dispatch forbids touching `panel:`, and
  a reporter's wording is not rewritten; `D-14.choice` carries the mapping they are read through.
- `BRIEF.md` 2, both new and both describing the retirement (`:134`, `:141`).

## Ledger — 41, one row moved

**Moved: `branch-gate allow + deny (N-11)` → N-10** (PART 7 (c)/(d)). It is a cycle-3 addition
(`notes/research-FEAT-58-apply-batch-c3.md:55-57`). Checked rather than assumed: the base ledger in
`runs/consolidate-eng/digest.md` contains **no** `N-11` string and no branch-gate or denial row (its
landing column carries engineering task numbers, not plan ids), and the only other N-11-owned
addition, `hardlink deny + positive control (N-11)`, was removed by name at cycle 5. **No other row
changed owner. Total 41.**

## Housekeeping

`BRIEF.md`'s coverage table needed **no change** — the fold is task-level; no REQ or SC changed row,
and every binding item still sits on its own REQ with at least one SC. The task-count reference now
reads eleven tasks with `N-11` retired (`:133-135`), and the ledger paragraph points at this note.

The table as it stands, verbatim (`BRIEF.md:88-99`) — the dispatch asked for it in the DIGEST, and
`validate-digest.py`'s pm schema is a closed key set, so it lands here:

| Item | What | REQ | SC |
|---|---|---|---|
| **D-1 (DoD)** | Exactly one feature directory materialised | REQ-01 | SC-01 |
| **D-2 (DoD)** | Every other feature readable on disk | REQ-02 | SC-01, SC-02 |
| **D-3 (DoD)** | Audit: active feature only, no corpus, refuses | REQ-03 | SC-04, SC-05, SC-06, SC-14 |
| **D-4 (DoD)** | No two features claim one branch | REQ-04 | SC-07 |
| **D-5 (DoD)** | Fresh clone and CI unchanged | REQ-05 | SC-12 |
| **M-1 (DoD)** | One idempotent `--verify`/`--repair`, verify never repairs, and a named gate calls `--verify` | REQ-06 | SC-09, SC-10 |
| **M-2 (DoD)** | It runs from `post-checkout`, `post-merge`, `post-rewrite` | REQ-07 | SC-11 |
| — | Corpus path gitignored; writes through it refused | REQ-08 | SC-02, SC-03 |
| — | The live `FEAT-02` / `FEAT-03` collision, on real data | REQ-09 | SC-08 |
| — | Nothing altered outside the active feature | REQ-10 | SC-13 |

## Open questions

None blocking. One advisory: `plan.yaml`'s frozen VL-01 and F-01 panel entries will read as citing a
task that does not exist until a reader reaches `D-14.choice`'s mapping — deliberate under the
never-falsify rule, and the reason the mapping is in a live decision rather than in a note.
