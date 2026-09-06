# Plan panel c2 — all seven findings closed, both cycles recorded (14 findings, 13 resolved, 1 open)

BLUF: every cycle-2 finding is closed in the plan and `panel:` now carries **fourteen** findings —
the seven cycle-1 ids unaltered in severity/reader/summary plus seven new cycle-2 ids — each with a
disposition true of the plan as it now stands. One finding is `open`: `u10`'s LOW, which the
operator deliberately did not action at cycle 1 (ruling R3). Only `BRIEF.md` and `plan.yaml` were
written; `approval` is untouched at `status: pending` with no `rulings`. plan.yaml `safe_load`s;
`check-plan-routes.py` exits 0 with 0 violations; all 14 PF- ids re-derive from the LOADED plan
(**ID_OK 14/14**).

## Part 1 — what changed, by rank

| Rank | Sev | Remedy | Where |
|---|---|---|---|
| 1 | med | missing-`section` exit-12 branch now exercised: unit `u13` (all three verbs absent + empty string, asserts code 12, `MALFORMED OPS`, the key `section`, the op index) and integration **`case20`** (a)/(b) through the CLI with sha256 unchanged and a following `apply --entries` at 0 | T-01 intent, T-02 intent, SC-04 |
| 2 | med | **settled: there is no `expertise_update` wrapper.** `resolve_ops` Step A owns the entire payload shape check; `cmd_ops` decodes JSON and hands the value through unaltered; a non-list refuses at 12 with a line naming `expertise_update` so a DIGEST-paster is taught what to pass. Cases `u14` and `case20(c)` | T-01 item 2 (one sentence, PAYLOAD SHAPE OWNERSHIP), T-01 Step A, T-02 |
| 3 (+6, +7) | med/low/info | both verify blocks now grep every case id they depend on before running the suite; `u15` (section emptied by drops) and `u16` (only entry in a section) added; `case19`'s reversed CLI half trimmed, `u11`'s reversal explicitly never trimmed | T-01/T-02 verify + intent |
| 4 | med | fixed by Part 2 alone. **D-15's wording re-checked and left unamended** — it says the HIGH "is resolved before signature", and `panel.findings` now reads `resolved`/`resolved_by: T-01`, so the prose is true | — |
| 5 | low | SC-09's second direction made falsifiable: a THIRD mutation copy (c) removes the verb `drop` from the vocabulary line so `ACCEPTED − CONTRACT == {drop}` and the case asserts *which* direction failed; reachable because T-01 item 3 now REQUIRES the `ops --ops` help to name `add, replace, drop` | T-01 item 3, T-02 case17, SC-09 |
| B-6.2 | advisory | SC-12 `evidence:` corrected to `unit, integration`; SC-04 likewise | BRIEF |

**Cycle-1 INFO (`PF-f9161…`, exit-12 byte-identity CLI-untested) is now CLOSED** by `case20`, which
is exactly what it asked for: MALFORMED OPS driven through the CLI with sha256 before/after.

## The two verify blocks, verbatim

T-01:

```
U="$(git rev-parse --show-toplevel)/tests/unit/test-expertise-ops.py"
for c in u1 u2 u3 u5 u6 u7 u8 u9 u10 u11 u12 u13 u14 u15 u16; do
  grep -qF "$c: " "$U" || { echo "T-01 MISSING CASE: $c"; exit 1; }
done
python3 "$U"
```

T-02:

```
I="$(git rev-parse --show-toplevel)/tests/integration/test-expertise-merge.py"
for c in case11 case12 case13 case14 case15 case16 case17 case18 case19 case20; do
  grep -qF "$c: " "$I" || { echo "T-02 MISSING CASE: $c"; exit 1; }
done
python3 "$I"
```

The greps are discriminating because both intents now REQUIRE every case to report through
`check()` under a label whose first token is its own id and a colon — the shape `case1: …` the
integration suite already uses. `"u1: "` cannot match `u11: `.

## Falsifiability, stated

- **SC-09.** Direction 1 (`CONTRACT − ACCEPTED == REWRITTEN`) fails on copies (a) and (b). Direction 2
  (`ACCEPTED − CONTRACT == {}`) fails on copy (c): the contract text loses `drop` while the tool
  still accepts it and still names it in `--ops` help, so the probe set exceeds CONTRACT and the
  difference is `{drop}`. Before this change the probe set could not exceed CONTRACT, so direction 2
  was true by construction.
- **SC-12.** Falsified by `case19` (CLI id sequence in FILE ORDER, marker isolation) and by `u11`'s
  reversal + `u12` at the resolver; T-01/T-02's verify now fails if any of `u11`, `u12`, `case19` is
  missing, which was the whole gap. `evidence: unit, integration` because half its assertions are
  unit-kind.
- **SC-04.** The exit-12-by-shape clause is no longer prose: `u13` and `case20` drive it, `case20`
  proving byte-identity.

## Dispositions — all 14, before and after

