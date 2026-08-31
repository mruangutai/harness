# Delta code review — cycle 29 — count-predicate repair

**Reviewed**: `1d292c2..73c636d`, one code file: `.claude/skills/harness/bin/test-validate-feature-json.py`
(+89/-3). Authorization: `answers/Q13-cycle-29-substring-gate.md`.

**VERDICT: PASS.** No must_fix. Two `should_fix` advisories, both zero-cost improvements to
regression guards that are currently correct, not currently-broken behavior.

## 1 — All three callsites, and no fourth

`git grep`-equivalent scan of every `file(s)` occurrence in the file (full-file grep, all hits
enumerated) confirms exactly three call sites route through `reports_exactly_one_file` (post-fix
lines 335, 360, 371), the helper's own docstring/regex (line 42-46), and two control functions
that call the helper with synthetic literals as **arguments**, not as `in`/`not in` comparisons
(lines 374-410). No fourth rendered-count predicate exists anywhere in the file.

**Bounded statement of the AST guard's reach** (`_rendered_count_substring_compares`, confirmed by
reading its body): it flags only an `ast.Compare` node whose operator is `In`/`NotIn` **and** whose
**left** operand is an `ast.Constant` string that **fullmatches** `\d+ file\(s\)`. It does NOT, and
structurally cannot, catch:
- the literal on the **right** operand (`r.stderr in "1 file(s)"`, reversed);
- an `Eq`/`NotEq` comparison (`"1 file(s)" == some_str`);
- a `.count()` / `.find()` call (not a `Compare` node with `In`/`NotIn` at all);
- an f-string/`JoinedStr` left operand (`f"{n} file(s)" in stderr`);
- the literal held in a variable first (`needle = "1 file(s)"; needle in stderr` — left operand
  becomes `ast.Name`, not `ast.Constant`);
- any count phrasing other than the exact `N file(s)` shape (verified against
  `validate-feature-json.py:52-53`, which is what the CLI actually emits — the shape matches).

None of these forms exist anywhere in the current file (grepped for `.count(`, `.find(`, and every
f-string; none combine with a rendered-count literal). The guard is narrowly scoped to exactly the
one syntactic shape that caused this defect, not a general "no substring test on a count" linter.
That narrowness is appropriate to the guard's stated purpose (its docstring says as much) and is
not itself a finding — see Advisory (a) below for the one place narrowness does carry cost.

## 2 — Spec compliance against Q13

- **Item 1** (replace the false assertion): satisfied. All three callsites now call
  `reports_exactly_one_file`, a `re.search(r"\b1 file\(s\)", ...)` word-boundary match — `"41
  file(s)"` no longer trips it. Confirmed by running the file directly against the live 41+
  -directory tree (see Verification below): all three original cases still pass, live.
- **Item 2** (permanent, mutation-sensitive control, independent of the live tree): satisfied, but
  in two layers with different scope:
  - **Helper level** — `case_reports_exactly_one_file_rejects_substring_match` and
    `case_reports_exactly_one_file_models_the_real_cli_line` call the helper directly with
    synthetic strings (`"41 file(s) swept"`, a reconstructed real scanning line, a multiline
    blob). Fully independent of the live tree's feature count. This alone is NOT
    callsite-mutation-sensitive — the guard functions' own docstring admits it: reverting any of
    the three callsites back to the bare `"1 file(s)" in r.stderr` literal leaves the helper
    correct and both these controls green, "the regression is invisible."
  - **Callsite level** — closed by the THIRD control,
    `case_no_bare_rendered_count_substring_outside_the_helper`, a static AST walk over the file's
    own source that would catch a callsite reverted back to the literal bare-substring shape.
    I verified this composition empirically rather than trusting the docstring: constructed an
    in-memory mutated copy of the real file with one callsite reverted to
    `"1 file(s) swept" in r.stderr` (a superset of the original bug, closer to a real revert) and
    re-ran the walker over it — see Advisory (a) for the exact commands and result. The static
    guard **catches** exact literal reverts to the callsites.
  - **Residual gap, stated rather than hidden**: the static guard only detects reintroduction of
    the *exact prior syntactic shape* (a bare `Compare`/`In`/`NotIn` against a rendered-count
    string literal). It would NOT catch a callsite that stopped calling the helper via some
    *other* wrong construct — e.g. an unconditional `True`, or a differently-broken predicate that
    isn't an `in`/`not in` literal compare. This is a legitimate, acceptable scope boundary for a
    guard whose stated job is "reverting to the exact prior defect," not general callsite
    correctness — I do not treat it as a finding.
