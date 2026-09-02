# BRIEF — FEAT-54 Handoff Done when

## Problem

A handoff note tells the successor what to do next and never tells it what finishing that action
looks like. The successor therefore re-derives the completion boundary from the plan, the brief and
the run digests, and when it guesses wrong it either stops early or keeps going past the seam. The
grilling measured the gap directionally over the FEAT-48/50/51 build handoffs: with the current
four-section note, a reader recovered 65.9% of the required facts about the next action and produced
3 of 15 perfect responses; with an explicit completion boundary, 96.5% and 13 of 15 (30-run
comparison, measured in the grilling session 2026-09-02). That is evidence about reading THESE notes,
not an accuracy claim about Harness, and no token or latency saving is claimed — total character
volume rose 2.8% and latency was inconclusive.

## Goal

Every handoff note written or edited from now on says where the immediate next action ends, in one
fixed, machine-checkable section whose authorities point at real targets — so the successor validates
the boundary instead of inferring it. The 141 handoff notes already on disk stay valid and untouched.

## Requirements

- REQ-01: Every newly written or edited handoff note states the completion boundary of the immediate
  action in `## Next` — not of the phase, and not of the feature — in a fifth standalone
  `## Done when` section.
- REQ-02: The section has one fixed shape: exactly one `Scope:` line carrying a concise action label,
  then one to four `Authority:` lines, and no other prose.
- REQ-03: Listed authorities combine as a logical AND: the action is complete only when every one of
  them is satisfied.
- REQ-04: An authority cites one of exactly four bounded kinds — a plan task's `verify`, a BRIEF
  success criterion, a validation finding, or an explicit user approval gate. A source-code location
  alone is not an authority.
- REQ-05: Authorities are typed, machine-readable pointers: `plan-task:T-03.verify`,
  `brief-sc:SC-04`, `finding:<path>#F-02`, `approval:<path>#<heading>`.
- REQ-06: A pointer that names no existing target is refused when the note is written or edited;
  syntactic well-formedness alone never passes at write. Resolution is a WRITE-TIME obligation
  only: the check over the persisted corpus verifies section presence, block shape and pointer
  grammar, and never re-resolves a pointer's target, so an untouched note that was valid when
  written cannot be invalidated by a later change to something it points at.
- REQ-07: Untouched historical notes remain valid: enforcing the new contract requires no edit to any
  note that existed at this feature's BASE COMMIT — `git merge-base main HEAD` = `b7956fc4`, where
  141 files match `.harness/harness/features/*/notes/handoff-*.md` and 0 of them carry
  `## Done when`. A handoff note written DURING this feature's own build is a new note: it complies
  with the five-section contract and is not added to that baseline.
- REQ-08: The 60-line whole-file cap still applies unchanged, and no section gains a per-section cap.
- REQ-09: No live document or gate still tells an author the contract is four sections — the
  template, the orchestrator playbook seam paragraph and the decision record all state five.
- REQ-10: The deterministic checks — section presence, block shape, pointer resolution — run in the
  permanent gates. The nondeterministic comprehension benchmark is rerunnable on demand at review and
  never joins the normal test run.

## Constraints

Out of scope, as the operator settled it (grilling `## Out of scope`):

- Rewriting the historical handoff corpus; no mass migration of the 141 notes.
- Raising the 60-line handoff cap.
- Section-specific caps for `Next`, `Trust`, `Dead ends` or `Working set`.
- Claiming token or latency savings from this change.
- Making the exploratory model benchmark a permanent automated release gate.

Decisions that bind, by number:

- DEC-159 SUPPLIES the contract being amended (four sections, write-time shape gate, INV-17 corpus
  scan) and DEC-160 SUPPLIES the 60-line cap. This feature extends the first and keeps the second.
- DEC-174 BLOCKS squad execution on the gate scripts and their tests: `check-domain.sh`,
  `check-state.sh`, `test-check-domain.py`, `test-check-state.py`, `run-unit-tests.sh` and any module
  those gates import are main-session-direct, whatever the domain resolver grants.
- DEC-179 BLOCKS a second matcher: pointer resolution has one implementation, reached by both gates.
- DEC-163 BLOCKS resting a criterion on a test kind whose `cmd` is null.
- `.agents/` is a symlink to `.claude/`; every path is written in the `.claude/skills/...` spelling
  the domain grants use.

