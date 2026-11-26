# FEAT-2542 validate c0 ruling — 2026-11-26

Run: r-20261126-2-validate-validator, ESCALATE at pin bc937a94.

**Authority.** The operator delegated approval to fable-advisor; ruled by AdvisorA4Validate.

**Gap.** An ok claim with a null feature fails open to the declared feature (must_fix 1). The printed repair commands, which are signed wording, are not runnable as printed (OQ-1).

**Ruling.**
- must_fix 1 is confirmed, high. Inside `_lookup_placement`, after the ok check and before the persona check, refuse any feature that is not a non-empty str. Do not add a separate sentinel. The omitted feature normalizes to `"legacy"` and must PASS.
- OQ-2: reuse the token `unreadable`.
- OQ-1: amend T-01.intent through `record-amendments` and apply wording rules 1-4.
- OQ-3: non-gating.
- OQ-4: add an ordering row; the two low gaps stay out.

**Constraints.** This is the fix round and consumes round 1 of 2. Re-validation is targeted and delta-scoped, with all five readers.

## Full ruling (verbatim)

All load-bearing claims are now verified at source. Ruling follows.

---

# Fix-round ruling — FEAT-2542 validate run r-20261126-2-validate-validator, pin bc937a94

Ruled by fable-advisor under the operator's delegated approval. Verdict on the run: **ESCALATE resolved — one fix round ordered.** The digest's substance is right; I verified the fail-open myself. One correction to the must_fix before anything else, because it changes a fixture's expected outcome.

**My most important disagreement: the must_fix's "null **or omitted**" conflates two shapes with opposite correct outcomes.** An *omitted* feature never reaches the guard as `None`: `find_run_claim` returns `claim.get("feature", LEGACY_FEATURE)` with `LEGACY_FEATURE = "legacy"` (inflight_registry.py:34,339), the write path normalizes falsy features the same way (:870), and the module states "A featureless claim is real — LEGACY_FEATURE exists for exactly those" (:858-859). So `"legacy"` is a deliberate, contract-conforming producer answer — a non-empty string the new check must **pass**, not refuse. Only an explicit on-disk `"feature": null` (registry damage; the writer cannot produce it) reaches the guard as `None`. A fixture written to expect refusal on the omitted shape would be red at the pin and would misstate the producer's contract.

## must_fix 1 — the null-feature fail-open

