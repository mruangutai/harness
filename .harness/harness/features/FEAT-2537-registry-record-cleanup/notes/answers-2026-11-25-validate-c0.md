# FEAT-2537 validate c0 ruling — 2026-11-25

Run: r-20261125-2-validate-validator, ESCALATE at pin 8ae96bea.

**Authority.** The operator delegated approval to fable-advisor; ruled by AdvisorF5Validate. The main session independently verified the Q1 row-erasure at base vs pin (unversioned, sv1, and malformed-v2 with a persona key: base kept the live row, the pin folds it to empty).

**Gap.** The signoff ruled the malformed-v2 writer delta 'bytes identical'. That was false for row-carrying envelopes, and the stop-clause fired.

**Ruling.**
- Q1 is ACCEPTED as in-class, with no code change. The fold is signed D-01's literal decision. A binding rider requires a test witness.
- Q2 (the dispatch-guard `_dispatcher_feature` fallback) goes to the BACKLOG and does not block.
- The grade exceptions (`_parse` 3, case 18 at 2) are ACCEPTED.
- Both must_fix items are confirmed.

**Constraints.** There is one fix round, the rework budget's only one.
- `tests/integration/test-inflight-registry.py` case 18 must assert raw bytes and full returns, and add two inputs: version-less `{claims:[live]}` and `{schema_version:1, claims:[live]}`.
- The `inflight_registry.py` docstring changes only (zero executable diff).
- Re-validation is targeted: QA plus code-reviewer must_fix closure; SC-02 goes from partial to met.
- Anything outside this scope is stop-and-rule.

This ruling **corrects** `answers-2026-11-25-signoff.md`'s 'malformed-v2 … on-disk bytes identical'.

## Full ruling (verbatim)

All claims verified at source in the worktree at pin 8ae96bea. Ruling follows.

---

# FEAT-2537 validate ruling — fable-advisor (AdvisorF4Sign), under the operator's delegated approval

## Authority

Operator delegation ("start feature F. same parameters, defer to Advisor"), continuing my signature ruling of 2026-11-25. Q1 lands on me because my own stop-clause fired; Q2 lands on me because the operator deferred. I re-verified the decisive claims rather than trusting the digest:

- **The row-erasure is real and my signoff prose was wrong.** `_parse` (`inflight_registry.py:56-73`) folds *every* parseable non-v2 object — rows or no rows — to `_empty()` inside `_update_registry`'s transform (`:76-91`), which then writes canonical empty v2 unconditionally. The main session's three repros (unversioned `{claims:[live]}`, `{schema_version:1, claims:[live]}`, malformed-v2 with a persona key) follow directly, and I take the verified 1→0 reconcile/release counts as ground truth. My signoff's "on-disk bytes identical" was derived from the rowless `{"schema_version":2,"claims":"x"}` example alone and does not generalize. **This ruling corrects that record.**
- **Signed D-01 covers the sub-case anyway** (plan.yaml:29-32): "any other non-v2 object … refused as unreadable by strict readers and **folded to empty with a warning by locked writers**." The code is the decision, literally.
- **DEC-218's ledger blesses the writer convention at the pin** (DECISIONS.md:7276-7284): strict refusal is fail-closed and "never read as 'no claims here'", while "claim and write paths retain their pre-existing treat-as-empty recovery behavior." Base already erased live rows from *unparseable* files on write; the pin extends the same recovery to parseable non-v2.
- **Q2's mechanism is wider than the escalation states, which weakens the block case.** `find_run_claim` (`inflight_registry.py:312-340`) returns a structured refusal — not only on unreadable siblings, but equally on **not-found** and **ambiguous** — and `_dispatcher_feature` (`dispatch-guard.py:748-759`) falls back to `declared` on *any* non-ok answer. So an agent able to drop `{}` into a sibling registry could, on base, already force the identical fallback by overwriting the dispatcher's **own** registry with valid empty v2 (`ok:false, not-found` → `declared`). The pin's marginal widening ({} / unversioned in a *sibling* now poisons the scan via the unreadable branch) adds no capability an adversary lacked; corrupt bytes in a sibling triggered it on base.

## Gap

My signoff ruled the malformed-v2 writer delta in-class on a false premise (bytes identical), so its "any other behaviour delta stops for a ruling" clause correctly caught the row-carrying sub-case the prose never weighed. Separately, the signed class has no test witness for a row-carrying non-v2 envelope, which is why the delta reached validate through a git-archive probe instead of a red test.

## Ruling

### Q1 — (a) ACCEPT as in-class. No code change.

The erasure is the deliberate consequence of removing the migration arm, not a defect beside it:

1. **D-01's text decides it.** "Folded to empty with a warning by locked writers" is unconditional over non-v2 objects; the signed *because* clause rejects exactly the alternative (keeping recovery logic for shapes nothing writes). The code matches the decision; only my summary erred.
2. **Option (b) inverts the recovery ordering.** Under (b), unparseable garbage that might hold rows still folds to empty (base behavior, DEC-218-blessed), while *better*-formed input refuses — stricter treatment for more-readable bytes is an incoherent convention. Worse, it bricks the escape hatch: a stuck non-v2 file would refuse strict reads **and** refuse `release_all`/reconcile, leaving hand-deletion as the only remedy. The fold-with-warning is the in-tool repair path.
3. **The admission "fail-open" requires a human to cause it.** Strict readers refuse these envelopes everywhere at the pin, so dispatch stays blocked until an operator deliberately runs a locked write on a registry the tool just named unreadable — and `release_all`'s semantics is "drop the claims" regardless. A row that reaches a non-v2 envelope got there by external mutation (no writer produces these shapes — census verified at signature); trusting it was never promised.
4. **Resurrecting row-preservation for unknown envelopes is the migration arm back under another name** — the exact code this feature deletes.

