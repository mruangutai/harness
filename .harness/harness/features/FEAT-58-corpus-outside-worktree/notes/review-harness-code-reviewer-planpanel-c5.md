# Review — scope reader — FEAT-58-corpus-outside-worktree — plan-panel-final (cycle 5)

**PASS with one new high.** The strike removed only what it was meant to, VL-01..VL-09 are all
correctly dispositioned in the *written artifacts*, the ledger recounts to 41 by direct
enumeration (not telescoping arithmetic), and structure/executability are clean. One new finding:
N-10 PART 7 clause (c)'s literal test-construction text ("assert it ALLOWS, exit 0") is
non-discriminating against `branch-create-gate.sh`'s actual refusal mechanism, which I verified at
source — both `deny()` and the allow path `exit 0`. That is the plan's own self-named
highest-risk clause and the gap is a `high`, so `severity_max: high` even though nothing else
gates.

Read at source: `plan.yaml` (full, all 11 tasks + 15 decisions), `BRIEF.md` (full), the amended
DoD note (`:119-153`), `answers-operator-c3.md`, `answers-operator-c5.md`,
`research-FEAT-58-apply-batch-c3.md`, `research-FEAT-58-apply-c5.md`, `research-FEAT-58-fold-n11.md`,
`research-FEAT-58-goalcheck-plan-c5.md`, `runs/goalcheckfinal-product/digest.md`,
`runs/consolidate-eng/digest.md`, `runs/planpanel4-validator/digest.md`, and
`.claude/skills/harness/bin/branch-create-gate.sh` (the actual script, to check the ALLOW/DENY
mechanism directly rather than trust the plan's paraphrase).

## The seven questions

**1. THE STRIKE — did Q6 remove only what it was meant to?**
- **D-2 (DoD) is still delivered.** N-03's two-route denial is intact and unaffected by the
  strike: Write/Edit route through `check-domain.sh`'s registered entrypoint (hook payload on
  stdin, exit 2 asserted) at `plan.yaml:1252-1256`, Bash route through
  `bash-write-guard.sh:855`'s `classify()`/`wrong_checkout` handling at `:1257-1258`, plus the
  mandatory paired positive control (own-directory write through both entrypoints must succeed)
  at `:1261-1262`. `linked_worktrees` — the function D-02 actually repairs — is on **neither**
  write route; it governs a report (N-06's audit + census), never a write decision, so the
  strike's removal of the hardlink half touches no code the D-2 denial depends on. Graded by
  SC-02/SC-03, both `automated`/`integration`, both on REQ-08. **Confirmed: the strike did not
  take D-2's enforcement with it.**
- **The ALLOW assertion survives the fold** — N-10 PART 7 case (c), asserted before (d) "for that
  reason," with the pinned pre-change false-denial kept in the file. It textually survives. But
  see the new finding below: its *literal operationalization* ("exit 0") does not actually
  discriminate ALLOW from DENY in this script, which is a defect in the surviving clause itself,
  not evidence the fold dropped it.
- **The ledger recounts to 41 by direct row enumeration**, not the goal-check's `25+11+6-1`
  telescoping: base matrix rows A-01..A-23 (23, verified by reading every row of
  `consolidate-eng/digest.md`'s table, no gaps) + X-1/X-2 (2) = 25; finding-derived rows F-01,
  F-02, F-03, F-06, F-04/C-03, VL-01/C-03, A-04/A-03/C-01, A-01/A-02/C-04, A-06, ALT-F2, ALT-F3 —
  counted by name, 11, not merely trusted as "11" — = 36; cycle-3 additions named individually —
  per-site count equivalence×4 (1 row), `corpus_root` refusal (1), hardlink deny+control (1),
  branch-gate allow+deny (1), census both halves (1), exemption's cases (1) — 6 named rows = 42;
  cycle-5 removal named once — hardlink deny+control — 1 row = **41**. Cross-checked against
  `research-FEAT-58-fold-n11.md`'s independent claim that the base ledger contains no `N-11`
  string and that the branch-gate row is the *only* row that changed owner (moved into N-10, not
  duplicated). **41 confirmed by naming every row, not by subtracting totals.**

**2. Disposition of VL-01..VL-09 — see table below.**

**3. Can the three weight-bearing proofs still report RED?**
- **Merge regression** (N-04 PART 2): step 1 asserts pre-merge S-count non-zero (not vacuous);
  step 3 asserts the skip-bit set by path membership; step 4 keeps the pre-change reproduction IN
  THE FILE and asserts the two runs DIFFER; "IT MUST FAIL TODAY" is stated verbatim in the task
  intent; an irreproducible fixture returns BLOCKED rather than weakening. Confirmed by direct
  read.
- **Equivalence** (N-06, A-08): "EXIT 0 IS EXPLICITLY NOT PROOF and exit status is EXCLUDED from
  the comparison" — confirmed verbatim in N-06's own intent text — plus the real-finding
  precondition and the perturb-for-inequality step.
- **`--verify` does not repair** (N-02, A-17): manifest (path→sha256, symlink recorded as
  readlink target, `.git/info/sparse-checkout` explicitly included) plus the skip-bit set,
  compared before/after for each of the six breaks, plus the route-one-break-through-`--repair`
  red proof recorded in the receipt.
All three: confirmed RED-capable by direct read, none against a moving ref (D-13's demotions hit
adjacent, different clauses).

**4. Are the positive controls still load-bearing, and is a third blind instance hiding?**
`.agents/skills` and `.harness/corpus` are asserted per-path, never by exit status, confirmed
directly in N-05 group 2 ("NEVER assert the command's exit status here"; the corpus check is
"NEITHER an existence check" — `islink` AND `realpath` equality, both named clauses). **A third
instance is hiding, in a different shape than the two known ones (the D-08 derivation gap and the
missing `REQUIRED_PATHS` entry) and different from VL-01's uncaught-raise shape too**: see the new
finding. It is a *discriminating-assertion* blindness rather than a missing-path blindness — the
plan depends on `branch-create-gate.sh`'s exit code meaning something for the ALLOW case, and it
does not, by the script's own design (`deny()` also exits 0). The previous panel's "no
demonstrable third instance" answer was scoped to the `REQUIRED_PATHS` shape specifically (its own
adequacy note says so) and did not evaluate this clause against the gate's actual source.

**5. The shape rule — eleven tasks, fourteen criteria, coherent surfaces?**
Clean. N-06 (4 test files) and N-10 (3 test files) are each one seam under D-07's
single-writer-per-shared-file device, not padding — confirmed directly: N-10's four read sites
plus the branch gate all resolve through one `feature_corpus` seam, and the branch gate differs
only in failure *direction* (fails closed wrongly vs. the four read sites' fail-open), which the
task states explicitly as the reason it is one surface rather than two. No task's `change_type`
demands a test kind it cannot honestly satisfy: every `cross_module`/`feature` task
(N-02, N-04, N-06, N-07, N-10) holds a real unit file I confirmed by name
(`test-worktree-state-derive.py`, `test-hook-shim-delegates.py`,
`test-check-state-expected-dirs.py`, `test-branch-uniqueness.py`, `test-feature-corpus.py`), and
every unit-free task (N-01, N-03, N-05, N-08, N-09, N-12) is `scaffolding`/`config`.

**6. The seven binding items — D-1..D-5, M-1, M-2, each its own REQ+SC, none by inspection?**
Clean, read at REQ text: D-1→REQ-01/SC-01, D-2→REQ-02/SC-01+SC-02, D-3→REQ-03/SC-04,05,06,14,
D-4→REQ-04/SC-07, D-5→REQ-05/SC-12, M-1→REQ-06/SC-09,10, M-2→REQ-07/SC-11. Every one of the
fourteen criteria declares `verify: automated` / `evidence: integration`; none of the seven falls
to inspection. REQ-08/09/10 (non-DoD but still REQ) are likewise SC-02,03 / SC-08 / SC-13, all
automated.

**7. Executability — verify: paths exist or are created by a named earlier task; depends_on
acyclic; nothing names N-11?**
Clean, traced directly from the `depends_on:` lines of all 11 tasks: N-01→[]; N-02→[N-01];
N-03→[N-02]; N-04→[N-02]; N-05→[N-04]; N-06→[N-01,N-02]; N-07→[N-01,N-10]; N-08→[N-07];
N-09→[N-02,N-03,N-04,N-05,N-06,N-07,N-08,N-10,N-12]; N-10→[N-01]; N-12→[N-06,N-07,N-10]. A valid
topological order exists (N-01, N-10, N-02, N-04, N-07, N-03, N-05, N-06, N-08, N-12, N-09 among
others); no cycle. `N-07→[N-10]` matches D-07's single-writer table verbatim ("feature_corpus.py
-> N-10, then N-07 ... serialised by N-07's depends_on edge"). No task's `depends_on` or `intent`
names `N-11` as a live edge; every prior `N-11` citation is either rewritten to its new owner or
deliberately preserved as frozen panel history and read through D-14's mapping — confirmed by
`research-FEAT-58-fold-n11.md`'s own accounting of all 25 occurrences, spot-checked at N-06's
intent (references only `N-10 PART 6/7` and the retirement fact) and N-10's intent (self-contained,
no dangling reference).

## New finding

- **reader: scope**
  **summary:** N-10 PART 7 clause (c) tells the executor to prove `branch-create-gate.sh` still
  ALLOWS a legal flow by asserting `exit 0` — but the gate's own `deny()` function (unmodified by
  this feature) *also* unconditionally `exit 0`s after printing its JSON payload, so an
  exit-0-only assertion cannot distinguish ALLOW from a false DENY.
  **severity:** high
  **lands on:** task N-10 PART 7 clause (c) (`plan.yaml`, "THE BRANCH GATE STILL ALLOWS" —
  `verify:` text, not yet-built code), SC-14, REQ-03.
  **concrete change:** reword clause (c) to require parsing the printed output and asserting it is
  *not* a `permissionDecision: deny` JSON payload (or, if the ALLOW path prints nothing, asserting
  the absence of any JSON on stdout), the same way N-07 PART 4(b) is worded for `merge-gate.py`
  ("assert the payload is not a denial ... NEVER assert an exit status as the refusal - there is
  none"). Add the identical warning sentence to N-10 PART 7 that N-07 PART 4 already carries for
  the structurally identical mechanism.
  **failure scenario:** I read `.claude/skills/harness/bin/branch-create-gate.sh` directly. Its
  `deny()` function (lines ~55-58) is `python3 ... print(json.dumps({"hookSpecificOutput":
  {...,"permissionDecision":"deny",...}})); exit 0` — confirmed by the file's own top-of-file
  comment: *"Deny is a structured permissionDecision (exit 0 + JSON)."* The flow-match success
  path (`match=$(ls -d ...) ... exit 0`, line ~89-92) also exits 0. If an implementer follows the
  plan's literal instruction and writes `assert result.returncode == 0` for the ALLOW case (which
  is what "assert it ALLOWS, exit 0" reads as, in contrast to clause (d)'s correctly-worded
  "denies with its existing message"), then a regression that makes the owner-root flow lookup
  fail for every branch — e.g., a bug in N-10 PART 6's `feature_corpus`-based `root` resolution
  that this exact task introduces — would cause `deny()` to fire for the legal flow Y too, and the
  test would still pass, because `deny()` exits 0 exactly like success. This is precisely the
  false-deny regression the plan calls "the clause this task is most likely to break," and the
  spec's own wording for the discriminating case does not force a test that can catch it. The
  parallel task for the structurally identical `merge-gate.py` mechanism (N-07 PART 4b) already
  contains the correct instruction and an explicit "never assert exit status" warning; N-10 PART 7
  omits it for the second gate sharing the same DEC-138-style contract.

