# Code review — FEAT-03-subissue-mirror — c0

Reviewed range: `4d00dbc..e68ba00` (all three build commits: `2897b09` T-01, `ae728e8` T-02..T-07,
`e68ba00` T-08). `git diff --stat e68ba00..HEAD -- .claude/skills/harness/bin
docs/harness/DECISIONS.md .harness/harness.json` is **empty** — no post-pin drift in the reviewed bin
surface. `git log --oneline e68ba00..HEAD` is **also empty** — no commits, human or otherwise, have
landed since the pin; `human_commits_in_scope: []` reflects that receipt, not an assumption. The three
` M` entries `git status --porcelain` shows (`STATE.md`, `feature.yaml`,
`.harness/logs/2026-07-31.md`) are **uncommitted working-tree edits**, not commits past the pin — they
sit on top of `e68ba00`, HEAD has not moved. `.../notes/qa-FEAT-03-c0.md` and
`.../notes/review-harness-security-reviewer-c0.md` are sibling agents' untracked artifacts, not mine.

Because `feature.yaml` is one of those dirty files, I re-ran my SC-10 discriminator against the
**pinned bytes**, not the working tree: `git show e68ba00:.../feature.yaml | grep -n -A5
'^github:'` → `github:` block at `:75-78`, still `parent: none` / `milestone: none` / `issues: {}`.
Matches what I'd read in the working tree — SC-10 holds at the pin. One citation-drift byproduct,
recorded as a finding below: DEC-138 am.7 (`docs/harness/DECISIONS.md:4350`) cites this block at
`feature.yaml:73`; at the parent commit `ae728e8` (where product squad's own digest verified `:73`)
that was correct, but `e68ba00`'s own commit appended a `runs:` entry to the same file, shifting the
block to `:75-78` in the very commit that lands the citation. Values unchanged, line number stale by
2 — a docs-accuracy nit, not an SC-10 violation.

`run-unit-tests.sh` re-run live, independent of the digests: **exit 0**, all three scripts PASS,
`ALL PASSED` from `test-gh-sync.py`. `check-docs.sh` exit 0, 45 patterns / 73 files. Every
discriminating grep in PLAN's verify blocks re-run directly against the working tree, not taken on
the digests' word (SC-06's four, D-01's regression guard, the `"gh"` literal, `amendment 7`) — all
match the expected post-task values.

## VERDICT: PASS

## Stage 1 — spec compliance

Every change traces to a task/`REQ`/`D`. Walked T-01 through T-08 against the diff line by line:

- **T-01** (`run-unit-tests.sh`, `harness.json`): streams child stdout/stderr unfiltered
  (`run-unit-tests.sh:26`, bare `python3 "$BIN_DIR/$s"`, no capture/tee/redirect), exit 2 for an
  unlisted `test-*.py` via the untouched glob drift-detector, exit 0/1 otherwise. `harness.json`
  diff is exactly the two specified keys, `exclude` byte-identical. Matches D-04/T-01 exactly.
- **T-02** (`gh_issues.py`, `wayfind.py`): five functions as specified, argv builders only. Carve-out
  verified by direct grep, not inspection alone: `grep -c 'sub_issues", "--paginate"' wayfind.py` = 1,
  `grep -c 'dependencies/blocked_by",$'` = 1 (was 2 pre-task — the retained list GET plus the now-moved
  write). `grep -c '"gh"' wayfind.py` = 0 — all three sites including `append_gist` (`:173`) convert.
  `:270`'s redundant `issue()` pre-attempt is untouched, matching the closed byte-identical carve-out.
- **T-03** (`gh-sync.py` `cmd_open`, `load_recorded`/`save_recorded`): parent adopted-or-created,
  `parent`/`parent_origin` written in the same `save_recorded` call every time (`gh-sync.py:262-278`),
  attach is a separate act-then-receipt step (`:296-300`, below). Regex forms match PLAN's pinned
  on-disk shapes byte-for-byte (`^\s{4}(T-\d+):\s*(\d+)` unaffected by the new `parent_origin:` line
  at 2-space indent).
- **T-04** (`close-task`): exactly one `issue close`, `absorbs:` prints and does not close
  (`gh-sync.py:310-314`). Both assertions inverted in place in `test-gh-sync.py`, not deleted.
- **T-05/T-06** (`abandon`/`ship`): `post_body_path` shared and used identically by both
  (`gh-sync.py:65-80`); origin-conditional parent close in all three cases (created/adopted/absent)
  for both subcommands, each proven against **both** close-call shapes in three fixtures per
  subcommand; milestone unconditional given a recorded milestone. `state_reason` enum is exactly
  `completed`(default)/`not_planned`, no `not_doing`. Neither writes `save_recorded` — confirmed by
  grep, not assumed — which is what keeps the absent-origin fixture's premise real.
- **T-07** (`check-state.sh` INV-21): warn-level, vacuous when `github.sync` is false (confirmed live:
  0 `INV-21` lines in this repo, exit code unaffected). Parent regex (`^\s*parent:\s*\d+`) cannot
  false-match `parent_origin:`, independently re-derived, not just trusted from the digest.
- **T-08** (`DECISIONS.md` amendment 7): lands at `:4299-4374`, states the table (created/adopted/
  absent × ship/abandon), the milestone-unconditional clause, the `gh_issues.py` extraction, and
  correctly declares **no** staleness marker for the two `SKILL.md` phrases — confirmed those phrases
  are still live (`SKILL.md:137`, `:144`) and `check-docs.sh` is still exit 0, matching the by-design
  gap the amendment names. (Citation drift at `:4350` noted above — low, not a spec violation.)

**No scope creep found.** The one item that could look like it — the three prose corrections
eng-lead authorized beyond the task specs' letter (`runs/2026-07-31-10-eng/digest.md` §"Three prose
corrections") — I assess as **completion, not scope creep**. All three are prose inside files already
in the correcting task's `files:` list (`test-gh-sync.py` for T-04's docstring, `gh-sync.py`'s module
docstring and `main()`'s usage string for T-05/T-06), describing behavior the same task changed, and
for T-05 the docstring edit is explicitly in PLAN's intent line ("wired into main()'s dispatch and the
module docstring's usage block"). Removing them would leave a comment stating the superseded contract
directly next to the code that reverses it — exactly the defect class D-02/DEC-158 exist to prevent.
No must_fix, no spec_violation.

**No omission found.** REQ-01..REQ-09 and D-01..D-06 all have a landing site; SC-01..SC-13 all have
either a passing automated assertion (re-run, not just read) or, for the `verify: inspection` ones
(SC-06, SC-07, SC-09, SC-10, SC-11, SC-13), a `file:line` citation I checked directly, at the pin.

## Stage 2 — code quality

Hunted fail-open specifically, per dispatch, across the highest-risk file (`gh-sync.py`):

- **`gh()`'s failure path is fail-closed, not fail-open.** Any non-zero return calls `skip()`
  (`sys.exit(0)`) immediately, before the caller's next line runs — so a failed attach POST
  (`gh-sync.py:298`) never reaches `rec["attached"].append(...)` / `save_recorded` (`:299-300`). The
  order is **act-then-receipt** throughout `cmd_open`, `cmd_abandon`, `cmd_ship` — verified by reading
  every `save_recorded`/`gh(...)` pairing, not assumed from the digest's claim.
- **Eng-lead's Q1 (attach path, empty `sub_issue_id`) — assessed, not blocking.** The scenario needs
  `gh(internal_id_args(...))` (`gh-sync.py:297`) to return **exit 0 with empty stdout** (real GitHub
  issues always populate `.id`, so this needs a schema anomaly), **and** the subsequent
  `attach_sub_issue_args` POST (`:298`) to also return **exit 0** despite an empty/invalid
  `sub_issue_id` value GitHub's API would ordinarily 422 on. If the POST fails as expected, `gh()`
  calls `skip()` inside that line and the process exits before the receipt is written (`:299-300` never
  runs) — so the ordinary failure mode is a clean, re-runnable SKIP, not corruption. Both conditions
  failing simultaneously against the real API is not something this codebase's structure can trigger by
  itself; it would require GitHub's API to accept a malformed write. Non-blocking — independently
  re-derived, not relayed.
- **Finding, low severity: `post_body_path` doesn't catch non-UTF-8 content.**
  `gh-sync.py:65-80`, specifically `open(path, encoding="utf-8").read()` at `:77`, is guarded only by
  `except OSError` (`:78`). `UnicodeDecodeError` is a `ValueError`, not an `OSError`, so a
  `--reason-file`/`--body-file` whose bytes aren't valid UTF-8 raises **uncaught**, producing a raw
  Python traceback instead of the intended `gh-sync: ERROR — ... unreadable` message. Reproduced
  directly: `post_body_path` on a file starting `\xff\xfe...` raises `UnicodeDecodeError` past the
  `except OSError`, and the full CLI invocation (`gh-sync.py abandon ... --reason-file <bad-encoding
  file>`) exits 1 via the uncaught exception rather than via `die()` — same exit code, worse message,
  and critically **no gh call happens first** (the crash is before any POST), so this is a UX gap, not
  a correctness or data-integrity one. It is not a build deviation: PLAN's T-05 intent (`PLAN.md:432`)
  literally specifies catching `OSError` only, so the build matches the decided value exactly — this is
  a PLAN-level gap, not something a build task got wrong, and per the review contract does not gate.
  No test exercises this path (all three "unreadable" test fixtures use permission-based unreadability,
  which does raise `OSError`, not encoding-based). Worth a follow-up line item, not a must_fix.
- **`load_recorded`/`save_recorded` round trip re-verified independently** against this feature's own
  `feature.yaml`, read at the pin (`e68ba00`): `github:` block is `parent: none` / `milestone: none` /
  `issues: {}` — SC-10 holds, confirmed by direct read of the pinned bytes, not the dirty working tree.
- No dead code, no copy-paste divergence found beyond what PLAN already called out and accepted
  (`wayfind.py:270`'s redundant pre-attempt, deliberately retained).

## Assessed-and-dismissed (the closed list) — cited, not re-raised

- SC-06's carve-out (retained list-GET endpoint strings in `wayfind.py`) — re-verified by the
  presence greps above, not voided.
- The D-01 `parent_args`/`blocked_by_args` absence-in-`gh-sync.py` guard — confirmed still 0, a
  standing regression guard per PLAN, not evidence of no change.
- `wayfind.py:270`'s redundant pre-attempt — confirmed byte-identical, out of scope.
- The `ticket` dry-run print's literal `-F sub_issue_id=` prose — confirmed unchanged, documentation
  not an argv build.
- D-02's inverted `absorbs` assertions — confirmed as the fix, not a weakened test.
- Absent/unrecognised `parent_origin` ⇒ leave-open — confirmed as the specified default in both
  `abandon` and `ship`, with dedicated fixtures for the no-marker case.
- The `ship closes the milestone regardless of parent origin` label living inside the adopted-parent
  fixture — confirmed at `test-gh-sync.py`, the correct placement to catch a wrapped `if origin ==
  "created":`.
- SC-10's scope (this feature's own `feature.yaml` is in the diff, but its `github:` block is not) —
  confirmed by direct read, at the pin.
- Did not propose re-anchoring `f929d44`/`1ce886a`.

## Open questions

- { id: Q1, question: "post_body_path (gh-sync.py:65-80) catches only OSError; a non-UTF-8
  --reason-file/--body-file raises an uncaught UnicodeDecodeError (traceback, exit 1 by Python
  default) instead of a clean die() message. Matches PLAN's literal spec (OSError only), so not a
  build defect — but is a real gap in PLAN's own decision. Worth a follow-up line to widen the catch
  to (OSError, UnicodeDecodeError)?", blocking: false }
- { id: Q2, question: "DEC-138 am.7 (DECISIONS.md:4350) cites feature.yaml:73 for 'parent: none'; at
  the pin (e68ba00) the block is at :75-78 because that same commit appended a runs: entry to the
  file above it. Accurate when product squad checked it (ae728e8), stale by 2 lines at the pin.
  Worth a docs touch-up, not a defect.", blocking: false }

## Digest

```
VERDICT: PASS
DIGEST:
  headline: FEAT-03-subissue-mirror's build matches BRIEF/PLAN exactly across all eight tasks; every SC-06/D-01/T-07 discriminating grep, SC-10's feature.yaml check, and the full unit suite were re-run live at the pin rather than trusted from the digests, and both fail-open hunts (the attach receipt path, gh()'s skip-before-receipt ordering) come back structurally fail-closed.
  severity_max: low
  findings: 1
  must_fix: []
  spec_violations: []
  reviewed: "4d00dbc..e68ba00"
  human_commits_in_scope: []
  open_questions:
    - { id: Q1, question: "post_body_path (gh-sync.py:65-80) catches only OSError; a non-UTF-8 --reason-file/--body-file raises an uncaught UnicodeDecodeError instead of a clean die() message. Matches PLAN's literal spec, not a build defect, but a real PLAN-level gap. Worth widening the catch?", blocking: false }
    - { id: Q2, question: "DEC-138 am.7 (DECISIONS.md:4350) cites feature.yaml:73; at the pin (e68ba00) the block is at :75-78 because that commit appended a runs: entry above it. Stale citation by 2 lines, values unchanged (SC-10 holds). Worth a docs touch-up?", blocking: false }
  files_touched: [.harness/features/FEAT-03-subissue-mirror/notes/review-harness-code-reviewer-c0.md]
  expertise_update: []
artifact: .harness/features/FEAT-03-subissue-mirror/notes/review-harness-code-reviewer-c0.md
```
