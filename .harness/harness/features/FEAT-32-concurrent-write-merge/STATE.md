# STATE — FEAT-32-concurrent-write-merge

## Current

Phase: **plan**, at its terminus. The Q3 amend round is **committed at `f6840d0`** on `feat/FEAT-32`
(HEAD was `62f861c`). `approval.status` is `pending` in `plan.yaml` and `## Approval` is `pending` in
`BRIEF.md` — **both byte-identical to the previous commit, verified by `diff` against `git show HEAD:`
immediately before staging**, not asserted. Nothing here signs.

**Q1 CLOSED.** `git merge-base --is-ancestor` returns true for `16b30c6` (DEC-90 strike), `1d2b036`
(DEC-197) and `47a9935`. Highest decision in this checkout is **197** in both `DECISIONS.md` and
`DECISIONS-INDEX.md`, so T-13 mints 198 and the duplicate hazard is gone. T-13 needed no edit — its
intent already reads the file rather than assuming a number; its DEC-90 degraded path is now inert.

**Q3 APPLIED: `main_session.writes` is the gate's INPUT, not a record.** T-14 no longer hardcodes a
plan.yaml regex; it sources the denial from the list. Host is `check-domain.sh`, not the merge tool,
and the ruling's own premise was falsified before choosing: `plan-merge.py` **does not exist yet**
(only `expertise-merge.py` of the five is on disk) and is a tool the writer CHOOSES to invoke, so a
check inside it is refusable by not calling it. `check-domain.sh` already opens `team-config.yaml`
(`:153-155`, `:297-302`), a `Write` carries whole-file `content` (`:1034`), and
`grep -n main_session check-domain.sh` returns **zero**. The chosen SHAPE survives; only its HOST
argument did not.

**The scope consequence, named: the hole was three files wide.** `team-config.yaml:89`/`:90` grant pm
`BRIEF.md` and `PLAN.md` whole with `except ## Approval` as a **comment**, so pm writing
`status: approved` into a BRIEF is unrefused at `62f861c`. One list-sourced mechanism closes all
three; refusing to generalise would hardcode a plan.yaml special case out of a list whose other two
entries state the same rule.

**The signer spread was FOUR-way, not three, and the tree behaves as none of them.**
`SKILL.md:34-35` (main session) was the only artifact already correct; `templates/plan.yaml:25-26`
names the ORCHESTRATOR and miscites DEC-120, which says the opposite; `harness-pm.md:27-28` names the
orchestrator "because only it can reach the user"; `team-config.yaml:91` miscites DEC-129. Authority:
DEC-120 `@2408`, sentence `:2431`; DEC-112 `:1931` corroborates. T-15 corrects the three losers.

**Ruling-by-ruling, verified against the artifact.** Q5 — `dec:` on D-04 (`:156`) and D-10 (`:324`)
now DEC-120; DEC-129 `@2954` has **zero** "approval" occurrences. pm found **four** DEC-129 hits in
`team-config.yaml`, not three: `:89`/`:90`/`:91` wrong, **`:108` correct**, and its own first-draft
blanket assertion would have failed on the correct line. Q6 — the six out-of-scope files appear
**nowhere** in `plan.yaml`; T-10 carries `OUT OF SCOPE - SEE ISSUE #639` at `:1357` and registers
exactly two, so a search for one of the six lands on the issue that owns it. Q7 — SC-14 re-observed
at `62f861c`: unit exit 0 / **179** metric lines / 0 beginning `FAIL`; integration exit 0 / **221** /
0 beginning `FAIL` / **3 containing `ERROR`**. Integration moved 93 → 221 (FEAT-30 added to
`INTEGRATION_SCRIPTS`); unit unchanged from `5d9b428`. Exit-0-plus-no-`FAIL` stays the mechanical
gate, counts are the shrink detector. Q8 — T-16 fixes `validate-digest.py:580`'s citation of `:838`
(statement at `:845`) and its **verify re-derives the line rather than pinning a literal**. Q9 — T-17
carries verbatim DEC-174 am.4 wording adding `dispatch-guard.sh`; enumeration `:4859-4860`, "the
category decides, the list records" `:4860-4862`; changes no lane. Q10 — **absent, zero cost**:
`grep -n phase` on `templates/plan.yaml` returns nothing. Q4/Q11 accepted as ruled.

**REQ-11 did not cover the generalisation, and pm caught it.** `BRIEF.md:64` read "a feature PLAN's
approval block"; a BRIEF is not a plan, so T-14 would have exceeded its traced source. REQ-11's noun
widened, **SC-20** added at `BRIEF.md:397`. Build order: T-14 `depends_on: [T-03, T-15]`, T-15 `[]` —
T-15 supplies the entry and T-14's new case reads the **real** `team-config.yaml`, so CI notices a
deletion. No cycle.

