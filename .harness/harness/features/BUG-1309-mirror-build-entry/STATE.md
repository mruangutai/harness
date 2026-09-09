# STATE

## Current

- feature: BUG-1309-mirror-build-entry
- run: c19 prepare — `runs/c19copy-product/` (product lead, pm: UAT Steps 3/3b re-anchored onto the
  operator's chosen refusal copy, and the D-19 decision drafted), **PASS**, zero send-backs.
- squad: product only. **No production source and no test file changed in this cycle by any agent,
  and none may be:** `merge-gate.py`, `merge-gate.sh` and `tests/integration/test-merge-gate.py` are
  the DEC-174 enforcement carve-out (`plan.yaml:47-49`, `:73-75`, T-05 `execution_mode`
  `:1047-1048`, D-11 `:139-157`). The refusal-copy edit itself is **main-session-direct** and is
  still owed.
- authorization: **operator ruling R-7, 2026-09-08** — one further focused cycle beyond the
  exhausted 16/16, and the operator's own chosen sentence for the merge-gate refusal:
  `<feature> needs its GitHub mirror recovery completed before this merge can continue.` Recorded in
  full, with the packet, at `notes/rulings-2026-09-08-c19-copy.md`.
- station: **review** (`plan.yaml` `status:`, unchanged), T-05 `done` (unchanged). `approval:` is
  byte-unchanged and unsigned by any agent; `BRIEF.md` is byte-unchanged — **no criterion moves**,
  so no re-signature is owed (SC-04 `BRIEF.md:108-111` still requires only the feature name and the
  re-run command; SC-10 `:157-159` is what this change serves).
- plan: **one additive decision, `D-19`**, applied through `plan-merge.py apply` (+23 lines, nothing
  removed, approval bytes intact). It records the new copy and names T-05's intent step 6
  (`plan.yaml:1249-1251`, which quotes the OLD sentence verbatim as the spec) **superseded, not
  rewritten** — PRINCIPLES rule 15. That quotation is the only place in the repository, outside the
  UAT and the gate itself, where the old wording is pinned.
- `review_sha`: still `9fe5cf3112aed6782dfe3f1833b5e7077b31d953`. It **predates the copy change and
  must be re-pinned** to the commit that carries it before any validator sees it (INV-6).
- mirror: unchanged — parent #1407 and nine sub-issues at review. No station moved, so no
  `gh-sync.py` write was owed.
- budget: **`cycles_used` 17 of `max_total_cycles` 17** — the cap was raised 16 → 17 on the
  operator's explicit authorization (DEC-157: raising a budget is a user decision, recorded here and
  in feature.json), and the 17th is consumed by this authorized copy cycle, of which the product run
  above is the first segment. **Exhausted again: no further fix of any kind is dispatchable without
  a new operator decision.** `len(runs)` 53 of `max_total_runs` 20 — INFORMATIONAL (INV-22).

### What landed this cycle, verified on disk rather than taken from the digest

- `notes/rulings-2026-09-08-c19-copy.md` — the ruling and the **direct implementation packet**: the
  exact production string, the two test assertions that must re-anchor, the UAT scope, the
  validation commands, and the non-goals.
- `notes/uat-BUG-1309-mirror-build-entry.md` — Step 3's quoted expected message and Step 3b's
  observe line now carry the new sentence; 356 → 359 lines, three intended edits, every other step
  byte-unchanged. Step 6's `recover-terminal … --yes` / not-`open` expectation was read and left
  alone: it stays true, because the new string still interpolates `{command_line}`.
- `notes/research-BUG-1309-c19-d19-draft.md` — pm's D-19 body, applied verbatim.
- `feature.json` — `max_total_cycles` 17, `cycles_used` 17, run `2026-09-08-c19copy-product` PASS.

### Next, in order

1. **Main session, direct:** `merge-gate.py:192` → the string in the packet §2, and the two
   assertions in `tests/integration/test-merge-gate.py` (`:65` `"recovery-required" in reason`,
   `:101` `"absent" in reason`) re-anchored per packet §5.2. **Case names are byte-frozen** — T-05's
   `verify:` matches all 26 with `grep -qF "ok    $n"` (`plan.yaml:1063-1073`). Then packet §5.4:
   the integration suite (36 ok, 0 FAIL, `ALL PASSED`, rc read from a variable), the discrimination
   probe, T-05's own `verify:` to `VERIFY-PASS`, commit, re-pin `review_sha`.
2. **SC-10, the hand test** — `notes/uat-BUG-1309-mirror-build-entry.md`, runnable once step 1
   lands. It is still the ship blocker.
3. Then the rewritten briefing, then the ship decision. The stale briefing at
   `notes/ship-review-2026-09-08-resume.md` and its B-1..B-13 backlog still await disposition.

## Open Questions

- Q1 (resolved, 2026-09-08) — SC-04's two evidence gaps: **operator accepted both** on
  inspected-correct source (`notes/research-BUG-1309-c18-sc04-ruling.md`). SC-04 reads MET by
  ruling, NOT by new automated evidence. The two backlog remedies it names remain unscheduled.
- Q2 (non-blocking, mine, reversible) — the `merge-gate: ` prefix is RETAINED in the new copy, on
  the ground that every sibling message carries it and the UAT identifies the speaking gate by it.
  To strike it, edit the source string and amend D-19's `choice:` with
  `plan-merge.py amend --key decisions --id D-19 --field choice` (compare-and-swap); nothing else
  depends on it.
- Q3 (non-blocking, UAT coverage) — the UAT has no step exercising the duplicate-claimant ambiguity
  scenario at all. Pre-existing.
- Q4 (non-blocking, harness defect, 5th and 6th sighting) — an agent returned a complete, well-formed
  fenced digest while the host recorded `failed (exit 1) — subagent called yield with null data`.
- Q5 (non-blocking, harness defect) — `bash-write-guard.sh` blocked `cp` and shell redirection for a
  read-only role but did not block `python3 -c "open(path,'w')"` run through bash.
- Q6 (non-blocking, backlog) — T-05's `verify:` grade assertion takes `min(grade)` over
  `git_merge`/`words`/`direct_merge`/`gh_merge` and never names `option_end`, `first_subcommand` or
  `merge_target`. Satisfied in fact (5/5/4); the remedy edits approval-gated `plan.yaml`.
- Q7 (non-blocking, backlog) — `merge_target` matches `--abort`/`--continue`/`--quit` by exact token
  equality while git accepts unambiguous abbreviation, so `git merge --abo` would be DENIED.
  Direction is over-deny, never a bypass.
- Q8 (non-blocking, plan hygiene, pre-existing) — T-05's enumerated case-name contract lists 21 names
  while `verify:` gates 26; the five D-13/D-14 names never reached the enumeration.
- SC-10 UAT is still NOT executed and still blocks the ship.
