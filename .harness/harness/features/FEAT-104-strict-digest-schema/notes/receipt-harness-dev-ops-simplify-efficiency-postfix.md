# EFFICIENCY angle (postfix) — FEAT-104-strict-digest-schema, at 99035a9c

BLUF: no material waste in the fix delta. Both hot-path additions are reuses of already-loaded
data plus microsecond-scale comparisons; measured, not estimated. Prior pass's F-1 (schema
reopen in `check-state.sh`'s sweep) is untouched by this delta and stands as before — still not
worth an apply at current or near-term census. `findings` below is empty.

## 1. `check-domain.sh` `_version_decreased` block (:1757+) — reuse, not a new read

`prior_doc` is already parsed at `check-domain.sh:1718-1722` (pre-existing identity-check logic,
unchanged by this diff) before the new block ever runs; the new code only calls
`prior_doc.get("schema_version")` on that already-in-memory dict. **No additional file read is
added.** Isolated cost of the new comparison logic itself, 2,000,000 iterations in-process:
**0.000337ms/call** — three orders of magnitude below the ~80-100ms process-spawn floor this
file's own comment (and the prior pass's measurement) already attributes to a governed write.
Not worth flagging.

## 2. `check-state.sh` per-run persona lookup (:1587+) — measured, not assumed

The dispatch frames this as moving from "a single exempt persona to a per-run lookup" and asks
for the sweep's cost before/after. Measured directly, two ways:

**(a) Isolated `validate()` call cost**, same digest text, 2,000 iterations each, in-process
(`importlib` load of `validate-digest.py`, `time.perf_counter()`):
- `validate("lead", text)`: 0.39610 ms/call
- `validate("harness-eng-lead", text)`: 0.39468 ms/call
- delta: **-0.00141 ms/call** — negative, i.e. no measurable cost from switching persona. The
  extra branch code (`dict.get` + two `isinstance` checks to pick `_persona`) is the only new
  work per iteration of the pre-existing `for sy in glob.glob(...)` sweep; it does not add a
  loop, a file, or a schema rebuild.

**(b) Whole-sweep wall time**, old vs. new script content, run three times each from a
`/tmp` scratch copy (content only — via `git show <sha>:path >file`, never touching the tracked
tree) with symlinks to the real `.claude/skills/harness/bin/*.py`/`*.json` siblings and
`HARNESS_PROJECT_DIR` pointed at this worktree, `env -u HARNESS_AGENT_TYPE /usr/bin/time -p bash
<script>`:
- 6126ac07 content (`"lead"` always): 5.84s, 5.45s, 5.66s (avg 5.65s)
- 99035a9c content (per-run persona): 5.23s, 5.57s, 4.84s (avg 5.21s)

New is within run-to-run noise of old (spread ~1s across both sets; new's average is actually
lower). No measurable regression.

**Census** at this checkout (`glob.glob(".harness/*/features/*/runs/*/state.yaml")`, 17 files
total): all 17 have `host` in `LEADS`; of those, 6 already declare `schema_version >= 2` today
(counted via `yaml.safe_load` + `isinstance(v, int) and not isinstance(v, bool) and v >= 2`).
Even at that count, (a) shows no per-call cost to attribute — there is nothing here that scales
with the v2 fraction, because the branch that used to always pick `"lead"` and the branch that
now sometimes picks `_host` cost the same to evaluate. This is not a case of "small today, grows
linearly" — it is O(1) extra work regardless of how many runs are v2, so it does not accumulate
as the run directory grows the way the dispatch's framing worried about.

## 3. `validate-digest.py` message/comment reword (:1401-1421)

Prose-only changes (comment text, one f-string literal naming the file path). Zero runtime cost
difference; not a candidate for this angle.

## 4. Test files

`test-check-domain.py`, `test-check-state.py`, `test-validate-digest.py` diffs are additional
case-table rows and a refactor of existing helper names (`_step_cases`/`_report`) — no new
full-suite invocation, no new subprocess-per-case pattern introduced. Per this angle's own prior
finding (P-16 in Expertise): the diff does not touch the suite-runner mechanism, so re-running
the full suites here would itself be the waste this angle exists to flag. Skipped.

## Findings

None. Both new hot-path branches are either a reuse of already-loaded data (check-domain.sh) or
an O(1) branch with a measured negative-to-zero delta (check-state.sh); neither introduces a new
read, a new loop layer, or a cost that scales with the run census.

## Unchanged from the prior pass

F-1 (`check-state.sh:1492-1496`, schema file reopened per matching run inside the sweep loop) is
untouched by this fix delta — same code, same "not worth an apply" judgement as the prior
receipt (0.0375ms/reopen, currently paid 0 times since `schema_version >= 2` census there is a
separate check from the persona-lookup one; even at a few hundred v2 runs, sub-0.3% of sweep
wall time). My judgement of the rest of the 78e34f06→99035a9c diff (sections 1-5 of the prior
receipt) does not move.

## Out-of-band

None.

findings_count: 0
