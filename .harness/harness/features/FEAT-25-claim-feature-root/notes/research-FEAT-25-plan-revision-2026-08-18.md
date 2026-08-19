# FEAT-25 · plan revision — R-1…R-7 applied

**All seven landed. R-1 landed MODIFIED: its premise is overturned at source.** Task count still 3,
approval still `pending`, no new SC forced. `check-plan-routes.py` exits 0 on the edited plan.

## R-1 — the must_fix, landed but not as ordered

The dispatch ordered me to write that the research note's sentence — *"Any derived rule would have to
special-case the harness itself"* — is **false as written**. It is not false. Writing "false" into
the record would itself be the rule-15 violation the dispatch is trying to prevent.

The dispatch verified `factory_config.py:226` (`name = repo_name.split("/", 1)[-1]`, true) but never
engaged **reachability**, which is what does the work. Re-verified by me at source:

- `FEATURES_ROOT` is built at **module scope**, where no repository name exists at all. There is no
  input to derive from.
- At the gate, every candidate is fleet-filtered: `repos_to_serve = [e["name"] for e in
  fleet["repos"]]`, then `if repo_name not in served_repo_names: continue` (both in
  `factory_claim.py`'s candidate loop, read at working-tree state).
- `mruangutai/harness` is pinned **out** of the fleet — `test-no-distribution.py:160-163`,
  `case3_absence_harness_is_not_a_fleet_member`.

So the split expression never receives `mruangutai/harness`. Fed a reachable input it yields
`kaya-ai`, and `.harness/kaya-ai/features` does not exist. A derived rule reaching today's plans
must map every reachable input to `harness` — hard-coding the literal. The sentence is **true with a
compressed warrant**; the warrant is reachability, not fleet-absence standing alone.

This is the same finding `harness-eng-lead` raised as a `must_fix`, retracted with the same
evidence, and recorded in its own Assessment (`runs/2026-08-18-01-eng/digest.md`).

**What I wrote instead.** The note's point 1 now supplies the missing premise and states exactly
what fleet-absence defeats (`workspace_path` whole) and does not defeat (the bare split expression —
defeated by reachability instead). The fleet-absence fact is kept, not deleted. D-01's `because` was
rewritten to the dispatch's three-step chain (surface / one segment / precedent) **plus** the
reachability-scoped fleet clause. **D-01's conclusion is unchanged: a fixed `harness` segment.**
Dispatch and digest agree on the destination; they disagreed only on the label.

## R-2 … R-7

- **R-2** landed. D-02 now names the wildcard shape, cites the three exact siblings
  (`check-plan-routes.py:540`, `validate-feature-json.py:41`, `layout_migration.py:172` — all three
  re-read by me), and rejects it on **"no single path to name"**, which holds under either R-4
  option. `check-state.sh` deliberately omitted: DEC-174 carve-out, weaker precedent, padding.
- **R-3** landed. T-02 intent item 1 rewritten as one text: extract `_plan(feature)` holding the
  memo, the join, the `load_plan` call and the `try/except YamlParseError` that `task()` carries
  inline today; `task()` and `plan_loaded()` both reach the file only through it; duplicating the
  `try/except` is explicitly forbidden with the poll-loop reason. New `verify:` clause counts
  `harness_yaml.load_plan` calls and asserts 1, both orders.
- **R-4 — option A taken.** `os.path.abspath` inside `_BlockerCache.plan_path`. Reasons: (1) the
  feature exists to send a debugger to the filesystem, and a relative path degrades exactly that
  whenever cwd ≠ repo root, so softening the promise works against the BRIEF's own Problem;
  (2) one in-scope mechanism edit versus three wording edits across REQ-02/SC-04/D-03; (3) it keeps
  BRIEF requirements untouched, confining BRIEF edits to R-6/R-7. `factory_config.py` not touched.
- **R-5** landed — one sentence closing D-02: D-03 converts the residual from silent to
  self-reporting.
- **R-6** landed. SC-08 rescoped to the **implementation diff** (the tasks' `files:` lists), naming
  the bookkeeping that lands outside `bin/` by construction, and keeping the untouched-set clause.
- **R-7** landed. Canonical forbidden set now stated **once**, in `## Constraints`: five files
  (`factory_config.py`, `fleet.yaml`, `harness.json`, `gh_board.py`, `check-domain.sh`) plus the
  `load_board` symbol. SC-08 references it. Grepped both artifacts — one spelling survives.

## The T-02 verify red observation

Ran the edited block verbatim (extracted from the plan by `safe_load`, executed with
`CLAUDE_PROJECT_DIR` set, output captured by command substitution). **EXIT=1.** Red on every
discriminating clause: all five `need` case names absent, ok-line count 113 (needs ≥119), and the
python heredoc raising `AssertionError: ('edge_i', 'T-01')` — the gate still collapses the absent
root into edge (i).

**The new one-read clause never executed** inside that run, because the earlier `edge_i` assert
exits first. So I ran the clause portion **alone against the unmodified module** and observed it:
`AttributeError: '_BlockerCache' object has no attribute 'plan_loaded'`, EXIT=1. Red observed, not
asserted.

It is also discriminating, which absence alone would not prove: with the intended `_plan` extraction installed
on `_BlockerCache` at runtime it **passes** (1 load, `plan_path` absolute); with the forbidden
duplicate-load spelling of `plan_loaded` it **fails**, reporting 2 loads. The clause discriminates
the exact implementation choice R-3 exists to force.

## Budget note

Adding the count clause pushed T-02 to 73 machine-field lines against DEC-182's cap of 50. I
compressed the verify block — a `need()` helper replacing the ten-line `hasok` ladder, and the two
python heredocs merged into one — without dropping a single assertion. Now 50 exactly, exit 0.
**T-02's verify has no headroom left**: any further clause needs a compensating extraction.

## Open

- The dispatch/digest conflict on R-1's premise is recorded above and non-blocking — the conclusion
  is identical either way.
- Carried forward from the eng run, still true: two feature directories share the id `FEAT-25`.
