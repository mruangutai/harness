## Security review — BUG-1286-test-tree-enforcement — panel cycle c1

**Verdict: PASS, info-only.** Scoped in (a fail-open/fail-closed integrity-control question is a
real STRIDE Tampering/Repudiation question even without network/auth surface), examined all four
dispatched items against the pinned diff `1977ebd6..9adbce6b`, found no exploitable defect. One
theoretical fail-open path exists in the Python API surface but is empirically unreachable through
the only real caller.

### What I examined

Read verbatim: `suite_layout.py` full diff (+116, `git diff 1977ebd6..9adbce6b --
.claude/skills/harness/bin/suite_layout.py`), `run-unit-tests.sh` in full, `suite-census.py` in
full (plus its diff, to separate new `tree-audit` code from pre-existing FEAT-47 code),
`tests/integration/test-run-unit-tests-layout.py` in full, `tests/unit/test-suite-layout.py`
imports/fixtures/case-11 region, plan.yaml D-01–D-06, and the DECISIONS.md/DECISIONS-INDEX.md diff
(docs-only, 3+/0- and an index-row rewrite — nothing security-relevant). Ran two things: the real
`test-run-unit-tests-layout.py` (14/14 PASS, corroborates orchestrator's 14 PASS / 0 FAIL), and a
throwaway repro standing up a rootless (`.git`-absent) tree with a planted `.harness/test_rogue.py`
to test whether the guard's fail-open branch is reachable through the real entrypoint.

### Item 1 — `tracked_paths()` shell-out

**No injection.** Both calls (`git ls-files -z`, `git rev-parse --show-toplevel`) use list-form
`argv` with `cwd=root`, no `shell=True`, no string interpolation of any value into a command
string — confirmed by grep across all four target files plus `suite-census.py`'s new
`_vocabulary_paths`: every subprocess call in the diff is list-form. `cwd=root` is caller-supplied
(from `run-unit-tests.sh`'s own `harness_boundary.resolve_root()`, not attacker input) and is not
shell-interpreted by `subprocess.run`. PATH-based resolution of the `git` binary is a real, generic
property of every `git`-shelling script in this codebase (`code_grade.py`, `suite-census.py`'s
pre-existing `migration`/`residue`, `run-unit-tests.sh` itself) — not introduced or widened by this
diff, and not exploitable without an attacker who can already plant a binary earlier on a trusted
developer's `PATH`, i.e. no privilege the attacker doesn't already have (P-02). 20s timeout: on
expiry, `TimeoutExpired` is caught and re-raised as `LookupError`, which is appended to `out` as a
violation — so a hang **fails closed** (`MISCONFIGURED`, exit 2), not silently. `listed.stderr`
reaching output: yes, `tracked_paths()` takes `next(iter(listed.stderr.splitlines()), ...)` and
`violations()` folds it into `"cannot enumerate tracked files under {root}: {error}"`. This is
git's own diagnostic text (e.g. `fatal: not a git repository`), generated from repo *state* not
repo *content* — no tracked file's bytes are echoed. The only user-influenced substring is `root`
itself (a local path), printed to a local developer's own stderr; no cross-trust-boundary leak.
**Verdict: no finding.**

### Item 2 — path handling

`os.path.realpath(toplevel) != os.path.realpath(root)` correctly resolves symlinks on both sides
before comparing, closing the "fixture root nested inside another checkout" case described in
plan.yaml D-03 — confirmed the ordering (toplevel check runs *inside* `tracked_paths()`, hence
*before* the self-ownership `suite_layout.py in tracked` check in `violations()`), matching D-03's
explicit constraint that this ordering "must not be moved." NUL-separated parsing
(`listed.stdout.split("\0")`) is the correct choice specifically because `git ls-files -z` emits
unquoted, NUL-terminated paths — a tracked path containing spaces, quotes, or embedded newlines
parses correctly and cannot be split incorrectly or used to smuggle a second path, unlike the
non-`-z` form which quotes/escapes and can be misparsed by naive splitting. `Path.rglob` /
`relative_to` usage in the new code (`planted_rel = {p.relative_to(root).as_posix() for p in
set(planted)}`) is purely syntactic (no filesystem resolution) over paths already constructed as
`root / ".claude/skills/harness/bin" / name`, so it cannot raise or misresolve regardless of
symlinks. **Verdict: no finding** — path handling in this diff is done correctly, notably more
carefully than a shell-based `git ls-files` + naive split would have been.

### Item 3 — fail-open-while-reporting-success (Tampering/Repudiation)

This is the one place I'd flag as worth a second look, and I judge it **assessed, not gating**, on
direct empirical grounds, not just reading the code:

- `violations()`'s repo-wide clause requires three preconditions before it scans anything: `.git`
  exists at `root`, `git rev-parse --show-toplevel` (inside `tracked_paths()`) resolves to `root`
  itself, and the tracked index contains `suite_layout.py` at its own real path. Fail any one and
  the repo-wide scan **silently does not run** (no violation recorded for the precondition
  failure itself) — the *shape* of a fail-open integrity control.
- This is not accidental: plan.yaml D-03 explicitly signs it off — "a root with no index at all
  must stay usable for the synthetic layout fixtures rather than being reported as a failure" —
  and D-02's `_registry_findings` closes the adjacent path (a `DOCUMENTED_EXCEPTIONS` entry with a
  glob character, e.g. someone committing a broad `"*.py"` exemption, is itself flagged as a
  violation, so the allowlist can't be silently widened).
- I did not accept the sign-off on paper alone. I built a throwaway rootless tree (no `.git`) with
  `.claude/` copied in, planted a tracked-shaped rogue (`.harness/test_rogue.py`), and ran the real
  entrypoint, `run-unit-tests.sh --check-layout`, against it directly (not `violations()` in
  isolation). Result: `run-unit-tests.sh: no harness root could be resolved ... — refusing to run`,
  exit 2, in *both* the clean and the rogue-planted case. `harness_boundary.resolve_root()` refuses
  to even start before `suite_layout.violations()` is ever called on a root lacking `.git`. So the
  fail-open branch D-03 accepts is real in the Python API (`suite_layout.violations()` called
  directly, which is exactly what the unit-test fixtures do) but **unreachable through the only
  real caller** (plan.yaml D-03's own claim: "`violations()` still has exactly one caller,
  Harness's own `run-unit-tests.sh`"), which independently refuses first. This closes the gap
  between "signed as acceptable" and "verified to not bite in production."
- Residual, correctly out of my remit: the guard's *source* (`suite_layout.py`,
  `DOCUMENTED_EXCEPTIONS`) is itself repo-tracked code that a malicious or careless commit could
  edit directly (e.g. neutering `is_test_shaped`) — this is the generic "the guard is part of what
  it guards" property of any in-repo static check, unchanged by this diff, and gated by ordinary
  code review, not by anything this feature could add. Naming it so the lead can route it if
  review coverage of `suite_layout.py` itself is ever weaker than assumed.

**Verdict: assessed and dismissed as gating** — signed (D-03), and independently verified
unreachable via the real entrypoint, with a runnable repro rather than a reading of the sign-off.

### Item 4 — secrets / data exposure

Grepped all six target paths plus a repo-root sweep for `password|secret|token|api[_-]?key|
credential` (case-insensitive): every hit in `DECISIONS.md` is "tokens" in the LLM-context-window
sense (e.g. `input_tokens`, `orchestrator_context_warn_tokens`), none credential-shaped; hits in
`suite-census.py` are the pre-existing, unchanged `RESIDUE_TOKENS` literal-string constant
(unrelated to secrets — it detects stale variable-name residue in prose). No environment variable,
credential, or git output is captured and written anywhere durable by the new code — `subprocess`
`stderr`/`stdout` in `tracked_paths()` and `_vocabulary_paths()` is either discarded, folded into a
one-line diagnostic surfaced to the invoking developer's own terminal/CI log, or (in
`tree-audit`) printed as a path census to stdout for human review — the census's own purpose is
"which tracked paths look test-shaped," not anything sensitive. `tests/manual/suite-census.py`'s
`residue()` and `children()` subprocess machinery are pre-existing (confirmed via the file's own
diff — only `_vocabulary_paths`/`_disposition`/`_measure`/`_read_note_rows`/`_print_measurement`/
`_print_diff`/`tree_audit` plus the `add_tree_audit_parser` wiring are new), out of scope for this
diff regardless. **Verdict: no exposure found.**

### Explicit framing

Developer-tooling diff: no network surface, no auth, no external user input, no persistence beyond
the local git index and stdout/stderr of a CLI the invoking developer already controls. The
closest thing to a trust boundary is "committed code vs. the guard that polices committed code,"
and D-02/D-03 already anticipate and close the two ways that boundary could be widened silently
(a glob'd exception, a rootless-fixture carve-out) — both verified above, one by re-reading the
ordering constraint, one by execution.

```yaml
VERDICT: PASS
DIGEST:
  headline: "No exploitable defect; the one fail-open branch (rootless-git precondition, D-03) is signed off and empirically unreachable via the only real caller, run-unit-tests.sh."
  in_scope: true
  scope_reason: "Diff adds a guard that shells to git and reads the tracked-file index (input it did not author), and is itself a fail-open/fail-closed integrity control (STRIDE Tampering/Repudiation) even absent network/auth/user-input surface."
  severity_max: info
  findings: 1
  must_fix: []
  threat_model:
    - { boundary: "suite_layout.tracked_paths() -> git ls-files/rev-parse subprocess", stride: "T", mitigated: true }
    - { boundary: "DOCUMENTED_EXCEPTIONS registry as an allowlist a commit could widen", stride: "T", mitigated: true }
    - { boundary: "violations() repo-wide clause fail-open on missing .git / non-toplevel root / unowned index", stride: "T,R", mitigated: true }
    - { boundary: "guard source itself editable by a malicious/careless commit (generic to any in-repo static check)", stride: "T", mitigated: false }
  open_questions: []
  files_touched: []
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-1286-test-tree-enforcement/.harness/harness/features/BUG-1286-test-tree-enforcement/notes/review-harness-security-reviewer-c1.md
```
