# Receipt — harness-backend-dev — BUG-1308 cycle 2 (VL-05/SEC-01/F1)

## BLUF
FIXED. `_reject_multiline` now refuses any `entry`/`target` for which
`len(value.splitlines()) > 1` — the parser's own definition of "a line" — instead of a hand-copied
`\n`/`\r` check. Both panel exploits (U+2028 cap bypass, VT cross-section reclassification) now
exit `12 MALFORMED OPS` instead of silently corrupting the file. Both regression suites (u17/u18,
case21/case22) widened to the full `str.splitlines()` alphabet, proven RED pre-fix and GREEN
post-fix. Both suites at the pin still exit 0, zero `^FAIL `. `expertise-merge.py` stays pure
addition against `origin/main` (0 removed lines). One item is blocked on a domain grant: SPEC.md
§5.3's exit-12 row needs a citation correction I cannot write myself (see Open below).

## Mechanism (1 sentence, per acceptance #2)
The gate is now `len(value.splitlines()) > 1` — literally `parse_expertise`'s own line-counting
primitive — so any future change to which characters Python's `splitlines()` treats as a boundary
changes both sides of the check simultaneously; there is no second, hand-maintained alphabet left
to fall out of sync.

## Step 1 — the code change (`.claude/skills/harness/bin/expertise-merge.py`)
`_reject_multiline` (now :170-188) keeps the original `"\n" in value or "\r" in value` line
untouched (REQ-07 forbids deleting it) and adds a second, broader check immediately after:
```
if len(value.splitlines()) > 1:
    _malformed(index, f"{field} must be a single line")
```
The first check is now a strict subset of the second and never fires independently; the docstring
gained an additive paragraph (before the closing `"""`, no line removed) explaining why. Applied
to `entry` (via `_validate_entry_shape`) and `target` (via `_validate_target_section`), both
unchanged call sites — only `_reject_multiline`'s body changed.

**Empty-string edge case** (`entry=""`): `"".splitlines() == []`, length 0, not `> 1` — not
refused, identical to pre-fix behavior (`"" ` contains no `\n`/`\r` either). Verified live:
`resolve_ops` on `entry=""` still returns `('REPLACED', 'G-01')`, matching every green test's
expectation for `target`/`section` falsy values, which `_validate_target_section` already refuses
earlier via `if not target` / `if not section` — those paths never reach `_reject_multiline`.

**`section` — not wired through `_reject_multiline`, and evidence that it doesn't need to be**:
`_validate_target_section` refuses `section not in CAPS` before any multiline concern could
matter, and every `CAPS` key (`Patterns`, `Gotchas`, `Outcomes`, `Open`) is a single ASCII word
with zero line-breaking characters. Proved by attempting the exploit directly:
```
section = "Gotchas\x0b## Patterns (max 15)"
-> MergeRefusal(12, ["MALFORMED OPS op index=0: section 'Gotchas\\x0b## Patterns (max 15)' is not
    one of Patterns, Gotchas, Outcomes, Open"])
```
Refused, but via the membership gate, not `_reject_multiline` — adding a redundant multiline check
on `section` would be dead code covering an already-unreachable state, so I did not add one.

## Acceptance #1 — both panel exploits, before and after
Loaded the file at pinned HEAD `085c6455` via `git show HEAD:<path>` into `/tmp/bug1308_prefix/`
(untracked scratch, outside the repo) and executed `resolve_ops`/`render`/`parse_expertise`
in-process, then re-ran the identical calls against the fixed module in the worktree.

**P1 — U+2028 cap bypass** (Gotchas at cap, 15 entries):
- Pre-fix: `resolve_ops` → `[('REPLACED', 'G-08')]` (exit 0 equivalent), in-memory count stays 15
  (cap check passes on the pre-render list). Re-parsing the RENDERED text with the tool's own
  `parse_expertise` → **16** Gotchas entries (phantom `G-16`).
