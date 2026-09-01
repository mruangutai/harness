# UI Review — FEAT-50-run-artifact-integrity — pinned SHA dca2d3d

**Mode:** B (post-build), scoped by measurement. **Verdict input: PASS, severity_max: low, must_fix: []**

## Census (37 changed files, `9f2a070..dca2d3d`)

`git diff --stat` over the full pinned range: 0 files match `.html/.css/.scss/.tsx/.jsx/.vue/.svelte/.less`.
The changed set is entirely `.sh` / `.py` (hook logic + tests), `.md` (BRIEF/STATE/notes/DECISIONS),
`.json` (feature.json), `.yaml` (plan.yaml). No `DESIGN.md` exists for this feature (checked: not
in the diff's name list, not present in `notes/`) — no rendered UI contract to audit, consistent
with the repo-tier Expertise default (files-only, no build step).

The only plausible surface, per dispatch: **CLI/hook operator-output messages** the changed gates
emit. I enumerated every added `print(...)`/`deny(...)` call in the diff (excluded: test-runner
self-check prints in `test-*.py`, which are developer test output, not operator gate output) and
audited each against REQ-01/REQ-02/REQ-08/SC-18.

## Findings

**REQ-08 / SC-18 (checkout-binding message names both target and worktree) — SATISFIED, both routes.**
- `check-domain.sh:733-735` (`feature_checkout_guard`, Write route): `"{target_path} is a feature
  artifact whose write belongs in worktree {expected}."` + `"Write this artifact in {expected}, not
  the main checkout."` — names both.
- `bash-write-guard.sh:718-720` (`feature_checkout_guard`, Bash route, via `deny()`): `"{absolute_path}
  is a feature artifact whose write belongs in worktree {expected}. Write it there, not in the main
  checkout."` — names both.
- `test-bash-write-guard.py:865-888` (`bash-feature-checkout-main`/`-short`) asserts both substrings
  present in stderr — confirms the contract is test-backed, not just narrated.

**REQ-01 (empty-return refusal) — actionable.** `validate-digest.py:1020-1025`: exit 2, message states
the fact ("an empty final message... satisfies no field of the digest contract") **and** the remedy
("Return again with the three-part VERDICT/DIGEST/artifact block") — passes the G-13 bar (fact +
remedy, not a bare exit code).

**REQ-02 (pass-through distinguishable from validated pass) — satisfied by asymmetry, not just wording.**
`validate-digest.py:1014-1019`: absent/null → exit 0 with explicit `"...the return was NOT VALIDATED"`
on stderr. Compare the validated-success path, `validate-digest.py:1642-1645`: exit 0, **silent** (no
stderr at all) when `errs` is empty. So an operator watching stderr sees a message only on the
unvalidated path — validated and unvalidated pass-throughs are not merely worded differently, they are
structurally distinguishable (silence vs. stated gap). Matches the BRIEF's REQ-02 language exactly
("stated in a form the dispatching tier can see").

**Low, non-gating: bash-write-guard.sh's `feature_checkout_guard` denial carries a domain-flavored
boilerplate that doesn't fit this checkout question.** `bash-write-guard.sh:647-651`'s shared `deny()`
helper appends, after every reason: *"File changes go through the Write tool, where your domain is
enforced... If the file should be yours, raise it as an open_question."* That coda answers a *domain*
question (who may own this path) but `feature_checkout_guard` is a *checkout* question — the writing
agent already owns the artifact; it just targeted the wrong worktree. Telling it to "raise it as an
open_question" if "the file should be yours" is a non-sequitur here (the file already is theirs).
This is not a new pattern introduced by this diff: `deny()` was already reused this way for the
structurally identical `out_of_place_worktree` case before this change (base `bash-write-guard.sh:640-652`,
unmodified by this diff). The new `feature_checkout_guard` call site (`bash-write-guard.sh:778`) just
extends an existing convention to a new call, and the required content (target + worktree, SC-18) is
present and correct regardless of the coda. Per P-11/G-11 (extending remedy scope into an established,
untouched convention is not this review's call), I record this as a low/advisory note rather than a
`must_fix`. Contrast: `check-domain.sh`'s sibling `feature_checkout_guard` (Write route) does **not**
carry this coda — its message is purpose-built and reads cleanly on its own.

## Not in scope / not found
- `.claude/skills/harness-team/SKILL.md` diff (+5/-2, agent-instruction prose, not an emitted runtime
  message) accurately describes the new REQ-04 refusal behavior; checked for drift against the code
  it documents, none found.
- `DECISIONS.md`/`DECISIONS-INDEX.md` additions are the decision record, not operator-facing runtime
  output — out of this role's remit per dispatch (CLI/hook operator output only).

## Open questions
None blocking.

```yaml
VERDICT: PASS
DIGEST:
  headline: No rendered UI in the pinned diff; audited CLI/hook operator messages (REQ-01/02/08, SC-18) — all satisfied, one low advisory note
  mode: B
  in_scope: true
  severity_max: low
  findings: 1
  must_fix: []
  states_unspecified: []
  contract_violations: []
  a11y: []
  open_questions: []
  files_touched: []
  expertise_update: []
artifact: .harness/harness/features/FEAT-50-run-artifact-integrity/notes/review-harness-ui-reviewer-feat50-pinned.md
```
