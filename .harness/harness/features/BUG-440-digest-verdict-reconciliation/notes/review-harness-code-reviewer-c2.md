## BLUF

**FAIL, unchanged from cycle 1's gating reason.** The remedy is genuinely test-only
(`.claude/skills/harness/bin/check-state.sh` is byte-identical between the two pins — `git diff
2964cddb..a1a6795 -- .claude/skills/harness/bin/check-state.sh` is empty) and it genuinely fixes
V-02 and V-03 (both mutants now discriminate). But V-01, the gating finding, is **STILL OPEN**:
`case_bug440_digest_verdict_reconciliation` still grades **1** (cyclomatic 22 / cognitive 12 / ABC
55.0) against test-code bar 3 — improved from cycle 1's 28/17/67.1 but not far enough. The
extraction did not move the defect into a helper (all three new helpers pass their bar); it left the
orchestration function itself — three `TemporaryDirectory` scenarios each closing over a large
boolean conjunction — still over budget.

## Pin discipline

- `git rev-parse HEAD` = `a1a67956a5844c67ce098e9580ee6692a92f9a30` (matches assignment).
- `git status --porcelain`: two tracked files modified (`feature.json`, `plan.yaml`) and four
  untracked sibling notes (`qa-bug440-c1.md`, `review-harness-code-reviewer-c1.md`,
  `review-harness-security-reviewer-c1.md`, `review-harness-ui-reviewer-c1.md`) — all from
  concurrent panel members writing to this worktree, not from any action of mine. I made zero edits
  to source, tests, or plan/feature files; only my own artifact and none of the disallowed paths
  were written.
- All source facts below are read via `git show <sha>:<path>` or `git diff <a>..<b>`, never the
  working tree.

## What moved

`git diff 2964cddb..a1a6795 --stat`: only `tests/integration/test-check-state.py` (65 insertions /
59 deletions). `check-state.sh` diff is empty. `notes/redproof-BUG-440.md` diff is empty. The remedy
is exactly what it claims to be: test-only. **Every cycle-1 spec-compliance clearance for
`check-state.sh` (REQ-01..04, REQ-03(a)-(e), D-07, PF-b884d6ee, SC-07) carries forward by name —
not re-derived, since the file that would falsify them is unchanged.**

## V-01 — code-grade.py, the gate

`python3 .claude/skills/harness/bin/code-grade.py --base 772790be52774eafe2971f9c44400e18b2d54275 --head a1a67956a5844c67ce098e9580ee6692a92f9a30`
(exit 1):

| function | line | cyclomatic | cognitive | abc | grade | driver | bar | result |
|---|---|---|---|---|---|---|---|---|
| `_bug440_digest` | 4618 | 2 | 0 | 2.4 | 5 | cyclomatic+cognitive+abc | 3 | PASS |
| `_bug440_build` | 4640 | 3 | 3 | 13.8 | 4 | abc | 3 | PASS |
| `_bug440_validate_fixture` | 4654 | 6 | 1 | 20.2 | 3 | abc | 3 | PASS |
| `case_bug440_digest_verdict_reconciliation` | 4666 | **22** | **12** | **55.0** | **1** | cyclomatic+abc | 3 | **FAIL** (SEVERITY: high) |

**V-01 is STILL OPEN — must_fix.** The extraction did NOT relocate the defect into an
under-bar helper (all three helpers pass cleanly); it reduced the case function's own numbers
(28→22 cyclomatic, 17→12 cognitive, 67.1→55.0 ABC) without crossing grade 3. The residual driver is
the same shape cycle 1 flagged: three sequential `with tempfile.TemporaryDirectory()` scenarios,
each closing a multi-clause `and`/generator-expression boolean (`mixed_ok`'s nine-way conjunction is
now the dominant cost). A further extraction — e.g. a helper that takes `(code, out, unchanged)` and
returns `mixed_ok` — is still owed.

## Test-code correctness re-review (item 4)

- `_bug440_digest`'s `assert validator.validate("lead", text) == [], text` (test-check-state.py:4625)
  is unchanged in effect from cycle 1 (relocated verbatim) — it is a loud self-check that the
  synthetic fixture stays valid against `validate-digest.py`'s live lead contract; it cannot mask
  drift because a contract change that invalidates the fixture text raises `AssertionError`
  immediately, failing the whole case rather than passing silently.
- `_bug440_build` (test-check-state.py:4640) guards `if text is not None:` before writing
  `digest.md` — run G (`text=None`) correctly leaves no `digest.md` on disk, which is what drives
  the `"digest.md is missing"` INV-15 assertion in `mixed_ok`. Correct.
