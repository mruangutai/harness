# QA gate re-run at merge pin `eb7e751355541ed601a400d5fd17391a55511552`

**BLUF: PASS.** Every measurement is green. One handed-down number ("61 scripts reporting PASS")
is false — the real count is 55 (28 unit + 27 integration) — but it is a reporting error upstream,
not a defect in the shipped diff, and does not change the verdict.

## Matrix (step 1)
Shipping diff `24af8d4..eb7e751` is the full FEAT-38 branch content (24af8d4 is `main` post-FEAT-43,
which never contained FEAT-38). Change types present: `logic`/`cross_module` (new
`check-decision-anchors.py` + its test `test-check-decision-anchors.py`, both landing together —
satisfies test-first pairing per P-05; changes to `gen-decisions-index.py`, `check-domain.sh`,
`check-state.sh`, `gh-sync.py`, `harness_yaml.py`, `plan-merge.py`, `board_lifecycle.py`,
`factory_decompose.py`, `check-plan-routes.py`, `upgrade-config.py`, `validate-digest.py`,
`run-unit-tests.sh`), `config` (`harness.json`, `fleet.yaml`, `.gitignore`, `tests.yml` — matrix
requires nothing), `docs` (SPEC/BUILD/DECISIONS/SKILL files — matrix requires nothing). No `api`,
`frontend`, `bugfix`, or `ai_behavior` change type present. Required floor: **unit + integration**
only (both `active`, non-null cmd). Added no kind beyond the floor — nothing in the diff warrants one.
`matrix_ok: true`, `must_fix: []`.

## Full suite (step 2)
`bash .claude/skills/harness/bin/run-unit-tests.sh > /tmp/feat38-suite.log 2>&1; echo EXIT=$?`
→ **EXIT=0**, captured immediately, not piped. Python count over the file: **0 lines begin `FAIL `**.

## `--check-kinds` (step 3)
`EXIT=0`; stdout: `check-kinds: the script arrays and test_kinds.integration.detect agree.`

## Discovery (step 4)
Runner echoes exactly one `PASS <script>` per array entry (`run-unit-tests.sh:152`). Restricting the
Python scan to lines matching `^PASS (test-\S+\.py)$` where the name is a member of `UNIT_SCRIPTS` ∪
`INTEGRATION_SCRIPTS`: **55 distinct scripts PASS-reported** (28 unit + 27 integration, no overlap,
none missing). A separate `--kind integration` run independently reproduces **27 distinct
integration PASS**, 0 FAIL — matches `INTEGRATION_SCRIPTS`.

**28-vs-27 reconciliation, verified:** `test_kinds.integration.detect` = 28 entries = 27 concrete
file paths + the `tests/integration/**` glob; `tests/integration/` does **not** exist in the tree at
`eb7e751` (`os.path.exists` false, `glob.glob('tests/integration/**', recursive=True)` → `[]`), so
the glob contributes 0 executed scripts. `INTEGRATION_SCRIPTS` correctly carries only the 27 concrete
files. This matches the expected reconciliation exactly.

**55-vs-61 arithmetic, resolved — the "61" claim is FALSE.** Raw unrestricted grep-style matching of
`^PASS \S+\.py$` over the log yields 60 lines / 56 distinct tokens, not 61, and even that count is
inflated by two artifacts unrelated to the real per-script tally: (a) four scripts —
`test-feature-worktree.py`, `test-expertise-merge.py`, `test-plan-merge.py`,
`test-observations-merge.py` — each print their own internal summary line
(`print("PASS " + scriptname)` at end of `main()`) in a format byte-identical to the runner's own
echo, so each contributes one extra duplicate line beyond the runner's one true PASS; (b) one
internal sub-case name inside another script's own output (`case_floor_inflight_registry.py`)
happens to end in `.py` and coincidentally matches the pattern. Neither artifact is a real
additional passing script. The correct, reconciled total is **55 = 28 + 27**, matching the array
sizes exactly. Nobody's arithmetic reaches 61 under any accounting scheme checked; that figure did
not survive re-measurement.

## Per-entry file existence (step 5)
Checked in Python (`os.path.exists`, worktree-absolute), all three arrays at the pin:
- `test_kinds.integration.detect`: 28 entries (1 glob: `tests/integration/**`, matches 0 paths as
  above), 27 concrete paths — **0 missing**.
- `UNIT_SCRIPTS`: 28 entries — **0 missing**.
- `INTEGRATION_SCRIPTS`: 27 entries — **0 missing**.
No resurrection of `test-context-watch-cli.py` / `test-context-watch-hook.py` or any other absent
file.

## Union proof (step 6)
Computed entry sets via `git show <sha>:<path>` in Python (never grep/diff-read) at base `79e2639`,
ours `8809c4b`, theirs `24af8d4`, pin `eb7e751`, for all three arrays:

|array|base|ours|theirs|pin|matches handed-down table?|
|---|---|---|---|---|---|
|`integration.detect`|26|27|27|28|yes|
|`UNIT_SCRIPTS`|26|26|28|28|yes|
|`INTEGRATION_SCRIPTS`|25|26|26|27|yes|

For every array: `pin == ours ∪ theirs` exactly (no extra, no missing member), `pin - base` = only
the two genuinely-new files (`test-code-grade.py`/`test-gate-policy.py` for unit;
`test-check-decision-anchors.py`/`test-code-grade-cli.py` for integration and detect), and
`base - pin`, `ours - pin`, `theirs - pin` are all **empty for every array**. Zero removals on either
side, confirmed — the pure-union claim holds exactly as stated.

## Fold survival (step 7)
- `DECISIONS.md` at pin: **6305 lines**, **188** `## DEC-` headings, **0** lines beginning
  `**Amendment` — all three counted in Python over `git show eb7e751:...`. Matches the claimed
  6305/188/zero exactly.
- `git diff 37676244..eb7e751 -- .harness/harness/docs/DECISIONS.md` → **empty**.
- `git diff 37676244..eb7e751 -- .harness/harness/docs/DECISIONS-INDEX.md` → **empty**.
Fold from the prior gate survived the merge byte-for-byte.

## Handed-down claims found FALSE
- **"61 scripts reporting PASS"** — false. Measured: 55 distinct scripts PASS-reported by the
  runner (28 + 27, zero overlap), with the discrepancy traced to duplicate self-summary lines in
  four test scripts plus one coincidental substring match, none of which represent additional real
  passing scripts. Everything else in the handed-down contract (the three array-size cells, zero
  removals, exit codes, FAIL count, `--check-kinds`, DECISIONS.md counts, both empty diffs) held
  exactly as claimed.
