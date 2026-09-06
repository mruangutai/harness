# QA review — BUG-1308, cycle 3 — VL-05 exploit reproduction at the pin

Pin graded: `5942e34e82cf84fd127ff496fdb64202ad647ba6`. Confirmed via
`diff <(git show <sha>:.claude/skills/harness/bin/expertise-merge.py) <worktree copy>` → `IDENTICAL`
(the pin only touched `SPEC.md`/feature bookkeeping, never the merge tool, so the working-tree file
IS the pinned file). All commands below invoke that exact file directly by absolute path — no copy
of it was ever made (bash-write-guard denies `cp` of it regardless of destination; the pinned tool
is read-only for me, only my throwaway `/tmp/qa1308wd/` fixtures and ops-JSON files are mine).

## Headline

**All five prior vulnerabilities (VL-01..VL-05) are CLOSED at the pin, reproduced by execution, not
by reading the fix.** One **new, must_fix** defect (**VL-06**) found under Step 3's target-shape
probe: `add`'s `target` has no ID-grammar validation, so a malformed target either **silently
vanishes** on re-parse (false `ADDED`/exit 0) or **aliases into a different id**, corrupting the
corpus without any refusal. It is not a re-emergence of VL-05's line-alphabet class and does not
survive as a cap bypass — but it is a genuine silent-corruption gap in code this feature introduces
outright (`add` is the new verb). Both suites are green at baseline counts (28 unit files / 46
integration files, 0 FAIL each).

## VL-01..VL-05 — closed, by execution

| # | Exploit | Command | Result |
|---|---|---|---|
| VL-01 | `\n` in `entry` | `replace` P-01 entry=`"line1\nline2"` | exit **12** `MALFORMED OPS...entry must be a single line` |
| VL-02 | non-string `target` | `drop` target=`123` (int) | exit **12** `target must be a string, not int` |
| VL-03 | duplicated base id | `replace` P-01 on a base with two P-01 rows | exit **11** `AMBIGUOUS TARGET...id appears 2 times` |
| VL-04 | (test-quality finding, not runtime) | — | not re-probed; unaffected by this pin's diff (doc-only) |
| VL-05(a) cap bypass | U+2028 in `replace` entry, at-cap (15) `Patterns` | `replace` P-01 entry=`"forged text\u2028- P-16: injected..."` | exit **12**, sha before==after (`6f1846f6...`), file untouched |
| VL-05(b) cross-section | `\x0b` forged `## Gotchas` header | `replace` P-01 entry=`"forged\x0b## Gotchas (max 15)\x0b- G-16: ..."` | exit **12**, sha before==after, file untouched |

For both VL-05 exploits the write never happened (sha unchanged), so the **re-parsed** counts are
trivially the pre-run baseline: `{'Patterns': 15, 'Gotchas': 3}` — no header injection, no
reclassification. This is the check cycle 1 skipped (exit-code-only); confirmed here by sha diff +
re-parse, not exit code alone.

The project's own integration suite proves the identical two exploits, at the pin, with the exact
re-parse assertions (`tests/integration/test-expertise-merge.py:1065-1102`, `_case21_cap_bypass` /
`_case21_cross_section`) — both PASS in the suite run below (`case21: (cap bypass)`, `case21:
(cross-section)` lines).

## Step 2 — attacking `len(value.splitlines()) > 1` on its own terms

| input | `splitlines()` | tool result | reparsed effect |
|---|---|---|---|
| `entry=""` | `[]` (0) | exit 0, `ADDED G-04` | text round-trips as `''` — correct, it was empty |
| `entry="\u2028"` | `['']` (1) | exit 0, `ADDED G-04` | **entry text silently becomes `''`** — the char is lost on re-parse (see below) |
| `entry="\x0b"` | `['']` (1) | exit 0, `ADDED G-04` | same silent loss |
| `entry="text\u2028"` | `['text']` (1) | exit 0, `ADDED G-04` | reparsed text truncates to `'text'` — trailing char lost |
| `entry="text\x0b"` | `['text']` (1) | exit 0, `ADDED G-04` | same truncation |
| `entry="\u2028text"` | `['', 'text']` (2) | exit **12** `entry must be a single line` | rejected, as designed |
| `target=""` | n/a | exit **12** `missing required key target` (falsy-string guard fires first) | n/a |

