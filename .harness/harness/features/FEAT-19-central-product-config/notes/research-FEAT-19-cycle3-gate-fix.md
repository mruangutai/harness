# FEAT-19 cycle 3 — the weak gate closed, and two rulings

## BLUF

T-02's `verify` now asserts `status == "unresolved"`, not merely that the key exists — the gate can
now catch the exact claim D-03 was priced to avoid. Both other items are ruled: **main() cases are
added** to T-01, and **the D-08 middle path is TAKEN**. `check-plan-routes.py` exits 0, 7/7,
0 violations; the plan `safe_load`s and all seven `verify:` are literal `|` blocks. Plan stays
`pending` — nothing here is signed.

## 1. The gate fix — T-02 `verify` only

Was: `elif "status" not in spec: bad.append(name + " has no status")`.
Now: `elif spec.get("status") != "unresolved":` and the failure line reports the offending value and
cites D-03 option A and DEC-187.

One clause covers both missing and wrong. It is in T-02's one-shot **only** — T-01's live-config
case is untouched and stays key-legality (mapping-ness, matrix closure, no `__bug_class__` in
`bugfix.always`). The one-shot dies with the task, which is the right lifetime for a check on a
decision's initial state; a `== "unresolved"` assertion in the permanent suite would fail the day
someone legitimately promotes a kind to `active`.

## 2. Ruling — main() cases: ADD them (four, not three)

Discriminating fact: SC-12 is `uat` and ships `not_met` by design, so without T-01 cases the CLI
surface has **zero build-time proof**, and its only evidence is the thinnest pointer in the feature.
The cost is four bullets in an `intent:` the implementer already executes; the benefit is that the
payload T-07 depends on is regression-guarded. Added to T-01's case list:

- exactly three top-level keys and no others — asserted as a key SET, so an extra key fails
- `product` is JSON null on the harness branch, present as a key rather than omitted
- `--which-config .` with cwd at the fixture root resolves the same as the absolute path — DESIGN
  Contract 5's relative-path acceptance, which nothing else asserted
- one refusal branch exits 2 with EMPTY stdout, diagnostic on stderr, per `factory_cli.run`

**SC-12 stays `uat`.** The verification method is fixed at approval; this is added regression
safety, not a converted criterion. No `traces:` change — T-01 already carries REQ-01..05 and the
refusal case is REQ-04.

## 3. Ruling — the D-08 advisory: TAKEN

Reason: it retires D-08's only real cost ("nothing checks the mirror") at zero change to
`harness_boundary.py`, so the DEC-174-in-substance question that decided the ruling is never
acquired. Declining would preserve a cost that has a free remedy.

The "cheap as described" condition was checked at source rather than taken on report:
`select_base(abs_target, root, workspace_root, workspace_bases, fleet_path, label)` takes **every**
input as an argument (`harness_boundary.py`, the `def select_base` line), so a fixture drives it
with no monkeypatching and no env manipulation. It returns a 3-tuple, so the case text names
element 0 as the base to compare — otherwise the implementer bounces on the call shape, which is
the cost the "free remedy" claim denies.

Added as a T-01 test case, with both of eng-lead's cautions written into the case text: nested
fixture **only** (`select_base` calls `sys.exit(2)` on the unregistered-checkout branch and would
abort the test process), and the signature coupling stated as intended rather than incidental. The
case also says explicitly that the import is read-only, in the test file alone, and that
`factory_product_config.py` still must not import it — otherwise it reads as contradicting T-01
step 5b.

Three places rewritten so the record does not contradict itself (G-13):

- `BRIEF.md` D-08 option A cost row — "nothing checks that it was" replaced by the test, with the
  limit stated: one fixture, not general agreement, and the mirroring is still a hand edit.
- `plan.yaml` T-05's containment bullet — same correction, so the DECISIONS entry the documentor
  writes records the mitigation and does not overstate it.
- `plan.yaml` T-01 step 5b — points at the test case, keeping "not an import" true of the module.

The plan's `decisions:` D-08 block is **unchanged**: its `choice` and `because` assert nothing the
test falsifies, and editing a ruling the dispatch closed is not mine to do.

## Not done, deliberately

- A4 (citing DESIGN Contract 3 row 7 in T-01) — the designer is in `DESIGN.md` concurrently; a
  citation written now can be stale tonight. Out of the dispatch's three items.
- A5, A6 — advisory statements of fact, no artifact change.
- Nothing committed. The operator signs first; `BRIEF.md`, `plan.yaml`, `DESIGN.md` remain
  untracked working-tree files.

## Gate results, re-run at working-tree state

- `python3 .claude/skills/harness/bin/check-plan-routes.py .harness/features/FEAT-19-central-product-config/plan.yaml` → **exit 0**, 7 OK rows, `0 violation(s) across 1 plan(s)`.
- `yaml.safe_load` of the plan → **exit 0**. All seven `verify:` scalars are `|` (regex over the raw
  file returned seven `|`, no `>`). T-02's verify is 28 lines, largest in the plan, inside the
  50-line per-task machine budget the checker enforces.
- Every heredoc'd `verify` body `ast.parse`s clean (T-02, T-03, T-05, T-06, T-07).
