# Plan repair c3 — N-03 and N-04 closed, N-05 and N-06 dispositioned

**Both repairable c2 findings are closed and the two info findings are dispositioned in writing.**
Four red-check gates now fail on a MISSING case, not only on a failing assertion (T-01, T-03, T-05,
T-07); REQ-10 has a success criterion for the first time (BRIEF SC-12, `verify: automated`
`evidence: integration`); T-05 case E asserts `typed` exactly `false`. Nothing else in `plan.yaml`
or `BRIEF.md` moved: 12 tasks, 20 decisions, `approval: {status: pending}`, `status: plan`, no
`panel:` key, 11 REQ / 12 SC, BRIEF `## Approval` `status: pending`. Send-back cycles: 0.

`plan.yaml` sha256 `4e70d074…c93481` before, `ddcdd313975fd127459f2dc1c00d38b39c7918ffe5078490f8fb78e852f30a26` after.
All five plan writes went through `plan-merge.py amend --expect-sha256`; no mismatch, no retry.

## Per finding

| Finding | Field changed | What changed | Proof |
|---|---|---|---|
| **N-03 gating** (med) | `tasks[T-03].verify`, `tasks[T-05].verify`, `tasks[T-07].verify`, `tasks[T-01].verify` | Each red-check now requires its cases/assertion groups individually before it accepts a non-zero exit: a per-case marker loop (`CASE <id>:`) plus a fixed-string loop over the load-bearing literals, then the unchanged RED pairing. | Loops quoted below; `grep -qF "CASE $c:"`; proof run in `## The gate now discriminates` |
| **N-03 traceability** | `BRIEF.md` `## Success Criteria` — appended SC-12 | REQ-10 is graded: adopted parent never typed on the adopting run **or a rerun**, `source_issues` numbers never typed, absent provenance never typed on first run or rerun and no provenance entry written. `verify: automated  evidence: integration`. | `BRIEF.md:160-170`, content string "This is REQ-10's only falsifiable grading." REQ-10 unchanged at `:58`; no other REQ or SC touched (11 REQ / 12 SC) |
| **N-04** (low) | `tasks[T-05].intent`, case E — the one authorised `intent:` edit | "left typed false **or absent**" replaced by "wrote an entry for EVERY item, each carrying typed exactly false - not absent, and not a missing item key", naming the no-receipt state as the thing that must fail the case. | content string `carrying typed exactly false - not absent, and not a missing item key` |
| **N-05** (info) | none — **divergence recorded as correct** | The backlog route keeps `false` (`:671`) where the feature/factory routes use `"created"`. `backlog-issues.json` is net-new and keyed by the item string, so absence there is "not created yet" with no legacy population to misread, and D-20 scopes itself to `feature.json`/`factory.yaml` (D-13 scopes the backlog receipt). Unifying would have required editing T-06 §5's `intent:`, outside this dispatch's one authorised intent edit, for zero safety gain. N-04's tightening pins the same value from the test side, so the two now agree in both halves. | no write; `:671` and `:511`/`:850` unchanged |
| **N-06** (info) | none — **accepted consequence, explicitly left** | Issues created in compatibility mode carry no provenance and are therefore never typed if the repository later enables Issue Types. No `## Settled` clause asks for retro-typing; D-20's fail-safe direction requires exactly this. Left as recorded, not repaired. | no write |

## The changed `verify:` blocks

T-03 (T-05 and T-07 are identical in shape, with case lists `A B C D E F` and `A B C D E F G H`
and their own string lists):

```bash
python3 -c "import ast; ast.parse(open('tests/integration/test-gh-issue-types.py').read())" || exit 1
for c in A B C D E F G H H2 I J; do
  grep -qF "CASE $c:" tests/integration/test-gh-issue-types.py || { echo "MISSING case $c - label every case from this task's intent with a line carrying the literal marker 'CASE $c:' (comment, docstring or print), so an OMITTED case fails this gate as loudly as a failing one"; exit 1; }
done
for s in IT_feature IT_bug IT_task IT_defect IT_epic updateIssue issueTypes 4242 adopted created; do
  grep -qF "$s" tests/integration/test-gh-issue-types.py || { echo "MISSING required assertion string: $s"; exit 1; }
done
python3 tests/integration/test-gh-issue-types.py && { echo "UNEXPECTED PASS: this test must be RED before T-04"; exit 1; }
echo "RED as required - all eleven cases present"
```

T-01's new leg (the fifteen-value loop and `UnknownWorkNature` grep are untouched):

```bash
for s in type_for_change_type type_for_nature type_for_parent overrides_from_config classify_capability query_failed capability_query_args node_id_args apply_type_args missing_types refusal_text Defect Story Epic Maintenance; do
  grep -qF "$s" tests/unit/test-issue-types.py || { echo "MISSING the assertion group naming: $s - ..."; exit 1; }
done
```

**Tasks changed and why.** T-03 and T-07 — the two N-03 named. T-05 — same shape, same defect
(`ast.parse` + non-zero exit only). **T-01 — inspected and it DID need something**: the fifteen-value
loop (F-06) discriminates assertion groups 1–5 only, so a file omitting group 7,
`classify_capability`'s four-row discriminator "the whole feature rests on", greened the gate. Its new
loop names one symbol per remaining group. **Inspected and left alone:** T-02, T-04, T-06, T-08 run a
named test file to GREEN (a missing case there fails the file's own assertions, or is caught by the
compatibility control they also run); T-09, T-10, T-11, T-12 are not red-checks — T-10's verify
already requires exactly one verdict line and a PATH-stripped SKIP leg, T-12's machine-compares two
copies.

**Why case markers rather than content greps alone.** Content strings cannot separate H from H2, or
J from H2, on T-03 — the cases N-03 actually names — because both assert over the same literals
(`4242`, `adopted`). The `CASE <id>:` marker is a cheap, reversible test-shape convention, decided
here and stated in the gate's own failure message; the doer receives the `verify:` verbatim, so it
cannot false-fail a compliant file. The `|` block style is preserved on every field (checked by
`yaml.compose`).

## The gate now discriminates — proved, not asserted

The T-03 `verify:` was extracted from the LOADED plan and run by `bash` against a fabricated
stand-in in a temp root:

- all eleven markers present, test exits 1 → exit **0**, `RED as required - all eleven cases present`
- `CASE J:` removed → exit **1**, `MISSING case J - …`
- `CASE H2:` removed (H still present) → exit **1**, `MISSING case H2 - …`

Before this change the same file omitting J or H2 exited 0. `check-plan-routes.py` on the final
plan: `0 violation(s) across 1 plan(s)`, exit 0 (T-12's DEC-174 line is the expected carve-out).

## Q1, answered at signature

**Chosen: `verify: automated`, `evidence: integration`** — not "accepted as diff-inspected". The
carriers are T-03 H2/J and T-07 F/H, which already exist as specified cases, and the N-03 gating
repair is what makes the automated claim honest: before it, an integration file could omit those four
cases and every gate stayed green, so `automated` would have named a runner that never ran them.
`inspection` was rejected because the property is behavioural across two runs — no `file:line` read
can settle what a second invocation does.

## Open questions

- None blocking. The operator sees one choice at signature: SC-12's method (above). No new REQ, no
  widened REQ-10, no scope change.
