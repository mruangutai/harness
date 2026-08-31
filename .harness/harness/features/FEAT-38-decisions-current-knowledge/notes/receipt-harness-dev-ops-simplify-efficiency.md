## BLUF

No efficiency findings. Every code-surface object named in the dispatch was measured; each
change in this feature either removes work (net efficiency gain, not a cost) or is a
comment/prose-only edit with zero runtime effect. `findings: []`.

## What I measured

- **`run-unit-tests.sh`** — T-24 removed exactly one entry (`test-check-decision-claims.py`)
  from `INTEGRATION_SCRIPTS` (line 31). Read the full kind-selection path (lines 33-53):
  `--kind` selects a plain array slice or concatenation, no duplication, nothing runs twice.
  The drift detector still runs over the union (by design, per its own comment) and the
  kind cross-check still runs on every invocation (by design). Removing one array entry is
  strictly fewer bytes forked, never more — a probable few-hundred-ms *reduction* against the
  orchestrator's 168.96s baseline, not measured in isolation (would require a full-suite run,
  which is out of scope for this angle per dispatch).

- **`.github/workflows/tests.yml`** — `git diff --stat` against the range: 4 lines changed,
  2 comment-only DEC-number corrections (`DEC-171 am.1` → `DEC-171`, `DEC-192` → `DEC-203`).
  No step added, removed, or reordered. No re-run of a suite or a hook-enforced check.

- **`.harness/harness.json`** — `git diff --stat`: 2 lines changed, both the `integration.detect`
  glob string with the deleted test's literal path removed (T-25's counterpart to T-24). A
  detect-glob shrinking by one entry is not a cost.

- **`board_lifecycle.py` / `check-domain.sh` / `check-state.sh`** — all diffs in range are
  docstring/comment DEC-renumbering only (`DEC-186`→`DEC-203`, `DEC-192`→`DEC-203`, `DEC-171
  am.1`→`DEC-171`). Verified via `git diff --stat` (2, 10, and 2 lines respectively) and full
  `git diff` read — no executable line touched in any of the three. `check-domain.sh` (a
  per-write hook, per the dispatch's own flag for extra scrutiny) has exactly one comment-only
  line changed; no code path added to its hot path.

- **`gen-decisions-index.py`** (`defenced_lines`/`parse_decisions`): read the call graph —
  `main()` reads `DECISIONS.md` once (line 273), calls `build_index` once (line 296), which
  calls `parse_decisions` once (line 172), which calls `defenced_lines` once (line 111). One
  linear pass over the file's lines, no repeated I/O, no repeated full-text walk. Measured
  directly on the real `DECISIONS.md` (6272 lines, `wc -l`):
  `time python3 .agents/skills/harness/bin/gen-decisions-index.py --stdout > /dev/null` →
  **0.044s real** (0.026s user, 0.023s sys). A second run via `subprocess` timing inside
  Python measured **0.032s elapsed**, rc 0, 41884 bytes of output. Not a hot path, not
  measurable waste at this file size. The unconsumed `lines`/`title` values the lead's
  pre-read flagged (SIMPLIFICATION/REUSE territory, not mine) cost nothing extra at runtime —
  they're already-computed values being discarded, not recomputed.

## Deliberate boundary runs — not flagged

None of the objects in scope added a new full-suite invocation at a boundary step; the one
suite-shape change (T-24's array-entry removal) is a reduction, so there is no boundary-run
finding to make either way.

## Commands run (read-only, no write path exercised)

```
wc -l .harness/harness/docs/DECISIONS.md          # 6272
time python3 .agents/skills/harness/bin/gen-decisions-index.py --stdout > /dev/null
git diff --stat <range> -- .github/workflows/tests.yml .harness/harness.json
git diff --stat <range> -- .claude/skills/harness/bin/check-state.sh .claude/skills/harness/bin/check-domain.sh
git diff <range> -- .claude/skills/harness/bin/board_lifecycle.py .claude/skills/harness/bin/check-domain.sh .github/workflows/tests.yml .harness/harness.json .claude/skills/harness/bin/check-state.sh
```

No source file edited, no generator write path run, no full unit suite run.
