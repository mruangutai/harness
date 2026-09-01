# SIMPLIFICATION angle — FEAT-50-run-artifact-integrity plan review

## BLUF

8 findings. The plan is sound and its load-bearing placement constraints (T-03/T-04's
`if _run_domain:`, after-match, not-in-SHAPE_PATTERNS rules) are correctly load-bearing and left
alone. The real over-commitment clusters around three habits repeated across tasks: (1) T-01's
inline verify duplicates the formal regression T-02 builds one task later, (2) three task
intents mandate exact, unverified comment prose instead of the fact the comment must carry, and
(3) two numeric/identifier pins (DEC-208's number, T-04's `RE_RUN_DIGEST` name, SC-11's exact
INV-32 count) bind the plan to drafting-time snapshots or implementation-detail spellings rather
than to the behavior actually required. Nothing here questions D-01..D-08 themselves or the
settled items (DEC-174 routing, DEC-143, INV-32 ruling, `stop_hook_active`).

## Findings

| id | sev | element | summary |
|---|---|---|---|
| SIMP-01 | med | T-01 vs T-02 | inline verify re-implements the 3-state check T-02 formalizes one task later |
| SIMP-02 | low-med | D-07 vs T-02/T-05 | mutant-idiom checklist re-derived in full prose twice instead of referenced by id |
| SIMP-03 | low | T-01/T-03/T-04 | exact unverified comment narratives pinned in three intents |
| SIMP-04 | med | T-04 | verify pins the identifier name `RE_RUN_DIGEST`, not the behavior |
| SIMP-05 | med | D-08/T-07/SC-14 | DEC-208's number is a drafting-time snapshot, hardcoded in 3 places |
| SIMP-06 | med | SC-11 | exact corpus-wide INV-32 count, vulnerable to unrelated concurrent approvals |
| SIMP-07 | low | T-03 | literal phrase "belongs in the worktree" grepped on source, unbacked by any behavioral test |

### SIMP-01 — T-01's verify duplicates T-02's formal suite
**element:** T-01 `verify:` (plan.yaml:160-169) vs T-02 case 1-3 (plan.yaml:222-247)
**summary:** T-01's own verify runs the exact same three payload/exit-code checks (empty→2,
absent→0, null→0) that T-02 then re-derives as a permanent regression suite one task later.
**failure_scenario:** T-01 lands satisfying its own three inline `printf | python3 --hook` checks.
T-02 is written independently against the same requirement but with its own payload
construction. A later change to the discrimination logic satisfies one spelling's exact byte
sequence (e.g. a `\n` vs `\r\n` payload difference) but not the other's; nothing re-diffs the two,
so the codebase carries two assertions of "the same fact" that can silently drift, and whichever
one nobody re-runs (T-01's verify is a one-shot landing gate, never re-run after) goes stale first.
**alternative:** Weaken T-01's verify to a syntax/import smoke check plus the `not validated`
grep only — e.g. `bash -n`-equivalent (`python3 -c "import ast; ast.parse(open('$V').read())"`)
and `grep -q 'not validated' "$V"` — and let T-02's `test-validate-digest.py` (which
`depends_on: [T-01]` and always runs immediately after) carry the sole exit-code/stderr
assertions as the one place this fact lives.

### SIMP-02 — D-07's mutant idiom re-spelled in full twice
**element:** D-07 (plan.yaml:129-138) vs T-02 case 4 "empty-red" (plan.yaml:248-260) vs T-05
case 4 "feature-checkout-red" (plan.yaml:434-443)
**summary:** D-07 exists as the one decision recording the mutant methodology (own-directory
copy, dot-prefixed name, mode-copy, finally-block removal, the four required assertions,
INCONCLUSIVE handling). T-02 and T-05 each re-derive that entire checklist in full prose rather
than citing D-07 and stating only the task-specific binding.
**failure_scenario:** A later feature amends D-07 (e.g. relaxes the own-directory constraint
once a shared test-fixture module exists). The two already-landed test files never reference
D-07 by id, so nobody editing them is prompted to reconcile; one gets updated, the other keeps
the stale four-assertion checklist verbatim, and a reader who trusts D-07 as the sole authority
finds it no longer matches either implementation.
**alternative:** Reword T-02 case 4 and T-05 case 4/7 to "build the mutant per D-07's idiom"
and state only the task-specific binding (source file, branch located by source text, target
directory) rather than re-listing the four assertions and INCONCLUSIVE condition each time.

