# Security review — FEAT-20-migration-detector — diff `88b1182..ea476fd`

## Verdict: PASS (scoped in, info-level only)

The diff adds a detector (`layout_migration.py`), its call site in `check-state.sh`, a CI
step in `.github/workflows/tests.yml`, and tests/docs. It reads repo-local files, globs
one directory level, prints a report, and exits 0/1/2. No new network input, no new
credentials, no new persisted user data. Scoped IN per the dispatch's named surfaces
because the code reads files it did not author and prints to CI logs and session output;
all five named surfaces were assessed and dismissed, one pre-existing item noted below
for the harness owner (not a defect in this diff).

## Surfaces assessed

**1. Regex ReDoS in `READER_TABLE` (`layout_migration.py:79-98`).** Every pattern is
either a literal, a bounded alternation, or a single unbounded quantifier
(`[^,)]+`, `[^/ ]+`, `[^/"]+`) with no nesting and no overlapping character classes —
the structural precondition for catastrophic backtracking (nested/ambiguous
quantifiers) is absent from all seven rows. Confirmed empirically: matched all four
distinct quantifier shapes against a 400k-char adversarial string (`(`×200000 +
`x`×200000); all four completed in <0.3ms. Not a finding.

**2. Traversal / unbounded walk in globbing (`layout_migration.py:127-137`).** Both
`_evidence()` globs (`.harness/features/*/feature.json`,
`.harness/*/features/*/feature.json`, and the docs equivalents) are single-level `*`
globs (`glob.glob`, not `**`/`glob(recursive=True)`), so each call is one `listdir`, not
a recursive tree walk — no symlink-loop or unbounded-depth DoS. `_reader_formset()`
reads exactly the seven fixed relative paths named in `READER_TABLE` (module-level
constants, not derived from any scanned input) joined onto `root`; the only variable is
`root` itself, which is operator/CI-supplied (`CLAUDE_PROJECT_DIR` or `.`), not
attacker input from repo content. Not a finding.

**3. GitHub Actions step (`.github/workflows/tests.yml:183-233`, "Layout gate").** The
only `${{ }}` interpolation is `${{ github.workspace }}`, a runner-trusted context value,
not PR/branch/commit-message content — the classic script-injection vector (untrusted
`${{ github.event.* }}` spliced into `run:`) is absent. All other shell variables
(`out`, `summary`, `examined`, `feature_dirs`, `doc_roots`, `reader_files`) are derived
from the local script's own stdout via `grep`/`sed`/`awk`, not from external input. Not a
finding.

**4. Data exposure in detector output.** `render()` (`layout_migration.py:216-243`)
prints only fixed repo-relative paths from `READER_TABLE` plus counts — no file
contents, no environment values, no credentials. These paths (e.g.
`.claude/skills/harness/bin/check-domain.sh`) are already public in the repository the
detector runs against. Not a finding.

**5. In-process import in `check-state.sh`'s heredoc — real finding, but pre-existing,
not introduced by this diff.** `check-state.sh` does `cd "$root"` then
`python3 - "$root" <<'PY'` with `PYTHONPATH="$_selfdir:..."`. For a script fed on stdin,
CPython puts `''` (cwd) at `sys.path[0]`, **ahead of** every `PYTHONPATH` entry — verified
directly: `PYTHONPATH=/anything python3 -c 'import sys;print(sys.path[:2])'` →
`['', '/anything', ...]`. Since `cd "$root"` runs before the heredoc, `''` resolves to
the *scanned* root, not `_selfdir`. Concretely: if `CLAUDE_PROJECT_DIR` points at a repo
whose root contains a file named `harness_yaml.py`, `os.py`, `re.py`, `glob.py`, or
`json.py` (or, after this diff, `layout_migration.py`), that file — not the real
module — is what gets imported and executed at every `/harness` session entry, before
`layout_migration.scan()`'s own D-04 applicability gate ever runs (the import happens
unconditionally at heredoc top).

