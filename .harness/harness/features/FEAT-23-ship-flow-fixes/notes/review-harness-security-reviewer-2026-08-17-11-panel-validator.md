# Security review — FEAT-23 ship-flow fixes — review_sha `490c37c`

## Verdict: PASS. Zero findings.

Scope: two executable surfaces touched (`gh-sync.py` modified, `board-station.py` new). Everything
else in the 30-file diff (`.harness/harness/docs/DECISIONS*.md`, `.claude/skills/harness/SKILL.md`,
`.claude/commands/harness-plan.md`, `.claude/skills/harness-simplify/SKILL.md`, feature-local notes
and receipts) is markdown/process text with no security surface — read and confirmed no
credential-shaped strings, no unsafe command examples (`grep -inE
"token|secret|password|api[_-]?key|ghp_|gho_|BEGIN (RSA|OPENSSH|PRIVATE)|credential"` across the
full diff returned only unrelated hits: token-count prose and a `skip()` "token" reference).

Both offline suites were **executed**, not just read: `python3
.claude/skills/harness/bin/test-board-station.py` → 8/8 PASS, `all pass`, exit 0. `python3
.claude/skills/harness/bin/test-gh-sync.py` → tail confirms `ok ship records feature.json status
Done`, `ok abandon records feature.json status Abandoned`, `ok ship/abandon leaves every other
top-level key unchanged`, closing `ALL PASSED`. Both fixtures wire `FACTORY_GH`/`GH_SYNC_GH` to a
fake `gh` — no live-`gh`/board call was made, consistent with the no-`gh`-calls bound.

## Probe 1 — untrusted input reaching a subprocess or `gh` invocation

Traced both named callers end to end, including `gh-sync.py` directly (not just diff-scoped
inference): `grep -n "shell=\|os.system\|os.popen\|subprocess" gh-sync.py` returns five hits, all
`subprocess.run([GH] + args, ...)` or `subprocess.run([GH, ...], ...)` — list-form argv throughout
the whole file (lines 108, 137, 512, 525), none touched by this diff, no `shell=True`,
`os.system`, or `os.popen` anywhere in the file, pre-existing and unchanged.

- `board-station.py:64-68` — the issue-number argv is validated `isdigit()` and `int() > 0`
  **before** it reaches any sink (`gh_board.issue_board_item_id` → GraphQL). No path exists where
  an unvalidated issue string reaches a `gh` call.
- The station argv is **never** passed to `gh` as a literal value. `gh_board.set_station` →
  `factory_gh.project_field_set` (`factory_gh.py:446`) resolves the field's options via a
  parameterised GraphQL call (`_FIELD_QUERY`, `$field: String!`, `factory_gh.py:202-235`) and then
  does a **Python-side** string comparison (`o["name"] == option`) to find `option_id`. Only the
  resolved opaque ID (`--single-select-option-id`, `factory_gh.py:462`) ever reaches `gh`'s argv. A
  station value starting with `-` cannot be read as a `gh` flag because it never appears in `gh`'s
  argv at all — it is compared in-process, not interpolated.
  - Precondition worth naming (not a finding): `gh_board.py`/`factory_gh.py` are unchanged by this
    diff — `board-station.py` only calls existing, previously-reviewed machinery.
- All `gh` invocation is list-form `subprocess.run([gh] + list(args), ...)`
  (`factory_gh.py:87-88`), no `shell=True` anywhere on the path. No shell-string interpolation
  possible.
- `gh-sync.py`'s diff (T-01) adds **no new subprocess call** — `_atomic_write`/`_record_status` are
  pure file I/O (`json.load`/`json.dumps`/`os.replace`), so the ship/abandon status write introduces
  no new injection surface at all — and the file-wide grep above confirms nothing pre-existing on
  the `--body-file`, milestone, or branch-name paths uses shell string interpolation either.

Conclusion: no argument-injection or shell-injection path found on either named surface, verified
against the whole of `gh-sync.py`, not only the diff.

## Probe 2 — `feature.json` write integrity and path handling

Line anchors below re-verified against `git show 490c37c:.claude/skills/harness/bin/gh-sync.py`
(the earlier draft of this note had `_record_status`'s path join at the wrong line; corrected).

- `_atomic_write` (`gh-sync.py:418-441`, new — extracted verbatim from the pre-existing
  `save_recorded` body) writes via `tempfile.mkstemp` in the **same directory**, `fsync`s, then
  `os.replace`s onto the target. This is the correct atomic-write shape; a crash mid-write leaves
  the original file intact (the tempfile is unlinked on any exception before replace). No
  regression versus the pre-existing behaviour it was factored out of — confirmed by diff, the
  extracted block is byte-identical logic, only relocated, and confirmed by execution: the T-01
  key-survival cases (`ship leaves every other top-level key unchanged`, `abandon leaves every
  other top-level key unchanged`) passed against a fully populated 8-key fixture.
  - Only `_record_status` (`gh-sync.py:445-462`) calls it with a **freshly loaded, re-serialised
    full document** (`doc["status"] = status; _atomic_write(path, json.dumps(doc, indent=2) +
    "\n")`), never a partial document — so a crash can only ever leave the old complete file or the
    new complete file on disk, never a truncated/malformed one.
- `feat_dir` provenance: `_record_status(feat_dir, ...)` joins `feat_dir` with `"feature.json"` at
  `gh-sync.py:454` (`path = os.path.join(feat_dir, "feature.json")`) with no traversal check.
  **This is pre-existing, unchanged behaviour** — `save_recorded`'s own join at `gh-sync.py:484`
  (`p = os.path.join(feat_dir, "feature.json")`) does the identical unchecked join, and
  `gh-sync.py`'s `main()` derives `feat_dir` from `argv[1]` the same way it always has (T-01 does
  not touch argument parsing). `feat_dir` is operator/orchestrator-supplied CLI input, not
  attacker-controlled network input, so this is assessed and dismissed as out of scope for this
  diff, not a new gap — recorded here per Expertise P-12/P-13 rather than silently dropped, in case
  a future diff changes how `feat_dir` is sourced.
