# Pre-flight — FEAT-51 SC-10 hand-test (`notes/uat-FEAT-51-c1.md`)

**READY WITH CORRECTIONS.** Three corrections must be applied before Step 0, or Steps 1–4 will run
and measure nothing: (1) pick a `<FEAT>` that has **no linked worktree**, (2) run the parent under
**Claude Code, not OMP**, (3) give the interrupted member a task that writes one of the **four
canonical artifacts**. With those three settled the script is executable as written; nothing else in
it is wrong. SC-10 stays `not_met` — I did not grade it.

## Why the three corrections (the root cause is one asymmetry)

The claim registry a dispatch writes is the **feature's worktree** when one exists
(`dispatch-guard.sh:115-126`, swap to `linked_worktrees` matching the feature id), but the quarantine
branch reads the **owner** root (`check-domain.sh:150-154, 188, 1685-1708`). Observed here: the
worktree registry holds three live FEAT-51 claims, the main-checkout registry holds `claims: []`
(`.harness/.inflight-claims.json` vs `.claude/worktrees/harness/FEAT-51-claude-code-lifecycle-safety/.harness/.inflight-claims.json`).
So for a worktree-claimed feature the boundary sees no claim and passes the orphan's write through:
Step 2 prints nothing and Step 3 prints four `OK` for the wrong reason.

`orphan_write` fires only when a live claim for the feature has `runtime != "omp"`
(`inflight_registry.py:291-312`) — under OMP the boundary is inert by design. And only
`plan.yaml`, `BRIEF.md`, `feature.json`, `STATE.md` are covered (`inflight_registry.py:23-26`), so
the script's own cheapest suggestion (line 32: a product-lead run with one pm dispatch) yields a pm
whose artifact is a `notes/research-*.md` — never quarantined.

## Step-by-step presuppositions, checked in this checkout

- **Step 0** — the four files exist for a plausible `<FEAT>`: yes for
  `.harness/harness/features/FEAT-50-run-artifact-integrity/` (BRIEF.md, plan.yaml, feature.json,
  STATE.md all present) and for FEAT-45; no `PLAN.md` anywhere, so the "drop it" note (line 27) is
  not needed. `.harness/.inflight-claims.json` exists (42 bytes, `{"claims": [], "schema_version": 2}`),
  so the `cp` succeeds and the Step 1 `diff` has a real baseline — **of the main registry only**.
  The four hashed files are exactly `CANONICAL_ARTIFACTS`; the set is complete, not arbitrary.
  Substitute a `<FEAT>` absent from `git worktree list` — FEAT-50 qualifies today; FEAT-51 itself is
  the worst possible choice, it still has a live worktree.
- **Step 1** — presupposes the parent's claim is visible where the boundary looks. Holds only under
  correction (1). Compatibility claims expire at `CLAIM_TTL_SECONDS = 1200`
  (`inflight_registry.py:29`) — 20 min, inside the script's own ~35 min budget.
- **Step 2** — `python3 .claude/skills/harness/bin/quarantine.py list --feature <FEAT>` exists and
  runs (exit 0, empty today: no `quarantine/` directory exists anywhere in the tree yet). Its root
  defaults to the checkout implied by the **script's own location** (`quarantine.py:70-79`), i.e. the
  main checkout. `--root` exists (`quarantine.py:239`) if the operator must aim it elsewhere.
- **Step 3** — `shasum -a 256 -c` over the Step 0 file is sound, but non-discriminating whenever the
  orphan's write was routed to a worktree (`check-domain.sh:727-731`): the main-checkout copies
  cannot change, so four `OK` is guaranteed independently of the boundary.
- **Step 4** — `adopt --file` exists (`quarantine.py:243`); for `plan.yaml` it delegates to
  `plan-merge.py`'s union merge (`quarantine.py:185-195`), which is exactly the "pre-existing tasks
  are all still there" expectation on line 89. **This is a real mutation of the chosen feature's
  canonical file** — pick a `<FEAT>` you are willing to change, and expect git to be the only undo.
  If `adopt` exits 2 naming a quarantine path, a stale live claim is refusing it (SC-11,
  `BRIEF.md:170-178`); `inflight_registry.py release-all` (cited at `inflight_registry.py:41`) is the
  release path, not a reason to record `not_met`.

## Substitutions to fill before starting

| Placeholder | Value comes from | First knowable |
|---|---|---|
| `<FEAT>` | a dir under `.harness/harness/features/` with all four canonical files and **no** entry in `git worktree list` | before Step 0 |
| `<persona>` | the interrupted member's agent name, e.g. `harness-pm` — `agent` in `quarantine_rel` (`inflight_registry.py:279-288`) | Step 1, at dispatch |
| `<session8>` | `session[:8]` of the member's session, or the literal `nosession` when the host reports none (same function) | Step 1 registry read; **copy it from Step 2's `list` output rather than deriving it** |
| `<basename>` | which of the four artifacts the member attempted | Step 2 output |

## The main-checkout constraint

"Run from the MAIN checkout AFTER merge" (`uat-FEAT-51-c1.md:6-8`) traces to
`BRIEF.md ## Verification gaps:211-214` and DEC-201's measurement: a spawned agent loads skills from
the main checkout. Consistency with the live claim: the code side is already satisfied — the FEAT-51
branch tip `838d9347` is an ancestor of `main` (`8ff525e2`) and `quarantine.py` is committed there
(`aab31504`). But the worktree still exists and still holds three live FEAT-51 claims, which the
script assumes gone. **Operator-facing correction, not mine to resolve:** act on a different feature,
or have the worktree removed from outside it first (never by an agent).

## Results that prove nothing (vs. results that falsify)

The script flags one (line 66: empty quarantine with no write attempted). Add these:

- Run under OMP → boundary inert (`inflight_registry.py:304-306`). Empty Step 2 = **uninformative**.
- Member's artifact not one of the four → no quarantine possible. Empty Step 2 = **uninformative**.
- `<FEAT>` has a worktree → registry asymmetry above. Empty Step 2 *and* four `OK` at Step 3 =
  **uninformative**, and Step 3 looks like a pass.
- More than 20 min between the parent's claim and the orphan's write → the claim TTL expired, the
  orphan writes canonically, Step 3 shows `FAILED`. That is **uninformative**, not falsifying;
  re-run with a shorter member task.
- Step 2 run with a root other than the one the write was routed to → empty for a path reason.

## Open questions — the operator's to-do list

- **Q1.** Is the dispatch-guard→worktree / check-domain→owner registry split intended? If not, the
  quarantine boundary can never fire for any worktree-claimed feature, which is every live feature.
  Harness-owner question; it changes what SC-10 can be run against at all.
- **Q2.** SC-10's own text (`BRIEF.md:165-169`) asks for three confirmations and does **not** include
  resumption identity; the script's Step 1 stop rule (lines 50-52) records `not_met` on a
  `replaced` Q1 even though the three clauses could still be met. Which governs the verdict line?
- **Q3.** `PF-e380f685c0697fb709ff29f65af0cf24` / `B-4` (script lines 94-105): the script answers a
  different event — operator-driven resumption, with the operator supplying the re-entry. The
  no-touch spike is cheaper and strictly more falsifying, and nine tasks rest on its premise. Buy it
  **before Step 1**, as the script advises; if it fails, Step 1 is not worth running.
- **Q4.** Which `<FEAT>` is the operator content to have `adopt` mutate?
