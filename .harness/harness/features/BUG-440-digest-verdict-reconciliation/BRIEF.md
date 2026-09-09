# BRIEF — BUG-440-digest-verdict-reconciliation

## Problem

A lead-hosted run can finish, write a durable `digest.md` saying `VERDICT: FAIL`, and have
`feature.json` `runs[].verdict` record `PASS` — and nothing notices. The class was found by hand at
FEAT-22's ship briefing, after 17 runs were reconciled manually (issue #440). `check-state.sh`
INV-15 already opens every completed lead digest and checks its *shape*
(`.claude/skills/harness/bin/check-state.sh:1516-1535`), so the two values sit one line apart from
each other and are never compared. Measured on the control-plane root's run tree on 2026-09-06 with
HEAD at `772790be52774eafe2971f9c44400e18b2d54275` — run directories are untracked, so the tree is
per-checkout and the sha pins only the code that read it: **308** completed lead-hosted runs carry a
`digest.md`, all 308 are structurally valid under `validate("lead", ...)`, **298** of those are
claimed by a `feature.json` `runs[]` entry and are therefore compared (the other 10 run directories
are unclaimed and out of scope by construction), and **4 of the 298 contradict their `feature.json`
entry** — including `FEAT-25-claim-feature-root/runs/2026-08-19-6-distill-validator`, recorded
`PASS` over a digest that says `FAIL`. Every downstream consumer — the goal-check, the cycle record,
the operator's read of "did this feature pass" — treats `feature.json` as truth.

## Goal

The state gate stops trusting the summary. For a completed lead-hosted run whose durable digest is
structurally valid, `check-state.sh` compares the digest's final verdict to the verdict recorded for
that run in `feature.json` and **refuses the tree when they disagree**, naming both records so a
human can see which one is wrong. Nothing is repaired automatically and no other run keeps or loses
a finding it has today.

## Requirements

- REQ-01: A completed, lead-hosted run whose `digest.md` is structurally valid and whose
  tail-anchored final `VERDICT:` differs from the matching `feature.json` `runs[]` entry's `verdict`
  produces a **blocking** state-check finding — the violation list that fails the check, not a
  warning. The finding names five things: the feature, the run id, the digest verdict, the
  `feature.json` verdict, and both file paths.
- REQ-02: Equal values produce **no finding of any kind**. A tree whose completed lead runs all
  agree with their recorded verdicts stays green and exits as it does today.
- REQ-03: Every case outside that intersection keeps its **current** behaviour, unchanged:
  (a) a run whose `host` is not one of the three leads — no finding; (b) a run whose `state.yaml`
  `status` is not `complete` — no finding; (c) a completed lead run with **no** `digest.md` — still
  exactly INV-15's existing missing-digest violation and nothing new; (d) a completed lead run whose
  `digest.md` fails `validate("lead", ...)` — still exactly INV-15's existing contract violation,
  with no second finding stacked on top; (e) a run **directory** with no matching entry in
  `feature.json` `runs[]` — silent. The comparison is quantified **from `feature.json`'s `runs`
  list**: a run directory the record does not claim is out of scope by construction, and so is a
  recorded entry with no `state.yaml`.
- REQ-04: The check writes nothing. Neither `feature.json` nor any `digest.md` is created, modified,
  moved or rewritten by it. The gate reports the contradiction; a human decides which record is
  wrong.

## Success Criteria

- SC-01: A fixture tree containing one mismatching completed lead run makes the check exit non-zero
  and emit exactly one new finding for that run, and that finding's text contains each of: the
  feature name, the run id, the digest verdict, the `feature.json` verdict, the `feature.json` path
  and the `digest.md` path — asserted as six separate substring assertions, not one match.
  verify: automated      evidence: integration
- SC-02: A fixture tree whose completed lead runs all agree exits 0 and emits no line naming the new
  invariant. FAILS IF the check is satisfied by the mismatch fixture alone.
  verify: automated      evidence: integration
- SC-03: Each of REQ-03's five cases is pinned by its **own** assertion in one fixture tree: no new
  finding names run (a), (b) or (e); run (c) still produces exactly its existing missing-digest
  violation; run (d) still produces exactly its existing contract violation and no second line.
  verify: automated      evidence: integration
- SC-04: `feature.json` and every `digest.md` in the fixture tree are byte-identical before and
  after the check runs, asserted by comparing a content hash of each file taken on both sides of the
  invocation.
  verify: automated      evidence: integration
