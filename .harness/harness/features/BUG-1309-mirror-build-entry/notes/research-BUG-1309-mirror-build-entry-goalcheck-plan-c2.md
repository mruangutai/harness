# Goal-check — the plan as it NOW stands vs the operator's stated intent — BUG-1309, cycle c2

**Does this plan deliver the operator's stated intent? Yes, with one blocking cross-task
contradiction.** Six of the eight settled bullets are delivered outright, two are partial, none is
missing; no out-of-scope line is crossed; c1's E1 and E2 are both genuinely closed (era skip now in
T-04 `plan.yaml:411-429`, T-05 `:555-570`, T-06 `:669`, T-07 `:791-813`; unpinned repo now records
nothing, D-09 `:93-94`, T-02 `:216-221`). The third amendment-introduced exposure is real and is item
3: the era rule and the retention rule no longer fire on the same condition. Authority is
`/Users/molchairuangutai/GitHub/harness/.harness/notes/grilling-mirror-build-entry-2026-09-06.md`,
re-read at source, not BRIEF.md. This note SUPERSEDES `…-goalcheck-plan-c0.md` and `…-c1.md`.

## 1 — The eight `## Settled` bullets

| # | Bullet (source `:7-14`) | Carried by | Verdict |
|---|---|---|---|
| 1 | Ship = post-merge terminal phase: finalizes merged code, records terminal local state, performs any recorded mirror transition, releases the worktree | T-08 `plan.yaml:897-909`, T-03 ship message `:339-348`, T-09 `:942-943` | delivered |
| 2 | Build entry = the signed-plan transition that starts execution and runs `gh-sync.py open`; never called Ship | T-08 `:889-895` (trigger cell replaces the `ab4d2fdc` phrase) and `:911-919` (SKILL.md new step 1), T-09 | delivered |
| 3 | Build refuses when the required local Build-entry outcome is absent; may proceed after a recorded temporary environmental failure | T-04 `:407-460` | delivered |
| 4 | Enabled sync → `opened` or `recovery-required`; local configuration/contract errors and partial remote writes block Build | T-02 `:196-227`, D-04 `:71-73`, D-09 `:93-94` | delivered |
| 5 | Disabled/unconfigured sync → `not-applicable`, an approved no-mirror mode | T-02 `:213-215`, T-01 `:131-133`, T-05 `:533-534`, T-06 `:668`, T-07 `:787-789` | delivered |
| 6 | `recovery-required` → main session reruns idempotent `open` before merge, and the user's merge action is refused until a normal receipt is recorded | T-05 `:573-575`, T-02 idempotence cases `:260-261`, D-02 `:63-65` | **partial** — the refusal has a disclosed hole: with `gh` down and the merge issued from a checkout whose local branch matches no feature, the merge is ALLOWED (`:576-587`). Deliberate (D-07 `:84-85`, SC-04 `BRIEF.md:110-112`) and correct under DEC-138; recorded here as a scope fact, not a defect |
| 7 | Legacy already-merged enabled-sync → explicit operator-approved recovery, terminal receipt only: milestone plus parent/source issue, never historical task sub-issues | T-03 `:286-332`, D-03 `:67-69`, D-05 `:75-77`, SC-05 | delivered |
| 8 | Legacy recovery while GitHub is unavailable → stays non-terminal and RETAINS its worktree until recovery and Ship succeed | T-03 skip funnel `:334-337`, T-07 `:784-786` (existing SKIP/FAILED gates kept, and they are what retains an era feature) | **partial** — T-07's new receipt-named retention explicitly EXCLUDES the era corpus (`:791-803`, `:854-860`), i.e. exactly the legacy features this bullet is about. Retention for them survives only through the pre-existing `gh-sync: SKIP` / `FAILED` gates. SC-06 (`BRIEF.md:118-120`) says the sweep declines "naming the missing Build-entry receipt" — true only for a NON-era feature, and T-07's case list has no era + outage case |

