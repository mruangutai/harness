# Plan panel — scope reader — BUG-285-yaml-loader-pin — cycle 0

BLUF: **No defect found.** Zero orphan REQs/decisions, zero unproduced SCs, `depends_on: []` on a
single task is trivially topological, and every anchor T-01's `intent:` cites — line numbers, helper
names, message substrings, the two literal fixture strings — was independently re-measured against
the live files in this worktree and matches exactly. Findings list is empty by observation, not by
omission.

## What I independently re-verified (not inherited from c0/c1/c2)

- Ran the fixture live: `harness_yaml.load_str("feature_id: F1\ngithub:\n  parent: 40\n", ...)` →
  `{'feature_id': 'F1', 'github': {'parent': 40}}`; `json.loads` on the same text raises
  `JSONDecodeError`. Matches D-01/SC-01 exactly.
- Traced the mutant path by hand through `gh-sync.py:522-561`: with `doc` replaced by the YAML
  parse, `isinstance(doc, dict)` passes, `"github" in doc` passes, `gh` is a dict, falls through to
  `rec["parent"] = _opt_int(gh.get("parent"))` → `40`, no exception. Confirms SC-03's claimed mutant
  behaviour (`gh-sync.py:554`).
- Traced the real path: `json.loads` raises at `:523`, caught at `:524`, `SystemExit` raised at
  `:529-531` with message `f"gh-sync: {path} does not parse, ..."` — contains both the full
  `feature.json` path and the literal substring `does not parse`. Confirms REQ-03/SC-02.
- Confirmed every numbered anchor in T-01's `intent:` against the real file with `grep`+`read`:
  `test-gh-sync.py` lines 16 (sys.path insert), 17-18 (`json`, `os`), 25 (`harness_yaml`), 144
  (`nested_feature_dir`), 769 (`check`), 1406-1410 (`_ghs` load), 1442 (T-06C case-2 close),
  1444 (`fix1 Part B` comment, literal), 1474-1480 (the zero-byte try/except template). All exact,
  none drifted — corroborating c2's "nothing drifted" claim rather than trusting it.
- Confirmed `check()`'s own output format (`gh-sync.py`… no, `test-gh-sync.py:769-776`): `ok    {name}`
  / `FAIL  {name}\n      {detail}`, and the file's own `sys.exit(1 if fails else 0)` at line 3556 —
  so SC-04's claims about literal `ok`/`FAIL`-prefixed lines are things this command actually prints,
  not an inference from exit code.
- Checked traces/SC coverage: REQ-01..04 all exist in BRIEF and all are cited by T-01's `traces:`;
  no orphan REQ, no task citing a non-existent REQ. SC-01 through SC-05 each map to an identifiable
  piece of T-01's work (fixture+2-way check, refusal-message check, probe+note, verify command,
  diff-scope inspection) — none is left with no producing task.

## The six contract questions

1. **Worth building?** Yes, no defect. Cost is one fixture in one file with zero production risk;
   benefit closes a real (if advisory) blind spot the operator diagnosed and explicitly scoped this
   tightly themselves (`intake-BUG-285.md` §1). Advisory severity does not make the fix disproportionate
   to its (small) cost.
2. **SC-03 self-certification?** Adequate, not a defect. The mutation-probe is one-off, but the
   *ongoing* regression detector is SC-02 (a permanent, re-runnable suite check), and SC-01's own
   two-directional assertions redden first if the fixture is later edited toward non-discriminating.
   BRIEF's `## Verification gaps` names exactly this residual (no gate re-verifies the assertion's
   future kill-ability) and that residual is inherent to one-off mutation testing generally, not a
   gap specific to this plan's execution; building permanent mutation infrastructure for one fixture
   would be disproportionate scope creep.
3. **D-02 author=grader (harness-qa)?** No defect — by design, not by this plan's choice.
   `harness/SKILL.md:149-152`: "harness-qa writes and runs the tests and enforces the `test_matrix`
   hard gate" is the standing architecture for every feature, not something D-02 introduces. The
   substantive correctness grading of SC-01/02/03 (verify: inspection) is a *different* persona's
   job — `harness-code-reviewer`, per `harness-code-review/SKILL.md`'s Stage 1 — so real independence
   exists at the point that actually matters (correctness), even though qa is both writer and
   test-matrix-gate for its own diff, as it structurally always is.
4. **SC pinning observable outcome vs. implementation?** No defect. BRIEF's SC-01 stays generic
   ("a fixture... that a YAML loader parses to a mapping and json.loads rejects") — it does not pin
   the literal string. The literal fixture text is pinned one level down, in `plan.yaml`'s `decisions:`
   as D-01 with stated rationale — exactly where an implementation choice that needs sign-off belongs,
   and it is a choice I independently measured to be correct. This is "no more specific than
   necessary" applied correctly: the BRIEF stays weak, the plan pins what's needed to be buildable.
5. **`lanes.rows[0].surface: tests/**` broader than the one file?** No defect. The lane defines
   domain eligibility, not task scope; `files:`, the `intent:`'s explicit single-file boundary, and
   `check-plan-routes.py`'s clean grant together already narrow it. Standard pattern, not unique here.
6. **REQ-04/SC-05 "delete nothing" vs. the standing "delete, never re-pin" test rule?** No defect —
   the two rules trigger on disjoint conditions. The standing rule fires when a change alters
   production behaviour a test currently pins, forcing a choice between re-pinning to new reality
   or deleting; this plan makes zero production changes, so no existing check's assertion is being
   invalidated or needs re-pinning. REQ-04/SC-05's blanket boundary and the standing rule simply never
   collide in this diff.

## Findings

None. Empty list is the honest result of the above checks, not a placeholder.
