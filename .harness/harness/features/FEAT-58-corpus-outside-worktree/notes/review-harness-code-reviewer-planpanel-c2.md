\
# FEAT-58 — plan-panel cycle 2, scope reader — re-derived, not narrated

**Verdict: no gating finding. Two new low/med findings on the amendments themselves; three
candidate gaps the dispatch flagged are re-derived as already closed and are named once, not
re-raised.**

Read at the worktree-prefixed paths throughout. `plan.yaml` and `BRIEF.md` untouched.

## Re-derived structural counts (not taken from the amendment record's own prose)

- REQ-01…REQ-12 (12) each appear in at least one task's `traces:`; no orphan.
- SC-01…SC-15 (15) each appear in at least one task's `traces:`; no orphan.
- No task's `traces:` cites a REQ/SC id absent from `BRIEF.md`.
- 16 tasks (`T-01`…`T-11`, `T-13`…`T-17`; `T-12` absent). 15 decisions (`D-01`…`D-15`).
- `depends_on` — every referenced id resolves to a real task; no reference to `T-12` anywhere in
  `tasks:`/`depends_on:` (its 4 remaining mentions are the historical `D-13` prose and 3 inside the
  untouched `panel:` cycle-1 record). No cycle found by hand-trace of the full edge list.
- `T-06` and `T-17` both edit `check-domain.sh` and both carry `test-check-domain-worktree.py`
  forward in their `verify:` chains (pre-existing regression suite, not created by either task).
  Grepped that file for the specific functions `T-17` fixes (`feature_checkout_guard`,
  `claim_checkout_guard`, `worktree_for_feature`, `claim_worktrees`) — the existing suite's
  cross-worktree cases (`SC-02b`, `wrong-checkout`/`bug895`) exercise the *layout* guard and the
  *session-root* guard, a different mechanism from the two functions `T-17` widens. No pinned
  assertion in that file contradicts either task's edit. Clean.

## Confirmed already closed by the amendments — not re-raised

- **G-9 (T-17 / SC-15).** `SC-15` now reads by outcome, per clause, and its red-first sentence is
  scoped explicitly to `(a)`/`(b)`/`(c)` — the two DENIAL tiers plus the `None`-refusal — with `(d)`
  the report tier stated in the criterion's own text as *"does not satisfy the criterion... not the
  denial behaviour."* `T-17`'s task text mirrors this split case-by-case. Fixed at the right tier.
- **T-03/T-04 call-count pins.** Deleting the prose "resolve once" pins and centralizing the one
  instrumented call-count assertion in `T-06` case (f) is the operator's Q4 ruling ("keep exactly
  one pin"), not an accidental loss of coverage: `D-11`'s relocation deletes the per-site branch
  structurally (one `corpus_features` call written at the top of each of the five relocated
  readers), so there is no multi-call-site risk in `check-state.sh`/the four validators the way
  there is in `check-domain.sh` (which has two separate consumers — `_hardlink_plan` and
  `SWEEP_GLOBS` — that could disagree on a mid-run mutation, which is what T-06(f) actually pins).
  Accepted residual, matches the c2 goal-check's own conclusion.
- **T-12 cut / "a whole-corpus read must be stated."** `D-05`'s residual is stated at its true
  width (`T-13`'s lint and `T-07`'s discovery scan both bound to tracked files under
  `.claude/skills/harness/bin/` only; a bypassing reader elsewhere is caught by neither, and D-05
  says so). This is G-8, already applied. No further gap found.

## New findings