**#551 OCCURRENCE 8 HAPPENED THIS ROUND, IN ITS STRONGEST FORM.** The lead was forced to a terminal
close with pm in flight, one run after occurrence 7, on the feature that exists to fix this. Its
report: the contract validator then **REJECTED a return that declined to grade an unobservable
child** — so the mechanism does not merely PERMIT a false verdict, it **DEMANDS** one. Two further
details: the lead wrote into **`runs/2026-08-21-2-product/`** instead of minting run-3, so that file
holds ROUND 3's digest under ROUND 2's id and round 2's digest is **lost** (`runs/**` is gitignored,
`.gitignore:7`) — which is precisely why this file and `feature.json` are the durable record. pm ran
to completion as an orphan and returned PASS. Occurrence 7 is now recorded in four places: `BRIEF.md`'s
#551 block ("six" → "seven"), D-06's `because:`, T-13 intent item 4, and **D-09's `choice:`**, which
had reasoned from 3–6 while its best datum sat unrecorded.

**Verified directly, because a forced-close round is where a digest must not be trusted.** `safe_load`
clean; **17 tasks** (T-01..T-17), **10 decisions**; 9 `main-session-direct` / 8 `team`;
`check-plan-routes.py` on this plan exits **0**, **0 VIOLATION, 6 DEVIATION** — T-01, T-07, T-08,
T-09, T-14 and new T-16, each the deliberate DEC-174 shape under DEC-179 (5 before this round).
Scoping the route check to one plan makes every line attributable and removes the enumeration P-05
needed last round. `check-state.sh` exits 1 with FEAT-32's sole violation being "BRIEF.md is NOT
approved" — the terminus. Suites green at `62f861c` independently of pm: `test-check-domain.py` exit 0
with **167** `ok` cases (the baseline T-14's "every prior case still passes" is measured against, and
a number the plan should carry), `test-validate-digest.py` exit 0, unit exit 0, integration exit 0.

`cycles_used` **0** of 10 (lead reported zero send-backs; a forced close is not rework — charging it
would hide the defect, DEC-157/rule 15). Runs **3** of 20.

**An orchestrator error, recorded because rule 15 applies to me.** I spawned a **second product-lead
by mistake** in the feature about concurrent writes — reached for `Agent` when I meant to continue the
live lead, and `SendMessage` proved **disabled for this session entirely**. Contained only because the
accidental dispatch carried a no-op instruction: PASS, 0 tool uses, 0 members, `files_touched: []`,
wrote nothing. The consequence: **a dispatch is unrecallable at send time here**, so two wrong anchors
I handed down (DEC-119 for the fail-open precedent; the operator's `templates/plan.yaml:25`) could only
be fixed by pm re-deriving them, which it did.

## Open Questions

- Q1 **BLOCKING — T-14's Edit rule is bypassable by the most obvious route.** `plan.yaml:1652-1656`
  decides an `Edit` by a TEXT HEURISTIC: deny when `old_string`/`new_string` holds a line whose first
  non-space text is the fragment. An Edit of `  status: pending` → `  status: approved` contains no
  `approval:` and no `## Approval` line, so it is **ALLOWED** and it flips the signature. Worse,
  `status: pending` is every TASK's own field, so the heuristic cannot tell the approval block's
  `status:` from a task's without applying the edit. Two fixes, no free option: **(a)** apply the edit
  in memory (honouring `replace_all`), parse, compare — exact, but contradicts `check-domain.sh:1039`'s
  recorded refusal to reconstruct Edit semantics ("no `replace_all` semantics, no TOCTOU window");
  **(b)** deny a governed agent's `Edit` of any fragment-bearing file outright — fails closed on the
  tool whose proposal cannot be evaluated, and the main session is untouched because a payload with no
  `agent_type` never reaches the domain phase, so D-04's Edit-based signing survives. (b) costs
  `Edit` on `plan.yaml` (near-zero; every other write already routes through `plan-merge.py`) and on
  `BRIEF.md` (real; pm edits it in place today). **pm's to fix — one more amend before signing.**
- Q2 **BLOCKING.** Sign or amend both artifacts. `BRIEF.md` changed again — REQ-11 widened, SC-20
  added, on top of last round's REQ-11/REQ-12/SC-17/SC-18/SC-19 and SC-16's withdrawal.
- Q3 **NOT blocking.** T-14 grew from one file to three. A consequence of sourcing from the list, not
  an independent widening — but the real cost, better seen at signature than discovered at build.
- Q4 **NOT blocking.** T-17 amends a signed decision; approving this plan IS the signature on that
  wording. A stronger justification exists: `dispatch-guard.sh` is a registered PreToolUse hook at
  `.claude/settings.json:45` alongside `check-domain.sh` (`:23`, `:56`), `bash-write-guard.sh` (`:36`)
  and `validate-digest.py --hook` (`:67`) — **every other registered hook is already in am.4's list;
  it is the only one absent** — and it has **no test file at all**, while am.4's rule includes "the
  test file of each". T-07 creates the test; T-17 closes the record.
- Q5 **NOT blocking.** SC-14's baseline records **3 integration lines containing `ERROR`**. The
  criterion binds no line BEGINNING `FAIL` and cannot see them. pm reads all three as expected-output
  cases carrying the word inside a test's own name; whether they should gate is unresolved.
- Q6 **NOT blocking, main session's act.** #551 needs occurrences 7 AND 8 appended, with both
  sharpened claims, plus the run-id collision. An agent composing a GitHub post is forbidden
  (DEC-138 am.6) and `gh-sync.py` has no subcommand for it.
