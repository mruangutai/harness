# Ship review — BUG-1016-worktree-relative-paths

**Ready to ship.** Validate c3 over pin `ef9cbce2` returned PASS with an empty must-fix list;
all seven success criteria are met; both signed perspectives pass. Branch tip `8c370f7c`
(code paths byte-identical to the pin). Merge is yours.

No report round was spawned: this briefing is assembled from the digests on disk —
`runs/plan-product`, `runs/plan-simplify-eng`, `runs/plan-apply-product`, `runs/t02-docs-product`,
`runs/build-simplify-eng`, `runs/validate-validator`, `runs/validate-c2-validator`,
`runs/validate-c3-validator` (each `digest.md`), plus the c3 goal-check
`notes/research-BUG-1016-worktree-relative-paths-goalcheck-validate-c3.md` and the T-01
main-session receipts `notes/t01-receipts-main-session.md`. `runs/t02-docs-eng` has no directory
(BLOCKED at 38 s: documentor is a product persona; re-routed to the product lead).

## Definition of done — graded (validate goal-check c3)

| Perspective (as signed in BRIEF) | Verdict | SCs | Evidence |
|---|---|---|---|
| **operator** — I can rely on a governed agent's relative file-tool calls reaching its assigned feature worktree, including omitted-path searches and multi-file edits. Explicit destinations remain explicit, uncertain assignments refuse rather than guess, and my main-session tools behave as before. | met | SC-01..SC-06 | goalcheck-validate-c3.md § Delivered perspectives; qa c3 `notes/review-harness-qa-c3.md:16,20-22` (124/0 at pin; R2 red 123/1 on old adapter; G1 mutant 122/2); receipts `notes/t01-receipts-main-session.md:8-26` |
| **code maintainer** — I can find one documented adapter contract and regression cases covering every supported tool shape, without introducing a second worktree resolver or changing another host. | met | SC-07 (+T-01, T-02) | goalcheck-validate-c3.md SC table; `notes/review-harness-code-reviewer-c3.md`; DEC-251 at `.harness/harness/docs/DECISIONS.md` @8013 and its DECISIONS-INDEX row |

SC-01..SC-06 automated (unit, `python3 tests/unit/test-omp-hooks.py`); SC-07 inspection. The
BRIEF declares no UAT and sanctions the absence of a TypeScript typecheck runner (BRIEF.md:32).

## What shipped

- `.omp/extensions/harness-hooks.ts` — one worktree-rooting adapter inside `registerHarnessHooks`
  for governed OMP read/grep/glob/write/ast_grep/ast_edit calls: relative paths and
  semicolon-list entries root in the assigned feature worktree; omitted/null search paths
  default to the worktree root; explicit blanks, absolute, `~` and scheme paths pass through
  byte-for-byte; edit section headers and MV destinations resolve to the same effective
  destinations the pre- and post-write domain checks see. Main-session and Bash behaviour
  unchanged. T-01 was main-session-direct (DEC-174): commits 10f38a42 (feature) and a6a1e9c8
  (R2 fix: quoted targets rooted at the quote boundary, not at the first text match).
- `tests/unit/omp-hooks.test.ts` — 124 adapter cases (109→124 across the feature), each new
  case recorded red before the adapter change (`notes/t01-receipts-main-session.md`; R2 test
  re-measured red by qa c3).
- `DEC-251` in DECISIONS.md + index row — the adapter contract (T-02, `runs/t02-docs-product`).

## Phase summaries (by digest)

- **Plan** (`runs/plan-product`, `runs/plan-simplify-eng`, `runs/plan-apply-product`): plan
  drafted, panel findings resolved, SF-01/02/04 applied, both perspectives pass goal-check 1;
  approved 2026-10-04 with rework ruling 2 rounds / 90 min.
- **Build** (`runs/t02-docs-product`, `runs/build-simplify-eng`): T-02 PASS; simplify 8/8 angles,
  nothing applied, one fixture-reuse finding (F1) ruled backlog. The lead's FAIL verdict rested on
  a false premise (its own run-start moved feature.json); 1 cycle charged to honour the ledger.
