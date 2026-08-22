# STATE — FEAT-32-concurrent-write-merge

## Current

Phase: **ship mission, build phase. THE USER GATE IS DISCHARGED — the operator ruled on all three
items. HANDED OFF at 428,899 context tokens against a 200,000 threshold; see `notes/handoff-build.md`.**
`status: Building`. Signatures `approved` /
`operator` / `2026-08-22` (`plan.yaml:4-7`, `BRIEF.md:431-435`). Mirror: milestone **21**, parent
**#700**, sub-issues **#701-717**.

**SIX OF MY EIGHT TASKS ARE DONE AND I VERIFIED EVERY ONE MYSELF.** T-02, T-03, T-04, T-05 (`build-eng`,
3 send-backs) and T-06, T-10 (`t06t10-eng`, **0** send-backs). Every `verify:` exits 0, run by me at
final bytes: T-02 18/18, T-03, T-04, T-05, T-06 55/55, T-10 (161s). Main-session lane done: T-01, T-07,
T-15, T-16. Issues #701-#707, #710, #715, #716 closed.
**REMAINING, both blocked:** T-13 (needs the operator's Q1 **and** main-session T-08/T-09), T-17 (needs
T-13). Main-session lane still open: T-08, T-09, T-11, T-12, T-14.

**I AUDITED ALL SIX RED PROOFS RATHER THAN TRUSTING EXIT CODES.** Each mutant imports cleanly, then
fails a proportionate NAMED subset — the signature of a real discriminator; all-or-nothing failure
would mean a mutant that died on import. `USE_FLOCK`(T-02) 2/18 both case4 · `UNION_MERGE`(T-03) 59/110
· `PRESERVE_BASE_BYTES` 22/110 · `APPROVAL_REFUSAL` 10/110 · `UNION_MERGE`(T-04) 6/33 cases 2/5/6/7/8 ·
`USE_FLOCK`(T-05) 2/38 case10 only. The lead's reporting matched mine everywhere except T-05, where it
said 1 and the true count is 2.

**NO ASSERTION WAS WEAKENED.** The only deletions are T-05's three sanctioned `.lock`-absence checks,
vacuous-or-red under a lock never removed. Measured: `test-expertise-merge.py` 344 lines / 30 `check()`
/ 3 lock assertions to 409 / **32** / **0** — three removed, five ADDED.

**SC-11 IS MET FOR ALL FOUR CONSUMERS** — `plan-merge.py`, `observations-merge.py`,
`expertise-merge.py`, `inflight_registry.py` each import the core and carry **zero** own
`fcntl.flock`/`O_EXCL`/`os.replace`.

**THE RUNNER WAS DOWN AND T-10 RESTORED IT.** It had been exiting **2 with ZERO tests** — the drift
detector is a hard precondition. Now `--check-kinds` exits 0: *"the script arrays and
test_kinds.integration.detect agree"*, and that cross-check ran for the FIRST time ever.
`test-run-unit-tests-kinds.py` is back to **23/23** from 15/23.

**SC-14 IS MET, measured with the restored runner.** unit exit 0, **187** lines matching
`^PASS |^FAIL |ERROR` (baseline 179), **0** beginning `FAIL`, **0** containing `ERROR`. integration exit
0, **470** lines (baseline 221), **0** beginning `FAIL`, **3** containing `ERROR` — unchanged, and the
plan predicted exactly those 3. Neither count is below baseline; every new test file is registered.

**I RATIFIED ONE DEVIATION FROM THE APPROVED PLAN, on a measurement.** T-10's intent orders SEVEN paths
appended to `test_kinds.integration.detect`, asserting `test-validate-digest.py` and
`test-check-domain.py` are ABSENT. **They were already PRESENT at HEAD** — DEC-197's own fix landed
after `62f861c`. I verified all seven are now present with **count 1 each**, no duplicates. Appending
them would have duplicated entries in a file the intent says to change in no other way. Five were
appended; the goal is met exactly. **T-10's intent text now teaches a false measurement** — plan prose,
so correcting it is pm's, and it is a backlog row, not a blocker.

**A DEFECT RISK CONFIRMED WITH A CONTROL; pm judged it BACKLOG, needs_signature, fixed OUTSIDE this
feature.** `plan-merge.py:37` imports `yaml` plainly (its intent demands "import it plainly") while
`harness_yaml.py` raises `DuplicateKeyError`. stdlib `safe_load` ACCEPTS a repeated key and keeps the
last; `harness_yaml.load_str` REJECTS; the same doc without the duplicate is accepted by BOTH — the
control. So `plan-merge.py` can splice a `plan.yaml` the toolchain then refuses to read, failing LOUD.
pm's rejected reading, worth keeping: *permission is not compulsion* — a guard added alongside
contradicts nothing, and that is exactly why it is not already signed. What the signed text leaves open
is whether the BASE file gets strict-parsed too, which would refuse plans already on disk.
**SC-11 PASSES WHILE READING FALSE:** its enumeration is "lock or replace primitive" and a YAML loader
is neither, but its lead sentence "There is one implementation" now misleads.

**A SENTENCE IN SHIPPED CODE IS NOW FALSE AND NOTHING DETECTS IT.** `harness_yaml.py:6-7` states
"Every other module in this tree that needs YAML imports THIS module, never `yaml` directly." Verified
by me: the only direct `import yaml` outside `test-*.py` is that module's own `:18` and
`plan-merge.py:37`. True before T-03, false after. No SC reaches it; there is no propagation checker
(DEC-188). One sentence, in a file no task owns.

