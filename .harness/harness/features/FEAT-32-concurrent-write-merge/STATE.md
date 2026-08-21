# STATE — FEAT-32-concurrent-write-merge

## Current

Phase: **plan, AT ITS TERMINUS.** Round 5's amend **landed complete and the lead returned PASS** with
zero send-backs, having spot-checked six sites at source itself. `plan.yaml` carries all four items;
`approval.status` is `pending` in `plan.yaml` and `## Approval` is `pending` in `BRIEF.md`, both
verified **byte-identical to HEAD by `diff` against `git show HEAD:`** — `BRIEF.md` is untouched in
full, not merely in its signature. **Nothing here signed anything. The operator signs next.**

**NO #551 OCCURRENCE THIS ROUND — occurrences stand at EIGHT, and I got this wrong twice before
getting it right.** At 16:00 the lead's `runs/2026-08-21-01-product/state.yaml` read `status:
blocked`, step `in_flight`, `completed_at: none`, `note: "host forced to close before the return
landed"`, and its `digest.md` read `VERDICT: BLOCKED`, `members: [{ verdict: none, files_touched: []
}]`. I measured `plan.yaml` byte-identical to HEAD at 16:03:10 and wrote a STATE.md saying the amend
had not landed. Then `plan.yaml` was written at **16:04:32**, pm's artifact at **16:06:05**, and I
rewrote STATE.md claiming pm had been abandoned mid-flight — occurrence 9. **Also wrong.** At
**16:07:47** the lead rewrote `state.yaml` to `status: complete`, step `complete`, `verdict: PASS`,
`completed_at: seq-2`, and at **16:08:23** its digest to `VERDICT: PASS`; it then returned normally.
Round 4's lesson repeats exactly: a mid-run digest is a defensive DRAFT — and this round extends it,
because `state.yaml` is working state too. **I reasoned that two agreeing files ruled out the draft
trap. They do not: both were written by the SAME author about a THIRD party, so their agreement
measures the lead's belief, not pm's state. Independence means a different author, not a second
file.** The only sound completion signals are the harness's own notification and
`state.yaml: complete` after it.

**WHAT LANDED, all four items, verified by me at `1e73248` and independently by the lead.**
- **Q1, the split — FIXED at both sites.** `:1734` now reads "split the entry on the FIRST space -
  `entry.split(" ", 1)`, never rsplit"; `:2035` asserts `split(" ", 1)`. `:1738-1758` carries the
  measurement as the reason. **1 denying entry of 4 versus 3 of 4** — I ran that parse myself before
  dispatching, against the real `main_session.writes` (3 entries at this sha) plus the fourth entry
  T-15 adds. **pm found a consequence I had not measured:** LAST-space splitting also corrupts the
  glob to `…/BRIEF.md ##`, which matches no path on disk, so those two entries were doubly dead, not
  merely fragment-less (`:1753-1754`). The only surviving `rsplit` in the file is the prohibition at
  `:1734`. D-10 `:289-290` states no direction and was correctly left alone — decisions still **10**.
- **Q2, the counter-example — ADDED at `:1795-1812`, immediately below limb B, rule text
  byte-identical to HEAD.** 9 tracked `*/PLAN.md`; 9 `^## Approval` at zero indent, and pm adds that
  the signature's own `status:` sits at zero indent too (10 such lines, the extra being FEAT-06's
  re-signature), making the inversion total; **27** task `status:` at TWO spaces across **5** files
  (FEAT-06 10, FEAT-07 10, FEAT-09 4, FEAT-02 2, template 1). `plan.yaml` runs the other way at the
  same sha: 23 files, indents 2×23 / 4×176 / 10×1. The refusal to hardcode two spaces now has a
  measured inversion behind it instead of a caution.
- **Item 3, Q5 as a STATED LIMITATION — added at `:1448-1464` (T-10), the site that owns the
  baseline.** No assertion, `verify:`, threshold or recorded number changed; the sole changed
  assertion line in the whole diff is `:2035`'s `rsplit`→`split`, confirmed by filtering the diff for
  `assert`. BRIEF.md SC-14 untouched. pm's measurement is finer than the disposition I passed down:
  integration exit 0, **221** lines matching `^PASS |^FAIL |ERROR` (equal to the `62f861c` baseline),
  **218** beginning `PASS `, of which **16** are script-level lines covering **14** distinct scripts —
  `test-feature-worktree.py:867` and `test-expertise-merge.py:338` each print a summary spelled
  exactly like the runner's `echo "PASS $s"` (`run-unit-tests.sh:62`) — and **202** case-level from
  **3** of the 14 (`test-check-plan-routes.py:82` also prints per case). That is pm's measurement,
  attributed: I did not re-run the suite.
