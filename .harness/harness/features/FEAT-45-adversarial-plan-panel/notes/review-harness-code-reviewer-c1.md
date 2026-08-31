# Code review — FEAT-45-adversarial-plan-panel — c1 (re-review at re-pinned SHA)

**Housekeeping note.** My first write of this note landed in the MAIN checkout
(`/Users/molchairuangutai/GitHub/harness/.harness/harness/features/FEAT-45-adversarial-plan-panel/notes/review-harness-code-reviewer-c1.md`)
because a relative path resolved against the session default cwd rather than the worktree — exactly
the stray-copy failure mode this dispatch warned cycle 0 left behind. Caught it immediately, wrote
the correct copy here (in the worktree) with an absolute path, and confirmed it landed correctly. I
am read-only and `rm` is blocked by the domain guard (`bash-write-guard`), so the stray main-checkout
copy is still there and needs removal by a session with write rights outside this domain — see `Q2`
below. **This note, in the worktree, is the authoritative one; the main-checkout copy is a duplicate
byte-for-byte at the time of writing and should be deleted, not merged.**

Reviewed the delta `d0ebbe6..c745d3a07c2accd8395c9df7a25d911d40dc2c09` (`git log --oneline` short
form `c745d3a`; confirmed unique via `git rev-parse c745d3a`). `git merge-base origin/main c745d3a`
= `7ebfc9e`; the feature's full base is `1d3e5db` (confirmed unchanged). Worktree HEAD is `401089a`,
one commit ahead of the pin touching only `feature.json`'s `review_sha` field — confirmed via
`git diff --stat c745d3a HEAD` (1 file, 1 line). No `[harness:human]` commits in `d0ebbe6..c745d3a`
(`git log --grep="harness:human"` empty). This is a re-review: cycle 0's clean areas (REQ-02/05,
REQ-14, SC-01, SC-06, SC-08, SC-09/10, SC-15) are not re-derived here.

**Correction on the pin string itself.** `feature.json` at HEAD (`401089a`) sets `review_sha` to
`c745d3a61f1049e5325854618511544b10f68753` — the exact string this dispatch names as "Pinned SHA."
That string does **not** resolve: `git rev-parse c745d3a61f1049e5325854618511544b10f68753` →
`fatal: Not a valid commit name`. The real fix commit is `c745d3a07c2accd8395c9df7a25d911d40dc2c09`
(same 7-char short prefix, different tail). I reviewed the real commit. Flagged as `open_questions`,
non-blocking to this review, but a future automated re-pin or `git show <review_sha>` against the
recorded string will fail. Not `reviewed content` in the sense this dispatch scoped me to (the diff
`d0ebbe6..c745d3a` is unaffected either way), but it is a defect in this same repin commit.

## Cycle-0 must_fix corroboration — all three CLOSED

**M1 (high, fail-open) — CLOSED.** `git show c745d3a:.claude/skills/harness/bin/check-state.sh`
lines 211-214:
```
severity = str(item.get("severity", "")).strip().lower()
disposition = str(item.get("disposition", "")).strip().lower()
if severity not in {"info", "low", "med"} and disposition != "resolved" and fid not in overruled:
    bad.append(f"INV-32: {feat} finding {fid} is {severity or 'unrated'} and remains open without an operator overrule.")
```
Deny-list inverted to allow-list. Traced both prior fail-open directions: absent key →
`item.get("severity", "")` → `""` → not in allow-list → gates. YAML `null` (`severity:` with no
value, or `severity: None` fixture) → `item.get` returns `None` → `str(None).strip().lower()` →
`"none"` → not in allow-list → gates. Both now closed. `disposition`'s sibling default is unchanged
by this diff and was already fail-closed (`"" != "resolved"`); not disturbed.

**M3 (med, missing regression) — CLOSED.** `case_inv32_unrated_severity_fails_closed`
(`test-check-state.py:2982`) exists, is not merely mentioned:
```python
findings = [
    {"id": "PF-unrated", "severity": "unrated", "disposition": "open"},
    {"id": "PF-absent", "disposition": "open"},
    {"id": "PF-null", "severity": None, "disposition": "open"},
]
code, out, _ = _inv32_run(_inv32_plan(finding=findings))
ok = code == 1 and all(finding["id"] in out for finding in findings)
```
All three directions in one fixture, each asserted by requiring its own id to appear in the gate's
output (the loop in check-state.sh processes every finding, so a fix that only fixed one direction
would still be caught since all three ids must appear). Wired into `main()`'s overall gate
(`ok_i32_severity = case_inv32_unrated_severity_fails_closed()`, added to the big `and` chain).
Ran live at the pin: `python3 .claude/skills/harness/bin/test-check-state.py` → exit 0, output lines
`ok - INV-32 plan panel fixtures, including inv32-red` and
`ok - INV-32 unrated severities fail closed`, no `FAIL` anywhere in the run.

