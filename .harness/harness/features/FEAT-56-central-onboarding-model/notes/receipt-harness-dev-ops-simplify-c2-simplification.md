# SIMPLIFICATION angle — FEAT-56 simplify-c2 — receipt

Read-only. Scope: `git diff 4b5dbb23..HEAD`, the three new integration suites, the new unit suite
(`tests/unit/test-fleet-product-config.py`), and every touched `bin/` file. No repo edit made.

## Method — accounting for every case

- `test-check-omp-port.py`: read the full `main()` body (23 `check()` calls). Grouped by fixture:
  1 baseline structural pair + 1 live-tree-pass + 10 mutate/assert pairs, each pair mutating a
  **different file/field** to trip a **different validation branch** in `check-omp-port.py`
  (AGENTS.md presence, model provider-neutrality, Claude adapter staleness, `async.enabled`,
  `task.maxRuntimeMs`, OMP lifecycle wiring, `plan-sign-gate.sh` wiring, `blocking: true`, one
  missing command door, the whole canonical command root missing). All 23 accounted for; **zero
  collapse**.
  2. `test-sync-command-adapters.py`: read the full `main()` body (12 `check()` calls). One pair
  collapses — see F2 below. The rest (clean pass, orphan-door, missing-adapter, apply-creates,
  apply-byte-match, check-passes-after-apply) are distinct branches in `sync-command-adapters.py`.
  3. `test-onboarding-split.py`: read in full (204 lines). Structured as per-token/per-marker case
  generators, not a flat `check()` list; its own docstring (lines 10-13) states the reason
  per-file-per-token assertions are not redundant with each other (a file-global search is blind to
  the one non-conforming file) — recognised, not re-litigated.
  4. `test-fleet-product-config.py`: read in full (285 lines, cases a/b/c/d/f/g/e-1/e-2). Each
  exercises a distinct branch of `product_config_report`/`_check_product_configs` (all-ok,
  first-fails, invalid-JSON, unexpected-exception-propagates, ordering, exit-code/payload shape).
  No collapse.

## Findings

**F1 — dead disjunct, `factory_config.py:478`.** `lane: applicable`, `severity: low`, `apply: yes`.
`if unreachable_count or len(report) != len(fleet["repos"]):` — the second disjunct can never be
true: `product_config_report` (same diff, `factory_config.py:341-353`) unconditionally appends
exactly one entry per `fleet["repos"]` member (its own docstring guarantees this), and any
unexpected exception propagates rather than returning early. Cost: a reader has to imagine a
scenario that cannot occur, and if `product_config_report`'s contract is ever loosened this branch
would start firing silently with no test ever having exercised it (confirmed: no case in
`test-fleet-product-config.py` sets up a short report). Alternative: `if unreachable_count:` and
drop "or the report came up short of the declared count" from the docstring at
`factory_config.py:454`.

