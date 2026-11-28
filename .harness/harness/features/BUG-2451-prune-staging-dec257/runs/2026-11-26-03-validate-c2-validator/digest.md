# BUG-2451 · validate c2 — FAIL (one med must-fix; every SC and both perspectives met)

**Reviewed SHA:** b7e1f26ecfdff7683d25009435a30098c5580c52 (feature.json pin), worktree copy. Code delta c1→fix is 10823d58. The full diff is T-01's five files against 47d6c54d / e83c4e20; code-reviewer measured `e83c4e20..b7e1f26e` as the five product paths plus feature records. cycles_used 0 (no send-backs from this run). severity_max **med**.

**BLUF.** MF-1 is fixed. Four readers (qa, code, security, pm) confirm it independently, and the new `unreadable_ui_cases` test goes naturally RED against the b2c1f55e pruner. SC-01..SC-04, DEC-238 `amend` and all five `keep` rows are met, so both perspectives are met. The verdict is still FAIL on one item, **MF-2R**. The five-file forbidden-claim guard required by T-01's signed intent matches its phrases case-sensitively, so a sentence-initial `Force-stage retained records.` inserted into the ship text stays green. The shipped text itself is correct: this is a regression guard that is still weaker than T-01 requires, not a behaviour defect. The rework ruling is spent, so whether to accept this residual or grant another round is the operator's decision (OQ-A). Repo note: `.harness/harness.json` `gates.review: advisory_unless_high` means a med-only must-fix does not gate ship at the review gate. The FAIL here is this lead's gate rule (must_fix non-empty).

## Per-reader verdicts

| Step | Persona | Verdict | Note |
|---|---|---|---|
| qa | harness-qa | PASS | `notes/review-harness-qa-c2.md`; unit 68/68, receipt `qa/manifest-unit.json`; verify exit 0 |
| code | harness-code-reviewer | FAIL | `notes/review-harness-code-reviewer-c2.md`; MF-1 resolved, MF-2 residual (med); code_grade pass |
| security | harness-security-reviewer | PASS | `notes/review-harness-security-reviewer-c2.md`; MF-1 resolved; one low |
| ui | harness-ui-reviewer | PASS (scoped out) | `notes/review-harness-ui-reviewer-c2.md`; census: five non-UI files; `runs/*/ui/` is evidence storage |
| goalcheck | harness-pm | PASS | `notes/research-BUG-2451-prune-staging-dec257-goalcheck-validate-c2.md`; all SC, perspectives, dispositions met |

## c1 dispositions

- **MF-1 — resolved.** Code, security, qa and pm each ruled it resolved, and each measured it rather than reading. `_unreadable_dirs` (prune-run-evidence.py:159–188) no longer removes `ui/`, walks with `followlinks=False` and skips linked run entries, and the refusal precedes `_prune` in both modes. The test `unreadable_ui_cases` (test:362–410) passes at the pin. qa ran it against the b2c1f55e pruner as a whole bin tree (sha256 0237578f…): exit 1, 48 PASS / 4 FAIL. The four are: dry-run rc 0 with nothing named; prune ended in an rmtree traceback without naming the dirs; prune mutated files; whole-tree identity changed. The dry-run no-mutation leg cannot red naturally, because the old pruner never mutated in dry-run; mutants cover it.
- **MF-2 — partially resolved; the residual is MF-2R.** Three parts are fixed. Restoration is literal: test:673,679 compare char-for-char, and injected spaces red both surfaces (code). The pruner checks read TOOL: qa saw the subject's path named in FAIL output under override. All five files are read, and a lowercase forbidden phrase planted in each file reds the check (code). The residual is that `claims()` (test:614–617) does not case-fold, so `Force-stage …` passes; the lead confirmed this at source. A second, smaller gap: the DEC-257 exclusion is unconditional (`without(decisions, "\n## DEC-257 ", …)`), so a *changed* DEC-257 claim also passes, where intent exempts only *unchanged* DEC-257 text. Excluding the test's own FORBIDDEN literal is within intent ("tests that negatively assert absence").
- **QA-F1 — resolved for prune, residual (inherent) for dry-run.** The unhooked raw-index legs no longer depend on the audit hook. Dry-run cannot red naturally, because neither defective pruner staged in dry-run; mutants cover it.
- **QA-F2 — resolved.** The aggregate at test:278–282 always runs and prints FAIL. A form/low residual remains: its condition is broader than its label.
- **QA-F3 — resolved.** Whole-feature byte identity is restored (test:151–160, 233–237).
- **PASS count:** qa, pm and the orchestrator each measured **52** PASS / 0 FAIL at the pin. Main's 55 in `notes/red-first-T-01.md` `## c1 fix` is not reproduced by any reader. The record is wrong on that number.

