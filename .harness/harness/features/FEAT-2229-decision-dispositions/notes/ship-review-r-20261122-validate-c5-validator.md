# FEAT-2229 Decision dispositions — ship briefing (after validate c5, pin c163d5ea)

**Bottom line: the feature is done on the merits and ready for your ship call, with one decision to make first.** All seven success criteria and the DEC-188 amendment are graded met at pin `c163d5ea`; the operator-authorized fix-c4 round closed the last two test gaps (M6/M8) and SEC-C4-01, each red-first then green and independently reproduced by qa. Validate c5 nonetheless returned **BLOCKED**, not PASS, because the security reviewer could not execute its planned actual-CLI controls — its Bash grant covers `git diff` only, so the host guard refused the fixture command before a single observation ran. That is a capability blocker in the harness, not a product defect: no must_fix was raised by any reader. The orchestrator, which holds a shell, executed the same classes of control (325 observations through the real CLI, no bypass found — `notes/sec-c5-orchestrator-probe.md`). **Decision needed (Q1 below): accept that evidence as the security runtime closure and ship, or grant the security reviewer an execution path and re-run over a new pin.** Recommendation: accept and ship.

No report round was spawned (DEC-69). This briefing is assembled from the digests at `runs/r-20261121-plan-product/digest.md`, `runs/r-20261121-simplify-eng/digest.md`, `runs/r-20261121-plan-c2-product/digest.md`, `runs/r-20261121-t03-product/digest.md`, `runs/r-20261121-simplify-build-eng/digest.md`, `runs/r-20261121-validate-validator/digest.md`, `runs/r-20261121-validate-c2-validator/digest.md`, `runs/r-20261121-validate-c3-validator/digest.md`, `runs/r-20261121-validate-c4-validator/digest.md`, `runs/r-20261122-validate-c5-validator/digest.md`, plus the c5 reader notes (`notes/review-harness-*-c5.md`, `notes/research-FEAT-2229-decision-dispositions-goalcheck-validate-c5.md`), the main session's `notes/receipt-main-session-T-01-T-02.md` / `notes/red-first-T-01.md` / `notes/red-first-T-02.md` (T-01/T-02 were main-session-direct by the signed plan), and the operator rulings in `notes/answers-2026-11-21-signoff.md`, `notes/answers-2026-11-21-f3i-ruling.md`, `notes/answers-2026-11-22-c4-ruling.md`.

## Done when — by perspective, graded (validate c5 goal-check)

| perspective (as signed) | verdict | discharged by | evidence |
|---|---|---|---|
| **operator** — I can see what a proposed change does to existing decisions before I sign it. Validate cannot call that change delivered while a promised decision edit is missing, and older work is not retroactively invalidated. | met | SC-01, SC-03, SC-05, DEC-188 (T-01/T-02/T-03) | `notes/research-FEAT-2229-decision-dispositions-goalcheck-validate-c5.md` §Perspectives; SC-01/03 via `notes/review-harness-qa-c4.md` (unit 40/40, base red 13/40; era/provenance base red), retained — c163d5ea touches no schema, writer, era or provenance path |
| **reader** — I can distinguish a mechanically malformed declaration from an incomplete or unjustified one. I can judge a proposed strike against the actual decision and route an unlanded promise to the task responsible for it. | met | SC-02, SC-04, SC-05 (T-01) | SC-02 at c163d5ea: `notes/review-harness-qa-c5.md` — M6 both directions red 128/130, each 129/130; M8 red 129/130; pre-fix identifier matcher red 122/130; pin green 130/130; T-01 verify, unit (62 files) and integration (89 files) runners exit 0 |
| **code maintainer** — I have one disposition record and one drafting check, integrated with the existing plan writer and goal-check rather than a parallel decision-audit system. The boundaries and regressions are explicit enough to change safely. | met | SC-06, SC-07 (T-02/T-03) | `46d0c4bc:.harness/harness/docs/DECISIONS.md:5313-5336,8253-8326` (DEC-188 amended, DEC-254 recorded); SC-07 team regressions green with base red (`notes/review-harness-qa-c4.md`); code-grade `--base dfa52536 --head c163d5ea` exit 0, 101 passing records (`notes/review-harness-code-reviewer-c5.md`) |

