# STATE — FEAT-32-concurrent-write-merge

## Current

Phase: **ship mission, build phase.** `status: Building`, committed through `4673d0b`. Both
signatures verified `approved` / `operator` / `2026-08-22` (`plan.yaml:4-7`, `BRIEF.md:431-435`).
Mirror: milestone **21**, parent **#700** (`created`), sub-issues **#701-717**.

**THE TWO LANES INTERLEAVE, and that is this feature's sequencing problem.** Nine tasks are
main-session-direct under DEC-174 (T-01, T-07, T-08, T-09, T-11, T-12, T-14, T-15, T-16); eight are
the team's (T-02, T-03, T-04, T-05, T-06, T-10, T-13, T-17). `plan.yaml:9-80` (`lanes:`, resolved at
`c32f332`) is the authority. **Statuses: done** T-01, T-07, T-15, T-16 · **building** T-02, T-03,
T-04, T-05 · **pending** the rest. Issues #701, #707, #715, #716 closed.

**MAIN-SESSION LANE RE-VERIFIED BY ME, not restated.** Both checkouts' `dispatch-guard.sh` are clean
with zero T-01 probe artifacts left behind. T-16's citation is right: line 845 *is*
`if d.get("stop_hook_active"):`. `test-dispatch-guard.py` and `test-validate-digest.py` both PASS when
I run them. DEC-129 at `:2954` is the feature-folder entry with **zero** occurrences of "approval",
DEC-120 at `:2408` is the user channel — so T-15's citation swap is sound.

**T-15 IS RESOLVED AND COST NO SIGNATURE.** Its verify asserted `endswith(" plan.yaml approval:")`
with a leading space against a grant whose character before `plan.yaml` is a **slash** —
unsatisfiable by construction. pm judged it **covered**, on a principle worth keeping: *a correction
to signed text needs no new signature only when the signed artifact itself forces the one right
answer; if it requires choosing among readings the artifact does not settle, it is new.* D-10
(`plan.yaml:1748`) spells the entry with the slash, so two signed statements agree and the verify
contradicts both — a transcription slip. One character dropped at `:2033`, still an `endswith`. **I
ran T-15's full verify myself: exit 0.** T-14 is unblocked.

**SEGMENT A IN FLIGHT** to `harness-eng-lead`: T-02 (`plan.yaml:440-559`), then T-03, T-04, T-05, all
`harness-backend-dev`. `harness_merge.py` (160 lines) and two T-02 receipts (`c1`, `c2` — **one rework
cycle**) are on disk; **nothing is committed or recorded, because the run has not returned.** My read
of the core: `flock` on `O_CREAT` never `O_EXCL`, lock file never removed, `os.replace` from a tempfile
in the same directory, `MergeRefusal` raised as a value rather than `sys.exit`, and
`require_destination` matching the **resolved** realpath rather than the argument — the exact path-form
hazard that would otherwise make the guard decorative. The `#627` identity gap is disclosed, not hidden.

**A GAP NOBODY PLANNED FOR, with pm now judging it.** `harness_merge.py:121` locks `path + ".lock"`
and D-02 makes that file **permanent** by design. Nothing ignores it: `.gitignore` has **no `*.lock`
rule**, `git check-ignore` on an `observations/*.md.lock` returns **NOT IGNORED**, `.harness/expertise/`
is in-repo, and T-11's scope is the single line `.harness/.inflight-claims.json` with "change nothing
else" — so **not even the registry's own `.lock` sibling is covered**, and T-11's verify greps only its
own path, so it can pass green while its lock dirties the tree. **It is NEW behaviour**:
`expertise-merge.py:290` removes its lock today; T-05's rewiring makes it persist. **No test can see
it** — every verify copies `bin/` to a `mktemp -d`. Consequence, in `.gitignore`'s own words twice:
untracked files dirty the tree and "a dirty tree halts the next team run" (SPEC 8.6), and
`feature-worktree.py remove` refuses on a dirty tree.

**#551's COUNT IS EIGHT, NOT SEVEN, AND ONLY THE OPERATOR CAN CORRECT IT.** Occurrence 8 is at
`runs/2026-08-21-2-product/digest.md:28` — an author independent of the `STATE.md` under suspicion —
parked as non-blocking, so it never reached `plan.yaml` or `BRIEF.md`. The plan's seven is **staleness,
not a deliberate hold**. **NEW, not covered**: T-13's intent *enumerates* 5, 6, 7 and pins all three to
`2026-08-21-1-product`, and signed `BRIEF.md:16` reads "seven measured occurrences".