## VL-01..VL-09 disposition — verified in written artifacts, not in reports of them

| id | prior sev | disposition now | where verified |
|---|---|---|---|
| VL-01 | high | **DISSOLVED**, not remedied | D-14 `choice`/`because` (`plan.yaml`): no fifth `test-corpus-denials.py` case, no error conversion, no `_hardlink_plan` change exists anywhere in the plan — confirmed by reading N-06 PART 2b (comment-only) and N-10/N-12 (neither references `_hardlink_plan`). `check-domain.sh:1907-1922` is untouched by any task's `files:`. Record correctly says dissolved, not fixed and not mistaken — the operator verified the exit-1-non-blocking premise himself (`answers-operator-c5.md` Q1). |
| VL-02 | high (reconciled up) | **APPLIED**, skip announced | N-09 PART 3 clause 3 SELF-SCOPE: two conditions (absent/non-40-hex, or `git cat-file -e` fails), confirmed read directly — "THE SKIP PRINTS ITS REASON AND NAMES THE ENDPOINT ... and the test ASSERTS that line was printed." Discrimination case present (syntactically-valid-but-unresolvable sha). `fetch-depth: 0` rejected with the measured premise in D-13. |
| VL-03 | high (reconciled up) | **APPLIED** | N-06 PART 2: "DO NOT MARK THIS SITE" replaces the old marker instruction, confirmed read directly. N-12: "BOTH QUANTIFY OVER THE DETECTED SET ... never over a marked set" — confirmed, both HALF-1 assertions read this way in N-12's own intent text. |
| VL-04 | low (both readers, ruling) | **RECORDED as an accepted blind class**, not fixed | N-12 intent, "THE ACCEPTED BLIND CLASS, RECORDED HERE AND NOT ONLY IN A NOTE" — confirmed present verbatim in the task text (`_SWEEP_PATTERNS`, list-of-strings via for-loop binding, out of the one-level assignment-resolution rule by construction). This is a panel ruling, not an open defect. |
| VL-05 | low (=F-10) | **APPLIED** | N-09 `change_type: scaffolding` with an in-task justification citing VL-05 by name; `test-nonregression-notes.py` struck, its four cases moved into PART 3 clauses 4-7 — confirmed by direct read of N-09's intent. |
| VL-06 | low (=F-11) | **APPLIED** | N-01: "the runtime list-equals-plan set comparison, and the non-strict PENDING accounting ... are STRUCK (finding VL-06)" — confirmed verbatim in N-01's own intent text; literal list + `--strict` existence failure retained, discharge site is N-09's `--strict` run only. |
| VL-07 | low (=F-12) | **DISSOLVED by the DoD amendment, no residual added** | Verified at the amended source (`dod-worktree-corpus-2026-09-10.md:136-143`): the operator withdrew the "gets stripped automatically" claim and ruled the `_ID_RE` scope-guard behavior *correct*. D-10's `because` and N-02's scope-guard text carry no probe-stripping language — read directly, N-02 says the guard exists so "the hook tier does not start refusing trees this feature never claimed," matching the amended note. The only surviving instance of the withdrawn sentence is inside the frozen `panel` block, left there deliberately (never-falsify rule). |
| VL-08 | low (=F-13, grew) | **APPLIED**, verified per clause (not trusted from the table) | Each of the 7 struck construction clauses re-checked directly at its named survivor: SC-01 per-path (N-05 group 2, each "its own named assertion with its own failure message"); SC-01 not-a-bare-existence (N-05's corpus check, "NEITHER an existence check"); SC-01 failing-state-first (N-05 group 1, "FAILING STATE DEMONSTRATED FIRST"); SC-09 by-invocation-not-exit-0 (N-06 PART 3a, "An exit-0 assertion alone cannot tell an invoked gate from an absent one"); SC-11 pre-change-shape-in-file (N-04 PART 2 step 4 and PART 3 step 4, both present); SC-13 stdout-AND-exit-status (N-09 PART 3 clause 3, "assert BOTH that the command's exit status is 0 AND that its stdout names no path outside"); SC-14 per-site-named-case (N-10 PART 5, "FOUR NAMED CASES, never one loop reporting an aggregate verdict"). All seven confirmed present in current text by me directly, not by anchor citation. |
| VL-09 | info | **Not this run's concern** (record-lineage correction, already acted on) | The post-fix goal-check this dispatch names (`research-FEAT-58-goalcheck-plan-c5.md`) is exactly the run VL-09 asked for; it exists and reports PASS on all ten axes. Nothing further for this reader. |

## Not re-reported (per dispatch's KNOWN STALE list)

GC5-01 (`panel:` block still `disposition: open`), GC5-02 (VL-08 survivor-table anchors ~20 lines
stale in `research-FEAT-58-apply-c5.md`, re-derived above rather than trusted), GC5-03
(marker-arithmetic N-11 attribution in the same note).

```yaml
VERDICT: PASS
DIGEST:
  headline: "Strike delivered only what it was meant to (D-2 intact, both routes), VL-01..VL-09 all correctly dispositioned in written artifacts, ledger recounts to 41 by direct row enumeration; one new high - N-10 PART 7(c)'s literal 'exit 0' ALLOW assertion cannot distinguish allow from deny in branch-create-gate.sh, whose deny() also exits 0 (verified at source)"
  reader: scope
  severity_max: high
  findings: 1
  must_fix:
    - "N-10 PART 7 clause (c): reword the ALLOW assertion to parse/assert absence of the deny JSON payload, matching N-07 PART 4(b)'s wording and warning, instead of asserting bare 'exit 0' against a script whose deny() also exits 0"
  spec_violations: []
  code_grade: n_a
  reviewed: "plan:.harness/harness/features/FEAT-58-corpus-outside-worktree/plan.yaml"
  human_commits_in_scope: []
  open_questions: []
  files_touched:
    - .harness/harness/features/FEAT-58-corpus-outside-worktree/notes/review-harness-code-reviewer-planpanel-c5.md
  expertise_update: []
artifact: .harness/harness/features/FEAT-58-corpus-outside-worktree/notes/review-harness-code-reviewer-planpanel-c5.md
```