**M2 (high, code-grade) — CLOSED.** Per this dispatch's correction, graded the file directly
(`code-grade.py .claude/skills/harness/bin/test-check-state.py`, no `--base/--head`) rather than
trust the crashing base/head invocation. All eleven touched functions:

| Function | Cyclomatic | Cognitive | ABC | Grade |
|---|---|---|---|---|
| `_inv32_plan` | 4 | 6 | 6.1 | 4 |
| `_inv32_run` | 1 | 0 | 9.4 | 4 |
| `case_inv32_unrated_severity_fails_closed` | 3 | 3 | 8.8 | 4 |
| `_inv32_basic_checks` | 6 | 2 | 17.5 | 4 |
| `_inv32_ruling_checks` | 5 | 1 | 18.8 | 4 |
| `_inv32_missing_reader_check` | 3 | 1 | 6.2 | 5 |
| `_inv32_skipped_reader_check` | 7 | 2 | 12.1 | 4 |
| `_inv32_reader_checks` | 3 | 0 | 3.5 | 5 |
| `_inv32_mutant_fixture_passes` | 5 | 1 | 11.0 | 4 |
| `_inv32_mutant_is_discriminating` | 6 | 3 | 20.4 | 3 |
| `case_inv32` | 2 | 2 | 11.0 | 4 |

Bar for test code is grade 3; all eleven clear it, zero `RESULT: FAIL` among them. `case_inv32`
dropped from cyclomatic 28/ABC 95.1 (grade 1) to cyclomatic 2/ABC 11.0 (grade 4). Line-by-line diff
of the refactor confirms every one of the original nine assertion directions (no-panel, high-open,
high-overruled, high-resolved, ruling-unattributed, stale-ruling, reader-missing, reader-skipped,
mutant-discriminating) survives, unweakened, redistributed into the named helpers — verified by
mapping each original `checks.append(...)` line to its new home. D-13's mutant fixture-reuse
requirement (same marker-anchored mutant, run over the no-panel and reader-missing fixtures, written
beside the original script never in the tmpdir) is intact verbatim in `_inv32_mutant_is_discriminating`
(`docs = (_inv32_plan(panel_marker=False), _inv32_plan(readers=missing))`, same
`os.path.join(os.path.dirname(SCRIPT), ...)` placement, same `finally: os.unlink`).

## Primary hunt: does the allow-list inversion gate anything spuriously?

Traced every source that can populate a finding's `severity` at runtime:
- `plan-panel.yaml` (both reader prompts) and `templates/plan.yaml:57` state the vocabulary
  identically: **`info | low | med | high | critical | unrated`** — six tokens, exactly.
- `harness-spec-driven/SKILL.md`'s "panel result" section: pm "never edits a finding's severity" —
  transcribed verbatim from the lead's digest.
- `.omp/` and `.claude/` `harness-validator-lead.md`: the lead "never assigns severity" either.
- `panel_findings.py` (full read): computes only `id` from `reader`+`summary`; touches no severity
  field at all.
- Grepped for a spelled-out `"medium"` anywhere a panel finding's severity could originate
  (doctrine, templates, fixtures) — zero hits; every `medium` hit in the tree is either
  `effort:`/`thinking-level:` agent frontmatter or `severity_max` (a different, digest-level field
  with its own validator) — unrelated field, confirmed by file and line.

Allow-list `{"info", "low", "med"}` covers exactly half the six-token vocabulary; the other three
(`high`, `critical`, `unrated`) are the three the design requires to gate, and all three do. No
legitimate value is excluded from the allow-list, so no spurious gate. `.strip().lower()` neutralizes
case/whitespace variance for both the allow-list and the (unchanged) disposition check.

**Sibling condition check.** `disposition != "resolved"` short-circuits identically before and after
this diff. Verified the specific concern: a `resolved` finding with `severity: null` — `disposition
!= "resolved"` is `False` regardless of severity, so the whole `and` chain is `False` and the finding
does **not** gate. This is intended (matches the pre-existing `high-resolved` fixture's own contract:
disposition clears the gate independent of severity) — not a new escape, not touched by this diff.

## New findings — none reach `high`

1. **`low`, spec detail-mismatch, not gating.** T-08's own intent text (`plan.yaml:991-993`,
   unchanged by this fix, still says): *"Add ONE more assertion inside the high-open case... Do not
   add a separate case for it; it is the same branch."* The shipped fix instead extracted a
   standalone `case_inv32_unrated_severity_fails_closed` function with its own `main()` entry. This
   is the better shape post-M2 split (the "high-open" fixture now lives inside `_inv32_basic_checks`,
   not a single case function to extend), and it does not weaken coverage — but it is a literal
   deviation from the plan's explicit "same branch" instruction, and it is also the mechanism by
   which `main()`'s already-oversized boolean chain grew by one more `and` clause (see #3). Not
   `must_fix`: the deviation improves testability and the coverage gap it fills is real.
