# DOES THIS PLAN DELIVER THE OPERATOR'S STATED INTENT? — PASS

PASS. All six cycle-0 findings (G1–G5, A1) are CLOSED in the artifacts themselves, and a full re-run of
the cycle-0 grading over the current BRIEF.md and plan.yaml surfaces no new blocking gap. Graded
read-only against `issue://1308` (the authority named by the grilling note line 23) and
`.harness/notes/grilling-six-residual-bugs-2026-09-05.md`. Nothing edited.

`git -C .../BUG-1308-expertise-replace-drop status --porcelain`:

```
?? .harness/harness/features/BUG-1308-expertise-replace-drop/
```

(the whole feature dir is still untracked; this note is inside it — no other file written.)

## PART A — cycle-0 findings

**G4 — CLOSED.** The canonical sentence is byte-identical in all four places, each introduced as the
shared statement: BRIEF SC-09 (`BRIEF.md:92-95`), D-10 (`plan.yaml:106-109`), T-02 case17
(`plan.yaml:297-300`), T-03 intent (`plan.yaml:371-374`). Text in each: *"Every op verb the
distillation contract names is either accepted by the expertise-merge.py ops subcommand or is merge,
the one verb the contract itself rewrites with the literal sentence: a replace on the surviving id plus
a drop of the absorbed id; and the tool accepts no verb the contract does not name."* The cycle-0
contradiction is gone: case17 no longer says "set equality, not containment" — it mechanises the
sentence as `CONTRACT − ACCEPTED == REWRITTEN` and `ACCEPTED − CONTRACT == ∅` with
`REWRITTEN = {"merge"}` gated on a verbatim substring test (`plan.yaml:304-319`). No alternative
predicate is readable from it.

**G3 — CLOSED**, all seven elements present (`BRIEF.md:105-114`, `plan.yaml:330-344`): two invocations
against one file (`apply --entries` adding P-09/P-10 vs `ops` replacing P-07); overlap forced
structurally by `Popen`-both-before-wait, no sleep; both assertions present — id census (eight prior ids
plus P-09/P-10, none lost) **and** P-07 carrying the replacement marker text; bounded (`timeout=30` per
child, `TimeoutExpired` is a FAIL not a skip) and deterministic (order not asserted; either order yields
the same final state, `plan.yaml:343-344`); the lock regression is named in both shapes (D-09);
labelled `(REQ-07, concurrency half)`; task coverage is T-02 case18, which cites SC-11 by id.

**G1 — CLOSED.** `plan.yaml:247-256` — T-02 `traces:` is REQ-01 through REQ-09; REQ-01 and REQ-02 present.

**G2 — CLOSED.** SC-09 now has one reading: "asserts exactly this: <canonical sentence>" plus a
*mandatory* RED demonstration against two enumerated drifted copies — sentence deleted, and an extra
verb named (`BRIEF.md:95-98`, mechanised at `plan.yaml:321-329` as copies only, real SKILL.md never
written). The "fails if either side changes alone" judgement call is replaced by two named mutants.

**G5 — CLOSED.** `plan.yaml:420` greps
`^- DEC-216 .* :: .*replace and drop through the ops subcommand` — unique to the ruling, not the
incidental word `ops`. T-04 intent mandates that exact substring, unbackticked (`plan.yaml:444-449`),
and SC-10 states the same literal (`BRIEF.md:100-101`). Re-derived: index rows do carry the
`^- DEC-NNN … :: <ruling>` shape (`DECISIONS-INDEX.md:209-215`), and DEC-215 is the last entry, so
DEC-216 is free.

**A1 — CLOSED as a recorded deliberate decision.** D-13 (`plan.yaml:126-138`) keeps exactly one barrier
— T-02 `depends_on: [T-01, T-03]` (`plan.yaml:260`) because case17 grades the text T-03 writes — and
removes the other: T-04 `depends_on: [T-01]` only (`plan.yaml:410-411`). Cost named: "one orchestrator
round trip inside the build phase, priced against an 8-cycle cap, and it is paid once rather than
twice", with the reason reordering is impossible (a drift detector run before the text exists would
grade the pre-change file).

## PART B — full re-grade of the current artifacts

1. **Issue Requirement clauses → REQ:** replace atomically→REQ-01; drop→REQ-02; preserve caps→REQ-03;
   reject missing→REQ-04; reject ambiguous→REQ-05; fail closed/no partial rewrite→REQ-06; compatible
   with concurrent union-merge→REQ-07 (**now both halves**: SC-06 codes/tokens + SC-11 concurrency);
   focused regression coverage→REQ-09. REQ-08 derives from the issue's Alternative (D-11). New gaps: **none**.
2. **Regression cases → behavioural verify:** capacity SC-01/case11, removal SC-02/case12, missing
   SC-03/case13, ambiguous SC-04/case14(a,b,c), atomic failure SC-05/case15 — each asserts exit code +
   stdout token + post-state (entry count, `- G-03:` absence, sha256 identity). No content-only
   criterion among the five. New gaps: **none**.
3. **Traceability both ways:** tasks→REQ: T-01 REQ-01..07, T-02 REQ-01..09, T-03 REQ-08, T-04 REQ-08.
   SC→task: SC-01..05→case11-15, SC-06→case16, SC-07→T-01 unit file (u10 permanent red), SC-08→cases
   11/12 `check-expertise.sh`, SC-09→case17, SC-10→T-04, SC-11→case18. Orphans in either direction: **none**.
4. **Determinism:** every SC names an observable — exit codes, exact stdout tokens, sha256 identity,
   ordinal index 7, section counts, id census. New gaps: **none**.
5. **Verifiability (re-derived, nothing project-wide run):** `tests/integration/test-expertise-merge.py`
   exists and its case-8 idiom is real (`case_cap_drift_detector`, "Case 8 … read as TEXT from both
   files", `:259-261`); cases run to 10, so 11–18 are free numbers. `tests/integration/test-gen-decisions-index.py`
   exists; `check-expertise.sh` takes a file argument (`for arg in "$@"`, `:28`);
   `tests/unit/test-expertise-ops.py` is created by T-01. Anchors re-derived and both hold: SKILL.md
   `:112`/`:116` "Updates are **ops**, each naming its target:" / `# add | replace | merge | drop`;
   SPEC.md `:904` "The apply is a union merge, not a whole-file write". New gaps: **none**.
   *Advisory (non-blocking):* SC-11's "well under 60 seconds" holds on the pass path; two sequential
   `timeout=30` waits reach 60s only in the failure path, which is already a FAIL.
6. **Scope:** four tasks = implementation, focused tests, contract text, governing docs/decision — all
   inside the grilling note's allowed set (line 12). No shim (D-09 leaves `apply` unmodified), no
   redesign, no unrelated cleanup. New gaps: **none**.
7. **Finishable in 8 cycles / no waiver:** four tasks, one declared main-session barrier priced in
   D-13; no risk acceptance, scope reduction or gate waiver anywhere. New gaps: **none**.
8. **Dependency shape:** T-01 → T-03 → T-02, and T-01 → T-04. Acyclic, topologically orderable. No
   verify asserts anything a predecessor deletes — T-01 explicitly forbids touching `compute_union`,
   which is what SC-07's u10 red case and case16 both depend on continuing to exist.
   `check-plan-routes.py <this plan>` exits 0, 0 violations, T-03's carve-out recognised. New gaps: **none**.

## Open

- Nothing blocking. `plan.yaml` carries no `panel:` key yet — expected, this cycle produces it.