## Contradiction resolved

qa ruled "MF-2 test side resolved", and code-reviewer ruled MF-2 residual. These do not conflict: qa's probes used the listed lowercase phrases, while code-reviewer's mutation used a capitalised variant. The lead read `claims()`: `phrase in " ".join(text.split())` has no case folding. Code-reviewer's ruling stands.

## Must-fix (one, against T-01)

1. **MF-2R · substance · med (code-reviewer) · T-01 intent "verification must reject forbidden positive claims in changed current text across the five owned files".** Two parts:
   - Case-fold the claim scan.
   - Limit the DEC-257 exclusion to text unchanged from base (or byte-equal to merge base).

   **Fix ordering:** a case-folded scan over the whole of DECISIONS.md and harness-ship.md widens pm's A-3 fail-closed brittleness. Measure the five current files for new false reds before landing. DECISIONS.md:8675 carries a lowercase `force-staging` inside DEC-257, so it is excluded today. Because the rework ruling is spent, this goes to the operator (OQ-A), not to a fix run.

## Advisory (not gating), ranked by irreversibility then severity

1. **Code-reviewer (substance, med, inherited), with pm A-1:** a recorded `ui/` leaf at 0400 or 0500 is listable but not searchable. Dry-run exits 0, and prune removes an earlier lane before `rmtree` raises. This is outside SC-02's letter ("unreadable"). The lane removed was prunable anyway, so the harm is a half-finished prune, not wrong deletion. Ranked first because the deletion is partial and cannot be undone.
2. **pm A-2 (inherited):** an unreadable dir in an *unrecorded* run's `ui/` is not walked. SC-02 scopes to recorded runs.
3. **Security (substance, low):** unreadable `ui/` directory names reach stderr unescaped (prune-run-evidence.py:179–180, 212–215). An embedded newline can forge a status line. The fix made this reachable; the refusal stays exit 1 and nothing is written.
4. **qa C2-F1 (substance, low, pre-existing):** "every" is discriminated only across runs. A per-run first-only mutant stays green (52/0). The code is correct today; the property is not pinned (P-08).
5. **qa C2-F2 (substance, low, pre-existing):** `followlinks=False` is untested; a mutant stays green. The failure would be fail-closed.
6. **qa QA-F2 residual (form, low):** the aggregate label is narrower than its condition.
7. **Form, low:** the 55-PASS claim in `notes/red-first-T-01.md` contradicts the measured 52.
8. **Security, inherited and dismissed again:** ancestor/TOCTOU containment and path echo in malformed-record errors. The security reviewer states the fix did not change them.

## Open questions

- **OQ-A (lead, blocking):** MF-2R is real, med, and inside T-01's files, but the rework ruling is spent. The operator has two options:
  - (a) Accept it as a recorded residual and ship. The review gate is `advisory_unless_high`, and the shipped text is correct today.
  - (b) Grant a narrow round for the case-fold and DEC-257-scope fix, with acceptance that a capitalised claim and a changed DEC-257 claim each go red and that no current text goes red.
- OQ-1 (pm, carried): DEC-225's wording should be clarified as intake-scoped. Out of scope.
- OQ-2 (pm): the `--root`-less hooked no-git path is behaviour-verified by pm probe P3 but untested. Backlog?
- A-3 (pm): the forbidden scan covers more than "changed current text", so a future unrelated `git add` in DECISIONS.md reds this unit test. This interacts with MF-2R's fix.

