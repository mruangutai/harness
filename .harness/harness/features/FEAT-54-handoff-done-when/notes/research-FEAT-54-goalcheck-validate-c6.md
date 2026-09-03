# Product goal-check — FEAT-54 handoff `Done when` — validate exit, at pin `dd55b357`

## BLUF

**PASS. All 14 non-UAT criteria are met; SC-10 is `pending_uat`.** Every panel evidence pointer I
tested resolved and the resolved evidence supports the criterion, with two pointers weaker than the
criterion they were offered for — both closed on evidence I derived myself, neither a behaviour
defect:

1. **SC-04's recorded run did not cover the clause it was cited for.** QA ran the literal command
   from `/Users/molchairuangutai/GitHub/harness` — the MAIN checkout, whose tree at `a12aa4e9` does
   not contain this feature's handoff notes (`test -f .../FEAT-54.../notes/handoff-plan.md` →
   absent). SC-04 requires the run to cover "every handoff note this feature itself wrote". I ran
   `bash .claude/skills/harness/bin/check-state.sh` from the WORKTREE root: **exit 0, 812 lines, 0
   lines naming `Done when`, 0 matching `refus|fail|INV-29`, 52 distinct feature/bug IDs** over a
   corpus of **145** `handoff-*.md` (141 baseline + the 4 this range added); all three FEAT-54 notes
   are present and each carries `## Done when`; the INV-17 handoff branch is demonstrably live in
   that run (6 exemption notes printed). Baseline is **141** entries at the pin, **zero** of them a
   FEAT-54 note and set-equal to SC-11's base arm — so the notes complied rather than being
   baselined. Substance met.
2. **SC-06's pointer named only `test-check-domain.py`.** Its second clause (the state check keeps
   exempting the baselined path and checks shape once present) lives in `test-check-state.py` at the
   named cases `FEAT-54 baselined missing section is exempt` and `FEAT-54 baselined malformed block
   reports`. Resolved there; met.

I ran the four cited test files at the pin's bytes (`git diff dd55b357 -- tests/` is empty): all
four exit 0, no `^FAIL`/`^not ok` line anywhere, and every case a criterion depends on printed `ok`
by name.

**Scope note, not a finding.** SC-04 is review-time by the BRIEF's own design (operator ruling on
PF-570b9c87): it asserts a repository-state fact at review, so passing here binds no later commit.
My run was from the worktree at `1e3cc982` — one commit past the pin, whose only diff is
`feature.json`'s `review_sha` field — with `STATE.md`/`feature.json` dirty and four untracked c6
review notes. No handoff note differs from the pin, so the handoff corpus measured is the pin's.

## Per-SC verdicts

| SC | Method | Verdict | Evidence I personally resolved |
|---|---|---|---|
| SC-01 | automated (integration) | met | `test-check-domain.py:4036-4042` — refusal needles `("## Done when","templates/HANDOFF.md")`; message at `check-domain.sh:1557-1559`. Both named cases `ok` |
| SC-02 | automated (integration) | met | `test-check-domain.py:4043-4064` — 5 required fixtures, each its own `_record_handoff_result` |
| SC-03 | automated (integration) | met | `test-check-domain.py:4067-4085` — 8 separately named cases |
| SC-04 | inspection | met | my own worktree-root run (BLUF ¶1). QA's `notes/qa-c6.md:20-33` does not reach the feature's own notes |
| SC-05 | automated (integration) | met | `test-check-domain.py:4235-4244` — asserts 60/61 line counts, 60 → exit 0, 61 → exit 2 with `cap is 60` |
| SC-06 | automated (integration) | met | `test-check-domain.py:4216-4232` **plus** `test-check-state.py:2227-2231` (pointer gap, ¶2) |
| SC-07 | inspection | met | `git show dd55b357`: `check-domain.sh:1562/1563`, `check-state.sh:54/1251` — one import + one call each; zero `scope:|authority:|plan-task:|brief-sc:|finding:|approval:` parser hits in either file (the 5 `approval:` hits are unrelated YAML-block prose) |
| SC-08 | inspection | met | see surface-by-surface block below |
| SC-09 | automated (integration) | met | `test-run-unit-tests-kinds.py:21-98` — positive registration + two mutants + `--kind all` isolation; ran 5/5 PASS |
| SC-10 | uat | **pending_uat** | no agent can grade it |
| SC-11 | inspection | met | my own run, both clauses (block below) |
| SC-12 | automated (unit) | met | `tests/unit/test-handoff-done-when.py:127-132` — all-four → `problems == []`; one-bad → `len(got)==1 and pointers[2][2] in got[0]` |
| SC-13 | automated (integration) | met | `test-check-domain.py:4086-4091` — 2 named cases, needle = all four prefixes |
| SC-14 | automated (integration) | met | `test-check-domain.py:4245-4247` + `test-check-state.py:2282-2296` (block below) |
| SC-15 | automated (integration) | met | `test-check-state.py:2234-2239` (e1, both baselined and not) + `2240-2243` (e2) + `2299-2348` caller-mode mutant, re-observed `real=0, mutant=1` |

## Clauses counted separately, never as one aggregate

