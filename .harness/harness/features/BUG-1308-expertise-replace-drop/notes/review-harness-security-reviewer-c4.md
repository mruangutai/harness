# Security review — BUG-1308 expertise-replace-drop — cycle 4 (DELTA, final)

Graded `b70d57b464743034231fed3d18227a17faae2ed4` via `git show <sha>:<path>` for
`expertise-merge.py`, `harness_merge.py`, `check-expertise.sh`, and both named test files.
Confirmed the delta under primary review, `5942e34e..b70d57b4`, touches only `expertise-merge.py`
(+16 lines: `_validate_target_grammar` + its one call site), `SPEC.md` (+16/-10 docs), and the two
named test files (+81/+28) — `harness_merge.py`/`check-expertise.sh` are byte-unchanged since c3.
All three bins were copied verbatim from the pin into `$TMPDIR` and diffed byte-identical against
`git show` before any reproduction ran; every probe below executed against that `$TMPDIR` copy,
never the worktree.

## Verdict: PASS — no must_fix. VL-01..VL-06 all CLOSED, reconfirmed by execution.

## VL-01..VL-06 reconfirmation

| VL | Repro | Result |
|---|---|---|
| VL-01 (entry newline) | full `splitlines()` alphabet (LF CR VT FF FS GS RS NEL LS PS) embedded in `entry` | every case: exit **12**, `"entry must be a single line"`, file sha256 unchanged. **CLOSED** |
| VL-02 (non-string target) | target ∈ {42, 0, 1.5, [1,2], [], {"a":1}, {}, True, False, None} | every case: clean `MergeRefusal(12)` (`"target must be a string, not <type>"`), **no TypeError**, file unchanged. **CLOSED** |
| VL-03 (dup-base add) | base `Patterns` carries `P-01` twice; `add`/`replace` target=`P-01` | both: exit **11** `AMBIGUOUS TARGET … appears 2 times`, file unchanged — never resolves to last occurrence. **CLOSED** |
| VL-05 (line alphabet parity) | same 10-char alphabet in `target` | every case: exit **12** `"target must be a single line"`, unchanged. **CLOSED** |
| VL-06 (grammar gate) | see below, exact acceptance-criteria repro | **CLOSED** |

**VL-06 exact repro (item 1):** seed file has `P-01`. `add target="PPPP-1"` → exit **12**
(`"does not match the entry id grammar"`), sha256 unchanged. `add target="P-01: fake prefix"` →
exit **12**, sha256 unchanged. `add target="P-02"` (well-formed) → exit **0**, `ADDED P-02`,
sha256 changes as expected; re-parse via the tool's own `parse_expertise` shows exactly
`[('P-01', 'seed pattern one.'), ('P-02', ...)]` — no `PPPP-1`, no `"P-01: fake prefix"`, no
duplicate `P-01`. Then `replace target="P-01"` → exit **0** `REPLACED P-01`, **not 11** — the
refused colon-prefix attempt planted nothing. Final file passes `check-expertise.sh` clean (`OK`).

## Adversarial grammar/ops-path probes (item 2/3) — exact input, exact outcome