## 2 — The three `## Out of scope` items (`:21-23`)

| Item | Crossed? | Ground |
|---|---|---|
| (i) Requiring sync for `github.sync: false` or unconfigured GitHub | **no** | `not-applicable` gates nothing (T-01 `:131-133`); T-05 self-gate `:533-534`, T-06 `:668`, T-07 `:787-789` all exit before deciding. D-09's block applies only to a project that set `sync: true` and left `repo` unpinned — an opted-in mirror, not the fenced category, and the collision is disclosed rather than resolved silently (`:94`) |
| (ii) Creating task-level historical mirror records after work completes | **no** | T-03 creates zero sub-issues and leaves `github.issues` as found (`:299-301`, `:363-374`); `recovery_command_for` exists precisely to stop a message sending the operator to a bare `open` (`:718-730`), and three refusal lines forbid the token `open` (`:451-452`, `:563`, `:693-695`) |
| (iii) Changing the user-gated merge policy | **no** | The merge stays the operator's act; the new PreToolUse deny fires only on the LOCAL receipt (`:554-575`), never denies on a failed GitHub read (`:587`), and allows the whole era corpus (`:555-570`). The refusal it does add is bullet 6, which the operator settled |

## 3 — The third amendment-introduced exposure: **found, and blocking**

**The era set is one symbol, but it is no longer one rule.** T-05's era gate fires "before
`build_entry` is read at all" (`:555-556`), so an era feature is merge-ALLOWED whatever its receipt
says. T-07's era gate deliberately "covers the ABSENT key only" (`:811-813`), so an era feature that
RECORDS `recovery-required` is RETAINED. The two conditions differ, and the gap between them is
reachable:

> a feature in `BUILD_ENTRY_ERA_EXEMPT` whose post-T-02 `open` stops on a temporary no-go records
> `recovery-required` → merge-gate ALLOWS the merge (`:555-570`) → `post-merge-sweep.sh` retains the
> worktree (`:804-813`) → `check-state.sh` INV-29 refuses, because a standing worktree whose feature
> reached a terminal state on the default branch is exactly what it reports
> (`check-state.sh:1931-1935`, read at source).

That is the identical INV-29 consequence D-08's `because` (`:89`) says the one era rule exists to
prevent — reintroduced through the value the amendment left uncovered. **BUG-1309 itself is in the
frozen set** (`:715-716`), so this is reachable on this feature's own merge. A second, smaller face of
the same split: T-04's `recovery-required` line tells the operator "the MERGE is refused until
gh-sync.py open records opened" (`:456-458`), which is FALSE for an era feature — T-05 allows it.

**Order check, done and clean:** every `verify:` is passable in the declared `depends_on` order.
T-01[] → T-06 → {T-04, T-05, T-07}; T-02 → T-03 → {T-04, T-07}; T-04..T-08 → T-09; acyclic. T-04
reads `rec["build_entry"]` which T-02 adds, and reaches it transitively through T-03. T-05 reads
`feature.json` directly and needs no T-03 fixture. T-07 fakes gh-sync's output. No task's `verify:`
runs a suite containing a later task's cases.

## 4 — The destination (`:4`)

**(a) Forward: reached.** For a feature created from this change onward the mirror lifecycle cannot be
lost silently — recorded at Build entry (T-02), refused on absence (T-04), merge-denied (T-05),
reported by INV-37 even at a terminal station with all task statuses absent (T-06), worktree kept
(T-07), doctrine renamed (T-08/T-09).

