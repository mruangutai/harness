# Review — FEAT-07 verify-teeth-batch-probe — c0

Tree confirmed: `git rev-parse HEAD` = `29b612e398d6651964e9d4626ed8070c5ab7bd7d` on
`feat/FEAT-07-verify-teeth-batch-probe`. Diffed `main..29b612e`. No `[harness:human]` commits in range.

## VERDICT: FAIL — one must_fix (med), Stage 1

**DEC-174 note, carried verbatim: this review does NOT discharge DEC-174.** Its compensating control
for `validate-digest.py` is a human — the CTO — reading the diff; that has not happened. My FAIL below
is a separate defect in a different file, not on the DEC-174 list.

## Stage 1 — spec compliance

**must_fix — mismatch, `ref: D-06`, `path: .claude/skills/harness-digest-dev/SKILL.md`.** SC-16
requires the REQ-08 receipt clause "stated on exactly one surface"; D-06 places it in
`harness-tdd-enforcement/SKILL.md`, "one copy, and nowhere else." Commit `4e2b57f`
(`[harness:t-04][harness:t-02]`) puts it in both files:
- `harness-tdd-enforcement/SKILL.md:97-104` — correct, matches D-06.
- `harness-digest-dev/SKILL.md:50-54` — a second copy: "Your B-7 receipt carries the command and its
  verbatim output. Paste both into `.harness/features/<FEAT>/notes/receipt-<agent>-<runid>.md>`...
  it makes skipping leave evidence in a file qa and the code reviewer already open... leads hold no
  Bash." Near-verbatim restatement of the `harness-tdd-enforcement` copy. T-02's own `intent:`
  (PLAN.md:590-598) asked only for the verify-before-you-return / cross-check-PLAN paragraph on this
  file — not this one.

The commit message for `4e2b57f` states the opposite of what its own diff does: "The REQ-08 receipt
clause lands in harness-tdd-enforcement rather than harness-digest-dev because that skill reaches
only four of the five specialists" — in the same commit that adds it to `harness-digest-dev` too.
`docs/harness/DECISIONS.md`'s new `## DEC-175` §6 repeats the same false claim ("went into
`harness-tdd-enforcement/SKILL.md`, one copy") as durable history.

**Failure scenario:** a future editor, trusting D-06/DEC-175's "one copy" framing, edits only
`harness-tdd-enforcement/SKILL.md` (e.g. the receipt path or the fabrication caveat). The
`harness-digest-dev/SKILL.md` copy — read by four of the five dev specialists — silently drifts out
of sync and states a contradicted version of the rule. Nothing catches it: T-02's own `verify:`
clause (PLAN.md:636-649) checks only for **presence** of `receipt`/`verbatim` on
`harness-tdd-enforcement` and never for their **absence** on `harness-digest-dev`, unlike every other
duplication risk in this same feature (T-03's `no-task` guard, T-08's `harness-handoff` guard), which
were paired with an absence check per DEC-169. That is the DEC-126/158 inline-drift failure D-06's own
rationale exists to prevent, now present one file over from where the rule says it must be exclusive.

Both copies say the same accurate thing *today* — this is latent drift risk, not current wrong
behaviour — so **severity: med**, not high. `must_fix` non-empty is what gates this FAIL on its own.

### Everything else in Stage 1 checked out
- REQ-01/02/03/09/10/11 and D-01/03/05/07/08 in `validate-digest.py` — see Stage 2.
- SC-11: `d6fa0a8` is the sole commit touching both `validate-digest.py` and `test-validate-digest.py`.
- SC-12: `gen-decisions-index.py --stdout | diff - docs/harness/DECISIONS-INDEX.md` exits 0 against
  the working tree, re-run myself; `DEC-175/176/177` present and correctly anchored.
- `run-unit-tests.sh` from repo root: exit 0, all cases including the FEAT-07 block (57 CLI cases +
  joint-hint case), the SC-15 dev-ops residue fixture, and the D-08 `task: none` regression fixtures.
