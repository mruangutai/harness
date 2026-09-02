# Review — PR #1189 (BUG-981-fixture-secret-scrub)

Reviewed: `13701b20..bd9b317d` (branch tip, working tree clean, no `[harness:human]` commits
in range). Direct worktree/PR flow — no `feature.json` exists for this branch and none should;
per dispatch, delivering this review via hub message + this artifact rather than the validated
pipeline.

## Stage 1 — spec compliance (issue #981, proposed work items 1–4)

All four satisfied, no scope creep, no omission:

1. **Key pattern hyphenation** — `sk-ant-|sk-[A-Za-z0-9-]{16,}` added exactly as proposed
   (`check-fixture-secrets.sh:41`). Confirmed by test + RED-proof: reverting to the original
   `sk[-_][A-Za-z0-9]{8}` shape silently passes the exact key that escaped before (`sk-ant-red`
   test, both `test-check-fixture-secrets.py` and live run).
2. **Identity check rebound to the capture** — `$(whoami)` replaced with
   `/Users/[^/…]+/|/home/[^/…]+/` (`check-fixture-secrets.sh:47`), independent of invoker.
3. **Positive controls preserved** — run once before any file check, against synthetic values
   shaped like each pattern; extended with a RED-proof (`run_positive_control_red_proof`) that a
   broken pattern refuses to run at all (exit 2) rather than reporting false-clean.
4. **Reusable, checked-in helper** — standalone `check-fixture-secrets.sh` + dedicated
   15-case `test-check-fixture-secrets.py`, registered in `run-unit-tests.sh`'s `UNIT_SCRIPTS`
   (single-line diff, exact name, no typo) and consistent with `harness.json`'s
   `test_kinds.unit.detect` glob (not added to `integration.detect`, correctly — see
   classification check below).

Diff is exactly 3 files / 318 insertions, nothing outside these four items.

**Not in scope, noted only:** FEAT-44's `plan.yaml` still carries the original inline sweep with
both original blind spots. Issue #981 doesn't ask for that historical artifact to be migrated,
and it's not re-executed post-ship, so this is not an omission against the cited proposal —
flagging as `open_questions` in case there's an appetite to point future captured-artifact
verify blocks at the new helper explicitly.

## Stage 2 — code quality

**Verified, ran the actual script (not just the test suite):**
- `python3 test-check-fixture-secrets.py` → 15/15 pass, both RED-proof mutants correctly
  discriminate (confirmed by direct run, not just reading the assertions).
- Shell quoting on `HOME_PATH_PATTERN`'s character class is correct: resolves to
  `[^/[:space:]"']` (verified by echoing the live variable). Matches `/Users/alice/…` and
  `/home/bob/…` shapes; does not over- or under-match on the quote/space exclusion.
- Unit-vs-integration classification: `test-check-fixture-secrets.py` forks a real subprocess
  per case, same shape as `test-check-omp-port.py` (also `UNIT_SCRIPTS`, also
  `subprocess.run([checker, …])` per case) — consistent with existing precedent, not a
  misclassification.
- `code-grade.py --base 13701b20 --head bd9b317d`: 6 functions graded, `code_grade: grade_2`
  for one record (below, with the required reasoning) — **no `fail`-grade record**, exit 0.

### must_fix — SECRET_PATTERN's `sk-[A-Za-z0-9-]{16,}` branch is unanchored and false-positives on ordinary kebab-case prose

`check-fixture-secrets.sh:41`. The alternative is a bare substring match: any text containing
literal `sk-` followed by 16+ further `[A-Za-z0-9-]` characters trips `BLOCKED`, regardless of
what precedes the `sk-`. English/technical compound words ending `-sk` (`task-`, `risk-`,
`desk-`, `disk-`, `ask-`, `mask-`, `kiosk-`, `whisk-`, `brisk-`) followed by a longer hyphenated
tail are exactly this shape. Demonstrated live against the actual `SECRET_PATTERN` string from
the file:

```
$ printf 'the task-runner-for-this-project completed successfully\n' | grep -qE "$SECRET_PATTERN" && echo MATCH
MATCH
$ printf 'please ask-your-teammate-about-this-config-value before merging\n' | grep -qE "$SECRET_PATTERN" && echo MATCH
MATCH
```