## Success Criteria

- SC-01: A handoff write carrying the four historical headings and no `## Done when` is refused, and
  the refusal names the missing section and the template; the same write with a well-formed block is
  allowed.
  verify: automated        evidence: integration
- SC-02: Each malformed block is refused, one fixture per violation: zero `Scope:` lines, two
  `Scope:` lines, zero `Authority:` lines, five `Authority:` lines, and a non-blank line that is
  neither. Each refusal names the count that broke the rule.
  verify: automated        evidence: integration
- SC-03: For EACH of the four authority types, a note whose pointer of that type resolves is allowed
  and a note whose pointer of that same type names no existing target is refused — eight fixtures,
  four resolving and four unresolvable, one pair per type, asserted separately so a type that
  resolves nothing cannot hide behind the other three.
  verify: automated        evidence: integration
- SC-04: The state check run over this repository's own corpus at `review_sha` reports no handoff
  violation — including over every handoff note this feature itself wrote, which is a NEW note and
  therefore carries `## Done when` like any other, and is not added to the frozen baseline.
  Verified at REVIEW TIME, not by a permanent suite case: at `review_sha`, from the repository
  root, the reviewer runs `bash .claude/skills/harness/bin/check-state.sh` and records its exit
  status, and that no reported line names `Done when`, in their own per-feature review note
  `.harness/harness/features/FEAT-54-handoff-done-when/notes/review-<reviewer>-*.md` — the
  deterministic place a later reader audits for whether this was executed. Falsified by any
  such line, including one naming a note this feature wrote. A permanent test case that scanned
  the live corpus would redden whenever a concurrent feature wrote a pre-sweep handoff note
  (operator ruling of 2026-09-02 on PF-570b9c87); the deterministic half of the claim — a clean
  corpus and no note mutated by the scan — is T-06 case (g) over a fixture corpus.
  verify: inspection
- SC-05: The 60-line cap still fires: a five-section note of 61 lines is refused with the cap
  message, and the same note at 60 lines is allowed.
  verify: automated        evidence: integration
- SC-06: An edit of a note that does not add `## Done when` is refused, so a note can leave the
  historical set only by becoming compliant; the state check keeps exempting that path and checks the
  section's shape once it is present.
  verify: automated        evidence: integration
- SC-07: Block parsing and pointer resolution have ONE implementation. Read at `review_sha`
  (`git show <review_sha>:<path>`): `check-domain.sh` imports `handoff_done_when` at one cited
  file:line and `check-state.sh` imports it at one cited file:line, and NEITHER gate carries a
  second block parser or a second pointer resolver of its own — no other parsing of the
  `## Done when` body and no other reading of a pointer target appears in either file.
  verify: inspection
