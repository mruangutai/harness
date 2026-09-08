# Scope review — BUG-124 plan-panel, cycle 0

**PASS, with notes.** Traceability is clean (every REQ-01..05 has a task, every SC-01..07 has
evidence-producing test cases, no orphans in either direction). Dependency order is a trivial,
correct linear chain (T-01 → T-02 → T-03). All measured file:line anchors in plan.yaml and BRIEF.md
check out exactly against the real files, with one exception (finding 3). Four advisory findings,
none blocking.

## Findings

1. **[med] T-01's live-manifest fixture contradicts REQ-04's own "no second edit" promise.**
   `plan.yaml` T-01 `verify:` asserts `len(g) == 3` against the LIVE `team-config.yaml`
   (`hb.run_dir_grant_globs(".")`), and T-01's intent requires the SAME assertion to be checked in
   permanently as a unit case ("the live manifest yields exactly the three run-dir globs",
   `tests/unit/test-harness-boundary.py`). REQ-04 explicitly invites a fourth squad's `/runs/` grant
   with "no second edit anywhere" — the day that happens, this checked-in test breaks and someone
   must edit it, which is exactly the maintenance burden the derived-vocabulary design exists to
   avoid. Consequence: a legitimate, REQ-04-sanctioned config change turns a permanent test red.

2. **[med] Fail-open surface: the vocabulary derivation itself is untested and undiagnosable.**
   D-03/T-02 route the whole vocabulary through a separate non-isolated `python3 -c` shell
   substitution whose stderr is sent to `/dev/null` and which is deliberately "incapable of failing
   the script." Every one of: `team-config.yaml` missing/unreadable/malformed, PyYAML not importable
   by whatever plain `python3` the hook's PATH resolves at actual Claude-Code-hook execution time
   (measured only from an interactive shell, `BRIEF.md`'s D-03 premise — not from inside a live
   hook invocation), or `resolve_root` returning falsy — all collapse into the identical generic
   "SKIPPED — vocabulary was empty" stderr line dispatch-guard.sh prints downstream. No test case
   exercises "the derivation subprocess itself is broken" (only case (e), a grant-less manifest,
   exercises the REQ-05 skip path) and nothing self-checks that the derivation can succeed in the
   deployed environment. If the hook's actual `python3` differs from the one measured interactively,
   the new guard becomes a permanent, silent no-op and issue #124 ships unfixed behind a green suite.

3. **[low] T-02 intent mis-cites its own "house idiom" precedent.** Intent says the new shell
   substitution should use "`sys.path.pop(0)` then `sys.path.insert(0, sys.argv[1])` — the same idiom
   check-domain.sh line 103 uses." Measured: `check-domain.sh:103` performs only `sys.path.pop(0)`
   (inside a `PYTHONPATH`-fed heredoc, not a `-c` string); the paired insert is at
   `check-domain.sh:125` — `sys.path.insert(0, _bin_dir)`, where `_bin_dir` is unpacked from
   `sys.argv[1:4]` at line 124 (i.e. `sys.argv[3]`, not `sys.argv[1]`). The two mechanisms also differ
   structurally (heredoc+env var vs. a `$(python3 -c '...')` substitution). Low consequence — the
   described idiom is sound standalone regardless of the mismatched citation — but an implementer
   checking the cited precedent will not find what is described there.