- **Both of Q13's stated constraints held**: the fix is in the predicate (word-boundary regex),
  never in the tree/count, and the controls do not read `len(paths)` or any live directory count.

## 3 — Advisory (a): `re.fullmatch` vs `re.search` — TESTED, not reasoned about

Ran three commands, repo file **never** touched (in-memory string mutation / `ast.parse` on a
string variable only):

```
$ python3 -c 'import re; left="1 file(s) swept"; print(re.fullmatch(r"\d+ file\(s\)", left) is not None, re.search(r"\d+ file\(s\)", left) is not None)'
False True
exit 0
```
Confirms peer-lead claim (i): `fullmatch` does NOT flag a revert carrying incidental surrounding
text (`"1 file(s) swept" in r.stderr`); `search` would.

```
$ python3 -c '<load real file source, walk AST with fullmatch-pattern and with search-pattern>'
fullmatch hits on real current source: []
search hits on real current source: []
exit 0
```
Confirms peer-lead claim (ii): switching the walker's regex to `re.search` produces **zero**
false-fires against the real, current file — the control literals (`"41 file(s) swept"`, etc.)
sit inside `check(...)`/`reports_exactly_one_file(...)` **call arguments**, not as the left operand
of a `Compare`/`In`/`NotIn` node, so the structural (node-type) filter — unchanged by the regex
choice — already excludes them. No cost to switching.

```
$ python3 -c '<same walk, but over an in-memory copy with one callsite reverted to
  "1 file(s) swept" in r.stderr>'
fullmatch hits on mutated source: [] -> guard would MISS the mutation
search    hits on mutated source: [335] -> guard would CATCH the mutation
exit 0
```
End-to-end proof: a realistic revert-with-suffix mutation at line 335 is **silently missed** by
the guard as shipped (fullmatch), and **caught** by the `search` variant, at zero measured cost.

**Ruling: should_fix.** Not must_fix — the guard as shipped still catches the *exact* historical
defect shape (verbatim bare-substring revert), which is the shape that actually happened twice in
this feature's history. But `search` is strictly stronger, empirically zero-cost, and one line to
change, guarding the exact class of near-miss revert (a reviewer restoring the old assertion with
a plausible tweak like appending context to the message) that a human hand-edit is likely to
produce. Given this file has already needed three remediation cycles for this one defect class,
leaving a free strengthening on the table is a real, if modest, maintainability gap.

## 4 — Advisory (b): the walker's own self-grade

```
$ python3 .claude/skills/harness/bin/code-grade.py --json .claude/skills/harness/bin/test-validate-feature-json.py
exit 0
```
Extracted record for `_rendered_count_substring_compares`: `cyclomatic=8, cognitive=10, abc=12.7,
driver=cognitive, grade=3, bar=3, result=PASS`. Confirms the task's framing: it passes, but sits
exactly at its bar with zero grade-band headroom on its binding metric (cognitive, driver of the
grade). Cyclomatic (8) is also exactly at its own band ceiling for grade 4 (`<=8`), so two of its
three metrics are pinned at their respective band edges. Precision on "one edit from red": cognitive
would need to rise from 10 to >15 to actually drop the overall grade to 2 (a `result: FAIL` in
`code-grade.py`'s own JSON/text, per `_result`); reading `code_grade.py`'s `_blocks`, a drop to
grade 2 does not trip the tool's own exit-1 gate (`_blocks` special-cases grade 2 as `severity: med`,
not blocking) — only a further drop to grade 1 would. So "red" in the exit-code sense is two grade
bands away, not one; "red" in the JSON `result` field's own display is one band away. Either way,
zero headroom on a freshly-introduced guard is the fact, independent of exactly which "red" is meant.

