# BUG-2349 — code review c1

PASS — T-01 satisfies the bounded implementation contract and authorized unit amendment. No findings. Main retains SC-04's post-merge verification obligation.

Reviewed `e239d88156c508c948d49cd31238ea13b3b39865..0174f364483df5c8d49f04e35d2308e5dca33257`. Git confirms merge-base equals the assigned base; feature.json carries the assigned pin. Six commits inspected; no `[harness:human]` commits. Only feature.json is dirty, inside feature records. Earlier pin: `2a476ca04c3516bdac3e69dfe66cec7eb372e243`; its successor range adds the unit floor and records, with no production/integration changes.

## Stage 1 — spec compliance

- **SC-03 inspection:** `.claude/skills/harness/bin/plan_merge/union.py:517-521` chooses the proposal head when base items are empty and proposal items exist; otherwise base precedence, proposal fallback and absent-key behavior remain. `_aligned_items` runs first (`:475-477`), enforcing parsed-item/text-range alignment before selection. Implementation changes remain confined to union.py; tests comprise the integration file plus the explicitly advisor-authorized unit amendment (`notes/unit-floor-c1.md:7-18`, feature.json amendment judgements).
- **SC-01:** `tests/integration/test-plan-merge.py:5092-5116` independently drives both keys through CLI apply and asserts literal reloaded fields. Baseline receipt `notes/receipts/sc01-sc02-red.txt:682-712` records both exit and reload failures, not import errors. Current green receipt records both successes.
- **SC-02:** integration `:5119-5129` asserts exit 5, the alignment diagnostic and unchanged bytes for a non-empty flow list. The fixture uses a valid decision mapping to reach the formatting refusal. No relaxation of `_aligned_items` or `_merge_union_key`.
- The delegated option-A amendment adds exactly `tests/unit/test-plan-merge-union-head.py` and its verify invocation, with no production delta or integration-as-unit waiver. Unit `:53-76` tests real in-process `apply_merge` for both empty keys and base-head retention. Baseline `receipts/unit-red-base.txt` records six behavioral failures loading e239d881's union.py and three passing preservation checks; amended green receipt `receipts/c1-verify-green-prefix.txt:687-701` records nine passing checks, suite success and scratch round-trip. These are inspected receipts, not reader executions; green was captured before committing the unit file atop 2a476ca0, explicitly recorded at receipt line 1.
- **SC-04 pre-merge:** the same green receipt identifies checkout SHA, command, output, reloaded D-01/choice x and rc=0. **Main still owns the post-merge literal verify with explicit surviving owner-root override and merged tool SHA. This is not a pre-merge failure.**
- Product `docs/spec.md`, `docs/decisions.md`, `docs/architecture.md` are absent (product docs directory inspected); no product guidance invented or substituted. No plan decisions are declared. The settled unit-floor and dismissed neighboring variants are not reopened.

## Stage 2 — code quality

No fail-open or silent-failure regression found: alignment refusal precedes selection, selector absence behavior is unchanged, and splice reload/schema/union-id verification remains intact (`union.py:43-138`). The production change is one bounded predicate, with no new allocation or seam. Unit assertions bind actual output, pair absence of inline `[]` with presence of a block head and literal reloaded items, and preserve a distinctive base-head comment. Reverting the predicate defeats both positive cases (recorded baseline red); unconditional proposal precedence defeats the comment assertion. No decoration-only tests found.

After validator lead explicitly authorized static grading only, ran `python3 /Users/molchairuangutai/GitHub/harness/.agents/skills/harness/bin/code-grade.py --base e239d88156c508c948d49cd31238ea13b3b39865 --head 0174f364483df5c8d49f04e35d2308e5dca33257`: exit 0, **PASSING: 9**, no high-severity or grade-2 records. Production selector and four integration functions are grade 4. Unit `check` and `merge` are grade 5; unit empty-base case is grade 4 (cyclomatic 5, cognitive 7, ABC 16.2), preservation case grade 4 (4/2/11.4). `code_grade: pass` is now measured. This resolves the initial no-execution authorization blocker without a fix cycle. No tests, mutants, build, lint, formatting or source edits performed.

## Principles applied

- **Delete First** — accepted the existing selector's one-condition replacement rather than a parallel merge path; declined speculative neighboring coverage beyond the delegated bounded repair.

Findings/spec violations/open questions: none. Outstanding ship obligation: main's SC-04 post-merge receipt.