### SIMP-03 — exact, unverified comment narratives pinned in three intents
**element:** T-01 (plan.yaml:206-209), T-03 (plan.yaml:319-322), T-04 (plan.yaml:348-351,
380-382)
**summary:** All three intents dictate the comment's exact narrative content (down to citing
"five empty returns in FEAT-45" / "six such writes" / "a lead reusing a run directory... destroyed
the cycle-0 record"), but no `verify:` block in any of the three tasks checks comment text — this
is pure unenforced prescription of wording, the HOW of documentation, where the requirement is
only that the WHY be stated.
**failure_scenario:** A reviewer treats the prescribed sentence as if it were acceptance-tested
because it reads like one, and pushes back on an implementer who wrote an equally clear but
differently-worded comment that satisfies REQ-01..04 exactly as well — time spent reconciling
wording nothing downstream checks.
**alternative:** Replace each with a WHAT-level requirement, e.g. for T-01: "Carry a brief
comment stating the branch discriminates on presence rather than truthiness, so the platform's
gap stays distinguishable from the persona's contract violation." — dropping the FEAT-45 count
narrative from the mandated prose (the measurement stays available in BRIEF.md/D-01..D-08 for
whoever wants it).

### SIMP-04 — T-04's verify pins an identifier name, not behavior
**element:** T-04 `verify:` (plan.yaml:383-393)
**summary:** The verify script asserts the literal source contains `RE_RUN_DIGEST` and that this
exact identifier appears inside the `SHAPE_PATTERNS = (...)` tuple text — an implementation-detail
name-match, not a behavioral check of the digest-protection rule T-04 actually adds.
**failure_scenario:** An implementer satisfies T-04's real requirement in full — a shape rule
recognizing `runs/<runid>/digest.md` and enforcing the prefix-preservation logic exactly as
specified — but names the compiled pattern `DIGEST_PATH_RE` (a naming choice as reasonable as the
file's existing `RE_STATE_YAML` convention would suggest either way). T-04's own verify then fails
on a purely cosmetic mismatch even though T-05's real behavioral fixtures (`digest-clobber`,
`digest-append`) all pass, forcing a rename with no functional purpose to satisfy a landing gate.
**alternative:** Replace the identifier-name grep with a direct behavioral check equivalent to
T-05's own fixture — invoke `check-domain.sh`'s pre route against a fixture non-empty
`digest.md` with a non-prefix payload and assert exit 2, then a prefix payload and assert exit 0
— or drop T-04's inline behavioral verify entirely and rely on T-05 (`depends_on: [T-03, T-04]`,
lands immediately after) as the one place this behavior is actually exercised.