**Cap bypass?** No — reran the exact `_check_caps` boundary: an `add` whose forged `target` matches an
*existing* id shape into an *already-at-cap* `Patterns` (15/15) still correctly refuses at exit **8**
`CAP EXCEEDED ... union_size=16` (`_check_caps` operates on the in-memory resolved structure before
render, so a single ops batch cannot smuggle a phantom entry past the cap).
**Cross-section reclassification?** No — confirmed closed above.
**Entry silently lost/duplicated on re-parse?** **Yes, for entry text** (not entry count): a lone or
trailing line-boundary character passes the single-line check (`splitlines()` doesn't count a
trailing/solo boundary as 2 lines) but the file-level `parse_expertise` call still splits on it when
re-reading the *whole file*, silently truncating the entry's stored text. No new entry appears, no
cap moves, no cross-section leak — just quiet content loss for a boundary-char payload. Low severity
(nobody puts a U+2028 in an Expertise entry on purpose) — **advisory/enhancement**, not a ship gate:
the docstring's own claim ("cannot diverge by construction") is about *line-count* parity with
`parse_expertise`, which holds; it never claimed *byte-for-byte round-trip fidelity* of the value.

**Can `render`/`_check_caps` still be reached with a count the validator didn't compute?** Constructed
the attempt (Step 3, below) rather than reasoned about it: **yes**, via `target`'s missing ID-grammar
check, not via the newline boundary — see VL-06.

## Step 3 — `target` shape probe → **VL-06 (new, must_fix)**

`add` into `Gotchas` (base: 3 entries, cap 15, room to spare):

