# Review — harness-code-reviewer (scope reader) — FEAT-58 plan panel, cycle 9

**BLUF: nothing structural. The goal-check's six findings are all correctly graded — severities,
STRUCTURAL/CLAUSE calls, and build-catches-vs-always-green calls all hold up against source. No new
high or critical found on independent read, but H-01's standing high is CONFIRMED, not resolved —
under review policy that gates on `severity_max >= high`, this review reports FAIL, matching the
operator's own Q8 terms: present the unresolved high, do not spend the tenth cycle fixing it.** All
full-artifact-set claims (structural check, the seven binding items, the three weight-bearing
proofs, the two-route D-2 denial, coverage=45, executability) check out against source and against
the operator's own answer trail. One low-severity addendum found (see L-02 grading below), not
raised as its own numbered finding.

## 1. Structural?

No. Every remaining defect is a test/instruction imprecision inside an otherwise-sound design; none
of them removes a design's ability to deliver a REQ. REQ-03's actual behaviour (refuse fail-closed
on a reach mismatch) is proven by N-06 PART 3(b) and `test-check-state-scope.py` case 2
(plan.yaml:2181-2467) — both are collected, mutation-driven, and independent of N-13's defective
demonstration. Agree with the goal-check.

## 2. Grading the six goal-check findings

| id | goal-check call | my read | agree? |
|---|---|---|---|
| H-01 | high, CLAUSE-DEFECT-ALWAYS-GREEN | confirmed (§3) — standing, unfixed | yes |
| M-01 | med, CLAUSE-DEFECT-ALWAYS-GREEN | confirmed against `harness_boundary.py:66-91` | yes |
| M-02 | med, CLAUSE-DEFECT-BUILD-CATCHES | confirmed against N-13 text + `check-state.sh:22-49` | yes |
| L-01 | low | confirmed against `bash-write-guard.sh` line numbers | yes |
| L-02 | low | confirmed, plus one addendum (below) | yes |
| L-03 | low, build-catches | confirmed by literal indentation vs. `grep -qxF` | yes |

**M-01, verified at source.** `harness_boundary.py:66-91`: `resolve_root` prints the discard notice
only inside the `if override: … not MARKER-carrying …` branch (the safe case). The dangerous branch
— `override` set **and** carrying MARKER — returns immediately with no print at all. N-13 PART 1's
own instruction strips `HARNESS_PROJECT_DIR` before asserting "notice absent," so the assertion is
true unconditionally: stripped ⇒ `override` is falsy ⇒ the print branch can never fire regardless of
whether the strip itself worked. The goal-check's classification is exactly right — nothing an
automated re-run can ever redden here.

**M-02, verified at source.** N-13 PART 2 clauses 3–4 (plan.yaml, "EXIT 8 DOES NOT GATE" /
"THE STRUCTURAL POSITIVE CONTROL") literally read "Run the shipped check-state.sh with cwd at the
probe," the identical phrasing the operator struck for PART 1 at Q1 ("cwd is inert…never…from the
caller's cwd"). `check-state.sh:22-49` resolves root via `_selfdir`, confirmed unchanged from PART
1's own citation. This is the same defect one paragraph after the operator ordered it fixed, just
not carried to the second occurrence — a plausible build-time trap since a builder adapting PART 1's
already-correct absolute-path helper for PART 2 could reuse the owner-root path and merely change
`cwd`, reproducing the bug PART 1 just eliminated. Because clauses 3–4 are inside the collected file
(`test-check-state-realdata.py`, run by `verify:`), a build agent who follows the stale instruction
gets an assertion that observes the wrong tree and fails outright — build-catches is the right call.

**L-01, verified at source.** `bash-write-guard.sh`: the worktree-add/move/remove/prune guard is
lines ~565–648 (the loop starts ~565, falls through to `if not findings: sys.exit(0)` at 646). The
no-destination and relative-destination refusals sit at 607–619 (confirmed by grep). The force-flag
refusal is at line 582, strictly inside `if _sub in ("remove", "prune"):` at line 577 — force on
`add`/`move` is never inspected by this block. `feature_checkout_guard` starts at line 704, matching
the goal-check's ":701-741 is a different function." N-13's citation of ":624-741" is wrong on both
counts exactly as claimed.

