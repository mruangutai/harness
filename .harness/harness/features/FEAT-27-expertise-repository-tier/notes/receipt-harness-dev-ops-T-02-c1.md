# Receipt — harness-dev-ops — T-02 — cycle 1

**BLUF: PASS.** Repository tier added to `inject-expertise.sh`, header/precedence wording
changed per 1a, `cap_body` budget-parameterized, agent-name and segment-name validation added,
18-assertion test suite written and registered, verify green, RED proof shows six failing
cases against b4659cd (not the caller's expected four/five), tree diff clean.

## STEP 1 — baseline (pre-edit)

1. `git show b4659cd:.../inject-expertise.sh | diff - .../inject-expertise.sh` → **empty, exit
   0.** RED baseline tree matches ada8e99 pin, no ESCALATE needed.
2. `run-unit-tests.sh --kind unit` → exit 0, **16/16** script-level PASS (`grep -c
   '^PASS test-'`), no `^FAIL `. `--kind integration` → exit 0, **12/12** script-level PASS, no
   `^FAIL `. No drift-detector exit 2. No pre-existing suite failure.
3. `check-expertise.sh .harness/expertise/` → exit 0, all 15 files `OK`, no `^ADVISORY ` line.
4. `git status --porcelain` snapshot: 3 modified (`STATE.md`, `feature.json`, `plan.yaml` under
   FEAT-27), 4 untracked (`FEAT-26-pr-linkage-recorded/`, two FEAT-27 notes files, one
   observations file) — all pre-existing, none of mine, none touched.

## STEP 2 — the work

Line anchors below are `grep -n` results against the FINAL (post-edit) file — not the
pre-edit read-out lines.

- `inject-expertise.sh:27` — agent-name gate now `grep -Eq '^harness-[a-z0-9-]+$'` before any
  path is built (1c), replacing the old `case ... harness-*)`.
- `inject-expertise.sh:103` — project header text changed to `## Your Expertise — this
  checkout's craft (project tier)`, "authoritative on conflict" removed entirely (verified:
  `grep -c "authoritative on conflict" inject-expertise.sh` → 0).
- `inject-expertise.sh:66-92` — repository-tier discovery: glob
  `$root/.harness/*/expertise/$agent.md`, `[ -r ]` guard (no nullglob needed), segment derived
  and filtered `^[a-z0-9-]+$` (1d), sorted by segment name via a shell sort at line 83
  (`sorted_idx=()` onward) — no `declare -A` (Expertise G-03). Confirmed under the machine's
  actual `/bin/bash` (3.2.57, not just `env bash`'s 5.3.15): ran the script under `/bin/bash`
  directly with a repository fixture, exit 0, correct output.
- `inject-expertise.sh:95-118` — emit group: global, project, then (only if ≥1 repo hit) the
  precedence line once (line 110), then each repository block sorted, then the index —
  repository blocks emitted with `cap_body <file> 40`, craft blocks with `cap_body <file> 150`
  (budget is now `cap_body`'s 2nd arg, per the intent).
- `inject-expertise.sh:95-97` — stale ordering-encodes-precedence comment replaced; new comment
  (line 97: "...ordering here is presentation only, not the precedence rule") states precedence
  is stated explicitly in the emitted line.
- `test-inject-expertise.py` — new file, 12 numbered cases (some producing multiple assertions:
  5a/5b, 7a/7b, 9a/9b, 12×4 values) = **18 total assertions**, all PASS post-edit. Shape follows
  `test-check-expertise.py`: plain python3, `INJECT_EXPERTISE_BIN` env override, temp dirs per
  case, printed PASS/FAIL, `sys.exit(1)` on any fail.
- `run-unit-tests.sh:17` — `"test-inject-expertise.py"` appended to `UNIT_SCRIPTS`.

## STEP 2b — hermeticity decision

`HOME` is neutralized per case via a fresh `tempfile.mkdtemp()` per subprocess call (not shared
across cases), pointed at `run_hook(root, home, ...)`'s `env["HOME"]`. This prevents any real
`$HOME/.harness/expertise/harness-qa.md` on this machine from leaking into cases 3/4/5/6's
empty/absent assertions. Cheap, reversible, recorded here per the dispatch's instruction — not
an intent reword.

## STEP 3 — RED proof (script under test = scratch copy pinned at b4659cd)

Ran `test-inject-expertise.py` with `INJECT_EXPERTISE_BIN` pointed at
`<scratchpad>/inject-expertise-b4659cd.sh` (chmod +x'd copy of `git show b4659cd:...`, never
reverted in place).

**Observed FAIL set: cases 1, 2, 3, 7a, 10, 11 — six cases, not the caller's expected four
(1, 7, 10, 12).**

- **case1** (`checks=[F,F,F,F,F,F,True]`, `precedence_idx=-1 repo_header_idx=-1`): pre-change
  hook has no repository block and no precedence line; the sole True is "does not contain
  'most specific'" (never claimed either way).
- **case2** (`[F,F,F,F,F,F]`): no repository-tier support at all pre-change, so both segment
  headers/bodies and the precedence line are absent. **Not in the caller's named set** —
  it's an additional, expected discriminator (repository tier didn't exist).
- **case3** (`[True, False, True]`): exit 0 and "repository" absent both hold, but the
  **project header text itself changed** — old text is `this codebase (project tier,
  authoritative on conflict)`, the case asserts the new `this checkout's craft (project
  tier)`. **Also not in the caller's named set**, and a genuine discriminator: the header
  wording change (1a) is caught here independent of the repository-tier feature.
- **case7a**: pre-change has no repository tier, so no `[TRUNCATED at 40 lines` notice is
  emitted for a 41-line repository file — 40-line budget doesn't exist yet.
- **case10** (`[True, False, False, False, True]`): repository-only fixture; old hook doesn't
  read the repository directory at all, so exit 0 holds and "no project header" holds
  (nothing was written there), but repo header/body/precedence are all absent.
- **case11** (`checks=[True, False, True, False, False, True]`, `stderr=''`): exit 0 and no
  traceback hold (old hook never touched YAML either), but project header (old wording), repo
  body, and precedence line are absent — the assertion catches the same wording/feature gaps
  as cases 1/3/10, just under an added-noise fixture.

**case12 passes against the pre-change hook, but by accident, per sub-value** (matches the
caller's flagged risk):
  - `harness-` — matches old glob pattern `harness-*` (zero-length suffix allowed), reaches
    path `.../harness-.md`, which doesn't exist → unreadable → empty stdout by absence of file,
    not by name rejection.
  - `harness-qa/../../etc` — matches `harness-*`, interpolates into
    `.../harness-qa/../../etc.md`, no such file → empty stdout by absence.
  - `harness-*` — matches `harness-*` as a literal string against the glob pattern (the `*` in
    the *value* isn't shell-expanded inside `[ -r ]`), path is literally `harness-*.md`, doesn't
    exist → empty stdout by absence.
  - `harness-qa;id` — matches `harness-*`, path `harness-qa;id.md`, doesn't exist → empty
    stdout by absence.
  None of the four is rejected by validation pre-change; all four are silent misses because the
  interpolated filename happens not to exist. This is a weak discriminator by design of the old
  script, exactly as flagged — the new script rejects all four by the regex anchor before any
  path is built, which case12 also exercises (18/18 PASS post-edit).

No traceback on stderr in any RED-set case; `stderr=''` where captured.

## STEP 4 — verify

The dispatch's quoted verify was byte-`diff`'d against `plan.yaml`'s T-02 `verify:` (loaded via
`yaml.safe_load`, written to a scratch file) before running — `diff` exit 0, identical. Then run
**unmodified**, once, via `bash <script-file>` (not re-typed inline):

- **Exit status: 0**
- **Final line: `PASS test-inject-expertise.py`**

`git status --porcelain` re-run and diffed against STEP 1 snapshot: **exactly my three files**
— `inject-expertise.sh` (M), `run-unit-tests.sh` (M), `test-inject-expertise.py` (??) — added.
Nothing else changed; no tidy/revert performed on the pre-existing FEAT-26/FEAT-27 dirt noted
in STEP 1.

## Full-suite sanity (script-level PASS/FAIL lines only, `grep -c '^PASS test-'`)

`run-unit-tests.sh --kind unit` → exit 0, **17/17** script-level PASS (16 pre-existing +
`test-inject-expertise.py`), 0 `^FAIL `. `--kind integration` → exit 0, **12/12** script-level
PASS, 0 `^FAIL `. Drift detector did not fire (exit 2 not observed on either run) —
`test-inject-expertise.py` is registered in `UNIT_SCRIPTS` in the same change as its creation,
per PART 3.
