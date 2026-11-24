# Validate c4 (rework round 3 of 3, the last): FEAT-2488 plan-merge atomicity: ESCALATE

**BLUF.** At review_sha `6528b4db2f0725c6051bae22099aa064b23336bb` (base `2491336e`, delta `0ab2c053..6528b4db`),
MF-9 is closed as ruled, and MF-10 is closed for the two names the ruling listed. CI is green with
PYTHONUNBUFFERED stripped: unit 68/68 and integration 95/95, with DEC-255 receipts in `qa/`. SC-01..07 are met and
all three perspectives pass.

Two findings still gate, and both are in surfaces this feature changed. Under the ruling's constraint ("a new high
in a changed surface returns to the advisor"), they go to fable-advisor. No rework round remains.

- **MF-11, T-02, high (code-reviewer), measured.** If a caller starts either amendment CLI with fd 1 closed, the
  amendment lands but the verb exits 1.
- **MF-12, T-01, contested: security rates it high, QA rates it med, I rate it med.** The journal names that
  recovery discovers are a wider set than the names check-domain denies.

Readers: qa PASS, goal-check PASS, ui PASS (scoped out after measuring 156 paths base..pin and 36 in the delta),
code-reviewer FAIL, security-reviewer FAIL.

## Closure of the round-3 items

|Item|Status at pin|Who measured|
|---|---|---|
|MF-9 (buffered broken stdout/stderr → rc 120)|**closed**. 2488/k, l and m are green when the child runs with PYTHONUNBUFFERED stripped. The pre-fix guards.py gives rc 120. A `_silence` no-op mutant turns l and m red|qa (aed85ace blobs + mutant), pm (mutants A/B, each red on one case only), code (re-ran its own c3 probe: rc 0, including when both streams are broken)|
|MF-10 (governed Write of the two sidecar names)|**closed for both literal names** on all four routes: as typed, case-folded, symlink and hardlink. T-09 13 is red against aed85ace's check-domain (8 FAILs). The drift-pin mutant also goes red|qa, pm, security (fixture)|
|T-01 ledgered amendment (files + intent)|truthful. The signature stands with no APPROVAL-RESET|pm|
|6b22caef test splits|the assertion multisets are identical (29/29, 73/73, 539–555/539–555)|qa, pm (AST)|
|C4 forbidden surfaces|untouched|pm, builder `c4-diff.txt`|

## Must-fix (ranked; both go to fable-advisor under the ruling)

1. **MF-11, T-02, high (code-reviewer), substance, changed surface.** `guards._print_receipts` calls
   `sys.stdout.flush()` unconditionally (`plan_merge/guards.py:315`). A CLI started with fd 1 closed has
   `sys.stdout is None`, so the call raises AttributeError, which is outside the `(OSError, ValueError)` catch.
   The result: both files are amended once, no journal is left, and the process exits 1.

   This is the same claim MF-9 delivered — "the verb still exits 0" (T-02 amendment 7, and SC-01's
   advisory-after-commit clause) — failing on a third stream state. At base, `print()` to a None stdout is a
   silent no-op. The explicit flush came in with this feature (d983f6c5) and was revised in fc69c032.

   I opened `:308-320` and confirmed the unguarded flush and the catch tuple. The code-reviewer executed the exit
   code. Retry risk: a caller that sees rc 1 after a commit may retry, which would amend twice.

