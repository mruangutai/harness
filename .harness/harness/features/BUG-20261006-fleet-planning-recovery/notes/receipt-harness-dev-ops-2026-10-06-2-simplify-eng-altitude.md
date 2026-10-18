# Receipt — simplify · altitude (plan surface) — BUG-20261006-fleet-planning-recovery

BLUF: angle completed (PASS = angle ran, not approval). 5 findings, all on T-01 (plan.yaml:103-149); T-02..T-05 and the mission shape raise none. None re-litigates lanes, PF-d051/PF-2157/PF-aa1a/PF-0dbb, or the accepted fleet-wide cycle-evidence duty. Read-only; no verification executed. Craft leaf read: delete-first.md.

Method: read angle-altitude.md, plan.yaml, BRIEF.md (long intent lines tail-read), and spot-checked baseline code for existing seams (`feature-schema.json:58` run `cycles_used`; `feature-record.py:138,255-265` per-run attribution and delta; `factory_config.py:221,292` product_config/board_for).

## Findings

### A1 — task — T-01 intent l.141 (cycle_evidence.reported_cycles) — fold-in
1. File: plan.yaml T-01 intent, "Cycle contract" paragraph (l.141).
2. Line: 141.
3. Summary: the closed `cycle_evidence` object stores `reported_cycles`, a third copy of a number the run already carries.
4. Cost: the count lives in the run's existing `cycles_used` (feature-schema.json:58, written by run-end at feature-record.py:258) and, for lead-digest source, in the digest's `DIGEST.cycles_used`. Storing `reported_cycles` as well adds a third value, plus a three-way equality check in schema, `inv_7`, and table contracts; each can drift or contradict. A drifted copy is exactly the "contradictory evidence" case the task then has to refuse.
5. Alternative: lead-digest source stores only `source,path,sha256`; the check is `run.cycles_used == digest.cycles_used`. Keep an explicit count field only for `operator-history`, where no digest carries it (or let the authorization note carry it and compare to `run.cycles_used`). Recommendation: **fold-in**.

### A2 — task — T-01 intent l.143 (refusal object) — fold-in
1. File: plan.yaml T-01 intent, "Refusal contract" (l.143).
2. Line: 143.
3. Summary: `return_status: refused` (single-valued enum) plus a mandatory paired `refusal` object is two fields for one fact.
4. Cost: the presence of the closed `refusal` object already says "refused". A one-value status adds a pairing rule (status without object, object without status) that schema, `feature_schema` semantic checks, INV-15/INV-46 and the test list (l.148 "absent provenance") all have to enforce and test. This is the "threaded signal" delete-first warns about.
5. Alternative: optional `refusal` object only (BLOCKED-only, source/digest hash/reason/by/at/validation_exit-or-authorization), with `return_status` removed. Recommendation: **fold-in**.

### A3 — task — T-01 (three evidence-reference shapes) — fold-in
1. File: plan.yaml T-01 intent, l.136 (history/recovery evidence path/hash), l.141 (cycle_evidence path/sha256 + authorization path/hash), l.143 (refusal digest path/hash + authorization path/hash); rule restated again l.145 and in T-03/T-04.
2. Line: 136, 141, 143, 145.
3. Summary: feature-relative, hash-bound, traversal/symlink-confined evidence reference is specified separately for three records; only digest *selection* is named as shared (`digest_record`), not the reference type or resolver.
4. Cost: three closed object shapes and three resolve/verify paths for one rule ("resolve inside target feature, store normalized relative path + SHA-256, refuse traversal/symlink/changed hash/wrong subject"). The security-relevant confinement is the part most likely to diverge between the writer (CLI operand) and the reader (`inv_7`/INV-15/INV-46/gate), which is SC-04's stated "same hash-bound local reference" requirement.
5. Alternative: name one `evidence_ref` (`path`,`sha256`) schema `$def` and one resolver in an existing module (`feature_schema` or `digest_record`), taking `(feature_dir, operand)` and used by `record-cycle-evidence`, `record-refusal`, `recover-mirror`, and every reader; l.145 becomes the single authority and T-03/T-04 point to it. Recommendation: **fold-in**.

### A4 — task — T-01 intent l.136 (history snapshot) — fold-in
1. File: plan.yaml T-01 intent, github schema paragraph (l.136).
2. Line: 136.
3. Summary: `github.history[]` hand-models a "closed snapshot of previous milestone, parent, attached, issues, source_issues, typed and build_entry fields", a second closed copy of the `github` field set; `recovery` repeats evidence path/hash that the history entry already holds.
4. Cost: two authorities for the github block's fields. Every later `github` field addition has to be mirrored into the snapshot or history silently loses data (the failure the archive exists to prevent). The recovery/history evidence pair duplicates reference data to be kept in sync.
5. Alternative: history entry = `{recovery_id, at, repo, reason, evidence_ref, previous}` where `previous` validates against the same github sub-schema (`$ref`, minus `history`/`recovery`); `recovery` carries `id`, modes, state and plan hash and points to the history entry for evidence. Absence-versus-value is preserved by copying the prior object verbatim. Recommendation: **fold-in**.

### A5 — task — T-01 intent l.140 (binding resolution across gh-sync/INV-37/board_lifecycle) — briefing-row
1. File: plan.yaml T-01 intent, "Repository contract" (l.135) and gate paragraph (l.140).
2. Line: 135, 140.
3. Summary: "bound repo -> declared check -> product_config -> board_for, never fall back" is written for gh-sync, then restated for INV-37, board_lifecycle and merge-gate/post-merge-sweep; the plan names reuse of the receipt/provenance predicates but not a single home for the binding resolution itself.
4. Cost: up to four callers re-implement "present non-null factory.repo is authoritative, must be declared, no Harness fallback". Fallback-on-error is the original defect class, so one caller regressing reopens SC-01 quietly.
5. Alternative: the T-01 brief tells the executor to implement one pure `feature_binding(record, fleet)` (owner-checkout default when unbound; refusal reason otherwise) beside the existing seams and call it from all four; no new module required. Recommendation: **briefing-row** (an implementation placement note, not a plan change).

## Mission/task-shape observations (no finding raised)
- T-01 is one task over 33 anchors and three independent defects (mirror binding, cycle accounting, refusal). Its stated reason, no intermediate shipped layer, is accepted; the closed schema is shared. Left per the settled lane/shape set. Note only: the focused `verify:` (l.131) runs 5 suites and does not include `test-validate-digest.py` (SC-06 negative controls), merge-gate or post-merge-sweep; the plan defers those to the full-matrix run (l.132, 149), so leave.
- T-02..T-05 sit at the right altitude: authority amendments are limited to named clauses, T-03..T-05 are operational and single-sourced on the target-local authorization note. Restatement of the confinement rule in T-03/T-04 is resolved by A3.
- PF-2157 (recovery-marker read-back) remains OPEN for signature; no new cost raised beyond what the panel recorded.

Empty-result check: no finding for T-02..T-05 or mission altitude.
