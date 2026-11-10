# PASS — T-01 security review

No independently exploitable security regression identified. In scope: this change deliberately narrows an enforcement gate using repository-authored status and historical comparison inputs. Reviewed exact full range `b7af829c0207522b43f978b5275a2ebdc96b3210..688c5ef5e3b6e0dd694afb3d6476c915934501d4` and rework `fe49c8df3807d875f2cd44410559966cc836b9ab..688c5ef5e3b6e0dd694afb3d6476c915934501d4`, not HEAD. Prior c0 security review was in scope with no independently exploitable finding.

## Boundaries and closure

- **T-01 / SC-01–02, tampering:** `check_state/ctx.py:55–75` counts column-zero status keys independently of values, including quoted keys, before accepting the single plain `done` value. The prior done-plus-list/empty/number/quoted-key ambiguity now retains subject checks by source inspection. Missing/unreadable/non-UTF-8 status remains unshipped. `runner.py:284–323` escapes the explicit selector's glob component and keeps preflight refusal before the shipped fast path. Treating a deliberately written single `status: done` as shipped is the approved DEC-252 boundary, not an independently discovered authorization bypass.
- **T-01 / SC-03, input handling:** `board.py:138–156` excludes booleans and non-ASCII digit strings before conversion; `artifact_accessors.py:145–178` translates `opt_int` ValueError into the existing not-a-recorded-issue-number refusal rather than accepting the value. This repairs the named superscript-digit failure at both layers without changing `feature_json_write.opt_int`. The strict census can record its documented refusal and `_landed_entry` can re-read shipped JSON for usable comparison claims. Rework tests bind duplicate subject selection and malformed historical parent/issue values beside a real collision; their execution is QA-owned, not claimed here.
- **T-01 / SC-03, historical data:** `ctx.py:83–107,423–453` keeps shipped raw mappings lazy and separate from active-record validation. `board.py:184–204,244–260` uses those fields only as collision ledger keys/diagnostic text, not subprocess arguments, executable templates, paths or authorization. No new credential read, network destination, external sink or cross-user data grant appears in the patch.
- **T-01 / SC-04:** retirement of INV-28/30 and the lost done-only handoff requirement are explicit DEC-252 tradeoffs, not unreported security regressions.

## Full changed-surface census

All 21 changed paths considered: seven runtime/schema files (`artifact_accessors.py`, `check-plan-routes.py`, `check_state/{board,ctx,runner,table}.py`, `feature-schema.json`) are in scope for enforcement/input/output review. Twelve test/fixture files are test-only; subprocesses are list-form, audit logs remain local fixture output, and the corpus export consumes an operator-selected local repository. The two decision/index files document the approved narrowing and have no executable surface. Full-patch credential/injection-term scan found no introduced secret or credential-bearing output. No dependencies added.

## Evidence limits

Read BRIEF, T-01, prior validator digest, binding grilling note and DEC-252; absent PRODUCT guidance remains disclosed. Source inspection closes the two named mechanisms for this security assessment; no tests/builds/linters executed. `notes/red-first.md` remains a builder receipt, not independently reproduced fail-first evidence. Historical `merge-602c81a385afae8871157a4fcb5b65e63c3e4f32.log` records 146 files and `verify-exit=0`; measured git diff from the review pin to that commit contains only feature.json `review_sha` changing from `09ac5a4e…` to `688c5ef5…`, not product code. This is not a claim of a fresh full verify at the exact review pin. QA owns executed regression/matrix closure; known INV-33 status drift is not a new security finding.

Findings: none. Must-fix: none. Open questions: none (existing c0 Q-01 is not duplicated). Source files changed: none.
