# Review — harness-ui-reviewer — FEAT-22-docs-layout-migration (Mode A, whole-plan, r8 re-fire)

BLUF: **PASS.** `must_fix: []`. All three r7→r8 folds land where the product digest's 15-hunk table
says (verified myself, not relayed — read the full plan text end to end, `:1-1304`, including the four
zones I had not opened this cycle before consulting the advisor: T-01, T-07, T-10, T-11). No
unannounced edit found anywhere in the file. One advisory (med): T-06's title now undersells the task
it heads. One new info-level residual noted in T-08's verify. Everything else is confirmed byte-
identical or newly verified against tracked sources at the pin.

Pin confirmed: `git rev-parse HEAD` = `0f12f14c166d231ddf648cc00ff4d12029ce0122`.
`wc -l plan.yaml` = 1304, matching the dispatch's stated EOF. Line `:1304` read directly and confirms
the close of T-11's last sentence — no residual content past what the digest's table accounts for.

## Re-measured vs inherited — the ledger the dispatch asked for

**Re-measured this cycle, by reading the working-tree plan.yaml directly** (not relayed from the
digest or from r7): `:1-285` (front matter + T-01, full), `:286-347` (T-02, full), `:347-493` (T-03,
full), `:493-593` (T-04, full), `:594-834` (T-05, full — includes `:619`, `:632-633`, `:715-732`,
`:783-786`), `:835-910` (T-06, full — includes title `:836`, files `:845-852`, intent `:867-905`),
`:910-950` (T-07, full), `:951-1152` (T-08 + T-09, full — includes `:1002-1026`, `:1068`, `:1074`),
`:1153-1304` (T-10 + T-11, full). That is the entire file, end to end.

