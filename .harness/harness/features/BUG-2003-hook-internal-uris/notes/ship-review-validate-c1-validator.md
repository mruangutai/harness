# Ship review — BUG-2003-hook-internal-uris

**BLUF: ready to ship.** Validate c1 over `c2170e265c30e36d6252668775ee41a8ebc93fb6` is clean on all five readers (qa, code, security, ui, pm goal-check), `must_fix` empty, `severity_max: none`. Production change is one commit (f9e23bcb, `.omp/extensions/harness-hooks.ts` + its test); the V1 rework (c2170e26) touched the test file only. Merge of `feat/BUG-2003-hook-internal-uris` is yours.

No report round was spawned. Assembled from disk: `runs/plan-product/digest.md`, `runs/2026-10-03-validate-validator/digest.md` (c0, FAIL), `runs/2026-10-03-validate-c1-validator/digest.md` (c1, PASS), `notes/research-BUG-2003-hook-internal-uris-goalcheck-validate-c1.md`, `notes/review-harness-{qa,code-reviewer,security-reviewer,ui-reviewer}-c1.md`.

## Definition of done — graded (validate goal-check c1)

| Perspective (as signed) | Verdict | SCs | Evidence |
|---|---|---|---|
| operator (governed agent): send agent messages and report tooling defects without them being mistaken for checkout-file writes; ordinary file-write permissions and refusals unchanged | met | SC-01, SC-03 | `notes/review-harness-qa-c1.md:5–6,10–21` (107/0 at pin; mixed-target base red reproduced); `tests/unit/omp-hooks.test.ts` :1054 allowed URIs, :1093–1111 mixed edit, :1134–1157 forbidden write, :1159–1171 main-session controls |
| security / harness owner: every other scheme refused by name, never resolved or forwarded; one scheme decision across write/edit, pre/post | met | SC-02, SC-04 | QA c1:10–20 (refused-URI and MV cases, base reds reproduced); `git show c2170e26:.omp/extensions/harness-hooks.ts` :265–347 shared `fileDomain`/`domainTarget` decision; `git diff --stat f9e23bcb c2170e26 -- .omp` empty |
| code maintainer: automated coverage for allowed URIs, refused URIs, real out-of-domain files, write/edit pre/post, mixed edits; fail-first and pass receipts with discriminating cases named | met | SC-05 | QA c1:5–6,10–22 — literal verify `python3 tests/unit/test-omp-hooks.py` 107 pass/0 fail; base-adapter reproduction at 7fba7e1d 103 pass/4 named fails; `notes/receipt-t01-fail-first.txt`, `notes/receipt-t01-pass.txt` |

## Lead summaries

- **product (plan, PASS, 0 cycles)** — `runs/plan-product/digest.md`: patch intake, one task T-01 (main-session-direct under DEC-174, `execution_agent` harness-backend-dev), five SCs, approval signed 2026-10-03 with rework ruling 1 round / 45 min (`notes/rework-ruling-2026-10-03.md`).
- **validator c0 (FAIL, over 85038f8c)** — `runs/2026-10-03-validate-validator/digest.md`: SC-01/02/04/05 met; V1 (substance, med, T-01) — SC-03 preservation controls absent from the test file. No runtime defect alleged. Fixed main-session-direct at c2170e26 (tests only).
- **validator c1 (PASS, over c2170e26)** — `runs/2026-10-03-validate-c1-validator/digest.md`: V1 closed; code review reached and passed its quality stage (never entered at c0); security static audit clean; ui self-scoped out (13 changed objects, no UI surface); goal-check all three perspectives met. The lead reports one internal send-back (goal-check initially BLOCKED pending QA execution evidence, resolved on the same pin) — counted as 1 cycle.

## Open questions

None blocking. Q1 from c0 is carried as backlog B-1 below (host behaviour that this very patch fixes once merged).

## Escalations

None.

## Spend and ledger

`feature-record.py spend`: runs 3, wall-clock 35 min, tokens 122,978, rework_minutes 23 of the 45-minute ruling. `cycles_used` 2 / 10 (1 attributed to the c0 FAIL routed back for the main-session-direct fix; 1 lead-reported send-back inside c1). Judgements: 4 (`mission: patch`, `continue`, `regate: continue`, `continue`). `len(runs)` 3 — under `max_total_runs`.

Ledger note: recording the c0 cycle re-closed run `validate-validator` via `run-end`, which rewrote its `ended_at` (04:00:25 → 04:05:47 UTC); verdict, tokens and the original digest are unchanged.

## Amendments

| at | decision | reason | overruled |
|---|---|---|---|
| — | — | no `amendment` judgements; T-01 was main-session-direct, no builder amended signed text | — |

overrule rate: 0/0

## UAT

Not required (BRIEF `## Verification gaps`: none; unit kind covers the surface).

## Proposed backlog

| ID | Nature | Finding |
|---|---|---|
| B-1 | chore | c0 Q1: readers inside the validate runs still had `agent://` and `xd://report_issue` routed to check-domain because the main checkout's unpatched hook governs subagents (G-15); the c0 security note therefore keeps an undeclared `reviewed` key (`notes/review-harness-security-reviewer-c0.md`). Self-resolving on merge of this patch; reconcile the c0 note's shape or accept as historical. |
| B-2 | enhancement | QA c1 advisory (`notes/review-harness-qa-c1.md`): the main-session controls assert zero domain-check calls rather than enumerating all runner calls; a stronger control would assert the full runner-call set. Non-blocking — the signed scope preserves file-domain behaviour, not blanket suppression. |
| B-3 | chore | Harness: `dispatch-guard` reads `HARNESS-FEATURE` from the task text only; a dispatch carrying it solely in the shared `context` block is refused as absent (observed twice this feature). Document or widen. |
| B-4 | chore | Harness: `observations-merge.py apply` does not create the `observations/` directory; the first append on a fresh feature fails at the lock-file open. |
| B-5 | chore | Harness: `gh-sync.py status review` refuses while a task station is still `review`, and a station write after the pin trips INV-33 — the ordering (task done + feature station, seam commit, then pin) is undocumented in `build-phase.md`. |
