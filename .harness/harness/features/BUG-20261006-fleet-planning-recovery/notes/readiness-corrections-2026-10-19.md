# Tooling readiness corrections — 2026-10-19

## Original pinned findings

Read-only code/security review of `b3f5552088c271c2083025ea9e7ff815741c310f`
found two actionable issues despite that pin's passing full matrix:

- **P1, code:** full replacement created task issues with the original feature
  milestone title, rather than the confirmed replacement milestone. A same-title
  old target milestone could receive the new task; an absent title could prevent it.
- **Medium, security, SC-03/SC-04:** live cycle evidence lacked run ownership.
  A different run could replay a zero-count artifact to reduce its attribution.
  Checking current references alone was insufficient: a corrected run could release
  its superseded artifact for the same replay.

These are original findings, not clearance of the later corrections. The b3f55520
full-matrix receipt remains true only for its immutable source. No later full matrix
is authorized by the consumed exactly-once ruling.

## Corrections

- Resolve the confirmed replacement milestone NUMBER's actual title once, only
  when full-mode task creation still needs it. Pass that title explicitly to task
  creation, including an adopted milestone with an unrelated title. This is not
  discovery of an uncertain create. Completed/terminal recovery remains a no-op.
- Verify live artifact ownership in the locked writer and shared reader. Another
  recorded run's namespace or current, previous, or refusal reference cannot supply
  a close. Arbitrary feature-local first-claim paths remain supported; separate
  files containing identical bytes remain legal.
- Preserve superseded path/hash references in `cycle_evidence.previous`. Verify
  every retained hash on correction and read. This is durable provenance, not a
  third count or an invented run ID in the persona payload. Historical operator
  authorization cannot claim an unattested `previous` list.
- Keep existing attribution delta/residual semantics and supported corrections.
  Do not replace them with a new monotonic-count rule. Original own-feature raw
  bytes, verdicts, timestamps, attributions and remote objects remain untouched.
- The fake remote now models milestone identity and actual issue association,
  rejecting unknown titles. Regressions check the resulting association, not a
  forwarded command or mock echo. Guidance is updated in ledger/github-mirror.

## Targeted evidence, not a new full matrix

The new ownership regressions first produced four actual failures plus one passing
identical-bytes boundary. The schema's historical-previous guard also failed at its
intended boundary before its fix. Initial GH recovery checks failed five scenarios
with the identity-aware fake; one remaining adoption fixture then needed the
separately confirmed remote milestone seeded explicitly.

Final corrected-source runs all exited zero:

| Command | Observed result | Command time |
|---|---|---:|
| `python3 tests/unit/test-feature-record.py` | 107 tests PASS | 20.01s |
| `python3 tests/integration/test-gh-sync-open.py` | ALL PASSED | 33.06s |
| `python3 tests/integration/test-check-state-records.py` | PASS | 11.78s |
| `python3 tests/integration/test-check-state-feat59.py` | PASS | 19.12s |

A separate real CLI smoke preserved total 6 (legacy residual 3 + run counts 2/1),
retained the superseded reference, refused cross-run replay and tampered prior
bytes without metadata changes, and exposed tampering through a fresh reader.
The milestone CLI smoke reached successful identity/archive/no-create-replay
assertions. Its initial harness used a stale imported fake; a fresh process fixed
that isolation problem. The separate subject smoke initially omitted the required
raw `artifact` field; fixing that throwaway input required no production change.
No temporary smoke artifacts were retained.

## Complexity and pre-pin quality

Frozen corrected source tree: `e3e514908403877003ef443219ba88f3f1b68a17`.
Canonical grading API against baseline
`63cac11a3216aa8d34792665a05fcb185f7cf73b`: raw **grade_2**, 81 passing,
35 named medium reasons, **zero high**. This is not an unqualified grading PASS.
The CLI correctly refused a tree object because it requires a commit; the precheck
used the same source grader/classifier over immutable tree blobs instead. A real
commit CLI assessment remains required after the pin.

The 35 named justifications in `build-verification-2026-10-18.md` still apply.
Changed metrics/reasons are explicit here:

- `_run_end_digest`: cyclomatic 15, cognitive 17, ABC 30.3; current and all prior
  immutable proofs must be checked before one attribution transition.
- `run_evidence_problems`: 10 / 18 / 23.5; owns one accepted/refused attribution
  audit and its diagnostic boundary. Lead validation is now a cohesive helper.
- `replacement_cases`: 17 / 28 / 43.4; full/terminal archival and completed replay
  remain one paired lifecycle scenario, now including actual milestone identity.
- `_replacement_role_adoption_case`: 14 / 8 / 44.8; verifies exact adopted-role
  identity, retained generation/archive and completion/replay in sequence.

Initial new high grades were removed by cohesive evidence/fixture helper
extractions without weakening or deleting assertions. The ownership predicate and
lead validator both now grade 4. Four separate read-only final quality refreshes
(reuse, simplification, efficiency, altitude) returned no findings. They do not
certify correctness/security.

## Remaining gate

Create the corrected local review pin, run the canonical pinned grading CLI and
obtain read-only code/security re-review. A new-pin full-matrix run requires a new
operator ruling. T-03/T-04/T-05 remain unactivated: no Kaya capture, history repair,
installation, push, merge or deployment has been performed or authorized here.

## Corrected source pin and observed smoke

The canonical feature-scoped state checker exited zero before committing (only
historical/layout notes); the signed plan checker resolved all 51 anchors with zero
failures. Local commit `d6074f0eaad0121546d4df7d1447fd7c3aa44486` contains the
corrections. Its actual canonical grading CLI exited zero with 81 passing,
35 named medium reasons, zero high findings and zero ungraded Python.