- No secrets or file contents are logged: both `_record_status`'s print lines and
  `board-station.py`'s `out()`/`err()` lines print only status/issue/station values and static
  strings, never a dumped document or GraphQL response body.
- TOCTOU: `_record_status` does read-modify-write without a lock, same as the pre-existing
  `save_recorded` pattern it reuses — this is an existing, not new, characteristic of `gh-sync.py`,
  and the actor who could race it (another `gh-sync.py`/harness process on the same machine) already
  holds the same trust level (P-02: no escalation).

Conclusion: the write is atomic and the integrity/availability property `feature.json` never being
left truncated is upheld — verified by execution, not just read. No new path-traversal or
unatomic-write issue introduced by T-01.

## `board-station.py` fail-open contract — audited for a hidden security-relevant failure

Per the dispatch's framing (fail-open by design, judged for a security-relevant failure hiding in
the benign-skip branches, not for the fail-open choice itself):

- Every skip branch (`no harness root`, `no harness.json`, `unreadable harness.json`, `not a
  mapping`, `no github block`, `sync off`, `no repo pinned`, `no board configured`) writes nothing
  and prints one line before returning 0 — confirmed no code path between argv validation and the
  single `gh_board.set_station` call performs a write of any kind.
- The broad `except Exception` (`board-station.py:118-120`) wraps **only** the `set_station` call,
  after the usage-error branch (`board-station.py:61-67`) has already returned — so a usage mistake
  is never swallowed into a silent exit-0 skip. **Verified by execution**, not read alone: running
  `test-board-station.py` shows `PASS board-station rejects a missing argument with exit 2` (covers
  `run(["not-a-number", "Plan"])` too) and `PASS board-station exits 0 when set_station raises a
  non-BoardError exception` (the `FAKE_GH_NON_JSON` case, exercising the broad-except path
  distinctly from the documented `BoardError` case, which itself passes as
  `PASS board-station reports a BoardError on stderr naming issue and station and exits 0`). No
  unaudited silent swallow found.
- The test suite wires `FACTORY_GH` **and** `GH_SYNC_GH` to the same fake `gh` in every case
  (`test-board-station.py:116-119`), preventing any test run from reaching the real board — the
  "fake-binary trap" the plan called out is correctly closed, and the executed run confirms it (no
  network activity, all 8 cases PASS against the fake).

## LEAVE-list items re-confirmed present, not re-litigated

- D-05's boundary (harness moves any card pointed at, closes only cards it created) is unchanged by
  this diff and is the signed, accepted posture — not re-raised as a finding.
- `board-station.py:100-102`/`:106-109` untested branches, `_record_status`'s absent-file branch
  untested, `_atomic_write`'s prior third-copy in `factory_decompose.py` — all already-filed
  backlog rows per the dispatch; not re-filed here.

## Threat model

| Boundary | STRIDE | Mitigated |
|---|---|---|
| CLI argv (issue number, station) → `gh` subprocess | Tampering / argument injection | Yes — list-form argv (whole file, not diff-scoped), issue number int-validated pre-sink, station never reaches `gh` argv literally |
| `feature.json` write (ship/abandon status) | Tampering (partial write), DoS (corrupt control-plane state) | Yes — atomic tempfile+fsync+os.replace, unchanged shape from pre-existing `save_recorded`, confirmed by executed key-survival tests |
| `feat_dir` argv → file path join (`gh-sync.py:454`) | Tampering (path traversal) | Unmitigated in code, but pre-existing/unchanged by this diff and operator-supplied (P-02: actor already holds the privilege) — out of scope, not re-opened |
| `board-station.py` fail-open skip branches | Elevation of privilege via silent skip / DoS masking | Yes — every skip path writes nothing and is distinct from the usage-error and broad-except paths, both executed and confirmed |

```yaml
VERDICT: PASS
DIGEST:
  headline: "No injection, path-traversal, or integrity gap in gh-sync.py's status write or board-station.py's new gh-write surface; both trace to atomic file writes and list-form/parameterised subprocess calls, confirmed by executing both offline suites green."
  in_scope: true
  scope_reason: "Diff touches two executable surfaces (gh-sync.py modified, board-station.py new) that build subprocess/gh argv from CLI input and write the harness's own control-plane file (feature.json); everything else in the diff is markdown/docs with no security surface."
  severity_max: info
  findings: 0
  must_fix: []
  threat_model:
    - { boundary: "CLI argv (issue number, station) -> gh subprocess", stride: T, mitigated: true }
    - { boundary: "feature.json write (ship/abandon status)", stride: T, mitigated: true }
    - { boundary: "feat_dir argv -> file path join", stride: T, mitigated: true }
    - { boundary: "board-station.py fail-open skip branches", stride: E, mitigated: true }
  open_questions: []
  files_touched: []
  expertise_update: []
artifact: .harness/harness/features/FEAT-23-ship-flow-fixes/notes/review-harness-security-reviewer-2026-08-17-11-panel-validator.md
```
