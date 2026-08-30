# SIMPLIFICATION angle — R-01 validate-final c13

BLUF: two minor findings (both `chore`, neither blocking). The central question —
`bytes` in `resolve_reviewed_commit` — is **not load-bearing**: it's an inherited-shape
accident, cheap to drop, not applied here. R-01 genuinely **reduced** duplication
(three commit-resolvers → one seam); it did not merely relocate it. Suites: 3/3 pass.
must_fix: [].

## Central question: is the `bytes` return load-bearing?

**No — verified by reading both use sites, not inferred.**

`resolve_reviewed_commit` (`validate-digest.py:540-545`) does `commit_oid(".", revision).encode()`,
turning `commit_oid`'s `str` into `bytes`. Its only consumer, `reviewed_python_change`
(`:548` on), uses the two oids in exactly two places:

1. `subprocess.run(["git","diff","--name-only","-z",base_oid,head_oid,"--"], capture_output=True)`
   (`:552-555`) — argv. Confirmed by direct test
   (`python3 -c "subprocess.run(['echo', b'hello', 'world'], capture_output=True)"` →
   `b'hello world\n'`): subprocess accepts mixed `str`/`bytes` argv identically on POSIX: each
   element is independently `os.fsencode`d. A `str` oid works exactly as well as a `bytes` one.
2. `result.stdout.split(b"\0")` / `path.endswith(b".py")` (`:558`) — `result.stdout` is `bytes`
   **regardless of argv type**, because `capture_output=True` with no `text=True` always yields
   raw bytes (confirmed by the same probe: `git --version` with all-`str` argv still returns
   `bytes` stdout). So the byte-split downstream needs nothing from the argv's type either.

Neither site needs `base_oid`/`head_oid` to be `bytes`. The `.encode()` buys nothing; it exists
only to match the pre-R-01 function's historical return shape.

**Cost of switching to `str`:** one line — drop `.encode()` at `validate-digest.py:543`
(`return commit_oid(".", revision)`). No caller change: line 552's argv list already accepts
`str` fine, and the split at `:558` is unaffected since it operates on `result.stdout`, not on
the oid values. **Test cost: zero.** Grepped `test-validate-digest.py` for every
`resolve_reviewed_commit`/`reviewed_python_change` assertion:
`check_resolve_reviewed_commit_guard` (`:1798-1820`) asserts only `result is not None` /
`is None` and that Git was not invoked — no `isinstance(result, bytes)` anywhere;
`check_reviewed_range` (`:1780-1821`) asserts only error-string content and the boolean
Python-changed verdict. No test pins the `bytes` shape.

**Verdict — reduce vs. relocate:** R-01 **reduced** duplication. Before, three separate
call sites independently ran `git rev-parse --verify … ^{commit}` with their own
argv-injection guards; now there is one seam (`code_grade.py:281-292`, `commit_oid`) and two
thin adapters (`code-grade.py:162-163`, four-line `try/except` in `validate-digest.py:540-545`).
The `.encode()` wrapper is not a second implementation of the resolver — it's an accidental
carry-over of a return-type contract nobody downstream needs. That's not "relocated
duplication", it's a small residual of inherited surface area on an otherwise real
consolidation.

## Findings

1. **file:line** `validate-digest.py:543` (also see analysis above)
   **summary** `.encode()` preserves a `bytes` return that neither consumer requires.
   **cost** Zero functional cost today — it's dead weight, not a bug. Cost of carrying it
   forward: the next reader has to redo this same argv/stdout trace to convince themselves it's
   safe to touch, same as this receipt just did.
   **alternative** `return commit_oid(".", revision)` (drop `.encode()`); no other line changes.
   **label** `chore`

2. **file:line** `code_grade.py:277-280` and `code-grade.py:115-118`
   **summary** Three blank lines precede `commit_oid` and `_result` respectively; every other
   top-level def in both files (e.g. `code_grade.py:34-36`, `:44-46`) uses the PEP8-standard two.
   **cost** Cosmetic only — no functional effect, but it's an inconsistency a formatter/linter
   would flag, and it's new in this diff (confirmed via `git diff HEAD`), not inherited.
   **alternative** Drop one blank line at each site to match the file's existing two-blank-line
   convention.
   **label** `chore`

