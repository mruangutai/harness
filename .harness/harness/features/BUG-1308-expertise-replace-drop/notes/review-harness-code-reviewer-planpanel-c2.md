# Plan-panel c2 — scope reader — BUG-1308-expertise-replace-drop

BLUF: the cycle-1 HIGH is closed in spec (stable `(section,id)` key + base-order rebuild pass, with
explicit order-independence and two new composition cases). No orphan REQs, no non-topological
dependency, no verify asserting something a predecessor deletes. Four new findings, all MED/LOW,
none gating: two are fresh verification-adequacy gaps the revision didn't reach (the operator's own
R2 mechanism is untested; T-01/T-02 verify still run whole suites so the flagship fix isn't
task-verify-falsifiable), one is an untested-but-determined edge case, one is a record
inconsistency between `D-15`'s prose and `panel.findings.disposition`.

## Standing question — orphan/dangling task-REQ hunt

No orphan `REQ`. `REQ-01..09` all appear in some task's `traces:`; every task cites only REQs that
exist (`T-01`→REQ-01..07, `T-02`→REQ-01..09, `T-03`→REQ-08, `T-04`→REQ-08). Dependency shape
`T-01→T-03→T-02`, `T-01→T-04` is acyclic and topological (`plan.yaml` `depends_on` fields, T-01:
`[]`, T-03: `[T-01]`, T-04: `[T-01]`, T-02: `[T-01, T-03]`). No verify block asserts anything a
predecessor deletes: T-01 is forbidden from touching `compute_union`/`cmd_apply`
(`plan.yaml` T-01 intent, "Do not touch compute_union, cmd_apply..."), so T-02's `case16` add-only
assertions are never undermined by T-01.

## (i) T-01 Step D, adversarial read

Read as a builder with no other context: Step D specifies a **rebuild**, not an in-place edit — walk
each section's base entries in original order, look up `(section, id)` against an ops index built in
Step B/C (which already forbids two ops naming one key), emit/skip/replace accordingly, then append
adds in proposal order (`plan.yaml:558-566` region, Step D text). This genuinely removes index
arithmetic from the addressing vocabulary — no op ever "carries, stores or computes a position"
(Step B). Order-independence for replace/drop is **stated**, not merely implied: "the merged section
is INDEPENDENT OF THE ORDER the ops were given in for replace and drop. Only adds are
order-sensitive, and only relative to each other" (`plan.yaml` Step D closing paragraph).

Six shapes, checked:
- multiple drops in one section — determined, tested (`u12`).
- drop + replace in one section — determined, tested (`u11`, `case19`).
- drop + add in one section — determined, tested by pre-existing `u8` (unchanged by the revision).
- ops in any order — stated explicitly as order-independent for replace/drop; tested both directions
  by `u11` and `case19`'s reversed-op run.
- section reduced to **empty** by drops — the general rebuild rule handles this without
  special-casing (empty walk output, no adds ⇒ `merged[section] == []`), so it is **not
  UNDETERMINED**. It is, however, **untested**: no case in `u1..u12` or `case11..case19` drives a
  section to zero entries. Severity: LOW — determined by spec, only a coverage gap, and REQ-02
  plausibly includes "drop the last surviving entry in a section" as a realistic distillation shape.
- an op naming the **only** entry in a section — same as above, subsumed by the general rule,
  likewise untested. Folded into the same LOW finding.

