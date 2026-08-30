# Handoff — FEAT-38, plan → build — written at 99bb52c, seq-1

## Next

**Nothing dispatches until the operator signs.** The amended BRIEF and plan are drafted,
reviewed and simplify-flagged; the phase exits at the user gate. The main session must first
RESET both approval fragments to `pending` — `plan.yaml:6-9` and `BRIEF.md`'s `## Approval` —
because no agent in this flow may write them (DEC-120), then take the one fresh signature.
After the signature: `gh-sync.py status <feature-dir> Ready`, then `gh-sync.py open` to mint
sub-issues for T-24, T-25, T-27, T-28, T-29 (none is attached yet), then the eng segment in
plan order T-27 → T-24 → T-25 / T-28, with T-29 after T-24.

## Trust

- Amended plan passes the route gate: 28 tasks, 0 violations, exit 0 — `check-plan-routes.py
  <feature-dir>/plan.yaml` — verified-at 99bb52c by me. The two `DEVIATION` lines on T-22/T-23
  are pre-existing and predate this amendment.
- Both approval fragments are byte-untouched — `git diff -U0` over both files shows no changed
  line inside either block — verified-at 99bb52c by me.
- The three held `verify:` corrections are in the plan: T-10 at `plan.yaml:877`, T-15 at
  `:1214`, T-19 at `:1425` with the `^KIND-DRIFT:` anchor kept verbatim — verified-at 99bb52c
  by me against `notes/research-verify-block-defects.md`.
- The removal order is measured, not reasoned. The three-step order took the whole suite to
  exit 2 across the interval via the MISCONFIGURED detector at `run-unit-tests.sh:60-74`;
  T-24 now merges the array edit and both deletions into one step — probe receipt
  `notes/receipt-harness-backend-dev-2026-08-29-21-eng-drift-probe.md` — verified-at 99bb52c
  by harness-backend-dev in a disposable /tmp copy, NOT re-run by me.
- T-24's `git grep -l check-decision-claims` sweep can be clean at its own completion: the only
  two occurrences in `DECISIONS.md` are the markers at `:6290-6291`, and T-24 depends on T-27
  which removes all eleven — verified-at 99bb52c by me.
- `review_sha` still reads `48bbe7e`. It is STALE — it pins the superseded validate phase.
  Re-pin before any validator run (INV-6). UNVERIFIED for any purpose beyond its own history.

## Dead ends

- The declarative `contains`/`max_lines` redesign in `notes/replan-remove-command-execution.md`
  is REJECTED by the operator — grilling artifact `.harness/notes/grilling-remove-executable-
  claims-2026-08-29.md`, `## Out of scope`. Do not revive it.
- `check-decision-anchors.py` / T-17 is RETAINED UNCHANGED. Its argv is a fixed
  `["git","ls-files"]` literal at `check-decision-anchors.py:111`; not in the risk class —
  grilling artifact, `## Facts I verified`.
- Backlog rows B-8 and B-11 are MOOT and B-10 SUPERSEDED — `STATE.md`, ruling 3. Do not
  implement then delete.
- T-26 is RETIRED into T-24 and its number is never reused — `plan.yaml:1792-1794`.

## Working set

- `.harness/harness/features/FEAT-38-decisions-current-knowledge/BRIEF.md`
- `.harness/harness/features/FEAT-38-decisions-current-knowledge/plan.yaml`
- `.harness/harness/features/FEAT-38-decisions-current-knowledge/STATE.md`
- `.harness/notes/grilling-remove-executable-claims-2026-08-29.md`
- `.harness/harness/features/FEAT-38-decisions-current-knowledge/runs/replan-simplify-eng/digest.md`
