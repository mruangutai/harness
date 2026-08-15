# Receipt — S2-publish-feature-key — harness-backend-dev

## Verdict

Fixed. `factory_decompose.py`'s publish now refuses a plan with no usable top-level `feature`
before any remote call, instead of writing `feature:None`/`feature:` labels and exiting 0.

## The defect, confirmed at source

`factory_decompose.py:293` (pre-fix): `feat_id = plan.get("feature")` — `.get()`, so a missing key
silently yields `None`, propagating into `feature:{feat_id}` labels (`:303`, `:316`, `:331`,
`:344`) and into `feature.yaml` (`:423`), with the entry point exiting 0.

## Additional propagation site found by grep (not in the operator's list)

`factory_decompose.py:316` (pre-fix line numbers) — `factory_gh.add_label(args.repo, args.parent,
f"feature:{feat_id}")`, the `--parent <n>` adopt path. Same `feature:{feat_id}` pattern as the four
sites the operator listed, guarded by the same fix since the guard runs before any of them.

## RED — shown before the fix, with the exact invocation

Command: `python3 .claude/skills/harness/bin/test-factory-decompose.py`

Before the fix, with the three new S2 fixtures added (missing/empty/whitespace `feature`) and no
production change yet, the run was:

```
FAIL  (S2-missing) exits non-zero
        code=None
FAIL  (S2-missing) nothing on stdout
        '{"repo": "acme/widget", "feature": null, ... "issues": {"T-01": 102, "T-02": 103}, ...}\n'
FAIL  (S2-missing) zero mutating gh calls — no remote write at all
        [('ensure_labels', ('acme/widget', ('harness', 'feature:None', 'chore', 'bug',
        'factory:claimed'))), ('create_issue', ..., ('harness', 'feature:None')), ...]
FAIL  (S2-missing) preflight itself never ran either — refused before step 3
        [('preflight', ()), ('ensure_labels', ...), ...]
FAIL  (S2-missing) no 'feature:None' label anywhere in what reached gh
        ['harness', 'feature:None', 'chore', 'bug', 'factory:claimed', 'harness', 'feature:None', ...]
ok    (S2-missing) no bare 'feature:' label anywhere in what reached gh either

FAIL  (S2-empty) exits non-zero
        code=None
FAIL  (S2-empty) nothing on stdout
        '{"repo": "acme/widget", "feature": "", ...}\n'
FAIL  (S2-empty) zero mutating gh calls — no remote write at all
        [('ensure_labels', ('acme/widget', ('harness', 'feature:', 'chore', 'bug',
        'factory:claimed'))), ...]
FAIL  (S2-empty) preflight itself never ran either — refused before step 3
ok    (S2-empty) no 'feature:None' label anywhere in what reached gh
FAIL  (S2-empty) no bare 'feature:' label anywhere in what reached gh either
        ['harness', 'feature:', 'chore', 'bug', 'factory:claimed', 'harness', 'feature:', ...]

FAIL  (S2-whitespace) exits non-zero
        code=None
FAIL  (S2-whitespace) nothing on stdout
        '{"repo": "acme/widget", "feature": "   ", ...}\n'
FAIL  (S2-whitespace) zero mutating gh calls — no remote write at all
FAIL  (S2-whitespace) preflight itself never ran either — refused before step 3
ok    (S2-whitespace) no 'feature:None' label anywhere in what reached gh
ok    (S2-whitespace) no bare 'feature:' label anywhere in what reached gh either

14 of 141 FAILING.
```

That RED run used an earlier, looser assertion set (`code not in (0, None)` and no stderr-content
checks). An advisor review flagged two gaps before this receipt was finalized: (a) `code not in (0,
None)` is looser than this module's own exit grammar — `factory_cli.py:10-16` documents exit 1 as
"nothing to do (not an error)" and states a tool "NEVER exits 1 for a failure", so the assertion
should pin `code == 2` (`EXIT_REFUSED`), matching test 1's sibling unsigned-plan check; (b) the task
required the message to NAME the failure, and nothing asserted that. Both were tightened — `code ==
2` plus two stderr-content checks (plan path present, `"feature"` mentioned) — before this receipt
was written. The final RED-then-GREEN cycle (18 → 24 new checks after tightening, all passing after
the fix; see Verification below) is what this receipt reports as final.

14 of 18 new (pre-tightening) checks failed. The 4 that passed vacuously (e.g. "no bare 'feature:'"
passing for the `missing` mode, "no 'feature:None'" passing for the `empty`/`whitespace` modes) did
so because that particular label text is not the one that mode's `None`/`""`/`"   "` produces —
expected, not a weakness in the discriminating checks (exit code, stdout, mutating-call list,
preflight-never-ran).

## Discriminating red — how confirmed

`make_feature_bad_feature_key(td, mode)` in the test file builds the fixture from the exact same
`plan_dict()`/`good_fleet_dict()`/`GOOD_BRIEF` used by the happy-path fixture (`make_feature`) —
same approved status, same two tasks, same fleet — and mutates only the `feature` key
(`del plan["feature"]`, `plan["feature"] = ""`, `plan["feature"] = "   "`). Everything else is
byte-for-byte what a passing publish already exercises elsewhere in this file (test 2), so the ONLY
variable across the red run is the `feature` key. The pre-fix run above shows the fixture reaching
step 7's board calls and internal_id/attach_sub_issue at the edge pass — i.e. the fixture is
otherwise fully valid and would publish cleanly if `feature` were present, which is the
discriminating property the operator asked for.

