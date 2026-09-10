# FEAT-104 — strict digest schema — ship review (c11)

**Ship it.** The goal is fully met: 9 of 9 requirements and **all 15 live success criteria** are
satisfied at the pinned review commit `984bd26b`, including **SC-13, which you closed yourself** —
your UAT read of the DEC-174 carve-out diff returned `passed` (`notes/uat.md`). SC-14 was struck
during planning and is absent from the signed BRIEF.

The blocking gate is green (`qa_gate`, both required kinds, exit 0). The reviewer panel is **PASS
with `must_fix: []`**, `severity_max: med` — advisory, not blocking, under
`gates.review: advisory_unless_high`. Nothing outstanding blocks the merge.

**Operator decision: accepted.** The operator selected **Ship all 29** after reviewing this
briefing: accept CF-3, create every unstruck B-1 through B-29 backlog issue, merge, and finalize
the Harness mirror.

- **CF-3 accepted** — `abff2a84` ("FEAT-56-central-onboarding-model: station done at ship", a
  one-line `status: review` → `status: done` flip on another feature's `plan.yaml`) is this
  branch's own root commit and will merge with this PR. It is a benign correction on an
  already-merged feature; excising it would rewrite history beneath the signed review pin.
- **B-1 through B-29 accepted** — every row in the backlog table below becomes a backlog issue.

## Disclosure — how this briefing was assembled

**No report round was spawned.** I read the run records off disk, per DEC-69. Every one of the
**29 digest files across all 28 recorded runs** was opened at least at its fenced `DIGEST:` block;
**read in full**: `runs/2026-09-10-17-panel-validator/digest.md` (the standing panel),
`runs/2026-09-10-18-goalcheck-product/digest.md` (the final goal-check), plus the residual-bearing
sections of `runs/2026-09-09-10-panel-validator/digest.md`,
`runs/2026-09-10-14-panel-validator/digest.md`, `runs/2026-09-10-13-simplify-eng/digest.md` and the
escalation blocks of `runs/2026-09-09-04-panel-validator`, `-05-qa-gate-validator`,
`-09-simplify-eng`, `runs/sigfix-c2-product`, `runs/od5-c3-product`. Also read:
`STATE.md`, `feature.json`, `plan.yaml` (approval, station, `panel`), `BRIEF.md` (`## Approval`,
SC-13), `notes/uat.md`, `notes/handoff-build.md`, `notes/handoff-validate.md`.
**No digest was unreadable**, and no phase is reported here from context rather than from disk.

I measured four things myself rather than adopting them:

- `git diff --stat 984bd26b..HEAD -- . ':!.harness'` is **empty** — the two commits past the pin
  (`4907a81b` prepare UAT, `6d28b350` record UAT pass) touch only this feature's own records, so the
  pin still reviews the shipping code.
- `git status --porcelain` in the worktree is **clean**.
- `validate-digest.py lead` over all 29 digest files: **28 valid**, one invalid —
  `runs/2026-09-09-08-simplify-eng/digest.md` ("VERDICT is PASS but a member returned FAIL"),
  which run `-09` supersedes. **Correction to the record:** STATE.md's Q6 names run `-06` as the
  unrepairable digest; `-06` validates today. `-08` is the one that does not (row **B-21**).
- `git rev-list --count origin/main..HEAD` = **47** commits; the code delta is **18 files,
  +3203/-19** (the 2017-line `pre-t04-validate-digest.py.fixture` dominates it), plus `DECISIONS.md`
  inside `.harness/`.

## What ships

Per `BRIEF.md` (approved 2026-09-09) and `plan.yaml` (`approval.status: approved`, 9 tasks
T-01, T-03..T-10, all `done`):

- An **unknown key on a digest return is rejected**, not ignored — the closed key set is derived from
  the personas' own documented DIGEST blocks, with a mechanical agreement assertion so the two
  cannot drift.
- The same closure applies **inside a run `state.yaml` `steps[]` entry**, where nothing governed keys
  before, with a declared free-form-inside **`evidence:`** container so per-step evidence keeps a
  legal home.
- **`schema_version` monotonicity** — a creation floor of 2 plus refusal of a 2→1 downgrade on update.
- **Refusal messages name the declaration route** by file and symbol, at both the digest and step
  seams.
- **Issue #37 resolved in-feature**: `adequacy_notes` is now a required lead field.
- Doctrine recorded: **DEC-223** (the closed digest contract) and DEC-126's falsified
  `adequacy_notes` clause corrected in place (T-09).

**Every source edit was main-session-direct.** DEC-174 makes `validate-digest.py`,
`check-domain.sh`, `check-state.sh`, `run-state-schema.json` and their tests operator-owned, so the
28 recorded runs are **planning, gates and reviews** — not builds. One squad build run exists
(`2026-09-09-01-t09-product`, the documentation task). This is also why every residual below routes
to you or to the backlog and **not one of them is fixable by a squad**.

## The gates

| Gate | Result | Evidence |
|---|---|---|
| `qa_gate` (**blocking**) | **PASS** at `984bd26b` — unit exit 0 / 36 files, integration exit 0 / 70 files at full baseline discovery, focused `test-check-domain.py` 13/13 | `runs/2026-09-10-15-qa-gate-validator/digest.md`, `notes/qa-2026-09-10-15.md` |
| `review` panel (advisory unless high) | **PASS**, `must_fix: []`, 4/4 reviewers PASS, `severity_max: med`, `code_grade: pass` (42 functions), zero send-backs | `runs/2026-09-10-17-panel-validator/digest.md` + four `notes/review-*-c11.md` |
| SIMPLIFY (last build step, before the pin) | **PASS**, applied: none, would-have-applied: none — the accept-shape enumeration found 15 rows over `properties.steps.items` and **0** falling through to accept | `runs/2026-09-10-16-simplify-eng/digest.md` |
| goal-check | **PASS** — 9/9 REQ, 14/15 live SC met by harness evidence, SC-13 left to you | `runs/2026-09-10-18-goalcheck-product/digest.md`, `notes/research-FEAT-104-goalcheck-build-c11.md` |
| `uat` (blocking when uat criteria exist) | **PASS** — you returned `passed` | `notes/uat.md` |
| `merge` | user-gated — **yours** | — |

**The panel's own honesty, carried not smoothed:** `PF-C10-01` (the contested defect that made c10
ESCALATE at `high`) is **CLOSED**, and closed the strongest way this feature managed — the
`harness-ui-reviewer` that rated it `high` reproduced the fixed message live and **withdrew its own
finding**; qa measured the same stderr independently; code confirmed the mechanism at source. The
fail-*open* shape the fix could have introduced was **refuted** by four independent re-derivations
plus the lead's own schema read. What the panel could *not* do: two of three matrix figures are
**adopted** from the same-pin qa run rather than re-measured, the RED half of the witness pair
(12/13 at `790023f0`) is inherited rather than re-flipped, and DEC-174 forbade every mutation, so
"cannot fail open" is enumeration over the schema as it stands — which is exactly what rows B-7 and
B-8 are about.