All 283 tracked blobs in `.claude/skills/harness/bin`, `.omp/extensions`, `tests`,
`.harness/harness.json` and `.harness/team-config.yaml`, plus exact plan bytes,
match that pin. A fresh-process POST-PIN smoke exited zero for BOTH corrected paths:

- Task associated with confirmed milestone 7, not old-title milestone 100; exactly
  one known-number title read; original archive unchanged; completed replay
  byte-identical with no additional remote create.
- Run-subject total remains 6; superseded evidence stays owned; cross-run replay
  exits 2 with `digest evidence belongs to run 'r1', not 'r2'`; tampering exits 2
  with an evidence-hash refusal; metadata remains byte-identical on both refusals;
  the fresh reader reports the same evidence-hash problem.

Read-only corrected-pin re-review is pending. No full matrix has run at d6074f0e.

## d6074f0e re-review and completed-recovery amendment

The independent security reader cleared SC-03-SC-04-CYCLE-SUBJECT, including its
superseded-reference residual, at d6074f0e and found no new scoped security issue.
The code reader cleared the original in-progress failure but returned one **P2**:
ordinary `open` after completed full recovery still used the feature's old title
when an approved amendment added a task. This is not a clean code-review verdict.

A new real-CLI regression reproduced that exact case before the fix (session
artifact 436, exit 1): local receipt remained milestone 7, while added T-02 attached
to the old-title milestone 100. Existing recovery/archive/receipts and completed
replay checks passed, isolating the incorrect association.

The one-line guard now recognizes any recorded replacement generation, not merely
an in-progress one, when a missing task needs creation. The existing missing-task
guard preserves lookup-free repeats, and the ordinary-open terminal guard remains
unchanged. Guidance now explicitly covers approved task additions after completion.

Frozen corrective tree `43870903fe2d3a2fc05a2261179459550b7b3e7d` grades raw grade_2:
83 passing, the same 35 named medium reasons, zero high. The new regression grades
3; its amendment fixture grades 5. No source attribution/evidence code changed
after the security clearance. Final targeted verification/pin/re-review are pending.

The final whole `test-gh-sync-open.py` driver now exits zero (31.96s), including
the new post-completion task's correct milestone association, preserved existing
receipts/generation/archive and byte-identical no-create ordinary-open replay.
No evidence/attribution source changed after the earlier 107-unit and checker
integration passes. The final quality refresh, source pin and re-review remain
pending; no full-matrix rerun was performed.

Four separate final d6074f0e-delta quality readers (reuse, simplification,
efficiency, altitude) returned no findings. No edits or checks were performed by
those readers; source correctness still requires the final pinned re-review.

## Final tooling source pin

The feature-scoped canonical checker exited zero before the final commit; the
plan checker again resolved all 51 anchors with zero failures. Final local source
pin: `03c4d9c95def9990dc9d4707e722a732f1a8cade`. Its actual canonical grading
CLI exits zero: raw grade_2, 83 passing, 35 named medium reasons, zero high and
zero ungraded. All 283 scoped runtime/source/test/config blobs and signed plan
bytes match the pin.

A fresh-process POST-PIN CLI smoke exits zero for all three paths: initial full
replacement, an approved added task after completion, and durable run ownership.
Both initial T-01 and subsequently added T-02 associate with confirmed milestone
7, not old-title milestone 100. The amendment preserves the original signatures,
receipts, recovery generation and archive; ordinary-open replay is byte-identical
with no create. Exactly one known-number read occurs for each task-creation phase,
none for either completed replay. Run total 6 remains unchanged on cross-run or
tampered-prior refusal, both metadata-preserving; the fresh reader detects tampering.

Final read-only code/security re-review remains pending. No full matrix has been
run at this pin, and no T-03–T-05 or operational authorization has been added.

## Final scoped readiness handoff

Independent read-only code re-review at `03c4d9c95def9990dc9d4707e722a732f1a8cade`
returned **correct**, no findings, confidence 0.98. Both milestone findings are
cleared, with no new finding in retained SC-03/04/05 evidence/refusal paths.
Independent security re-review returned **no substantive findings**; durable
cycle-subject ownership, including superseded references, remains cleared, and
the final milestone delta adds no discovery/adoption/authorization bypass.
Neither reviewer ran checks or made edits; these are T-01/T-02 scoped clearances,
not whole-feature or deployment certification.

**Remaining decision:** authorize exactly one full active unit matrix and one
full active integration matrix at this new pin, or keep them held. The original
plan's exactly-once matrix limit and the consumed f9a13cac/b3f55520 rulings do not
authorize a rerun at 03c4d9c9. No such command has run. Previous raw receipts,
historical verdicts/times/counts, direct-run BLOCKED 0 and `cycles_used: 0` remain
unchanged. No T-03–T-05, Kaya, installation, push, merge or deployment is authorized.

## Authorized final-pin matrix — 2026-10-24

The operator subsequently selected **Authorize one new-pin matrix**. Both kinds
ran exactly once at 03c4d9c9 and passed: unit 55/55 files, integration 83/83 files.
After both commands, all 283 source/runtime/test/config blobs and signed plan
bytes still match the pin. Full command/time/output receipts are preserved in
`pinned-matrix-03c4d9c9.md`. This consumes that new ruling and completes the
authorized T-01/T-02 tooling verification; it does not activate T-03–T-05 or
authorize any Kaya/install/push/merge/deployment operation. No historical
receipt, verdict, timestamp or accounting value was rewritten.
