# Handoff — FEAT-38, plan → build — written at 6be3de5, seq-1

Anchors below are CONTENT, not line numbers, deliberately: this feature moved every anchor in
`plan.yaml` twice in one afternoon, and a stale `file:line` in a handoff is the rot the feature
exists to remove.

## Next

**Nothing dispatches until the operator signs.** The amended BRIEF and plan are drafted,
reviewed and simplify-flagged; the phase exits at the user gate. The main session must first
RESET both approval fragments to `pending` — `plan.yaml`'s `approval:` block and `BRIEF.md`'s
`## Approval` — because no agent in this flow may write them (DEC-120), then take the one fresh
signature. After the signature: `gh-sync.py status <feature-dir> Ready`, then `gh-sync.py open`
to mint sub-issues for T-24, T-25, T-27, T-28, T-29 (none is attached yet), then the eng segment
in plan order T-27 → T-24 → T-25 / T-28, with T-29 after T-24.

## Trust

- Amended plan passes the route gate: 28 tasks, 0 violations, exit 0 — `check-plan-routes.py
  <feature-dir>/plan.yaml`, pass the FILE not the directory — verified-at 6be3de5 by me. The two
  `DEVIATION` lines on T-22/T-23 are pre-existing and predate this amendment.
- Both approval fragments are byte-untouched across all three replan commits — `git diff -U0`
  over both files showed no changed line inside either block — verified-at 6be3de5 by me.
- The three held `verify:` corrections are in the plan: T-10's exclusion-list replacement, T-15's
  `check-expertise.sh "$E"`, and T-19's column-0 anchoring — verified-at 6be3de5 by me against
  `notes/research-verify-block-defects.md`. **T-19's is not the signed spelling.** It reads
  `grep -qE '^(KIND-DRIFT|MISCONFIGURED):'` — the anchoring extended to the second detector —
  and T-19's own `intent:` discloses that in full. Read it before assuming the signed text landed.
- The removal order is measured, not reasoned. The three-step order took the whole suite to
  exit 2 across the interval via the MISCONFIGURED detector at `run-unit-tests.sh:60-74`;
  T-24 now merges the array edit and both deletions into one step — probe receipt
  `notes/receipt-harness-backend-dev-2026-08-29-21-eng-drift-probe.md` — verified-at 6be3de5
  by harness-backend-dev in a disposable /tmp copy, NOT re-run by me.
- T-24's `git grep -l check-decision-claims` sweep can be clean at its own completion: the only
  two occurrences in `DECISIONS.md` are the two markers inside DEC-205, and T-24 depends on T-27
  which removes all eleven — verified-at 6be3de5 by me.
- `review_sha` still reads `48bbe7e`. It is STALE — it pins the superseded validate phase.
  Re-pin before any validator run (INV-6). UNVERIFIED for any purpose beyond its own history.
- `check-state.sh` exits 1 here, on nothing this amendment caused: three gitignored digests from
  superseded runs carry no `VERDICT`/`DIGEST`/`artifact` at all and cannot be repaired without
  inventing another agent's verdict, and INV-26 reports 23 cards at Review whose tasks read
  `done` — verified-at 6be3de5 by me.

## Dead ends

- The declarative `contains`/`max_lines` redesign in `notes/replan-remove-command-execution.md`
  is REJECTED by the operator — grilling artifact `.harness/notes/grilling-remove-executable-
  claims-2026-08-29.md`, `## Out of scope`. Do not revive it.
- `check-decision-anchors.py` / T-17 is RETAINED UNCHANGED. Its argv is a fixed
  `["git","ls-files"]` literal; not in the risk class — grilling artifact, `## Facts I verified`.
- Backlog rows B-8 and B-11 are MOOT and B-10 SUPERSEDED — `STATE.md`. Do not implement then
  delete. B-9 is absorbed into the plan as T-29 rather than filed.

## Working set

- `.harness/harness/features/FEAT-38-decisions-current-knowledge/BRIEF.md`
- `.harness/harness/features/FEAT-38-decisions-current-knowledge/plan.yaml`
- `.harness/harness/features/FEAT-38-decisions-current-knowledge/STATE.md`
- `.harness/notes/grilling-remove-executable-claims-2026-08-29.md`
- `.harness/harness/features/FEAT-38-decisions-current-knowledge/runs/replan-simplify-eng/digest.md`
