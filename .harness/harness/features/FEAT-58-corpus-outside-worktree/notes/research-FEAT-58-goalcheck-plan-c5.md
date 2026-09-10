# Goal-check — post-fix grade against the operator's stated intent — cycle 5

**Does this plan deliver the operator's stated intent? YES.** All ten axes PASS. The cycle-5 answers
landed whole, the strike removed only what it was meant to, and **D-2 (DoD) enforcement survived the
Q6 strike intact** — the load-bearing question of this run. Three findings, all `low`/`med`, none
gating: they are record-accuracy defects in the `panel` block and in one superseded note, not defects
in what the plan builds. This grade is read-only; `plan.yaml` and `BRIEF.md` are untouched.

Supersedes the `-c3` grade (GC-01 high, GC-02 med), whose remedies landed. Graded against the
AMENDED DoD note (`.harness/notes/dod-worktree-corpus-2026-09-10.md:136-143`), the shape rule,
`answers-operator-c3.md` and `answers-operator-c5.md` — not against `BRIEF.md`, which is itself under
grade.

## Axis verdicts

**1. The five things done means — PASS. All five are DELIVERED, not merely tested.** (1) one feature
dir: production cone in `worktree-state.py` check 1 / `--repair` (`plan.yaml:1111-1131`), graded
N-05. (2) corpus readable: the symlink is CREATED by N-02 check 3 repair (`:1137-1138`) + `.gitignore`
(N-03 PART 1, `:1227-1231`) — a production mechanism, D-09. (3) audit narrowed: N-06 PART 1 edits
`check-state.sh:118-120` (`:1592-1608`); the four genuinely-cross-feature sites are WIDENED, not
narrowed, by N-10 PART 2 (`:2165-2183`). (4) branch uniqueness: N-07 PART 1/2 production predicate +
`merge-gate.py` consumer swap (`:1766-1813`). (5) fresh clone/CI: the production scope guard at
`:1094-1106`, three conditions, exits 0 changing nothing; N-09 grades it.

**2. The seven binding items — PASS. Seven REQs, seven separate, none merged, none deferred, none
graded by inspection.** Read from REQ TEXT, not the coverage table: D-1→REQ-01 (`BRIEF.md:50-51`)/SC-01;
D-2→REQ-02 (`:52-54`)/SC-01+SC-02; D-3→REQ-03 (`:55-57`)/SC-04,05,06,14; D-4→REQ-04 (`:58-59`)/SC-07;
D-5→REQ-05 (`:60-62`)/SC-12; M-1→REQ-06 (`:63-64`)/SC-09,10; M-2→REQ-07 (`:65-68`)/SC-11. **M-1 and M-2
are still first-class**: each holds its own REQ whose text is the mechanism itself (`--verify` reports
and never repairs; runs from all three hooks and never breaks the git op it rides on), each graded by
`verify: automated evidence: integration`. Every one of the fourteen criteria is `automated`; not one
binding item falls to inspection.

**3. The three that carry the weight — PASS. All three can report RED.**
(a) *Merge regression* — N-04 PART 2 (`:1333-1358`). Can go red: step 1 asserts the pre-merge S count
non-zero, so it cannot be vacuously green; step 3 asserts the skip-bit SET by path membership, never a
count; step 4 keeps the pre-change reproduction IN FILE and asserts the two runs DIFFER; and an
irreproducible fixture returns BLOCKED rather than weakening the assertion (`:1357-1358`). It fails
today by construction — the repair call it asserts does not exist yet.
(b) *Equivalence* — N-06 (`:1717-1737`). Exit status EXCLUDED and named as such (`:1719-1721`). Can go
red: the fixture must carry at least one REAL finding, asserted as an explicit precondition
(`:1727-1728`), which kills the two-empty-sets tautology; step 4 perturbs X's record and requires
INEQUALITY. Normalisation is bounded to the absolute root only (`:1722-1726`).
(c) *`--verify` does not repair* — N-02 (`:1190-1208`). Can go red: comparison is over STRUCTURES
(path→sha256 manifest + `git ls-files -t` skip-bit pair set), `.git/info/sparse-checkout` explicitly
in the manifest, symlinks recorded as readlink target and never followed, run for EACH of six breaks;
and the RED PROOF at `:1206-1208` routes one break through the `--repair` path and requires this file
to redden for that case and stay green for the other five.

**4. The mandatory positive controls — PASS.** Per-path, each its own named assertion with its own
failure message (N-05 group 2, `:1461-1499`): `.claude/skills` and the `.agents` spelling with
`realpath` equality (`:1467-1473`); the three non-features `.harness` subtrees each separately, the
NESTED `docs/DECISIONS.md` called out (`:1475-1483`); `.harness/harness.json` asserted SEPARATELY
(`:1484-1486`); **`.harness/corpus` its own named case, `islink` AND `realpath` equality, never a bare
`exists()`** (`:1488-1495`) — and it is carried in `REQUIRED_PATHS` with its per-entry assertion FORM
so N-05 cannot degrade it (`:969-977`). Derivation: group 3 adds three tracked things including the
nested one, greps `bin/`+`hooks/` for the names first, and step 4 pins "no source file was edited"
by `git status` + sha256 of `worktree-state.py` (`:1508-1531`). `sparse-checkout set` exits 0 with no
args and with patterns matching nothing is stated as the REASON the control is mandatory
(`:1461-1463`) and the exit status is explicitly never asserted.

