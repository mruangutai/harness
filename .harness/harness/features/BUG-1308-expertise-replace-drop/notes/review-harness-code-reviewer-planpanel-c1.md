# Plan panel c1 — scope reader (harness-code-reviewer) — BUG-1308-expertise-replace-drop

BLUF: PASS-with-notes overall shape (traceability, exit-code allocation, dependency graph, doc
anchors all check out), but one **HIGH** finding: the plan's own spec for applying multiple
ops to one section is ambiguous in a way that permits a real index-shift corruption/crash bug,
and no unit or integration case in T-01/T-02 exercises the combination that would expose it.
Per constraints this returns to the lead; I am not accepting risk on it.

## Six mandated files — what each settled

1. `plan.yaml` (full, both halves) — read. Settled the task graph, decisions D-01..D-13, and the
   exact wording of T-01–T-04's `intent:`/`verify:` blocks used below.
2. `BRIEF.md` — read. Settled REQ-01..09, SC-01..11 (all `verify: automated`, none
   `verify: inspection` — so Stage-1's inspection-citation duty does not apply to this
   plan-only cycle), and the constraints/verification-gaps sections.
3. `notes/research-...-goalcheck-plan-c1.md` — read. A prior PASS re-grade; I independently
   re-verified its G1–G5/A1 closure claims (DEC-216 free slot, SKILL.md:112/116 anchors,
   SPEC.md:904 anchor, check-expertise.sh CAPS/arg-loop) rather than trusting them, per G-01/P-03.
4. `expertise-merge.py` (full, all elided ranges re-read) — confirmed `compute_union`,
   `cmd_apply`, `parse_expertise`, `render`, `CAPS = {"Patterns":15,"Gotchas":15,"Outcomes":10,
   "Open":5}`, `require_expertise_destination`, and exit codes 0/6/7/8/9 exist exactly as the
   plan describes them; **10, 11, 12 are unused anywhere in this file today**; argparse's own
   exit 2 is untouched (only one subparser, `apply`, currently registered).
5. `harness_merge.py` (full, all elided ranges re-read) — confirmed `locked_update(path,
   transform, timeout=None)` and `MergeRefusal(code, lines)` exist as described; confirmed D-08's
   byte-identity claim structurally: `locked_update` never calls `os.replace` when `transform`
   raises, for *any* refusal code — this is a property of the shared core, not something T-01
   has to reimplement. Confirmed D-09: both subcommands would lock on `<file>.lock`, so `ops`
   and `apply` serialise against each other automatically once `ops` calls
   `harness_merge.locked_update(resolved, transform)` on the same resolved `--file` path.
6. `harness-distill/SKILL.md` — read. Confirmed the cited anchors: `:112` "Updates are **ops**,
   each naming its target:", `:116` "# add | replace | merge | drop" — both exist and say what
   the plan says they say.
7. `tests/integration/test-expertise-merge.py` (full, all elided ranges re-read) — confirmed
   helpers `write_file(path, sections)`, `write_entries(path, sections)`,
   `target(root, stem)`, `run_apply(file_path, entries_path)`, `check(name, ok, detail="")` all
   exist with the signatures T-02 assumes. Confirmed existing case numbering is 1,2,3,4,5,6,8,9,10
   (case 7 was never used) — so 11 onward really is free, and case 8's "read CAPS as TEXT from
   both files" idiom is real (`case_cap_drift_detector`).

## Findings

### F1 — HIGH — Step D's apply-in-order/resolved-index spec permits an untested index-shift bug for same-section multi-op proposals