All eight rows of the goal-check's SC table (SC-01…SC-07, DEC-188) read `met`; the c5 note states per SC whether the c163d5ea delta touches its subject (only SC-02's) and retains c4 evidence by pointer for the rest.

## What each squad delivered

- **Product — plan (c1 FAIL → c2 PASS).** `runs/r-20261121-plan-product/digest.md`: the pending plan was complete and the plan goal-check passed, but the original scope failed the panel (a high substance finding on T-01). `runs/r-20261121-plan-c2-product/digest.md`: cycle 2 closed it; architecture and plan readers passed; plan returned `pending` and was signed by you on 2026-11-21 (`notes/answers-2026-11-21-signoff.md`, rework ruling 3 rounds / 90 min).
- **Engineering — SIMPLIFY twice, flag-only.** `runs/r-20261121-simplify-eng/digest.md` (plan-side) and `runs/r-20261121-simplify-build-eng/digest.md` (build-side): four-angle passes, no source edits, two non-blocking briefing rows (B-1, B-2 below). No amendments.
- **Product — T-03.** `runs/r-20261121-t03-product/digest.md`: DEC-254 recorded, DEC-188 amended, SPEC integrated by the documentor.
- **Main session — T-01, T-02 (main-session-direct by the signed plan).** `notes/receipt-main-session-T-01-T-02.md`, `notes/red-first-T-01.md`, `notes/red-first-T-02.md`: the disposition record, loader/writer and `plan-merge.py check` gate, each red-first. Fix rounds c2/c3/c4 also landed here (`8cf1d93f`, `ef269da2`, `c163d5ea`).
- **Validator — five validate cycles.** c1 `runs/r-20261121-validate-validator/digest.md` FAIL (T-01 creation/section defects, T-02); c2 `runs/r-20261121-validate-c2-validator/digest.md` FAIL (SC-02 own-section selection, F3 suffix); c3 `runs/r-20261121-validate-c3-validator/digest.md` FAIL (F3-I over-indented fence closer); c4 `runs/r-20261121-validate-c4-validator/digest.md` ESCALATE (F3-I production-closed, every SC met, two test-only gaps M6/M8 with the rework ruling spent — your c4 ruling authorized one more round); c5 `runs/r-20261122-validate-c5-validator/digest.md` BLOCKED: qa PASS, code PASS, ui PASS (declined, no UI surface across 57 changed paths), goal-check PASS, security BLOCKED on execution capability (`notes/review-harness-security-reviewer-c5.md`: static closure of SEC-C4-01 by inspection, zero of 107 planned CLI observations executed, guard refusal confirmed).

## Open questions

- **Q1 (blocking).** Security runtime acceptance for SEC-C4-01: the reader's static review finds the fix correct and raises no must_fix, qa reproduced the identifier spoof red-first through the actual CLI, and the orchestrator executed 325 actual-CLI controls over the reader's planned classes with no bypass (`notes/sec-c5-orchestrator-probe.md`). Do you (a) accept that as closure and proceed to ship, or (b) grant the security reviewer an execution path (its Bash grant is `git diff` only) and re-run over a new pin? **Recommendation: (a).** Note on (b): SC-13 forbids a second reader run over c163d5ea, so it needs a new pin, and the fix in the reviewer's grant is a harness change outside this feature.
- The reader's capability gap itself (a security reviewer required to run actual-CLI controls with no execution grant) is listed as backlog row B-9; it belongs to the harness, not this feature.

## Resolved escalations

- c4 → operator: M6/M8 test-only gaps with the ruling spent → `notes/answers-2026-11-22-c4-ruling.md` authorized one round (tilde tests + SEC-C4-01), landed as `c163d5ea`, judged at c5.
- c3 → operator: F3-I CommonMark fence/heading class → `notes/answers-2026-11-21-f3i-ruling.md`, landed as `ef269da2`, judged at c4.
- No lateral escalations between squads.