**I CLOSED pm's QUESTION ON IT WITH A MEASUREMENT IT HAD NO TOOL FOR, and it STRENGTHENS the entry.**
Whether the mechanism *demands* a false verdict turns on whether a member `verdict: none` is accepted.
**It is not.** `validate-digest.py:705` ranks members against `{PASS, FAIL, ESCALATE, BLOCKED}`; piping
synthetic lead digests through `validate-digest.py lead` on stdin, `none` and `unknown` are REJECTED
naming that list, while `PASS` and `BLOCKED` are rejected **only** for a missing `branch` field — the
control proving the discriminator is the verdict value, not a broken fixture. Occurrence 8's author
observed the same rejection live, so the claim rests on **two independent evidence classes**.
**Occurrence 9 is RAISED, NOT COUNTED:** `t13-count-product` was force-closed with pm in flight, but pm
completed and the lead returned an honest graded digest, so the harm did not materialise — and this
feature's round-5 precedent is explicit that a force-close followed by a successful resume is not one.

**`--check-kinds` IS RED, EXPECTEDLY.** `test-dispatch-guard.py is not in run-unit-tests.sh's explicit
script list` — T-07 created it, **T-10 registers it**, which is why T-10 lists T-07 in `depends_on`.
Green at `b1281df`; the final commit does not ship red. **SC-14 depends on T-10** doing this: it
requires `test_kinds.integration.detect` to name each new test file by path.

**ONE COMMIT BEHIND MAIN AND I CANNOT FIX IT.** `12c66b3` (PR #719) fixed `RUNS_AGENT_EXEMPT` —
FEAT-32 exempt at **5**, and writes now land (confirmed at index 5 with `agent` present). `merge` is in
`HEAD_MOVERS` (`bash-write-guard.sh:144`), refused for every governed agent, so **the merge is the main
session's act** and must wait until no run is in flight, because a HEAD move re-points every file under
every agent in the tree. Not urgent: both `feature_schema.py` importers in the suite **PASS against the
stale copy**, so being behind is a correctness problem for what ships, not a gate failure.

`cycles_used` **0** of 10 — two product runs, zero send-backs. Runs **7** of 20.

## Open Questions

- Q1 **BLOCKING, THE OPERATOR'S SIGNATURE — gates T-13, which gates T-17.** Amend T-13's intent from
  seven #551 occurrences to eight, supplying occurrence 8's sentence with its own run dir
  (`2026-08-21-2-product`) and its "demands a false verdict" claim, now measured twice over, while
  leaving the `2026-08-21-1-product` pin on 5/6/7. Paying it now costs one amend; paying it at T-13
  time writes seven permanently into an authority with **no propagation checker**.
- Q2 **NOT blocking, operator's call, the same trade already declined once.** `BRIEF.md:16` also reads
  "seven measured occurrences". Amending the BRIEF resets its approval for prose — the trade refused on
  SC-14. Middle path: amend T-13 only, accepting that the BRIEF understates a number the authority
  states correctly.
- Q3 **NOT blocking, pm's observation.** T-13's `verify:` asserts only token presence, so seven and
  eight both pass it. If the intent is amended, consider binding the count into the verify.
- Q4 **NOT blocking, CARRIED — do not re-raise and do not fix.** SC-14 names **221** as its basis while
  the plan records at `:1448-1464` that the number is not attributable to scripts; the operator declined
  to overturn pm's leave-it recommendation. **The criterion still works** — 221 is used as a SHRINK
  DETECTOR ("neither count is BELOW its baseline"), which holds whatever the number is composed of. A
  goal-check tripping on SC-14 must name this as the carried question, never as fresh.
- Q5 **NOT blocking, a SECOND SC-14 question found in an old digest, not a new one.**
  `runs/2026-08-21-2-product/digest.md` Q4 records **3** integration lines *containing* `ERROR` at the
  `62f861c` baseline, which SC-14's "no line *beginning* `FAIL`" test does not catch; left unresolved.
- Q6 **NOT blocking, the durable half of the defect that blocked me.** `RUNS_AGENT_EXEMPT` was fixed by
  hand for two features. The suite asserts the map's MECHANISM, never its COVERAGE:
  `test-validate-feature-json.py:361-399` proves lookups work, `test-check-domain.py:2232` uses `feat not
  in RUNS_AGENT_EXEMPT` as a fixture *precondition*. Nothing asserts the key set matches the corpus —
  exactly why two features went missing. Backlog row.
- Q7 **NOT blocking, pm's question.** `DECISIONS-INDEX.md` carries no row on what re-opens an approval
  signature, so the covered-vs-new principle above lives only in a notes file.
- Q8 **NOT blocking, the main session's act; an agent composing a GitHub post is forbidden** (DEC-138
  am.6). #551's occurrence record needs updating once Q1 settles. Plus a backlog row against run-dir
  minting: a zero-padded seq once sorted before an existing `-1-` id and overwrote a prior round's
  digest. Dirs are NOT renamed — that would erase the evidence. **All dirs minted this phase are
  correct**, though pm once wrote one into the MAIN checkout instead of the worktree; I deleted it.
- Q9 **NOT blocking, pre-existing, NOT mine.** `check-state.sh`'s one violation is FEAT-26's unapproved
  BRIEF — a different flow, standing before this change.
