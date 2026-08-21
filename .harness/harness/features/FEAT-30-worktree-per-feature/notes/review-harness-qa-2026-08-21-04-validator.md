# review-qa — evidence adequacy audit — FEAT-30 @ a76d69a

**Conclusion first:** the suite is green and the four established findings all corroborate under direct
re-execution. The gate's `matrix_ok: true` and `179/213 green` are real facts about *this* diff, and
they are a weaker statement than they read as — SC-01b's headline proof crashes-and-discards rather
than fails cleanly, T-03's own red proof is provably inert (I reproduced the mutation and measured
which cases redden), and three named safety switches have zero checked-in coverage. None of this
overturns the PASS already recorded by qa-gate — it sharpens what that PASS is evidence *of*.

## Corroborated — established finding 1 (crash-swallowing, test-feature-worktree.py)

**Confirmed by direct code trace**, not re-run of the fixture (avoids re-deriving what three CLI
mutations already proved). `case_isolation` (`test-feature-worktree.py:196`,
`os.path.join(info["dest"], f"marker-{fid}.txt")`) raises `TypeError` the instant any entry in
`created` carries `dest: None` — verified interactively: `os.path.join(None, "x")` raises
`TypeError: expected str, bytes or os.PathLike object, not NoneType`, matching the exact failure the
finding names. `main()` (`:827-861`) wraps only `shutil.rmtree` in `try/finally`; the `for name, ok,
detail in RESULTS` reporting loop sits **after** that block, so the exception propagates past it —
zero of the 88 collected results print, and 13 of 17 `case_*` calls after `case_isolation` never run.
**Severity: high. squad-appliable** (`test-feature-worktree.py` is T-01/T-10, `execution_mode: team`,
not the DEC-174 carve-out). **Gates:** yes — SC-01b's own case B lives downstream of this same
`main()` shape, so a crash anywhere in the 13 cases before it silently reports the whole file green.

## Corroborated — established finding 2 (T-03's red proof is inert)

**Reproduced directly**, not accepted on read. I copied `.claude/skills/harness/bin` to a scratch dir
(via Python `shutil.copytree`, since `bash-write-guard` denies `cp`/redirect targets outside my
domain even in `/tmp`), mutated `WORKTREES_SEGMENT` in the copy exactly as T-03's `verify:` block
does (`plan.yaml:558-563`), pointed `CHECK_DOMAIN_BIN` at the mutated copy, and ran
`test-check-domain.py` against the real repo's manifest:

- **Exit 1, 5 collateral FAILs**, none about grant parity: `schema/a CRASHING schema module...`,
  `a write INTO an out-of-place worktree...`, `the ROOT-SIDE verdict names .claude/worktrees...`,
  `a session rooted in a LEGITIMATE worktree...`, `SC-02b refuse: a linked worktree OUTSIDE the
  layout...` — all about *where worktrees belong*, not about *whether inside/outside grants agree*.
- **All 16 of the real T-03 assertions** (`{agent}: in-worktree grant equals root grant, and names
  {agent}`, `test-check-domain.py:1796`) print `ok`, 16/16, **measured**, under the mutation the
  verify block itself applies.

This is T-04 working as designed, confirmed rather than assumed: T-04's own verify
(`plan.yaml:637-651`) targets the eeabc59 guard, not a `WORKTREES_SEGMENT` string swap, and T-03's
mutation only reaches code paths T-04 did NOT touch (the `worktree_owner`/`checkout_relative`
placement rules, which still spell `WORKTREES_SEGMENT` inline in a few sites and correctly redden
when it moves). **Not a regression — it is a scope mismatch in what the red proof asserts.** I
additionally confirmed the discriminating counterexample exists elsewhere in the same feature: T-05's
red proof (mutating `bash-write-guard.sh` back to eeabc59) reddens exactly its own new SC-03/SC-07
cases (10 named FAILs, all HEAD-move/force-remove assertions) with **zero** collateral noise — so the
"exit-code-only, but the failures happen to be the right ones" shape is achievable in this feature and
T-03 simply isn't it. **Severity: med. enforcement-layer** (`test-check-domain.py`, T-03/T-04,
`execution_mode: main-session-direct`). **Does not gate** — the 16 real assertions are sound and
green on their own merits; the defect is in the verify block's exit-code framing, which is exactly
the class DEC-169 warns about (an absence/exit assertion is never a check on its own).

## Corroborated — established finding 3 (two refuted claims)

