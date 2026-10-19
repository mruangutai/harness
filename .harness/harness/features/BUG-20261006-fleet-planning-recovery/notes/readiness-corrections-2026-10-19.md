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