| # | Id | Cyc | Sev | Reader | Before | After | resolved_by |
|---|---|---|---|---|---|---|---|
| 1 | PF-f4d258f365f54f04d9cc976baf0ad981 | 1 | high | scope | open | resolved | T-01 |
| 2 | PF-3f8a11143ba40f67b0f326d532381d5e | 1 | med | should-not-exist | open | resolved | T-01 |
| 3 | PF-21e98fb21fbbe9fefe7c47cc9784c99b | 1 | med | should-not-exist | open | resolved | T-02 |
| 4 | PF-0fd81890be0279f72e1fd44bc27f9828 | 1 | med | scope | open | resolved | T-03 |
| 5 | PF-5674cd3640c7f69731e86e655135ca8c | 1 | low | should-not-exist | open | resolved | T-02 |
| 6 | PF-12c69147fda194c41e76361acb23eef1 | 1 | low | should-not-exist | open | **open** | — |
| 7 | PF-f9161ebeb204bb05a72667ebc1f7df84 | 1 | info | scope | open | resolved | T-02 |
| 8 | PF-6eace9b84f7491d9c0f9461b164da28f | 2 | med | scope | (new) | resolved | T-01 |
| 9 | PF-fc185bd5f67813ea22007906c445bc46 | 2 | med | should-not-exist | (new) | resolved | T-01 |
| 10 | PF-9806b1eebdbadbc4e1c4ccdd1382bacd | 2 | med | scope | (new) | resolved | T-01 |
| 11 | PF-3438775a7c1207792bb12c759fae0c02 | 2 | med | scope | (new) | resolved | — (closed by this transcription; no task carries it, so the key is omitted) |
| 12 | PF-f4ebe4d9be854c06c6171cb796d9b10e | 2 | low | should-not-exist | (new) | resolved | T-02 |
| 13 | PF-b2f2b9dbb61f45c4da64d3870c5fb00f | 2 | low | scope | (new) | resolved | T-01 |
| 14 | PF-01888451a6ea7d757ba1ed591cd2f0e8 | 2 | info | should-not-exist | (new) | resolved | T-02 |

**Row 6 is the only `open`, and it is not an oversight:** it is `u10`, the permanent red case. The
operator ruled R3 at cycle 1 that `u10` stands (`cycle1_dispositions`: `DELIBERATELY_NOT_ACTIONED`),
SC-07 names it, and neither cycle-2 reader re-raised it. Recording it `resolved` would falsify the
record; it stays open, unactioned by design.

**Row 7 deviates from the validator lead's `cycle1_dispositions`, deliberately.** The lead recorded
that INFO `OPEN` because it was true when the digest was written; Part 1's `case20` closed it
minutes later. The acceptance rule — a disposition true of the plan as it now stands — governs, and
the lead's own rank-1 assessment says the two intersect and share one remedy pass.

Severities, readers and summaries of rows 1–7 are byte-identical to what was recorded at cycle 1
(re-derived: each id recomputes from its own stored `reader` + `summary`). Rows 8–14 carry the
cycle-2 readers' own severities, unreassigned, and the lead's summary text folded only.

## Gates

- `yaml.safe_load(plan.yaml)` — clean. `approval: {status: pending}`, no `rulings` key.
- `check-plan-routes.py <plan>` — `0 violation(s) across 1 plan(s)`.
- `panel_findings.py`-derived ids re-computed from the loaded plan: **14/14 ID_OK**, 0 mismatch.
- `git -C <worktree> status --porcelain`:

```
 M .harness/harness/features/BUG-1308-expertise-replace-drop/BRIEF.md
 M .harness/harness/features/BUG-1308-expertise-replace-drop/feature.json
 M .harness/harness/features/BUG-1308-expertise-replace-drop/plan.yaml
?? .harness/harness/features/BUG-1308-expertise-replace-drop/notes/research-BUG-1308-expertise-replace-drop-goalcheck-plan-c2.md
?? .harness/harness/features/BUG-1308-expertise-replace-drop/notes/review-harness-code-reviewer-planpanel-c2.md
```

`feature.json` was already modified before this run (both the c2 digest and the scope reader
recorded it); no write of mine touched it. Nothing outside the feature directory. No formatter,
linter, build or project-wide suite run.

## Open questions

- **Q1 (non-blocking, operator/main session):** row 7 above — the cycle-1 INFO is recorded `resolved`
  rather than the lead's `OPEN`, because `case20` closed it after the digest was written. Flip it
  back only if the record must mirror the digest rather than the plan.
- **Q2 (harness defect, non-blocking):** `check-state.sh` INV-32 expects a `goalcheck` reader entry
  in `panel.readers` (`expected_readers = {"should-not-exist", "scope", "goalcheck"}`), but the
  validator lead's digest names only the two it ran; the goal-check is run in the product segment
  and is not in the validator's `readers:` list. Inventing a third entry the lead never recorded
  would be transcription fabrication, so it is not written. Same shape at cycle 1.
- **Q3 (recurrence, transcribed from the c2 digest, non-blocking):** the scope reader's task returned
  host status `failed (exit 1)` while emitting a well-formed digest and artifact.