The artifact class this script exists to scrub — a captured OMP session transcript — is
saturated with exactly this vocabulary: kebab-case file paths, script names, feature/branch IDs,
CLI flags, and this repository's own idiom of long hyphenated compound identifiers (e.g.
`risk-tolerance-check-guard`, `task-decompose-lead` shaped strings appear routinely in this
project's own transcripts and docs). A false BLOCKED on a benign line forces either editing the
authentic captured text to dodge the gate (degrading fixture fidelity — the opposite of what a
scrub gate should encourage) or bypassing the check outright, which reintroduces the exact
"false sense of coverage" problem #981 was raised to close, just from the other direction.
Concrete, low-risk fix: anchor the `sk-` alternatives so they can't start mid-word, e.g.
`(^|[^A-Za-z0-9])sk-(ant-)?[A-Za-z0-9-]{15,}` or equivalent `(^|[^A-Za-z0-9])sk-` prefix
requirement — real key material is never preceded by another alnum character. This was the
literal shape proposed in issue #981 ("`sk-[A-Za-z0-9-]{16,}` covers …"), so this is a Stage-2
quality gap in the implementation of an accepted proposal, not a Stage-1 spec deviation.

### should_fix (med) — positive controls only self-verify 2 of the pattern's 6 alternation branches

`check-fixture-secrets.sh:59-75`. Both `control_secret` and `control_home` are hardcoded to the
exact two shapes #981 fixed (`sk-ant-…`, `/Users/…`). `AKIA…`, `-----BEGIN`, `github_pat`/`ghp`/
`gho`/`xox[abp]`, and `credential_pin` have no runtime self-check at all — a future hand-edit
that broke, say, the `AKIA` branch (malformed escaping, a merge that shifts alternation grouping)
would still print "clean — … both positive controls fired," which reads as full validation but
isn't. Today those branches are covered by `test-check-fixture-secrets.py`'s regression cases
(now wired into CI via `UNIT_SCRIPTS`), so this isn't a live gap — but the runtime self-check
(the thing a human trusts when they see "both positive controls fired" on their own machine,
independent of whether CI ran) covers a third of the pattern's alternatives. Consider one
combined control string exercising all six branches, or softening the success message to name
what was actually verified.

### Verified non-issues (recorded per P-15, so they don't get re-raised)
- `HOME_PATH_PATTERN` excludes `'`/`"` from the username segment, so a username containing an
  apostrophe (`/Users/o'brien/…`) wouldn't match — not exploitable: POSIX usernames (and macOS
  short names, which is what home directories are keyed on) can't contain quotes or spaces, so
  this shape never occurs in a real path.
- `credential_pin` literal is a real JSON record-type field name from the OMP capture format
  (confirmed against `FEAT-44` provenance notes), correctly left untouched — not a stray token.
- `set -uo pipefail` (no `-e`) is deliberate and correct: the file loop must keep checking every
  path after one match, which the "multiple files" test pins.
- File permissions: both new files are `100755` in the tree — directly executable, no `chmod`
  step needed by a caller.

### code_grade — reasoned, grade_2, does not block
`run_cases` (`test-check-fixture-secrets.py:41`): CYCLOMATIC 10, ABC 42.2, GRADE 2 vs test bar 3.
**Reason:** the function is a flat sequence of ~12 independent scenario blocks (write fixture →
fire the real script → assert), not nested/branching logic; ABC is driven by breadth (many
sequential operations) rather than depth. Splitting each scenario into its own function would
multiply per-case boilerplate (tmp dir, imports) without reducing real complexity, and would
scatter the exhaustive-enumeration read that's the point of this suite (mirrors the file's own
per-branch regression loop). Test-tier function, one notch under bar, does not gate.

## VERDICT

```yaml
VERDICT: FAIL
DIGEST:
  headline: >-
    Both #981 blind spots are correctly fixed and RED-proofed, but the new SECRET_PATTERN's
    unanchored sk- branch false-positives on ordinary kebab-case prose common to this project's
    own captured transcripts — undermines the reusability the fix exists to deliver.
  severity_max: high
  findings: 3
  must_fix:
    - "check-fixture-secrets.sh:41 — SECRET_PATTERN's sk-[A-Za-z0-9-]{16,} branch is an
       unanchored substring match; false-positives on kebab-case words ending -sk (task-,
       risk-, desk-, ask-, disk-, mask-) followed by a long hyphenated tail, demonstrated live
       against the shipped pattern. Anchor with (^|[^A-Za-z0-9]) or equivalent."
  spec_violations: []
  reviewed: "13701b20..bd9b317d"
  human_commits_in_scope: []
  code_grade: grade_2
  open_questions:
    - id: Q1
      question: >-
        FEAT-44's plan.yaml still carries the original two-blind-spot inline sweep. Is there
        appetite for a follow-up pointing any future captured-artifact verify: block at the new
        check-fixture-secrets.sh explicitly, so the fix actually gets reused rather than
        re-copied?
      blocking: false
  files_touched: []
  expertise_update: []
artifact: .harness/harness/features/BUG-981-fixture-secret-scrub/notes/review-harness-code-reviewer-pr1189.md
```
