# Goal-check — FEAT-53 plan, cycle 4 — 2026-09-02

**BLUF. Yes, qualified.** Every ruling the operator issued across the grilling and all three answers
files is delivered at source, V-1..V-5 are closed in the amended fields (not merely summarised), the
seventh KPI is complete end to end, and the accuracy / handoff-eval KPI appears nowhere. Three
qualifications, none of them a build defect and none fixable in this step: two rulings the operator
already gave (DEC-2 keep the client build, DEC-3 accept the alpha) are still written up as *open at
signature*, so the signature packet re-asks answered questions; `DESIGN.md` still names the dead
`react-charts` as the second fallback the same ruling struck; and DEC-5's prototype closure predates
the seventh tile, so the operator's visual sign-off does not cover the surface now being signed.

**Does this plan deliver the operator's stated intent?** **Yes, with three qualifications** — the
plan builds what the operator asked for; two of his own decisions are not recorded as decided, and
one closed gate (DEC-5) now covers less than the plan it closed.

Graded against `.harness/notes/grilling-metrics-dashboard-2026-09-01.md` and
`notes/answers-2026-09-01-plan-signature{,-c2}.md`, `notes/answers-2026-09-02-plan-signature-c3.md`
— never against `BRIEF.md`, which is derived from them.

## Verdict per operator commitment

| Source | Commitment | Verdict | Evidence |
|---|---|---|---|
| grilling Settled | general capability, any onboarded project | met | REQ-02; `plan.yaml` T-06 intent (resolves everything from `project_root`) |
| grilling Settled | live interactive server, not `render-brief.py` static HTML | met | D-03, D-05, D-06, D-17 |
| grilling Settled | real web framework + JS charting, justified DEC-190-style in a gate/CI | met | D-03 (three rejections named); T-12 `--check`; T-22 CI Flask step |
| grilling Settled | six KPIs, each as described (incl. distribution-not-mean, Python-only caveat live per project) | met | REQ-03..REQ-09; D-12, D-13; T-07 |
| grilling Settled | KPI 6 as agent/model tier, provider join scoped as its own task | met | D-13; T-09 |
| grilling Settled | no DB, no cache at launch; trend in append-only `trend.jsonl`; history never recomputed | met | D-09, D-10, D-11, D-18 |
| grilling Settled | SQLite named as future lever only, deferred not rejected | met | D-09 |
| grilling Out of scope | no cost/dollar metric, no cross-provider, no cross-project, no `.sh`/`.ts` grading | met | BRIEF `## Out of scope`; grep for `cost_usd\|dollar\|spend\|price` over plan/DESIGN/BRIEF returns only the out-of-scope bullet |
| grilling Not-yet-specified ×8 | all eight resolved (framework, hosting, trigger, defect sourcing, KPI-6 join, entry point, trend schema + approval sourcing, touchpoint mechanism) | met | D-03, D-05, D-06, D-15, T-09, D-01/D-17, D-18/D-14, D-16/D-21/T-11/T-20 |
| c1 DEC-1 | hold the web-framework call, pick one, record rejections | met | D-03 `choice`/`because` |
| c1 DEC-2 | KEEP the client build, D-20 stands | met in substance, **not recorded as ruled** | D-20 `choice` keeps it, but `because` and BRIEF `## Constraints` still say "needs an explicit yes or no at signature" |
| c1 DEC-3 | ACCEPT the alpha with the documented rollback; dead reference struck | **partial** | D-08 still says "NO FALLBACK LIBRARY IS NAMED … operator decision outstanding at signature"; `DESIGN.md:250` still names React Charts as the second fallback |
| c1 DEC-4 `PF-328f8f3c` | scope absent-touchpoint-zero to post-instrumentation | met | D-21; T-11 four-branch ladder; SC-17 |
| c1 DEC-4 `PF-7408d83a` | a task that wires the chart, verify on rendered output | met | T-21 (`getByTestId` + subtree assertions, reds demonstrated); T-22 |
| c1 DEC-5 | prototype opened and reviewed before signing, not waived | met, **now stale** | closed by the operator in c2 (`notes/handoff-plan.md:23`); `DESIGN.md:531-541` discloses the committed prototype has no seventh tile and no 3×3 grid |
| c1 Backlog | accept B-1..B-10, label Dashboard | met with a carrier gap | B-1..B-5 carried as panel dispositions; **B-7..B-10 live only in `notes/ship-review-2026-09-01-plan.md:126-129`** and no task owns filing them |
| c2 Q1 `PF-45518258` | add T-21 to T-16's `depends_on` | met | T-16 `depends_on: [T-12, T-15, T-21]` |
| c2 Q2 | cycle time from BRIEF approval; update D-14/T-06/D-21/trend; strike B-6 | met | D-14; T-06 `approval_date`; D-21 start rule; D-18 `approved_on`; B-6 struck (`STATE.md:18`) |
| c2 Q3 B-11 | epoch + touchpoints committed, committer named in the owning task | met | D-22; T-20 (`git add` written into each of the three instructions); T-02 gate |
| c2 Q3 | accept B-12..B-14 as backlog | met | panel rows, disposition `backlog` |
| c3 Q1 V-1 | name a committer for `trend.jsonl` | met | see below |
| c3 Q2 | fix B-15..B-18 | met | see below |
| c3 Q3 | seventh tile, merged PRs by week, only new scope | met | see below |
| c3 | accuracy KPI nowhere in FEAT-53 | met | see the stated line below |