Diffed against `88b1182` (`git show 88b1182:.../check-state.sh` lines 1-35): the
identical `cd "$root"` + heredoc-with-`import harness_yaml"` structure predates this
diff byte-for-byte. This diff's only contribution is one additional shadowable module
name (`layout_migration`) added to an already-open pattern — it does not create the
cwd-precedence behaviour, widen who can trigger it, or change who can plant a file at a
scanned root. Per P-08/P-12: assessed and dismissed as a **pre-existing** issue, not a
regression in this diff, so it does not gate this review. Recording as an open question
for the harness owner below, since it is real and was not previously named in the
decisions I could find.

**One inaccuracy worth flagging separately:** `test-check-state.py` case x.5's comment
says "the script prepends ITS OWN dir to PYTHONPATH, so a shadow dir cannot outrank the
real module." That is true for PYTHONPATH-listed directories but false for the cwd
(`''`), which precedes PYTHONPATH entirely. Someone citing that comment later as proof
the import is safe from shadowing would be relying on a false statement. Info-level,
in the diff, worth a one-line correction whenever this area is next touched.

**6. Secrets sweep across the full diff (2696 lines, all 22 files, not just the 8 named
source files).** `git diff 88b1182..ea476fd | grep -iE 'token|secret|api[_-]?key|password|ghp_|AKIA'`
— one hit, in `docs/harness/DECISIONS.md` prose: "...whose leading token is the pinned
literal NOT APPLICABLE..." — the English word "token" describing a string literal, not a
credential. No secrets found.

## Not findings, explicitly

- Test files (`test-layout-migration.py`, `test-check-state.py` case_x) use only
  `tempfile.TemporaryDirectory()` fixtures, no `subprocess`/`shell=True`/`eval`/`exec`,
  no committed credentials.
- `run-unit-tests.sh` change is a one-line array addition (test registration), no
  security surface.
- `DECISIONS.md`/`DECISIONS-INDEX.md` changes are prose-only.

```yaml
VERDICT: PASS
DIGEST:
  headline: "Layout-migration detector is read-only, single-level-glob, linear-regex; no injection, no new secrets, no new auth surface — one pre-existing (not introduced here) cwd-shadow import risk in check-state.sh's heredoc, flagged as an open question, not a gate."
  in_scope: true
  scope_reason: "Diff adds code that reads files it did not author (READER_TABLE against arbitrary repo content) and writes to CI logs and session-entry output; all five dispatch-named surfaces (ReDoS, traversal/DoS, GH Actions injection, output data exposure, in-process import) were checked."
  severity_max: info
  findings: 2
  must_fix: []
  threat_model:
    - { boundary: "layout_migration.py reading repo-local files named in READER_TABLE", stride: "T", mitigated: true }
    - { boundary: "GitHub Actions Layout gate step run: block", stride: "T|I", mitigated: true }
    - { boundary: "check-state.sh heredoc import resolution (cwd precedes PYTHONPATH)", stride: "E", mitigated: false }
  open_questions:
    - { id: Q1, question: "check-state.sh's heredoc runs `cd \"$root\"` before `python3 -`, so sys.path[0] is the scanned root's cwd, ahead of PYTHONPATH — a top-level file at CLAUDE_PROJECT_DIR named harness_yaml.py, os.py, re.py, glob.py, json.py, or (as of this diff) layout_migration.py is imported and executed at every /harness session entry instead of the real module. This predates this diff (identical shape at 88b1182 with the harness_yaml import) so it is not a regression gating FEAT-20, but it looks like a real RCE-shaped gap on any repo root not fully trusted (e.g. an untrusted PR branch checked out as CLAUDE_PROJECT_DIR). Worth its own ticket.", blocking: false }
    - { id: Q2, question: "test-check-state.py case x.5's comment claims a shadow dir 'cannot outrank the real module' via PYTHONPATH prepending — true for PYTHONPATH entries, false for cwd. Worth a one-line correction next time that test is touched, to prevent someone citing it as proof of safety.", blocking: false }
  files_touched: []
  expertise_update: []
artifact: .harness/features/FEAT-20-migration-detector/notes/review-harness-security-reviewer-c0.md
```