- Post-fix: `resolve_ops` → `MergeRefusal(12, ["MALFORMED OPS op index=0: entry must be a single
  line"])`.

**Escalated — VT cross-section reclassification** (Patterns 14/15, Gotchas at cap 15; my fixture
targets `P-08` rather than the panel's `P-07`, so my observed split differs numerically from the
panel's 7/23 while demonstrating the identical mechanism):
- Pre-fix: `resolve_ops` → `[('REPLACED', 'P-08')]` (exit 0 equivalent), in-memory Patterns=14 /
  Gotchas=15 (cap check passes). Re-parsing the rendered text → Patterns collapses to **8**,
  Gotchas grows to **22** (forged G-16 plus the reclassified P-09..P-14 tail).
- Post-fix: `resolve_ops` → `MergeRefusal(12, ["MALFORMED OPS op index=0: entry must be a single
  line"])`.

## Step 2 — widened regression cases
`LINE_BREAKING_CHARS` added to both test files, derived programmatically (probes `chr(0x00..0x9F)`
plus `\u2028`/`\u2029` through `len(("a"+c+"b").splitlines()) > 1`) rather than hardcoded — it
resolved to exactly `\n \v \f \r \x1c \x1d \x1e \x85 \u2028 \u2029` (10 chars) on this Python.

- `tests/unit/test-expertise-ops.py` `case_u17`/`case_u18` (:286/:298): loop widened from
  `("\n","\r")` to `LINE_BREAKING_CHARS`.
- `tests/integration/test-expertise-merge.py` `case_ops_entry_injection`/`case_ops_target_injection`
  (case21/case22): loops widened the same way, extracted into `_case21_full_alphabet` /
  `_case22_full_alphabet` helpers (grade discipline, see below); added `_case21_cap_bypass` and
  `_case21_cross_section` exercising the panel's exact two escalated exploits, each asserting the
  **re-parsed** file via the tool's own `expertise_merge.parse_expertise` (imported by file path,
  same pattern the unit suite already uses), not exit code alone — `case21` also gained a re-parse
  assertion (`Patterns` count stays 1) for the same reason. **Correction I caught myself**: the
  original `forged` payload for case21 embedded a literal `\n` unconditionally
  (`"## Gotchas (max 15)\n- G-16: ..."`), which meant every loop iteration was refused by the OLD
  `\n`-only check regardless of which separator prefixed it — a self-defeating fixture that could
  never redden pre-fix for any separator but `\n`/`\r`. Removed the embedded `\n` from `forged` so
  each separator is tested in isolation; re-verified RED below reflects the corrected fixture.

**RED proof** (pre-fix module swapped in via `EXPERTISE_MERGE_BIN=/tmp/bug1308_prefix/expertise-merge.py`,
restored by construction — the env var never touches the tracked file):
- `tests/unit/test-expertise-ops.py`: 18 checks FAIL (u17/u18, 8 non-`\n`/`\r` separators × ~2
  checks each), exit 1. Same run against the fixed module: 0 FAIL, exit 0.
- `tests/integration/test-expertise-merge.py`: 59 checks FAIL (case21 full alphabet + cap-bypass +
  cross-section, case22 full alphabet + re-parse), exit 1. Same run against the fixed module: 0
  FAIL, exit 0, 198 PASS.

## Acceptance #4 — code-grade before/after (bar: grade 3, test files)
`--base/--head` mode grades committed `HEAD` content, not the uncommitted working tree, on this
version of the tool — so before/after numbers below come from direct-path invocations
(`code-grade.py <path>`), cross-checked against `git stash`-reverted disk content:

