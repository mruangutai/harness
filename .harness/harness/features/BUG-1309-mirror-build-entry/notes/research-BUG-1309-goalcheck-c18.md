# Goal-check c18 — SC-04 and SC-11 at `9fe5cf3112aed6782dfe3f1833b5e7077b31d953`

**BLUF. SC-11 = MET (unchanged and untouched by this cycle's delta). SC-04 = UNMET — on ONE
remaining evidence clause, and not the one c17 was worried about.** All three c17 gaps are closed:
gap A (clause a) MET, gap C (clause i) MET four-for-four, gap B (clause h — "ambiguity before the era
gate") **ruled MET** on the reasoning in §2. Grading SC-04 conjunct by conjunct surfaces a clause no
earlier goal-check graded separately: the ambiguity deny's **reason text** — "a reason saying the
duplicated top-level `branch` field must be corrected" — is asserted by **no** case. Behaviour is
correct in source; the `automated` evidence SC-04 declares does not reach it. Budget is exhausted
(16/16), so it is reported unmet, not remedied and not waived.

Graded at the pin only, via `git show 9fe5cf31:<path>`. Evidence consumed, never re-measured:
`notes/qa-c18.md` (36 ok / 0 FAIL / ALL PASSED / rc=0, `matrix_ok: true`),
`runs/c18-validator/digest.md` (panel PASS, `severity_max: med`, `must_fix: []`),
`notes/research-BUG-1309-goalcheck-c17.md`. No suite re-run by me.

## 1. SC-04 (`BRIEF.md:108-125`) — clause table, `verify: automated evidence: integration`

Line anchors are into `git show 9fe5cf31:tests/integration/test-merge-gate.py`.

| # | clause (short) | carrying case | verdict | evidence |
|---|---|---|---|---|
| a | single-owner deny (`recovery-required`, or absent under enabled sync) names the feature **and** the re-run command | `T-05 recovery-required denies`; `T-05 non-era absent build_entry denies naming feature and re-run command` | **MET** | `:65`, `:67-68` (asserts `FEAT-9001-fixture-non-era` **and** `gh-sync.py open` in one reason); discriminating, `qa-c18.md` §2 Gap A |
| b | `opened` / `not-applicable` / `recovered-terminal` are allowed | `T-05 opened allows`, `T-05 not-applicable allows`, `T-05 recovered-terminal allows` | **MET** | `:71-75` (exit 0, `d is None`) |
| c | era-exempt merge ALLOWED at exit 0 with no permission decision emitted | `T-05 era-exempt absent build_entry allows`; `T-05 era-exempt recovery-required allows` | **MET** | `:92-93`, `:95-97` (`r.returncode == 0`, `d is None`, `predates` on stderr) |
| d | two or more valid attributable claimants → DENIED | `T-05 duplicate valid records claiming the branch deny naming both` | **MET** | `:157-163` |
| e | EVERY claiming directory id named, stable across runs | same case | **MET** | `:161-162` (both ids; `reason == repeated_reason` over two invocations); `sorted()` at `merge-gate.py:173` |
| f | the reason says the duplicated top-level `branch` field must be corrected | **none** | **UNMET** | `:159-163` asserts only the two ids, `"gh-sync.py" not in reason`, and run-to-run equality — no fragment of the wording (`claimed by more than one`, `branch`, `Correct the duplicated`) is asserted by any case in the file. Correct in source: `merge-gate.py:174` |
| g | NO re-run / receipt command offered on the ambiguity deny | same case | **MET** | `:162` (`"gh-sync.py" not in reason`) |
| h | ambiguity decided BEFORE the era gate | `T-05 duplicate era-exempt claimant still denies before era gate` | **MET** (ruling §2) | `:165-174`; genuinely era-exempt second claimant `BUG-1030-stale-anchor-write-hazard` (`feature_schema.py:227`); `qa-c18.md` §2 Gap B |
| i | one owner plus ANY noise is not ambiguity — unreadable, malformed, non-object, different-branch | `T-05 single owner ignores unreadable malformed non-object and different-branch noise`; `T-05 single owner plus unrelated malformed record still allows` | **MET** | `:183-205`, `:181`; each of the four arms individually removed from a scratch copy reddens the case — `qa-c18.md` §3, four for four |
| j | a branch no valid record claims is ALLOWED while such a record exists | `T-05 branch matching no feature allows`; `T-05 no-record branch ignores unrelated malformed record` | **MET** | `:80`, `:137-149` |
| k | `gh` unavailable, no local condemnation → ALLOW with one stderr note | `T-05 gh outage with no matching feature allows` | **MET** (note) | `:117` — asserts `could not verify` in stderr and `d is None`; asserts the content, not that it is exactly one line |

**SC-04 = UNMET**, solely on clause (f). Every other conjunct is carried by a named, passing,
integration-kind case at the pin.

Clause (f) remedy, plainly: one added conjunct on the existing case at `:159-163` (e.g. `"branch" in
reason`). **No budget exists to make it in this cycle** — `cycles_used` is 16 of 16. Nothing here is
waived: the behaviour is inspected-correct at `merge-gate.py:172-175`, which is `inspection`, not the
`automated` evidence SC-04 declares.

## 2. Clause (h) — the open judgement: **MET**

The case exists, passes, and constructs a genuinely era-exempt second claimant. qa measured it
**non-discriminating** against one specific mutant — hoisting the era gate above `len(owners) > 1`
and keying it on `owners[0]` — because `glob.glob` on this host returns `FEAT-9001-fixture-non-era`
before `BUG-1030-stale-anchor-write-hazard` irrespective of creation order, so the era-exempt
claimant never occupies `owners[0]` (`qa-c18.md` §2/§Coverage; the orchestrator reproduced the glob
order independently).

Ruled MET, on three grounds, none of which is a lowered bar:

1. **SC-04 asks for automated evidence of a BEHAVIOUR** — "the deny is reached even when a claimant
   IS era-exempt". The case observes exactly that observable: an era-exempt claimant is present and
   the merge is denied, naming both ids, with no receipt command. That is the clause's own subject.
2. **Its sibling SC-03 demands reddenability in its OWN text; SC-04 does not.** SC-03 spells out
   "The refusing assertion is DISCRIMINATING at `review_sha` … an assertion that cannot be made to
   redden is reported as non-discriminating rather than kept" (`BRIEF.md:97-107`). SC-04 carries no
   such sentence — and SC-11 does. Importing SC-03's requirement into SC-04 would grade a criterion
   the brief did not write; the weakest-sufficient-specification rule cuts against that, and so does
   the fact that the operator signed three criteria with three different bars deliberately.
3. **The behaviour is correct in source, re-derived by me at the pin, not taken from qa.**
   `git show 9fe5cf31:.claude/skills/harness/bin/merge-gate.py`: the ambiguity guard is
   `if len(owners) > 1:` at `:172` with its `deny(...)` at `:174`, and the era gate
   `if feat in feature_schema.BUILD_ENTRY_ERA_EXEMPT:` is at `:179`, after `feat_dir, document =
   owners[0]` at `:176`. The guard keys on the **count** alone and never on `owners[0]`'s identity,
   and the message uses `sorted(...)`, so the ordering is order-independent by construction. (The
   dispatch's `:167-181` is the same region, one anchor block off.)

What is therefore NOT proven, stated so it cannot be read as more than it is: the case is a
**behaviour witness, not a defence**. It would keep passing under an `owners[0]`-keyed era hoist on
this filesystem. **The remedy would be ONE fixture ordering change — make the era-exempt claimant
sort first (rename it, or create it as the only lexicographically-first entry) so it lands at
`owners[0]`. NO budget exists to make it in this cycle.** Per O-02 this is a fragility to route as a
backlog chore, never grounds to fail the clause the criterion actually wrote.

## 3. SC-11 (`BRIEF.md:161-172`) — **MET**, confirming the c17 grade at this pin

**The one-commit delta does NOT touch SC-11, its three cases, or its discrimination evidence.**
Established, not assumed:

- The range `94b5e465..9fe5cf31` contains exactly one code commit, `9fe5cf31`
  (`tests/integration/test-merge-gate.py`, +37/−1). `git diff --name-only 94b5e465..9fe5cf31` over
  `.claude` and non-test `*.py` returns **nothing**: `merge-gate.py` is byte-identical at both pins,
  so the `e374c9a2` discrimination measurement still applies unchanged.
- `9fe5cf31`'s three hunks cover old lines 64-70, 160-165 and 168-173. The SC-11 loop sat at old
  `:191-198`; it is **outside every hunk** and moved only by renumbering, to `:227-234` at the pin.
  The three tuples are unchanged text: `T-05 merge --abort on an owing branch allows`,
  `T-05 merge --continue on an owing branch allows`, `T-05 merge --quit on an owing branch allows`,
  each driven through `check()` with `r.returncode == 0 and d is None` on a fresh owing `fixture()`.
- All three passed in this cycle's run (`qa-c18.md` §1 — 36 ok, 0 FAIL, `ALL PASSED`, rc=0, captured
  without a pipe).
- Discrimination against `git show e374c9a2:.claude/skills/harness/bin/merge-gate.py` is **cited,
  not re-run by me**: `notes/qa-c17.md:50-63`, one row per case name, each recording that it reddens
  at `e374c9a2` (old code denies). Carried forward legitimately only because the production file did
  not move in the range, per the check above.

## 4. Non-modification

The only file I wrote is this note, plus one bullet appended to
`observations/harness-pm.md` through `observations-merge.py`. `BRIEF.md`, `plan.yaml`,
`feature.json`, `STATE.md`, the UAT script, every production source file and every test file are
**unmodified by me**; HEAD is `9fe5cf31` unchanged. No suite, formatter or linter was run.

## 5. Open questions

- **Q1 (blocking the ship decision; not SC-10).** SC-04 is UNMET on clause (f) — the ambiguity
  deny's reason wording carries no automated assertion — with the behaviour inspected-correct at
  `merge-gate.py:174`. Budget is 16/16, so the operator chooses: accept the single evidence gap with
  a recorded ruling, or carry it as a follow-up bug for the missing conjunct. Not mine to decide,
  and I did not soften the grade.
- **Q2 (non-blocking).** Clause (h)'s case is a witness, not a defence: it survives an
  `owners[0]`-keyed era hoist because of this host's glob order. One fixture ordering change fixes
  it; it belongs in the same follow-up as Q1.
- **Q3 (non-blocking, calibration).** Clause (k)'s case asserts the stderr *content* but not that
  the note is exactly one line, and the `chmod 0` fixture in clause (i) is non-claiming
  (`qa-c18.md` §3 tail). Neither changes a verdict; both are tighter-fixture notes.
