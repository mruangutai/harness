# QA confirm-falsifiability — FEAT-14, review_sha 1c5fd67 (HEAD 12e3fa2)

## Step 0 — binding
HEAD = `12e3fa2`. `.claude/skills/harness/bin/{gh-sync.py,test-gh-sync.py,check-domain.sh,test-check-domain.py}`
all clean. `git diff 1c5fd67..12e3fa2 --stat` touches only `feature.json` (the pin bump) — pin-only,
confirmed. Every result below is measured against the pinned tree.

## Step 1 — T-06C retirement: SOUND RETIREMENT, REPLACEMENT PIN MISSING

Mutant (disposable worktree at HEAD): `load_recorded`'s `doc = json.loads(text)` reverted to
`doc = yaml.safe_load(text)` (imported `yaml`, widened the except to `yaml.YAMLError`) — the exact
inverse of the B-5 convergence the retirement cites.

**Result: `test-gh-sync.py` stayed fully green — 74/74 — under the mutant.** No fixture in the file
distinguishes a YAML reader from a JSON reader anymore.

Why: every JSON fixture is valid YAML (superset), so the happy-path cases can't discriminate. The
one case that *could* — `fix1 B row2`, the 0-byte file — asserts
`"does not parse" in str(e) or "cannot be known" in str(e)` (`test-gh-sync.py:798-799`). Under
`yaml.safe_load`, an empty string parses to `None`, which fails the `isinstance(doc, dict)` check and
raises the **different** message `"... parsed but is not a JSON mapping ... cannot be known. Refusing
to sync ..."` — and that message *also* contains `"cannot be known"`. The OR'd substring check passes
under both the JSON reader and the reverted YAML reader; it cannot fail on this mutation.