### SIMP-05 — DEC-208's number is a drafting-time snapshot, hardcoded three times
**element:** D-08 (plan.yaml:139-146), T-07 intent "DEC-207 is the last entry in the file"
(plan.yaml:522), SC-14 (BRIEF.md:154-158)
**summary:** D-08 commits to the literal number `DEC-208`, T-07's intent justifies it by
asserting DEC-207 is currently the last entry (true as of this read — confirmed: `DECISIONS.md`'s
highest entry is DEC-207), and SC-14 hardcodes `grep -q '^- DEC-208 @'`. All three depend on that
snapshot still holding at T-07's execution time, not at drafting time.
**failure_scenario:** This harness runs many feature sessions in parallel (visible directly in
this run's own peer roster). A concurrent feature's own documentor task appends its own new
decision before T-07 executes here, making "DEC-207 is the last entry" stale. T-07's documentor
either duplicates an already-used `## DEC-208` heading — `gen-decisions-index.py`'s diff check
only verifies the index matches the authority file byte-for-byte, not that the number is unique,
so this passes SC-14's own diff leg while corrupting the numbering — or renumbers to DEC-209, at
which point D-08's body and SC-14's literal grep are both wrong and nothing forces anyone to
reconcile them, since they are prose and a grep target in two different files.
**alternative:** State D-08's choice as "one new decision, numbered as the next unused DEC-NNN at
landing time" rather than committing to DEC-208 by name; have T-07's intent read "confirm the
next unused number directly against `DECISIONS.md` at execution time — do not trust this plan's
DEC-207 snapshot"; have SC-14 grep a resolved value at grading time (`grep -q "^- DEC-$(cat
.harness/.../review_sha_dec_number) @"` or equivalent) instead of the literal `DEC-208`.

### SIMP-06 — SC-11 pins an exact corpus-wide count, not a FEAT-50-scoped one
**element:** SC-11 (BRIEF.md:134-141)
**summary:** SC-11 requires the corpus-wide `INV-32` row count to be *identical* (`= 32`) before
and after this feature, in addition to its already-present "no violation names FEAT-50" leg. The
count is corpus-wide, not scoped to this feature's diff.
**failure_scenario:** While FEAT-50 is in flight, an unrelated feature's plan is approved
elsewhere in the same repo without its own panel result recorded — the same pre-existing
condition every one of the other 32 rows already represents, and one this harness's own parallel
multi-feature operation makes plausible, not hypothetical. The corpus-wide count moves to 33 for
a reason with nothing to do with FEAT-50's diff, and SC-11's exact-equality leg fails, blocking
sign-off on otherwise-complete, correct work.
**alternative:** Drop the exact-count-identity leg and keep only the already-present "no
violation naming FEAT-50" leg (which is what REQ-05/D-08's actual intent — "the two fixes FEAT-45
shipped stay in force" — needs); or, if the identity check is wanted as a stronger form, replace
the hardcoded `32` with a dynamically captured baseline taken at task start
(`before=$(... measured before this feature's work began)`) compared against the count at grading
time, rather than a literal number embedded in the verify command.

### SIMP-07 — T-03's literal-phrase grep is unbacked by any behavioral assertion
**element:** T-03 intent (plan.yaml:296-300) and `verify:` (plan.yaml:323-327)
**summary:** T-03's own verify greps the literal phrase `belongs in the worktree` out of
`check-domain.sh`'s source. Neither SC-03 nor T-05's actual behavioral cases (`feature-checkout-*`)
assert this exact wording — they check only that stderr names the target path and the worktree,
generically. Judged against T-01's `not validated` (argued and accepted as load-bearing because
exit code alone cannot discriminate the fix from the defect): this one is different — T-05's exit
code plus a generic content check (path+worktree named) already fully discriminates the fix, so
the exact phrase is a GREP clause, not a behavioral one.
**failure_scenario:** A later wording pass rewords the denial message to something equally clear
("write refused: target must sit inside <worktree>") that still names both path and worktree —
every real behavioral check (SC-03, T-05 case 1) keeps passing, but T-03's own already-landed
verify (a one-shot landing gate) is the only place asserting the old spelling, so the mismatch is
invisible until someone happens to re-run T-03's exact verify line.
**alternative:** Replace T-03's literal-phrase grep with a smoke invocation asserting the
observable behavior instead — run `check-domain.sh`'s pre route against a minimal fixture shaped
like T-05's case 1 and assert exit 2 — deferring the exact wording check entirely to T-05's
stderr-content assertions, which already require path+worktree naming without pinning phrasing.

## Explicit clean results (named shapes with no finding)

- **SC-01/SC-02 vs T-01/T-02's `verify:`, T-01's `not validated` literal specifically**: judged
  load-bearing, not flagged. T-02's intent argues correctly (plan.yaml:242-243): the absent/null
  branch and the pre-existing broken code both exit 0, so the exit code alone cannot discriminate
  the fix from the defect — the stderr text is the only discriminator. Kept as-is. (The
  *duplication of the surrounding 3-state check* between T-01 and T-02 is flagged separately as
  SIMP-01; the literal itself is sound.)
