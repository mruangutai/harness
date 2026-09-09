# Plan fix c3 — all four decisions applied; plan routes clean — BUG-1309

**Applied, nothing re-litigated.** Nine field amendments (T-02 `verify`+`intent`, T-03
`verify`+`intent`, T-04 `verify`, T-07 `verify`+`intent`+`depends_on`, D-08 `choice`+`because`) plus
BRIEF SC-03 and SC-04. Tasks stay **9**, decisions **9**, REQ **10**, SC **10**, `approval.status:
pending`, BRIEF `## Approval` `pending`. Every write went through `plan-merge.py amend
--expect-sha256`; no new id, no renumbering.

## D-a — the era gate now governs retention (T-07)

T-07's `intent:` retention paragraph now opens with the ERA GATE, placed after the returncode
(`post-merge-sweep.sh:188-191`), `gh-sync: SKIP` (`:192-195`) and `gh-sync: FAILED` (`:206-209`)
gates and before the `feature-worktree.py remove` call (`:213-217`): **absent `build_entry` + basename
in `feature_schema.BUILD_ENTRY_ERA_EXEMPT` → print one line and FALL THROUGH to remove**; retention
applies only to a non-era feature. The branch **does print**, on **stdout** — every other decision this
function announces is stdout and the bed asserts `r.stdout` — opening `post-merge-sweep: <feature_id>
predates the build-entry receipt (feature_schema.BUILD_ENTRY_ERA_EXEMPT), so the worktree is removed
normally.`, carrying no `open` token, the same shape as T-04's and T-05's era lines. The gate covers
the ABSENT key only: an era-named feature that actually recorded `recovery-required` is retained like
any other. The INV-29 derivation is stated in the intent and in D-08's `because` (verified at source:
`check-state.sh:1929-1935`). One symbol, one definition — stated in the intent, as T-04/T-05/T-06 state it.
Import route named: `sys.path.insert(0, BIN_DIR)` is already at `post-merge-sweep.sh:37`.

**Test pair added:** `"T-07 era-exempt absent build_entry is swept"` beside
`"T-07 non-era absent build_entry keeps the worktree"`, fixtures differing only in directory name,
with the same "one without the other is a REJECTED return" words T-04/T-05 use.

**`depends_on` re-proposed `[T-03, T-06]`** — T-07 now consumes T-06's symbol. Graph walked with a
DFS carrying a recursion stack: **acyclic** (T-07 has no dependent but T-09).

**D-08 widened under its existing id:** `choice` now names the retention check as a fourth reader of
the set; `because` carries the INV-29 consequence.

## D-b — verify shell shape

Grepped all nine tasks: the **only** bare `<cmd> && exit 1` statement was T-04's
`printf … | grep -q '^FAIL' && exit 1`. It is now `if printf … ; then exit 1; fi`. `|| exit 1` was
left untouched everywhere. Post-amendment count of `&& exit 1` in `plan.yaml`: **0**. Every new block
written under D-d uses the `if … then exit 1; fi` shape from the start.

## D-c — BRIEF SC-03 and SC-04

Both quantifiers are now scoped to a feature **NOT in `feature_schema.BUILD_ENTRY_ERA_EXEMPT`**, and
each carries the era half: SC-03 "Build CONTINUES at exit 0"; SC-04 "the merge is ALLOWED at exit 0
with no permission decision emitted". Every other clause kept verbatim — station discriminator,
pre-change failing demonstration, LOCAL-receipt clause, gh-unavailable ALLOW.
**Both halves are covered by declared tests:** SC-03 by T-04's `T-04 non-era absent refuses` /
`T-04 station discriminator` and `T-04 era-exempt continues`; SC-04 by T-05's era-named ALLOWED
fixture beside its non-era DENIED fixture. No task invented.

## D-d — verify assertion strength