- T-02/03/05/06/07/08/10 doc surfaces spot-checked against PLAN `intent:`/BRIEF SC by reading the
  diff hunks directly: field spellings, `§2`/`§4` placement in `harness.md`, the literal string
  "before any claim" present on both required surfaces and absent from `harness-handoff/SKILL.md`,
  qa fail-gate annotations on both qa surfaces. All match.
- `bin/check-docs.sh`: "no stale statements found."

Stage 1 completed in full despite the must_fix (rather than stopping) because this dispatch named the
fail-open hunt in `validate-digest.py` as its explicit target and no fix cycle exists for this
advisory-gated step — both stages needed to ship in one pass.

## Stage 2 — fail-open hunt on the four flagged `validate-digest.py` surfaces

All four hold up; no fail-open found. Traced by reading `git show 29b612e:...validate-digest.py` and
exercising the CLI directly.

1. **`CONDITIONAL`/`_unbound` (`:117`, `:119-130`).** `seen.get(gov, "")` — the `""` default is
   present exactly as D-08(iii) requires. A MISSING `task` makes `_unbound` return `False`
   (`str("").lower()` is `""`, not `"none"`), so the requirement BINDS on a missing governor, fail
   closed. Confirmed empirically (`dev omitting task entirely is rejected`). Call sites `:539`
   (releases the requirement) and `:587` (releases only the `n/a`-with-PASS gate, not the
   `pass`/`fail` contradiction) are on the correct sides — confirmed via the
   `task: none + task_verify: fail` fixture, which still rejects.
2. **`re.Pattern` branch (`:642-650`), `TASK_ID_RE` (`:136`).** Uses `fullmatch`, not `search`. It is
   an `elif` in the same chain as the other type branches, so nothing else in that loop (`sorted()`,
   `join()`) ever sees a `re.Pattern` value. `dev task: bogus` rejects (fixture green) — confirms the
   branch is load-bearing, not dead.
3. **`GATE_FAIL_VALUES` type-strict comparison (`:108-110`, check `:614-623`).**
   `val == want and isinstance(val, type(want))`, positioned after both preceding `continue`s, so
   genuinely outside the placeholder branch. `qa matrix_ok: false + PASS` fixture confirms the gate
   *fires* on the boolean. The `0 == False` guard's *non-firing* direction is unexercised by any
   fixture and is unobservable regardless — `allowed is bool` rejects `matrix_ok: 0` in the type
   branch before this code runs — so there is no failure scenario here, not a finding.
4. **Four-branch missing-field hint (`:544-571`) and joint followability (SC-18c).** Traced the
   both-omitted case by hand: `task`'s hint fires unconditionally; `task_verify`'s hint also fires
   (its own `_unbound` check is `False` when `task` is absent, not `"none"`) and carries the
   `CONDITIONAL` escape ("...or omit this field entirely if you wrote `task: none`"). Both licensed
   repairs — `task: none`+omitted, and `task: T-01`+`pass` — validate, confirmed by
   `run_joint_hint_case()` (green) and by re-running both digests through the CLI myself.

**One `low` finding: a stale line-pointer in the honest-limit comment.** The comment at
`validate-digest.py:572-576` reads `# ... a re-prompted return is not re-validated — :691-692 is
"if d.get('stop_hook_active'): return 0"`. At `29b612e` that check is actually at line 838
(`git show 29b612e:.claude/skills/harness/bin/validate-digest.py | grep -n stop_hook_active` →
`:838`, not `:691-692`; `:691` is inside the unrelated lead-roll-up `members: []` check). This
diff inserted ~150 lines above the passthrough without updating the pointer. Low severity — the
passthrough itself is unchanged and still exists — but it is a comment that no longer matches the
code, on the one comment BRIEF insists must not overstate what REQ-11 closes; a reader following the
pointer lands on unrelated code.

## Accepted residue — not reported as defects
- `dev-ops` `suite: fail` + `VERDICT: PASS` stays accepted (D-03), pinned by its named fixture, green.
- `task: none` remains self-declared, exactly as BRIEF `## Verification gaps` states.

Neither looked mis-scoped; no `open_question` raised on either.
