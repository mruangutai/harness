# Security review · FEAT-2622 · cycle 2

**FAIL — MF-1’s stale-row match is closed, but the open-row carve-out can still mask an independent `must_fix`.** Reviewed `3e979ae3cd303fdf65746bf13c8c8e041dac4964..edcda5be091e5b1aa6dcc7021e410aae56de0222`.

## SEC-02 · high · substance · T-01

`exposure: {trigger: plausible, vs_today: regression, control: adversary}`

A plan scope reviewer may validly return `FAIL` with a discounted finding and an independent `must_fix`: `validate-digest.py:1623–1636,1665–1673` rejects links to discounted findings but preserves a distinct blocker, as signed D-06 requires. The product lead can transcribe the discounted finding and accurately report the member at `FAIL`. The new relief logic sees only the lead’s findings and on-disk rows, not the member’s blocker (`validate-digest.py:2138–2149,2265–2302`; `schemas/digest/common.json:909–936`). If the transcribed finding matches an open discounted `med` row and nothing else gates, the lead can report `PASS`: `validate-digest.py:2336–2369` ranks that member as `PASS`. A lead with ordinary fan-in authority can thus suppress a genuine blocker without falsifying the finding’s exposure, falsifying the member verdict, or resolving an open row. The base rejected relief on that open row. The append authorization at `validate-digest.py:2823–2836` binds the lead’s destination, not the member’s reasons for failing.

**Must fix:** Grant open-row relief only on independently corroborated member evidence that no separate gate remains. If that evidence is unavailable, retain worst-wins. Preserve the pre-existing resolved-row route. This conclusion is from the pinned source trace, not a live bypass execution.

## MF-1 closure and self-rating

Ran a read-only predicate probe on the exact pinned function definitions from `git show`, in memory. `_matched_row_reason` and `_discounted_non_gating` relieved a matching discounted `med` control, but denied an open discounted `med` row against a current plausible `high` finding, an adversary-controlled `med`, and an otherwise discounted `high`. No live hook, signature, or write path was invoked; the probe was not refused. A reader can self-rate contrived/no_worse/non-adversary at `med`, which the signed design allows, but that rating alone cannot relieve a finding that still carries `adversary` control or a gating severity. It also does not by itself authorize relief of the member’s separate blocker.

## Scope and evidence

- **SC-06:** `panel_findings.py:97–116` owns the predicate and non-gating set; `validate-digest.py:1612–1614,2289–2291` and `plan_merge/panel.py:482–494` use them. The writer refuses missing/malformed exposure and discounted gating rows; legacy omissions never qualify for open-row relief. Existing signature severity normalization is unchanged (`panel_findings.py:174–183`).
- The digest schema, generated returns, and team prompts are in scope as enforcement inputs. Guidance, decision/index, template/reference, tests, and feature-local records add no independent runtime boundary. No new request/auth, credential, dependency, or export path; no separate actionable injection or disclosure finding.
- Pinned code grade passed (43 functions). No integration suites or live gate execution. Open questions: none.
