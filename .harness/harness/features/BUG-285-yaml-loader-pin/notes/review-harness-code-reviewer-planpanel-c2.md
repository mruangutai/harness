# Scope review — BUG-285 amended plan, plan-panel cycle 2

## Conclusion

**Clean. Zero findings.** Cycle 1's one `high` (T-02's DECIDED except clause omitting
`UnicodeDecodeError`) is genuinely closed, not just relabelled, and closing it opened nothing new.
Traceability, dependency order, and all three `verify:` blocks remain sound. All seven probes below
came back clean; none rises to a filed finding.

## The two closures, verified at source (not taken on report)

1. **T-02's tuple.** `intent:` now decides `except (json.JSONDecodeError, UnicodeDecodeError,
   OSError) as e:`. Re-measured: `issubclass(UnicodeDecodeError, json.JSONDecodeError)` is False,
   `issubclass(UnicodeDecodeError, OSError)` is False, `issubclass(UnicodeDecodeError, ValueError)`
   is True — so this tuple, unlike cycle 1's two-name pair, does reach it. The read-and-decode
   happens inside `open(path, encoding="utf-8").read()`, before `json.loads` is ever called, so the
   decode failure surfaces as `UnicodeDecodeError` exactly where arm 2 catches it.
2. **BRIEF.** SC-06 (`BRIEF.md:133-146`) now grades coverage of three failure classes, not the
   literal spelling; SC-11 (`:170-181`) is new and instructed — T-03's `intent:` (`plan.yaml`,
   T-03) carries a fourth named check for the non-UTF-8 input, confirmed present in the tree, not
   merely promised.

## Probe answers

**1. Coverage enumeration (T-02 intent item 2b) vs `harness_yaml.py`'s real `load_file`/`load_str`
— CLEAN.** Checked each claim against source:
- `os.path.exists` early return (`factory_decompose.py:114-115`) returns `True` for a directory, so
  a directory named `feature.json` is *not* pre-empted by it, as claimed — `open()` then raises
  `IsADirectoryError`, an `OSError`, caught by arm 3. Confirmed.
- Permission failure → `PermissionError`, an `OSError`. Covered by arm 3. Confirmed.
- Undecodable bytes surface from the `.read()` call itself, before `json.loads` runs — covered
  *only* by naming `UnicodeDecodeError` explicitly, as claimed.
- `DuplicateKeyError` and `MissingDependency` are both confirmed `YamlParseError` subclasses
  (`harness_yaml.py:48,68`) — the enumeration's claim that the old reader refused both is accurate.
  `MissingDependency` "disappears" under the JSON reader because `json` is stdlib — accurate.
  Nothing misstated or omitted.

**2. SC-11's discriminating power — CLEAN, with an explicit answer.** SC-11 alone does **not**
discharge cycle 1's finding: it is honestly self-disclosed as green under both the old and the new
handler, so on its own it cannot distinguish fixed from broken. What discharges the finding is the
*pair*: (a) the corrected DECIDED tuple in T-02's `intent:` is the actual fix, and (b) SC-06 was
regraded to an inspection-based coverage check — evaluated by reading the except clause against the
enumerated failure classes at review time, which *would* redden on a regression to the two-name
pair, unlike the old SC-06 that only grepped for the incomplete pair's literal presence. SC-11's
role is a standing regression guard against the tuple being re-narrowed *after* this fix lands, not
a proof of this fix. That is exactly what it is documented to be; no gap.

**3. T-03 check 4 spans two `check()` calls under a "THE FOUR CHECKS, each named, each its own
check() call" heading — answered, not filed.** The heading is literally inaccurate (4 items, 5
`check()` calls total), but it does not reach a builder producing the wrong thing: item 4's body
text is unambiguous on its own ("assert in ONE check joined with and: ... In a second named check
assert ..."), and splitting a presence assertion (`SystemExit` + code + path) from an absence
assertion (neither phrase present) into two separate `check()` calls matches this file's own
established convention — `tests/unit/test-factory-cli.py:108-112` splits an identical
presence/absence pair (message text vs. "no 'unexpected failure' text") into two calls the same
way. Also confirmed: item 4's presence check is not vacuous — "if load_factory RETURNS instead of
raising, emit a failing check" is present, so the absence check cannot pass by an empty-stderr
non-raise. Cosmetic; no concrete wrong outcome; not filed.

**4. Dependency order vs. T-02's vacuous unit gate — this is listed as STATE, not a re-openable
finding, and I concur with cycle 1's lead judgment on the merits.** `T-02 depends_on: []`,
`T-03 depends_on: [T-02]` is a valid topological order. T-02's own `verify:` line 1
(`run-unit-tests.sh --kind unit`) does sweep a unit-test directory that does not yet contain
`tests/unit/test-factory-decompose-loader.py` at T-02's own execution time — that sweep exits 0
identically to a real pass. Nothing changed this cycle that alters this: T-03 still lands the file
and still runs both verify commands before ship, so coverage is genuinely delivered, just not by
T-02's own gate. Order is right; the gate does not need reshaping.

**5. Duplicate-key loosening — CLEAN, and stronger than "nothing depends on it."** Grepped the tree
for `DuplicateKeyError` consumers: `bash-write-guard.sh`, `check-domain.py`, `check-state.sh` all
catch it for *manifest*/*rulebook* YAML files, never for `feature.json`. More directly:
`feature_json_write.py:71` — the one locked, schema-validated write authority for `feature.json`
that both `gh-sync.py` and `factory_decompose.py`'s own `write_factory` already go through — parses
with plain `feature_schema.json.loads(base.decode("utf-8"))`, which already silently last-wins on a
duplicate key. So `load_factory`'s current YAML-based duplicate-key *rejection* is already
inconsistent with the write path's own tolerance; this change removes that inconsistency rather
than introducing one. No finding.

**6. Carried-forward findings (F3, `PF-2242299b…`) — CLEAN, no growth.** pm's cycle-2 hash table
shows T-01 `intent`/`verify` and T-02 `intent`/`verify` byte-identical to their pre-write values;
only T-03 `intent` changed (check 4 added, heading corrected, `factory_cli` import added). No third
mutation probe was introduced — T-02's inline `python3 -c` verify probe is unchanged from cycle 0/1
and is a behavioural check, not a mutation probe against a production-code copy. F3 and
`PF-2242299b369215b13ad577fe4279d52e` stand exactly as before: open, `info`, non-gating.

**7. Over-specification of T-02's `intent:` — CLEAN.** The growth (the rejected-alternatives
reasoning, the nine-mode enumeration) is not free-floating detail: REQ-06 demands byte-exact
behavioural preservation across every failure mode the old reader absorbed, so pinning the exact
exception tuple *is* the acceptance criterion here, not an implementation choice beyond it. Every
added sentence ties to either "this failure mode must still be covered" or "this one deliberately
isn't, and here is why" — it is evidence-grounded, not padding, and it is exactly the kind of
precision a hand-maintained except-tuple needs after cycle 1 showed what happens without it.

## Other checks (no findings)

- REQ-01..08 all trace to T-01/T-02/T-03; no orphan REQ, no `traces:` citing a nonexistent REQ.
- `depends_on` shape is a valid topological order (T-01: [], T-02: [], T-03: [T-02]); no cycle.
- No `verify:` block asserts something a predecessor task deletes.
- The `approved`/`pending` approval-state disagreement and the stale `lanes:` table are STATE, not
  re-reported here.

## Contract block

```yaml
VERDICT: PASS
DIGEST:
  headline: "Cycle 2 scope review: cycle 1's UnicodeDecodeError gap is genuinely closed by the corrected T-02 tuple plus a regraded, inspection-backed SC-06; SC-11 is honestly a standing guard, not a proof, and that is sufficient; all seven probes come back clean."
  severity_max: none
  findings: 0
  must_fix: []
  spec_violations: []
  code_grade: n_a
  reviewed: "plan:.harness/harness/features/BUG-285-yaml-loader-pin/plan.yaml"
  human_commits_in_scope: []
  open_questions: []
  files_touched: [".harness/harness/features/BUG-285-yaml-loader-pin/notes/review-harness-code-reviewer-planpanel-c2.md"]
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-285-yaml-loader-pin/.harness/harness/features/BUG-285-yaml-loader-pin/notes/review-harness-code-reviewer-planpanel-c2.md
```
