# Receipt — main session — FEAT-2225 T-03 and T-04 (main-session-direct, DEC-174)

**BLUF.** T-03 committed as `c6b5e3c7` (marked done in `27c9f594`). T-04's literal verify passes:
exit 0 in 15 s, 0 FAIL lines, bun 149 pass / 0 fail. Fail-first was observed for every slice
against the pre-change sources.

## How it was built

The main session split the work into slices with disjoint file ownership and a fixed shared
contract (cross-slice interfaces: tool name and arguments, the digest `persona` field, the
`verify-receipt` call, the `merge-distill` command, and the guard's mutator/read split). The
slices were executed by generic task workers acting for the main session, not by governed Harness
personas. The main session integrated, wrote the end-to-end suite and holds every commit.

| Slice | Files | Fail-first | Final |
|---|---|---|---|
| T-03 guidance | 4 skill/reference docs, 16 persona tool lists and bodies | `test-member-expertise.py` against 7c2f2d48: 28 FAIL (16 tool lists, 12 guidance checks) | 0 FAIL |
| T-04 host tool | `harness-hooks.ts`, `omp-hooks.test.ts` | `notes/red-first-T-04-host.md`: 140 pass, 9 fail | 149 pass, 0 fail |
| T-04 digest contract | `common.json`, `validate-digest.py`, `dispatch-guard.py` + 3 suites | `notes/red-first-T-04-digest.md`: unit 2, dispatch-guard 16, validate-digest 22 FAIL | 34 tests OK; 157/157; ALL PASSED |
| T-04 write guard | `bash-write-guard.py`, `harness_boundary.claim_set_refusal`, guard suite | `notes/red-first-T-04-guard.md`: 51 FAIL | 89/89 new, all sections green |
| T-04 merge gate | `merge-gate.py`, merge-gate suite | `notes/red-first-t04-merge-gate.md`: 23 FAILED | 65 ok, ALL PASSED |

## Main-session integration changes

- `tests/integration/test-member-expertise.py` (new): 16-persona tool/write/own-file-grant checks,
  capability limits, T-03 guidance passages, and capability-class representatives (shell-less
  lead, read-only reviewer, dev-ops, orchestrator, leaf dev) applying create/add/replace/drop on
  craft plus a repository-tier add through `member-ops`, each verified by its own receipt; a claim
  under another persona's name is refused. Deadline 45 s via SIGALRM; actual ~4 s.
- `tests/unit/test-harness-boundary.py`: the bug1304 advice check now requires `expertise_apply`
  and no shell CLI; new repository-tier advice case.
- `tests/integration/canonical-reader-classification.json`: rows for T-01's `_decode_json`
  (canonical_writer_transform) and `parse_receipt` (module_internal_format), merge-gate's moved
  `_github_config` harness.json read and new `_parse_json`. Audit: 0 unresolved, no CLASSIFICATION
  lines.
- `distillation.md`: states the `distill-<squad>` run-id convention and the
  `HARNESS-FEATURE-TREE-ROOT` requirement the digest slice enforces.
- `harness-orchestrator.md`: de-duplicated one clause.

## Deliberate test expectation changes (contract changes, not weakened assertions)

- test-bash-write-guard `[bug1304]`: a governed `python3 .../expertise-merge.py apply` was asserted
  allowed; it is now refused in favour of `expertise_apply` (SC-03).
- test-merge-gate `T-05 gh outage with no matching feature allows` now denies: unreadable changed
  paths refuse rather than guessing non-distill (SC-05). The DEC-138 allow-with-warning path keeps
  coverage through the new view-fails/diff-readable case.
- test-validate-digest #1855 fixtures `QA_DISTILL` / `REVIEWER_DISTILL` use `expertise_update: []`:
  their old items carried no persona and no receipt, which new returns may not do.

## Coverage map for the cumulative behaviour (T-04 intent)

The end-to-end script covers configuration, guidance and member application. The cross-gate
behaviours are proven in the gate suites that own them, all run at validation:
caller binding and spoofing (omp-hooks.test.ts); leaf/lead receipt matching, fabricated,
wrong-persona and stranger receipts, live and durable close (test-validate-digest.py); distill
marker on every child (test-dispatch-guard.py); every shell mutator form for lead, reviewer,
dev-ops and leaf dev (test-bash-write-guard.py); collision replay, changed-main and cap refusals,
supersession (test-expertise-merge.py from T-01); lock contention, stale head/main, replay and
build-entry refusals before gh merge, raw git/gh detection (test-merge-gate.py).

## Not exercised here

- TypeScript typecheck: `cmd: null` (BRIEF verification gap); not run.
- `tests/manual/probe-handoff-comprehension.py` (credentialled host) — required before ship.
- Full unit/integration suite and code-grade: run at the seam, recorded separately.
