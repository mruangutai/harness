# Security review c1 — BUG-2161

PASS — no exploitable security regression found. No security-specific must-fix was routed; F1 and GC-01 are resolved by inspection in T-01. This is not a ship/UAT verdict.

## Reviewed identity and scope

Exact range: `1ef80c260aed1e288981a9cbea842b7c394c0419..b5929a92e87a7792ddaa7ea99e3f849a699a82ab`. Git diff confirms four changed paths: gh-sync.py, the unit and integration abandonment suites, and the fix receipt. The diff from production fix `0474ae66ac6a9dc378da7006365e49b04eb85a52` to the review tip changes only the receipt. The three reviewed code/test files have no working-tree differences from the exact tip. The receipt's uncommitted final head annotation is not part of the pinned delta.

In scope: changes narrow GitHub mutation authorization and gate local evidence deletion. Tests and receipt introduce no production entry point. This independently assesses the touched lifecycle surface rather than assuming earlier review coverage.

## Findings and routed fixes

- **F1, high, substance, code-reviewer, T-01: resolved by inspection.** `gh-sync.py:1823-1832` prunes only after an already-abandoned read or successful `_record_station`. The helper returns False for absent plan/nonzero station command (`:675-689`), so refusal retains evidence and reports FAILED. Unit additions distinguish refused/successful/already-abandoned paths; integration adds an absent-plan retained-evidence case. No execution claimed.
- **GC-01, high, substance, goalcheck, T-01: resolved by inspection.** `_hold_back_sources` (`gh-sync.py:1663-1682`) removes protected parent/task numbers before planning; `cmd_abandon` uses authoritative parsed sources and this acting record (`:1767-1774`). Both executor close/comment targets and detach parent come from that filtered record (`:1835-1848`), preventing the alias mutation path without opt-in. With opt-in, existing overlap planning remains. Added unit/integration cases pair held aliases with positive disposal.
- **New security findings: none.** Source parsing admits integers, excludes bool, and precedes mutations (`:474-502`). New reporting adds no shell/SQL/template interpretation; existing GitHub writes retain list-form argv and original reason-file provenance. Full four-path delta contains no credential material or new dependency, auth route, request destination, data disclosure, or deletion target. The existing operator-owned shared-ticket risk remains explicitly accepted by D-01/DEC-203 §8, not a new finding.

## Authority and limits

Read full must-fix-c1 and fix receipt, BRIEF, T-01/D-01–D-03, product AGENTS, SPEC §§9/11, DEC-138, DEC-203 §8, DEC-238, and PRINCIPLES. SC-06's no-shared-ticket-check constraint remains intact in the changed execution path (`gh-sync.py:1767-1774`); T-02 docs and settled F2/F3 are not reopened. No tests, grading/check scripts, builds, lint, formatting, goalcheck, or live GitHub writes run. QA owns execution evidence; SC-07 remains post-merge operator acceptance.

Open questions: none.