2. **MF-12, T-01, contested severity (security high, QA med; my rating med), substance, changed surface.**
   - **The gap.** check-domain denies only `plan.yaml.harness-merge.journal` and
     `feature.json.harness-merge.journal` (fc69c032, `check-domain.py:2610-2624`). Discovery is wider:
     `harness_merge._journals_naming` (`:413-422`) picks up **every** entry ending in `JOURNAL_SUFFIX`, and
     `_journal_names` (`:402-410`) treats an unreadable journal as naming every file. I confirmed both sites.
   - **QA's measurement.** A harness-orchestrator Write of `evil.harness-merge.journal` exits 0. After that,
     `locked_update(plan.yaml)` and `locked_update(feature.json)` both refuse with exit 5 until a human removes
     the file.
   - **What remains open.** The forge route stays closed, because replay of a non-pair name is refused. What
     remains is the wedge/DoS route. The ruling widened MF-10 to the second name specifically for that route.
   - **Why I rate it med, not high.** It is availability-only. It is recoverable by deleting one file. The same
     wedge is reachable through the already-backlogged Bash route.
   - **Why I still gate it (P-04).** It is the residue of a ruled remedy, in a changed surface. The advisor ruled
     the wedge in scope, so the advisor decides whether the two-name remedy as ruled is enough. Both ratings are
     carried.
   - **Remedy candidates.**
     - Deny the whole `*.harness-merge.journal` suffix in the feature-dir grammar. This is check-domain only and
       inside T-01's amended files.
     - Narrow discovery to `JOURNAL_PAIR` names. This is harness_merge and touches the C5 journal surface.

**Fix order, if any round is granted.** MF-12's remedy choice is independent of MF-11. MF-11 should land together
with the `_silence` robustness note below, because both are in the same `guards.py` receipt helper.

## Assessed, not gating

- **Code med (T-02, changed, fc69c032): `_silence` robustness.**
  - When the replacement stdout is a real stream on a caller-owned fd 4, `_silence` dup2s /dev/null over fd 4.
  - A capture object that has no `fileno` raises AttributeError before the "landed" note is written.
  - This affects in-process callers only, since the CLI's own streams are fds 1 and 2.
  - The MF-11 fix should cover both cases, because the helper is the same.
- **Security med (T-01, static only): main-rooted hardlink detection.** It scans feature dirs under the gate's own
  checkout, not under the assigned linked worktree. The anchoring is pre-existing; this feature applies it to the
  new sidecar boundary. It needs an existing alias plus an in-place write, and nobody executed it. This is backlog
  unless the advisor folds it into MF-12.
- **Code low (T-01): RE_PAIR_JOURNAL's `$`** also matches a basename that ends with a newline. The error is in the
  over-denial (fail-closed) direction. Not gating.
- **QA coverage gaps.**
  - T-09 13 sends only Write. The Edit and NotebookEdit denials were checked by reading the code only.
  - T-01's literal `verify:` does not run test-check-domain-approval.py. Only the integration kind exercises
    MF-10.
  - SC-07 preservation shows no discrimination.
- **pm: 2 form advisories** (see the goal-check note).
- **Previously ruled items were not re-raised:** OQ-3, QA A2, A3, the c1 advisories, Bash porosity and
  sanitization.

## Adequacy

- QA's `suite: pass` rests on DEC-255 receipts `qa/manifest-unit.json` (68) and `qa/manifest-integration.json`
  (95). Both were run under `env -u PYTHONUNBUFFERED`, and the discovery counts are non-zero and unchanged.
  This closes the c3 adequacy gap that hid MF-9.
- MF-11 is a third stream state, a missing stream as opposed to a closed or broken one. No reader's suite covers
  it, and only the code-reviewer's probe reached it (P-06).

Members' artifacts: `notes/review-harness-{qa,code-reviewer,security-reviewer,ui-reviewer}-c4.md` and
`notes/research-FEAT-2488-plan-merge-atomicity-goalcheck-validate-c4.md`.