`D-06`'s amendment (relative order, not exact index) is consistent everywhere it is cited: Step D
("keeps its original ordinal among the surviving entries (D-06)"), `T-04`'s SPEC intent
("a replace rewrites the entry ... without moving it so a replace-only proposal leaves section size
and ordinals unchanged"), and `BRIEF.md` SC-01 ("7th ordinal") — SC-01 is replace-only so absolute
and relative ordinals coincide there; no contradiction found.

`u11`/`u12`/`case19` actually exercise what's claimed: `u11` asserts the exact composed sequence
`[P-02,P-03,P-04,P-05]` plus marker-text isolation, in both op orders; `u12` asserts
`[P-02,P-03,P-05]` length 3 for two drops; `case19` is the CLI-level analog of `u11` plus a
byte-identical reversed-order run. All match their prose claims.

## (ii) Dangling references to deleted content — none found live

Grepped `plan.yaml` and `BRIEF.md` for `u4`, `case14`, `cross-section`, `whole-file`, and
ambiguity-condition counts. Every `u4`/`case14(a)` occurrence is one of: the verbatim, untouched
`panel.findings` reader record (historic, correctly left alone), `T-01`'s "There is no u4: ... it is
unrepresentable" (asserts non-existence), or `T-02`'s "sub-case (a) ... is DELETED, not renamed"
(asserts non-existence). `BRIEF.md` SC-04 states "two ambiguity conditions ... no third condition,"
matching `D-03`'s "Exactly two conditions." No coverage table, SC, or decision anywhere still counts
three conditions or describes the deleted mode as live. `case14`'s remaining sub-cases keep their
`(b)`/`(c)` labels with no renumbering, and the plan says so in place — exactly the numbering-gap
mitigation the assignment asked me to check for.

## (iii) Falsifiability of every `verify:`

- **T-01** (`python3 tests/unit/test-expertise-ops.py`) and **T-02**
  (`python3 tests/integration/test-expertise-merge.py`): both name paths/binaries that exist today
  (confirmed on disk except `tests/unit/test-expertise-ops.py`, correctly absent — T-01 creates it).
  Both remain **whole-suite invocations** after the revision. This is a live, unaddressed gap: an
  implementation that never writes `u11`/`u12`/`case19` (or writes them vacuously) still exits 0 on
  both verifies, so **SC-12 — the plan's fix for the cycle-1 HIGH — is not falsifiable by the task's
  own automated verify**; confirming it requires a manual read of the suite for the named cases,
  exactly as this goal-check and I both had to do. `T-03`/`T-04` closed the analogous cycle-1 med
  finding with token greps; `T-01`/`T-02` did not receive the same treatment, and none of the four
  operator rulings (R1-R4) named it. **Finding, MED.**
- A second, sharper instance of the same shape: `D-05`/`SC-04`'s new claim — an op missing `section`
  on **any** verb refuses at exit 12 MALFORMED OPS — is the mechanism that actually *enacts* the
  operator's R2 ruling (deleting the optional-section affordance), yet **no case in `u1..u12` or
  `case11..case19` exercises it**. `u7` is the only exit-12 case and it targets `op: merge`, not a
  missing `section` key. A shape-check bug here (e.g. a missing-section op silently resolving
  whole-file, reintroducing the mode the operator explicitly removed) ships undetected by every
  verify the plan declares. **Finding, MED.**
- **T-03** and **T-04**: verify blocks are token greps over files confirmed to exist
  (`.claude/skills/harness-distill/SKILL.md`, `SPEC.md`, `DECISIONS.md`, `DECISIONS-INDEX.md`,
  `tests/integration/test-gen-decisions-index.py` — all present via `glob`). Both were demonstrated
  RED against the unbuilt tree per the revision note, so they discriminate. No predecessor deletes
  anything either verify depends on.

No verify block asserts something a predecessor task deletes; no non-topological ordering found.

## Cycle-1 finding disposition (my own three, from `runs/2026-09-05-plan-panel-c1-validator/`)

| Cycle-1 finding | Status |
|---|---|
| HIGH — Step D index-shift, untested | **CLOSED.** Rebuild-from-base-snapshot pass, stable `(section,id)` key, explicit order-independence, `u11`/`u12`/`case19`. See residual MED above (verify falsifiability of the closure itself — a related but distinct concern). |
| MED — T-03/T-04 verify narrower than intent | **CLOSED.** Both verify blocks now grep the previously-omitted tokens (7/8/9/12, apply-unchanged sentence for T-03; SPEC's 10/11/12 and DEC-216's Over/Because/Tradeoff/DEC-refs for T-04). Confirmed present in `plan.yaml`. |
| INFO — exit-12 byte-identity unit-proven only | **OPEN, unchanged.** `u7` is still a pure `resolve_ops`/`cmd_ops`-adjacent unit call; no `case11..case19` drives MALFORMED OPS through the CLI with a sha256 before/after. Matches the revision note's own "no action" disposition. |

## New finding — record inconsistency (not one of the three settled rulings)

`D-15` states "`PF-f4d258f365f54f04d9cc976baf0ad981` is resolved before signature," yet
`panel.findings` still carries `disposition: open` with no `resolved_by:` for that finding or for
the other three the operator ruled on (`PF-3f8a11143ba40f67b0f326d532381d5e`,
`PF-21e98fb21fbbe9fefe7c47cc9784c99b`, `PF-0fd81890be0279f72e1fd44bc27f9828`). The revision note
defends this as deliberate ("panel: untouched ... because the panel is re-run and re-recorded after
this revision"), which is in tension with `D-15`'s own "is resolved" language — the field the
signature step reads still contradicts the prose the operator is meant to sign. This is the same
inconsistency the c2 goal-check already raised as its own non-blocking `Q1`; it remains unfixed in
the plan.yaml on disk. **Finding, MED** — administrative/record risk (wasted re-adjudication cycle or
gate confusion), not a functional defect.

## Severity summary

No `high`/`critical`/`unrated` finding from this reader. Four `MED` (untested R2 exit-12 mechanism;
T-01/T-02 whole-suite verify unfalsifiability for SC-12; the `D-15`/`panel.findings` disposition
contradiction — three new; plus the record-inconsistency item is a fourth), one `LOW` (untested
empty-section/single-entry-section outcomes). None must-fix under this reader's judgment; all are
should-fix / advisory to the operator's next pass.

## git status (verbatim, for the lead — I hold shell, the lead does not)

```
 M .harness/harness/features/BUG-1308-expertise-replace-drop/feature.json
?? .harness/harness/features/BUG-1308-expertise-replace-drop/notes/research-BUG-1308-expertise-replace-drop-goalcheck-plan-c2.md
```

All six mandated files read in full: `plan.yaml` (both halves), `BRIEF.md`, the c2 goal-check note,
`expertise-merge.py`, `harness_merge.py`, `harness-distill/SKILL.md`. Revision note and cycle-1
digest read as context.