- `_bug440_validate_fixture`'s `os.walk` (test-check-state.py:4654-4658) runs after `_bug440_build`
  has written every present `digest.md`, so the hash set covers exactly the files that exist at
  that point (M, E, N, I, O — not G, which was never written) — same coverage as cycle 1, only
  relocated.
- `digest = lambda verdict: _bug440_digest(validator, verdict)` (line 4673) re-validates on every
  call, but the validator is pure regex/text-shape checking over a ~10-line fixture, called 6 times
  total in this case — no material cost. Not a defect.

## V-02 (mutant m2, "warn not bad") — RESOLVED

New third fixture (test-check-state.py:4698-4700): `entries=("M",)`, single run M with a mismatched
digest, `blocking_ok = mismatch_code == 1 and "INV-37" in mismatch_out`. Verified against
`check-state.sh`'s actual control flow (`git show a1a6795:.claude/skills/harness/bin/check-state.sh`
line 1552 `bad.append(...)` for INV-37; line 2508 `sys.exit(1 if bad else 0)` — only `bad`, never
`warn`, drives the exit code). This fixture has exactly one run, so exit 1 has exactly one possible
cause; the old fixture's G and X runs (which forced exit 1 independently) are absent here. A mutant
demoting the INV-37 append from `bad` to `warn` now flips `mismatch_code` to 0, failing
`blocking_ok`. Genuinely bound.

## V-03 (mutant m3, reconciliation under the outer else) — RESOLVED

Fixture run X's digest text changed from `"# digest\n"` to `"VERDICT: FAIL\n"`. Verified: the
former has no `VERDICT:` line at all, so even under the m3 mutant, `_dm` (the regex match at
check-state.sh:1548) is `None` and the reconciliation code is unreachable either way — no
discrimination. The new text has a real `VERDICT:` line but is otherwise invalid — confirmed by
running `validate("lead", "VERDICT: FAIL\n")` directly: returns 8+ errors (no DIGEST: block, no
artifact:, missing headline/team/steps_run/...). Under correct code this routes to the `if _errs:`
branch (check-state.sh:1531, "does not satisfy the lead digest contract") and never reaches the
reconciliation `else:` at line 1541; under the m3 mutant (reconciliation hoisted to the outer else)
it would reach the `_dm` match, produce a spurious `runs/X` INV-37 entry, and fail
`mixed_ok`'s `not any(f"runs/{name}" ... for name in (..., "X", ...))` clause. Genuinely bound.

## V-04 — CONFIRMED, STILL OPEN (med, not promoted)

Six-token tuple at test-check-state.py:4691-4692 —
`("FEAT-TEST", "M", "FAIL", "PASS", "feature.json", "digest.md")` — is **byte-unchanged** from
cycle 1. Three of the six tokens still cannot fail (`"M"` is guaranteed by the `runs/M` pre-filter;
`"feature.json"`/`"digest.md"` are literal filenames baked into check-state.sh's f-string), and
`"FAIL"`/`"PASS"` remain order-blind: transposing the two `!r` interpolations in the INV-37 message
(check-state.sh:1554/1556) would still satisfy `all(token in mismatch[0] for token in ...)` and ship
green. Reporting at cycle-1's severity (med), not gating on my own authority.

## V-05 / V-06 / V-07 / V-08

- **V-05** (low) — unchanged by construction: anchors in `check-state.sh:1553`, which is
  byte-identical to the prior pin. Still open, same severity.
- **V-06** (info) — **RESOLVED.** `entries` is no longer a dict; the mixed-case call site
  (test-check-state.py:4684) now passes a plain tuple `("M", "E", "N", "I", "G", "X")`. Confirmed
  against `_bug1305_invariant_feature` (test-check-state.py:4532-4555): it only ever does
  `for name in names:` and hardcodes `verdict: PASS` in the written `feature.json` — the old dict's
  values were provably always discarded, and the new tuple makes that honest instead of implying
  per-entry configurability that never existed.
- **V-07** (info) — unchanged by construction: the new INV-37 region still sits outside the INV-36
  `try/except` one line above it in `check-state.sh`, which is byte-identical to the prior pin.
- **V-08** (info) — unchanged: no change owed, `check-state.sh` untouched.

## Gating wiring

Confirmed at the pin: `case_bug440_digest_verdict_reconciliation()` is still called at
test-check-state.py:4859 (`ok_bug440 = ...`) and still ANDed into the file's final gate at
test-check-state.py:4873 (`... and ok_bug1305 and ok_bug440 and ok_i33`). Not dropped from the
conjunction.

## Verdict rationale

`must_fix` is non-empty (V-01, code-grade FAIL, tool-assigned SEVERITY: high) → `FAIL`,
`severity_max: high`. V-02/V-03/V-06 resolved; V-04/V-05/V-07/V-08 open at cycle-1 severity,
none gating on their own.