- **F-1, a fourth item the LEAD found and pm settled — DRIFT, not error, re-anchored at `:1863-1874`.**
  The paragraph claimed "EXACTLY TWO" other-indent `status:` lines, naming this plan's `:647` at
  ELEVEN spaces. pm measured `^ {11}status:` as **1 at `6bb7d82`** and **0 at `1e73248`** — the line
  reflowed under round 4's amend. My own count at `1e73248` agrees (2sp×1, 4sp×17, no eleven). So the
  operator's "10 and 11 spaces" was TRUE at `6bb7d82` and my "does not reproduce" is true at
  `1e73248`: both correct, different shas, which is precisely the drift-versus-falsification
  distinction the paragraph exists to enable. It now reads **EXACTLY ONE** (`FEAT-14…:1154`, ten
  spaces, prose), anchored to `1e73248`, and says outright that the earlier figure was drift rather
  than quietly swapping the number.

**GATES at `1e73248` with the amend on disk.** `yaml.safe_load` CLEAN; **17** tasks, **10**
decisions — unchanged. `check-plan-routes.py` exit **0**, **0 VIOLATION**, FEAT-32's own deviations
still **6** — enumerated and attributed rather than grepped for the id (P-05): T-01 notes, T-07
`test-dispatch-guard.py`, T-08 `dispatch-guard.sh`, T-09 `validate-digest.py`, T-14
`check-domain.sh`, T-16 `validate-digest.py`; the other 7 of 13 belong to FEAT-29 and earlier
features. `validate-feature-json.py` exit 0. `check-state.sh` exit 1 with FEAT-32's sole VIOLATION
"BRIEF.md is NOT approved" — the terminus, unchanged. `plan.yaml` diff shape **+77 / −16**, and it is
the only artifact file changed by the round. No enforcement-layer file was touched by anyone, so
DEC-174's carve-out holds: this amend plans, it does not execute.

**PROCEDURE THAT WORKED, recorded because round 3's failure was its inverse.** Premise first, then
dispatch. The four-entry parse ran BEFORE the dispatch was written, so the dispatch carried a
measurement rather than a hypothesis and pm spent no cycle re-deriving it. Round 3's ordering error
cost a whole amend round; this ordering cost about five minutes. The lead also wrote its grading
criteria BEFORE the return could land (`runs/2026-08-21-01-product/send-back-criteria.md`), so the
grading was not fitted to the answer — that file is worth reusing.

**THE RUN-ID DEFECT, fourth distinct shape in five rounds, and the lead owns this one by name.** It
minted `2026-08-21-01-product` without enumerating `feature.json`, which already held `-1-`, `-2-`,
`-3-`: the zero-padded seq sorts before `-1-`, and it wrote its artifacts INTO round 4's dir,
**overwriting round 4's digest** (round 4's substance survives only in this file's git history at
`6bb7d82` and `1e73248`). Round 5 is recorded as `2026-08-21-5-product`, the id it should have
minted, so `check-state.sh` notes that dir absent — a truthful pointer at the defect. Dirs are NOT
renamed: renaming now would erase the evidence. Earlier shapes: zero-padding, round 3's digest in
round 2's dir, now dir reuse with data loss. `runs/**` is gitignored (`.gitignore:7`).

`cycles_used` **0** of 10 — no rework: one dispatch, one pm, four items delivered first pass, zero
send-backs reported. Runs **5** of 20.

## Open Questions

- Q1 **BLOCKING — SIGN OR AMEND. This is the terminus.** `plan.yaml` carries the Q1 split fix, the Q2
  counter-example, the Q5 limitation and the F-1 re-anchor; `BRIEF.md` is untouched since the round-4
  signature request (it gained SC-21 then, on top of REQ-11's widening and SC-20, and
  REQ-12/SC-17/SC-18/SC-19 before that, SC-16 withdrawn). Both approvals are `pending` and
  byte-identical. Only the main session writes either signature.
- Q2 **NOT blocking — pm's own question, and it is a BRIEF edit with an approval reset, so the
  operator's call alone.** SC-14 still states 221 as its comparison basis, so the criterion reads as
  if the number were attributable to scripts while the plan now records that it is not. Leaving it is
  defensible: the limitation sits at the site that owns the baseline, and the mechanical gate (exit 0,
  no `^FAIL`, the per-file `^PASS` assertions) is untouched by the duplication. Changing SC-14 would
  reset an approval for prose.
- Q3 **NOT blocking, main session's act.** #551 needs occurrences **7 and 8** — **not 9**; this round
  is not one, per the correction above. Plus a backlog row against run-dir minting, now data-losing
  rather than merely confusing. An agent composing a GitHub post is forbidden (DEC-138 am.6).
- Q4 **NOT blocking, ACCEPTED and closed.** Limb A's false positive — an `old_string` of `date:` alone
  is denied — is the stated price of closing the `replace_all` sweep. Recorded in the plan, not
  reopened.