Checked whether any automated gate is watching this specific function for regression: read
`test-code-grade.py`'s `SELF_GRADED_FILES` tuple (the CR-01 meta-gate that requires every `.py`
file *this feature* changed under `bin/` to either appear there, graded against its own bar with
any below-bar function named in `SELF_GRADING_ALLOWLIST`, or be excluded by a one-line comment).
`test-validate-feature-json.py` is **absent from `SELF_GRADED_FILES`** — not tracked, not
allowlisted, not excluded by comment. It is a FEAT-14 file only incidentally touched by this
cycle's fix, so CR-01's original scope (computed at an earlier review cycle, for the code-grading
engine's own source files) plausibly never intended to cover it — but the file *has* now been
changed by this feature's branch, and CR-01's own stated rule ("every changed file must appear
here or be excluded... none are excluded") does not currently hold for it.

**Ruling: should_fix.** Not must_fix — the function passes cleanly under the tool's own intended
PASS band (grade 3 ≥ bar 3 is a legitimate pass, not a violation of any written rule), and it is
demonstrably correct today (Item 2's mutation test). But this is the last line of defense for a
defect class that has already cost this feature three remediation cycles, and no automated gate
anywhere is watching this specific function's grade going forward — a later edit (e.g. extending
the walker to close one of Item 1's stated gaps) could silently push it into `result: FAIL`
territory with nobody noticing until the next manual review. Recommend either adding
`("test-validate-feature-json.py", "_rendered_count_substring_compares")` to the CR-01 tracking
machinery, or trimming the walker's cognitive complexity for headroom. Out of scope for me to
decide which; flagging as an open question.

## 5 — No FEAT-43 source regression

```
$ git -C <worktree> diff --stat 1d292c2b2e22486fd7ad47fa9021ddec880dabcb..73c636dda65977faa9f9c171eedad35fed3213eb
 .../harness/bin/test-validate-feature-json.py      |  92 ++++++-
 .../FEAT-43-code-risk-grading/feature.json         |   8 +-
 .../notes/qa-mergedelta.md                         | 277 +++++++++++++++++++++
 .../review-harness-code-reviewer-mergedelta.md     | 180 +++++++++++++
 .../review-harness-security-reviewer-mergedelta.md | 269 ++++++++++++++++++++
 5 files changed, 822 insertions(+), 4 deletions(-)
exit 0
```
The only `.py` file in this diff is the target test file. FEAT-43's own graded-engine source
(`code_grade.py`, `code-grade.py`, `gate_policy.py`, `validate-digest.py`,
`check-plan-routes.py`, and their tests) is **not present in this diff at all** — untouched
between the two pins. The other four changed paths are `feature.json` (feature state) and three
review/QA note files from the concurrent merge-delta review wave — process artifacts, explicitly
non-goal ("main's own content" / prior review waves), not source.

## Verification performed

- `git log --oneline -1` → `73c636d test: replace the count substring predicate at all three
  callsites and guard them` — HEAD is the pin.
- `git status --porcelain` at start and end: **identical** (diffed, no output). Pre-existing
  worktree-local state (`feature.json` modified, several untracked `answers/`/`notes/` files) was
  present before I started and is unrelated to my read-only work.
- `git status --porcelain -- .claude/skills/harness/bin/test-validate-feature-json.py`: empty —
  the target file itself carries no modification.
- `git -C /Users/molchairuangutai/GitHub/harness status --porcelain | grep -v '^??'`: no output —
  the main checkout has no tracked modification (only pre-existing untracked feature/log dirs).
- Ran the test file directly end-to-end against the live tree
  (`HARNESS_PROJECT_DIR=$PWD python3 .../test-validate-feature-json.py`): exit 0, `ALL PASS`,
  including all three new cases and the two rewritten callsite assertions — confirms the fix and
  controls work against the real, current (41+ directory) repository state, not just synthetic
  strings.

## What I did NOT cover

- The full `run-unit-tests.sh --kind unit` wrapper (ran the test module directly instead — same
  cases, same result) or any canonical suite beyond it — explicit non-goal.
- The eight already-closed FEAT-43 defects, and `main`'s own content (feature.json / note-file
  changes in this diff) — explicit non-goals.
- The callsite-mutation experiment — explicitly reserved for the QA wave that runs after this
  review, against the same pinned tree.
- Any fix, edit, or mutation to the actual repository file — read-only per role; both advisories
  are reported as findings, not applied.

```yaml
VERDICT: PASS
DIGEST:
  headline: "All three callsites route through the shared word-boundary predicate with no fourth site and no live gap; two zero-cost strengthenings (fullmatch->search, self-grading tracking) are should_fix, not must_fix."
  severity_max: med
  findings: 2
  must_fix: []
  spec_violations: []
  reviewed: "1d292c2b2e22486fd7ad47fa9021ddec880dabcb..73c636dda65977faa9f9c171eedad35fed3213eb"
  human_commits_in_scope: []
  open_questions:
    - { id: Q1, question: "Should _rendered_count_substring_compares's regex move from re.fullmatch to re.search (empirically zero false-fire cost, catches a realistic revert-with-suffix mutation that fullmatch misses)?", blocking: false }
    - { id: Q2, question: "Should test-validate-feature-json.py (and _rendered_count_substring_compares specifically) be added to test-code-grade.py's SELF_GRADED_FILES/SELF_GRADING_ALLOWLIST tracking, since it currently sits at grade==bar with zero headroom and no automated gate watches it?", blocking: false }
  files_touched: []
  expertise_update: []
artifact: .harness/harness/features/FEAT-43-code-risk-grading/notes/review-harness-code-reviewer-delta-c29.md
```