## SC-13 — your UAT

`notes/uat.md`, `status: passed`, one step **U-01** against `review_sha: 984bd26b`: read the full
`git diff origin/main...984bd26b` of the seven carve-out files and confirm every change is limited
to the declared contract — no enforcement bypass, no unrelated behaviour, no historical
run-artifact rewrite. **Result: passed.** That closes the last live criterion; the goal-check's
`pending-operator` row is now `met`. The three concrete items pm and the panel flagged for that read
were CF-1, CF-4 and Q14 — all three survive as backlog rows (B-1, B-3, B-2), so passing the UAT did
not silently absorb them.

## Escalations — every one resolved

| # | Raised by | Substance | Resolution |
|---|---|---|---|
| E1 (`sigfix-c2`) | product-lead | A stale cross-worktree `harness-product-lead` claim made the run dir unwritable | **REFUSED at my tier** — not mine to release and liveness genuinely open; the lead returned its digest inline and I landed it. Recurred once (`q2-c4`). Row **B-28** |
| E1 (`od5-c3`) | pm | Does OD-5's strike mean *removal*, now that `plan-merge.py` has a `delete-items` verb? | **Yes** — verified at the control plane (human commit `11541475`); executed in `od5b-c3-product`, T-02 removed, nine tasks remain |
| E1 (`-04-panel`) | security-reviewer | A 2→1 `schema_version` downgrade on an update write escaped both gates, falsifying REQ-02 — `high` | **Fixed** main-session-direct; F1 confirmed CLOSED by execution at c9 and c10 |
| E1 (`-05-qa`) | validator-lead | The branch tip reverted the F2 fix graded PASS at `99035a9c` and deleted its two tests | **Resolved** — pin corrected to the real tip `168f875f`; F2 re-graded and **DECLINED with evidence**, the stranding reproduced on a real artifact by two reviewers. Residual row **B-15** |
| E1 (`-09-simplify`) | eng-lead | Every remedy the pass could offer needs an edit inside the DEC-174 carve-out, which resolves to NOBODY for eng | **Accepted as designed** — findings became recommendations; one worth-doing fix landed main-session-direct at `ce1fd115` |
| E1 (`-14-panel`) | ui-reviewer | `PF-C10-01` severity contested: ui `high` (would block) vs lead `med` | **Fix taken rather than adjudicated**; c11 measured it closed and the raiser withdrew it |
| c9 Q2 (`-04/-05`) | orchestrator | Who authored `168f875f`? | Established as the real branch tip; the F2 revert understood and its declination re-grounded |

