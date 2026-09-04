# Code review c6 — FEAT-54, review_sha dd55b3570c6a20f5ca1da016d6959752bd0ffc74

**PASS.** F-11 is closed at a committed SHA in all three real handoff notes. SC-07, SC-08, SC-11
all verified PASS by direct pinned-byte inspection. Stage 2 ran for the first time at any SHA for
this feature and found nothing gating: 90/90 changed Python functions pass their risk-grade bar, no
new fail-open path, and the one place I probed hardest for a silent-swallow defect (the
`handoff_done_when_baseline` exemption list) is both correctly scoped and positively tested against
regression in both directions.

All reads below are `git show dd55b357:<path>` or, where noted, on-disk reads that the run
constraints certify are byte-identical to the pin (worktree HEAD `1e3cc982` differs from the pin
only by a `review_sha` bump inside `feature.json`, which none of my reads touch).

## F-11 re-grade — per note

Diff evidence: `git diff dd55b357^ dd55b357 -- notes/handoff-{plan,build,validate}.md`.

### handoff-plan.md — PASS
Old (c4/c5): `## Next` = "re-sign plan.yaml and BRIEF.md" as the ONE next action; `Done when`
authority = `approval:BRIEF.md#Approval` — a heading that was already present and green, so a
successor could stop before re-signing. That was F-11.
New: `## Next` was rewritten so the tracked action is no longer "re-sign" but "execute T-01"
("After the main session re-signs..., execute T-01 as the first build action. Do not continue to
later tasks until T-01's declared verification passes"). `Done when` now reads `Scope: execute and
verify the first unfinished build task` / `Authority: plan-task:T-01.verify`. The Trust section
states T-05 is the only completed build task, so T-01 is unverified at write time — checking the
authority at read time shows unresolved-until-run, not green. The stated Scope and the stated
immediate action in `## Next` now name the same thing (T-01), and the authority cannot be true
before T-01's own verify runs. Semantic test passes.

### handoff-build.md — PASS
Old: `## Next` = "run the validation panel"; `Done when` authority =
`approval:BRIEF.md#Approval` (already-true, same defect class as above).
New: `## Next` was reordered so the FIRST, immediate action is "Run SC-04's exact repository-state
inspection... The state command must exit 0..."; running the full panel is explicitly the SECOND
action, gated on the first passing ("Once that prerequisite passes, run the panel..."). `Done when`
now reads `Scope: establish the clean repository-state prerequisite for validation` / `Authority:
brief-sc:SC-04`. This authority is not a static fact like an approval heading — it is only true
when the literal SC-04 command exits 0, which is exactly the described immediate action, and c5
independently confirmed literal SC-04 was failing (exit 1, INV-29) at the moment this class of note
was being read. It cannot be pre-satisfied by anything other than doing the action. Semantic test
passes.

### handoff-validate.md — PASS (not in c5's F-11 scope; same test applied)
`## Next` = "Have the BUG-1157 owner... reconcile the standing checkout... so the exact
repository-root state command exits 0. Then commit the already-applied F-11 handoff corrections,
re-pin, and rerun the complete four-reader panel." `Done when`: `Scope: restore the literal SC-04
repository state gate` / two ANDed authorities: `brief-sc:SC-04` and
`finding:.../review-harness-code-reviewer-c5.md#F-04`. Both bound the same immediate action
(reconciling BUG-1157 so SC-04 exits 0) and both were open at write time — SC-04 was failing and F-04
was an open must-fix in the cited c5 note, not a closed one. Neither authority was already
satisfied. Semantic test passes.

## Resolver run (separate question: shape/grammar/pointer-existence, NOT the semantic test)

Ran the shipped module directly — `problems(rel_path, text, root, resolve=True)` — against the
pinned bytes of all three notes, `root` = worktree (targets referenced — `plan.yaml`, `BRIEF.md`,
`notes/review-harness-code-reviewer-c5.md` — are none of them `feature.json`, so this reads the
same bytes the pin has):

```
handoff-plan.md:     problems: [] (resolved clean)
handoff-build.md:    problems: [] (resolved clean)
handoff-validate.md: problems: [] (resolved clean)
```

This answers "does every pointer syntactically resolve to a real target" — it does, for all three.
It answers nothing about whether the cited target was already true before the action started; that
is the semantic question graded above by hand, per this dispatch's instruction that a green resolver
is not a pass on F-11.

## SC-07 — PASS
`check-domain.sh:1562` — `import handoff_done_when` (single import, inside the `RE_HANDOFF.match`
branch). Call site `check-domain.sh:1563` — `problems.extend(handoff_done_when.problems(rel,
content, root, resolve=True))`, exactly once.
`check-state.sh:54` — `import handoff_done_when` (module-level, wrapped in try/except that sets
`handoff_done_when = None` on failure). Call site `check-state.sh:1251` — exactly one
`handoff_done_when.problems(_rel_handoff, _text, root, resolve=False)`.
`grep -n "Scope:\|Authority:\|plan-task:\|brief-sc:\|LEGAL_PREFIXES"` over both scripts returns zero
matches in either file — no second block parser, no second pointer-grammar or resolution logic
anywhere else in either gate.

## SC-08 — PASS
`templates/HANDOFF.md` (pinned): "Five sections, all required... Done when describes the ONE
immediate action in Next..." — five, not four.
`SKILL.md:311` (pinned): "Five sections, ~60 lines, shape-gated at write: `## Next`... `## Trust`...
`## Dead ends`... `## Working set` and `## Done when`" — five, all five named.
`DECISIONS.md:3701,3723,6698` and `DECISIONS-INDEX.md:163,214` (pinned): all say "five sections" /
"fifth required handoff section."
`check-domain.sh:1554` (pinned): `required = ["## Next", "## Trust", "## Dead ends", "## Working
set", "## Done when"]`, and its refusal message at :1558 reads "the five sections are the contract."
`check-state.sh:1069-1070` (pinned): `HANDOFF_SECTIONS` lists all five; `HANDOFF_NARRATIVE_HEADINGS
= HANDOFF_SECTIONS[:4]` is NOT a contract assertion — it is an internal subset used only to separate
the free-text sections (checked for non-empty body, INV-17) from the machine-checked `## Done when`
block (checked via the imported resolver). The `## done when` heading is checked separately and
additionally at :1211-1212, so the live contract enforced by this script is still five sections, and
no comment or message anywhere in it states "four" as the current requirement.
The two BRIEF-named exempt lines (FEAT-31 74-note migration measurement at cf51dce, and the INV-17
empty-body narrative) are present, byte-identical, and both name a past sha/feature-id while
reporting what was observed then — correctly untouched per PRINCIPLES rule 15.
No other "four section(s)" contract claim found in any of the four named surfaces.

## SC-11 — PASS
Run from `/Users/molchairuangutai/GitHub/harness` (repository root, not the worktree), per the
BRIEF's literal two-arm check:
```
BASE=$(git merge-base main dd55b3570c6a20f5ca1da016d6959752bd0ffc74)   # = 0ec44965a961d19177de871c3bb1f02b701e646b
```
- Diff arm (4 lines): `FEAT-51-.../notes/handoff-validate.md`, `FEAT-54-.../handoff-build.md`,
  `FEAT-54-.../handoff-plan.md`, `FEAT-54-.../handoff-validate.md`.
- Base arm: 141 lines.
- PRIMARY `comm -12 <(diff) <(base)`: **empty** — no historical note was rewritten.
- CONTROL `comm -23 <(diff) <(base)`: **4 lines**, set-for-set identical to
  `git diff --diff-filter=A --name-only $BASE $SHA -- '.../notes/handoff-*.md' | sort` (verified by
  direct comparison, same 4 paths). Control is non-empty and correctly shaped — not a diff-arm
  failure.

## Stage 2 — code quality (first run for this feature, any SHA)

**Risk grade** (`code-grade.py --base $(git merge-base origin/main dd55b357) --head dd55b357`,
`env -u HARNESS_AGENT_TYPE`): **90 FUNCTION records, 90 PASS, 0 FAIL, 0 SEVERITY lines.**
`PASSING: 90` — matches c5's own earlier measurement exactly, at a now-committed pin.

**Fail-open hunt**, focused on `handoff_done_when.py` (288 new lines, primary subject) and the two
gate-script hunks this feature actually touched:
- Every resolver (`_resolve_plan`, `_resolve_brief`, `_resolve_finding`, `_resolve_approval`) fails
  CLOSED on read/parse error — returns an unresolved-problem string, never silently "resolved."
  `_resolution_problems` wraps the whole dispatch in `except Exception` and converts ANY resolver
  crash into a reported problem ("resolver failed closed (...)"), never a swallow.
- Both gate scripts fail closed on import failure: `check-state.sh:54-56` sets
  `handoff_done_when = None` and later (`:1245-1248`) turns that into a reported violation rather
  than skipping the check; `check-domain.sh:1561-1565` wraps the import+call in try/except and
  turns any failure into "REFUSING the write."
- `check-domain.sh`'s Edit-path widening (this feature adds `RE_HANDOFF.match(target)` to the set of
  identities reconstructed and shape-checked pre-write) also FIXES a real prior fail-open in the
  same hunk: `open(..., errors="replace")` silently mangled non-UTF-8 disk content into a
  reconstructed candidate that could then pass shape checks against corrupted bytes; the diff
  changes this to `except UnicodeError: return _UNREADABLE_EDIT`, and the caller turns that sentinel
  into `sys.exit(2)` with an explicit "cannot be reconstructed safely" message before any write.
  This is tested, not just inspected: `tests/integration/test-check-domain.py` case "handoff pre-Edit
  unreadable existing file fails closed" asserts exit 2, the exact message substring, AND that file
  bytes are unchanged (`before == after`) — proof the block happens before the mutation (my
  Expertise P-02: exit-before-write turns a miss into a clean skip, not corruption).