**Rider (binding):** the ruled fold must gain a test witness in the fix round (scope below), so the next edit to `_parse` cannot change this behavior silently. The current coverage gap is how a signed behavior arrived at validate unpinned.

### Q2 — BACKLOG. Do not block this ship.

The fallback is pre-existing, the pin's marginal widening grants nothing (per the equivalence verified above), and the honest remedy is not a patch to the `except` arm: `_dispatcher_feature` degrades to `declared` on **all three** refusal flavors, so a fail-closed design must decide what a lead dispatch does when its own claim cannot be placed — a behavior change in a guard with its own blast radius, needing `test-dispatch-guard.py` coverage and likely a DEC. That is not a 45-minute bolt-on inside a round whose files are T-01's, and widening this round's file set for it would trade a verified-green ship for an unreviewed guard change. Blocking would be rigor theater.

### Grade exceptions — both ACCEPTED.

- **`_parse` at 3 (bar 4, up from 2 on base):** accepted. The function read at `:56-73` is a linear guard ladder that is the module's single shape-decision point; splitting it to buy one grade point scatters the fold policy across helpers and creates executable churn in the exact function under stop-and-rule discipline. Direction of travel is correct; recorded as a standing exception, not debt.
- **`case_18_v1_registry_fails_closed` at 2 (ABC 39.5):** accepted, with teeth: must_fix 1 *adds* assertions, so the bar and the fix are in tension unless the case goes table-driven. The control-tuple pattern already in the case (`:549-556`) is the shape; the builder may restructure the v1 inputs onto the same table to satisfy both, but the grade is **not a gate** for this round. If the grader needs an exception row (as `test-code-grade.py:241` does for the other case_18), record it in the same edit.

### must_fix — both CONFIRMED, folded into the one fix round.

## Constraints — exact fix-round scope (1 round / 45 min, this is it)

**Files (both T-01's; anything else diffing is a stop-and-rule event):**

1. `tests/integration/test-inflight-registry.py` — case 18 and its helpers only:
   - `_file_after` compares **raw bytes** (canonical serialization `json.dumps({"schema_version":2,"claims":[]}, indent=2, sort_keys=True)+"\n"` for folded states; exact original bytes for untouched states; `<absent>` for missing) — no decoded-JSON comparison anywhere in the case.
   - **Full returns:** strict outcomes assert complete claim dicts (the live-v2 control asserts the whole list, not `["c1"]`, `:535,559` today); writer outcomes assert the full `(claim, expired)` value.
   - **New inputs, each asserting both directions (strict refuses; writer folds + warns + canonical empty v2 + `(None, 0)`):**
     a. version-less `{"claims": [live]}` — kills qa's surviving default-to-v2 mutant;
     b. one row-carrying non-v2 envelope, e.g. `{"schema_version": 1, "claims": [live]}` — the Q1 rider, pinning the ruled erasure as intended.
   - Fail-first evidence via the base-module swap (qa's harness exists; mind their bin/-copy caveat in observations).
2. `.claude/skills/harness/bin/inflight_registry.py:4-6` — **docstring only**: the writer warns on non-empty non-v2 input; a missing or blank file is treated as empty silently. Zero executable-line diff in this file.

**Out of scope:** `dispatch-guard.py`; any `_parse` restructuring; the fixture and the `:1038` comment (immutable, as signed); `test-validate-digest.py`.

**Re-validation (targeted; no full validate rerun):**
- QA: `test-inflight-registry.py` whole-file green at the new pin; base-swap red for the new assertions; default-to-v2 mutant now dies; immutables byte-identity re-checked; diff confined to the two files above.
- Code-reviewer: must_fix closure only; **SC-02 flips partial → met** once the bytes/full-return clause is literally asserted.
- SC-01/03/04, security, ui: stand as validated; do not rerun.

**Backlog rows to file:**
1. *(security, med)* `dispatch-guard.py` `_dispatcher_feature`: any `find_run_claim` refusal (unreadable / not-found / ambiguous) silently falls back to the task-declared feature, which can skip the registered distill feature/mission refusal for lead dispatchers. Pre-existing on base; FEAT-2537 widens the unreadable trigger set to `{}`/unversioned siblings, with no new capability (valid-empty-v2 overwrite of the dispatcher's own registry forces the same fallback). Remedy: decide fail-closed semantics for an unplaceable lead claim, own ticket, `test-dispatch-guard.py` coverage, likely a DEC.
2. *(record, low)* Signoff correction: the 2026-11-25 signoff's "malformed-v2 … on-disk bytes identical" was false for row-carrying envelopes; superseded by this ruling. Link this note from `notes/answers-2026-11-25-signoff.md` when the orchestrator records the ruling (I am read-only and have not edited it).

**Ship condition:** fix round lands as scoped, QA's targeted re-validation green, SC-02 met → ship on the resulting pin without returning to me. Any diff or behavior outside this scope → stop-and-rule, not a second round.