```yaml
VERDICT: ESCALATE
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2488-plan-merge-atomicity/.harness/harness/features/FEAT-2488-plan-merge-atomicity/runs/r-20261124-5-validate-validator/digest.md
DIGEST:
  headline: 'ESCALATE to fable-advisor at 6528b4db. MF-9 is closed and MF-10 is closed
    for both ruled names. CI is green with PYTHONUNBUFFERED stripped (unit 68, integration
    95) and SC-01..07 are met. Two findings in changed surfaces still gate: MF-11
    (T-02, high, measured), where a CLI started with fd 1 closed exits 1 after committing,
    and MF-12 (T-01, rated high by security and med by QA and the lead), where any
    other *.harness-merge.journal name wedges plan and feature writes at exit 5.'
  team: validate
  steps_run: 5
  cycles_used: 0
  members:
  - step: qa
    persona: harness-qa
    verdict: PASS
    headline: 'Matrix green with PYTHONUNBUFFERED stripped: unit 68/68 and integration
      95/95, runner exit 0. MF-9 and MF-10 closed by natural reds at aed85ace plus
      mutants. New med N-1: other journal names still wedge writes.'
    files_touched:
    - .harness/harness/features/FEAT-2488-plan-merge-atomicity/runs/r-20261124-5-validate-validator/qa/manifest-unit.json
    - .harness/harness/features/FEAT-2488-plan-merge-atomicity/runs/r-20261124-5-validate-validator/qa/manifest-integration.json
    - .harness/harness/features/FEAT-2488-plan-merge-atomicity/observations/harness-qa.md
  - step: code
    persona: harness-code-reviewer
    verdict: FAIL
    headline: 'New T-02 high: with fd 1 closed, both amendment CLIs exit 1 after committing
      (sys.stdout is None and guards.py:315 flushes it). The buffered broken-pipe
      probes now exit 0. Code grade: pass.'
    files_touched: []
  - step: security
    persona: harness-security-reviewer
    verdict: FAIL
    headline: Both exact sidecar names are denied. Recovery still discovers unreserved
      *.harness-merge.journal names that halt plan and feature writes (high). Hardlink
      coverage for linked worktrees is incomplete (med, static only).
    files_touched: []
  - step: ui
    persona: harness-ui-reviewer
    verdict: PASS
    headline: 'Mode B scoped out: of 156 paths base..pin and 36 in the delta, none
      is UI.'
    files_touched: []
  - step: goalcheck
    persona: harness-pm
    verdict: PASS
    headline: All 3 perspectives pass and SC-01..07 are met. MF-9's 'exits 0' is true
      under buffered stdio. The T-01 amendment is truthful and the signature stands.
      Round 3 stayed in scope and C4 is untouched.
    files_touched: []
  must_fix:
  - 'MF-11 (T-02, high, harness-code-reviewer, substance, changed surface d983f6c5/fc69c032):
    guards._print_receipts calls sys.stdout.flush() unconditionally (plan_merge/guards.py:315).
    A CLI started with fd 1 closed has sys.stdout None, so the flush raises AttributeError,
    which the (OSError, ValueError) catch does not cover. Measured: both files land
    once and no journal is left, but the exit code is 1. That falsifies T-02 amendment
    (7) and SC-01''s advisory-after-commit on a third stream state. At base, print
    to a None stdout is a no-op. Route to fable-advisor per the ruling. The fix should
    also cover _silence''s fd-confusion and missing-fileno cases.'
  - 'MF-12 (T-01, contested: security-reviewer high, QA med, lead med; substance,
    changed surface fc69c032/f4b1962e): check-domain denies only the two pair sidecar
    names, but harness_merge._journals_naming (:413-422) discovers every *.harness-merge.journal,
    and _journal_names (:402-410) makes an unreadable one name every file. QA measured
    that an orchestrator Write of evil.harness-merge.journal exits 0, after which
    locked_update of plan.yaml and feature.json refuses with exit 5. Forging stays
    closed; the wedge the ruling widened MF-10 for is still open. Remedy candidates:
    deny the whole suffix in check-domain (inside T-01''s amended files), or narrow
    discovery to JOURNAL_PAIR (C5 surface). Route to fable-advisor.'
  branch: none
  open_questions:
  - id: OQ-1
    question: 'Round 3, the last, closed MF-9 and MF-10 as ruled, but two gating findings
      remain in changed surfaces. MF-11 (T-02, high, measured): a CLI started with
      fd 1 closed exits 1 after its amendment lands. MF-12 (T-01, security high vs
      QA and lead med): other *.harness-merge.journal names wedge plan and feature
      writes at exit 5. Under the ruling, these return to fable-advisor. Options:
      grant a further round, ship with these recorded as accepted risk, or stop.'
    blocking: true
  - id: OQ-2
    question: 'MF-12 severity and remedy: is the two-name denial as ruled sufficient,
      given that the wedge route stays open under any other suffix name? If not, should
      the fix deny the whole *.harness-merge.journal suffix in check-domain (inside
      T-01''s amended files), or narrow harness_merge discovery to the JOURNAL_PAIR
      names (the C5 journal surface)?'
    blocking: true
  escalations:
  - id: E-1
    raised_by: harness-code-reviewer
    question: 'A new high in a changed T-02 surface: after a landed amendment, a CLI
      started with fd 1 closed exits 1'
    domain: FEAT-2488 rework budget / C5 ruling
    routed_to: harness-orchestrator -> fable-advisor
    resolution: pending
    decided_by: pending
    recorded_as: runs/r-20261124-5-validate-validator/digest.md MF-11
  - id: E-2
    raised_by: harness-security-reviewer
    question: The MF-10 remedy leaves the wedge open under non-pair *.harness-merge.journal
      names; severity is contested (high vs med)
    domain: harness enforcement (check-domain.py) / C5 journal surface
    routed_to: harness-orchestrator -> fable-advisor
    resolution: pending
    decided_by: pending
    recorded_as: runs/r-20261124-5-validate-validator/digest.md MF-12
  expertise_update: []
  adequacy_notes:
  - 'MF-9 is closed by measurement from three lenses: QA (aed85ace blob red, plus
    a _silence no-op mutant that turns 2488/l and m red), pm (two mutants, each discriminating),
    and code-reviewer re-running its own c3 probe (rc 0, including with both streams
    broken).'
  - 'MF-10 is closed for both literal names on the as-typed, case-folded, symlink
    and hardlink routes: T-09 13 shows 8 FAILs against aed85ace''s check-domain, and
    the drift-pin mutant goes red. Only Write is exercised; the Edit and NotebookEdit
    denials were checked by reading the code only.'
  - The DEC-255 receipts manifest-unit.json (68) and manifest-integration.json (95)
    were run under env -u PYTHONUNBUFFERED, which closes the c3 adequacy gap. Discovery
    counts are non-zero and unchanged.
  - 'For MF-11 and MF-12, the lead confirmed the cited sites in the worktree (guards.py:308-320;
    harness_merge.py:402-422). Execution is the readers'': code-reviewer for MF-11,
    QA for MF-12.'
  - 'Lead''s severity reconciliation for MF-12: med, because it is availability-only,
    recoverable by deleting one file, and the same wedge is reachable through the
    backlogged Bash route. It is still gated because it is the residue of a ruled
    remedy in a changed surface. Both ratings are carried (P-04).'
  - 'Non-gating: code med on _silence (it dup2s over a caller-owned fd, and a capture
    with no fileno raises; in-process callers only); security med on main-rooted hardlink
    detection that misses linked worktrees (static only, pre-existing anchoring);
    code low on RE_PAIR_JOURNAL''s $ matching a trailing newline (fails closed); pm''s
    2 form advisories.'
  - T-01's literal verify does not run test-check-domain-approval.py; only the integration
    kind exercises MF-10.
  - 'UI scoped out by a measured census: 156 paths base..pin and 36 in the delta,
    none of them UI.'
  sc_status:
  - id: SC-01
    verdict: met
    method: automated
    evidence: 2488/a, k, l and m, and T-09 13, are green in QA manifest-integration.json
      at 6528b4db with PYTHONUNBUFFERED stripped. MF-11 shows the clause still fails
      when fd 1 is closed, which no test exercises.
  - id: SC-02
    verdict: met
    method: inspection
    evidence: _silence and _note_on_stderr only dup2 devnull, with no mkstemp, os.replace
      or journal I/O (pm)
  - id: SC-03
    verdict: met
    method: inspection
    evidence: harness_merge.py is unchanged in the delta; carried from c3
  - id: SC-04
    verdict: met
    method: automated
    evidence: 2488/g green at the pin; regression-lock baseline in red-t02-plan-merge-base.txt:892-895
  - id: SC-05
    verdict: met
    method: inspection
    evidence: Successors untouched; the 6b22caef split keeps identical assertion multisets
  - id: SC-06
    verdict: met
    method: inspection
    evidence: feature_json_write.py, harness_merge.py, plan-merge.py and amend.py
      are unchanged in the delta
  - id: SC-07
    verdict: met
    method: automated
    evidence: git diff --quiet on the six suites returns rc 0, and all six are green
      at the pin, as are the 9 test-check-domain*.py files
  needs_approval: true
  severity_max: high
  matrix_ok: true
  coverage_gaps:
  - No test starts a CLI child with fd 1 closed (sys.stdout None) after commit (MF-11)
  - No test covers a governed Write of a non-pair *.harness-merge.journal name, or
    the wedge it causes (MF-12)
  - T-09 13 exercises Write only; the Edit and NotebookEdit sidecar denials are untested
  - No test covers the hardlink route with a main-rooted gate and a linked-worktree
    journal
  - T-01's literal verify does not run test-check-domain-approval.py
  - SC-07 preservation shows no discrimination
  findings:
  - kind: substance
    scope: none
    severity: high
    reader: harness-code-reviewer
    summary: 'MF-11 T-02: a CLI started with fd 1 closed exits 1 after its amendment
      lands (guards.py:315 flushes a None sys.stdout)'
    why: 'Measured: files land once, no journal is left, exit code 1. AttributeError
      falls outside the (OSError, ValueError) catch. The surface was introduced by
      this feature (d983f6c5, fc69c032).'
  - kind: substance
    scope: none
    severity: high
    reader: harness-security-reviewer
    summary: 'MF-12 T-01: journal discovery accepts a wider set of names than check-domain
      denies; a non-pair sidecar wedges locked writes at exit 5'
    why: 'check-domain.py:2610-2624 denies two names, while harness_merge.py:413-422
      discovers every *.harness-merge.journal. QA measured the wedge and rated it
      med (N-1). The lead reconciles to med: availability-only, recoverable, Bash
      parity. It is gated because it is ruled-remedy residue in a changed surface.'
  - kind: substance
    scope: none
    severity: med
    reader: harness-code-reviewer
    summary: 'T-02: _silence can dup2 devnull over a caller-owned fd, or raise AttributeError
      on a capture with no fileno'
    why: Measured at guards.py:271-281 (fc69c032). In-process callers only. Fold into
      the MF-11 fix.
  - kind: substance
    scope: none
    severity: med
    reader: harness-security-reviewer
    summary: 'T-01: main-rooted hardlink detection does not scan the assigned linked
      worktree'
    why: check-domain.py:129-155 and 2506-2536. Static only. Pre-existing anchoring,
      newly applied to the sidecar boundary. Not gating.
  - kind: substance
    scope: none
    severity: low
    reader: harness-code-reviewer
    summary: 'T-01: RE_PAIR_JOURNAL''s $ anchor matches a basename with a trailing
      newline'
    why: Over-denial, so it fails closed. Not gating.
  - kind: substance
    scope: none
    severity: med
    reader: harness-qa
    summary: 'QA N-1, the same defect as MF-12 (deduplicated): an evil.harness-merge.journal
      Write exits 0 and wedges plan.yaml and feature.json at exit 5'
    why: Measured by QA. Merged into MF-12, with both ratings carried.
  readers: []
  files_touched:
  - .harness/harness/features/FEAT-2488-plan-merge-atomicity/runs/r-20261124-5-validate-validator/qa/manifest-unit.json
  - .harness/harness/features/FEAT-2488-plan-merge-atomicity/runs/r-20261124-5-validate-validator/qa/manifest-integration.json
  - .harness/harness/features/FEAT-2488-plan-merge-atomicity/observations/harness-qa.md
  - .harness/harness/features/FEAT-2488-plan-merge-atomicity/runs/r-20261124-5-validate-validator/state.yaml
```