## The five findings closed this cycle — opened at source, not trusted from the summary

- **V-1 closed.** `D-22.choice` covers all three runtime-created files and names the committer for
  each; `T-19` intent ("THE APPEND AND ITS COMMIT ARE ONE ACT") has `record_ship` git-add and commit
  `trend.jsonl` immediately after `append()`, wrapped non-fatally, and cites `gh-sync.py:659-661` for
  why no existing step commits it.
- **V-2 closed.** `brief_approval.py` is in `T-06.files` and its intent creates
  `approval_date(feature_dir) -> (value, reason)` as the only parse; `T-11`'s `feature_start` *calls*
  it and is told not to restate the parse; `D-14.choice` records the one-authority/two-callers rule.
- **V-3 closed.** `T-06` fixtures four gap features (no BRIEF, no Approval section, status not
  approved, approved with empty date), four separate assertions, and the four sentences asserted to
  differ — with "never a count of unavailable entries" written in.
- **V-4 closed.** `T-11` intent: every writing case copies the fixture tree to a `TemporaryDirectory`
  and passes the copy; read-only cases must *not* copy; a recursive digest of `dashboard/fixtures/`
  before and after is asserted equal as its own case.
- **V-5 closed.** `D-21.choice` and `T-11` branch 3 both compare reduced UTC dates, and `T-11` adds
  the same-calendar-day case as its own assertion reaching branch 4.

## The seventh KPI (Q3) — complete end to end

REQ-15 → SC-19 (`automated`/`integration`, four assertions, empty week demonstrated failing first)
and SC-20 (`inspection` at `review_sha`) → payload in `T-10` (weekly buckets from `trend.jsonl`,
counted as **shipped features not populated `pr`**, week bounds + empty-bucket count returned,
pre-segmented) → tile and panel 7 in `T-14` (3×3 grid, full-row span, inline sourcing rule) → mount
and the third gated case in `T-21` → suite/CI reachability in `T-22` (label byte-identical on both
sides) → honest empty bucket: `null` with the verbatim reason `no ship record in the week of
<YYYY-MM-DD>`, the sparkline breaking at it (CAP-09), never `0`. `T-10` traces REQ-15, `T-14` traces
REQ-15, `T-21` traces REQ-15. DESIGN C-1/C-2 add no capability row and Q4 is answered by `T-10`.
**No link in that chain is missing.**

## The accuracy / handoff-eval KPI

**Stated as its own line: the accuracy / handoff-eval KPI appears nowhere in `BRIEF.md`, `DESIGN.md`
or `plan.yaml` — not as a requirement, criterion, decision, task, tile, capability, panel note or
deferred follow-up reference.** Method: case-insensitive regex over exactly those three files for
`accuracy|handoff|hand-off|FEAT-54|required-facts|30-run|perfect.response|ambiguity|eval harness|eval
study|dispatch eval|ai_behavior|follow-up feature|deferred to a follow` — zero matches; and a second
pass for `eighth|KPI 8|tile 8|eval tile|4x2` over the whole feature directory — zero matches. The
only `eval` token in any of the three is `BRIEF.md:137`, the `eval` **test kind** with `cmd: null` in
the verification-gaps paragraph, which is unrelated.

## What the plan quietly dropped or narrowed — the cross-cycle check

1. **Two operator rulings are not recorded as ruled.** c1 DEC-2 said KEEP the client build and c1
   DEC-3 said ACCEPT the alpha with a documented rollback. `D-20.because`, `D-08.choice` and BRIEF
   `## Constraints` (lines 78-80, 85-87) still present both as "an operator decision outstanding at
   signature". The plan therefore asks the operator, at cycle-4 signature, two questions he answered
   on 2026-09-01. Nothing in the build changes — the substance is right — but the record is wrong,
   and "the documented rollback" the ruling accepted is named nowhere.