| # | Probe | Result |
|---|---|---|
| whitespace/tab | `" P-09"`, `"P-09 "`, `"P- 09"`, `"\tP-09"`, `"P-09\t"`, `"P-\t09"` | all exit 12, grammar mismatch — no partial-match slips |
| homoglyph letter | Cyrillic `Р-01` (U+0420) | exit 12 — `[A-Za-z]` is a literal ASCII class, not unicode-expanded |
| **unicode decimal digits** | `P-٠١` (Arabic-Indic), `P-०१` (Devanagari) | **exit 0**, ADDED, distinct id from `P-01`, round-trips, `check-expertise.sh` OK |
| **fullwidth-digit homoglyph** | `P-０１` (U+FF10/11 — visually near-identical to `P-01`) | **exit 0**, ADDED as a DISTINCT id, `check-expertise.sh` reports **OK** — see F1 |
| entry body embeds `X-99: ...` | `entry="X-99: this looks like a second entry id"` | parses back as one entry, correct id, no phantom second entry — no issue |
| cross-section id collision | `P-01` exists only in `Gotchas`; `add target=P-01 section=Patterns` (Patterns empty) | exit 0, succeeds cleanly, scoped correctly — matches the already-accepted "no cross-section uniqueness gate" item, not re-raised |
| **oversized target** | `target = "P-" + "9"*10000` (10 KB id) | **exit 0**, ADDED, `check-expertise.sh` OK — see F2 |
| **oversized entry, no whitespace** | `entry = "A"*10000` (one "word") | **exit 0**, `check-expertise.sh`'s `WORD_CAP=50` never fires (counts words, not chars) — see F2 |
| control chars (non-line-breaking) | NUL, BEL, ESC(`\x1b`), DEL, ZWSP embedded in `entry` | all **exit 0**, byte present verbatim in rendered file — see F4 |
| `--file` dot-dot escape | `.harness/expertise/../../elsewhere_secret/x.md` | exit 9, refused, secret untouched |
| `--file` bad suffix | `....md.bak` | exit 9, refused |
| `--file` non-`harness-*` name | `not-a-harness-agent.md` | exit 9, refused |
| symlink **inside** tier → **outside** target | legal-looking path, real target outside `.harness/**` | exit 9, refused, real target file untouched |
| symlink **outside** tier → legal expertise file | resolves via realpath to a legal path | exit 0, writes the real (legal) file — **F5, assessed/dismissed**, documented pre-existing "WHO not WHERE" gap (issue #627) |
| `--ops` payload type confusion | JSON object, bare string, number, null (not a list) | all exit 12, `"payload is not a list"` |
| `--ops` deeply nested JSON | `"["*2_000_000 + "]"*2_000_000` | **uncaught `RecursionError`**, exit 1 — see F3 |

## Findings (advisory/backlog only — no must_fix)

- **F1 (low, bug):** `_validate_target_grammar`'s round-trip through `ENTRY_RE` inherits Python
  `\d`'s Unicode-decimal-digit awareness. Fullwidth digits (`P-０１`) are accepted as a id
  visually confusable with `P-01`, distinct to every parser but not to a human skimmer — a
  spoofing risk, not a cap/duplicate bypass. Recommend restricting the id's numeric position to
  ASCII `[0-9]`.
- **F2 (med, bug):** no character-length cap exists on `target`, and `check-expertise.sh`'s
  `WORD_CAP=50` counts words, not characters, so a single-token `entry` is uncapped too. Since
  this file is injected whole into every future spawn, an unbounded single line silently defeats
  DEC-145's size intent. Pre-existing in `check-expertise.sh` (untouched this delta); newly and
  more easily reachable through the machine-authored `ops` path this feature ships. No data loss,
  self-contained blast radius (the writing persona's own future context) — backlog, not gating.
- **F3 (med, bug):** `cmd_ops`'s `transform` catches only `json.JSONDecodeError`; sufficiently
  deep nested-array `--ops` JSON raises an uncaught `RecursionError`, exiting 1 instead of a
  documented `MergeRefusal` code. Confirmed no data loss (write only happens after `transform`
  returns) and no lock leak (flock releases in `_acquire_flock`'s `finally` on any exception).
  Recommend catching `RecursionError` alongside `JSONDecodeError`. Backlog.
- **F4 (low, bug, converges with c3):** c3 found unsanitized control-char echo on the `CONFLICT`
  stdout refusal path (rated low/advisory/backlog). I confirm the same underlying gap has a
  second, more persistent vector: these characters (incl. ESC, enabling ANSI injection) are
  written verbatim into the FILE on a successful add, not just echoed once on refusal — same
  severity, same backlog item, noting the added persistence for whoever fixes it.
- **F5 (info, assessed/dismissed):** symlink-outside-tier→legal-file write succeeds; this is
  exactly the documented, filed-separately (#627) "checks WHERE, never WHO" limitation both
  `require_expertise_destination` and `harness_merge.py`'s own docstrings state. Not new, not
  re-raised.

## Test suites (env -u HARNESS_AGENT_TYPE, from worktree root)
`run-unit-tests.sh --kind unit`: 0 `^FAIL ` lines (`test-expertise-ops.py` cases u1-u22 all PASS).
`run-unit-tests.sh --kind integration`: 0 `^FAIL ` lines (`test-expertise-merge.py` cases 1-26
incl. 25/26 target-grammar all PASS; case8 cap-agreement check also PASS).

## git status --porcelain (worktree root, this session)
```
 M .harness/harness/features/BUG-1308-expertise-replace-drop/observations/harness-pm.md
?? .harness/harness/features/BUG-1308-expertise-replace-drop/notes/research-BUG-1308-expertise-replace-drop-goalcheck-sc-c4.md
?? .harness/harness/features/BUG-1308-expertise-replace-drop/notes/review-harness-code-reviewer-c4.md
?? .harness/harness/features/BUG-1308-expertise-replace-drop/notes/review-harness-qa-c4.md
?? .harness/harness/features/BUG-1308-expertise-replace-drop/notes/review-harness-ui-reviewer-c4.md
```
All four are concurrent sibling reviewers' own artifacts (pm/code-reviewer/qa/ui-reviewer for c4),
not mine. I made zero edits inside the worktree; every reproduction ran under
`/tmp/harness-sec-c4/` against byte-verified copies of the pin.