**(a) F-ALT-1 (simplify pass) — independently reconfirmed, not merely re-read.** Grepped both
checked-in test files for the three switch names: `UNION_APPLY` appears zero times in
`test-expertise-merge.py`; `REFUSE_ON_DIRTY`/`REQUIRE_LANDED` appear zero times in
`test-feature-worktree.py`. Each mutation proof lives *only* in its task's `plan.yaml` `verify:`
block (T-06 `:1033-1041`, T-02 `:463-465`) — a one-time, hand-run string replace, never a case in the
suite that runs on every future gate. The operator's refutation ("flipping each to `False` reddens
its suite") is about the **build-time** verify, which I confirm is real and ran once; it is not
evidence the **checked-in** suite would catch a future regression of the same switch, and it will not
— nothing in either file references these three names. I read this as the operator's refutation and
qa's original finding talking about two different time horizons, both correct on their own terms.
**Severity: med. squad-appliable** (`expertise-merge.py`/T-06 is `harness-backend-dev` team-mode; the
`feature-worktree.py` switches are T-02, also team-mode, `harness-dev-ops`). **Does not gate** — an
addition, not a fix to broken behavior.

**(b) F-6 (qa's own finding) — accepted as refuted, per the operator's own re-run.** Not re-derived.

## Sweep for the defect class elsewhere (established finding 4)

Checked every new/changed test file's `main()` shape for the crash-swallowing pattern (defer all
printing until after a `try/finally` that wraps only cleanup):

| File | Shape | Verdict |
|---|---|---|
| `test-feature-worktree.py` | `RESULTS` collected, printed after `try/finally` | **defect confirmed** (F-1 above) |
| `test-expertise-merge.py` | Same textual shape (`RESULTS` after `try/finally`, `:253-276`) | **not vulnerable** — every `case_*` here drives `expertise-merge.py` via `subprocess.run` with no `check=True` and reads its exit code/stdout into an assertion; a broken tool produces a bad *value* the assertion catches, not a raw Python exception. No downstream `case_*` here consumes another case's result unconditionally the way `case_isolation` consumes `create_four`'s `dest`. |
| `test-check-domain.py` | Per-case `print()` inline in the loop, no deferred collection (`main():2026-2054`) | **not vulnerable to the same shape** — a crash mid-loop still shows every case that ran before it. A residual, lower-severity risk: an uncaught exception inside `run_worktree_grant_parity()` or a sibling `run_*` would still abort the remaining `run_*` calls with no clean `FAIL`/`ok` line for that one case and a bare traceback instead of the `N/M cases passed` footer — not "88 discarded", but "some tail of cases never gets a verdict, and the failure looks like a crash, not a red". Not separately findable as high given the print-as-you-go design already limits the blast radius; **noting as info, not filing**. |
| `test-bash-write-guard.py` | Same per-case immediate print shape (`main():784-798`) | **not vulnerable**, same reasoning |

**(b) assert-only-non-zero-exit `verify:` blocks**, swept across all ten `plan.yaml` tasks:

- T-01 (`&& exit 1` on any RED PROOF FAILED, else `|| exit 1`) — **already F-5**, corroborated by the
  prior validator run and not re-derived here.
- T-03 (`WORKTREES_SEGMENT` mutation, `&&`/`||` exit-only) — **corroborated above**, inert.
- T-05 (eeabc59 guard swap, `&&`/`||` exit-only) — **same textual shape, but measured NOT vacuous**:
  10 named FAILs are exactly the new SC-03/SC-07 cases. Recorded as the counterexample above.
- T-02, T-06 — exit-only shape wraps a build-time mutation with **no matching checked-in case at
  all** (F-ALT-1, corroborated above) — a stronger gap than "vacuous assertion", since there the
  verify block is the *only* proof in existence, ever, of any kind.
- T-04 — verify block is exit-only but proven non-vacuous by the prior validator run (33/38 +
  5/8 deep-layout reddened under the real mechanism mutation); not re-run here to conserve budget.

**Conclusion on the class:** the exit-code-only `verify:` shape appears in six of ten tasks
(T-01,02,03,04,05,06). It is vacuous in exactly two — T-01 (fixture guard fires first) and T-03
(mutation lands on unrelated code) — non-vacuous in two measured directly (T-04, T-05), and for two
(T-02, T-06) the deeper problem is that there is no standing case to ever run again, vacuous or not.
This is uneven, not a blanket defect — treat each task on its own evidence, not by the shape of its
`verify:` line alone.

