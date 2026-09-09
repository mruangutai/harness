# Panel transcription — FEAT-104 cycle 1 — pm

**Transcribed. `plan.yaml`'s top-level `panel` key now carries both readers (`ran`), all four
surviving findings at the readers' own severities, and both dismissals — written through
`plan-merge.py apply` and nothing else. `approval:` is still `{status: pending}`; no task,
decision, requirement or SC changed. And the Q1 measurement is positive: this project's CI DOES
clone shallow today, so PF-4bd91290's consequence is immediate, not latent.**

## What landed

`.harness/harness/features/FEAT-104-strict-digest-schema/plan.yaml`, key `panel` (top-level,
sibling of `approval:`, appended after `tasks:`). `last_run: planpanel-c1-validator`, `cycle: 1`,
`severity_max: high`.

| id | rank | sev | reader |
|---|---|---|---|
| `PF-4bd91290deaf98062943319ff3ea5641` | 1 | **high** | should-not-exist |
| `PF-d2cefa75a1931540efa60d3561f7df6b` | 2 | med | should-not-exist |
| `PF-4d84bb7e52beff3ee62eb98a7115ae9e` | 3 | low | scope |
| `PF-7469688fee994f7ec08ad85dea1d1f8b` | 4 | low | scope |

Severities, summaries, evidence strings and dispositions are the digest's own words. Nothing was
re-argued, re-ranked, re-rated or re-worded. Both dismissals carried with their reasons.

## Two envelope deviations from the dispatch — both to satisfy shipped tooling

1. **Finding ids are content hashes, not `PF-01..PF-04`.** `panel_findings.py:28-33` computes
   `PF-<sha256[:32]>` of `reader\n<normalized summary>`, `harness-spec-driven` says compute it and
   never type it, and `check-state.sh:515-517` reads a changed id as a STALE RISK ACCEPTANCE — the
   mechanism only works if the id is content-derived. Sequential ids renumber on re-run, so an
   operator ruling recorded against `PF-01` would silently start covering a different finding. The
   lead's rank order is preserved verbatim in a `rank:` field (1→PF-4bd91290 … 4→PF-7469688f), and
   `panel.transcription_rule` records the normalization.
2. **Each reader entry keys on `reader:`, not `id:`.** `check-state.sh:538-541` indexes
   `panel.readers` by `item["reader"]`; every live plan (e.g. `BUG-1081.../plan.yaml:17-19`) uses
   the same spelling. An `id:` key would make both readers invisible to INV-32.

## Q1 answered — CI clones shallow

`.github/workflows/tests.yml:50` — `- uses: actions/checkout@v4`, and **no `fetch-depth` key
anywhere in the file** (one job, `integration`, one checkout step, whole-directory grep clean).
`actions/checkout` defaults to `fetch-depth: 1`, so this is the **absent-key case = shallow**.
PF-4bd91290's contradiction with `tests/integration/test-validate-digest.py:30-33` holds either
way; the measurement only says the spurious red arrives on the first CI run, not eventually. The
plan was not changed on the strength of this.

## For the operator's batched signature review (DEC-176)

PF-4bd91290 is `high` and its remedy rewrites SC-06 (BRIEF), T-01 `files:`+PART 6 and T-08 — all
operator-signed. Neither the lead nor pm may accept that risk, and no fix was dispatched. It reaches
the user as a change request, and its acceptance route is
`plan-merge.py sign-approval --overrule PF-4bd91290deaf98062943319ff3ea5641:<reason>`.

**One thing the record does not yet carry:** `check-state.sh:534` expects three readers —
`should-not-exist`, `scope` and `goalcheck`. Only the first two exist at plan phase; the goalcheck
reader is a later panel. INV-32 grades approved plans only, so this is not live today, but this
`panel` key as written would not satisfy INV-32 the moment the plan is signed. That is a sequencing
fact about the plan phase, not a transcription gap — flagged, not fixed.