**(b) `FEAT-*` / `BUG-*` symmetry: structurally yes, asserted nowhere.** No task branches on the
prefix: the era set is a prefix-blind glob of `.harness/*/features/*` (T-06 `:710`),
`recovery_command_for` keys on basename and plan.yaml only (`:718-723`), and merge-gate locates a
feature by branch (`:551-553`). **BUG-* is handled by the same task ids as FEAT-* — T-02, T-04, T-05,
T-06, T-07 — and by no separate one.** But no fixture in any case list is staged under a `BUG-*`
directory name, and REQ-01's clause "reads the same way for `FEAT-*` and `BUG-*` flows"
(`BRIEF.md:34-36`) is quantified over by no SC: SC-09 grades the docs, and T-08's intent (`:885-923`)
names neither prefix.

**(c) BRIEF honesty about the legacy corpus: honest.** `BRIEF.md:150-157` names all 17 sync-enabled
directories with no milestone, calls them KNOWINGLY UNRECOVERED, states the guarantee is forward-only
and that each is recovered only by an explicit operator-approved `recover-terminal`. `BRIEF.md:11-17`
now records the measured fact that the late `open` already RAN. The destination sentence "never
silently loses its mirror lifecycle" is therefore forward-only-satisfied, and the BRIEF says so.

## 5 — Signature readiness — every residual

| # | Residual | For signature | The one clause that closes it |
|---|---|---|---|
| R1 | Era split (item 3): merge ALLOWED on an era `recovery-required` while the sweep RETAINS it → INV-29 | **blocking** | In T-07's era gate, extend it from the absent key to `recovery-required` as well — or, equivalently, in T-05 step 5 deny an era feature that RECORDS `recovery-required`. One or the other, not both |
| R2 | T-04's `recovery-required` stderr line asserts the merge is refused; false for an era feature (`:456-458`) | **blocking** (same clause family as R1, one sentence) | Scope that sentence: "…the MERGE is refused unless this feature is era-exempt" |
| R3 | T-06's `verify:` greps `test-check-state.py` stdout for `INV-37` (`:656`) — passes on a `FAIL` line that names the invariant | non-blocking | Read that bed's runner shape and require its per-case ok/PASS line for each named case, as T-02/T-03/T-07 now do |
| R4 | T-05's `verify:` names no case names (`:521`); `tests/integration/test-merge-gate.py` does not exist yet, so SC-04's era half rests on the suite's own accounting | non-blocking | Impose the case-name contract in T-05's intent at the moment the file is written, in T-04's "THE CASE NAMES BELOW ARE A CONTRACT" words |
| R5 | Bullet 8 / SC-06: the receipt-named retention excludes the era corpus, which is the corpus the bullet is about (item 1 row 8) | non-blocking (behaviour preserved by the kept SKIP/FAILED gates) | One clause in SC-06 saying the retention it grades is the non-era case and that legacy retention rests on the existing `gh-sync: SKIP`/`FAILED` gates |
| R6 | REQ-01's FEAT-*/BUG-* symmetry clause is asserted by no SC and no fixture (item 4b) | non-blocking | One clause in T-04's or T-05's case list staging one era/non-era fixture pair under a `BUG-*` directory name |
| R7 | T-04's era case says "add one such name to the fixture set the test controls" (`:490-491`); the set is a frozen literal in `feature_schema.py`, so the test controls nothing | non-blocking | Strike that alternative: stage the fixture under a name that IS in the frozen set, as T-05 `:622` and T-07 `:855` already say |
| R8 | merge-gate fail-open: `gh` down + local branch matching no feature allows a merge a receipt is owed for (`:576-587`) | non-blocking — **accepted by design**, D-07 `:84-85`, DEC-138 | None owed. If the operator wants it closed it is a change to the out-of-scope merge-policy line, i.e. theirs |

## Not graded here

`check-plan-routes.py` (exit 0, three declared DEC-174 deviations), the absence of a bare `&& exit 1`,
the four `BUILD_ENTRY_ERA_EXEMPT` references and SC-01/03/04's restated halves were MEASURED by the
orchestrator on this plan and were not re-derived. `plan.yaml` and `BRIEF.md` were not written by this
run; nothing was approved; HEAD was not moved.