## Spend and ledger

`feature-record.py spend` at c5 close: 10 runs, 126 min wall, 596 244 tokens; rework window 74 min / 3 rounds (ruling 90 min / 3 rounds, plus one round authorized beyond it by the c4 ruling). Cycles 4 of 10 (c2: 1, c4: 1, c5: 2 — the c5 count is two same-run receipt corrections the lead reported, not product rework). Runs 10 of the informational 20. Judgements: 16 (1 mission, 4 regate, 5 continue, 6 succession, 0 amendment). The c5 succession judgement landed 16 s after its run-start because the first attempt exceeded the reason cap — recorded as it happened, not back-dated.

## Amendments (DEC-229)

| at | decision | reason | overruled |
|---|---|---|---|
| — | — | the build amended no signed task text | — |

overrule rate: 0/0

## UAT

Not required: no `verify: uat` criterion in BRIEF.md; the surfaces are a CLI gate, a plan record and documentation.

## Proposed backlog — strike rows by ID; unstruck rows become issues on ship acceptance (DEC-138)

| ID | nature | item | source |
|---|---|---|---|
| B-1 | chore | Index-row grammar has three spellings (`plan_merge/check.py:200,263`, `check-plan-routes.py:2394-2408`, `gen-decisions-index.py:75-86`); the lowercase-aware STRUCK predicate differs from the older route reader's uppercase-only one — consolidate to one reader | `runs/r-20261121-simplify-build-eng/digest.md` B-1 |
| B-2 | chore | Shape/check/era/landing contracts recur across `SPEC.md:2009-2031,2287-2302`, DEC-188 and DEC-254; keep the detail in DEC-254 and reduce the others to summaries plus links | same digest, B-2 |
| B-3 | bug | `plan-merge.py check` reports `create: true` files as "already exists" on landed plans | `notes/handoff-validate-c3.md` (carried from simplify) |
| B-4 | bug | Scanner vs CommonMark: Unicode line-break/whitespace mismatch lets a CLI-reproduced spoof heading resolve (absent in the live corpus) | `notes/review-harness-qa-c4.md`; confirmed backlog by your Q2 |
| B-5 | bug | Fences inside list containers create phantom fence state (CLI-reproduced; absent in the live corpus) | same; confirmed backlog by your Q2 |
| B-6 | bug (harness) | C4-QA-CONTRACT: the qa digest validator refuses FAIL for mandatory coverage gaps while the suite and matrix are green, so a qa receipt must say PASS or ESCALATE | `runs/r-20261121-validate-c4-validator/digest.md`; confirmed backlog by your Q2 |
| B-7 | enhancement | T-01/SC-02 tilde closer-length rule has no regression case (mutants X2/X5/X6 survive 130/130; backtick leg covered) | `notes/review-harness-qa-c5.md` Gap A |
| B-8 | enhancement | T-01/SC-02 tilde closer-with-info-string rule has no regression case (mutant X3 survives 130/130; backtick leg covered) | `notes/review-harness-qa-c5.md` Gap B |
| B-9 | chore (harness) | The security reviewer is asked for actual-CLI controls but holds a `git diff`-only Bash grant; the guard refuses its fixture commands before execution — decide the grant or move such controls to a shell-holding tier by rule | `notes/review-harness-security-reviewer-c5.md` SEC-C5-EXEC |
| B-10 | enhancement | `## DEC-10-` (hyphen at line end) is accepted as DEC-10's heading by `DEC_ID_END`'s `-\s` because the scanner keeps the newline; conformant with the signed comment and no new gain, but worth a stated decision or a trailing-`-` exclusion | `notes/sec-c5-orchestrator-probe.md` |

Nothing else survived collation; everything not listed here is closed.

## Ship mechanics (yours)

Branch `feat/FEAT-2229-decision-dispositions` at `e220cde8`+this briefing commit; pin `c163d5ea`; station `review` on the board (`gh-sync.py status review` run before c5). Nothing has been pushed, no PR opened, nothing merged.