**#551 FIRED AGAIN DURING ITS OWN FIX — the count is MOVING and that is the point.** pm measured
**eight**. The `yamlgap-product` lead was then force-closed with pm in flight and the validator DEMANDED
a verdict for an unobservable child (its Q5 calls that nine). The `t06t10-eng` lead reports the stop
hook pressing it the same way and says it held. **Recommendation: do NOT freeze an integer in an
authority file with no propagation checker** — record "eight measured as of <sha>, and the mechanism
fired again during this feature's own build."

**TWO FINDINGS THAT LAND ON THE MAIN SESSION'S T-08/T-09, raised at architecture review.** (1)
`claim()` FAILS CLOSED on lock contention: `inflight_registry.py:104` does not catch `MergeRefusal`, so a
10s lock timeout propagates out of `claim()`; in a `PreToolUse` hook a nonzero exit BLOCKS the dispatch,
while **D-07 states the opposite posture**. T-06 satisfies its spec, so this is the hook cutover's
problem. (2) `agent_type` was ABSENT on T-01's capture because it came from the main session, so the
DISPATCHER key on a governed spawn is **unconfirmed** — T-08/T-09 must derive or capture it, never assume.

**ONE COMMIT BEHIND MAIN AND I CANNOT FIX IT.** `12c66b3` (PR #719). `merge` is in `HEAD_MOVERS`
(`bash-write-guard.sh:144`), refused for every governed agent, so **the merge is the main session's
act**. No run is in flight now, so the window is open.

`cycles_used` **3** of 10 — all three from segment A. Runs **11** of 20.

## Open Questions

- Q1 **DISCHARGED — the operator ruled on all three, no signature is outstanding.** (a) The #551 count
  becomes hedged wording in the PLAN ONLY, not a bare integer, and must say the mechanism fired again
  during this feature's own build; `BRIEF.md:16` STAYS at seven and the disagreement is deliberate, to be
  stated as such in the plan. (b) `.harness/**/*.lock` APPROVED and landed by the main session at
  `.gitignore:46` — verified by me: all five lock paths ignored, `plan.yaml` itself correctly not. (c) The
  YAML split recorded as a limitation and the false sentence fixed at `harness_yaml.py:5-6`; the code fix is an approved follow-up OUTSIDE FEAT-32, filed by the main session. Run `ruling-product` applied (a) and (c) and returned **PASS**, 0 send-backs, recorded. **The new SC-13 statement is its SIXTH, not its seventh** — SC-13 held FIVE clauses, so its own trailing "four of the six" was ALREADY FALSE at `b013dde`; pm removed those integers rather than correct one, since a corrected integer rots on the next statement added. My "seventh" came from pm's earlier request and I repeated it without enumerating — my own P-05 violation. **Occurrence 9 of #551 occurred DURING that run** and the floor wording absorbed it with no edit, which is the durability property being bought, proven by an event after the wording was written.
- Q2 **NOT blocking, operator's call, a trade already declined once.** `BRIEF.md:16` also reads "seven
  measured occurrences"; amending the BRIEF resets its approval for prose.
- Q3 **NOT blocking.** T-13's `verify:` asserts only token presence, so any count passes; if the intent is amended, bind the count into the verify.
- Q4 **NOT blocking, CARRIED — do not re-raise, do not fix.** SC-14 names **221** as its basis while the
  plan records at `:1448-1464` that the number is not attributable to scripts. It still WORKS as a shrink
  detector, and the measured 470 is far above it. The `ERROR`-lines sub-question is CLOSED by T-10's
  intent: all three carry the word inside a test's own NAME. A goal-check must name this as carried.
- Q5 **NOT blocking, recorded residuals, not work.** The exit-6 LOCKED branch of T-03 case 4, T-04 case
  7 and T-06 case 7 was admitted but taken 0 of 20 trials each, because `LOCK_TIMEOUT_SECONDS = 10.0`
  makes the loser WAIT. Pinned by T-02 case 8 and expertise-merge case 3 — by the SET, not those cases.
- Q6 **NOT blocking, backlog.** `RUNS_AGENT_EXEMPT` was hand-fixed for two features; the suite asserts
  the map's MECHANISM, never its COVERAGE — exactly why two features went missing. Also pre-existing and
  NOT mine: `check-state.sh`'s one violation is FEAT-26's unapproved BRIEF.
- Q7 **NOT blocking, ANSWERED.** No `DECISIONS-INDEX.md` row governs what re-opens a signature. pm: it
  deserves an entry as FOLLOW-UP, not folded into T-13, which would smuggle a governance rule in.
- Q8 **NOT blocking, the main session's act; an agent composing a GitHub post is forbidden** (DEC-138
  am.6). #551's record needs updating once Q1 settles, plus a backlog row against run-dir minting.
- Q10 **NOT blocking, backlog, WIDER THAN THIS REPO.** `templates/gitignore.snippet` installs into every
  repo the factory touches, has 8 rules and no lock rule. Separate pre-existing drift: its `:7` reads
  `.harness/features/*/runs/**`, missing the `<repo>` segment the multi-repo migration added.
- Q11 **NOT blocking, a HARNESS DEFECT hit live by two leads this run.** The `SubagentStop` digest
  contract has no in-progress value, so a lead hosting an async member cannot idle — ending a turn is a
  contract violation and the only satisfying returns are terminal verdicts it has not earned. I hit the
  same wall myself. `validate-digest.py:845` means a second identical return SHIPS.