**F2 — same-path pair, `test-sync-command-adapters.py:78-80` collapses into `:70-71`.**
`lane: applicable`, `severity: info`, `apply: no — backlog (no assertion may be weakened after the
qa gate)`. "missing banner line fails --check" / "missing-banner failure names the file" and
"edited adapter body fails --check" / "edited-body failure names the file" both trip the identical
branch in `sync-command-adapters.py:40`
(`if not target.is_file() or target.read_text(...) != content:`, the second disjunct) — the only
difference is which literal corrupts the adapter body (dropped banner vs. appended drift line).
Neither exercises a distinct branch, boundary, or precedence rule the other doesn't. Not applied
per the apply ceiling (qa already PASSed this suite's coverage); recorded for `harness-pm`/backlog
only.

**F3 — CLI-probe absence assertions, recognised and excluded.** `_cli_probe_absence_cases()`
(`test-onboarding-split.py:72-83`), used at line 182 for `harness-init/SKILL.md` and inline at
lines 175-179 for `harness-add-repo/SKILL.md`, pin `claude --version` / `2.1.217` source text on
purpose — the permanent guard on the operator's CLI-floor ruling (own docstring, lines 73-75).
Identified; excluded from both the collapse analysis and the implementation-pinning check by
design, not oversight.

**Implementation-pinning sweep (point 2): none found beyond the excepted CLI-probe cases.** The
onboarding-split and product-config assertions pin skill/command *prose* and CLI *stderr* text —
for a skill (LLM-read instructions) and a CLI (operator-read output), that prose/text **is** the
observable contract, not internal wiring. The one internal-constant reference
(`fc._PRODUCT_CONFIG_PATH`, `test-fleet-product-config.py:219`) compares report shape against the
module's own path constant rather than a re-typed literal — a live-drift guard, not a mock echo;
not flagged (matches Expertise O-2: adjacent-looking checks that each guard a distinct fact are
not redundant just because they resemble each other).

**bin/ comment sweep (point 4): clean.** All seven touched scripts
(`check-domain.sh`, `check-instruction-paths.py`, `check-state.sh`, `gh-sync.py`,
`layout_migration.py`, `post-merge-sweep.sh`, `upgrade-config.py`) rewrite operator-facing
messages/comments to state the present central-model fact (e.g. "this control-plane clone", "a
copy or worktree of the control plane carries every reader file") — none narrates the change
itself ("now also", "previously this"). `post-merge-sweep.sh`'s comment already replaced a
line-number citation (`SKILL.md:73/:78`, now stale after the 279-line cut) with a heading-name
citation — the dead-reference fix this pass would otherwise have flagged is already done. No
findings here.

**F4 — ordering-fixture lead: decided YES, spec below.** `lane: applicable`,
`severity: med` (closes a named, currently-unbound discriminator), `apply: yes` (adds an assertion;
does not weaken one, so it does not collide with the no-weakening rule).
`qa-FEAT-56-c2.md` §4 is right: the `12f74ea8` blob has no `harness-add-repo/SKILL.md`, so the
ordering clause in `_central_model_marker_cases()` (`test-onboarding-split.py:86-123`) has never
been observed reddening, and qa's own ad hoc reversed-order probe against a synthetic string
already proved it discriminates. This is cheap (one pure-function call, no I/O, no fixture files)
and closes a real, named gap — worth adding. Spec, precise enough to apply without re-derivation:

- Add a new case function in `test-onboarding-split.py`, after `_central_model_marker_cases`
  (i.e. anywhere above `main()`, e.g. after line 123):
  ```python
  def case_central_model_marker_order_regression():
      """Synthetic proof the ordering clause can redden: the 12f74ea8 blob has no
      harness-add-repo/SKILL.md to exercise it (qa-FEAT-56-c2.md §4), so this binds the
      discriminator directly instead of resting on that accident."""
      ordered = f"{DEFAULT_BRANCH_MARKER}\n{FLEET_MARKER}\n{SEGMENT_MARKER}\n"
      reversed_ = f"{SEGMENT_MARKER}\n{FLEET_MARKER}\n{DEFAULT_BRANCH_MARKER}\n"
      ordered_last = _central_model_marker_cases(ordered, "synthetic (correct order)")[-1]
      reversed_last = _central_model_marker_cases(reversed_, "synthetic (reversed order)")[-1]
      return [
          ("synthetic ordering regression: correctly-ordered markers pass the ordering clause",
           ordered_last[1], ordered_last[2]),
          ("synthetic ordering regression: reversed markers fail the ordering clause",
           not reversed_last[1], reversed_last[2]),
      ]
  ```
- Slot it into `main()`'s `results = (...)` tuple (currently lines 188-194), appended after
  `+ case_cli_probe_strings_absent_from_both_cut_skills()`:
  `+ case_central_model_marker_order_regression()`.
- Helper called: `_central_model_marker_cases(text, source_label)` (already exists, unmodified).
  Expected result: first synthetic case passes (`True`), second synthetic case passes because
  `not reversed_last[1]` is `True` (i.e. the reversed input itself fails the ordering clause,
  proving it can redden).

## Not flagged (recognised, out of scope)

D-14, the CLI-probe absence assertions (F3 above), the two-artifact split, the four canonical
doors, the generated-adapter model, REUSE-1, REUSE-3 — none re-litigated.

```yaml
VERDICT: PASS
DIGEST:
  headline: one applicable dead-conjunct finding, one backlog-only test collapse, CLI-probe exclusions confirmed, ordering-fixture lead decided yes-with-spec
  findings:
    - id: F1
      file: .claude/skills/harness/bin/factory_config.py
      line: 478
      summary: "unreachable disjunct `len(report) != len(fleet[\"repos\"])` in the exit-code check"
      cost: "reader must imagine an impossible case; a future loosening of product_config_report's contract would make this branch fire untested and unnoticed"
      alternative: "`if unreachable_count:` alone; drop the matching clause from the _check_product_configs docstring at line 454"
      lane: applicable
      severity: low
      apply: "yes"
    - id: F2
      file: tests/integration/test-sync-command-adapters.py
      line: 78
      summary: "\"missing banner line\" pair collapses into \"edited adapter body\" pair (sync-command-adapters.py:40, same disjunct, different corrupting literal)"
      cost: "two cases exercise one branch; no distinct boundary, precedence, or error is added by the second"
      alternative: "collapse case 4/5 into case 2/3, or repoint case 4/5's fixture at a genuinely distinct branch (e.g. the actual_names-minus-expected orphan-removal disjunct is already covered separately at line 84)"
      lane: applicable
      severity: info
      apply: "no — backlog (no assertion may be weakened after the qa gate)"
    - id: F3
      file: tests/integration/test-onboarding-split.py
      line: 72
      summary: "CLI-probe absence assertions (claude --version / 2.1.217) identified as the deliberate, permanent operator-ruling guard"
      cost: "n/a — recognition only"
      alternative: "none; excluded by design per dispatch"
      lane: report-only
      severity: info
      apply: "n/a — excluded by dispatch, not a finding"
    - id: F4
      file: tests/integration/test-onboarding-split.py
      line: 123
      summary: "ordering-fixture lead: add a synthetic out-of-order case binding _central_model_marker_cases's ordering clause, since 12f74ea8 has no harness-add-repo/SKILL.md to exercise it"
      cost: "the ordering clause SC-01 rests on stays unbound by any permanent fixture; a regression there would stay green"
      alternative: "see full spec in receipt body: new case_central_model_marker_order_regression(), slotted into main()'s results tuple after case_cli_probe_strings_absent_from_both_cut_skills()"
      lane: applicable
      severity: med
      apply: "yes"
  open_questions: []
  files_touched:
    - .harness/harness/features/FEAT-56-central-onboarding-model/notes/receipt-harness-dev-ops-simplify-c2-simplification.md
  expertise_update: []
artifact: .harness/harness/features/FEAT-56-central-onboarding-model/notes/receipt-harness-dev-ops-simplify-c2-simplification.md
```