## Proposed backlog — strike by id

Every finding that survived collation and does **not** gate. Nothing here blocks the merge; nothing
here is fixable by a squad while DEC-174 stands (rows marked ⌘ sit inside that carve-out).

| ID | Nature | Item | Source |
|---|---|---|---|
| B-1 ⌘ | bug | **CF-1 (`med`)** — `check-state.sh:1525-1526` interpolates `run_id` and the step id as **bare strings**, alone in this diff, so the accepted DEC-85 Bash-write route can spoof or erase the very INV-16 audit line that reports it. One-line fix (`!r`, or list-wrap to match `_names`). No operator-channel witness exists — reproduced in a throwaway script, never through the real `/harness` sweep | c9/c10/c11 panels |
| B-2 ⌘ | bug | **Q14 (`med`, contested ui med / qa low / code low / lead med)** — a **declared** step key with a type violation prints under the *undeclared step key or evidence shape* head, whose remedy tells the author to move the key under `evidence:`. An author who follows it produces `evidence: {cycles: "3"}`, **accepted at exit 0**, while the step-level field the retry accounting reads goes silently absent. Reachable today, uncovered by any test | c11 panel |
| B-3 ⌘ | bug | **CF-4 (`low`)** — the `schema_version` downgrade rejection renders a raw Python `None` when an update to an existing v2 checkpoint omits `schema_version`, where the sibling floor message says `schema_version is absent`. Reproduced by ui; disposed by the lead on `validate-digest.py` being byte-identical, by no reviewer | c9 panel, carried c11 |
| B-4 ⌘ | chore | **CF-2 (qa `med` / code `info` / lead `low`)** — `check-state.sh:1590`'s literal-`"lead"` at-rest exemption has **no test able to report RED**: swap in the `_host` value computed four lines above and every historical artifact silently re-exempts | c9 panel, carried c11 |
| B-5 ⌘ | chore | **R1/Q20** — `test-check-state.py:51-54` asserts run/step/key but **not** the declaration route, though `check-state.sh:1526-1528` emits one. Outside SC-08's subject (INV-16 is an at-rest report, not a rejection); a one-line hardening | c11 goal-check |
| B-6 ⌘ | chore | **Q9** — the generic-`lead` archive exemption at `validate-digest.py:1407` has **no test able to redden**. It does not falsify REQ-08 (present at the pin, behaviour demonstrated) but it is that requirement's standing regression risk | c10/c11 panels |
| B-7 ⌘ | enhancement | **Q15 (`info`, latent)** — `shape_problems` splits required-vs-offending on the **validator name** rather than the structural cause (empty `error.path`). A future step-level `minProperties`/`dependentRequired` would fill neither bucket and emit **no denial**. Unreachable at this pin (schema census by the lead and all four reviewers); deliberately not hardened against keywords the schema does not declare | c11 panel |
| B-8 ⌘ | enhancement | **Q16 (`info`, latent, security-only find)** — `_missing_required` keys on `validator == "required"` with **no path check**, so a nested `required` violation (a future `evidence` sub-object) reports as a missing *step* key. Fail-closed but mislabelled; gate on `error.path == []` when nested `required` first arrives | c11 panel |
| B-9 ⌘ | chore | **Q17/Q19** — SC-08's step seam is pinned by the **invocation path**, not string uniqueness: `undeclared step key` has two producers (`check-domain.sh:1671`, `check-state.sh:1526`). Safe today because the test fires a Write hook; a future test asserting that phrase against combined or at-rest output needs a producer-unique string | c11 panel |
| B-10 ⌘ | chore | **SIMPLIFY-SC08-01 (`low`)** — all four substrings in `test-check-domain.py:88-89` come from one unconditional `out.append` pair (`check-domain.sh:1653-1658`), so clauses 3 and 4 are implied by clause 2 *at today's emitter*. Not applied: no apply may weaken an assertion, and the clauses buy detection of a future message split | `-13-simplify-eng` |
| B-11 ⌘ | chore | **Q7** — the strict `schema_version` predicate is hand-written at **3 complete** sites (`check-domain.sh:1594-1597`, `:1761-1764`, `check-state.sh:1487-1489`) plus **2 partial** type-half restatements (`check-domain.sh:1601`, `:1767-1768`) with no shared home; `run-state-schema.json` types the field as integer with **no minimum**, so the floor lives only in shell | `-08/-09-simplify-eng` |
| B-12 ⌘ | chore | Stale comment at **`check-domain.sh:1646-1647`** — it now describes only the `_offending` half of a two-branch loop (ui `low` / code `info`). Concrete scenario: someone extending the `required` handling later, trusting "name their nearest field", reintroduces the PF-C10-01 shape | c11 panel |
| B-13 ⌘ | chore | **F-104C10-01 (`info`)** — the seam assertions test the **whole stderr buffer**, so a regression splitting route text and offending-key line across two writes still passes. The file's established convention, not a regression of this delta | c10 panel |
| B-14 ⌘ | chore | **F-104C10-02 (`info`)** — the step seam's "symbol" is thin (file path + one JSON property name) against the digest seam's three Python identifiers. Closed under `plan.yaml:460-462`'s decided route; recorded for whoever reuses the pattern | c10 panel |
| B-15 ⌘ | enhancement | **F2's runtime residual** (declination stands) — `stop_hook_active`'s accepted one-shot passthrough (SC-09/DEC-208) plus the persona-blind at-rest sweep leaves an undeclared key on a **new** lead digest uncaught at rest. No safe remedy was shown to exist; two reviewers reproduced the stranding on a real artifact | c9 panel, confirmed c11 |
| B-16 ⌘ | chore | **Guards argued fail-closed, not mutation-proven** — `check-domain.sh`'s step guard got six live probes at c11, but `validate-digest.py` and `check-state.sh`'s guards remain reasoned only; DEC-174 forbade the mutation that would demonstrate them | c9 panel, partial at c11 |
| B-17 ⌘ | chore | `check-domain.sh`'s pre-existing **`_no_parser` bootstrap early return** — sits above both FEAT-104 blocks; security confirmed the next at-rest sweep catches what it lets through | c9 panel, carried c11 |
| B-18 ⌘ | bug | The pre-existing **DEC-85 Bash-write bypass** — CF-1's precondition. Already with the main session; re-raised by nobody as new, and listed here only so it does not die with this feature | c9/c11 panels |
| B-19 | chore | **F-QA-1** — `T-05` declares `change_type: logic` against DEC-212's `touches_config_shape`. Integration coverage exists regardless; a matrix-classification note for the next task on this surface, now in its third cycle | c9/c10 qa |
| B-20 ⌘ | chore | **T-06 has no omitted-`schema_version`-on-update case** — the coverage hole that is exactly why CF-4's `None` rendering was never seen by a test | c9 panel |
| B-21 | bug | The **append-only digest correction channel cannot repair** a missing required field or a self-contradiction — it writes past the point where `validate-digest.py`'s parser stops (the validator slices from the LAST `VERDICT:`). Measured now: `runs/2026-09-09-08-simplify-eng/digest.md` is the one invalid digest on this feature ("VERDICT is PASS but a member returned FAIL"), superseded by `-09` and unrepairable in place; the guard refused two correction attempts | `-08/-09-simplify-eng`, my measurement |
| B-22 | bug | A **`^FAIL ` census over `run-unit-tests.sh` is defeated** by `tests/unit/test-factory-claim-mutation.py`, which reprints 4 captured `FAIL  BUG-1290 …` lines as its own success output at exit 0. Any gate or acceptance clause reading that count literally misreports a green suite as red | `-02`/`-07`/`-15` qa |
| B-23 | chore | **"The tree must be clean" is unsatisfiable** for an agent writing its own feature artifacts — only `runs/**` is gitignored, so a legitimate note or observations write reddens the clause. Scope such clauses to *tracked* modifications | orchestrator, c9-c11 |
| B-24 | bug | Terminal `yield` exiting 1 with **"yield called with null data"** on a complete fenced block — seen on qa, the eng lead and two `dev-ops`. Did not recur in the last two cycles | STATE Q12 |
| B-25 | enhancement | **Read-only review panels have no scratch-write route** — `harness-code-reviewer`'s `mktemp -d` probe was refused by `bash-write-guard` for **two consecutive cycles** (reading only the schema, writing only `/tmp`) while qa and ui executed live probes. The guard is working and the reviewer behaved correctly, yet the panel's strongest lens is systematically the one that cannot execute | c10/c11 panels |
| B-26 | enhancement | The **lead digest schema has no home for per-kind suite exits and file counts, and declares no `code_grade`** — worked around both cycles by naming the declared field set and carrying the grade in the headline | Q-B3/Q4, c9-c11 |
| B-27 | chore | **INV-26 card/plan mismatch** — FEAT-104's GitHub cards read `building` against a plan reading `done` because D-23 moves no card to the done station before `gh-sync.py ship`. Standing mirror behaviour, not this feature's defect | `notes/handoff-build.md` |
| B-28 | bug | **Cross-worktree persona claims are not type-scoped** — a live `harness-product-lead` claim from another feature refused a lead's own `runs/**` write on this one, twice, forcing the digest to be landed from my tier. Blast radius is run bookkeeping only; FEAT-56 owns the escalation and this row cites rather than re-files it | `sigfix-c2`, `q2-c4` |
| B-29 | chore | **The reviewed range and the graded range differ by one commit** — `origin/main..<pin>` includes a branch's root commit, `code-grade.py`'s merge-base range does not, so every mechanical gate was blind to CF-3 by construction. Whatever you decide about CF-3 itself, the blindness outlives it | c9 panel |