**5. The exclusions — PASS.** No byte figure, no `du`, no worktree size, enforced as ASSERTIONS not
prose: N-01 EXCLUSION 1 and 2 (`:1001-1028`), shown-to-fire required, discharged only at N-09's
`--strict` run (`:1010-1016`, `:2100-2106`). Three measurement modes only (`:1022-1025`). Synthetic
`git init` fixture, never a copy of this repo, with the <100-tracked-file bound plus two
no-source-outside-tmp clauses (`:918-999`).

**6. The cycle-5 answers — PASS. Each landed whole; the strike removed only what it was meant to.**
- **Q6 — THE LOAD-BEARING ANSWER: D-2 IS STILL DELIVERED.** SC-15 is gone (14 criteria, SC-01..SC-14),
  D-14 records the strike with all three reasons (`:466-527`), `_hardlink_plan` at `:1907-1922` is
  marker-only (N-06 PART 2b, `:1636-1646`). **Both denial ROUTES survive with their criteria**:
  Write/Edit route through `check-domain.sh`'s registered entrypoint, hook payload on stdin, exit 2
  asserted — `plan.yaml:1252-1256`; Bash route through `bash-write-guard.sh` reaching `classify()`
  `:840` / `wrong_checkout` `:855` — `plan.yaml:1257-1258`; **paired positive control, not optional**,
  a write to the active feature's own dir through both entrypoints must SUCCEED — `:1261-1262`. Graded
  by **SC-03** (`BRIEF.md:195-198`, both entrypoints named, own-dir write still succeeds) and **SC-02**
  (`:189-194`), both `automated`/`integration`, both on **REQ-08** (`:69-71`, coverage row `:97`).
  Enforcement is live and reproduced, and `linked_worktrees` is on NEITHER write route (D-02 `because`,
  `:123-129`) — so the audit fix is not a hidden dependency of the denial. **The strike did not take
  D-2's enforcement with it.**
- **Q1 — landed as DISSOLVED.** No fifth `test-corpus-denials.py` case, no error conversion, no
  `_hardlink_plan` change; D-14 `because` `:514-518` records it as dissolved and NOT mistaken.
- **Q2 — landed, and the skip ANNOUNCES.** N-09 `:2043-2058`: two conditions, `git cat-file -e` per
  endpoint, the skip prints its reason and NAMES the endpoint, and **the test asserts that line was
  printed**; the discrimination case at `:2093-2096` proves the announce fires. `fetch-depth: 0`
  rejected with the measured premise, in D-13 and at `:2056-2058`.
- **Q3 — landed.** N-06 PART 2 now reads "DO NOT MARK THIS SITE" (`:1629-1634`); BOTH N-12 assertions
  quantify over the DETECTED set (`:2355-2364`), with the quantifier called load-bearing; D-15 records
  it (`:529-551`).
- **Q4 — all four landed, none deferred, no `approval.rulings` acceptance.** VL-05: N-09 is
  `scaffolding` with the in-task justification (`:1945-1950`) and `test-nonregression-notes.py` struck,
  its four cases moved to PART 3 clauses 4-7 (`:2071-2085`). VL-06: N-01 `:1005-1016`. VL-07: dissolved
  by the DoD amendment. VL-08: **verified PER CLAUSE — all seven survivors present**: SC-01 per-path
  (`:1465-1466`), SC-01 not-a-bare-existence (`:1488-1495`), SC-01 failing-state-first (`:1443-1446`),
  SC-09 by-the-invocation-it-records (`:1671-1675`), SC-11 pre-change-shape-in-file (`:1353-1356`,
  `:1373-1374`), SC-13 stdout-AND-exit-status (`:2061-2064`), SC-14 per-site-named-case (`:2212-2214`).
- **Q5 — clean.** No probe-tree residual in D-10 or N-02; the only surviving probe-stripping sentence
  is inside the FROZEN panel record (`:754-760`), correctly left unrewritten.

**7. The fold — PASS.** N-11 retired, id left as a deliberate gap. The ALLOW assertion survives as
N-10 PART 7 **(c)**, asserted BEFORE the deny clause **and for that reason**, with the pre-change
false-denial kept as the pinned reproduction (`:2247-2252`); (d) DENY follows with the stated reason
that (c) alone is satisfied by a gate that allows everything (`:2253-2255`). The production half is
PART 6 (`:2226-2239`), shape (c) only, with a comment forbidding a refusal arm. **N-10's surface is
still coherent**: one seam — resolve the owner root behind `feature_corpus` — over six production
files that all do the same thing, plus its markers and its three tests. The branch gate differs only
in failure DIRECTION (fails closed wrongly), which the task states explicitly (`:2227-2228`); that is
one surface, not two.