- **Validate** — three cycles over one adapter:
  - c1 (`runs/validate-validator`, pin 8211687f) FAIL R1: predicate wording differed from BRIEF
    Constraints; closed by the operator's BRIEF amendment b011c90f
    (`notes/brief-amendment-2026-10-04.md`), no code change.
  - c2 (`runs/validate-c2-validator`, pin 55c99a85) FAIL R2: `rootTarget` placed the root before
    the opening quote for all-quote targets (`"""`); fixed main-session-direct at a6a1e9c8 with a
    discriminating regression.
  - c3 (`runs/validate-c3-validator`, pin ef9cbce2) PASS: qa, code, security, ui (scoped out,
    zero visual surfaces), goalcheck all PASS; G1 (quoted `~`/absolute/scheme exclusion rows)
    resolved by the same test.

## Open questions

- Q1 (harness defect, non-blocking): check-domain refused governed `write agent://<peer>` and
  `write xd://report_issue` as filesystem paths in every squad this feature — BUG-2003's scheme
  pass-through is not reaching the live hook. Harness owner to triage (B-3 below).
- Q3 (harness defect, non-blocking): a feature.json post-write check in this worktree emitted
  handoff-shape complaints about notes under another worktree (FEAT-1928); the sweep crosses
  worktree boundaries (B-4 below).

Resolved escalations: none lateral. Two operator rulings closed R1 (BRIEF amendment, option a)
and R2 (fix, option a).

## Spend and ledger

`feature-record.py spend`: 9 runs, 119 wall-clock minutes, 591,597 tokens; rework 40/90 min,
rework rounds 0/2 (no governed fix run — both rework items were DEC-174 main-session-direct).
cycles_used 4/10 (build-simplify FAIL 1, validate c1 1, validate c2 1, validate c3 1 — the last a
lead-reported in-run send-back for a qa receipt shape correction). Runs 9/20 — within budget.
Judgements: 10 (mission 1, continue 4, regate 3, succession 2).

## Amendments (DEC-229)

| at | decision | reason | overruled |
|---|---|---|---|
| — | — | the build amended no signed task text | — |

overrule rate: 0/0

## Proposed backlog

| ID | Nature | Item | Source |
|---|---|---|---|
| B-1 | chore | Dedupe `rootedHooks` fixture against `governedUriHooks` (tests/unit/omp-hooks.test.ts:1291) | simplify F1, `runs/build-simplify-eng/digest.md`; operator ruled backlog |
| B-2 | chore | Re-sign D-01/T-02 singular `path` wording to reflect ast_edit `paths: string[]` (docs/plan wording only; DEC-251 already records the array) | documentor Q1, `runs/t02-docs-product/digest.md` |
| B-3 | bug | check-domain treats `agent://` and `xd://` write targets as filesystem paths and refuses them (BUG-2003 pass-through not live) | validate c1–c3 open_questions Q1 |
| B-4 | bug | feature.json post-write check reports handoff-shape findings for notes under a different worktree | orchestrator Q3, STATE.md |
| B-5 | chore | Add dedicated rows for quoted `~`/absolute/scheme exclusions per predicate × tool, and an executed quote-only edit-section/MV row (currently covered via shared-helper inspection) | validate c3 `coverage_gaps` |
| B-6 | chore | `ast_edit` remains outside the hook mutation authorization/domain set (pre-existing) | `notes/t01-receipts-main-session.md` § Deviations; DEC-251 |

Unstruck rows become backlog issues on ship acceptance; anything not listed here is dropped.

## Ship steps (main session)

1. Review and, if any amendment were present, overrule by `at` — none here.
2. `gh-sync.py ship <feature-dir> --body-file notes/ship-review-validate-c3-validator.md` from
   the main checkout; backlog B-1..B-6 as issues (bug/chore).
3. Merge `feat/BUG-1016-worktree-relative-paths` at 8c370f7c; the post-merge hook removes the
   worktree. Then dispatch feature-close distillation naming `notes/` and `observations/` only
   (the gitignored `runs/` tree dies with the worktree).