**Runner shapes confirmed at source; they differ.** `tests/integration/test-gh-sync.py:702-708`
(`check()`) prints `ok    <name>` / `FAIL  <name>`. `tests/integration/test-post-merge-sweep.py:890-894`
prints `PASS: <name>` / `FAIL: <name>` and `EXIT=…`, exiting non-zero on any failure — a **different**
runner, so T-07's block asserts `PASS: <name>` and rejects `^FAIL:`. T-07's intent also requires the
new `case_*()` function be registered in `main()`'s results tuple (`:876-888`), else it prints nothing.

T-02 (7 names), T-03 (7 names), T-07 (7 names) each now: run the suite `|| exit 1`; reject `^FAIL`
(`^FAIL:` for T-07); require the runner's ok/PASS line for each literally-named case. Each task's
`intent:` declares the identical names as a CONTRACT in T-04's words, checked programmatically
(every name in a `verify:` appears quoted in its own `intent:`).

**Probed, not assumed** (`/tmp/planfix-c3/probe_t07.py`, `probe_ghsync.py`, throwaway; verify blocks
run verbatim under `set -e` against synthetic stdout). All four blocks: green only on all-cases-ok +
rc 0; non-zero on a missing case, on a case that printed FAIL (whether the runner exits 1 or 0), on a
suite exit 1, and on the old failure mode — prose-only stdout containing the token the block used to
grep. Zero mismatches. Scenario 1 also proves the D-b defect is gone: the grep-miss no longer aborts
under `set -e`.

## check-plan-routes.py — verbatim, exit 0

```
MANIFEST /Users/molchairuangutai/GitHub/harness/.harness/team-config.yaml
OK T-01 granted to harness-backend-dev, harness-dev-ops, harness-qa
OK T-02 granted to harness-backend-dev, harness-dev-ops, harness-qa
OK T-03 granted to harness-backend-dev, harness-dev-ops, harness-qa
DEVIATION T-04 .claude/skills/harness/bin/gh-sync.py, tests/integration/test-gh-sync.py granted to harness-backend-dev, harness-dev-ops, harness-qa but declared main-session-direct
OK T-05: declared main-session-direct (.claude/settings.json, .claude/skills/harness/templates/settings.snippet.json, .omp/extensions/harness-hooks.ts ungranted)
DEVIATION T-06 .claude/skills/harness/bin/check-state.sh, .claude/skills/harness/bin/feature_schema.py, tests/integration/test-check-state.py granted to harness-backend-dev, harness-dev-ops, harness-qa but declared main-session-direct
DEVIATION T-07 .claude/skills/harness/bin/post-merge-sweep.sh, tests/integration/test-post-merge-sweep.py granted to harness-backend-dev, harness-dev-ops, harness-qa but declared main-session-direct
OK T-08: declared main-session-direct (.claude/skills/harness/references/github-mirror.md, .claude/skills/harness/SKILL.md ungranted)
OK T-09 granted to harness-documentor
0 violation(s) across 1 plan(s)
```

`yaml.safe_load` clean: 9 tasks, 9 decisions, `approval: {status: pending}`, all 9 `verify:` values
still literal `|` blocks; D-08's `choice` tail ends "…and open otherwise." and `because` "…quietly
keeps naming open."

## Open questions — believed defective, NOT changed (out of this dispatch's named scope)

- **Q1 (non-blocking).** T-06's `verify:` still greps `test-check-state.py` stdout for `INV-37` —
  the same prose-dependent shape D-d struck from T-02/T-03/T-07. D-d named three tasks; T-06 was not
  among them. Same substitution fits (that bed's runner shape must be read first; it was not read here).
- **Q2 (non-blocking).** T-05's `verify:` asserts only the two suites' exit status and names no case
  names, so SC-04's era half rests on the suite's own accounting rather than on a named `ok`/`PASS`
  line. `test-merge-gate.py` does not exist yet, so its runner shape cannot be confirmed at source
  today; the case-name contract could be imposed at the moment the file is written.
