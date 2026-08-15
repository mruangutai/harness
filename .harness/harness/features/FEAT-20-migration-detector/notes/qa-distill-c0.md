# Distillation — harness-qa — FEAT-20-migration-detector

Cold pass over `notes/qa-c0.md` and `notes/review-harness-qa-c0.md` plus four lead-relayed
candidates. Anchors re-read at source before accepting anything (`runs/qa-gate-validator/digest.md`,
`runs/2026-08-14-2-product/digest.md`) — relay framing is the least trustworthy input (P-01).

## Section counts

| Section | Before | After |
|---|---|---|
| Patterns | 12 | 13 |
| Gotchas | 5 | 6 |
| Outcomes | 3 | 5 |
| Open | 0 | 0 |

No displacement — every section had headroom under its cap.

## Ops applied

- `add P-13` (Patterns) — source: **relay #2**. Count provenance for mixed plan-required/added
  test cases ("cases 1-18… 18 required by plan, plus 17-18 added" self-contradicts a 16+1=17
  plan-required total). Reviewer ruled it info, not a send-back, but the underlying habit —
  reporting a merged total instead of the breakdown — is worth institutionalizing regardless of
  whether it blocked anything this cycle.
- `add G-06` (Gotchas) — source: **relay #1, half (b)**. The SC-11 caveat "not bracketed pre/post
  the exact run" was false; the same artifact's own prose already described performing the
  bracketing with `diff` returning 0. Confirmed at `runs/qa-gate-validator/digest.md:51-56` and by
  re-reading `qa-c0.md:83-90`, which now correctly narrates the bracketed measurement. A modest-
  sounding caveat is still a record claim and still falsifiable.
- `add O-04` (Outcomes) — source: **relay #3, re-scoped**. Read `runs/2026-08-14-2-product/
  digest.md:32-44` directly rather than trusting the relay's framing: pm did not fault the delta-
  naming (upheld) — it faulted recording SC-10 as "satisfied under my reading" when the text is
  unmet and only the intent is met. The entry encodes pm's actual distinction (two findings, route
  up) rather than the relay's looser framing (name the delta, ask).
- `add O-05` (Outcomes) — source: **relay #4**. Self-flagged in both `qa-c0.md` ("this is itself
  worth flagging as a finding") and independently in the panel note
  (`runs/qa-gate-validator/digest.md:86-89`): a near-exact Phase-1/Phase-2 match came from a plan
  that pinned cases by number in three documents, not from a strongly independent derivation.

## Rejected

- **relay #1, half (a)** — `cycles:`/`must_fix:` at top level outside `DIGEST:`. Rejected. The
  preloaded `harness-handoff` template already shows `DIGEST:` as a mapping containing every field,
  and `validate-digest.py` caught the violation in-cycle (the send-back that produced this very
  artifact set). An entry restating an already-enforced structural contract adds nothing a future
  spawn doesn't already get from the template plus the validator — exactly the DEC-145 bloat the
  craft/observation split exists to prevent.

## Stale-entry check

Lead flagged none as falsified; independently confirmed P-04 and O-03 both fired correctly this
feature (matrix denominator stated in both `qa-c0.md` and the panel note; O-03 explicitly used for
the T-03/T-04 config/docs inspection framing). No changes to either.

## Schema gap surfaced, not distilled

`validate-digest.py`'s `GATE_FIELDS = {"qa": {"suite", "matrix_ok"}}` rejects `suite: n/a` /
`matrix_ok: n/a` alongside `VERDICT: PASS` unconditionally (tested empirically:
`suite: n/a, matrix_ok: n/a` + `PASS` → `BLOCKED (contract violation)`; the same values +
`BLOCKED` → `digest ok`). This dispatch ran no gate — it is a distillation-only task — so the
honest values are `n/a`, but there is no distillation exemption analogous to dev-ops's
config/docs exemption (DEC-173 widened the vocabulary for declined gates but not for non-gate
dispatch types). This is a harness defect, not something to guess around or paper over with a
false `suite: pass` — raised as `open_questions`, not folded into Expertise (a bug report would
outlive the fix).

**Update:** the `SubagentStop` hook confirmed the prediction and bounced the `PASS` return. Per
its own suggested fix ("Return BLOCKED or FAIL, or report the real result") and since no real gate
result exists to report (none ran this dispatch), `VERDICT` is now `BLOCKED` — a routing artifact
of the schema gap, not a statement that distillation failed. The work itself (Expertise file,
`check-expertise.sh` OK, this artifact) is already durably written to disk and unaffected by this
verdict.

```yaml
VERDICT: BLOCKED
DIGEST:
  headline: Expertise distilled and durably written (4 ops applied, 1 relay half rejected) — VERDICT forced to BLOCKED only because the digest contract has no n/a-with-PASS path for a non-gate qa dispatch.
  suite: "n/a"
  failures: 0
  matrix_ok: "n/a"
  coverage_gaps: []
  sc_evidence: []
  open_questions:
    - { id: Q1, question: "validate-digest.py's GATE_FIELDS requires qa's suite/matrix_ok in {pass,fail} whenever VERDICT is PASS, with no exemption for non-gate (e.g. distillation) dispatch types — the only honest value for a dispatch that ran no gate is n/a, which the validator rejects. Recommend a distillation-dispatch exemption analogous to dev-ops's config/docs exemption, or a documented convention for how distill-only qa returns should represent these two fields.", blocking: true }
  files_touched: [.harness/expertise/harness-qa.md, .harness/features/FEAT-20-migration-detector/notes/qa-distill-c0.md]
  expertise_update:
    - { op: add, target: P-13, section: Patterns, entry: "WHEN citing a test count that mixes plan-required and self-added cases DO break down the provenance — how many the plan requires versus how many are additions — rather than reporting one merged total, which overstates plan compliance.", why: "relay #2 — self-contradictory case count (18 vs 16+1) traced to a merged total; reviewer ruled info, habit still worth fixing" }
    - { op: add, target: G-06, section: Gotchas, entry: "WHEN writing a caveat that claims you did NOT do something DO check it against what your own artifact's prose actually describes before including it — an inaccurate caveat, even one that errs toward modesty, is still a falsified record.", why: "relay #1(b) — false SC-11 caveat in a signed artifact, sent back and repaired in-cycle" }
    - { op: add, target: O-04, section: Outcomes, entry: "WHEN a criterion's literal wording is stricter than the artifact scoping it DO report two distinct findings — intent-satisfied and text-unmet — and route the verdict up, rather than recording the criterion as satisfied under your own reading.", why: "relay #3, re-scoped from source — pm's actual ruling was against 'satisfied under my reading', not against naming the delta" }
    - { op: add, target: O-05, section: Outcomes, entry: "WHEN Phase 1's expected coverage list matches the built suite almost exactly DO check whether the plan pinned test cases by number or verbatim string before crediting the match to independent derivation — a prescriptive plan collapses the gap structurally, not a stronger anti-bias signal.", why: "relay #4 — self-flagged in own artifact and confirmed independently in the panel note" }
  cycles: 0
artifact: .harness/features/FEAT-20-migration-detector/notes/qa-distill-c0.md
```
