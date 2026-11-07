# Receipt — harness-backend-dev — simplify · simplification · BUG-20261006-fleet-planning-recovery

BLUF: PASS (angle completed; not an implementation approval). 5 findings, none blocking; all are schema/seam
trimming inside T-01, none touches the settled set. The large cutover itself (binding, recover-mirror, evidence
accounting, refusal) survives the deletion test: each piece closes a named SC and reuses an existing seam. Read-only;
nothing applied, nothing executed.

Angle: `.agents/skills/harness-simplify/references/angle-simplification.md` (plan surface). Craft: `delete-first.md`.
Existing seams consulted at baseline: `feature-record.py` (`cmd_run_end` L240, `_close_run_stages` L628,
`_require_decision_file` L383), `digest_record.py`, `gh-sync.py` (`cmd_recover_terminal` L1271), `feature-schema.json`
runs[] (L56-59), `digest-schemas/harness-{eng,product,validator}-lead.json` (all carry `cycles_used`).

## Findings (file · line · summary · cost · alternative · recommendation)

### F1 — Evidence confinement is specified as new behavior; an existing confinement helper is not named
- File: `plan.yaml` T-01 intent, "Evidence confinement and authorization" paragraph (the paragraph after record-refusal, ~L145 of the file) vs `feature-record.py:383` `_require_decision_file`.
- Summary: `_require_decision_file` already does feature-dir realpath + `commonpath` confinement for `set-rework`/`raise-cycles`, but also accepts cwd-relative candidates — exactly what the plan forbids. The plan never says to replace it, so the cutover can end with two resolvers with different cwd semantics.
- Cost: four new reference sites (cycle_evidence, refusal, mirror authorization, history/recovery evidence) plus INV-7/INV-15 readers each need the same rule; hand-copied in the writer and again in the readers, a traversal/symlink fix lands in one and not the other. The old helper's looser rule stays live for INV-39 decisions.
- Alternative: one pure `feature_schema` predicate (resolve feature-relative, realpath, regular-file, in-dir, sha256) used by all writers, all `check_state` readers and `_require_decision_file` itself (tightened). State "no second resolver" in the intent the way it already says "no second parser".
- Recommendation: **fold-in** (one sentence in T-01).

### F2 — `cycle_evidence.reported_cycles` stores a fact that is already stored twice
- File: `plan.yaml` T-01 "Cycle contract" paragraph; `feature-schema.json` runs[].cycles_used L58.
- Summary: for source=lead-digest the plan requires `reported_cycles == DIGEST.cycles_used` (hash-bound file) and run-end also writes the same number as `runs[].cycles_used`. Three copies of one integer; INV-7 must then check all pairs.
- Cost: an extra schema field, an extra equality rule per reader/writer, and one more state that can disagree. Note `close-run` already takes `--cycles-used` AND a digest that carries the same value (`feature-record.py` L628, L794): the plan keeps the caller-typed count and adds a check that it matches the digest.
- Alternative: store `{source, path, sha256}` (+ `by/at/authorization` for operator-history); `runs[].cycles_used` stays the one attributed count; INV-7 verifies it equals the digest's `cycles_used` through `digest_record` when source=lead-digest. For operator-history the count is the entry's `cycles_used`, authorized by the hashed note. Optionally close-run derives the count from the validated digest and drops the flag, but that is a CLI change — decide at briefing.
- Recommendation: **fold-in** (drop `reported_cycles`); the close-run flag removal is **briefing-row**.

### F3 — `return_status: refused` is a single-valued enum that only mirrors presence of `refusal`
- File: `plan.yaml` T-01 "Refusal contract" paragraph.
- Summary: the plan itself says "no accepted status field is needed"; `return_status` has one legal value and is "paired" with `refusal`, so presence of `refusal` already means refused. Deletion test: removing `return_status` loses nothing.
- Cost: a second field plus a pairing rule (neither without the other, BLOCKED-only) in schema, `feature_schema`, close-run, record-refusal, INV-15/46 and fixtures; one more way for a record to be half-written.
- Alternative: `refusal` alone, with the BLOCKED-only rule on it. Likewise `refusal.validation_exit=1` is constant for source=close-run (close-run accepts only exit 1) and records nothing the source does not already imply; drop it too.
- Recommendation: **fold-in**.

### F4 — `github.history[]` snapshot is a hand-listed closed copy of the active github block
- File: `plan.yaml` T-01 schema paragraph ("closed snapshot of the previous milestone, parent, attached, issues, source_issues, typed and build_entry fields") and `feature-schema.json#github`.
- Summary: the snapshot enumerates the mapping fields a second time.
- Cost: the next field added to `github` (this change already adds `repo`) must be added to the snapshot or archived mappings silently lose it; "preserving absence versus value" then has two implementations.
- Alternative: define the mapping fields once as a schema `$defs` shared by the active block and the history snapshot (snapshot = that def plus its own `repo`), so absence-versus-value semantics live in one place.
- Recommendation: **fold-in** (low).

### F5 — Operator-history authorization shape repeats three times
- File: `plan.yaml` T-01: cycle_evidence (`by, at, authorization path/hash`), refusal (`by, at, authorization path/hash`), github.history/recovery (`evidence path/hash`, authorization for mirror).
- Summary: the same `{by, at, path, sha256}` reference is spelled separately per record; `record-cycle-evidence` and `record-refusal` also both do "evidence authorizes this exact run/subject/hash".
- Cost: three closed definitions and three "authorization for a different feature/repository/run/plan/operation" checks that can drift; the plan's own wording already differs ("authorization" vs "evidence").
- Alternative: one closed `evidence_ref` def and one `operator_authorization` def in the schema, one `feature_schema` verifier parameterized by subject (run id+hash / repo+plan); both new verbs and recover-mirror call it. Pairs with F1.
- Recommendation: **fold-in** together with F1.

## Considered, no finding
- T-01 size (33 anchors): mirror provenance (SC-01/02) and run accounting (SC-03..06) share only the closed schema and the evidence resolver; the single-task decision is explicit and settled. Size alone is not flagged. If F1/F5 are not taken, that shared resolver is the only coupling and would be the natural split seam — **leave**.
- recover-mirror vs `recover-terminal`: reuses `_recover_terminal_apply` routes, milestone 422 recovery, and the work-started rule per the plan; passes the deletion test (adoption-only cannot replace mappings). Not flagged.
- Marker read-back: already recorded as open PF-2157; no new cost found here beyond the plan's own bounds. Not re-raised.
- Dual live/historical verbs (`close-run --refused-return` vs `record-refusal`; `run-end --digest` vs `record-cycle-evidence`): settled (PF-0dbb); distinct payloads. Not flagged.
- Wide reader fan-out (merge-gate, post-merge-sweep, INV-37, board_lifecycle): plan routes all through pure `feature_schema` predicates; justified by SC-01. Not flagged.

## Principles applied
- Delete First: F2/F3 each delete a field the plan's own other fields already imply; F1/F5 collapse repeated checks into one existing seam.

files_touched: [] (receipt excluded). Verification: none run (read-only assignment).
