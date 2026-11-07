# BUG-2161 — code review c1

PASS: F1 and GC-01 are resolved by inspection; no blocking regression. One new test-only complexity advisory, owner T-01.

Reviewed exact fix range `1ef80c260aed1e288981a9cbea842b7c394c0419..b5929a92e87a7792ddaa7ea99e3f849a699a82ab`. Git confirms production/test changes belong to `0474ae66ac6a9dc378da7006365e49b04eb85a52`; the tip adds only receipt SHA lines. The receipt's final head annotation is uncommitted as disclosed. No human-tagged commits in the cumulative origin/main merge-base range (`e817d3572087c9b9052e1f673c2ee177403a5896`). No dirty production/tests/docs; dirty feature.json, station-only plan change and notes are lifecycle records. feature.json deliberately retains c0 review_sha: this is the dispatched independent fix-tip assessment, not a new pin. No pin written or checkout created.

## Stage 1 — spec compliance / routed discriminators

- **F1: resolved** (original high/substance/code-reviewer/T-01; SC-03/D-02). `gh-sync.py:1824-1833` short-circuits existing abandonment or requires `_record_station` True before pruning; False reports FAILED and keeps evidence. Actual refusal returns False at `675-688`. New unit matrix covers refusal, successful write and already-abandoned bypass (`tests/unit/test-gh-sync-abandon-sources.py:320-337`); integration asserts retained evidence and absent plan on refused recording (`tests/integration/test-gh-sync-abandon.py:1217-1231`). Existing abandoned retained/absent-runs cases remain at `1103-1125`. Successful-prune fixture now supplies a writable plan rather than relying on the removed defect (`52-57`).
- **GC-01: resolved** (original high/substance/goalcheck/T-01; SC-01). Authoritative plan sources are read before planning (`gh-sync.py:1764-1770`). `_hold_back_sources` removes protected task numbers and clears a protected parent (`1663-1681`), so executor `1833-1845` cannot comment/close/reseat/label those numbers or indirectly detach children from that parent. Both dry and real paths report the held role and flag (`1684-1688,1768-1774`). Tests pair each alias's zero-write assertion with nonalias progress and opted-in disposal (`unit:284-318`; `integration:1182-1215`). With opt-in, protected is empty and the existing overlap planner is unchanged. Without aliases, parent and sorted task entries are identical; plan/apply and close-before-Backlog order are unchanged.
- **F2: leave.** Signed SC-02 requires Backlog after close, not comment last; T-01 preserves settled operation order. `_source_plan` and executor ordering are unchanged. F3's accepted advisory and T-02 remain settled.
- **SC-06 inspection:** exact-tip DEC-203 §8 (`.harness/harness/docs/DECISIONS.md:6361-6385`), unchanged index row (`DECISIONS-INDEX.md:201`) and CLI usage/flag refusal (`gh-sync.py:7-16,2571-2581`) retain opt-in, reason provenance, local finalization and no corpus-check contract. These documentation surfaces have no working-tree or fix-range diff. SC-07 remains post-merge operator UAT, not claimed here.

## Stage 2 — quality

No new fail-open or silent-failure defect found. Held-record filtering occurs before any remote mutation; refusal precedes pruning. The filter earns its seam by removing both direct targets and parent-mediated detach authority. Read-only simplification assessment found no necessary change; no build-side simplify/apply or repin performed. Receipt contains no Principles applied claims requiring reconciliation.

Mandatory pinned mechanical grading executed over `e817d3572087c9b9052e1f673c2ee177403a5896..b5929a92e87a7792ddaa7ea99e3f849a699a82ab`: 27 passing records, no high records, two grade-2 test helpers:

- **New advisory: med/substance/code-reviewer/T-01**, `tests/unit/test-gh-sync-abandon-sources.py:270`, `touches`: cyclomatic 9, cognitive 17, ABC 13.0, driver cognitive. Nested event/argument predicates increase the maintenance cost of distinguishing direct issue writes from board writes; a missed predicate can undercount protected writes. Accepted test-only grade-2 reason: one scanner handles the two existing event shapes and checks endpoint arguments as well as direct issue commands; keeping these recognizers together makes the zero-write oracle explicit. Nonblocking; no requested repair.
- **Settled F3**, integration `main._src_ops:864`: cyclomatic 12, cognitive 3, ABC 17.5, driver cyclomatic. Existing accepted reason retained: four related per-source log recognizers return positions/presence together; comprehensions drive cyclomatic count while cognitive load remains 3. Not reopened.

## Principles applied

- Model the Domain: assess protected identities once in the acting record rather than demand guards at every executor branch.
- No more specific than necessary (PRINCIPLES §6): do not invent comment-last ordering.
- Never falsify the record (§15): distinguish inspection and grading from unexecuted runtime tests.

No tests, builds, linters, formatters, mutants, goalcheck or live GitHub writes performed. Regression assertions were inspected, not executed; QA owns signed/configured runner evidence. Open questions: none.