| `target` | tool result | reparsed `Gotchas` | what happened |
|---|---|---|---|
| `"not an id"` | exit 0, `ADDED not an id` | **3** (was 3, entry never added) | rendered line `- not an id: x` never matches `ENTRY_RE` (`^- ([A-Za-z]{1,3}-\d+): (.*)$`) — **the entry vanishes on the very next parse. The tool reports success on data it just destroyed.** |
| `"\u2028"` (from Step 2's target case) | exit 0, `ADDED  ` (blank printed — the id itself is unprintable) | **3** (unchanged, entry invisible) | same silent-loss class, worse: even the *outcome line* is unreadable |
| `"P-07: forged"` | exit 0, `ADDED P-07: forged` | **4**, but re-parsed as `('P-07', 'forged: x')` | the target's embedded `": "` is swallowed by `ENTRY_RE`'s own grammar — the entry lands under id **`P-07`** (colliding with the *existing* `Patterns/P-07`, a different section here so no direct clash today, but the *caller* believes they wrote `target="P-07: forged"` and instead planted an id + corrupted text nobody asked for) |

Root cause: `_validate_target_section` (`expertise-merge.py:191-203`) checks `target` is a non-empty,
single-line **string** — it never checks the value matches the same `ENTRY_RE` id-grammar
(`[A-Za-z]{1,3}-\d+`) that `parse_expertise` requires for the entry to be visible at all. For
`replace`/`drop` this can't happen (their target must equal an *existing* base id, which was already
grammar-constrained when the base file was parsed) — it is exclusively reachable through **`add`**,
the exact verb REQ-07 introduces in this feature. The tool's own Step-A docstring states the design
intent explicitly ("Refuse it here, at the single Step A shape gate, rather than at each of render's
write sites") — this is that same gate, just missing one grammar check it already has the regex for
(`ENTRY_RE` is a module constant). This is not VL-05's root cause (line-boundary alphabet) — it survives
regardless of that fix — and it does not defeat `_check_caps` (verified above: caps still fire
correctly), but it is a genuine silent-corruption / false-success defect in code this feature ships.
**Classified must_fix**: an `ops add` with a malformed target either destroys its own data invisibly
(reporting success) or plants a colliding, corrupted id — with no refusal path at all, unlike every
other malformed shape this tool defends against.

## Step 4 — u17/u18/case21/case22 alphabet audit

`LINE_BREAKING_CHARS` (`tests/unit/test-expertise-ops.py:33-36`, mirrored in
`tests/integration/test-expertise-merge.py:47-50`):
```python
LINE_BREAKING_CHARS = tuple(
    chr(c) for c in list(range(0x00, 0xA0)) + [0x2028, 0x2029]
    if len(("a" + chr(c) + "b").splitlines()) > 1
)
```
This **executes** `str.splitlines()` against every candidate and keeps only what the *live* Python
actually treats as a boundary — it is driven by the same definition the fix uses
(`len(value.splitlines()) > 1`), not a hand-copied literal list, which is precisely the property that
failed in cycle 1 (a fixed `\n`/`\r` pair silently fell behind the parser's real alphabet).
`u17`/`u18` (unit) and `case21`/`case22` (integration) iterate this derived tuple for `entry` and
`target` respectively; all 20 `u17`, 20 `u18`, 38 `case21`, 35 `case22` sub-assertions PASS at the pin
(verified in the suite run below, `grep -c` of the log — zero FAIL among them).

**What would still be missed if Python added a new boundary character**: only one outside the
*scanned* range `0x00-0x9F ∪ {0x2028, 0x2029}` — e.g. a hypothetical new separator at, say, `0x3000`.
The **test's parametrization** would silently stop enumerating it (the scan is range-bounded, since
there is no public API to enumerate the full alphabet without probing candidates). Critically, this
is **not a re-opening of VL-05**: the *production* check (`len(value.splitlines()) > 1` in
`_reject_multiline`) calls the real, unconditional `splitlines()` — it would still correctly reject the
new character; only this test's *proof of enumeration* would need a wider scan to keep demonstrating
it. Reported as an **informational observation**, not a defect: current behavior is correct; test
assurance is bounded to the known universe as of this Python.

## Step 5 — both suites

Run from worktree root, `env -u HARNESS_AGENT_TYPE` (Expertise G-07 — without it `test-plan-merge.py`
false-fails, unrelated to this diff).

- **unit**: `env -u HARNESS_AGENT_TYPE .agents/skills/harness/bin/run-unit-tests.sh --kind unit`
  → exit **0**, `^FAIL ` count **0**, **28 files** (`pool: 8 workers, 28 files, 3.66s wall`) — matches baseline.
- **integration**: no `run-integration-tests.sh` exists; used
  `run-unit-tests.sh --kind integration` per the fallback instruction
  → exit **0**, `^FAIL ` count **0**, **46 files** (`pool: 8 workers, 46 files, 86.98s wall`) — matches baseline.
- `test-expertise-ops.py` (unit): exit 0, 0.08s — includes u17 (20 sub-cases) and u18 (20 sub-cases), all PASS.
- `test-expertise-merge.py` (integration): exit 0, 10.51s — includes case21 (38 sub-checks) and case22
  (35 sub-checks), all PASS, plus case18 (SC-11, below).

## Step 6 — SC-11 (concurrency)

`case_concurrent_writers` / case18 (`tests/integration/test-expertise-merge.py:902-923`) exists at the
pin and matches BRIEF SC-11 verbatim: the test process itself calls `harness_merge.acquire(lock_path)`
— the same primitive `locked_update` uses — then spawns both a real `apply` child (add-only, P-09/P-10)
and a real `ops` child (`replace` P-07) via `subprocess.Popen`, polls both every 0.05s for a 2.0s hold
window, and asserts **neither exits** while the test holds the lock. No env var, no injected sleep, no
test-only flag, no edit to `expertise-merge.py`/`harness_merge.py` — genuine production-lock contention.

Observed in this run: `case18: neither child exits during the 2.0s hold window ... (2.00s observed)` —
**PASS**, plus all four follow-on assertions (both children exit 0 after release; final Patterns id
census = original 8 + P-09 + P-10; P-07 carries child B's marker text) — all **PASS**. Runtime:
`test-expertise-merge.py (exit 0, 10.51s)` total; case18's own hold window is the dominant 2.0s of that.

## `git status --porcelain`

```
 M .harness/harness/features/BUG-1308-expertise-replace-drop/observations/harness-pm.md
?? .harness/harness/features/BUG-1308-expertise-replace-drop/notes/research-BUG-1308-expertise-replace-drop-goalcheck-sc-c3.md
?? .harness/harness/features/BUG-1308-expertise-replace-drop/notes/review-harness-ui-reviewer-c3.md
```
None of these are mine — they are concurrent sibling reviewers'/pm's own artifact writes in this
shared worktree (`ResumeBug1308.WorriedBedbug.GoalcheckDeltaC3`, `ResumeBug1308.ValidSquid.ReviewUiC3`).
I made zero edits to any tracked file; every probe ran against throwaway copies/fixtures under
`/tmp/qa1308wd/` (outside the repo entirely), invoking the pinned tool directly by absolute path.

## Findings summary

| id | severity | disposition | evidence |
|---|---|---|---|
| VL-01..VL-05 | — | **CLOSED**, confirmed by execution | table above |
| VL-06: `add`'s `target` has no ENTRY_RE id-grammar check | high | **must_fix** | Step 3 table; silent data loss + false success, or id-collision corruption |
| entry with a lone/trailing line-boundary char loses that byte on round-trip | low | advisory (`bug`) | Step 2 table |
| `LINE_BREAKING_CHARS` test scan is range-bounded (0x00-0x9F + 2 pts) | informational | advisory (`chore`), no defect | Step 4 |
