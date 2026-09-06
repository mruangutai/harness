## VERDICT: PASS (no must_fix; severity_max = med, all pre-existing/carried)

BLUF: All five c8 fix rulings HOLD at source, on all three routes where per-route. The four
operator-accepted surfaces are unchanged. The 5(d) sequencing worry is real-looking but resolves
safe: no task verify or gate invokes the standing unit suite between T-01 and T-12, and qa_gate
fires only after the whole eng segment (T-12 included) per `harness/SKILL.md`'s documented
segment order — a process-discipline dependency, not a plan defect, and it fails loud if violated.
One carried finding (PF-e74a2da…, med) still reproduces unchanged. Two new low findings found:
a stale "seven purposes" caption in `github-mirror.md` that T-12 never updates and no gate checks,
and a grep-proxy pin-guard verify (T-01) that cannot mechanically enforce the three-separate-
failures design it correctly specifies in prose.

## A. Discharge roll-call

1. **Backfill-only-refusal case, all three routes — HOLDING.** Verified independently (not on
   c8's word): T-03 `for c in A B C D E F G H H2 I J K` includes `K`; case K text `"K. THE
   BACKFILL IS THE SOLE SOURCE OF A MISSING TYPE"`, `FAKE_TYPES=nobug`, uses `feature.json`
   (this route's own shape) with `github.issues`/`github.typed[...] = "created"`, asserts
   non-zero exit, `"Bug"`+`"github.issue_types"` in combined output, zero `issue create`, zero
   `updateIssue` (incl. none derived from 502), remnant unchanged. T-05 `for c in A B C D E F G H`
   includes `H`; case H uses `backlog-issues.json` (this route's own shape: `typed: false`, not
   the string `"created"`) recording `"bug:a defect"` #602, same five assertions. T-07
   `for c in A B C D E F G H I J` includes `J`; case J uses `factory.yaml` `typed` = `"created"`
   (this route's own shape) for task #703, explicitly asserts `"THE PARENT'S CREATE INCLUDED"`.
   All three fixtures match their route's real recorded shape; none is inert (each states "EVERY
   ISSUE THIS RUN WOULD CREATE HAS A DECLARED TYPE" / equivalent, isolating the backfill as sole
   cause). `nobug` literal is in all three required-string loops.

2. **D-14 overclaim — HOLDING, and swept plan-wide.** D-14 `because`: `"A GraphQL createIssue
   with issueTypeId IS possible … and it is DELIBERATELY UNUSED"` — confirmed. Grepped the whole
   1665-line file for every re-derivable phrasing of the old overclaim
   (`cannot set a native type|cannot carry.*type|so the type can only be applied after|impossible
   to (set|carry)`): the only three hits are (i) D-14 itself, now fixed and correctly scoped
   ("the gh CLI's own create cannot carry a type" — a true, narrow claim, immediately paired with
   the GraphQL-possible sentence); (ii) T-02's send-back-amended intent, now reading `"issueTypeId
   is a measured input field of BOTH CreateIssueInput and UpdateIssueInput, so a create CAN carry
   the type; this plan deliberately does not use it"`; (iii) the historical finding-summary text
   inside `panel.findings` quoting the OLD wording as a record of what was fixed (expected, inert
   prose). T-08's factory_gh.py note ("type is applied after the create because gh 2.92.0 has no
   --type flag on issue create") is correctly scoped to the CLI path and never claims total
   impossibility. No survivor found anywhere else.

3. **T-06 gated integration test — HOLDING.** Verify line 2: `python3
   tests/integration/test-gh-issue-types.py || exit 1`. Intent: `"BOTH ARE IN YOUR VERIFY, which
   runs test-gh-issue-types.py itself … Do not rely on running it by hand."`

4. **T-10 §6 SKIP wording — HOLDING.** One `query_failed` bullet: `"THAT ONE WORDING COVERS EVERY
   NON-ANSWER, and there is no second one: an authorisation error, a NOT_FOUND, and gh being
   unable to reach the TARGET's host at all … ALL classify query_failed"`. Grepped for `"SKIP gh
   cannot reach"` — zero hits, confirmed gone. §7 unchanged: `"exactly one of LIVE PASS,
   CAPABILITY PRESENT, CAPABILITY ABSENT or SKIP … add no fifth token"` — grepped, no fifth token
   anywhere.

5. **The coupled pin split — HOLDING, graded on all four sub-points, independently measured:**
   - (a) D-08 `choice`/`because` read in full: both describe exactly the narrowed three-item row
     (capability query, node-id read, probe read-back) and explicitly place
     `gh_issues.internal_id_args` outside the pin as one unpinned `DECISIONS.md` sentence. No
     residual reference to the old eight-hundred-plus-char scope.
   - (b) Ran `re.findall(r'whether a target repository supports native Issue Types.*?explicit
     create opt-in', plan_text)` myself: 3 hits — T-11 §3 (394 chars) and T-12 §1 (394 chars) are
     byte-**identical** (`matches[0]==matches[2]` → `True`); the third hit is the 80-char regex
     literal quoted in T-01's own intent prose, exactly as claimed. T-11's verify greps
     (`"which native issue types a repository declares"`, `"the native type assigned to an issue
     Harness created"`, `"EIGHT purposes"`) are all substrings of the confirmed 394-char text or
     of the literal heading rewrite T-11 §3 instructs (`"SEVEN"→"EIGHT purposes"`, confirmed by
     grep against DEC-203's *current* heading text at :6064, which reads
     `"carried forward and now SEVEN purposes"` — a mechanical word swap produces the literal
     grep target).
   - (c) T-01 §13 intent literally specifies the three-separate-failures design (`"MISSING PIN …
     same report … DRIFTED PIN with both strings … A single comparison … is NOT enough"`) — the
     **design is correct as specified**. See low finding below: the mechanical verify gate for
     this task can only proxy-check for the substring `"DRIFTED"`, not the actual three-way
     behavior.
   - (d) **Sequencing — answered, evidence below.**

## The 5(d) sequencing question

**Found: no task verify between T-01 and T-12 invokes the standing unit suite**, and there is
no top-level `gates:` key in `plan.yaml` (grepped `^gates:` — zero hits; the `gates.qa_gate:
blocking` cited in the dispatch lives in `.harness/harness.json:351-355`, a repo-level config, not
a plan-level gate). Every task's own `verify:` names specific files
(`tests/unit/test-issue-types.py`, `tests/integration/test-gh-issue-types.py`, etc.); none globs
`tests/unit/test-*.py` or shells out to `run-unit-tests.sh`. `run-unit-tests.sh`'s `unit` kind
globs `tests/unit/test-*.py` (confirmed by reading the script), which would pick up
`test-issue-types-pin.py` and fail red — but the only caller of that full-suite path is the
project's `qa_gate`, documented in `.agents/skills/harness/SKILL.md:145-148` as **segment 2 of
the build phase, run only after "the eng segment"** (segment 1, "A build team is single-squad by
construction (DEC-118)"). T-12 is `main-session-direct` (DEC-174 carve-out), executed by the
orchestrator itself rather than the build squad, but nothing in the plan or in `SKILL.md` states
that a main-session-direct task is deferred to *after* qa_gate — the segment-order text treats
"the eng segment" as covering all planned work regardless of executor. **This is a real gap, but
it is a process-discipline dependency on the orchestrator, not a plan-encoded or tool-encoded
guarantee**, and if violated it fails LOUD (qa_gate is `blocking`; a premature run would redden the
whole suite, not silently pass). No task's `verify:`, no `gates:` block, and no config I read
claims otherwise or papers over it. I found nothing — in the plan, in `run-unit-tests.sh`, or in
`.harness/harness.json` — that would make this fail *silently*.

## B. Four accepted surfaces — unchanged

All four `disposition:` strings read `operator_accepted` (`PF-56a2ce7a…`, `PF-0c12a033…`,
`PF-e27f1c30…`, `PF-d8a7b516…`), confirmed by direct read of `panel.findings`. Surfaces:
`adopted` marker intact at D-10, D-20, T-04 §7 (`rec["typed"]["parent"] = "adopted"`), T-08 §8
(`factory["typed"]["parent"] = "adopted"`). T-05 case F's tripwire intact verbatim: `"Assert the
second run makes three MORE 'issue create' argv - today's duplicate behaviour"`. T-10 §6 residue
intact verbatim: `"resolve the type a real create would use - gh_issue_types.type_for_parent
(overrides) read from the same harness.json - and if gh_issue_types.missing_types names it,
print … SKIP … and exit 0 WITHOUT creating"`. None silently tidied.

## C. New findings this cycle

- reader: scope · severity: **low** · summary: `github-mirror.md`'s caption still claims "seven
  purposes" after T-12 adds an eighth row, and nothing checks it.
  why: T-11's parallel edit to `DECISIONS.md` is explicitly told to rewrite `"carried forward and
  now SEVEN purposes"` → `"EIGHT purposes"` and T-11's verify greps for the literal `"EIGHT
  purposes"`. T-12's intent (§1–§3) never touches `github-mirror.md`'s line 7 caption ("bounded to
  an enumerated set — seven purposes") and T-12's verify (three checks: `github.issue_types`
  substring, the pin-guard test, the two-file identity script) never greps for an updated count.
  A faithful builder ships a table with 8 rows under a caption that still says 7 — a future
  reader auditing this reference file for how many bounded read-back purposes exist gets the
  wrong count from prose that contradicts its own table, and no gate catches it.
  anchor: `github-mirror.md:7` (`"seven purposes"`, unmatched by any T-12 §1–§3 instruction or
  verify check); `plan.yaml` T-12 `verify:`/`intent:` (no mention of the caption).

- reader: scope · severity: **low** · summary: T-01's pin-guard verify can only prove the
  substring `"DRIFTED"` exists in the test file, not that missing-pin and drifted-pin are
  actually two independently-triggerable failures.
  why: T-01 §13 correctly specifies three separate assertions (missing-in-DECISIONS.md,
  missing-in-github-mirror.md, then equality), explicitly warning `"A single comparison … is NOT
  enough … two absent values compare equal."` But the mechanical gate
  (`grep -qF "DRIFTED" tests/unit/test-issue-types-pin.py`) is satisfied by any implementation
  that merely prints a string containing "DRIFTED" somewhere — including a naive
  `if a != b: print("DRIFTED…")` that treats two `None` extractions as equal and silently
  passes on exactly the state the guard exists to catch. Same defect class already recorded and
  accepted-in-scope as `PF-e74a2da89380cfa94f6b1693191d759d` (grep-loop verify buys gate parity,
  not behavioral coverage), just at a new site (T-01's pin guard rather than T-03/05/07's case
  loops); not re-ranking that disposition, flagging the new location for the record.
  anchor: `plan.yaml` T-01 `verify:` (`grep -qF "DRIFTED"` line) vs. T-01 `intent:` §13's
  three-separate-failures prose.

No orphan/undefined REQ traces found (REQ-01…11 each traced by ≥1 task); `depends_on` forms a
valid DAG (T-01→T-02→{T-03,T-05,T-07}→…→T-12, no cycle); every task's case-letter `for c in` loop
matches its intent's declared case letters exactly (T-03: 12/12, T-05: 8/8, T-07: 10/10); every
task's required-string loop is satisfiable by its own intent text (spot-checked all three
integration tasks plus T-01's unit-test loop). No fixture's recorded-shape claim contradicts its
route's real receipt shape (checked against D-13/T-06 for backlog's `typed: bool`, D-20/T-04 for
gh-sync's three-state string, T-08 §8 for factory's three-state string).

## D. Carry-forward from cycle-4 `panel.findings`

Of 11 entries: 4 confirmed `operator_accepted` (§B, unre-litigated), 6 ids confirmed HOLDING and
DROPPED (§A: `PF-1f968f2cd73a799708e4be589d48e61b`, `PF-e02dcbdf60fdf5eede40feb6066e8a08`,
`PF-452948136bf467869d223e027191ae49`, `PF-62b2b8ae0acc3509b474b744469137dc`,
`PF-383a1a92195cf2cdfba9828bda854195`, `PF-9a71cb9a0c590b06b890ff1517b80385` — note this is six
ids across the five rulings, ruling 5 covers two; the dispatch's "five ids" appears to count
rulings, not ids — dropped all six since all re-verified HOLDING).

- **`PF-e74a2da89380cfa94f6b1693191d759d`(med) — RE-DERIVED AT SOURCE, carried verbatim.** T-03's
  `for s in … nobug github.issue_types` loop (plan.yaml, T-03 `verify:`) is still file-global
  `grep -qF`, unscoped to any case marker — confirmed by reading the loop itself, not assumed.
  It now also covers the newly-added `nobug` literal and case-K marker the same way it covered
  everything before: gate parity, not coverage. The disposition recorded against it
  (`batched_to_signature_review`, not re-ranked, not re-scoped) already states this is accepted
  scope of a ruled remedy, not a new defect — carrying forward per instruction, not re-arguing it.

## DIGEST

```yaml
VERDICT: PASS
DIGEST:
  headline: All five c8 rulings hold per-route at source; four accepted surfaces intact; one carried
    med finding re-derives unchanged; two new low findings (stale purposes-count caption, grep-proxy
    pin guard); 5(d) sequencing risk is real but process-level and fails loud, not silent.
  severity_max: med
  findings: 4
  must_fix: []
  spec_violations: []
  reviewed: "n/a (plan-panel cycle, no code, no review_sha — DEC-207/BUG-1080)"
  human_commits_in_scope: []
  open_questions:
    - { id: Q1, question: "Does the orchestrator's build-loop tooling guarantee a main-session-direct
        task (T-12) lands before qa_gate is dispatched, or is this purely operator/orchestrator
        discipline? If purely discipline, is a note worth adding to the harness build-loop SKILL so
        future signature-imminent plans with a similarly red standing-suite file don't rely on
        memory alone?", blocking: false }
  files_touched: ["/Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-55-issue-types-created-work/.harness/harness/features/FEAT-55-issue-types-created-work/notes/review-harness-code-reviewer-planpanel-c5.md"]
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-55-issue-types-created-work/.harness/harness/features/FEAT-55-issue-types-created-work/notes/review-harness-code-reviewer-planpanel-c5.md
```
