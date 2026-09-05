# Security Review — Cycle 2 — BUG-1286-test-tree-enforcement

**VERDICT: PASS.** The cycle-11 refactor (`bb3a31ed`) is behaviour-preserving on every axis this
role checks. No new security surface, no widened one, no regression to the guard's fail-closed
posture. One new function (`_violations_callers` in the B-3 test) reads tracked source files by
path; traced to no exploit chain beyond what commit access already grants.

## What I examined before scoping

Enumerated the diff two ways, per the dispatch:

1. **Full feature diff** (`merge-base(origin/main, bb3a31ed)` .. `bb3a31ed`, 80 files) — confirmed
   this is the whole feature's accumulated history (BRIEF, plan.yaml, ~60 notes/receipts/research
   docs, prior commits' code). Grepped the entire diff for
   `password|secret|token|api[_-]?key|bearer|credential|BEGIN (RSA|OPENSSH|PRIVATE)|ssh-rsa|AKIA…`
   — every hit is either LLM-context "tokens" (`input_tokens`, `…_warn_tokens`) or the pre-existing
   `RESIDUE_TOKENS` prose-detector constant in `suite-census.py`. No credential-shaped string.
2. **This cycle's actual diff**, isolated with `git diff 9adbce6b..bb3a31ed` restricted to the
   three authorised paths, confirmed by `git log --oneline` on those paths that `bb3a31ed` is the
   *only* commit touching them since the previous pin. Full diff-stat of `bb3a31ed` vs its parent
   (17 files) confirms nothing outside `suite_layout.py`, `test-suite-layout.py`,
   `qa-tree-audit.md` (the authorised B-2 one-token SHA fix), and administrative record files
   (`STATE.md`, `feature.json`, receipts, observations) changed — `tests/integration/test-run-unit-
   tests-layout.py` and `tests/manual/suite-census.py` are untouched this cycle.
3. Read the full post-refactor `suite_layout.py` (216 lines) end to end, not just the diff hunks,
   to see every helper in final form and confirm `tracked_paths`, `is_test_shaped`, and
   `DOCUMENTED_EXCEPTIONS` themselves are byte-unchanged (diff shows zero touch to those).

No pre-emptive skip: the surface (a subprocess-shelling repo-layout guard) has an established prior
review (cycle 1, `review-harness-security-reviewer-c1.md`) that already covered `tracked_paths`'
argv construction, `shell=True` absence, PATH resolution, stderr echo, and realpath comparison. This
cycle's question is narrower by the dispatch's own framing — did decomposition widen it — and I
answer that question directly below rather than re-deriving cycle 1's conclusions.

## Decomposition audit (`suite_layout.py`, B-1)

Diffed `9adbce6b..bb3a31ed` for this file line-by-line against the dispatch's four sub-questions:

- **(a) subprocess invocation moved to a weaker-construction path?** No. `tracked_paths()` is
  untouched — same two list-form `subprocess.run` calls (`git ls-files -z`, `git rev-parse
  --show-toplevel`), same `cwd=root`, no new call site added anywhere in the twelve new helpers.
  Every helper operates on already-resolved data (`tracked` tuple, `Path` globs); none shells out.
- **(b) string interpolation into a command?** None introduced — no f-string or `%`/`.format()`
  feeds any `subprocess.run` argv anywhere in the diff.
- **(c) exception handler broadened, now swallowing rather than reporting?** No. The single
  `except LookupError` in the old inline block moved verbatim into `_tracked_scan`, same exception
  class, same outcome: caught → converted to a `"cannot enumerate tracked files under {root}: {error}"`
  finding, never silently dropped. `_tracked_scan` returns `([finding], None)` on that path, and the
  caller (`violations`) always appends whatever `_tracked_scan` returns via `out.extend(scan_findings)`
  — there is no branch that discards it.
- **(d) finding-string content changed (path disclosure via logs)?** No. Every emitted string
  (`"documented exception is not an exact path: …"`, `"…is listed twice: …"`,
  `"…is unnecessary: …"`, `"…is no longer tracked: …"`, `"{unit} contains no test-*.py"`,
  `"{name} appears in both …"`, `"test file is not selected by the runner: {path}"`,
  `"test-shaped file remains under bin: {path}"`, `"cannot enumerate tracked files under {root}: …"`,
  `"tracked test-shaped file outside tests/: {rel}"`) is moved, not edited — confirmed by diffing the
  `+` lines against the corresponding `-` lines token-for-token. All paths echoed are already
  repository-relative or repo-local paths the guard itself computed, same class of value as cycle 1
  reviewed; nothing new is interpolated into a message.