No redundant conjuncts found: the `not isinstance(reasons, list) or not reasons or not all(...)`
guard at `validate-digest.py:772-776` looks doubled but isn't — `all([])` is `True`, so
`not reasons` is the only thing that catches an empty list; removing it would silently accept
`grade_2_reasons: []`. Left alone.

No change-narrating comments found in this diff's added lines. The narrating-style comments
`grep` surfaces in `validate-digest.py` (lines 197-224, 300-304, 439-442, 581-585, 609-611,
724-725, 802-806, 965-969, 1001-1005) predate this diff (absent from `git diff HEAD` for this
file) and are out of scope per the dispatch's non-goal — not re-litigated here.

`commit_oid`'s `--verify --end-of-options` / `^{commit}` anchors and the `revision.startswith("-")`
guard: confirmed load-bearing (argv-injection anchors), not flagged, per dispatch instruction.

## Suites (real values, not `n/a`)

```
test-code-grade.py       → PASS test-code-grade            exit=0
test-code-grade-cli.py   → PASS test-code-grade-cli         exit=0
test-validate-digest.py  → ALL PASSED (65/65 CLI, 14/14 hook, 24/24 T-09, 2/2 template) exit=0
```
`suite: pass` (real, observed — not the `n/a` legal for this persona under other contracts).

## git status --short (final action)

```
 M .claude/skills/harness/bin/code-grade.py
 M .claude/skills/harness/bin/code_grade.py
 M .claude/skills/harness/bin/test-check-plan-routes.py
 M .claude/skills/harness/bin/test-code-grade-cli.py
 M .claude/skills/harness/bin/test-code-grade.py
 M .claude/skills/harness/bin/test-validate-digest.py
 M .claude/skills/harness/bin/validate-digest.py
 M .harness/harness/features/FEAT-43-code-risk-grading/STATE.md
 M .harness/harness/features/FEAT-43-code-risk-grading/feature.json
 M .harness/harness/features/FEAT-43-code-risk-grading/notes/handoff-validate.md
?? .harness/harness/features/FEAT-43-code-risk-grading/answers/Q2-cycle-11-authorization.md
?? .harness/harness/features/FEAT-43-code-risk-grading/answers/Q3-cycle-13-overrun.md
?? .harness/harness/features/FEAT-43-code-risk-grading/answers/Q4-simplify-routing.md
?? .harness/harness/features/FEAT-43-code-risk-grading/answers/Q5-simplify-apply-authorization.md
?? .harness/harness/features/FEAT-43-code-risk-grading/notes/qa-regate-c13-r01.md
?? .harness/harness/features/FEAT-43-code-risk-grading/notes/qa-validate-fix-c13-qa-validator.md
?? .harness/harness/features/FEAT-43-code-risk-grading/notes/receipt-harness-backend-dev-efficiency-validate-fix-c13.md
?? .harness/harness/features/FEAT-43-code-risk-grading/notes/receipt-harness-backend-dev-reuse-validate-final-c13.md
?? .harness/harness/features/FEAT-43-code-risk-grading/notes/receipt-harness-backend-dev-reuse-validate-fix-c13.md
?? .harness/harness/features/FEAT-43-code-risk-grading/notes/receipt-harness-backend-dev-validate-fix-c11.md
?? .harness/harness/features/FEAT-43-code-risk-grading/notes/receipt-harness-backend-dev-validate-fix-c13-r01.md
?? .harness/harness/features/FEAT-43-code-risk-grading/notes/receipt-harness-dev-ops-altitude-validate-fix-c13.md
?? .harness/harness/features/FEAT-43-code-risk-grading/notes/receipt-harness-dev-ops-simplification-validate-fix-c13.md
?? .harness/harness/features/FEAT-43-code-risk-grading/notes/ship-review-validate-fix-c13-simplify-eng.html
?? .harness/harness/features/FEAT-43-code-risk-grading/notes/ship-review-validate-fix-c13-simplify-eng.md
```
No source or test file changed by this run — only this receipt was added, under my own
`notes/` path.