- `_read_target`'s stat-then-open size check has a benign TOCTOU window (file could grow between
  `stat()` and `open().read()`), but this operates over trusted repository-local files at
  write/review time, not adversarial concurrent input — not rated as a finding.
- Targeted probe: `handoff_done_when_baseline` (the REQ-07 exemption list) is the mechanism most
  structurally capable of a silent fail-open — a wrongly-scoped baseline would let a genuinely new,
  contract-noncompliant note through forever. Measured directly: the pinned `harness.json`'s
  141-entry `handoff_done_when_baseline` is EXACTLY set-equal to the SC-11 base-arm (`comm -3`
  between the two, sorted, is empty) — it contains all and only the notes that existed at
  `merge-base(main, review_sha)`, and explicitly does not contain any of the four notes this
  feature or FEAT-51 added. `test-check-state.py` (`_feat54_baseline_cases`) independently pins
  both failure directions: "absent baseline key means no exemption" (fail-closed default) and
  "baselined malformed block reports" (the exemption only ever waives the missing-section case, not
  shape/grammar once a `## Done when` exists) — so a baseline entry cannot be used to launder a
  malformed block.
- No bare `except:` / silent `except Exception: pass` was introduced by this feature's diff hunks in
  either gate script; the pre-existing ones in both files sit well outside the touched line ranges
  (verified by line-number comparison against `git diff --stat`/hunk ranges).

