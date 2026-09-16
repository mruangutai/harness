# Plan-panel c4 — scope reader (spec compliance) — BUG-1286-test-tree-enforcement

**BLUF: the amendment holds up under adversarial re-check. No new must_fix. The two-group vocabulary
is coherent across all five cited sites, SC-18's graders exist exactly as described, the widening
breaks nothing authored under the narrower rule, Fix 1 (T-03/T-04 output contract) cannot fail on a
faithful audit of a clean tree, and every `verify:` clause is runnable, non-vacuous, and correctly
ordered. REQ tracing has zero orphans and the task DAG is a valid topological order.**

## 1. Two-group split coherence — checked at all five cited sites, no blanket claim survives

D-01 `choice`/`because` (plan.yaml:34-65), T-01 constants + predicate (`:273-291`), T-01 cases 8/10
(`:386-401`), T-03 disposition vocabulary incl. `out-of-vocabulary` (`:471-476`), T-05's DEC-213
amendment text (`:557-608`), BRIEF SC-18 (`BRIEF.md:144-153`) and the Verification-gaps bullet
(`:190-198`) — I re-derived the guard predicate and the census disposition logic by hand against
every overlap case (restricted-only+source-ext, restricted-only+non-source-ext, agnostic-only at any
ext, both-tuples-match) and they agree in every case; none of the five sites states or implies the
extension restriction is repository-wide. Grep sweep for surviving blanket claims (`extension`,
`restrict`, `whatever.*extension`) over `plan.yaml`+`BRIEF.md` confirms every hit is explicitly
scoped to group one / the bin clause / the agnostic pair. Matches goal-check's independent sweep
(`notes/research-...-goalcheck-plan-c4.md` §"Fix 2").

## 2. SC-18's graders exist exactly as described — confirmed

BRIEF SC-18 names T-01 case 10's two paths (`.harness/tools/session_test.md`,
`.harness/evidence/run.test.jsonl`) and case 8's pair
(`.harness/notes/probe-something.md`/`.py`) verbatim; T-01's case 8 (`plan.yaml:386-388`) and case
10 (`:394-401`) text match those citations exactly, same paths, same direction, same "no finding
while ... does" framing. Both cases are separately gated (D-01, T-05 amendment text explicitly
forbids collapsing them). No mismatch.

## 3. Widening vs. assertions authored under the narrower rule — independently re-measured, holds

Re-ran `git ls-files` in the worktree with `fnmatch` over both pattern tuples myself (not trusting
the amendment's own note): **TOTAL 85, OUTSIDE 9, VIOLATIONS 0** — identical to T-03's "Expected
measurement" text and to the goal-check's independent `git ls-tree` cross-check. All 9 outside rows
match `probe-*` only (7 `.md`, 1 `.jsonl`, 1 `.ts` = the FEAT-44 exception); zero match either
agnostic pattern. Case 1's fixture and case 10's fixture are explicitly kept separate
(`plan.yaml:399`: "Assert it in this case and not by widening case 1's fixture"), so SC-06's
one-element exact-equality list is unaffected by the new case. T-03's `TOTAL 85 OUTSIDE 9
VIOLATIONS 0` and T-04's anticipated per-row dispositions are both confirmed accurate against the
real tree at HEAD (`c040c319`), not stale from the pre-amendment vocabulary — no `qa-tree-audit.md`
draft exists yet in `notes/` to have gone stale.

## 4. Fix 1 on its merits — no reading of a correct note fails T-04's verify

T-04's `verify:` (`out=$(... --against ...) && printf ... | grep -q ...`) takes the census exit
status per the amended combined rule ("non-zero on any row difference AND non-zero on any violation
row"). Traced every way a *correct, faithful* note could still redden this: (a) timing drift from a
later task's commit — T-05 only touches `DECISIONS.md`/`DECISIONS-INDEX.md`, whose basenames match
neither pattern tuple, so the measured row set is stable across the whole build; (b) a second
non-`text` fenced block in the note colliding with `--against` parsing — `baseline()`'s regex
(`tests/manual/suite-census.py` — literal `` ```(?:text)?\n(.*?)\n``` ``, confirmed by reading the
file) only recognizes a bare or `text`-tagged fence, and any mis-fencing would zero out the parsed
row set and fail T-04's own verify at build time, which is a self-correcting gate, not a silent
divergence. The only reading where a *faithful* note fails is a tree that genuinely holds a
violation — which the task's own text calls out as an intended fail ("the audit FAILS: report it
rather than reclassifying it") — that is fail-closed working as designed, not a defect.

## 5. `verify:` clause integrity — all five pass literal-text inspection

T-01/T-02: no grep, run real test files, non-vacuous by construction. T-03: grep target
(`probe-session-accessors.ts.*documented-exception`) confirmed present in the real tracked tree
(independently verified via `git ls-files`) and requires the not-yet-existing `tree-audit`
subcommand to resolve it — not vacuous. T-04: same anchor, gated additionally by the combined
`--against` exit rule — not vacuous, depends on T-03. T-05: both `grep -q` targets confirmed
0-hits-today by direct read (`grep -c "tracked test-shaped file outside" DECISIONS-INDEX.md` → 0;
`grep -c "Amended by BUG-1286-test-tree-enforcement" DECISIONS.md` → 0), and the task text itself
mandates the same preflight check before editing — non-vacuous by construction, and the
"Amended by ..." house-style precedent (`DECISIONS.md:4908,5296,6174`) is real, confirmed present.
All five run from repo root with relative paths, consistent with sibling tasks' convention.

## Orphan-REQ / DAG check

REQ-01..REQ-08 each traced by ≥1 task (T-01: REQ-01/02/03/04/05/08; T-02: REQ-01/02/03; T-03/T-04:
REQ-06; T-05: REQ-07) — zero orphans, zero tasks citing a non-existent REQ. `depends_on` graph
(T-01→{T-02,T-03}, T-03→T-04, {T-01,T-02}→T-05) is a valid DAG, no cycles; no task's `verify:`
depends on state a predecessor deletes, and no successor is required to backfill a predecessor's
`verify:` assertion.

## Off-table items — not re-litigated

D-05's archival coupling: description re-checked against `tests/manual/probe-omp-session-accessor.py`
lines 54-55 (the `PROBE` assignment) — accurate, no new inaccuracy found. Vocabulary-unification and
`tracked_paths_fn` injection-seam alternatives: not revisited, per `review-harness-eng-lead-plan-c0.md`.

## Findings

None. This is a genuine clean pass, not an unchecked one — see sections 1-5 above for what was
independently re-derived or re-measured rather than taken on the amendment's word. No `high`,
`critical`, or `unrated` finding to escalate.