`test-gh-sync.py:720-722` ("FEAT-14 fix1 (B-5) converged feature.json's reader on json.load ... the
old comment-tolerance assertion is retired by design") is a **comment block**, not an executable
assertion — confirmed by reading it directly; it asserts nothing.

**No inverse assertion exists.** Nothing in the file feeds `load_recorded` a comment-bearing
(`#`-suffixed) fixture and asserts rejection — the replacement the retirement's own justification
implies is missing.

**Verdict: SOUND RETIREMENT, REPLACEMENT PIN MISSING.** The eng lead's justification is verified
true, not pretextual — B-5 genuinely moved the reader to `json.load`, and a comment-bearing fixture
is unparseable by construction under it, so retiring the old assertion was the right call. What did
not happen is writing its replacement: no fixture feeds `load_recorded` a comment-bearing document
and asserts rejection, so B-5's reader-contract (JSON-only, not YAML) is currently unbound by any
test that can fail on it. Measured by mutation, not reasoned.

## Step 2 — corroboration

- **Pre-fix `gh-sync.py` (`0b33188`) + HEAD's `test-gh-sync.py`:** exactly **6 failures**, all
  `fix1 *` (`fix1 B row2` zero-byte, `fix1 B row2 (a_list)`, `fix1 B row2 (a_scalar)`,
  `fix1 B row4 (github=a_string)`, `fix1 B row4 (github=a_list)`, `fix1 A: a failed save_recorded
  leaves feature.json byte-identical`). Zero others. **Matches the expectation exactly.**
- **Pre-fix `check-domain.sh` (`8dc5650`, parent of `0b33188`) + HEAD's `test-check-domain.py`:**
  exactly **1 failure** — `schema/a CRASHING schema module DENIES the write rather than letting it
  through` (`wanted exit 2, got 1` — fail-open reproduced). Zero others. **Matches the expectation
  exactly.**

Both corroborated as reported.

## Step 3 — vacuity check, HIGH-1's new `test-check-domain.py` fixtures (`run_schema`, ~1382-1447)

- **Genuine crash, not a stub.** The fixture physically patches `feature_schema.py` on disk (injects
  `raise ValueError("injected: checker is broken")` into `problems_for_text`) and invokes
  `check-domain.sh` as a real subprocess via `fire()`, then restores byte-identically and **asserts**
  the restore (`test-check-domain.py:1441-1445`). Not simulated.
- **Exit code is asserted** — `case(..., r.returncode, 2, ...)` at `:1434-1437` — the load-bearing
  signal per the dispatch (1 vs 2).
- **The crash-vs-import-message distinction is unpinned.** `check-domain.sh:894-916` separates
  `"feature_schema is not importable"` (ImportError branch) from `"feature_schema CRASHED"` (any
  other exception) specifically so a reader isn't sent chasing PYTHONPATH for a fault that isn't
  there. `test-check-domain.py` has **no fixture that makes `feature_schema` itself unimportable** —
  only `"not importable"` and `"PYTHONPATH"` string occurrences in this file are in a *different*
  fixture (`harness_yaml`, lines 290-301), unrelated to the schema gate. The attribution the fix
  exists for is untested. Adequacy note, not a must_fix (per dispatch).
- **Route coverage: Write only.** All three `run_schema` cases call `fire()`
  (`test-check-domain.py:104-108`), which hardcodes `tool_name: "Write"`. Neither an Edit payload nor
  the Bash `PostToolUse` sweep is exercised for the schema check specifically — `shape_problems` (the
  shared function containing the schema gate) is reached from a single shared loop
  (`check-domain.sh:1201-1203`), so it is *plausible* both routes reach the same code, but nothing in
  this suite demonstrates it for the schema branch. Two of three routes are unbound for HIGH-1's own
  fix.

(HIGH-3 out of scope — noting only: nothing above bears on SC-04/05/16 automated assertions.)

## Step 4 — the four gates (verbatim exit codes)

| Gate | Result | Load-bearing for either HIGH? |
|---|---|---|
| `run-unit-tests.sh` (default `--kind all`) | **0** — last line `PASS test-factory-integration.py`, all suites green | Partial — it runs `test-gh-sync.py` and `test-check-domain.py` in-place at HEAD, so it confirms the fixes don't regress anything else, but it is the same green already interrogated by mutation above — it does not, by itself, prove either HIGH's new assertion discriminates (that needed the worktree mutants) |
| `validate-digest.py` over the feature's 19 run digests (persona `lead` — the files derive from `-eng`/`-product`/`-validator` suffixes, all map to `lead`) | **0** for all 19 | Not load-bearing for either HIGH — digest schema conformance, orthogonal to the fix |
| `check-state.sh` | **0** (all findings are `note`-level, none `FAIL`) | Not load-bearing for either HIGH — general corpus hygiene, one `note` names an orphaned `confirm-validator` run dir on this feature but that's bookkeeping, not the fix |
| `check-plan-routes.py` | **0**, `0 violation(s) across 10 plan(s)` | Not load-bearing for either HIGH — grant/route drift across all plans, unrelated to the schema/gh-sync fixes |

## Tree state

`git status --porcelain` (repo root), taken AFTER writing this artifact:
```
?? .harness/features/FEAT-14-feature-json-schema/notes/qa-confirm-falsifiability.md
?? .harness/features/FEAT-14-feature-json-schema/notes/review-harness-code-reviewer-confirm.md
```
Both untracked: this artifact (mine, expected) and the parallel code-reviewer's artifact (not mine,
left as found). No modified/staged files. The four DEC-174 carve-out files are clean (verified before
and after).

`git worktree list` at finish:
```
/Users/molchairuangutai/GitHub/harness                                                12e3fa2 [feat/204-feature-json-schema]
/private/.../scratchpad/feat14-probe                                                  cf15660 (detached HEAD)
/Users/molchairuangutai/GitHub/harness/.claude/worktrees/FEAT-13-single-issue-board-lookup  ec7d463 [feat/FEAT-13-single-issue-board-lookup]
```
`feat14-probe` predates this run (not created by me). Checked read-only:
`git -C <path> status --porcelain` is **empty** — it holds no live mutant; the dispatch's warning
about an earlier run's live mutant does not describe this worktree's current state. Not removed —
ownership unclear, and removing another agent's worktree without knowing whether it's still in use
risks destroying in-progress state; that call belongs to the operator. The three worktrees I created
(`wt-step1`, `wt-prefix`, `wt-cd`) were each removed with `git worktree remove --force` immediately
after use; none remain.