**8. Coverage — PASS. 41 rows, one removal, arithmetic closes.** Base ledger 25 (A-01..A-23 + X-1, X-2)
+ 11 finding-derived = 36 (`runs/consolidate-eng/digest.md:75-122`, corrected count at `:193-195`),
+6 at cycle 3 (`research-FEAT-58-apply-batch-c3.md:55-57`), −1 at cycle 5 = **41**. The one removal is
**`hardlink deny + positive control (N-11)`**, named (`research-FEAT-58-apply-c5.md:55-58`), and it is
the ONLY one; its positive-control half is not lost as a claim because A-07 already carries it. Every
cycle-3 addition still lands: per-site count equivalence ×4 → N-10 PART 5 (`:2212-2221`); `corpus_root`
refusal → N-10 PART 5 (`:2222-2224`); branch-gate allow+deny → N-10 PART 7 (moved, not removed —
`research-FEAT-58-fold-n11.md:74-81`); census both halves → N-12 (`:2366-2377`); the exemption's cases
→ N-07 PART 3 cases 5-8 and N-08 clauses 1-4. **Nothing dropped and nothing silently demoted.** The two
earlier evidence-form demotions are STILL VISIBLE in the evidence column the operator signs —
`BRIEF.md:301-310` names both (N-09's `AUDIT UNCHANGED`, N-06's `PRE-CHANGE REPRODUCTION`), states what
is therefore NOT re-proven, and names what carries it; the third (A-23) is disclosed at `:291-300`.

**9. The shape rule — PASS.** Eleven tasks, each one surface: fixture+baseline (N-01), the command
(N-02), the read path (N-03), the hook tier (N-04), the creation surface (N-05), the audit (N-06),
branch uniqueness (N-07), the real-data act (N-08), non-regression close-out (N-09), the owner-root
seam (N-10), the census (N-12). Fourteen criteria, each an observable outcome. **No task carries a
`change_type` demanding a test kind it cannot honestly satisfy** — the VL-05 shape: every
`cross_module`/`feature` task holds a real unit file (N-02 `test-worktree-state-derive.py`, N-04
`test-hook-shim-delegates.py`, N-06 `test-check-state-expected-dirs.py`, N-07 `test-branch-uniqueness.py`,
N-10 `test-feature-corpus.py`), and every unit-free task is `scaffolding`/`config` (N-01, N-03, N-05,
N-08, N-09, N-12). The fold is what makes N-10 honest: post-strike N-11 would have been a
gate-behaviour change with no unit half.

**10. What the DoD kills — PASS. None crept back.** Migration/convergence: no task; `BRIEF.md:320-322`
Non-goals. Corpus-root anchor: explicitly rejected in D-09 `choice` (`:31-32`). Fifteen-reader ledger:
rejected in D-09 `because` (`:40-42`). Reflink/clonefile: appears only as the excluded mechanism
(`:1019-1021`, `BRIEF.md:314-317`). Byte-count criteria: none — X-1 makes their absence an assertion.
Incremental-sweep cache: forbidden by name in N-10 (`:2161-2163`) and D-01. *Observed, not a finding:*
the fenced `lanes:` block still carries a `notes/migration-record.md` row (`:23-25`), a residue of the
killed task inside the key the operator ruled unwritable — it binds nothing.

## Findings

- **GC5-01 · `panel` (plan.yaml:619-808) · med.** Every one of the eight findings still reads
  `disposition: open` (`:638, :663, :687, :731, :746, :763, :783, :805`), including the three the
  operator ruled on and the four he ordered folded in — all of which landed. `harness-spec-driven`
  requires a finding pm believes fixed to carry `disposition: resolved` with `resolved_by:`. As it
  stands the signature packet reports three open `high` findings against a draft that answered them,
  and VL-07's frozen summary quotes a DoD sentence the operator has since withdrawn.
  **Change:** at the next panel transcription, carry `resolved` + `resolved_by` for VL-01 (D-14),
  VL-02 (N-09/D-13), VL-03 (D-15/N-06), VL-05 (N-09), VL-06 (N-01), VL-07 (dissolved by the DoD
  amendment), VL-08 (the five SC edits); leave every summary and severity verbatim.
- **GC5-02 · `notes/research-FEAT-58-apply-c5.md` · low.** Its VL-08 survivor table (`:42-48`) cites
  `plan.yaml` line anchors taken before the N-11 fold — every one of the seven is now off by roughly
  twenty lines (e.g. SC-01's failing-state clause cited at `:1420-1423`, actually `:1443-1446`). All
  seven survivors are present; only the pointers rotted. **Change:** re-derive the seven anchors, or
  replace them with PART/clause references, which do not rot.
- **GC5-03 · `notes/research-FEAT-58-apply-c5.md:68-70` · low.** The marker arithmetic still
  attributes `branch-create-gate.sh`'s marker to N-11 (`N-10 6 · N-11 1`). Superseded by
  `research-FEAT-58-fold-n11.md`, but this is the note a reader opens first for the cycle-5 pass.
  **Change:** restate as `N-10 7`, or add a one-line superseded-by pointer at the head of the note.

## Open questions

None blocking. GC5-01 is the only one the signature packet depends on, and its natural home is the
final panel re-run already ordered under "what happens next".
