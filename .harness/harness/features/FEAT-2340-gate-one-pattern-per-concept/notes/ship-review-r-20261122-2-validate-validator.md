# Ship review — FEAT-2340 Gate one pattern per concept

**Ready to ship.** The validate panel passed every reader over `125a04f8` with no must-fix findings, both signed perspectives are graded met, and zero rework cycles were spent. The merge is yours; nothing has been pushed, no PR opened.

No report round was spawned. This briefing is assembled from disk:
- `runs/r-20261122-1-plan-product/digest.md` (plan, PASS)
- `runs/r-20261122-2-validate-validator/digest.md` (validate, PASS)
- `notes/research-FEAT-2340-gate-one-pattern-per-concept-goalcheck-validate-c1.md`, `notes/review-harness-{qa,code-reviewer,security-reviewer,ui-reviewer}-c1.md`
- `notes/simplify-pass.md`, `notes/verify-T02-{baseline,post}.receipt`, `notes/code-grade-e239d881-125a04f8.md` (main-session build evidence; the build was main-session-direct and has no run digest)

## Done when — graded

| Perspective (as signed) | Verdict | SCs | Evidence |
|---|---|---|---|
| **code maintainer** — I can recognize a path concept and a constant's meaning without decoding aliases, while retaining the gate's deliberate bootstrap independence. | met | SC-01, SC-02 | goalcheck-validate-c1.md line 6; code-reviewer-c1.md (no findings; protected declarations preserved) |
| **operator** — I can rely on the same gate decisions and diagnostic names after the cleanup, with prevention guidance landing before the gate refactor and no expansion into other files. | met | SC-03, SC-04 | goalcheck-validate-c1.md line 7; qa-c1.md (8 suites rc 0, 478 ok, baseline/post receipts equal); df6ae1cc precedes ffe320f5; production diff confined to the four approved files |

## What landed

- **T-01** (df6ae1cc): angle-reuse asks for a second matcher/constant/helper for an existing concept; angle-simplification asks whether a new name hides behaviour behind an alias; model-the-domain carries the three naming bullets and the bootstrap-respelling exception.
- **T-02** (ffe320f5, check-domain.py only): `_I` → `re.IGNORECASE` everywhere; one `RE_HANDOFF` with non-greedy `phase` and optional `cycle` (`_RE_HANDOFF_CYCLE` deleted); one `_PLAN_YAML_PATTERN` compiled twice with the original flag asymmetry; `VERB` → `SHAPE_DIAGNOSTIC_LABEL`; stale comment fixed. Protected declarations, fixture and tests untouched. Touched functions grade 4/5/5 against bar 4.
- **SIMPLIFY** (acd655c7): four read-only angles using the new T-01 questions, nothing found.
- T-02's baseline verify ran ~11 s inside the 55 s budget; the 300 s authorization in the signature was not used.

## Leads

- Plan (`runs/r-20261122-1-plan-product/digest.md`): two tasks, both main-session-direct; panel c1 six findings all resolved at apply; goalcheck PASS both perspectives.
- Validate (`runs/r-20261122-2-validate-validator/digest.md`): qa PASS (matrix floor empty for docs/scaffolding; integration family executed as SC-03 regression evidence), code PASS, security PASS (write-denial boundaries preserved), ui scoped out, goalcheck PASS; `severity_max: none`, `must_fix: []`.

## Coverage gaps the panel recorded (not gating)

- Multi-cycle handoff canonicalization and mixed-case plan diagnostic ordering are carried by SC-02 inspection, not automated tests (as the BRIEF signed).
- No check-domain unit suite exists; only the integration family ran.

## Open questions and escalations

- Q-01 (validator lead, non-blocking): qa reports the digest validator demands a `fail_first` entry even for a signed regression-only automated SC; recorded as backlog B-17 below.
- Escalations: none.

## Spend and ledger

- Runs 2 / 20 · cycles 0 / 10 · wall clock 28 min · rework 8 min of 90, 0 of 2 rounds · tokens 102,447.
- Judgements: 2 (`mission: plan`, `succession: continue`).
- Amendments: none. overrule rate: 0/0.
- UAT: none required (BRIEF `## Verification gaps`).

## Proposed backlog

One row per out-of-scope group (BRIEF `## Out of scope`; detail in `notes/inventory-Inv2340.md` §5). Each is its own later sequential patch; strike rows by ID.

| ID | Nature | Row |
|---|---|---|
| B-1 | chore | Group F — feature tree/artifact prefix: 7 files (check-domain, harness_boundary, feature_corpus, check_state/runner, check-instruction-paths, handoff_done_when, validate-digest) differ in depth, captures, identifier strictness, repository tier. Consolidate to one grammar with named variants. |
| B-2 | chore | Group J — feature.json destination: check-domain, feature_json_write, factory_decompose (deliberately broader), harness_boundary. |
| B-3 | chore | Group Y — plan.yaml destination: check-domain (route guard and shape, now one text), plan_merge/guards, harness_boundary. |
| B-4 | chore | Group O — observation note: check-domain route guard accepts any Markdown basename while observations-merge restricts to `harness-[a-z0-9-]+.md`; reconcile. |
| B-5 | chore | Group E — expertise path/tier: check-expertise, check-instruction-paths, expertise-merge, merge-gate, harness_boundary; prefix, destination and persona-capturing variants. |
| B-6 | chore | Group S — run state.yaml: check-domain and harness_boundary carry an intentional identical pattern-text pair (bootstrap exception). Decide whether the exception stays or a shared source is allowed. |
| B-7 | chore | Group G — run digest: check-domain / harness_boundary identical pair plus validate-digest's root-capturing variant. |
| B-8 | chore | Identical strict feature-slug regex: check-domain `_FEATURE_ID_RE` and dispatch-guard `FEATURE_RE`; plus the looser pair feature-worktree / feature_corpus. |
| B-9 | chore | Identical distill-run token regex: feature-record, dispatch-guard, validate-digest; validate/fix token overlap with prune-run-evidence. |
| B-10 | chore | Identical shell-assignment prefix: bash-write-guard and harness_yaml. |
| B-11 | chore | Identical perspective-heading pattern text: check_state/brief and handoff_done_when (flags differ by search scope). |
| B-12 | chore | Identical expertise-section regex: check-expertise and expertise-merge. |
| B-13 | chore | Identical persona matcher: expertise-merge and inject-expertise; segment matchers differ in first-character constraint. |
| B-14 | chore | DEC-id matchers: check-skill-refs, harness_yaml, gen-decisions-index; anchoring/capture differences must be preserved. |
| B-15 | chore | Short-name renames outside check-domain.py (SEV, OPS, SEP, RAW, _WHAT, PIN, …) per the T-01 naming rule. |
| B-16 | enhancement | Mechanical lint for flag aliases and duplicate matchers per concept, deferred by the grilling. |
| B-17 | bug | Digest validator / qa contract: a signed regression-only automated SC has no `fail_first` evidence to give, yet the contract reads a green suite without one as FAIL (validator Q-01). Make the regression-only case expressible. |
| B-18 | bug | `handoff_done_when.py` `brief-sc:` resolver matches only `SC-NN:` lines; a by-perspective BRIEF writes `- SC-NN (perspective):`, so `brief-sc:` pointers never resolve for that shape (hit writing handoff-build.md). |

## Not done here

- Push, PR, merge, `gh-sync.py ship` and backlog issue creation are the main session's on your instruction.
- The main checkout's copy of check-domain.py keeps `_I`/`_RE_HANDOFF_CYCLE` until this branch merges; it governs the hooks meanwhile.