- **T-03/T-04 placement constraints** ("Inside `if _run_domain:`", "AFTER the raw-then-stripped
  match, never inside it", "Do not add a pattern to SHAPE_PATTERNS or the sweep list" for T-03;
  RE_RUN_DIGEST *placement* in SHAPE_PATTERNS, the sweep-omission rule, and the prefix-comparison
  logic for T-04): judged load-bearing and left alone, per the plan's own explicit labeling and
  D-04/D-06's stated reasoning — each is the actual difference between a working and a silently
  broken gate. (T-04's verify *mechanism* for checking the SHAPE_PATTERNS placement — the literal
  identifier match — is flagged separately as SIMP-04; the placement requirement itself is sound.)
- **T-02/T-05 case-name tokens** (`empty-red`, `null-passthrough`, `feature-checkout-red`,
  `digest-clobber-red`, `feature-checkout-absent`, `digest-append`) and the matching `git show
  <review_sha>:... | grep` clauses in SC-02/04/06/14: these are GREP clauses (case-identifier
  labels used only to confirm a case was added), not behavioral assertions — the actual behavior
  is asserted by the exit-code/stderr checks inside each case, independent of the label text. They
  are brittle to a case-description rename but low-cost and low-probability to actually break
  (nobody renames a landed test case's label without reason), and unlike SIMP-07 they gate on
  their own file's own test suite rather than pinning a phrase inside production source — judged
  acceptable, not flagged as a separate finding beyond noting the distinction here.
- **SC-10's 1463/1945 floors**: MEASUREMENT, correctly weak. Explicitly a floor (`-ge`, not `=`)
  dated at `75daa3b`, so it only reddens on a genuine regression (fewer collected tests), never on
  unrelated growth. BRIEF.md:125-130 states the design reasoning directly. Clean.
- **SC-13's "examined 45 feature dir(s)"**: MEASUREMENT, correctly scoped as history. Confirmed
  against a live run in this worktree: `check-plan-routes.py` (no args) now reports "examined 46
  feature dir(s)" — one higher, as expected, because FEAT-50's own directory now exists on disk.
  This text is framed explicitly as "At `75daa3b`... this being the first live `plan.yaml`" and is
  not part of SC-13's actual gating command, which targets only this feature's single `plan.yaml`
  path and is unaffected by corpus size. Clean, no finding.
- **T-07's DEC-208 heading title and 30–45 line guidance**: the exact heading wording
  ("A run's own record is enforced, not expected: ...") and the line-count range are unenforced by
  `verify:` (SC-14 checks only `^## DEC-208 ` as a prefix). Considered flagging as over-specified
  HOW, but the *substance* a decision-record heading and body must convey (which three rulings,
  which decisions each cites) is legitimately WHAT for a documentation artifact whose entire
  purpose is its prose — unlike T-01/T-03/T-04's source-code comments, nothing else in the
  codebase could carry this content instead. Not flagged.

## What I read

- `.agents/skills/harness-simplify/SKILL.md` §SIMPLIFICATION
- `plan.yaml` in full (574 lines): `lanes`, all 8 `decisions` D-01..D-08, all 7 `tasks` T-01..T-07
  including every `intent` and `verify` block
- `BRIEF.md` in full: all 7 REQ, all 14 SC, `Verification gaps`, the open INV-32 ruling
- `.harness/harness/docs/DECISIONS.md` — confirmed DEC-207 is currently the last entry (191
  `## DEC-` headings is wrong count from a bad grep; corrected via `grep -o 'DEC-[0-9]*' | sort -n
  | tail`, which shows DEC-205, DEC-206, DEC-207 as the top three)
- Ran `python3 .claude/skills/harness/bin/check-plan-routes.py` (no args, whole corpus) to check
  SC-13's "examined 45 feature dir(s)" claim against current state — confirmed it now reports 46,
  consistent with the claim being correctly framed as history rather than a live assertion

## Open questions

None — all four named shapes are covered above, either by a finding or an explicit clean result.