**L-02, verified at source, plus an addendum.** `BRIEF.md:401-403` still reads "`core.hooksPath` is
`.claude/skills/harness/hooks`, tracked so it travels with a clone" — the precise sentence the
operator withdrew at cycle 8 (measured `git ls-files | grep -c gitconfig` → 0; confirmed in
`answers-operator-c8.md` and in the DoD note's own "CORRECTED 2026-09-10" paragraph). Confirmed
still present, unfixed. **Addendum, not raised as a separate finding:** the same sentence also cites
`bash-write-guard.sh:611-741`, which suffers the identical stale-anchor problem as L-01 (611 sits
mid-guard, 741 is inside `feature_checkout_guard`, a different rule entirely). Since it's the same
document, same severity class, and BRIEF.md's Constraints section is not one of the two
operator-owned-text carve-outs in scope, folding it in here rather than inflating the count.

**L-03, verified at source.** N-09's note-template block (plan.yaml, PART 2) shows `## AUDIT
UNCHANGED` and its three fields indented 14 columns versus `## NOTHING ALTERED`'s 8, reading as a
nested sub-block. N-09's `verify:` runs `grep -qxF '## AUDIT UNCHANGED' notes/nonregression.md` — an
exact whole-line, column-0 match. A note produced by literally following the template's indentation
fails that grep. Because the grep is in the collected `verify:` string itself, a builder discovers
this the moment they run the task's own gate — build-catches is right.

## 3. H-01, own read

Confirmed independently. N-06 PART 1's shipped derivation is "one derivation, used twice": both the
expected and reached sets key off first-level directory names under `.harness/*/features/*`.
Staging the **pre-fix** spelling (expected keyed by `feature.json` presence, 79 records; reached
still the directory walk, 89 dirs) against the real owner root necessarily yields `MISSING=[]`
(every recorded feature has a directory) and `UNEXPECTED=10` (the ten record-less directories,
independently confirmed as issue #1640 and out of scope). Clause 1 as PP-03 loosened it ("no
REFUSAL, missing empty; unexpected-only tolerated," matching N-06 PART 1's own "gate on missing
always, gate on unexpected only inside a linked worktree") passes on exactly this input — the
pre-fix copy cannot redden it, as a matter of arithmetic over data recorded elsewhere in this same
plan, not a hypothetical. This is a real, provable contradiction between PP-04's ordered remedy and
PP-03's ordered remedy, landed in the same round as the assignment states.

**Not structural**, and I agree with the goal-check's grounds: SC-16's owner-root half, as the
operator amended it at cycle 8, is defined as *the absence of a refusal* — the plan's shipped
behaviour matches that text exactly (confirmed against BRIEF.md's SC-16 wording). REQ-03's actual
refusal-on-missing behaviour is proven red-capable by two *other*, collected, mutation-driven tests
— N-06 PART 3(b) ("A STRUCTURAL --verify FAILURE MAKES THE GATE REFUSE") and
`test-check-state-scope.py` CASE 2 ("MUTATION / FAIL-CLOSED: … assert a NON-ZERO exit whose message
carries the counts") — both confirmed present and both independent of N-13. The defect is confined
to a **one-time, receipt-graded proof excluded from the collected suite by D-13**, which is exactly
why it's ALWAYS-GREEN rather than build-catches: nothing in `verify:` ever exercises it, so a false
"REDDENED" claim in the receipt heading is not mechanically detectable.

**This remains a genuine, standing high.** Per the operator's own Q8 terms, a new high found at
this last round is to be presented with the fix NOT applied, named with its concrete failure
scenario, for the operator to accept at signature or convert to a build-phase task — not fixed this
cycle. My review confirms the goal-check's H-01 is real and correctly classified; I am not
resolving it, so this review's own severity_max is high and, under `severity_max >= high → FAIL`,
this review reports FAIL rather than PASS.

## 4. First-read surfaces

- By-path invocation + `HARNESS_PROJECT_DIR` strip (N-13 PART 1): correctly spelled per the
  operator's Q1 ruling, confirmed against `harness_boundary.py:66-78`'s MARKER-preference logic.
- Clause 1's "no REFUSAL" wording: matches PP-03's ruling and N-06 PART 1's own tolerated-report
  language verbatim.
- PART 1 red proof: broken as detailed in §3 (H-01).
- PART 2's fourth announced-skip (INV-31): **does its job.** The skip line is required to literally
  name INV-31 and quote its message form ("no harness hook runs on this clone. Fix: git config
  core.hooksPath …"), confirmed against `check-state.sh:2508-2567`'s actual INV-31 text
  (goal-check's anchor is exact, verified by grep). This names the covering gate rather than
  implying the hook mechanism is optional — the framing the assignment asked me to test survives.
- N-06 PART 4's zero-match case: concrete and non-vacuous — feeds a canned zero-name derivation to
  the pure function and asserts a refusal naming the pathspec, closing the non-emptiness floor that
  PART 1 only stated in prose (PP-06/finding).

## 5–6. Weight-bearing proofs, two-route denial

All three weight-bearing proofs (N-04 PART 2 clause 4's merge regression, N-06's equivalence test's
discrimination clause, N-02's manifest+skip-bit norepair red proof) retain explicit discrimination
clauses in the task text — confirmed by direct read for N-06's equivalence test (four clauses,
clause 4 named "DISCRIMINATION," perturb-and-expect-inequality). SC-11's 3337-deleted /
3807-skip-bits-cleared figures are stated as a measured host baseline, consistent verbatim across
BRIEF.md, the DoD note, and N-04's cited receipt section — not a fixture literal, so they cannot go
stale by construction. The two-route D-2 denial (Write/Edit via `check-domain.sh`, Bash via
`bash-write-guard.sh:855`) is undisturbed, confirmed via D-02's decision text and N-03's PART (c)
paired positive control ("through each of the same two entrypoints must SUCCEED").

## 7–9. Seven binding items, coverage, executability

Cross-checked every task's `traces:` field against the seven-item table: D-1→REQ-01→SC-01 (N-05),
D-2→REQ-02→SC-01/02 (N-03/N-05), D-3→REQ-03→SC-04/05/06/14/16 (N-06/N-10/N-13),
D-4→REQ-04→SC-07 (N-07), D-5→REQ-05→SC-12 (N-09), M-1→REQ-06→SC-09/10/16 (N-02/N-13),
M-2→REQ-07→SC-11 (N-04/N-05). All present, none merged, none deferred, all fifteen criteria are
`verify: automated evidence: integration`. Coverage's 45-vs-48 ruling is internally consistent
across the BRIEF's own cycle-3/5/6 ledger accounting and the operator's own running counts in the
four answer files (36→42→41→45, each transition named). N-11 appears nowhere as live (its surviving
halves are explicitly folded into N-10 PART 6/7 per D-14); SC-15 appears nowhere as live (struck,
its criterion id left as a deliberate gap). `depends_on` is topological: N-13 (last-but-one) depends
on N-02/N-06/N-10; N-09 (last) depends on nearly everything. No orphan REQ id and no task tracing a
non-existent REQ found in this pass, beyond the already-graded L-01/L-02 stale anchors.

## Findings

None NEW beyond the six already carried by the goal-check. All six graded above and confirmed
correct at their stated severities. H-01 is a standing, unfixed high (per Q8 terms, correctly
deferred to operator signature rather than fixed this cycle) — that is what drives this review's
own VERDICT to FAIL under `severity_max >= high`, not a defect in the goal-check's handling of it.

```yaml
VERDICT: FAIL
DIGEST:
  headline: Nothing structural; goal-check's six findings all confirmed correctly graded (H-01 high/always-green — standing, unfixed per Q8; M-01 med/always-green; M-02 med/build-catches; L-01/L-02/L-03 low). No new high or critical found. severity_max is high solely because H-01 stands unresolved, matching the operator's own terms to present it, not fix it, this cycle.
  severity_max: high
  findings: 6
  must_fix: ["H-01 (goal-check finding, confirmed correct and unfixed): N-13 PART 1's red proof cannot redden against real data — staging the pre-fix derivation yields MISSING=[]/UNEXPECTED=10, which the loosened clause 1 tolerates, so the proof does not discriminate the pre-fix derivation from the shipped one; per operator Q8, present unfixed for signature/build-phase-task decision rather than spend the tenth cycle on it"]
  spec_violations: []
  code_grade: n_a
  reviewed: "plan:/Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-58-corpus-outside-worktree/.harness/harness/features/FEAT-58-corpus-outside-worktree/plan.yaml"
  human_commits_in_scope: []
  open_questions: []
  files_touched: []
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-58-corpus-outside-worktree/.harness/harness/features/FEAT-58-corpus-outside-worktree/notes/review-harness-code-reviewer-planpanel-c9.md
```