- SC-08: Read at `review_sha` (`git show <review_sha>:<path>`), no assertion about the CURRENT
  contract survives as four sections in `.claude/skills/harness/templates/HANDOFF.md`,
  `.claude/skills/harness/SKILL.md`, the DEC record, or ANYWHERE in `check-domain.sh` or
  `check-state.sh` — required-section lists, heading constants, normative comments AND user-facing
  refusal or cap messages alike; each states five and names `## Done when`.
  EXEMPT, and to be left byte-identical: a comment that reports a PAST MEASUREMENT or a past
  incident rather than the live contract, identified mechanically by BOTH naming a specific past
  commit sha or a past feature id AND reporting what was observed at that point — a count taken
  then, or the behaviour of the code as it stood then. PRINCIPLES rule 15 forbids rewriting the
  record, so such a line is not a defect and no task orders it edited. The
  two known exempt sites, named by content because line numbers move, both in `check-state.sh`:
  the FEAT-31 74-note migration measurement ("Measured at cf51dce ... All 74 carry the four
  headings and are within the cap") and the INV-17 empty-body-check narrative (FEAT-31 T-10, "a
  note carrying all four headings and nothing under any of them passed").
  Falsified by: any line, or any comment wrapped across lines, in either gate script that states
  the CURRENT contract as four sections — a required-heading list, a heading constant, a normative
  comment above a branch, or a refusal or cap message enumerating intent, trust, dead ends and a
  working set without `## Done when`. A line meeting the exemption test above is NOT a falsifier.
  verify: inspection
- SC-09: The comprehension benchmark is rerunnable on demand and absent from the normal suites:
  with the probe registered, `run-unit-tests.sh`'s probe-registration check reports zero KIND-DRIFT
  lines over the real config; un-registering that kind produces a KIND-DRIFT line naming
  `probe-handoff-comprehension.py`; and the probe's basename appears in neither `UNIT_SCRIPTS` nor
  `INTEGRATION_SCRIPTS`, so `--kind all` never executes it.
  verify: automated        evidence: integration
- SC-10: The operator writes one real handoff note in the new shape and judges the refusal messages
  actionable, the section worth its lines against the 60-line budget, and the `Scope:` label the
  template and the refusal messages led them to write as describing the IMMEDIATE action in
  `## Next` — a label naming the phase or the feature instead must read as wrong against the
  template's own wording.
  verify: uat
- SC-11: This feature touched no handoff note that existed before it. Run from the REPOSITORY ROOT
  (a run from a subdirectory silently empties the diff arm), with
  `BASE=$(git merge-base main <review_sha>)` and the two sorted arms — the diff arm
  `git diff --name-only $BASE <review_sha> -- '.harness/harness/features/*/notes/handoff-*.md' | sort`
  and the base arm
  `git ls-tree -r --name-only $BASE -- .harness/harness/features | grep -E 'notes/handoff-[^/]+\.md$' | sort`:
  - PRIMARY CLAUSE: `comm -12 <(diff arm) <(base arm)` prints NOTHING. The diff runs from this
    feature's base commit to `review_sha` and is intersected with the notes that existed at that
    base, so a commit inside this feature that rewrote a historical note appears in this output.
  - POSITIVE CONTROL: `comm -23 <(diff arm) <(base arm)` prints AT LEAST ONE LINE, and its output
    equals, set for set, the handoff notes this feature added —
    `git diff --diff-filter=A --name-only $BASE <review_sha> -- '.harness/harness/features/*/notes/handoff-*.md' | sort`.
    An EMPTY control FAILS this criterion: it means the diff arm read no paths at all, so the empty
    primary clause proves nothing. `comm -13` is NOT the control — it lists the untouched baseline
    notes and stays non-empty however broken the diff arm is (measured 137 lines on a stand-in
    range whose diff arm was healthy, and 141 on a range whose diff arm printed zero paths).
  verify: inspection
- SC-12: Authorities combine as a logical AND, distinguished from ANY observably: a block of four
  authorities of which three resolve and one does not is REFUSED with exactly one message naming
  the unresolvable pointer, while the same block with all four resolving returns no problem at all.
  verify: automated        evidence: unit
- SC-13: An authority outside the four types is refused by the write gate (exit 2) with a message
  listing the four legal prefixes — asserted twice, once for an unknown prefix and once for a bare
  source-code location such as `check-domain.sh:1523`, so "a code location is not an authority" is
  observed rather than assumed.
  verify: automated        evidence: integration
- SC-14: No per-section cap is introduced, asserted on BOTH gates with a separately named case in
  each: a five-section note whose `Trust` section runs 25 lines and whose whole file is exactly 60
  lines is ALLOWED by the write gate (exit 0, and no cap message in stderr) in
  `test-check-domain.py`, AND is reported by no line of the state check in `test-check-state.py`.
  The only length refusal remains the 60-line whole-file cap, so a per-section cap sneaked into
  either gate reddens one of the two cases.
  verify: automated        evidence: integration
- SC-15: The persisted-corpus check never re-resolves a pointer target, asserted as a pair in
  `test-check-state.py`: (e1) a note — baselined or not — whose block is well formed and whose
  pointers are grammatically legal but name targets that do not exist is reported by NO line of
  the state check; (e2) the same note with a malformed block IS reported with the count named,
  and a note whose authority prefix is outside the four legal types IS reported with the four
  legal prefixes listed. So a later BRIEF that renumbers an SC cannot redden an untouched note,
  while shape and grammar violations stay caught.
  verify: automated        evidence: integration

## Verification gaps

- `eval` has no runner (`cmd: null` in `.harness/harness.json` `test_kinds`): the claim that the
  fifth section improves a reader's comprehension is NOT mechanically proven. What carries it is the
  locally-run comprehension probe, rerun by hand at review, and the grilling's 30-run measurement —
  directional evidence, not a gate.
- `ui`, `component` and `typecheck` have no runner and no surface here; nothing rests on them.

## Approval

status: pending
approved-by:
date:
