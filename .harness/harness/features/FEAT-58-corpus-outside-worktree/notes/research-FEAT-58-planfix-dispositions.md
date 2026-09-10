# FEAT-58 — planfix dispositions (all three review digests, one pass)

**Every finding from the three digests is disposed. 3 rejected with reasons; the rest applied.**
`plan.yaml` gained one task (T-16) and two decisions (D-11, D-12) and 20 amended fields; `BRIEF.md`
gained the R-1 predicate correction in two places, the REQ-09/SC-09 de-counting, and the
single-statement worktree count. Approval stays pending in both. `check-plan-routes.py` exits 0
(0 violations; the DEVIATION lines are the expected DEC-174 carve-out output). `depends_on` is
still acyclic, every REQ-01..11 and SC-01..14 is traced, and no task traces a nonexistent id.

**Finding-id namespaces collide across digests** — `F1`–`F6` exist twice with different meanings.
Every row below is qualified by source.

## planfix-eng rulings (`runs/planfix-eng/digest.md`, authoritative mechanism)

|id|disposition|where it landed|
|---|---|---|
|R-1 / item 1|applied, all THREE sites|`BRIEF.md` REQ-04, `BRIEF.md` SC-04, `plan.yaml` T-01 intent. Predicate counts under the passed-in `root`; three refusal states enumerated with (C) the only count-bearing one; blobless clone called out as a non-trigger; SC-04's fixture retained|
|R-2 / item 7|applied|new **D-11** (relocation of the five non-hook-bound sweeps, with the ~25-site repoint recorded as the rejected alternative and the `corpus_open`/batching cascade named)|
|R-3 / items 3+4|applied|T-01 intent: three functions, `corpus_features(root, *, provider="history", ref=None)`, `ValueError` on path+ref and on unknown provider, no `corpus_open`. T-03/T-04 intents replaced with the once-computed `bases[feat]` map (D-12)|
|R-4 / item 5|applied|T-13 intent (two allow-listed basenames, each with its reason) and `T-13.depends_on = [T-03,T-04,T-05,T-06,T-08,T-09,T-16]`; T-06 intent corrected to CALL `corpus_features(..., provider="path")` rather than retarget a glob|
|R-5 / item 6|applied|T-07 gains the discovery-subset (⊆) assertion reusing T-13's git-index enumeration, with non-mechanisability stated; ledger recorded OPEN with the named reason (`bash-write-guard.sh`, `gh-close-gate.sh`, `plan-sign-gate.sh` unclassified); **T-16** owns `branch-create-gate.sh`|
|R-6 / item 9 (reuse F1–F6)|applied, all six|F1→T-03 verify (6 suites); F2→T-04 verify (4 suites); F3→T-06 verify + `check_domain_support.py` `drive()`/`_env()` named in intent; F4→T-08 verify; F5→`verify_required_paths` exported by T-08, imported via importlib by T-09, called by `--verify`; F6→`<sha> = git merge-base <default-branch> HEAD` written into all five sites (T-03, T-04, T-05, T-06, T-12)|
|item 2 (H-1 union)|applied|new **D-12** — ref-only API, caller-side cwd union, per-feature `bases` map, three rejected alternatives recorded|
|item 8 (M-6 batching)|**rejected**, as ruled|relocation deletes the measured 21×87 case; the surviving `corpus_read` caller reads O(1–2) files per merge against a 17.4 ms batch floor. No plan change|

**Correction of record:** ruling item 7 states "only `check-domain.sh`, `merge-gate.sh`,
`dispatch-guard.sh` are hook-registered". That sentence is wrong — `.claude/settings.json` registers
NINE hook commands. The ruling's *conclusion* survives untouched: none of the five relocation
targets appears in `settings.json`. D-11 is worded to the conclusion, not to the false premise, and
T-16's lane cites `settings.json` directly.

## planreview-validator (`runs/planreview-validator/digest.md`)

|id|source|disposition|
|---|---|---|
|MF-1|lead (ext. of ui F2)|applied — see R-1|
|MF-2|lead|applied — T-16|
|MF-3|lead (ui F1, reconciled)|applied — T-01's message contract now REQUIRES a next-step clause in all three refusal states, asserted in its own right (not by token presence) at T-01(c)/(h), T-03(a), T-04, T-05(a), plus `BRIEF.md` SC-04 and SC-05|
|MF-4|lead (ui F5)|applied — T-14's sweep globs `.claude/skills/**/SKILL.md` + `.claude/agents/*.md`, asserts the globbed set is non-empty and larger than three; SC-11 rewritten to an open set|
|F1 (ui)|ui-reviewer|applied — same as MF-3|
|F2 (ui)|ui-reviewer|applied — same as MF-1|
|F3 (ui)|ui-reviewer, low|**rejected.** T-05 already carries the audience clause at the one site where a model must decide retry-or-stop. Differentiating every message by audience is architecting ahead of a demonstrated failure, and MF-3's next-step requirement already covers the operator-facing gap that motivated it|
|F4 (ui)|ui-reviewer, low|applied — T-08 STEP B's failure text now names the cause class (derivation or ref wrong) and the remedy (destination removed, re-run after fixing), asserted in T-08 case (d). Cheap and rides on an edit already being made|
|F5 (ui)|ui-reviewer|applied — same as MF-4|
|F6 (ui)|ui-reviewer, advisory|applied — SC-11 names `harness-ui-reviewer` and states the sweep is its evidence, not a competing gate|

