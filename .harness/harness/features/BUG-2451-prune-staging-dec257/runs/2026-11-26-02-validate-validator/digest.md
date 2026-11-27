# BUG-2451 · validate c1 — FAIL

**Reviewed SHA:** b2c1f55e89bc20a9ef397cb183452270548aa3ee (feature.json pin), diff 47d6c54d..b2c1f55e on T-01's five files only. cycles_used 0 (no send-backs). severity_max **high**.

**BLUF.** The staging removal works: the unit matrix is green, RED against 47d6c54d was reproduced independently, and the DEC-238 and ship text restoration matches its source exactly. Validation still FAILs on one blocking defect. The pre-mutation unreadable-directory refusal skips each recorded run's `ui/` subtree, so SC-02's "EVERY unreadable directory under recorded runs" is not met. The refusal sentence this feature added to DECISIONS.md and harness-ship.md now promises behaviour the code does not have. A second, cheaper must-fix concerns the five-file test: it is weaker than T-01's intent requires.

## Per-reader verdicts

| Step | Persona | Verdict | Note |
|---|---|---|---|
| qa | harness-qa | PASS | `notes/review-harness-qa-c1.md`; 3 low advisories |
| code | harness-code-reviewer | FAIL | `notes/review-harness-code-reviewer-c1.md`; high + med; code_grade pass |
| security | harness-security-reviewer | FAIL | `notes/review-harness-security-reviewer-c1.md`; med (same defect as code #1) |
| ui | harness-ui-reviewer | PASS (self-scoped out) | `notes/review-harness-ui-reviewer-c1.md`; measured per-file census, no rendered UI |
| goalcheck | harness-pm | PASS → lead overrides SC-02 | `notes/research-BUG-2451-prune-staging-dec257-goalcheck-validate-c1.md` |

## Matrix and fail-first (qa)

- change_type bugfix requires `unit` only. It is satisfied: run-unit-tests exit 0, 68/68 files. Receipt: `runs/2026-11-26-02-validate-validator/qa/manifest-unit.json`. T-01's `verify:` exited 0 at the pin. Ran on this host's interpreter, not CI.
- SC-01: QA reproduced RED itself against the 47d6c54d pruner: exit 1, 5 assertion FAILs. These include `pruner invokes no git subprocess` and the unhooked complete-evidence index case (index grows from 266 to 2004 bytes).
- SC-02: the 47d6c54d pruner already had both checks, so it gives no natural RED. QA used mutants M1–M6 instead, and each one turns one leg's test RED. This covers only the legs the tests exercise. No leg exercises `ui/`, which is how the blocking defect got past it.

## Goal-check (pm), as ruled by the lead

- **operator → partial** (pm: met). SC-03 is met. SC-02 is not met; see MF-1.
- **code maintainer → met.** SC-01 and SC-04 are met. QA-F1 qualifies this: only one index leg has a natural RED.
- Decision dispositions: DEC-238 `amend` is met; the bullet equals 5e51124e plus one sentence, and the index regenerates identically. All five `keep` rows (DEC-174, 179, 225, 254, 257) are met, with their text untouched at the pin.

## Must-fix (ranked, ordered; all against T-01, remedied by Main under the rework ruling — no hosted fix)

1. **MF-1 · substance · high (code-reviewer) / med (security-reviewer) · SC-02.** Raised by both readers; the lead confirmed it at source. `_unreadable_dirs` in prune-run-evidence.py runs `dirs.remove("ui")` at the top of each recorded run, and its docstring says "outside its ui/". The result: an unreadable directory under a recorded run's `ui/` is never named. Dry-run exits 0. Normal mode can delete earlier lanes and then fail inside `rmtree` without having refused first. The exclusion was inherited from the 47d6c54d staging walk, but the signed SC-02 and the newly added refusal sentence both say *every*. Fix:
   - Walk `ui/` too, without following links.
   - Add a test with multiple unreadable `ui/` directories and a separate prunable lane, in both modes, checking that files and index are unchanged.
   - Keep the symlink skips.

   Severity reconciliation: both ratings are transcribed. The lead's reading of impact is bounded: the data at risk was already slated for deletion and is tracked by git. Even so, the verdict is FAIL because a must-fix exists, so the high/med split does not change routing.
2. **MF-2 · substance · med (code-reviewer) · SC-03 regression guard / T-01 intent.** T-01's intent asks the five-file check for "exact historical text" and "changed text across all five files", and the check falls short in three places:
   - test:519 folds whitespace before comparing.
   - The absence scan covers selected regions only.
   - test:546 reads `BIN/prune-run-evidence.py` instead of `TOOL`, so the docstring assertion never reads the subject under override. red-first-T-01.md RED-2 records this as well.

   The shipped text is correct today (the code reviewer and pm both inspected it), so this is pinned-against-regression, not correct-today. Fix it after MF-1, in the same file.

## Advisory (not gating)

- QA-F1 (substance, low): the hooked per-mode index legs PASS on 47d6c54d. Index RED exists only in the unhooked normal-mode case, and dry-run has no natural index RED (47d6c54d's dry-run never staged).
- QA-F2 (form, low): the `PASS - real temporary git repository index is byte-identical` line is printed only when every leg passes. It never prints a FAIL line of its own, though the per-mode FAIL lines still do.
- QA-F3 (substance, low): the dry-run byte-identity check was narrowed from the whole feature tree to `runs/` only. A dry-run that rewrote feature.json would go unseen. This is a small loss of non-staging coverage; fold it in with MF-1 if cheap.
- Security, assessed and dismissed as inherited and unchanged since 47d6c54d, not regressions: ancestor/TOCTOU containment, and absolute paths echoed in malformed-record errors.
- pm A-3 / OQ-2: the default `--root` path has no hooked no-git case.
- UI: none.

## Open questions (non-blocking)

- OQ-1 (pm): should DEC-225's "no panel and no goal-check run" clause be clarified as intake-scoped?
- OQ-2 (pm): should a backlog chore add a `--root`-less hooked no-git case?
- OQ-3 (lead): MF-1's only alternative to the letter fix is to narrow the signed SC-02 and the D-01 sentence to exclude `ui/`. That would amend signed text and is the operator's call. The lead recommends the letter fix because it is cheap and stays inside T-01's files.

Scope-change candidates: none raised. Diff measured by readers: `e83c4e20..b2c1f55e` is the five files plus the feature dir.

```yaml
VERDICT: FAIL
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2451-prune-staging-dec257/.harness/harness/features/BUG-2451-prune-staging-dec257/runs/2026-11-26-02-validate-validator/digest.md
DIGEST:
  headline: 'BUG-2451 at b2c1f55e: staging removal is green and the text restoration
    is exact, but validation FAILs: the unreadable-directory refusal skips recorded
    ui/ trees, so SC-02 ''every'' and the newly added refusal sentence are false (MF-1);
    the five-file test is weaker than T-01''s intent (MF-2)'
  team: validate
  steps_run: 5
  cycles_used: 0
  members:
  - step: qa
    persona: harness-qa
    verdict: PASS
    headline: unit matrix satisfied at the pin (68/68, receipt qa/manifest-unit.json,
      verify exit 0); SC-01 RED reproduced independently against 47d6c54d; SC-02 legs
      turned RED under scratch mutants; 3 low advisories
    files_touched:
    - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2451-prune-staging-dec257/.harness/harness/features/BUG-2451-prune-staging-dec257/runs/2026-11-26-02-validate-validator/qa/manifest-unit.json
  - step: code
    persona: harness-code-reviewer
    verdict: FAIL
    headline: T-01 skips unreadable recorded UI trees and its five-file check accepts
      literal drift and forbidden claims
    files_touched: []
  - step: security
    persona: harness-security-reviewer
    verdict: FAIL
    headline: T-01 skips unreadable recorded UI directories, violating SC-02's pre-mutation
      refusal
    files_touched: []
  - step: ui
    persona: harness-ui-reviewer
    verdict: PASS
    headline: 'Mode B scoped out after a measured per-file census: none of the five
      files changes rendered UI'
    files_touched: []
  - step: goalcheck
    persona: harness-pm
    verdict: PASS
    headline: operator and code maintainer graded met; DEC-238 amend landed exactly;
      5 keep rows untouched (the lead overrides SC-02 to not_met)
    files_touched: []
  must_fix:
  - 'MF-1 (T-01, substance, high per harness-code-reviewer / med per harness-security-reviewer,
    SC-02): _unreadable_dirs in .claude/skills/harness/bin/prune-run-evidence.py does
    dirs.remove(''ui'') at each recorded run''s top level, so unreadable directories
    under recorded ui/ trees are never named. Dry-run exits 0, and normal mode can
    delete lanes and then fail in rmtree without refusing first. Fix: walk ui/ too
    without following links, keep the symlink skips, and add a regression with multiple
    unreadable ui/ directories plus a separate prunable lane in both modes, asserting
    exit 1, every directory named, and files and index unchanged.'
  - 'MF-2 (T-01, substance, med per harness-code-reviewer, SC-03 regression guard
    / T-01 intent): the five-file check in tests/unit/test-prune-run-evidence.py folds
    whitespace (test:519), scans only selected regions, and reads BIN/prune-run-evidence.py
    rather than TOOL (test:546). Fix: make restoration checks literal, cover changed
    current text across all five files, and bind the pruner assertions to the selected
    subject. Order this after MF-1, in the same file.'
  files_touched:
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2451-prune-staging-dec257/.harness/harness/features/BUG-2451-prune-staging-dec257/runs/2026-11-26-02-validate-validator/qa/manifest-unit.json
  branch: none
  open_questions:
  - id: OQ-1
    question: (pm) Should DEC-225's 'with no panel and no goal-check run' clause be
      clarified as intake-scoped, so no later reader cites it to skip validate disposition
      grading? This is out of this feature's scope.
    blocking: false
  - id: OQ-2
    question: (pm) Should a backlog chore add a --root-less hooked no-git case? The
      ship invocations omit --root, and the default root path is git-free by inspection
      only.
    blocking: false
  - id: OQ-3
    question: (lead) MF-1's only alternative to the letter fix is to narrow the signed
      SC-02 and the D-01 refusal sentence to exclude ui/, which amends signed text.
      The lead recommends the letter fix, which is cheap and inside T-01's files.
      Does the operator agree?
    blocking: false
  escalations: []
  expertise_update: []
  adequacy_notes:
  - Reviewed SHA b2c1f55e89bc20a9ef397cb183452270548aa3ee; the readers measured e83c4e20..b2c1f55e
    as the five T-01 files plus the feature dir only.
  - QA receipts come from this host's interpreter, not CI.
  - 'SC-02 fail-first is mutation-tier only: the 47d6c54d pruner already had both
    checks. The mutants cover only the legs the tests exercise, and none exercises
    ui/, which is how MF-1 passed qa and pm.'
  - pm graded SC-02 and the operator perspective met. The lead overrides SC-02 to
    not_met and the operator perspective to partial, after confirming the ui exclusion
    at source.
  - 'Gate: the verdict is FAIL because must_fix is non-empty. The high/med split on
    MF-1 does not change routing. The lead''s view is that impact is bounded: the
    affected data was already slated for deletion and is git-tracked.'
  - T-01 is main-session-direct (DEC-174, DEC-179). Both must-fixes go to Main under
    the rework ruling (1 round / 45 min); no hosted fix run exists.
  - 'Dismissed as inherited and unchanged since 47d6c54d: the security reviewer''s
    ancestor/TOCTOU containment and absolute-path echo in malformed-record errors.'
  - All five findings are against task T-01 (task-scoped); the scope field reads none
    per the contract.
  sc_status:
  - id: PERSPECTIVE-operator
    verdict: partial
    method: inspection
    evidence: pm graded met; the lead rules partial because SC-03 is met but SC-02
      is not met (MF-1)
  - id: PERSPECTIVE-code-maintainer
    verdict: met
    method: inspection
    evidence: SC-01 and SC-04 met (pm, qa, code-reviewer); qualified by QA-F1
  - id: SC-01
    verdict: met
    method: automated
    evidence: 'qa''s own run against 47d6c54d: exit 1, 5 assertion FAILs incl. ''pruner
      invokes no git subprocess'' and the unhooked index case (266 to 2004 bytes);
      GREEN at the pin; receipt runs/2026-11-26-02-validate-validator/qa/manifest-unit.json'
  - id: SC-02
    verdict: not_met
    method: automated
    evidence: the tests pass, but prune-run-evidence.py _unreadable_dirs excludes
      recorded ui/ subtrees (code-reviewer prune-run-evidence.py:172-184, security-reviewer,
      confirmed by the lead), and the only tests use qa/ paths (test:303-329). pm's
      'met' is overridden.
  - id: SC-03
    verdict: met
    method: inspection
    evidence: DECISIONS.md:8152-8162 and harness-ship.md:47-56 equal their 5e51124e
      text plus one sentence at character level (code-reviewer); gen-decisions-index
      --stdout equals DECISIONS-INDEX.md at the pin
  - id: SC-04
    verdict: met
    method: inspection
    evidence: CLI, keep, BUG-2294, symlink and --keep/pin code unchanged from 47d6c54d;
      ship step position, invocations and commit name preserved (code-reviewer, pm)
  - id: DEC-238
    verdict: met
    method: inspection
    evidence: amend matches D-01 exactly at b2c1f55e DECISIONS.md:8152-8162; index
      row regenerates; owning task T-01 (pm)
  - id: DEC-174
    verdict: met
    method: inspection
    evidence: text untouched at the pin; T-01 built main-session-direct (pm)
  - id: DEC-179
    verdict: met
    method: inspection
    evidence: text untouched; all 5 paths declared before signature (pm)
  - id: DEC-225
    verdict: met
    method: inspection
    evidence: text untouched; intake had no panel (pm); wording tension recorded as
      OQ-1
  - id: DEC-254
    verdict: met
    method: inspection
    evidence: text untouched; five-field rows with single owner T-01 (pm)
  - id: DEC-257
    verdict: met
    method: inspection
    evidence: text untouched; pruner runs no git (pm, qa)
  needs_approval: none
  severity_max: high
  matrix_ok: true
  coverage_gaps:
  - No test exercises an unreadable directory under a recorded ui/ tree (MF-1).
  - 'QA-F1: the hooked per-mode index legs PASS on 47d6c54d; index RED exists only
    in the unhooked normal-mode case, and dry-run has no natural index RED.'
  - 'QA-F3: the dry-run byte-identity check narrowed from the whole feature tree (incl.
    feature.json) to runs/ only.'
  findings:
  - kind: substance
    scope: none
    severity: high
    reader: harness-code-reviewer, harness-security-reviewer (med)
    summary: 'T-01 / SC-02 (MF-1): the unreadable-directory preflight excludes recorded
      ui/ subtrees'
    why: dirs.remove('ui') in _unreadable_dirs means dry-run exits 0 and normal mode
      can delete lanes before rmtree fails, without the promised pre-mutation refusal.
      This contradicts the signed SC-02 and the newly added refusal sentence.
  - kind: substance
    scope: none
    severity: med
    reader: harness-code-reviewer
    summary: 'T-01 / SC-03 guard (MF-2): the five-file check is not literal, covers
      selected regions only, and reads BIN instead of TOOL'
    why: A whitespace change to the restored text, or a forbidden claim added outside
      the scanned regions, still passes, so the regression guard is weaker than T-01's
      intent requires.
  - kind: substance
    scope: none
    severity: low
    reader: harness-qa
    summary: 'T-01 QA-F1: the index-byte-identical leg has a natural RED only in the
      unhooked normal-mode case'
    why: The audit hook blocks git add before the index changes, so the hooked per-mode
      index assertions alone do not discriminate the defect. Advisory.
  - kind: form
    scope: none
    severity: low
    reader: harness-qa
    summary: 'T-01 QA-F2: the byte-identical PASS line is emitted only when all legs
      pass and never prints FAIL'
    why: A tally of FAIL lines would miss an index regression; the verify grep and
      the per-mode FAIL lines still catch it. Advisory.
  - kind: substance
    scope: none
    severity: low
    reader: harness-qa
    summary: 'T-01 QA-F3: the dry-run immutability check narrowed to runs/ files'
    why: A dry-run that rewrote feature.json would pass; the pruner has no such writer
      today. Advisory; fold in with MF-1 if cheap.
  readers:
  - reader: qa
    status: ran
    persona: harness-qa
    reason: none
  - reader: code
    status: ran
    persona: harness-code-reviewer
    reason: none
  - reader: security
    status: ran
    persona: harness-security-reviewer
    reason: none
  - reader: ui
    status: ran
    persona: harness-ui-reviewer
    reason: none
  - reader: goalcheck
    status: ran
    persona: harness-pm
    reason: none
```