- SC-05: The new test case is demonstrated to **fail** against the pre-change `check-state.sh`: the
  build records the invocation and the verbatim failing output in
  `.harness/harness/features/BUG-440-digest-verdict-reconciliation/notes/redproof-BUG-440.md`, read
  at the pinned sha with
  `git show <review_sha>:.harness/harness/features/BUG-440-digest-verdict-reconciliation/notes/redproof-BUG-440.md`.
  FAILS IF the note is absent at that sha, or records a pass.
  verify: inspection
- SC-06: No other invariant's behaviour changes: `python3 tests/integration/test-check-state.py`
  exits 0 with no line beginning `FAIL`. Baseline observed at
  `772790be52774eafe2971f9c44400e18b2d54275`, before any change: exit 0, 216 output lines, 0 `FAIL`
  lines, 51.9s wall.
  verify: automated      evidence: integration
- SC-07: The verdict is read through the semantics that already exist, not a second convention: at
  the pinned sha, the new code's tail-anchor and verdict regexes are byte-identical to
  `validate-digest.py:1155-1160` and cite those lines in a comment, it reuses the digest text INV-15
  has already read rather than re-reading the file, and it restates no list of legal verdict tokens
  (the new region contains no literal `PASS`/`FAIL`/`BLOCKED`/`ESCALATE` set — the comparison is
  string equality and needs none).
  verify: inspection

## Constraints

- **Supplies the mechanism, does not block:** DEC-156 (the durable digest a successor reads) is why
  `digest.md` is authoritative and why INV-15 already opens it. `validate-digest.py:1155-1164`
  supplies the tail-anchored semantics and the legal token set; `validate("lead", ...)` already
  rejects a digest with no `VERDICT:` line or an illegal token, so a structurally valid digest always
  yields one parseable, legal verdict and no unparseable branch is owed.
- **Blocks:** DEC-174 — `check-state.sh` is the state gate and cannot vouch for its own change, so
  its implementation and its own tests are main-session-direct, not team work. The `feature.json`
  `runs:` parse at `check-state.sh:643-652` is pinned as a 3-tuple because INV-7 and INV-22 unpack
  exactly three; this feature must not widen it.
- **Out of scope, chosen at grilling:** retroactive repair of historical records; any change to
  cycle accounting, the `feature.json` schema, or digest-return semantics.
- **DISCLOSURE — the gate goes red on day one, and it needs one ruling at signature.** Because
  repair is out of scope, the 4 live mismatches re-measured on 2026-09-06 become 4 blocking findings
  at every `/harness` entry in the control-plane root the moment this merges. Written as
  *recorded in `feature.json`* → *digest says*:
  `FEAT-07-verify-teeth-batch-probe/goalcheck-product` `FAIL` → `ESCALATE`;
  `FEAT-22-docs-layout-migration/2026-08-16-15-distill-product` `INCOMPLETE` → `PASS`;
  `FEAT-22-docs-layout-migration/2026-08-16-15-distill-validator` `INCOMPLETE` → `PASS`;
  `FEAT-25-claim-feature-root/2026-08-19-6-distill-validator` `PASS` → `FAIL`. Note the two
  `INCOMPLETE` records are not legal digest verdicts at all, so exact equality is what surfaces
  them. That is the feature working as specified, and it is a consequence this feature makes
  reachable rather than one the ticket asked for. **The ruling — pick one, A, B or C:**
  **(A) Merge now, accept the red:** `/harness` entry stays red with these 4 blocking findings
  until you or a delegate reconciles the four records under a separate reconciliation ticket you
  own filing.
  **(B) Reconcile first, then merge — the gate is green on day one:** you or a delegate corrects
  the four `feature.json` records before this merges. The four records are per-checkout data edits
  in the control-plane root, independent of this code change, so B adds no scope to this feature
  and changes no requirement, criterion, decision or task — it is sequencing, and it is yours to
  order because those records are yours. No grandfathering is needed under B.
  **(C) Neither:** the plan goes back before signature for repair or grandfathering scope it does
  not have today.
- Run directories are untracked and per-checkout: the build worktree contains none, so every test
  fixture is synthetic and no live lead digest can be copied into one.

## Verification gaps

- None for this surface. `integration` has a real runner
  (`.agents/skills/harness/bin/run-unit-tests.sh --kind integration`) whose detect glob
  `tests/integration/**` matches the file this feature's tests live in, so no criterion above rests
  on a `cmd: null` kind.

## Approval

status: approved
approved_by: operator
date: 2026-09-06
