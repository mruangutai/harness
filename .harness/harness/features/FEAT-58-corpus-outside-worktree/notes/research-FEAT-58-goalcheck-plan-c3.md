# Goal-check c3 — FEAT-58 amended plan (12 tasks / 13 decisions / 15 SC) vs the operator's intent

**Answer: DELIVERED on eight of nine axes; NOT delivered on one, and the gap is a planning defect no
retry fixes.** All five DoD outcomes, all seven binding items, the three weight-bearing proofs, the
mandatory positive controls, the exclusions and all four batched answers landed whole; the assertion
ledger is intact 36/36 with the two demotions visible where the operator signs. **The one failure:
`N-12`'s census, as specified, cannot pass and no task can make it pass — so `SC-14`'s census clause
is unmeetable as written.** One high, one med, two low. Nothing else regressed during the 9→12 / 13→15
growth. Supersedes `notes/research-FEAT-58-goalcheck-plan-c0.md` (which graded the pre-amendment draft).

## Findings

**GC-01 · high · `N-12` / `SC-14` — the census quantifies over a scope no task can touch.**
`N-12` (plan.yaml:2000-2003, HALF 1 at :2018-2019) scans *every* `.py`/`.sh` under `bin/`, detects three spellings
including "a literal path string carrying `.harness` and `features`", and HALF 1 demands **ZERO
unmarked sites over the real tree**; `SC-14` (BRIEF.md:227-235) repeats it. `N-12`'s `files:` is one
test file (plan.yaml:1993-1994), and `D-07`'s single-writer table (plan.yaml:254-268) gives the
other files no writer. Marked sites total ten across eight files (N-06 `check-state.sh:118-120` +
`harness_boundary.py:151-174`; N-07 `merge-gate.py:134`; N-10 four sites; N-11 two sites). Measured
in this worktree now: **114 lines in 32 files** under `bin/` carry `.harness` and `features` on one
line — `N-12`'s own "30 lines across 15 files" is a bare figure with no invocation recorded.
Survivors with no writer include `check-domain.sh:1053-1061` `_SWEEP_PATTERNS` (a real corpus glob
that `D-02` plan.yaml:115-117 deliberately does **not** edit), `check-state.sh:462-467`,
`board_lifecycle.py:489,946`, `check-plan-routes.py:15,290,539,593,764,887`, `quarantine.py:42-46`,
`layout_fixtures.py:30-47`, `validate-digest.py:544-857`, `feature_json_write.py`, `plan-merge.py`.
**Change asked for:** either (i) narrow the census subject to sites that *enumerate* the corpus on
disk — a value reaching `glob`/`ls`/`os.listdir`/`iterdir` — state that comments, message strings and
regexes are out of subject, and record the measured count **with the invocation** at the pin; or
(ii) widen `N-12`'s `files:` to every file needing a marker and add the matching `D-07` single-writer
rows (which re-opens `check-state.sh`'s FEAT-57 serialisation). (i) is the smaller edit and keeps the
red-capability HALF 2 intact.

**GC-02 · med · `SC-01` / `N-01` REQUIRED_PATHS / `N-05` group 2 — DoD point 2 is not graded at the
creation surface.** `REQUIRED_PATHS` (plan.yaml:726-734) and `SC-01`'s per-path enumeration
(BRIEF.md:145-154) do not name `.harness/corpus`; `N-05` group 1b asserts only "the required paths of
group 2" (plan.yaml:1202-1206). `N-03` proves the read but depends on `N-02` only, so its worktree
need not have been produced by the creation path. Mechanism is fine (`worktree-state.py` checks 3/4a
at plan.yaml:895-898) — the *grading* of "a newly created worktree can read the corpus" is absent.
**Change:** add `.harness/corpus` to `REQUIRED_PATHS` as `islink` + `realpath == <owner>/.harness/harness/features`,
its own named assertion in `N-05` group 2, and one clause in `SC-01`.

**GC-03 · low · `SC-01`, `SC-09`, `SC-11`, `SC-13`, `SC-14`, `SC-15` — test-construction language
survives in criteria and grew.** "demonstrated first" (BRIEF.md:153-154, :239), "asserted by the
invocation it records, never by exit 0" (:193-194), "reproduced in the same file" (:205), "BOTH the
stdout and the exit status asserted" (:218-219), "never as one aggregate" (:230). Panel `F-13` is
`disposition: open` (plan.yaml, findings block) and Q4 ordered only F-03/F-04/F-05/F-06 — so this is
not a breach of the ruling, but it is the operator's own shape rule (authority 2) and the two NEW
criteria added more of it. **Change:** strike the trailing construction clause from those six (the
panel verified each survives verbatim in the owning task's intent) or record F-13 accepted in
`approval.rulings` — an explicit ruling, not silence.

**GC-04 · low · record accuracy.** `plan.yaml:23-25`'s `lanes:` row for
`notes/migration-record.md` is the only surviving trace of the killed migration/convergence task; no
task writes that path and `D-07` does not list it. Unwritable key, filed separately — flagged only so
the signature reader is not misled. Separately, `notes/research-FEAT-58-apply-batch-c3.md:7-8` says
"12 TASK `DEVIATION` lines"; re-run at this pin gives **10** DEVIATION + 2 OK, no MANIFEST deviation,
`0 violation(s)`, exit 0. The substantive claim holds; the count does not.

## The nine axes

1. **Five DoD outcomes — delivered, not merely tested for.** (1) one dir: cone derived in
`worktree-state.py` check 1 (plan.yaml:884-901), applied by `post-checkout` (N-04). (2) corpus on
disk: symlink `D-09` + checks 3/4a + `.gitignore` (N-03 PART 1) — see GC-02 for the grading gap.
(3) audit narrowed + fail-closed: N-06 PART 1. (4) branch uniqueness: N-07 + N-08. (5) fresh
clone/CI: N-02's three-condition scope guard (plan.yaml:860-872) + N-09 PART 1 (a)(c)(d).
2. **Seven binding items — each on its own REQ with ≥1 SC, read at REQ text.** REQ-01…REQ-07 =
D-1…D-5, M-1, M-2 (BRIEF.md:50-68); none merged, none deferred, every SC `automated`/`integration`
(no inspection substitution). **M-1 and M-2 are still first-class, not implementation detail:**
REQ-06 states the idempotent command and `--verify` never repairing in its own words (:63-64) and is
graded by SC-09+SC-10; REQ-07 states hook-fired execution and hook-failure containment (:65-68) and
is graded by SC-11. Both own tasks (N-02, N-04) and `D-12` gives `--verify` a named caller so it does
not ship uncalled.
3. **The three weight-bearing proofs — all can report RED.** (a) Merge regression: `N-04` PART 2,
own file, pre-merge `S`-count non-zero precondition, step 4 pre-change reproduction **constructed in
the fixture** (plan.yaml:1119-1124), host 3337/3807 cited as measurement and forbidden as an
assertion, BLOCKED if unreproducible. (b) Equivalence: `N-06`'s own file, exit status excluded and
recorded-not-asserted, real-finding precondition, perturbation step 4 → red-capable. (c) No-repair:
`N-02`'s own file, manifest + skip-bit set per six breaks incl. `.git/info/sparse-checkout`, symlinks
by `readlink`, plus a route-one-break-through-repair red proof.
4. **Positive controls — mandatory form met.** `N-05` group 2 asserts per path with its own message,
never an exit status, `.agents`/`.claude` both spellings with `realpath` equality, the three
non-features `.harness` subtrees individually, `harness.json` separately, a non-active feature
absent, and two one-at-a-time discrimination probes. Derivation: group 3 adds a top-level dir, a
`.harness` subtree **and** a nested `.harness/harness` subtree, with the no-source-edit clause.
5. **Exclusions — asserted, not prose.** `N-01` EXCLUSION 1 at plan.yaml:761-779 and EXCLUSION 2 at :780-783, with a
shown-to-fire proof, re-run under `--strict` in `N-09` PART 4; fixture is `git init` with a
<100-tracked-file bound plus two no-external-source clauses. Only the three modes are sanctioned —
stricter than the DoD, which also permits a `df -k` delta; no criterion needs it.
6. **The four batched answers — each landed whole.** **Q1:** all nine choke points in scope with
shapes stated at the site (N-06 pts 1 & 9 `(a)+(b)`; N-07 pt 2 `(c)+(b)`; N-10 pts 3-6 `(c)+(b)`,
with "NONE takes shape (a)" and why; N-11 pt 7 `(c)+(b)`, pt 8 `(c)` only). The trap is handled:
`branch-create-gate.sh:89` gets **no refusal arm** and `N-11` PART 5 case (c) asserts the ALLOW path
still allows, ordered **before** the deny case, with the pre-change false denial pinned. **Q2:** no
persisted index anywhere — grep of plan+BRIEF returns only `D-01`'s recorded deletion
(plan.yaml:71-110), `N-07`'s prohibition (:1471-1474) and `N-08`'s (:1595-1596); F-08 recorded
**DISSOLVED** with the subject-has-ceased reasoning, F-06's D-01 half dissolved with it; the 1.2 s
figure struck against the measured 0.0023 s. **Q3:** Arm B, records uncorrected (`N-08`:1587-1594),
`BRANCH_ERA_EXEMPT` keyed on the exact frozenset above the predicate, reason non-empty and
load-bearing, tests pin both halves plus superset and emptied-reason (N-07 cases 5-8; N-08 clauses
2-4); `SC-13` whole, no exclusion anywhere; the four literal-`none` records produce zero findings
(N-07 case 2, N-08 clause 1 with a >70-row read guard). **Q4:** F-06 asserts the **deny payload**
and no merge-gate non-zero survives in live spec (only inside the frozen `panel` record at ~:563);
F-03+F-05 are one arm-aware pinned discharge site with `N-09`'s inline `git diff` **deleted**
(:1732-1734); F-04+F-07 are one rule, `D-13`, naming its three sites.
7. **Shape rule after growth — holds for tasks, marginal for criteria.** Each of the twelve owns a
coherent surface; three are grading-only by construction (`N-05` after N-04, `N-08` after Arm B
removed its production surface, `N-12` after every marker exists) and each states why. Routing
re-verified: `check-plan-routes.py <plan>` → `0 violation(s)`, exit 0. Criteria: see GC-03.
8. **Coverage — 36/36 have a landing place. Full audit:** A-01→N-01 self-check · A-02→N-05 g1 ·
A-03→N-05 g2 · A-04→N-05 g3 · A-05→N-03 (a) · A-06→N-03 (b) + `.gitignore` grep · A-07→N-03 (c) ·
A-08→N-06 `test-check-state-equivalence.py` · A-09→N-06 scope c1 · A-10→N-06 scope c2 ·
A-11→N-07 P3 c1-4 (file now `test-branch-uniqueness.py`) · A-12→N-07 P4 (a)(b) · A-13→N-08 (its
`--check` clause deleted with the index) · **A-14**→N-09 P1: (a)(c)(d) standing, **(b) demoted** ·
A-15→N-01 record + N-09 P3 c2, **standing** · A-16→N-02 six cases · A-17→N-02 norepair file ·
A-18→N-02 idempotence · A-19→N-04 P2 + HOST-SCALE RESIDUAL · A-20→N-05 g1b · A-21→N-04 P3 ·
A-22→N-04 P4 · **A-23**→N-09 P3 c3 (verify duplicate deleted; one pinned standing assertion) ·
X-1/X-2→N-01 EXCL 1/2 + N-09 `--strict` · F-01→N-02 msg clause 1 · F-02→N-02 norepair verb clause ·
F-03(ledger)→N-02 ANNOUNCE case · F-06(ledger)→N-02 clause 3 + N-06 remedy tail · F-04/C-03→N-04 P1
rule 5 + P4 (b) · VL-01/C-03→N-02 check 5 + dirty-tree asymmetry + N-04 (b) · A-04/A-03/C-01→N-07 P2
+ P4 (c)(d) · A-01,A-02/C-04→index half deleted (recorded in D-01), review-sha half survives in N-08
· A-06(ledger)→N-02 scope guard + N-04 neighbour re-run · ALT-F2→N-06 P2 + scope c3 ·
ALT-F3→N-07 single-implementation assertion. **The demotions are visible where the operator signs:**
BRIEF.md:261-270 names both as "a real reduction", `D-13` (plan.yaml:406-441) names the cost rather
than absorbing it. **The corrected attribution is what is written:** the demoted clause is described
as `N-09` PART 1 (b) (A-14) in both `D-13` and the BRIEF gap; `A-15` (failing-set equality) is stated
as standing. Nothing dropped, nothing silently demoted.
9. **What the DoD kills — no creep.** Migration/convergence (BRIEF Non-goals :280-282, and GC-04),
corpus-root anchor and the fifteen-reader ledger (`D-09` records both as rejected, plan.yaml:36-42),
reflink/clonefile (Non-goals :274-277; `clonefile` appears only inside EXCLUSION 1's rationale),
byte-count criteria (none; `du` only as the thing asserted absent), incremental-sweep cache (only as
"do not add caching", :1841-1843).

## Open questions

- **Q1 (blocking the ship, not the signature):** GC-01 — narrow the census subject, or widen `N-12`'s
  `files:` and the single-writer table? pm recommends narrowing.
- **Q2 (non-blocking):** GC-03 — strike the construction clauses, or rule F-13 accepted?