2. **`DESIGN.md:250` still names React Charts as the second fallback**, which c1 DEC-3 struck and
   which BRIEF now records as dead (React 16 peer vs React 19 substrate). DESIGN and BRIEF
   contradict each other on the same fact.
3. **DEC-5's closure is stale.** The operator closed the prototype gate in c2 over a six-tile 3×2
   landing grid (`notes/prototypes/FEAT-53/src/components/KpiTiles.jsx:1`). `DESIGN.md:531-541`
   honestly discloses that the committed prototype has no seventh tile, no 3×3 grid, no TBL-1..TBL-3,
   no S-5 and nothing of C-3 — and that its appearance has never been rendered by anyone. `T-05`'s
   intent still specifies a "3x2 tile grid", so nothing in the plan would extend it. With `ui`
   runnerless, the prototype was the only place the seventh surface could have been judged before
   build.
4. **Four accepted backlog rows have no live carrier.** B-7..B-10 were accepted ("None struck") and
   exist only in the immutable cycle-1 briefing; B-1..B-5 and B-12..B-14 survive as panel
   dispositions, but no task and no plan row owns filing any of them via `gh-sync.py backlog`. B-7 in
   particular is substantive off this repo — pruned branches null half of KPI 1 — and is honestly
   deferred rather than lost, provided the filing happens.
5. **A settled premise moved, and is disclosed.** The grilling's ~1.1 s per-request measurement is
   superseded by 4.3–5.3 s with an 8.0 s pinned ceiling (BRIEF `## Constraints`, SC-16, D-09). No
   narrowing — but the no-cache deferral now rests on a cost four to five times the one the operator
   settled it against, and only he can re-affirm that.

Nothing else across the four cycles was narrowed: the "nice to have" KPI 6 became a full requirement
(widened, not dropped), and every grilling out-of-scope line is still out of scope.

## BRIEF edit made in this step

`SC-04` re-phrased so "the six KPIs" is bound to the six the criterion enumerates rather than
asserting the KPI set is six — assertions, `verify: automated` and `evidence: unit` unchanged. No
other staleness of the six/seven count survives in `BRIEF.md` (`## Goal` says seven; `## Constraints`
says "Five of seven"; coverage table carries REQ-15/SC-19/SC-20). `## Approval` byte-unchanged,
`status: pending`.

## Addendum — 2026-09-02 — Q5 (the stale `3x2` grid literals) is closed

Q5 asked whether any plan field still described the pre-cycle six-tile `3x2` landing grid after
BRIEF, DESIGN C-1 and `T-14` moved to seven tiles on `3x3`. It did, in exactly two fields, and both
are now amended through `plan-merge.py amend --expect-sha256`:

- **`T-05.intent`** — the prototype-scope clause now reads "the landing tile grid in DESIGN C-1's
  fixed order - a fixed 3x3 grid of seven tiles, tiles 1-6 filling rows 1 and 2 three across and
  tile 7, Merged PRs over time, LAST and spanning the full third row at every breakpoint". Wording
  follows `T-14.intent`'s LANDING paragraph rather than inventing a third phrasing. Nothing else in
  `T-05` changed — gap-state list, fixture-payload rule, publication path, never-live-data rule and
  `status` are untouched, and DEC-5 stays closed.
- **`T-07.intent`** — the SC-06 rationale's grid literal is now `3x3`.

**This supersedes one clause of item 3 above:** "`T-05`'s intent still specifies a '3x2 tile grid'"
is no longer true. The rest of item 3 stands unchanged — the *committed prototype* is still a
six-tile `3×2` build that no one has ever rendered (`DESIGN.md:531-541`), and correcting `T-05`'s
contract does not extend it. The verdict of this note is unchanged.

Sweep: zero occurrences of `3x2` or `3×2` survive anywhere in `plan.yaml`; the three `3x3`
occurrences are `T-05` (line 331), `T-07` (line 541) and `T-14` (line 990).

**One finding raised rather than fixed here.** The same `T-07` sentence — and BRIEF `## Verification
gaps` (`BRIEF.md:154-158`) — says the tokens `12` and `3` are un-greppable because "they occur
inside `1024`, `3x3` and `ES2022`". The `3` half is true (`3x3` carries it, twice). The `12` half is
false of all three named values: `12` is a substring of none of `1024`, `3x3` or `ES2022`. Its real
carrier is `127.0.0.1` (D-05's bind address, `plan.yaml:60`, `T-12` at `866`/`869`) and `122`, which
is itself a forbidden literal and so cannot serve as the excuse. The rationale's conclusion survives
— `12` genuinely cannot be greped bare — but it cites the wrong evidence in two artifacts, one of
which is out of scope for this step. Carried as `open_questions` Q1.
