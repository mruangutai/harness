# ALTITUDE read — BUG-1081 code-grade enforcement

**Verdict: nothing to fold in.** The `classify(grades, test_kinds)` seam sits at the right
depth, has exactly the two real consumers it claims, carries no hidden lifetime, and the
policy split between `code_grade.classify` and `validate-digest.py`'s
`_mechanical_code_grade`/`code_grade_enforcement_error` is clean. One low-severity residual
is recorded below and left, not applied.

## The four design tests, against `classify`

1. **Deletion test — PASS (real seam).** Delete `classify` (`code_grade.py:481-507`) and its
   two callers each have to reconstruct bar selection (`_is_test_path`, `code_grade.py:445`),
   block/severity computation (`_blocks`/`_severity`, `code_grade.py:460-467`) and the
   fail > grade_2 > pass precedence (`code_grade.py:501-506`) independently:
   `code-grade.py:56` (`_paths_report`) and `code-grade.py:103` (`_diff_report`) would each
   need their own copy, and so would `validate-digest.py:722`
   (`_classify_canonical_range`). Complexity reappears at all three call sites — it does not
   vanish. Not a pass-through.

2. **Interface is the test surface — PASS.** `test-code-grade.py:420-457`
   (`check_classify_bars`, `check_classify_grade_two_is_reasoned`, plus the malformed-policy
   case) calls `code_grade.classify(...)` and asserts on its returned `(records, result)`
   tuple only — no direct call to `_blocks`/`_severity`/`_is_test_path`.
   `test-validate-digest.py`'s BUG-1081 section (from `2215`) drives
   `validator.code_grade_enforcement_error` / `validator._mechanical_code_grade`, the public
   seam on that side, never `_classify_canonical_range`'s internals directly. The one place a
   test reaches into `code_grade.py`'s private names is
   `test-code-grade-cli.py:330-338`, and that is a *different* test — a self-grading quality
   check (every qualname in the module must grade ≥4 via `SELF_GRADING_ALLOWLIST`
   discipline), not a behavioral assertion about `classify`. It does not bypass the interface
   for behavior coverage.

3. **One adapter = hypothetical, two = real — CONFIRMED, two real consumers.**
   `code-grade.py:56` and `code-grade.py:103` (the CLI, both path-list and diff-range
   reporting) and `validate-digest.py:722` (the digest gate). Both need the same bars and the
   same precedence; that duplication is exactly what the seam earns its keep against, matching
   D-03's ruling that this lives in one importable place.

4. **Lifetime — pure, no state introduced.** `classify` is called fresh per invocation with a
   `test_kinds` mapping the caller already parsed; nothing is cached or held across calls, and
   the docstring says so explicitly ("this seam never reads configuration or ambient cwd
   itself", `code_grade.py:487`). No adapter, no pooled resource, nothing to state a lifetime
   for.

## The `classify` / `_mechanical_code_grade` split

Correct altitude, no policy leak. `classify` owns exactly the grading rule: bar selection,
per-record severity, and the fail/grade_2/pass precedence — pure data in, pure data out, and
explicitly never decides `n_a` (`code_grade.py:494`, "distinguishing 'nothing changed' from
'changed but nothing gated' is the caller's job, not this seam's"). `validate-digest.py` owns
everything about *reaching* that seam correctly for one review: deriving the canonical range
(`_canonical_review_range`, `validate-digest.py:648`), reading the checkout's own
`test_kinds` (`_load_test_kinds:686`), deciding `n_a` when no `.py` path changed
(`_mechanical_code_grade:734`, before `classify` is ever called), and turning `SyntaxError` /
any other exception crossing the seam into a named, repair-bearing refusal
(`_classify_canonical_range:711-731`) rather than a traceback. None of that restates a grading
rule — it is range derivation and presentation, which is the caller's job by design (D-05,
DEC-209). `resolve_reviewed_commit` (`validate-digest.py:555`) correctly reuses
`code_grade.commit_oid` rather than re-implementing commit resolution, and
`_git_line_or_none` (`validate-digest.py:619`) is the one shared basis for the
default-branch/merge-base lookups in that module — no duplicate git-shelling found.

## Finding — recorded and left

**File/line:** `.claude/skills/harness-code-review/SKILL.md:73-99` (new "The enum is an audit
claim" section) vs. `validate-digest.py:734-758` (`_mechanical_code_grade`'s docstring) vs.
`DECISIONS.md` DEC-209.

**Summary:** the same enumerated set of six refusal conditions (unresolvable `origin/HEAD`,
unresolvable `review_sha`, no merge base, degenerate range, missing/malformed `test_kinds`,
unparseable committed Python) is spelled out in prose in three places.

**Cost:** if a future change adds, removes, or renames one of these refusal branches in
`validate-digest.py`, the `SKILL.md` prose (which a `harness-code-reviewer` run actually reads
and acts on, since it cannot import the Python module) has no mechanical link back to the code
and can go stale silently — a reviewer would then act on an out-of-date enumeration.

**Alternative considered:** loosen the `SKILL.md` wording to something that doesn't name the
set (e.g. "each grading or derivation failure refuses by name, with its own repair") so it
can't drift item-by-item.

**Why left, not applied:** `SKILL.md` is instructing an agent persona that has no access to
`validate-digest.py`'s source — prose restatement for that audience is not an implementation
duplication, it's the only channel that reader has. `DECISIONS.md`'s DEC-209 is a frozen
historical record, not living documentation, and is exempt from "keep in sync" by convention.
And `test-validate-digest.py`'s `N_A_REFUSAL_SUBSTRINGS` table (`test-validate-digest.py:2159`)
already ties specific refusal wording to specific code paths under test, so a code-side change
to the refusal set fails a test before it can silently diverge from the doc unnoticed — a real,
if partial, compensating control already exists. Not worth an apply against a settled,
just-landed decision (DEC-209) for a residual this narrow.

**Nature:** chore. **Recommendation:** leave.

## No other findings

No special case bolted onto shared infrastructure, no check living at one call site where a
shared home already existed, no workaround patching a symptom the mechanism should refuse
outright. D-03/D-05/D-07 not re-litigated.