## The fix

`factory_decompose.py`, inserted as step "2b", between plan-signature check (step 2) and
`factory_gh.preflight()` (step 3, "THE POINT OF NO RETURN"):

```python
feat_id = plan.get("feature")
if not isinstance(feat_id, str) or not feat_id.strip():
    factory_cli.refuse(
        TOOL, "plan has no usable feature id", plan_path,
        "add a top-level `feature: <FEAT-id>` key to the plan before publishing",
    )
```

Uses the same `factory_cli.refuse(tool, what, value, next_step)` convention as the existing
"plan not signed" refusal three lines above it (`:281-285`) — `what` names the failure, `value` is
the plan path, `next_step` tells the operator what to add and where. `refuse()` exits 2
(`EXIT_REFUSED`), matching the existing unsigned-plan path, and prints to stderr only — stdout stays
empty, matching the C-3a convention already asserted for the unsigned-plan case.

**Placement relative to the first remote call:** before `factory_gh.preflight()` at (post-insert)
line ~295, which is itself the module's own documented "POINT OF NO RETURN — the first remote write
this tool makes" (comment now at the `ensure_labels` call). Placing the guard here means a plan with
no `feature` costs zero preflight calls and zero remote calls — confirmed by the
`rec.calls == []` assertion (not just `rec.mutating_calls()`), which the operator's finding
specifically asked for ("Assert on the recorded calls, not only on the exit code").

**Empty-string / whitespace-only decision:** rejected, same as missing. `isinstance(feat_id, str)`
excludes `None` (missing-key case); `.strip()` truthiness excludes `""` and whitespace-only. All
three collapse to one guard because all three produce an unusable label (`feature:None`,
`feature:`, or `feature:   ` — the last confirmed live in the whitespace-mode RED transcript above,
`('ensure_labels', ('acme/widget', ('harness', 'feature:   ', ...`)). Justification: the operator's
own framing — "A guard that only catches the missing key still writes `feature:` as a label" — is
exactly the empty-string case, and nothing in the finding distinguishes empty from
whitespace-only as a lesser problem; both fail to name a real feature.

**`isinstance(feat_id, str)` also rejects a non-string value** (e.g. a bare YAML number or list
under `feature:`). Checked this is not over-blocking any live plan: `grep -n "^feature:"
.harness/features/*/plan.yaml` returns exactly one line —
`.harness/features/FEAT-10-software-factory/plan.yaml:2: feature: FEAT-10-software-factory` — a
proper non-empty string. No live plan is broken by the type check.

## Out-of-bounds check

`harness_yaml.py` was read (not edited) to confirm `REQUIRED_TASK_FIELDS`/`load_plan` carry no
top-level `feature` requirement (`harness_yaml.py:282`, `:287`) — the guard lives entirely in
`factory_decompose.py`, never in the shared loader. `git status` on the file: unchanged, `??`
untracked as before, no edits.

## Verification — commands, exit codes, counts

All run from `/Users/molchairuangutai/GitHub/harness`.

| Command | Exit | Result |
|---|---|---|
| `python3 .claude/skills/harness/bin/test-factory-decompose.py` | 0 | **147/147** (was 123/123 before this task) |
| `python3 .claude/skills/harness/bin/test-factory-gh.py` | 0 | 82/82 |
| `python3 .claude/skills/harness/bin/test-factory-claim.py` | 0 | 77/77 |
| `python3 .claude/skills/harness/bin/test-factory-config.py` | 0 | 56/56 |
| `python3 .claude/skills/harness/bin/test-factory-integration.py` | 0 | 97/97 |
| `.claude/skills/harness/bin/run-unit-tests.sh --kind unit` | 0 | 10/10 files PASS |
| `.claude/skills/harness/bin/run-unit-tests.sh --kind integration` | 0 | 14/14 files PASS |
| `.claude/skills/harness/bin/check-docs.sh` | 0 | "no stale statements found" (62 patterns / 309 files, receipt included) |

**Count that moved:** `test-factory-decompose.py` went from 123 to 147 checks (+24: 8 assertions ×
3 fixtures — missing/empty/whitespace `feature`; 6 assertions in the first RED pass, tightened to 8
after advisor review added a pinned `code == 2` in place of `code not in (0, None)` and two
stderr-content checks — plan path present, `"feature"` named). Every other file's count is unchanged
from the S1 baseline. No count decreased anywhere.

## Files touched

- `.claude/skills/harness/bin/factory_decompose.py` — the guard (production fix, stays)
- `.claude/skills/harness/bin/test-factory-decompose.py` — `make_feature_bad_feature_key()` fixture
  helper + 18 new S2 assertions (test-first, stays)

No git operations performed (no add, no commit, no checkout, no stash) per the hard constraints.
No mutation was needed for the red demo — the defect was live, so writing the test first produced
red for free, per the task's own note.