| Function | Before (cyc/cog/abc/grade) | After (cyc/cog/abc/grade) |
|---|---|---|
| `case_u17` | 2/1/5.1/**5** | 2/1/5.7/**5** |
| `case_u18` | 2/1/5.1/**5** | 2/1/5.7/**5** |
| `case_ops_entry_injection` | 3/3/24.4/**3** | 2/0/14.0/**4** |
| `case_ops_target_injection` | 2/3/23.0/**3** | 1/0/14.9/**4** |
| `_case21_full_alphabet` (new) | n/a | 2/1/14.0/**4** |
| `_case21_cap_bypass` (new) | n/a | 2/0/15.1/**4** |
| `_case21_cross_section` (new) | n/a | 3/0/18.3/**4** |
| `_case22_full_alphabet` (new) | n/a | 2/1/14.5/**4** |

All at or above bar. `case_ops_target_injection` needed the same loop-extraction treatment as
case21 (`_case22_full_alphabet`) — its first draft, with the widened loop left inline, graded 2
(ABC 28.4) and would have failed review; caught it myself before returning.

## Acceptance #5 — REQ-07
```
$ git diff origin/main -- .claude/skills/harness/bin/expertise-merge.py | grep -c '^-[^-]'
0
```
`git diff HEAD -- .claude/skills/harness/bin/expertise-merge.py` shows exactly one hunk,
`@@ -174,9 +174,18 @@ def _reject_multiline(...)`. `apply`, `compute_union`, and `cmd_apply` sit at
lines 442-532, 114-140, and 533-582 respectively — nowhere near the touched range — confirmed
untouched by that single hunk boundary, not by re-reading their bodies.

## Acceptance #6 — both suites, from the worktree root
```
$ .agents/skills/harness/bin/run-unit-tests.sh --kind unit
pool: 8 workers, 28 files, 2.12s wall
exit 0, ^FAIL  count: 0
$ .agents/skills/harness/bin/run-unit-tests.sh --kind integration
pool: 8 workers, 46 files, 62.30s wall
exit 0, ^FAIL  count: 0
```
28/46 discovered files match the pin exactly — no discovery regression. (No separate
`run-integration-tests.sh` exists; `run-unit-tests.sh --kind integration` is the actual runner, per
the bin directory listing.)

## Acceptance #7 — git state
```
$ git status --porcelain
 M .claude/skills/harness/bin/expertise-merge.py
 M tests/integration/test-expertise-merge.py
 M tests/unit/test-expertise-ops.py
```
All three are mine; no sibling notes/observations files were dirty at the moment of this check
(earlier panel write-ups mention concurrent siblings' files — none appeared in this snapshot).
`git rev-parse HEAD` → `085c6455811a27ef461bc51c0a8962c329d5c477`, unchanged from the pin. No
commit made.

## Out of scope, explicitly not touched
F2 (falsy-key message misattribution), F3 (render's header fallback), SEC-02 (unanchored
destination suffix match), SEC-03 (no invalid-JSON-syntax case), `apply`/`compute_union`/`cmd_apply`,
`harness_merge.py`.

## Open — blocking
1. **SPEC.md §5.3 exit-12 row (Step 3 outcome)**: the row's PROSE ("gives an `entry` or `target`
   that is not a single-line string" → exit 12) is **already accurate** under the new definition —
   no prose change needed, this is a real empty-result outcome. However, my fix shifted every line
   number in `expertise-merge.py` from :170 onward by +9 (inserted lines inside
   `_reject_multiline`), which makes the row's own two citations stale: `:153-225` should read
   `:153-234` (`_parse_op`'s new end line), and `:378-381` should read `:387-390` (the
   "payload is not a list" `MergeRefusal` block's new location). I hold no write grant on
   `.harness/harness/docs/SPEC.md` (`check-domain` refused it) — routing this to whichever
   persona owns that file. Note: the same +9 shift also makes the *neighboring* rows' citations
   (`:157-167`, `:244-253`, `:233-241`, `:280-291`) stale, but those rows are outside my declared
   scope ("the exit-12 row" only) — flagging, not fixing.

## Files touched
- `.claude/skills/harness/bin/expertise-merge.py`
- `tests/unit/test-expertise-ops.py`
- `tests/integration/test-expertise-merge.py`