**Ordering (D-03, the one way this refactor could fail-open):** confirmed structurally correct. The
git-toplevel `realpath` comparison lives *inside* `tracked_paths()` (unconditional, executes before
that function returns on any success path) and is called first thing inside `_tracked_scan()`;
`_tracked_scan` only reaches the self-ownership test (`".claude/skills/harness/bin/suite_layout.py"
not in tracked`) after `tracked_paths()` has already returned successfully. `violations()` calls
`_tracked_scan` before `_registry_findings`, same sequence as the original inline code. A fixture
root nested inside another checkout still raises `LookupError` from `tracked_paths()` before any
self-ownership branch is reached — it is reported as a violation, not silently accepted. This
matches D-03's literal text (`plan.yaml:122-133`) and is unchanged by the refactor.

**Registry rules (4 clauses) still able to fire:** yes — `_duplicate_or_malformed` covers rules 1–2
(glob-shaped, duplicate), `_unnecessary_or_stale` covers rules 3–4 (unnecessary outside `tests/`,
no-longer-tracked); `_entry_finding` composes them with the same short-circuit order and the same
`seen.add(rel)` timing (only after the first two rules pass) as the original single loop.

**Vocabulary (D-01/D-04):** confirmed a single `is_test_shaped()` implementation, called from both
`_unnecessary_or_stale` (registry clause) and `_tracked_outside_tests_findings` (repo-wide clause) —
no second inline spelling introduced.

## B-3's new scan (`test-suite-layout.py`, `_violations_callers`)

Read the new helper and the assertion (`check("violations() has exactly one non-test caller…")`).

- Uses `git ls-files` (list-form, `check=True`, no `shell=True`) scoped to `cwd=ROOT` — the test's
  own repository root, not attacker-controlled input.
- Filters out `tests/`-prefixed paths, then filters by extension (`SOURCE_EXTENSIONS`) — `.md` is
  excluded, so the nine `notes/`/`BRIEF.md` prose mentions of `violations()` structurally cannot
  satisfy or break the assertion. **Verified empirically**, not just read: built a synthetic
  throw-away git fixture (`/tmp`, no writes to the worktree) with (1) the real caller
  (`run-unit-tests.sh`), (2) a second `.py` file calling `suite_layout.violations(x)`, (3) a `.md`
  file mentioning `violations()` in prose only. `_violations_callers` returned both real callers
  and ignored the `.md` file; the assertion's equality check evaluated `False` (red) with the second
  caller present, and `True` (green) once it was removed. This is the identity-level evidence the
  assignment asked for, not a read-and-conclude claim.
- **Read/symlink note (new code, INFO, not gating):** `(root / rel).read_text()` opens whatever
  `git ls-files` lists, following a checked-out symlink if one were committed at a source-extension
  path outside `tests/`. In principle a committer could plant a tracked symlink pointing outside the
  repo and have its target's content scanned by this regex. Traced the exploit chain and stopped:
  planting a tracked symlink already requires commit access to this repository, which is the same
  privilege level needed to edit `suite_layout.py` or the guard directly — no escalation, and the
  matched content is never echoed, only the *filename* is added to a list that appears solely in
  `repr()` on assertion failure. Per this role's own pattern (an actor who already controls a value
  already holds the privilege it grants), this is not a finding.
- **Detection-scope note (INFO, not gating):** the regex `suite_layout\.violations\(\s*[^)\s]`
  matches only the literal spelling `suite_layout.violations(`. An aliased import
  (`import suite_layout as sl; sl.violations(x)`) or `getattr`-based dispatch would evade it,
  producing a false "single caller" green on a second real caller. This is a test-robustness gap,
  not a security one: the threat model requires an insider with commit access intentionally evading
  a repo-hygiene assertion, who already has the access needed to edit the assertion itself or the
  guard it protects. Recording it here so it isn't silently reintroduced as a security finding by a
  later reviewer; routing it to code-review/QA as a test-quality note is more appropriate than a
  security gate.

## STRIDE — Tampering axis

Cycle 1 dismissed "the guard's own source is editable by a careless commit" as generic and not
introduced by that cycle's diff. **Assessed again at this pin, unchanged, still not introduced by
this diff** — the guard's editability is a property of every commit to this repository, not
something `bb3a31ed`'s decomposition created or altered. No STRIDE boundary in this diff crosses
from a lower-trust to a higher-trust actor; the only "actors" here are repository committers acting
on their own already-owned files. ASSESSED-AND-DISMISSED, not re-raised as a finding.

## Conclusion

Security surface: **preserved**, not widened, not narrowed. Zero gating findings. Two INFO-level
observations recorded above for the record (symlink-follow reachability, regex detection scope);
neither meets this role's bar for a finding (no describable attacker gain beyond pre-existing
privilege).