4. **[med] T-03's verify binds four words, not the sentence.** `grep -q "dispatch-guard.sh refuses"`
   passes on any edit that keeps that literal phrase while getting the described mechanism wrong —
   wrong exit code, wrong condition (e.g. "ownership" instead of "shape"), or dropping the
   "naming the slug and a compliant form" clause that REQ-02 needs for actionability. This is the
   assertion-subject gap DEC-169/issue #979 name: the grep's subject is a substring, not the claim.
   T-03 is `main-session-direct` with no other reviewer on this docs task, so a transcription slip in
   the added sentence ships uncaught. (Distinct from GOALCHECK-F1, which is about a *different*
   verify's self-refusing path, not phrase-matching.)

## On the two already-ruled items

- **GOALCHECK-F1** (high, self-refusing `verify:`): agreed, correctly rated high — a bootstrap
  bug that would refuse the very re-run/QA dispatches that quote it.
- **GOALCHECK-Q1** (D-01 does not catch a well-formed wrong-squad slug): no dispute with the
  disposition (operator decision at signature, non-vacuity and false-positive reasoning both hold).

## Verified anchors (no drift found unless noted above)

`dispatch-guard.sh:25` (`GUARD_BIN_DIR`), `:105-112` (import try/except, confirmed exact),
`check-domain.sh:103` (confirmed, but see finding 3 for the paired-line drift),
`team-config.yaml:45,306,315,324` (confirmed exact), `SKILL.md:272-274` (confirmed exact),
`harness_boundary.matches`/`resolve_root(bin_dir, strict=...)` (both exist, signatures as claimed),
`_checkout`/`_read_registry`/`_claims_for`/`case_17_*` in `test-dispatch-guard.py` (all exist;
`_checkout` writes `agents: {}` — confirmed literally an empty mapping, so the "empty vocabulary"
claim holds), `check`/`run_case`/`main` in `test-harness-boundary.py` (all exist). Ran
`python3 tests/integration/test-dispatch-guard.py` at the current (pre-T-02) worktree state: **48 of
48 cases passed**, matching the plan's cited count exactly.

## Proportionality

Not over-scoped for a BUG: T-01/T-02 are the one guard check plus its helpers and tests; T-03 is a
single sentence in an already-existing paragraph. Not under-scoped either — every REQ has a task,
every SC has a producing test case (including SC-06's red-proof-in-receipt and SC-07's
no-stranded-claim, both explicitly required in T-02's intent).

```yaml
VERDICT: PASS
DIGEST:
  headline: Plan traces cleanly REQ-to-task and SC-to-evidence; four advisory findings (test fragility, an unverified fail-open assumption, a citation drift, and a phrase-only doc gate), none blocking.
  severity_max: med
  findings: 4
  must_fix: []
  spec_violations: []
  code_grade: n_a
  reviewed: "plan:/Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-124-run-dir-squad-suffix/.harness/harness/features/BUG-124-run-dir-squad-suffix/plan.yaml"
  human_commits_in_scope: []
  findings_detail:
    - { severity: med, summary: "T-01 verify + permanent unit test hardcode len(g)==3 against the live, mutable team-config.yaml", consequence: "A REQ-04-sanctioned fourth-squad grant addition turns a checked-in unit test red, forcing exactly the second edit REQ-04 says should never be needed." }
    - { severity: med, summary: "Vocabulary-derivation subprocess (D-03) is stderr-silenced, incapable-of-failing by design, and untested for its own breakage", consequence: "If the hook's actual runtime python3 lacks PyYAML (unlike the interactively-measured shell), the new guard becomes a permanent silent no-op indistinguishable from the benign REQ-05 skip, and issue #124 ships unfixed behind a green suite." }
    - { severity: low, summary: "T-02 intent mis-cites check-domain.sh:103 as the source of sys.path.insert(0, sys.argv[1])", consequence: "The real insert is at check-domain.sh:125 using sys.argv[3] in a structurally different heredoc+PYTHONPATH pattern; an implementer checking the citation finds a mismatch and may copy the wrong wiring or lose time reconciling it." }
    - { severity: med, summary: "T-03 verify (grep -q \"dispatch-guard.sh refuses\") binds a 4-word phrase, not the sentence's content", consequence: "An edit that keeps the phrase but states the wrong exit code, wrong condition, or drops the compliant-form clause still passes, and no other reviewer covers this main-session-direct docs task." }
  open_questions: []
  files_touched: []
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-124-run-dir-squad-suffix/.harness/harness/features/BUG-124-run-dir-squad-suffix/notes/review-harness-code-reviewer-planpanel-c0.md
```