**Re-derived at the pin, not accepted from the digest:** the DEC-189 arithmetic (T-08 §"ONE MORE
CLAUSE") — `harness_boundary.py:89-94` (`git show`) lists the four named paths as `docs/harness/**`,
`docs/PRINCIPLES.md`, `README.md`, `.github/**`; `team-config.yaml:118` grants `README.md` verbatim
and `:199` grants `.github/**` verbatim (both matched before and after the move, so neither ever made
the "nothing to match" argument); `team-config.yaml:117` grants `docs/**`, a different string from
either `docs/harness/**` or `docs/PRINCIPLES.md`, so pre-move both are matchless — "two of the four."
Post-move, T-02's `.harness/*/docs/**` entry is the literal string T-08's amendment renames
`docs/harness/**` to, so that one now matches; `docs/PRINCIPLES.md` still has nothing to match. **One
of the four**, independently confirmed. `docs/harness/DECISIONS.md:5583-5585` (`git show`) carries the
exact clause being corrected — `:5583` opens with "team-config.yaml grants docs/** and contains no
docs/harness/** entry anywhere," `:5584` continues "A glob-keyed classifier would have," and `:5585`
closes "nothing to match two of the four named paths against" — matches the plan's citation verbatim.

**Also re-derived at the pin:** `.harness/notes/audit-decisions.py` (`git show`) has exactly two
occurrences of the legacy spelling, both at `:15-16` — matches T-06's intent claim exactly, same
discipline as r7's `grep -cF` check on `test-check-domain.py`.

**Inherited, stated as such:** the "raised from 28" framing in the dispatch. No r7 snapshot exists to
diff against (untracked file). The figure is derivable, not diffable: r7's own floor would sum to
`1+3+6+5+6+2+5=28` (the same eight terms as r8's `1+3+6+5+6+1+2+5=29`, minus the notes-tool term) —
consistent with "the fold adds exactly one file" but I have not verified an r7 artifact stated 28.

## Item-by-item, per the dispatch's numbered remit

1. **T-09 allow-list arm (`:1068`, `.harness/notes/audit-decisions.py) ;;`) and floor message
   (`:1074`)** — read directly, confirmed verbatim. The 29-file floor reconciles against my own count
   of the enumerated cluster in T-09's intent (`:1143-1145`): `1+3+6+5+6+1+2+5=29`. Message text is
   clear and actionable (names the count, the floor, and dumps the file list on failure).
2. **T-05 guard `:783-786`** — read directly. Sits immediately under the "THE VERIFY EXPECTS EXACTLY
   ONE SCRIPT-LEVEL FAILURE" heading (`:773`), which is exactly where a maintainer chasing the `:619`
   echo ("integration FAILs are not the one expected") would land after reading the intent. Reads as
   intended: forbids widening the expected-FAIL set, and gives an explicit escalation path ("stop and
   report it") for breakage outside the plan's owned files. One minor observation, not a finding: the
   `:619` echo itself doesn't point back at this clause by name — proximity in the intent block
   carries the connection, not a cross-reference. Advisory only.
3. **T-06 intent `:891-904`** — read directly. Accurately and precisely describes
   `audit-decisions.py` as a live module-scope reader ("Two MODULE-SCOPE reads execute the moment the
   file is imported or run") distinct from the six prose sites, states the FileNotFoundError failure
   mode, and correctly scopes the edit to the two string literals only. No defect.
4. **T-08 `:1002-1026`** — read directly and independently re-derived (see above). The amendment
   correctly states the sentence stays literally true ("Do not write that the sentence is now false;
   it is not," `:1009`) and pins the correction to the arithmetic alone ("two of the four" → "ONE of
   the four," `:1013`). Matches what I independently derived from `harness_boundary.py` and
   `team-config.yaml` at the pin, not merely what the amendment text asserts of itself.
5. **T-04 COLLECT_FIXTURE (`:556-569`) and T-02's mirrored position pin (`:315-318`)** — read
   directly this cycle (previously only known from the digest). Both confirmed: T-02 pins the new
   grant as "the SECOND entry" immediately after the documentor's `docs/**` entry at
   `team-config.yaml:117`; T-04 pins the fixture's ninth entry "AS THE SECOND ELEMENT... immediately
   after `docs/**`" and states explicitly why the pin matters ("If the manifest and the fixture
   disagree on position the assertion fails on ordering while every entry is present, which reads as
   a mystery"). Upgraded from "claim to verify" to verified.
6. **T-05 `:619`, `= 1`** — read directly, confirmed `test "$(grep -cE '^FAIL test-' "$i")" = 1`. The
   verdict on keeping it at 1 is eng-lead's/the validator lead's, not mine; the prose that explains it
   (`:773-786`, item 2 above) is sound.

## The specific call — T-06's title

**Finding, non-blocking, `severity: med`.** `:836` still reads "Correct the instruction-side literals
and the two gate diagnostics." The task now owns seven files (`:845-852`). Six of the seven fit the
title's two categories cleanly: four instruction-side prose files (`CLAUDE.md`,
`harness-principles/SKILL.md`, `templates/plan.yaml`, `check-plan-routes.py`'s comment) and the two
named gate diagnostics (`check-state.sh`, `check-domain.sh`). The seventh,
`.harness/notes/audit-decisions.py`, belongs to neither category, and the task's own intent says so in
its own words at `:867-868`: "six are a present-tense claim in live instruction or live code, and the
seventh is a live tool that READS the moved docs at import." Its failure mode is categorically
different from the other six — a live module-scope read that raises `FileNotFoundError` at import
(dead tool) rather than a stale string that misleads a reader (`:897`: "these raise FileNotFoundError
at import, so the tool is dead rather than stale"). T-09's own intent (`:1120-1122`) independently
refuses to fold it into "the instruction-side six," calling it out as its own line item for the same
reason. Every governing surface — files list, intent, and the downstream task that audits the commit
— already states the seventh file's true category correctly. Nothing mechanical consumes the title
(no verify or gate reads it), so the risk is bounded to a human skimming the task list and
under-weighting the crash-class risk this task also carries.

I am **not** re-validating pm's stated rationale ("preserve the reviewer PASS on that text") through a
fresh PASS — that rationale attaches to the r7 signature, which the dispatch states does not carry
forward, and I am judging the title on merit against the seven-file task it heads, as instructed. On
merit: the title describes six of seven files accurately and omits the seventh's distinct risk class
entirely. That is an incompleteness, not a misdescription of the six it does name — this is why I rate
it `med` rather than `high`: nothing in the title is false, and the task's own intent and T-09's intent
both correct the record in full before an implementer would ever act on the omission. Remedy text, if
folded into any r9 eng-lead's parallel review forces: something naming the third category, e.g.
"Correct the instruction-side literals, the two gate diagnostics, and the decision-audit reader" or
similarly scoped. Whether `change_type: docs` (`:838`) is still the right classification for a task
that now edits a live executable module-scope read is eng-lead's call, not mine — I name it, I do not
rule on it.

## Two pm overrides — wording reviewed, verdicts not

- **T-05 expected-FAIL count kept at `= 1`** (declined the dispatch instruction to raise it to 2): the
  guard prose explaining this (`:773-786`, item 2 above) is sound and correctly placed. Verdict is
  eng-lead's/validator lead's, already ruled correct.
- **T-09's allow-list arm tightened to the exact path** `.harness/notes/audit-decisions.py` rather
  than a `.harness/notes/*` glob (`:1068`): the instruction prose explaining the choice (`:1148-1151`)
  is clear and well-reasoned — names the risk directly ("a glob would let an unrelated one ride the
  cluster commit silently — the exact class this audit exists to catch"). No accompanying error
  message exists for this specific arm (it is a silent-pass allow-list entry, consistent with every
  other arm in the same `case`). No wording defect.

## One additional finding — T-08's verify echo overclaims what its check proves

`:967-968`:
```
awk '/^### DEC-189 amendment 1/{f=1} f&&/two of the four/{print "ARITH"; exit}' "$d" \
  | grep -q ARITH || { echo "amendment does not correct the two-of-the-four arithmetic"; exit 1; }
```
This only detects that the literal phrase "two of the four" appears (quoted, per the intent's
instruction at `:1022`) inside the amendment section — it does not check that the corrected figure
("ONE of the four," `:1013`) actually appears anywhere. An amendment that quotes the old figure
without ever stating the new one would pass this check while failing to correct anything. The echo
text says "does not correct," which is stronger than what the grep proves. `severity: info/low`,
non-blocking — this is the same accepted residual family already named in this plan at `test-check-
domain.py:221`/`:789` ("the verify can force the false claim out but cannot prove the replacement is
right; the replacement sentence is yours to get right, and a reviewer reads it," `:1023-1024`). Not
worth a cycle on its own; noting for the record since failure-time text overclaiming what its check
verifies is squarely this role's lens.

## Anchor audit — full-file, no unannounced edit found

Reconciled every one of the 15 hunks in the product digest's table against a direct read of the r8
text, across the whole file (not just the zones the dispatch flagged as previously reached):

| Hunk (digest label) | r8 location read this cycle | Confirmed |
|---|---|---|
| T-01, 256–259 (4→8) | `:254-277`, the widened RED STATES paragraph naming test-harness-yaml.py's second break | yes, read in full — previously unread zone |
| T-02, after 310 (0→4) | `:315-318`, the position-pin clause | yes |
| T-04, after 510 / 516-519 / before 544 | `:556-569`, COLLECT_FIXTURE block | yes |
| T-05, after 748 (0→5) | `:783-786`, the widen-guard | yes |
| T-06, 818-825 / 833-834 / after 855 | `:836` (title, unchanged text) / `:891-905` (audit-decisions.py entry) | yes |
| T-08, after 916 / after 948 (0→26) | `:1002-1026`, the arithmetic clause | yes, independently re-derived |
| T-09, after 989 / 995 / 1036-1039 / 1060-1064 | `:1068` (new arm), `:1074` (29-file floor), `:1112-1122`, `:1139-1151` | yes |

Zones the digest lists with **zero** hunks (T-03, T-07, T-10, T-11) were read in full this cycle too
(previously T-07/T-10/T-11 were unread by me; T-03 was read on a prior pass this session). All four
read internally consistent, with no new-content markers and no drift from what the surrounding tasks'
intents claim about them — in particular T-10's arithmetic (`:1238-1245`, `25 - 15 - 3 - 2 = 5`) does
not touch `.harness/notes`, consistent with the digest's claim that T-10's table did not need to move
for the fold.

**This closes the gap flagged in my r7 note.** r7 recorded that the `+20`/`+21` zones past its own
`:705` rested on attestation, because no r7-native anchor of mine reached that far. This cycle I hold
r7-native anchors at `:990` and `:994` (my own prior read), which the delta maps to `:1069` and
`:1073`. Read directly this cycle: `:1069` = `docs/harness/*) ;;` (byte-identical to r7's `:990`);
`:1073` = `k=$(grep -v '^docs/harness/' "$c" | grep -c .)` (byte-identical to r7's `:994`). **Upgraded
from attested to verified.**

**A5/A6 standing item (`:606`→`:632-633`), per instruction not re-opened but byte-identity confirmed**
at the new anchor: `grep -qF 'hook(".harness/harness/docs/SPEC.md", "harness-documentor")'
$B/test-check-domain.py || { echo "case (h) at :924: the hook subject is not pinned to the migrated
docs path"; exit 1; }` — text unchanged from r7's citation, shifted exactly +27 as predicted. Not
re-litigated.

**`:688-705` enumeration entry**, also standing, confirmed at its shifted anchor `:715-732`:
"KEEP THE PAIR DISTINGUISHABLE" clause reads byte-identical to r7's citation. Not re-litigated.

## Not reopened

Per the dispatch's standing list: the `test-check-domain.py:789` residual (ruled UNCHANGED on r7,
disposition carried, not re-derived); the withdrawn S-02b MF-1 remedy; the suite measurement; the
audit-completion question (operator-ruled satisfied); `DESIGN.md`'s legitimate absence (established
twice, nothing in r8 changes it).

Carried forward from r7, unchanged disposition, not re-derived this cycle: Q1 (the `:789` subject-path
gap — T-05's D-03 human-read-diff carve-out is the only backstop, same residual class as
`harness_boundary.py:221`).

## Accessibility and theme parity

Not applicable, stated explicitly. Every surface in scope is `plan.yaml` verify/intent prose, shell
and Python literals — no rendered output, no colour, no interactive state. Batch/CLI diagnostic text
is the operator-visible surface in scope, audited above (items 1–2, and the T-08 echo finding).

## What this verdict does and does not bind

All 11 tasks remain `status: pending`; nothing has executed. This verdict binds plan TEXT only. No
Mode B review is proposed here — the build is held by operator instruction, and nothing in this review
proposes or begins execution work.

```yaml
VERDICT: PASS
DIGEST:
  headline: All three r7->r8 folds verified end-to-end against the working-tree plan (full 1-1304 read, all 15 digest hunks reconciled, DEC-189 arithmetic independently re-derived at the pin); T-06's title now undersells the seven-file task it heads (med, non-blocking); one new info-level residual in T-08's verify echo. must_fix:[].
  mode: A
  in_scope: true
  severity_max: med
  findings: 3
  must_fix: []
  states_unspecified: []
  contract_violations: []
  a11y: []
  open_questions:
    - { id: Q1, question: "Carried from r7, disposition unchanged: T-05's intent mandates a subject-path change at test-check-domain.py:789 (the --resolve half); no verify assertion names it directly. Same residual class already accepted at harness_boundary.py:221. Non-blocking.", blocking: false }
    - { id: Q2, question: "T-06's title (:836) omits the third file category (.harness/notes/audit-decisions.py, a live import-time reader) that its own intent and T-09's intent both name explicitly. Recommend folding a title fix into any r9 eng-lead's parallel review forces, rather than a standalone cycle. change_type: docs (:838) on a task now editing a live executable is eng-lead's call, not mine.", blocking: false }
    - { id: Q3, question: "T-08's verify (:967-968) checks that the amendment quotes the old figure ('two of the four') but does not check that the corrected figure ('ONE of the four') is present anywhere. Info-level residual, same accepted-check-limitation family as test-check-domain.py:221/:789. Not worth a cycle alone.", blocking: false }
  files_touched: []
  expertise_update: []
artifact: .harness/harness/features/FEAT-22-docs-layout-migration/notes/review-harness-ui-reviewer-2026-08-15-plan-r8.md
```