## planreview-eng (`runs/planreview-eng/digest.md`)

|id|disposition|
|---|---|
|C-1|applied — see R-1|
|H-1|applied — D-12|
|H-2|applied — T-01 signature (R-3)|
|H-3|applied — D-11 deletes the branch rather than centralising it; `bases[feat]` in T-03/T-04|
|H-4|applied — R-4|
|H-5|applied — R-6 F1/F2|
|H-6|applied — T-10's second verify command pins `merge-base origin/main HEAD..HEAD` and fails on non-zero return code OR non-empty stdout; SC-07 restated to require both halves|
|H-7|applied — T-14 resolves the ref ONCE as `review_sha` when pinned else `HEAD` and PRINTS which; SC-11 stays `verify: inspection` with the sweep as its named evidence, so the two no longer disagree on grading method|
|H-8|applied — R-6 F5|
|H-9|applied — D-11|
|M-1|applied — `T-07.depends_on` gains T-08 (and T-13, T-16)|
|M-2|applied — each sweep row now EXECUTES the reader against the partial-root fixture and asserts non-zero + the refusal message, instead of asserting a file exists and names the reader. The overlap with SC-04's suites is deliberate and stated: those prove behaviour, this row is the accounting instrument that survives one of them being deleted|
|M-3|applied — T-03/T-04/T-05/T-06 pass the root the script has ALREADY validated into `corpus_root(...)`, never a second independent `os.getcwd()`|
|M-4|applied — T-09 integration case (d): the required-path control FIRES at migration|
|M-5|applied — R-6 F6, five sites|
|M-6|**rejected** — batching ruled out; see planfix item 8|
|M-7|applied — R-6 F3/F4|
|M-8|applied — D-05 is declared the single authority; T-12's guard comment and T-14's prose POINT to it and do not restate the rule|
|M-9|applied — D-05's `because` WITHDRAWS the false claim that D-08's lint is a partial instrument against the correspondence residual. The lint sees bypass only; nothing instruments correspondence, and the entry now says so|
|L-1|applied — T-09's `--verify` calls `verify_required_paths` for every non-refused live worktree; case (e) covers the nonempty-but-wrong cone|
|L-2|applied — T-07's `feature-worktree.py` parity row is scoped to the functions T-08 leaves alone, matching the `harness_boundary.py` row|
|L-3|applied — D-06's `because` narrowed to HARNESS-ROUTED writes, with the out-of-band write named as inside the residual|
|L-4|applied — structural, not arithmetic. `BRIEF.md` Problem states the count ONCE with its citation (`grilling-worktree-corpus-2026-09-09.md:62`) and its mode (`:56`: two throwaway probes removed after measurement, so a live count may read fewer); Verification gaps and Non-goals now REFERENCE that paragraph. Neither number was "chosen": 30 is the only measured figure, 29 is the unmeasured settled statement, and no criterion is gated on the value|
|I-1|**rejected as unfixable by any route, not left open.** The lanes row's false "no member domain grants it" clause is already recorded as false by D-10. `lanes:` is a top-level key; `plan-merge.py` has no verb that reaches one (`apply` is add-only and exits 7 on a changed value, `amend` reaches `tasks`/`decisions` only). D-10 is the correction of record and no further plan change is possible|
|I-2|**rejected as contained.** The receipt's "17 distinct" vs 21 discrepancy cannot mislead: T-03's intent keeps the standing order to re-enumerate the sweep sites at the file's then-current state rather than trust either count|
|Q1 (eng)|answered by R-1: REQ-04 rewritten so the predicate is about the resolution SOURCE, removing the REQ-02/REQ-04 tension|
|Q2 (eng)|answered by D-12: the active in-flight feature is in scope, admitted at the caller, outside the completeness count|
|Q3 (eng)|applied — no plan-level mechanism sequences one feature against another, so T-15's precondition becomes a HARD IN-FILE GATE: the test exits non-zero naming which half failed if FEAT-57's manifest is absent, its ref unresolvable, or its declared path count disagrees. It must never skip or pass vacuously. Also raised as a non-blocking `open_question` for the orchestrator|

## Simplification angle (`notes/receipt-harness-data-engineer-planreview-eng.md`)

1 and 2 are already carried — finding 1 (provider spelled implicitly) IS H-2/R-3, finding 2 (T-06
keeps a glob T-13 forbids) IS H-4/R-4. **Confirmed, not double-applied.** Finding 3 is L-4 above.

## Open, for the operator

- The `<sha>` convention resolves against `origin/main` in T-10's verify literal. If the default
  branch is ever renamed, that literal and the five `merge-base` sites go stale together.
- `plan-merge.py amend --yaml-value` re-emits a list at the parent key's indentation
  (`    - T-03` under `    depends_on:`). It is legal YAML, `safe_load` round-trips it, and both
  splices exited 0 — so the validator's reported defect did not block. Cosmetic only; recorded
  because the next author will see two indentation styles in one file.