2. **`low`, residual self-check gap, not gating.** T-08's own `verify:` block
   (`plan.yaml:907-916`) still does not grep for the literal token `unrated` — the same gap cycle 0's
   Finding S1 named. Functionally covered anyway: `case_inv32_unrated_severity_fails_closed`'s
   boolean now participates in `main()`'s overall exit code, which the `verify:` block's
   `python3 .../test-check-state.py` invocation does check — so a future regression here still fails
   the gate, just not via the named-token half of the verify block.
3. **Informational, not a new finding.** `main()` (`test-check-state.py:3106`) is `GRADE: 1`
   (cyclomatic 41, ABC 88.5) when graded standalone. This is pre-existing debt: the function is an
   `ok_a … and ok_exit_unchanged` accumulator spanning every INV case in the file (INV-17 through
   INV-32, per its own comments), and this fix's diff added exactly one variable and one `and`
   clause to an already ~39-clause chain. Not raising as `must_fix` per the grading skill's explicit
   "not a touch-it-fix-it ratchet" — this file's other pre-existing gated functions (`case_g`,
   `case_k`, `case_n`, `case_o`, `case_u`, `case_v`, `case_x`, `case_inv29`, etc.) are the same kind
   of legacy debt, untouched by `d0ebbe6..c745d3a`, and out of this review's scope.

## Carried forward from cycle 0 — re-confirmed at the new pin, none re-derived

- **M4** (med) — `panel_findings.py:31-33`'s `digest[:8]` truncation: file absent from `c745d3a`'s
  diff (`git show c745d3a --stat` touches only `check-state.sh` and `test-check-state.py`); read the
  file in full at the pin, byte-unchanged. Still open.
- **M5** (med) — `test-plan-panel.py:161-181`'s unbound SC-03 direction: file absent from `c745d3a`'s
  diff. Still open, unchanged.
- **M6** (low) — `check-state.sh:216-228`'s `expected_readers = {"should-not-exist", "scope",
  "goalcheck"}` block: read it at the pin, identical to cycle 0's citation, sits immediately after
  the fixed severity block but outside the two changed lines. Unchanged.
- **M7** (low, UI domain) — the withhold message's text did shift incidentally:
  `f"...is {severity}..."` became `f"...is {severity or 'unrated'}..."`, so an absent/null severity
  now prints the word `unrated` instead of a blank. The remedy-omission critique M7 raised is
  unaffected — the message still states the fact, not the fix. Deferring the UI judgment call to
  `harness-ui-reviewer`.

```yaml
VERDICT: PASS
DIGEST:
  headline: "M1/M2/M3 all independently corroborated CLOSED at c745d3a — the deny-to-allow-list inversion closes both the absent- and null-severity fail-open, the regression test asserts all three directions and is wired into the suite's exit code, and all eleven refactored inv32 helpers grade 3+. Hunted the allow-list widening for spurious gating against the doctrine's full six-token severity vocabulary and found none; two low advisory notes on plan/verify-text drift, nothing reaching high."
  severity_max: med
  findings: 6
  must_fix: []
  code_grade: pass
  spec_violations:
    - { kind: mismatch, path: ".claude/skills/harness/bin/test-check-state.py", ref: "T-08" }
  reviewed: "d0ebbe6..c745d3a07c2accd8395c9df7a25d911d40dc2c09"
  human_commits_in_scope: []
  open_questions:
    - { id: Q1, question: "feature.json at HEAD (401089a) records review_sha as c745d3a61f1049e5325854618511544b10f68753, which does not resolve via git rev-parse to any commit — the real fix commit is c745d3a07c2accd8395c9df7a25d911d40dc2c09. Same short prefix, fabricated tail. Worth correcting before the next repin or any tooling that resolves review_sha directly.", blocking: false }
    - { id: Q2, question: "My first write of this cycle's note landed in the MAIN checkout (.harness/harness/features/FEAT-45-adversarial-plan-panel/notes/review-harness-code-reviewer-c1.md, outside the worktree) before I caught it and wrote the correct copy in the worktree. I am read-only and rm is blocked by the domain guard, so the stray main-checkout copy is still on disk and needs deleting by a session with write rights outside this domain — do not treat it as a second reviewed artifact, it is a byte-identical duplicate of this one.", blocking: true }
  files_touched: []
  expertise_update: []
artifact: .harness/harness/features/FEAT-45-adversarial-plan-panel/notes/review-harness-code-reviewer-c1.md
```