**SC-08 — each named surface, read at the pin, one at a time.** `templates/HANDOFF.md`: "Five
sections, all required" + a live `## Done when` section with its shape. `SKILL.md:311,314`: "Five
sections… and `## Done when`" (`:135` "four segments" is the build phase, not the contract).
DEC record: `DECISIONS.md:3701` "exactly five sections", `:3710` the `## Done when` bullet,
`:3723/3725` both gates demand five, `:6698` DEC-214 "the fifth required handoff section";
`DECISIONS-INDEX.md:163,214` both say five/`Done when`. `check-domain.sh`: required list `:1554`
five entries; normative comment `:1547-1548` "five fixed sections including ## Done when"; **both
user-facing messages** name it — cap `:1552-1553` ("…a working set and ## Done when") and missing
`:1557-1559` ("the five sections are the contract"). `check-state.sh`: `HANDOFF_SECTIONS` `:1069`
five entries; the missing-section text `:1255` and the cap text `:1256` (emitted at `:1259-1261`)
enumerate nothing by hand — they print the computed `miss` list — so no four-section message
exists. A case-insensitive sweep of `four|4 section|4-section` over both gate scripts returns 16
and 13 hits respectively; I read every one —
all concern four state files, four hook routes, four interpreter launches etc., **except** the two
BRIEF-named exempt sites, and I confirmed both **byte-identical** to the feature's base
`0ec44965` (`cmp` on the extracted comment bytes): the FEAT-31 74-note measurement
(`check-state.sh:1199`) and the INV-17 empty-body narrative (`:1218`, 8 comment lines identical).
Two judgements recorded rather than buried: (a) `HANDOFF_NARRATIVE_HEADINGS = HANDOFF_SECTIONS[:4]`
(`:1070`) is a **derived subset** naming the sections whose bodies the empty-body check reads — not
a contract claim, and structurally unable to drift from the five-item list; (b) `DECISIONS.md:3765`
("fitting a real four-section handoff") passes the criterion's own mechanical exemption test — it
names FEAT-03 and reports what was measured then (49 lines, cap 40→60), and rule 15 forbids
rewriting it.

**SC-11 — two clauses, graded apart.** `BASE=0ec44965`, run from the worktree root. Diff arm 4
paths, base arm 141. PRIMARY: `comm -12` printed **0 lines**. CONTROL: `comm -23` printed **4
lines** (non-empty, so the diff arm really read paths) and `diff` against
`--diff-filter=A` output is **empty — set-equal**. Both clauses met independently.

**SC-03 — four types, eight assertions.** `plan resolves`/`plan unresolved`, `brief …`,
`finding …`, `approval …` — 8 separately named `ok` lines, each unresolved case needling its own
bad pointer. No aggregate.

**SC-02 — five violations, five fixtures.** `zero Scope` ("has 0 Scope: lines"), `two Scope`
("has 2 Scope: lines"), `zero Authority` ("has 0 Authority: lines"), `five Authority` ("has 5
Authority: lines"), `stray prose`. The count clause holds for the four countable violations; the
fifth has no count to name and its refusal quotes the offending line instead
(`handoff_done_when.py:205`, "contains unexpected line …"). Wording artifact of the criterion, not
a behaviour gap — a count for "a non-blank line that is neither" would be meaningless.

**SC-13 — two assertions.** `handoff unknown authority docs:whatever` and `handoff unknown
authority check-domain.sh:1523`, each exit 2 with all four legal prefixes required in stderr.

**SC-14 — one separately named case per gate.** `handoff no per-section cap` in
`test-check-domain.py` (Trust 50 lines, file exactly 60, exit 0) and `FEAT-54 no per-section cap` in
`test-check-state.py` (Trust 25 + Working set 25, `assert len(note.splitlines()) == 60`, zero
reported lines) — the state case matches the criterion's fixture shape literally, the domain case
uses a strictly larger single section. The "no cap message in stderr" clause is entailed rather than
separately asserted: the cap string is appended only inside the `len(lines) > 60` branch and any
appended problem forces exit 2, so exit 0 excludes it.

**SC-15 — the (e1)/(e2) pair.** e1 is asserted twice, `non-baselined absent targets do not rot` and
`baselined absent targets do not rot`, both with an empty needle tuple so ANY line naming the note
fails them. e2 is `shape remains enforced` (needles `("Scope","2")` — the count is named) and
`grammar remains enforced` (needle `legal prefixes`). Noted: the state-side grammar needle is weaker
than the criterion's "four legal prefixes listed"; the enumeration itself is asserted over the same
single shared message by `test-handoff-done-when.py:120-125` and `test-check-domain.py:4086-4091`,
which SC-07's one-implementation finding makes sufficient.

## REQ coverage

REQ-01→SC-01/SC-06; REQ-02→SC-02; REQ-03→SC-12; REQ-04→SC-03/SC-13; REQ-05→SC-03/SC-13;
REQ-06→SC-15 (write-time-only obligation) + SC-03; REQ-07→SC-11 + the 141-entry baseline check;
REQ-08→SC-05/SC-14; REQ-09→SC-08; REQ-10→SC-09 + SC-04. Every REQ has at least one criterion that
resolved to shipped code or shipped config. Nothing in the BRIEF is unclaimed.

## Open questions for the tier above

- **Q1 (non-blocking).** SC-04 mandates the run be recorded "in their own per-feature review note
  `notes/review-<reviewer>-*.md` — the deterministic place a later reader audits". It is recorded in
  `notes/qa-c6.md` and now here; `review-harness-code-reviewer-c6.md:169` explicitly disclaims the
  literal SC-04 run as out of its dispatch. No `review-*` note carries it. The fact is established
  and durably recorded in the same features dir, so I graded the substance met — but a later auditor
  following the criterion's own filename will find nothing. Operator's call whether that discharges
  the clause or the recording location should be honoured literally.
- **Q2 (non-blocking, scope).** SC-04 as designed cannot bind any commit after the pin, and no
  standing gate replaces it — the panel's own `adequacy_notes` says the same. Not a defect of this
  feature; a candidate for the backlog alongside VL-F-01.
