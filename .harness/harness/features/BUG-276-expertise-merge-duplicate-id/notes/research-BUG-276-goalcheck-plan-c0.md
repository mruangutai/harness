# Goal-check — BUG-276 drafted plan vs the operator's stated intent

**Does this plan deliver the operator's stated intent? Yes for the narrowed defect, with three
exceptions — two of them blocking at signature.** The guard the operator asked for (within-one-
proposal duplicate id, refuse at exit 11, ops convention) is specified correctly, measured
correctly, traced, and testable. But (a) the plan instructs a docstring edit that makes its own
SC-06 unmeetable, (b) the BRIEF attributes the issue's field losses to a tool that did not exist
when they happened, and (c) one genuinely different silent-reduction route survives the guard, so
D-06's stated reason — "the measured loss is fully closed by refusing the ambiguous input" — is
false as written. Nothing here argues for widening scope; F-01 is a separate bug, F-02/F-03 are
edits to the plan's own text.

## Findings

- **F-01 · med · the dropped clause is not fully discharged.** `parse_expertise`
  (`.claude/skills/harness/bin/expertise-merge.py:73-95`) keeps only title / `SECTION_RE` /
  `ENTRY_RE` / indented-continuation lines, and `render` (`:103-111`) emits only what was parsed —
  so any other base line is discarded at exit 0, on **both** the apply and ops paths (both call
  `parse_expertise` then `render`: `:481-532`, `:577-586`). Measured directly against the pre-fix
  module: `- ARCH-01: x` (4-letter prefix) and `- P-01:` (no space after the colon) vanish, entry
  count down, no exception; `## Open Questions` (two-word header) is dropped and its entries are
  relocated into the preceding section. `check-expertise.sh:152-154` *would* flag such a line, but
  never sees it — the drop precedes the write, exactly the blindness the BRIEF already names for
  duplicate ids (`BRIEF.md:14-16`). **Position:** the guard closes the route the operator narrowed
  to; a second silent-reduction route remains reachable. It is not in this ticket's scope, and it is
  why the monotonic/content-presence clause the issue asked for is not redundant. Route audit is
  exhaustive over the three routes named in the dispatch: post-guard union (`compute_union:114-140`
  — only ever appends to `list(base_entries)`, so it cannot reduce), ops (`_rebuild_section:334-348`
  reduces only on an explicit `drop`, which prints `DROPPED`), and parse/render (loses). No live
  Expertise file trips F-01 today: a probe over every `.harness/expertise/*.md` and
  `.harness/*/expertise/*.md` found zero unmatched lines.
- **F-02 · high · the field evidence cannot be this defect.** `expertise-merge.py` was added
  2026-08-21 (`git 47a9935a`, FEAT-30); the losses the issue measures are dated 2026-08-12
  (`a810c115`, "FEAT-13 close-out: two lost Expertise lessons recovered"). No `compute_union` existed
  then — those losses came from whole-file-rewrite distillation (DEC-95/DEC-125), the thing this tool
  was built to end. `BRIEF.md:12-13` nonetheless asserts "Issue #276 measured the same loss in the
  field" and lists P-09 / P-06 / P-10 / G-06. **Position:** the planned guard would **not** have
  prevented those losses; high confidence, from commit dates on both sides. The defect is real
  regardless — independently measured at 6d969ed3 (`BRIEF.md:7-11`, reproduced here). Fix the BRIEF
  prose before signature; do not widen the fix.
- **F-03 · high · the plan makes its own criterion fail.** `plan.yaml:39` (D-05) and T-01 step 3
  (`plan.yaml:126-129`) instruct adding codes 9, 10, 11, 12 to the docstring table
  (`expertise-merge.py:14-19`). `apply` can return 6, 7, 8 (`:492-510`), 9 (`:470-474`) and, after
  the fix, 11 — never 10 or 12, which only `resolve_ops` raises (`:274`, `:154`). `SC-06`
  (`BRIEF.md:80-81`) grades "no code listed that `apply` cannot return". Executed as written, T-01
  fails SC-06. **Position on point 4: trim to 9 and 11.** Only 11 is forced; 9 is a genuine
  omission on the apply path and costs one line; 10 and 12 are unrequested ops-path work that
  contradicts the criterion.
- **F-04 · low · the operator's premise is inverted, and only the BRIEF says so.** Confirmed
  first-wins myself: `compute_union`'s `if eid not in seen` append (`:136-138`) keeps the first
  occurrence, so `{P-02 ALPHA, P-02 BRAVO}` merges to `P-02 ALPHA`, conflicts empty, exit 0. The
  dispatch says "keeping only the last-seen one". `BRIEF.md:10` and `plan.yaml:69-74` both record
  FIRST-wins, so the record is right — but neither says the dispatch wording was wrong, so the
  operator can sign without noticing their model was inverted. **Position:** the plan is right to
  follow the measurement; say the correction out loud at signature.
- **F-05 · med · the verify commands are name-attestable.** `plan.yaml:62-65` and `:150-153` grep
  for literal `PASS  <name>` lines; `test-expertise-ops.py:387` and
  `test-expertise-merge.py:1342` print that for any truthy `ok`. A check *named*
  "u23a: different texts refuse with code 11" can therefore pass on a weaker assertion, and the
  mandated red-first observation (`plan.yaml:106-107`, `:198`) leaves no trace in the verify's own
  output. The intent text pins the real assertions, so this is a review burden, not an unwritable
  task — worth naming in the reviewer's dispatch.
- **F-06 · info · one trace carries no new work.** REQ-03 / SC-04 trace to T-02 (`plan.yaml:139`),
  but T-02 explicitly forbids adding regression sub-cases (`plan.yaml:195-197`); the evidence is
  pre-existing `case_add_only_compatibility` (`tests/integration/test-expertise-merge.py:614`).
  Legitimate reuse — but the trace should say so, or goal-check will read it as new evidence.

## Point 5 — success-criterion sufficiency

**Position: SC-01..SC-05 are sufficient for the narrowed intent and none is satisfiable while the
defect is reachable.** SC-03 (`BRIEF.md:67-71`) asserts on `compute_union` directly and demands the
pre-fix red, so it cannot green on the pre-fix function; SC-05 (`:76-79`) reaches the `base_bytes
is None` branch (`expertise-merge.py:489-490`) that no unit call touches. Their *automation* is
weaker than their wording by F-05. **SC-06 is not gate-bearing** — `verify: inspection`, no command,
graded by a reader — and as written it is failed by the very task that traces to it (F-03).
Coverage: every REQ has a task; every SC has a task; the only task step no requirement forces is
T-01 step 3's codes 10 and 12.

## Open questions for the operator

- Q1 (blocking): F-03 — trim D-05 to 9 and 11, or widen SC-06 to the whole tool? One of the two.
- Q2 (blocking): F-02 — strike the field-loss attribution from `BRIEF.md:12-13`, or restate it as
  "a different mechanism, since fixed"?
- Q3 (non-blocking): F-01 — file the parse/render drop as its own bug, and let D-06 keep the
  exclusion but with a truthful reason?