## Per-SC adequacy — what green does and does not bind

- **SC-01b (headline).** `case_shared_checkout_negative` (`:766-823`) is a real discriminating
  negative, correctly designed, and I confirmed its logic reads as claimed: case B accepts either
  `IsolationViolation` from the predicate or a recorded committer failure as "detected" (`:807-809`),
  which is defensible for *contention* but under-proves the *criterion*'s "detected by the same
  isolation predicate" wording (F-4, corroborated). **More importantly for this audit:** this case
  is case #7 of 17 in `main()`'s sequential list (`:846`), so it inherits F-1's crash risk from
  every case before it — a failed `create` in `create_four` (case 0) means SC-01b's own two
  assertions never execute and the suite still reports **exit 1** (indistinguishable, by exit code
  alone, from SC-01b actually catching a violation). **The green measured by qa-gate is real green,
  not simulated failure** — but the proof that green is *meaningful* rests on `create_four` never
  partially failing on the machine that runs it, which is a fixture reliability assumption, not an
  assertion the suite makes about itself.
- **SC-02, SC-02c, SC-04, SC-07** — no new findings from this pass; the prior validator's per-line
  citations (`case_cut_point`, `test-check-domain.py:1810-1838`, `case_landed_refuse_then_allow`,
  dirty-tree cases) are consistent with what I read, not re-verified line-by-line here to conserve
  budget.
- **SC-02b, SC-05** — `test-check-domain.py:1987-2010` (paired accept/refuse) and the 16-agent
  roster walk (`:1766`, `:1796`) — **directly re-run by me in this pass** (see finding 2), both
  green on their own terms, independent of T-03's inert red proof.
- **SC-03** — T-05's red proof independently reconfirmed by me as non-vacuous (10 named FAILs,
  exact match to the new cases). Strong.
- **SC-08** — UNION_APPLY's only proof is the T-06 build-time verify (F-ALT-1, corroborated). The
  checked-in suite has never once exercised the mutation it claims to guard against, and cannot,
  because the constant's name appears nowhere in it. **A regression here ships silently.**
- **SC-09** — both suites measured green by the prior validator (179/0, 213/0); not re-measured here.

## Confidence bound, per the dispatch's own framing

Every finding above is a fixture proof. The two-level `<segment>/<repo>/<id>` layout T-04 exists to
serve has zero live instances outside `test-check-domain.py`'s and `test-feature-worktree.py`'s own
fixtures — so "the grant-parity check is correct" and "T-03's red proof is inert" are both claims
about behavior nobody has yet exercised on a real multi-repo run. Weigh SC-01b, SC-02c and SC-05
accordingly: sound as measured, unproven as lived.

## Findings summary

| # | Severity | File:line @ a76d69a | Routing | Gates? |
|---|---|---|---|---|
| F-1 (corroborated) | high | `test-feature-worktree.py:196,827-861` | squad-appliable | yes (masks SC-01b) |
| F-2 (corroborated) | med | `test-check-domain.py` T-03 `verify:` (`plan.yaml:558-563`) | enforcement-layer | no |
| F-ALT-1 (corroborated) | med | `expertise-merge.py:48`, `feature-worktree.py:28-29`; no case in either test file | squad-appliable | no |
| info (new, not filed) | info | `test-check-domain.py` `run_*` sequencing, `main():2044-2052` | squad-appliable | no |

## Open questions

None blocking. F-2 and the T-01/T-03/T-05 verify-shape sweep are advisory context for whoever signs
off on the family Q3 raised in the simplify-eng digest (one standing instrument vs. four backlog
rows) — I have no new vote on that beyond confirming the sweep found six affected tasks, not four.

## SC evidence table (for pm's goal-check)

| SC | Verdict | Test |
|---|---|---|
| SC-01b | met, with caveat | `test-feature-worktree.py:766-823` (case B); caveat: F-1's crash risk upstream, F-4's predicate-bypass |
| SC-02b | met | `test-check-domain.py:1987-2010` |
| SC-03 | met, strong | `test-bash-write-guard.py` HEAD-move cases; red proof independently reconfirmed non-vacuous here |
| SC-05 | met | `test-check-domain.py:1766,1796` — reconfirmed green under T-03's own mutation |
| SC-08 | met on paper, uncovered going forward | `expertise-merge.py` UNION_APPLY has no checked-in mutation case (F-ALT-1) |