```yaml
VERDICT: FAIL
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2451-prune-staging-dec257/.harness/harness/features/BUG-2451-prune-staging-dec257/runs/2026-11-26-03-validate-c2-validator/digest.md
DIGEST:
  headline: "BUG-2451 at b7e1f26e: MF-1 is fixed, with a natural RED against b2c1f55e,\
    \ and every SC, both perspectives and all dispositions are met. Validation still\
    \ FAILs on one med must-fix, MF-2R: the forbidden-claim guard is case-sensitive,\
    \ so `Force-stage \u2026` passes. The rework round is spent, so it goes to the\
    \ operator (OQ-A). The review gate is advisory_unless_high."
  team: validate
  steps_run: 5
  cycles_used: 0
  members:
  - step: qa
    persona: harness-qa
    verdict: PASS
    headline: Unit 68/68 at the pin (receipt qa/manifest-unit.json) and T-01 verify
      exits 0. SC-01 RED reproduced against 47d6c54d (12 FAIL). SC-02 shows a natural
      RED against b2c1f55e (4 FAIL). MF-1, QA-F2 and QA-F3 are resolved; QA-F1 is
      resolved for prune. Measured 52 PASS.
    files_touched:
    - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2451-prune-staging-dec257/.harness/harness/features/BUG-2451-prune-staging-dec257/runs/2026-11-26-03-validate-c2-validator/qa/manifest-unit.json
    - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2451-prune-staging-dec257/.harness/harness/features/BUG-2451-prune-staging-dec257/observations/harness-qa.md
  - step: code
    persona: harness-code-reviewer
    verdict: FAIL
    headline: 'MF-1 resolved; MF-2 remains: the five-file guard passes an explicit
      force-staging instruction even though the pinned ship text is correct'
    files_touched: []
  - step: security
    persona: harness-security-reviewer
    verdict: PASS
    headline: 'MF-1 resolved: recorded UI directories are checked before mutation
      in both modes; one low diagnostic-integrity finding'
    files_touched: []
  - step: ui
    persona: harness-ui-reviewer
    verdict: PASS
    headline: 'Mode B scoped out after a measured census: all five files are non-UI,
      and runs/*/ui/ is evidence storage'
    files_touched: []
  - step: goalcheck
    persona: harness-pm
    verdict: PASS
    headline: Both perspectives are met and SC-01..SC-04 are met. The refusal sentence
      is now true of the code. DEC-238 amend and all 5 keep rows are met.
    files_touched: []
  must_fix:
  - 'MF-2R (T-01, substance, med per harness-code-reviewer; T-01 intent ''verification
    must reject forbidden positive claims in changed current text across the five
    owned files''). claims() in tests/unit/test-prune-run-evidence.py (around :614-617)
    matches FORBIDDEN without case-folding, so a sentence-initial ''Force-stage retained
    records.'' in the ship text stays green; code-reviewer showed this by in-memory
    mutation and the lead confirmed it at source. Also, the DEC-257 exclusion is unconditional,
    so a changed DEC-257 claim passes, while intent exempts only unchanged DEC-257
    text. Remedy: case-fold the scan, limit the exclusion to unchanged DEC-257 text,
    and measure the current five files for new false reds (pm A-3). The rework ruling
    is spent, so this is the operator''s decision (OQ-A), not a fix run.'
  files_touched:
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2451-prune-staging-dec257/.harness/harness/features/BUG-2451-prune-staging-dec257/runs/2026-11-26-03-validate-c2-validator/qa/manifest-unit.json
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2451-prune-staging-dec257/.harness/harness/features/BUG-2451-prune-staging-dec257/runs/2026-11-26-03-validate-c2-validator/state.yaml
  branch: none
  open_questions:
  - id: OQ-A
    question: '(lead) MF-2R is med, inside T-01''s files, and the rework ruling (1
      round / 45 min) is spent. Option (a): accept it as a recorded residual and ship.
      The review gate is advisory_unless_high, and the shipped text is correct today.
      Option (b): grant a narrow round. Acceptance would be that a capitalised forbidden
      claim and a changed DEC-257 claim each go red, and that no current text goes
      red. Which does the operator choose?'
    blocking: true
  - id: OQ-1
    question: (pm, carried from c1) Should DEC-225's 'no panel and no goal-check'
      wording be clarified as intake-scoped? This is out of this feature's scope.
    blocking: false
  - id: OQ-2
    question: (pm) The --root-less hooked no-git path was behaviour-verified by pm
      probe P3, but no test exercises it. Should a test be backlogged?
    blocking: false
  - id: OQ-3
    question: (pm A-3) The forbidden scan covers all of DECISIONS.md except DEC-257,
      plus all of harness-ship.md. That is wider than 'changed current text', so a
      future unrelated 'git add' in DECISIONS.md would turn this unit test red. Should
      the scan be narrowed? This interacts with MF-2R's remedy.
    blocking: false
  - id: OQ-4
    question: (code-reviewer advisory + pm A-1/A-2) Two inherited permission edges
      sit outside SC-02's letter. (1) A recorded ui/ leaf at 0400 or 0500 is listable
      but not searchable, so prune removes an earlier lane before rmtree raises. (2)
      An unreadable directory in an unrecorded run's ui/ is not walked. Should either
      be backlogged?
    blocking: false
  escalations: []
  expertise_update: []
  adequacy_notes:
  - 'Reviewed SHA: b7e1f26ecfdff7683d25009435a30098c5580c52, worktree copy. Code delta
    from c1 is 10823d58. code-reviewer measured e83c4e20..b7e1f26e as T-01''s five
    product paths plus feature records.'
  - 'MF-1 is resolved. Four readers measured it independently. Evidence: prune-run-evidence.py:159-188
    walks ui/ with followlinks=False, and the refusal precedes _prune in both modes.
    The unreadable_ui_cases test (test:362-410) passes at the pin. Against the b2c1f55e
    pruner it fails naturally: exit 1, 48 PASS / 4 FAIL. The dry-run no-mutation leg
    cannot red naturally; mutants cover it.'
  - 'MF-2: three parts are resolved: the restoration check is literal (test:673,679),
    the pruner checks are bound to TOOL, and all five files are scanned for lowercase
    phrases. The case-sensitivity and unconditional-DEC-257-exclusion parts remain
    as MF-2R. The test''s own FORBIDDEN-literal exclusion is within intent.'
  - 'qa ruled ''MF-2 test side resolved'' and code-reviewer ruled residual. The lead
    resolved this for code-reviewer: qa probed only lowercase listed phrases, and
    claims() has no case-folding.'
  - 'QA-F1: resolved for prune; residual for dry-run, where it is inherent (no defective
    pruner mutated in dry-run). QA-F2: resolved; a low form residual remains because
    the aggregate label is narrower than its condition. QA-F3: resolved; whole-feature
    byte identity is restored.'
  - 'PASS count: qa, pm and the orchestrator each measured 52 PASS / 0 FAIL at the
    pin. Main''s 55 in notes/red-first-T-01.md ''## c1 fix'' is not reproduced, so
    the record is wrong on that number.'
  - QA receipts come from this host's interpreter, not CI.
  - 'Gate: FAIL because must_fix is non-empty (lead rule). In this repo, harness.json
    gates.review is advisory_unless_high, so a med-only must-fix does not gate ship
    at the review gate. Every SC and both perspectives are met; the FAIL rests only
    on a T-01 verification-intent requirement, not on shipped behaviour.'
  - 'Operator decision needed: accept MF-2R as a residual or grant a narrow round
    (OQ-A); recorded as open question, needs_approval true.'
  - T-01 is main-session-direct (DEC-174, DEC-179). Nothing was sent back from this
    run because the rework ruling is spent.
  - 'Dismissed again as inherited and unchanged by the fix (security reviewer): ancestor/TOCTOU
    containment, and absolute-path echo in malformed-record errors.'
  sc_status:
  - id: PERSPECTIVE-operator
    verdict: met
    method: inspection
    evidence: SC-02 and SC-03 are met. The refusal sentence on both restored surfaces
      is now true of the code (pm, code-reviewer, security-reviewer).
  - id: PERSPECTIVE-code-maintainer
    verdict: met
    method: automated
    evidence: 'SC-01 and SC-04 are met. The test reds against 47d6c54d (12 FAIL) and
      b2c1f55e (4 FAIL) and is green at the pin, 52/0 (qa, pm). MF-2R qualifies this:
      the regression guard for the restored text is case-sensitive.'
  - id: SC-01
    verdict: met
    method: automated
    evidence: "qa ran the pin's test with PRUNE_RUN_EVIDENCE_BIN set to the 47d6c54d\
      \ pruner (sha256 55df0581\u2026): exit 1, 40 PASS / 12 FAIL, all assertions.\
      \ This includes 'pruner invokes no git subprocess' and an index change from\
      \ 9148 to 8663 bytes. The test is green at the pin. Receipt: runs/2026-11-26-03-validate-c2-validator/qa/manifest-unit.json."
  - id: SC-02
    verdict: met
    method: automated
    evidence: '_unreadable_dirs walks ui/ with no link following, and the refusal
      precedes _prune in both modes (prune-run-evidence.py:159-188,208-216). unreadable_ui_cases
      has a natural RED against b2c1f55e: 4 FAIL, among them dry-run rc 0 with nothing
      named and prune ending in an rmtree traceback. qa, code-reviewer, security-reviewer
      and pm agree.'
  - id: SC-03
    verdict: met
    method: inspection
    evidence: DECISIONS.md:8152 and harness-ship.md:47-56 each equal their 5e51124e
      text plus exactly one refusal sentence (literal diff; pm, code-reviewer). The
      index regenerates identically. fix-c1 changed no text surface. The guard residual
      is tracked separately as MF-2R.
  - id: SC-04
    verdict: met
    method: inspection
    evidence: The fix-c1 pruner diff touches only the docstring and _unreadable_dirs.
      The CLI, keep set, UI-only deletion, symlink handling and --keep/pin code are
      unchanged. harness-ship.md is byte-identical to the c1 pin (pm, code-reviewer).
  - id: DEC-238
    verdict: met
    method: inspection
    evidence: 'The amend matches D-01: the DECISIONS.md:8152 bullet equals 5e51124e
      plus one sentence and is the only DECISIONS.md hunk. The index row regenerates.
      Owner T-01 (pm).'
  - id: DEC-174
    verdict: met
    method: inspection
    evidence: 'keep: text untouched at the pin (DECISIONS.md:4521) (pm).'
  - id: DEC-179
    verdict: met
    method: inspection
    evidence: 'keep: text untouched at the pin (DECISIONS.md:4851) (pm).'
  - id: DEC-225
    verdict: met
    method: inspection
    evidence: 'keep: text untouched at the pin (DECISIONS.md:7511). The wording tension
      is recorded as OQ-1 (pm).'
  - id: DEC-254
    verdict: met
    method: inspection
    evidence: 'keep: text untouched at the pin (DECISIONS.md:8423) (pm).'
  - id: DEC-257
    verdict: met
    method: inspection
    evidence: 'keep: the body is byte-identical to the merge base, and only the index
      row''s line anchor moved (pm, code-reviewer).'
  needs_approval: true
  severity_max: med
  matrix_ok: true
  coverage_gaps:
  - 'qa C2-F1: ''every'' is discriminated only across runs. A per-run first-only mutant
    in _unreadable_dirs stays green (52/0). The code is correct today but the property
    is not pinned.'
  - 'qa C2-F2: the no-follow-links property of the unreadable walk is untested. A
    followlinks=True mutant stays green; that failure would be fail-closed.'
  - 'QA-F1 residual (inherent): the dry-run index and immutability legs have no natural
    RED; only mutants discriminate them.'
  - No test exercises the --root-less hooked no-git path (pm OQ-2).
  - 'MF-2R: the forbidden-claim guard does not catch case variants or changed DEC-257
    text.'
  findings:
  - kind: substance
    scope: none
    severity: med
    reader: harness-code-reviewer
    summary: 'T-01 (MF-2R): the five-file forbidden-claim guard is case-sensitive
      and excludes DEC-257 unconditionally'
    why: Inserting 'Force-stage retained records.' into the ship introduction leaves
      the aggregate check green, and so does a new broad-ignore claim inside DEC-257's
      body. This falls short of T-01's signed intent that verification reject forbidden
      positive claims in changed current text. The pinned text is correct today.
  - kind: substance
    scope: none
    severity: med
    reader: harness-code-reviewer (pm A-1 concurs)
    summary: 'T-01 advisory, inherited: a listable but non-searchable recorded ui/
      leaf (0400) causes partial pruning'
    why: 'Measured: dry-run exited 0, and normal mode removed an earlier lane before
      rmtree raised PermissionError. The directory is not ''unreadable'' in SC-02''s
      sense, so this is outside the criterion and not a gate.'
  - kind: substance
    scope: none
    severity: low
    reader: harness-security-reviewer
    summary: 'T-01: unreadable ui/ directory names are emitted to stderr without escaping'
    why: A local writer controlling a recorded ui/ directory name can forge a status
      line with an embedded newline (prune-run-evidence.py:179-180,212-215). The fix
      made this reachable from ui/ descendants; the refusal remains exit 1 and nothing
      is written.
  - kind: substance
    scope: none
    severity: low
    reader: harness-qa
    summary: 'T-01 C2-F1: the per-run ''every unreadable directory'' property is not
      discriminated'
    why: Every fixture run holds one unreadable directory, so a mutant that keeps
      only the first error per run stays green. The code is correct today.
  - kind: substance
    scope: none
    severity: low
    reader: harness-qa
    summary: 'T-01 C2-F2: the unreadable walk''s no-follow-links property is untested'
    why: Every linked fixture target is readable, so a followlinks=True mutant stays
      green. The failure would be fail-closed (over-refusal).
  - kind: form
    scope: none
    severity: low
    reader: harness-qa
    summary: 'T-01 QA-F2 residual: the ''index is byte-identical'' aggregate label
      is narrower than its condition'
    why: The aggregate also covers the subprocess, staging and behaviour legs, so
      a FAIL on it can misattribute the cause.
  - kind: form
    scope: none
    severity: low
    reader: harness-qa, harness-pm
    summary: notes/red-first-T-01.md '## c1 fix' claims 55 PASS, but three independent
      measurements give 52
    why: The fix author's record carries a count no reader reproduced. The honest
      record should state the measured count.
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