**F1 — med — `T-06` traces `SC-04`, but `check-domain.sh`'s corpus calls structurally cannot
produce the refusal `SC-04` describes; the reachable refusal is `SC-05`'s shape, which `T-06`
does not trace.**
`D-04` binds `check-domain.sh`'s hardlink and sweep enumerations to `provider="path"` only
(*"identity and inode reads resolve path-only at the corpus root"*). Per `T-01`'s own spec, the
completeness/short-corpus check (`SC-04`'s "prints N of M") compares *root's own materialised
count* against *the resolved set* — for `provider="path"` those are the same on-disk listing by
construction (`T-01` case (i) tests `provider="path"` only for the `ValueError` paths, never for a
short-vs-resolved refusal; only history-provider cases (c)/(d)/(e)/(f) exercise "N of M"). So
`corpus_features(..., provider="path")` can only ever raise the *root-unresolvable* shape (no `N of
M`, `SC-05`'s territory) — never the *short-corpus* shape `SC-04` demands ("a fixture whose corpus
root holds M feature directories with fewer than M materialised... prints N of M"). `T-06`'s own
test cases (a)-(f) confirm this in practice: case (c) is "corpus_root unresolvable... naming the
corpus root it could not resolve and the next step" — no `N of M` fixture anywhere in the six
cases. `SC-04`'s text carves out one explicit exception for this exact class of mismatch
(*"For merge-gate.py the required behaviour is a denied merge, not a swept count"*) but writes none
for `check-domain.sh`, and `T-07`'s reader ledger lists `check-domain.sh` under "SWEEPS, refusal
asserted by `SC-04`'s own suites" without qualification.
Consequence: a reviewer trusting "`T-06` traces `SC-04`, `T-06`'s suite is green" as proof that
`check-domain.sh`'s short-corpus refusal is tested would be wrong — no such fixture exists in the
plan, and given the provider split it cannot exist in the shape `SC-04` states. This is the same
defect class the c2 goal-check flagged against `SC-15` ("a criterion that can go green while its
requirement is false") recurring at a different site. Fix shape: either add a `merge-gate.py`-style
carve-out to `SC-04`'s text for path-provider readers, or re-trace `T-06` to `SC-05` (which it
actually demonstrates) instead of `SC-04`.
Anchor: `plan.yaml` `T-06.traces`, `T-06.intent` case (c); `BRIEF.md` `SC-04`, `SC-05`; `plan.yaml`
`D-04`.

**F2 — low — `T-05`'s two-frame naming in the deny message is prose with no verify watching it.**
`T-05`'s intent instructs implementing `REQ-05`'s two-frame shape verbatim in `merge-gate.py`'s
deny message ("record the ENUMERATION frame... and the CONTENT frame... name both in the deny
message"). `T-05` traces `[REQ-03, REQ-04, SC-04, SC-09]` — neither `REQ-05` nor `SC-14`. `SC-14`'s
own text scopes itself explicitly to *"check-state.sh and... the four validator sweeps"*, excluding
`merge-gate.py` by name. None of `T-05`'s six test cases (a)-(f) assert the frame tokens
(`provider=history`/`provider=path`) appear in the deny message — case (a) asserts only "the count,
the corpus root AND a next-step clause." An implementation could ship without the frame naming and
every listed test would still pass.
Consequence: low — the deny decision itself, the count, the corpus root and the next-step clause
are all genuinely tested; only the audit-trail provider/ref annotation in the message is
unenforced, which weakens `REQ-05`'s stated auditability purpose for this one reader without
anyone noticing.
Anchor: `plan.yaml` `T-05.intent` (frame-lines paragraph) vs `T-05.traces`; `BRIEF.md` `SC-14`.

## Not spent as findings

- `T-08` case (g) (the absent-`fix-sha` refusal) is falsifiable as written: it asserts exit
  non-zero, the missing-input message, and that nothing is created, and no plausible
  implementation (env-var fallback, silent default) satisfies all three while skipping the guard.
  No red-proof instruction is attached to case (g) specifically (unlike (f)), but the mechanism
  (`argparse` `required=True`, no default) makes the omission low-risk. Not raised as a finding.
- `SC-09`'s "sweep rows... covered by SC-04's per-reader refusal assertion" resolves to `T-07`
  asserting only that the *named suite file exists and is non-empty* — a weak presence check on its
  face, but the actual refusal is graded for real by the owning task's own `verify:` chain
  (`T-03`/`T-04`/`T-05`/`T-06`'s own suites run independently), so the weak check is attribution
  hygiene (catching a stale filename), not a stand-in for the refusal proof itself. Not a finding.