No must-fix found in Stage 2.

## Findings carried, not re-opened
F-01–F-10 and SEC-F-10: closed in c5 with evidence; no new contrary evidence observed at this pin.
SEC-F-08 (med, advisory): unchanged, not this reader's lane.

## Out of scope for this run
Literal SC-04/F-04 (repository-state gate exit code) — not in this dispatch's assignment; owned by
QA/UI this cycle per the roster. PM goal-check and SC-10 UAT explicitly not run.

```yaml
VERDICT: PASS
DIGEST:
  headline: "F-11 closed in all three real handoff notes at a committed SHA; SC-07/08/11 verified PASS at the pin; Stage 2 ran for the first time and found nothing gating (90/90 risk-grade pass, no fail-open)."
  severity_max: none
  findings: 0
  must_fix: []
  spec_violations: []
  reviewed: "0ec44965a961d19177de871c3bb1f02b701e646b..dd55b3570c6a20f5ca1da016d6959752bd0ffc74"
  human_commits_in_scope: [dd55b3570c6a20f5ca1da016d6959752bd0ffc74]
  code_grade: pass
  code_grade_passing: 90
  sc_status:
    - id: F-11-handoff-plan
      verdict: PASS
      evidence: "notes/handoff-plan.md Done when Authority now plan-task:T-01.verify, unresolved-until-run at write time; ## Next rewritten so its tracked action is T-01, not the already-current re-signature."
    - id: F-11-handoff-build
      verdict: PASS
      evidence: "notes/handoff-build.md Done when Authority now brief-sc:SC-04, which was failing (exit 1) at write time; ## Next reordered so SC-04 inspection is the stated immediate action."
    - id: F-11-handoff-validate
      verdict: PASS
      evidence: "notes/handoff-validate.md Done when authorities (brief-sc:SC-04 AND finding:...#F-04) both open at write time; not in c5's original F-11 scope but passes the same test."
    - id: SC-07
      verdict: PASS
      evidence: "check-domain.sh:1562/1563 and check-state.sh:54/1251, one import + one call site each; zero Scope:/Authority:/prefix matches elsewhere in either file."
    - id: SC-08
      verdict: PASS
      evidence: "HANDOFF.md, SKILL.md:311, DECISIONS.md:3701/3723/6698, DECISIONS-INDEX.md:163/214, check-domain.sh:1554/1558, check-state.sh:1069-1070/1211-1212 all state five sections; the two BRIEF-named exempt past-measurement comments are present and untouched."
    - id: SC-11
      verdict: PASS
      evidence: "comm -12 empty (primary); comm -23 = 4 lines, set-equal to the diff-filter=A added set, run from repo root with BASE=0ec44965a961d19177de871c3bb1f02b701e646b."
  open_questions: []
  files_touched: []
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-54-handoff-done-when/.harness/harness/features/FEAT-54-handoff-done-when/notes/review-harness-code-reviewer-c6.md
```
