# Plan repair — FEAT-55 cycle 1 — all nine goal-check findings

**All nine REPAIRED, none declined.** `plan.yaml` still loads (`yaml.safe_load`, 12 tasks / 19
decisions), `check-plan-routes.py` exits 0 with 0 violations, and `approval:` / `status:` are
byte-untouched (`panel:` still absent, as before). No task added, nothing renumbered, BRIEF.md not
touched. Two rulings recorded as **D-18 (R7)** and **D-19 (R8)**.

| F | Disposition | Ids and fields changed |
|---|---|---|
| F-01 high | repaired | T-04 `intent` §6/§7 (typed mapping now two-valued: `True` = created-and-typed, string `"adopted"` = adopted; adopt branch writes the marker in the same `save_recorded`; backfill is a **key-presence** test, never truthiness), T-08 `intent` §8 (same on `factory_decompose.py:404-407`, exemption added where there was none), T-03 `intent` case H (asserts the marker) + new case **H2** (adopt with `--parent`, rerun without, zero `updateIssue` for that node id, marker still `"adopted"`), T-07 `intent` new case **F** (same on the factory route) |
| F-02 med | repaired | T-10 `verify` — no longer a grep on a constant: reads `github.repo` from `.harness/harness.json` and requires the verdict line to name it, requires exactly one verdict line, asserts the default run creates nothing, and a second run with `PATH` stripped of `gh` must SKIP **and exit 0**. Proved discriminating: a constant-echo stub fails the no-gh leg (exit 1), a probe that consults the environment passes (exit 0) |
| F-03 high | repaired | T-11 `intent` §3 and T-12 `intent` §1 carry one 511-char pinned line, **md5 `c23c47d4…` in both**. It covers (a) capability + declared names, (b) the issue-identifier reads named as *existing practice* (three call sites cited at `eb9d044e`, with "this feature does not remove them" stated in both), (c) the probe's opt-in type read-back. Old substring retained, so both greps still hold; new grep for `the native type assigned to an issue Harness created` added to T-11 `verify`, and T-12 `verify` now *machine-checks* the two copies are identical. D-08 `choice`/`because` amended to describe three clauses, not two |
| F-04 med | repaired | T-05 `intent` case D (rerun must show **exactly one `issueTypes` argv** and zero diagnostics — available mode prints none) + new case **F** (compatibility-mode rerun); T-07 `intent` new case **G** (zero-create factory rerun, exactly one `^factory: issue types ` line); T-06 `intent` §2 no longer overclaims. **Residue, stated in the plan:** a zero-*create* compatibility invocation is unreachable on the backlog route — `main()` dies on `backlog` with no items (`gh-sync.py:1777-1778`) and F-07 gates the receipt off the label path — so the once-per-invocation guarantee is carried there by the query count |
| F-05 med | repaired via D-18 | D-02 `choice`/`because` (feature → Task on a sub-issue; parents via `type_for_parent`; override key `feature` stays legal per D-12), T-01 `intent` assertion 1 + assertion 5, T-02 `intent` (`DEFAULT_TYPE_BY_CHANGE_TYPE["feature"] = "Task"`, three role-scoped resolvers named), T-03 `intent` (fixture gains a **feature** task so the surprising case is proven on the planned route; cases A/C/E), T-04 §4 and T-08 §6 (never resolve a parent through the change_type table), T-07 case A and case **D** (override fixture moved to `{"bugfix": "Story", "parent": "Story"}` — SC-06 keeps a task sub-issue *and* a parent; the contested `feature` override key is pinned at unit level instead). D-01, D-03, D-12 checked: **not falsified**, left alone |
| F-06 low | repaired | T-01 `verify` — fifteen per-value greps (twelve `change_type` spellings, three natures) plus `UnknownWorkNature`, so the red state cannot be an assertionless file. Smoke-checked: silent on a complete file, names each missing value on a truncated one |
| F-07 low | repaired (gate, not BRIEF) | T-06 `intent` §5 (receipt **read and written only when the state is `available`**) and §6 (skipped-item line only there), T-05 `intent` cases C and F assert it behaviourally, D-13 `choice`/`because` amended to carry the gate |
| F-08 low | repaired via D-19 | T-10 `intent` (read-only default; new `CAPABILITY PRESENT` verdict; `--create-in <owner/name>` must equal the configured repo or exit 2 creating nothing; LIVE PASS line reports the number and the `gh issue delete` removal command; close in `finally`), T-09 `intent` (registered `cmd` is the default, non-creating invocation and must never carry the flag) |
| F-09 low | repaired | T-04 `verify` += `tests/integration/test-gh-sync.py`; T-08 `verify` += `test-factory-decompose.py` and `tests/unit/test-factory-gh.py`; and yes, F-07 makes the same argument for T-06 — its `verify` += `test-gh-sync.py` |

## Verification run

- `python3 -c "import yaml; yaml.safe_load(open('.harness/harness/features/FEAT-55-issue-types-created-work/plan.yaml'))"` → OK, 12 tasks, 19 decisions.
- `diff /tmp/feat55-scratch/pin-t11.txt /tmp/feat55-scratch/pin-t12.txt` → exit 0; `md5sum` equal (`c23c47d44ab3093dd48429b835c91fb5`).
- `python3 .claude/skills/harness/bin/check-plan-routes.py <plan>` → `0 violation(s)`, exit 0.
- Every `traces:` entry is inside REQ-01..REQ-11. Every `verify:` is a literal `|` block.

## Open question for the operator

**Q1 (non-blocking).** D-19 makes the probe read-only by default, which introduces a fourth verdict,
`CAPABILITY PRESENT`, for an Issue-Types-enabled repository run without `--create-in`. SC-10
enumerates two verdicts. BRIEF.md is frozen this cycle so I did **not** edit it: for the pinned
`mruangutai/harness` (`issueTypes: null`) SC-10's enumeration is unstrained, and `LIVE PASS` remains
reachable under the opt-in. If the operator wants SC-10 to name the read-only verdict, that is a
one-line BRIEF amendment at signature.