**Authority.** D-01 ("the silent declared-feature fallback, which is the defect" — DEC-258's own *Over* list, DECISIONS.md:8740); SC-02's class definition ("every `find_run_claim` outcome", BRIEF.md:71); my signoff constraint 3 (inflight_registry.py byte-identical to base), which forces the fix guard-side.

**Gap.** Verified at source: `_lookup_placement` returns `found["feature"]` unvalidated (dispatch-guard.py:829); `_dispatcher_placement` stores it where `None` already means "outside the contract" (:833-840); `_bound_distill_feature` then takes the declared-feature branch (:884-886). An ok, persona-matched claim with `feature: null` silently falls back to the declared feature — exactly D-01's class, and it falsifies DEC-258's "placed only by its own runtime claim" for this shape. The characterization enumerated `find_run_claim` outcomes by cause, never by the shape of a successful row; that is how it escaped.

**Ruling. Confirmed, gating, severity high stands.** Security's med rested on registry damage as precondition — but a damaged registry is the precondition this whole feature exists to handle loudly (DEC-218: cannot-read is never no-claims; a malformed row is the same moral class). Fix: inside `_lookup_placement`, **after the `ok` check and before the persona check**, refuse at exit 2 any ok result whose `found["feature"]` is not a non-empty `str`. Order matters: `_refuse_persona_mismatch` interpolates `found["feature"]` into a printed release command (:810-813), and `--feature None` is precisely the broken-printed-command defect class of ESC-1, so the malformed-record diagnosis must win over the persona diagnosis.

**On the sentinel question: no separate sentinel object.** With the refusal placed inside `_lookup_placement` before its `return`, the function's postcondition becomes "non-empty str, or exit 2" — the collision is unrepresentable by construction, which *is* the structural fix. `_PLACEMENT_UNSET` already distinguishes unset from `None`; after this change `None` uniquely means outside-contract. A distinct outside-contract sentinel would be machinery guarding against a state that can no longer occur. Refused as over-engineering.

**Constraints.** The check is `isinstance(feature, str) and feature`. Fixtures (data-carrying, in the ok+persona-match state): `feature: null` → exit 2, cause token, red at base; `feature: ""` → same (cheap, and it is the only other shape the check names); **omitted feature → a characterization row asserting the dispatch keeps its base outcome with placement `"legacy"`** (green at base and pin — it pins the producer default so the wrong "omitted = refuse" expectation cannot creep in later). `inflight_registry.py` stays byte-identical. New red rows get `predicted_red` lines and QA reproduces them at base; append a new Pin run block per T-01 Step 4's re-run rule.

## OQ-2 — cause token

**Authority.** DEC-258's five states (DECISIONS.md:8700-8712); SC-02's token list (BRIEF.md:73-76); the rework budget.

**Ruling. Reuse `unreadable`. No sixth token.** The remedy class is identical — the registry *file* holds an ill-formed record; the operator repairs that file in place and never deletes it — and the token exists for programmatic classification, not forensic precision; the detail line carries the precision ("the live claim bound to `<id>` in `<root>` names no feature"). A sixth token would amend DEC-258's enumeration, SC-02's token list, and the test matrix's token assertions, buying only a sharper label within the same remedy — bad trade inside 2 rounds / 90 min.

**Constraints.** The refusal goes through `_refuse_placement(agent_id, "unreadable", <detail naming the root and the shape>, <repair-in-place remedy>)`, so the Inspect line prints automatically. Honest record: amend DEC-258's `unreadable` bullet with one clause — "also raised by the guard for an ok claim whose feature is not a non-empty string (a malformed claim row)". I signed DEC-258 under delegation and rule this amendment now. The index ruling (post-`::` prose) is untouched; regenerate anchors per T-02's own rule; the DECISIONS.md edit re-triggers T-02's terminal gate.

## OQ-1 — the printed commands (blocking) — **approve the amendment, this round**

**Authority.** The signed T-01 Step 3(ii) text (plan.yaml:258-272, read verbatim); the t02-wording precedent: deviations from signed intent go through `plan-merge.py record-amendments`, never `amend`, never a silent edit.

**Gap.** Verified at source: the Inspect line is `"--root %s. A governed lead's..."` — the period adjoins the real path, unquoted, bare script name (dispatch-guard.py:783-787); the persona-mismatch remedy prints `--root %s, then re-dispatch` (:812-813); the ambiguous remedy embeds the bare script twice (:762-769). `inflight_registry.py` is not on PATH, so the command as printed either fails or — worse, with a stray `.`/`,` glued to `--root` — targets a nonexistent or wrong registry path. And "never the declared one" over-claims: QA measured that a lead placed in a *non-distill* run claims in the declared feature, by design.

**Ruling. Yes — amend T-01.intent via `record-amendments` and fix in this round**, one amendment batch covering both this wording and the new (i′) feature-validity clause from must_fix 1. Exact replacement rules:

1. **Resolvable script.** Print `python3 %s` where `%s` is the real sibling path, computed once as `Path(__file__).resolve().parent / "inflight_registry.py"` — never the bare name, never a `<bin>` placeholder.
2. **Shell-quote every interpolated runtime value** (agent_id, feature, root) in a printed command with `shlex.quote` — not naive single quotes, so embedded quotes and spaces survive.
3. **No prose punctuation adjacent to a command.** Each printed command ends its line; introducing prose ends with `:` on the preceding line (e.g. "…release it in its own registry, then re-dispatch:" ⏎ four-space-indented command). The Inspect block becomes: `  Inspect:` ⏎ indented command line ⏎ the contract sentence on its own line.
4. **Narrowed sentence**, replacing the over-claim: *"A governed lead's dispatch is placed by its own runtime claim (DEC-258); a placement that cannot be established is refused, never silently rebound to the declared feature."* This echoes DEC-258's signed wording and claims nothing about where a successful non-distill placement's claim lands.

**Constraints.** Only two assertion sites couple to this text — `find-run --agent-id <id>` (test-dispatch-guard.py:1929) and `("list --root", "release --agent-id <id> --feature")` (:1913). `shlex.quote` leaves safe tokens like the fixture ids bare, so these fragments should survive verbatim; the builder confirms rather than assumes, and updates those two sites only if quoting changes them. BRIEF SC-02's required `find-run --agent-id <id>` substring must remain.

## OQ-3 — the plan route's second registered-run read

**Authority.** DEC-258 rule 2 ("the route and the **distill preflight** consume one dispatch-local answer", DECISIONS.md:8731-8733); the signed T-01 freeze list ("Leave these unchanged: `_start_preflight`, …").

**Ruling. The lead's non-gating stands; the code-reviewer's "med, gating" is overruled.** Verified at source: the second read is `_reader_preflight` → `_registered_digest` (dispatch-guard.py:684,:655) — BUG-2110 base behaviour the spec explicitly froze. What DEC-258 forbids is the route and the *distill preflight* seeing different run state, and they cannot: both consume the one memoized `_placed_distill_feature`. The reader preflight's independent read gates plan-pending status and fails closed on divergence. "Fixing" it would modify frozen base behaviour mid-fix-round for a race that was traced, never timed — scope expansion. If anyone wants the reads unified, that is a standalone ticket, not this feature.

## OQ-4 — ordering row and the low test-strength gaps

**Authority.** My signoff build-time constraint 5 (`_dispatcher_placement()` once, after `_direct_orchestration_refusal()`, before `_start_preflight()`); DEC-258's "before any other preflight and before any claim".

**Ruling. Ordering row: in.** A signed, contracted ordering with a surviving mutant (g, 397/397) is a constraint without a witness. It is cheap and lives in the file already being edited. Shape: a fixture where placement fails *and* the registered-run preflight would also refuse — assert stderr names the placement cause, not the run refusal; move `_dispatcher_placement` after `_start_preflight` and the row goes red. **The two low gaps: out.** The exit-tied-to-refusal rows (QA F-4) and case 41's never-ran-vs-swallowed discrimination are advisory, have no surviving mutant behind them, and the second needs call-counting instrumentation. Neither earns space in a 2-round budget; they go to the follow-up list, unticketed.

---

## Fix-round scope (exact)

**Files.**
- `.claude/skills/harness/bin/dispatch-guard.py` — the non-empty-str feature check inside `_lookup_placement` (after ok, before persona); the three printed-command rewrites (Inspect block, persona-mismatch remedy, ambiguous remedy) per rules 1-4.
- `tests/integration/test-dispatch-guard.py` — rows: null-feature (red at base), empty-string-feature (red at base), omitted-feature→`"legacy"` characterization (green both), ordering row killing mutant g (red under the mutant); the two wording-coupled assertion sites confirmed or minimally updated.
- `plan.yaml` — one `record-amendments` batch on T-01.intent: the (i′) feature-validity refusal and the Step 3(ii) wording rules.
- `DECISIONS.md` — one clause added to DEC-258's `unreadable` bullet; `DECISIONS-INDEX.md` regenerated (ruling prose unchanged).
- `notes/characterization-pin.md` — `predicted_red` lines for the new red rows; new Pin run block at the fix commit.

**Out of scope:** `inflight_registry.py` (byte-identity holds), `_reader_preflight`/read unification, F-4 exit-tying, case-41 discrimination, any sentinel object.

## Re-validation scope

**Targeted, delta-scoped, all five readers** — each verifies only its own finding's closure, no re-review of unchanged substance: **qa** re-runs the four suites, reproduces base-red for the new rows, checks the new Pin block, equality gate, and `inflight_registry.py` byte-identity; **code** and **security** verify the fail-open is closed at the new source lines; **ui** copy-runs each printed command verbatim against a path-with-spaces fixture root; **goalcheck** re-grades only SC-02 (partial→met) and SC-04's evidence line (DEC-258 body now accurate for the null shape). SC-01/SC-03/SC-05 stand on existing evidence except SC-03's seam diff, which re-runs mechanically against the new pin.

## Budget

**Yes — this consumes round 1 of 2** (rework clock runs from the fix dispatch; the scope above fits well inside 90 minutes). Exhaustion returns to the operator per signoff constraint 11.