`plan.yaml:197-200` (T-01 intent, Step D): *"application, in the order the ops were given...
drop removes the entry at the resolved index"* where "resolved index" is explicitly computed
against the **original** base_sections (`plan.yaml:186-187`, Step B: *"EVERY op against the
ORIGINAL base_sections, never against the result of an earlier op"*).

**Concrete failure scenario.** Patterns holds `[P-01..P-05]` at indices 0-4. A proposal carries
two ops on the *same section*: op1 = drop `P-01` (original index 0), op2 = replace `P-05`
(original index 4). A literal reading of Step D — apply sequentially, "remove the entry at the
resolved index" — pops index 0 first, shrinking the list to 4 items; op2 then tries to act on
index 4 of a now-4-item list: either an `IndexError` (crash on a well-formed proposal) or, if the
implementation instead re-derives a "current" index some other ad hoc way, a silent write to the
**wrong entry**. Reversing the two ops in the same proposal does *not* crash (replace first
doesn't change length), so the bug is order-dependent — the kind that looks fine until the one
op-ordering a real distillation proposal happens to use.

**Why nothing catches this.** I re-checked every case named in T-01 and T-02 for a scenario
where two ops resolve against *different original indices in the same section*:
- u8 (`plan.yaml:237`) is the only multi-op-same-section unit case, and it is drop+**add** —
  add is append-only and order-independent, so it can never exercise the index-shift path.
- u1-u7, u9, u10 are all single-op cases.
- case15 (`plan.yaml:289-292`, ATOMIC FAILURE) is the only multi-op integration case with a
  replace *and* a drop together, but its third op is invalid, so nothing is ever applied and the
  merged result of ops 1+2 is never rendered or inspected — atomicity is proven, index
  correctness is not.

REQ-01 and REQ-02 (replace, drop) are the two requirements this bug would violate, and this is
exactly the scenario harness-distill's own condense-at-cap guidance
(`harness-distill/SKILL.md`: *"condense until you are under it"*) makes a realistic distillation
shape — dropping/replacing several entries in one section in one proposal. Severity is HIGH
because the failure mode is a realistic case (REQ-01/02's core mechanism, silently misapplied or
crashing) with zero test evidence either way — per the dispatch's own standard, this is a
success-criterion (SC-01/SC-02's multi-op composition) that no task actually produces evidence
for. Recommend: pin the intent to a diff-based semantics (drops/replaces computed against
original indices and rebuilt as one pass, independent of proposal order) and add one unit case
(two drops, or drop+replace, at different original indices in one section) plus one integration
case exercising the same shape to a successful (not atomic-failure) landing.

### F2 — MED — T-03 and T-04 `verify:` blocks check a narrow subset of what their own `intent:` mandates

`plan.yaml:359-363` (T-03 verify) greps for 4 strings: the invocation shape, the merge-rewrite
sentence, `MISSING TARGET`, `AMBIGUOUS TARGET`. T-03's intent (`plan.yaml:392-401`) additionally
requires the file to state target/section requiredness rules, the full refusal vocabulary for
**7 CONFLICT, 8 CAP EXCEEDED, 9 (not an Expertise file), and 12 MALFORMED OPS** (`plan.yaml:395-
396`), and "add-only proposals may still go through apply --entries, unchanged." None of that is
machine-checked — an executor who satisfies only the 4 greps produces a passing task with an
incomplete doc.

`plan.yaml:416-422` (T-04 verify) greps for the DEC-216 header, the DECISIONS-INDEX ruling
substring, `expertise-merge.py ops` anywhere in SPEC.md, and runs the index generator test. T-04's
intent (`plan.yaml:424-443`) additionally requires SPEC.md to state exit codes 10/11/12
specifically beside 6/7/8/9, that caps are pointed at rather than restated, and DECISIONS.md's
DEC-216 entry to carry a specific Chose/Over/Because/Tradeoff content (naming DEC-66/95/145) —
none of which the verify command confirms.

This is not blocking on its own (docs content-completeness is reasonably left to the executing
agent and a later reviewer per "no more specific than necessary"), but it is a real
success-criterion-with-no-evidence gap on the *mechanical* verify path specifically, so I record
it distinctly from F1. Recommend tightening both verify blocks to grep at least the exit-code
tokens (`10`, `11`, `12` beside `MISSING TARGET`/`AMBIGUOUS TARGET`/`MALFORMED OPS`) and the
DEC-216 `Over:`/`Because:`/`Tradeoff` labels, or accept the gap explicitly as inspection-only.

### Note (info, non-gating) — exit-12 byte-identity is unit- but not integration-proven

u7 (`plan.yaml:236`) proves `resolve_ops` raises `MergeRefusal(12, ...)` for `op=merge`, but as a
pure-function call with no file I/O, so it says nothing about whether the CLI path leaves the
file untouched. No T-02 case exercises MALFORMED OPS through the actual CLI with a sha256
before/after check the way case13/14/15 do for codes 10/11. This is low-risk only because the
guarantee is structural in `harness_merge.locked_update` (proven generic to *any* raised
`MergeRefusal`, already regression-tested via the pre-existing exit-7/8/9 cases) rather than
something T-01 has to reimplement per refusal code — and REQ-09 does not name "malformed" among
the regression shapes it requires, so this is fully in-scope-compliant. Recording per P-15 so it
is not silently re-raised later.

## What I checked and did NOT find a defect in

- REQ↔SC↔task traceability both directions: no orphans (REQ-01..09 all traced; SC-01..11 all
  have a task producing evidence).
- Dependency graph: T-01 → {T-03, T-04} → T-02 (T-02 depends on both T-01 and T-03) is acyclic
  and topologically valid; T-04 correctly drops the T-03 dependency per D-13, and the files each
  task touches never overlap, so T-03/T-04 parallelism is safe.
- No task's verify asserts something a predecessor deletes: T-01 explicitly forbids touching
  `compute_union`/`cmd_apply`/`parse_expertise`/`render`/`CAPS`/`require_expertise_destination`,
  and T-02's case16 plus u10 both depend on exactly those surviving unmodified.
  `check-plan-routes.py` result cited in the goalcheck note is consistent with my own read.
  DEC-216 slot is genuinely free (DECISIONS.md's last entry is DEC-215 at `:6762`,
  DECISIONS-INDEX.md's last row is DEC-215 at row 215) — verified myself, not taken on faith.
- The canonical "replace on the surviving id..." sentence is byte-identical everywhere it must
  be (D-10, BRIEF SC-09, T-02 case17, T-03 intent, and now also T-01's own op=merge refusal
  message text) — re-checked myself rather than trusting the goalcheck note's G4 closure.

## git status

`git -C <tree> status --porcelain`:
```
?? .harness/harness/features/BUG-1308-expertise-replace-drop/
```
No other path dirty. I wrote only this note; no edit to plan.yaml, BRIEF.md, or any source/test
file.
