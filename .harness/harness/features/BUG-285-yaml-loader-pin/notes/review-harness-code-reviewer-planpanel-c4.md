# Code review — BUG-285 — plan-panel cycle 4 — scope reader + measurements

**BLUF: PASS.** What the plan instructs the five tasks to BUILD is correct and internally coherent.
Every REQ traces to a task, every task traces to a real REQ, the DAG is acyclic and correctly
serialized (T-01 before T-04/T-05, D-13), the two guard families (T-02 item 5's refusals, item 6's
coercion) compose without interaction, and the ABSENT path is guaranteed by an automated test
(SC-16 / T-03 checks 9–10), not merely by builder discipline. All anchors below were re-verified at
source in this worktree at `6cb113f4` after main's merge; none had drifted from the plan's citations.
No `must_fix`. `severity_max: low`.

## Job A — scope findings

- **[low] T-05's cross-reader value-parity rows (SC-14 groups E1–E3) are a narrow drift detector for
  the duplicated `_opt_int`/`_as_recorded_int` coercion (D-16) — only two value shapes are exercised
  (a quoted `"7"`, a bool `true`).** Concrete scenario: a future edit makes
  `factory_decompose.py`'s copy accept a negative-signed digit string (`"-5"` → `-5`) while
  `gh-sync.py:512-524`'s `_opt_int` is untouched and still returns `None` for it (`"-5".isdigit()` is
  `False`) — `run-unit-tests.py --kind unit` stays green, because none of T-05's 12 fixed inputs
  contains a negative, floating, or otherwise-shaped wrong-typed value. D-16's own justification for
  accepting the duplicate ("what stops it is not discipline but a detector … a change to either copy
  alone reddens the suite") is true only within the tested input set, not in general. Not gating: both
  copies are literally identical today (`factory_decompose.py:133-141` vs `gh-sync.py:512-524`,
  verified at source), so nothing currently reads wrong; this is a bound on the detector's future
  reach, worth recording rather than fixing now.
- **[info] Two panel findings read stale.** `plan.yaml`'s `panel.findings` still carries
  `PF-142f3a51...` (low — "check-plan-routes.py deviation claim mismatch") and `PF-a5b9a3c8...`
  (low — "SC-11 'one check' vs T-03's two checks") both `disposition: open`, but both are now closed
  in the current text: B1 below re-measures the checker at 0 violations, and SC-11's own prose
  ("bent to the task rather than the task to the criterion") already matches T-03's two-check split
  (4a/4b). Recommend the disposition fields be flipped at next plan-merge so a signer does not
  re-litigate a closed question. Non-gating.
- **[info] The `issues` key-admission divergence (gh-sync.py:613 vs factory_decompose.py:137-141,
  see B3) is left open by explicit, repeated choice** (BRIEF Risk (iii), D-06, D-14's carried-forward
  text, SC-14/15's shared comment, Verification gaps) rather than silently dropped. It is a genuinely
  separate policy question — which `issues` keys to admit, not a parser choice or a fail-open read —
  and needs an operator ruling this plan cannot manufacture. Defensible under the one-cycle-remaining
  budget. Non-gating, recorded per this dispatch's instruction.
- **Altitude/duplication — none found.** Five tasks / sixteen decisions / sixteen SCs is heavy for a
  two-function change, but every decision traces to a measurement or an operator ruling, and the two
  pairs that look like they could overlap are explicitly disjoint by their own text: SC-06 (source
  inspection of the absent-path guard shape) vs SC-16 (behavioural test of the same guard, "stays on
  the one method that can falsify it behaviourally"); SC-14 (cross-reader value parity) vs SC-15
  (docstring enumeration content). No wrong-altitude or duplicate criterion.
- **Probes 2/3/4/6/7 — verified, no defect.** (2) Item 5's shape refusals and item 6's coercion
  operate on disjoint dimensions — 5a/5b gate on `isinstance(doc, dict)` / `isinstance(f, dict)`,
  reached only when both are mappings, before the member-level coercion runs (item 6e); a wrong-typed
  *member* never touches a shape refusal and vice versa. (3) The absent path (`factory_decompose.py
  :114-115` early return, `:126`'s membership test before `:133-141`'s reads) is pinned by an
  *automated* gate (SC-16 = T-03 checks 9 & 10, `return == _empty_factory()`), not merely trust. (4)
  T-05's 12 inputs span 11 of the 13 measured classes (the three non-mapping variants — list/string/
  int — are consolidated to one cross-reader representative per D-15's reasoning, with all three
  covered on the `load_factory` side by T-03 checks 5–7, and list/string already pre-existing on the
  `load_recorded` side at `test-gh-sync-open.py:447-450`), and asserts VALUES not just verdicts (E1/E2
  pin `parent == 7`, `issues == {"T-01": 12}`, not merely "neither raised"). (6) SC-15's mandated
  two-part enumeration (holds / deliberately-differs) is what T-04's intent instructs verbatim, no
  residual convergence language survives. (7) see the info finding above.

## Job B — three measurements

**B1 — `check-plan-routes.py`, from worktree root:**
```
$ b1_out=$(python3 .claude/skills/harness/bin/check-plan-routes.py .harness/harness/features/BUG-285-yaml-loader-pin/plan.yaml 2>&1); b1_exit=$?
```
`b1_exit=0`. Output:
```
MANIFEST /Users/molchairuangutai/GitHub/harness/.harness/team-config.yaml
OK T-01 granted to harness-backend-dev, harness-dev-ops, harness-qa
OK T-02 granted to harness-backend-dev, harness-dev-ops
OK T-03 granted to harness-backend-dev, harness-dev-ops, harness-qa
OK T-04 granted to harness-backend-dev, harness-dev-ops
OK T-05 granted to harness-backend-dev, harness-dev-ops, harness-qa
0 violation(s) across 1 plan(s)
```
Zero `DEVIATION` lines. Confirms main's merge made the manifests byte-identical — the standing low
finding (PF-142f3a51...) premised on a team-config skew is resolved.

**B2 — `check-state.sh` INV-15 sweep, from worktree root:**
```
$ b2_out=$(bash .agents/skills/harness/bin/check-state.sh 2>&1); b2_exit=$?
```
`b2_exit=1` (unrelated: 3 pre-existing `VIOLATION` lines — BRIEF not approved, `notes/handoff-
plan.md` over the 60-line handoff cap, INV-37 no `github.build_entry` recorded). No line in the
sweep names `.harness/harness/features/BUG-285-yaml-loader-pin/runs/2026-09-09-01-planpanel-
validator/digest.md` — INV-15 does **not** refuse it (`grep -c` for that run id and for the digest
path both return 0 matches among the 3 `VIOLATION` lines). The file's **last** yaml block (the
2026-09-11 correction appendix, superseding only the `severity_max` field of the 2026-09-09 block per
its own text) carries `severity_max: low`.

**B3 — `issues` key-admission divergence, confirmed at source:**
- `gh-sync.py:613`: `if n is not None and re.fullmatch(r"T-\d+", str(k).strip()):` — admits only
  `T-\d+`-shaped keys, strips them.
- `factory_decompose.py:137,139-141`: `issues = f.get("issues")` / `if isinstance(issues, dict):` /
  `for k, v in issues.items():` / `if isinstance(v, int) and not isinstance(v, bool): factory
  ["issues"][str(k)] = v` — admits any key verbatim, no regex filter.
Divergence confirmed exactly as the shared context states.

## Open questions
- none blocking.

artifact: this file