## Budget — one crossing, disclosed

- **`cycles_used: 10` of `max_total_cycles: 10` — EXHAUSTED.** This is the hard bound. It was not
  crossed: the last three runs each returned zero send-backs. But **no fix cycle remains**, and none
  is needed — every surviving item above routes to you or to the backlog, not to a squad. If you
  want any B-row fixed *inside* this feature, that is a budget raise, and it is your decision to
  record in `feature.json`.
- **`len(runs): 28` of an informational `max_total_runs: 20` — CROSSED.** Informational by design
  (INV-22, issue #79): it notices a long feature and stops nothing. 18 PASS, 4 FAIL, 6 ESCALATE.
  **My read: most of these runs earned their place, and some did not.** Earning it: three
  qa/panel/goal-check cycles at three successive pins, each one closing a specific contested defect
  (F1, F2, PF-C10-01, SC-08's proof gap) with measured evidence rather than argument. Not earning
  it: **six runs were tooling overhead, not work** — `od5-c3`/`od5b-c3` (a missing `delete-items`
  verb, then found to exist), `paneltranscribe-c1`/`c1b` (a reader entry that needed a second verb),
  `-08`/`-09-simplify` (a digest that could not be repaired in place, so the run was re-issued).
  Rows B-21, B-26 and B-28 are the specific causes. A feature of this shape should be a ~22-run
  feature.

## Where things stand on disk

- `review_sha: 984bd26b`; branch tip `6d28b350`; **no code differs between them**.
- `plan.yaml`: `approval.status: approved` (2026-09-09, operator), `status: review`, nine tasks
  `done`, `panel` recorded from `planpanel-c1-validator`. `BRIEF.md ## Approval`: `approved`.
- Worktree clean. `pr: null` — **nothing has been merged, pushed, PR'd or synced to GitHub.** The
  mirror still reads `review` (parent 1584, sub-issues 1585-1593, milestone 65).

## Artifacts

Under `.harness/harness/features/FEAT-104-strict-digest-schema/`:

- `notes/uat.md` — your UAT, `passed`
- `notes/research-FEAT-104-goalcheck-build-c11.md` — the per-criterion goal-check with provenance
  labelled per leg (ADOPTED vs MEASURED)
- `notes/review-harness-{code-reviewer,qa,security-reviewer,ui-reviewer}-c11.md` — the standing panel
- `notes/qa-2026-09-10-15.md` — the blocking gate at the pin
- `runs/*/digest.md` — 28 runs; 28 of 29 digest files validate, `-08` excepted (B-21)
- `notes/ship-review-plan-signature-c{1,2,3,4}.md` — the plan-phase packets, superseded, kept legible
- `notes/handoff-{plan,build,validate}.md` — the phase seams
