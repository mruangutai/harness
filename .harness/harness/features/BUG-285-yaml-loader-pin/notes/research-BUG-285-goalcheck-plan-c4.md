# does this plan deliver the operator's stated intent? ALMOST — and not yet. FAIL on one criterion.

Grade of the FIVE-task, THIRTEEN-decision plan (`plan.yaml`, working state over `6cb113f4`) and
`BRIEF.md` REQ-01..11 / SC-01..15 against the 2026-09-11 rescope plus the Q7 fold-in ruling: *the
feature exists because two readers of `feature.json` disagree, and it is not done while either is
left behind.*

**The shortfall, in one sentence.** The plan closes every divergence it names, but a **second
divergence survives that the record does not name** — and SC-15 + T-04 item 3 instruct the builder to
write a docstring asserting that exactly ONE does. Shipping that docstring re-commits the very
offence D-06 exists to correct: an unverifiable prose claim of convergence, false in a new way. One
criterion (SC-15) cannot be met as written. Everything else grades met or partial.

## The parity coverage question — derived at source, not from the plan

I read both readers (`gh-sync.py:527-594`, `factory_decompose.py:111-128`), derived the classes from
their control flow, and measured them. The post-change matrix was produced by patching both sources
**in memory** (no tree write; `__file__` kept at the real path so root resolution is unaffected):
`load_recorded`'s read guard → `(OSError, UnicodeDecodeError)`, parse guard → `ValueError`;
`load_factory`'s parse → explicit read + `json.loads` under
`(json.JSONDecodeError, UnicodeDecodeError, OSError)`.

|Class (post T-02+T-04)|`load_recorded`|`load_factory`|In T-05's six?|
|---|---|---|---|
|C1 absent (`:556` / `:114`)|accept|accept|yes — input 2 (control)|
|C2 read failure: directory / chmod 000|refuse|refuse|**no**|
|C3 undecodable bytes|refuse|refuse|yes — input 6|
|C4 parse failure incl. zero-byte, YAML-only text|refuse|refuse|yes — inputs 3,4,5|
|C5 duplicate key|accept (last wins)|accept (last wins)|**no**|
|C6 document parses to a non-mapping (`[1,2]`, `"s"`)|**refuse** `:578`|**accept** `:124-125`|no — excluded, D-08|
|C7 **own block key present but NOT a mapping** (`{"github":"x","factory":"x"}`)|**refuse** `:588-594`|**accept** `:127-128`|**no — undisclosed**|
|C8 mapping lacking the block key|accept `:583`|accept `:126-128`|partly — input 1 has both keys|

**Answer: NO, the six inputs do not span the ways the readers can actually disagree.** They span
every class the feature *closes* (C1, C3, C4) and are red pre-change on three of six (measured), so
D-09's no-mutation-probe ruling holds. But **two classes still diverge post-change, not one**, and
the plan records only C6.

- **C6 (`[1,2]`) — D-08's exclusion is SOUND.** Closing it means making `load_factory` refuse a
  non-mapping document; T-02 item 5 deliberately keeps that guard, so closing it changes approved
  behaviour and widens scope. Disclosed to the operator at `BRIEF.md:137-143`. Adequate.
- **C7 — ungraded by anyone, and the same shape as C6.** `{"github": "x"}` is refused by
  `load_recorded` at `:588-594`; `load_factory` takes `f = doc.get("factory")`, finds a non-dict, and
  returns the empty factory at `:127-128` — "nothing recorded", the exact fail-open shape this bug
  exists to remove. Measured diverging both pre- and post-change. It appears in **no** decision, no
  REQ, no SC, and not in `BRIEF.md ## Risk`. D-08's justification would apply to it verbatim; the
  defect is that nobody applied it.
- **C5 duplicate key — narrated, not pinned, and that is adequate.** After T-02 both readers accept
  last-wins (measured), so the direction CLOSES. Nothing asserts it directly, but parser identity is
  pinned by T-01's and T-03's two-directional fixtures, and the duplicate-key behaviour is a
  consequence of parser identity. Recorded at `BRIEF.md:107-109` and T-02 item 2b. No input owed.
- **C2 — the one cheap improvement.** Both readers refuse a `feature.json` that is a DIRECTORY and
  one that is unreadable (measured), but only because T-02 names `OSError`. That arm is graded by
  SC-06 **inspection alone**; no automated check defends it. A seventh input ("`feature.json` is a
  directory", verdict `refuse` both) would cost T-05 four lines and convert an inspected claim into a
  standing gate.

## The never-graded half

|Item|Grade|Evidence|
|---|---|---|
|T-04|met|Anchors re-verified at `6cb113f4`: read `:558-560`, `except OSError` `:561`, msg `:562-564`, `json.loads` `:566`, dead member `:567`, comment `:568-571`, isinstance `:578`. Both edits are exactly the two the defect needs. Pre-change escape reproduced: `UnicodeDecodeError` uncaught, no `SystemExit`|
|T-05|**partial**|Six-input set correct and red pre-change (3/6 diverge); shape, loading pattern and D-11 restraint sound. Incomplete as a parity gate — C7 absent, C2 absent (above)|
|D-06|**partial**|Ruling (correct, don't confirm) right. Its `because` says "six of the seven agree and one still does not" — **measurably false**: two classes still diverge|
|D-07|met|Matrix re-derived, not copied; `unit` demanded for T-04 (`touches_runtime_code` TRUE), T-05 test-only; retargeted commands run and pass|
|D-08|**partial**|Exclusion sound and well argued for C6; "One divergence SURVIVES" is wrong by one. Recording for the operator is otherwise exemplary|
|D-09|met|No probe needed: the pre-change tree IS the mutant, verified — 3 of T-05's own 6 inputs disagree before T-02/T-04|
|D-10|met|`issubclass(UnicodeDecodeError, OSError)` False, is a `ValueError`; `json.loads` on `str` cannot raise it; `ValueError` retention is what refuses the zero-byte file. Placement in the READ guard is where the exception is actually raised|
|D-11|met|Verified: gh-sync raises bare `SystemExit` (code = message), `load_factory` exits `EXIT_REFUSED` via `factory_cli.refuse`. Demanding equal codes would change a CLI contract for no operator gain|
|D-12|met|`load_recorded` appears in `test-gh-sync-open.py` only; `_ghs` bound `:361`, reader-contract blocks `:350-474`, support docstring `gh_sync_support.py:844-846`. Placement correct by measurement|
|D-13|met, with one overclaim|Serialization is necessary — T-04/T-05 run the file T-01 edits, and `depends_on` is the only ordering the scheduler reads. But "The direction is forced" is false: T-04 → T-01 removes the same race and keeps the exact `79 ok` baseline instead of "above 79". Either order is correct; nothing to change|
|REQ-09|met|T-04 + SC-12|
|REQ-10|met|T-04 edit 2 + SC-13|
|REQ-11|**partial**|True of the chosen six-input set as written; the record understates what is left behind|
|SC-12|met|T-05 check A (verdict ≠ `escape:`) + check C (path present, no class name, no `Traceback`)|
|SC-13|met|Coverage-not-spelling framing correct; both message anchors and `:578` verified unchanged|
|SC-14|met as worded|Six inputs, per-reader verdicts, cross-reader equality, refusal-observable clauses, two positive controls. Its "four of the seven" refers to the seven-input superset, not its own six (3 of 6) — accurate but easy to misread|
|SC-15|**not_met — unmeetable as written**|It mandates a docstring naming "the non-mapping input as still divergent". C7 also survives, so the mandated text asserts a completeness that is false. Amend the criterion (and T-04 item 3, D-06, D-08, `BRIEF ## Risk`) to name both classes, or close C7|

## Re-grade of the already-graded half (the retarget moved every anchor)

Re-measured at `6cb113f4`, all at source, none trusted from `research-BUG-285-retarget-c3.md`:
**T-01/T-02/T-03 met; SC-01..SC-11 met except SC-11 partial.**

- Insertion point resolves: `test-gh-sync-open.py:396` is the `T-06C: a feature.json with no github:
  block…` check, closing `:399`; `:401` is `---------- fix1 Part B…`. Zero-byte fixture `:426-442`,
  case name at `:438`/`:441`. Helpers `:22-25`, `json :16`, `os :17`, `sys.path :13-14`, `_ghs :361`.
  `gh_sync_support.py:144/830/844-850`. `import harness_yaml` precedent at
  `test-gh-sync-start-task.py:25`. `test-factory-cli.py:11-15,28`. `(1c)` at
  `test-factory-decompose.py:426-437`, fixture `{ not: valid json [[[`, and its third check asserts
  `"YamlParseError" not in err` — post-change the message carries `JSONDecodeError`'s `str()`, which
  contains no class name, so it stays green.
- Baselines re-run by me, not adopted: `test-gh-sync-open.py` exit 0 / **79 ok** / 0 FAIL;
  `test-gh-sync-record.py` exit 0 / **56 ok** / 0 FAIL. SC-04 exact.
- **The unit-suite trap: clean at criterion level, one hole at task level.** Measured:
  `run-unit-tests.py --kind unit` → **exit 0, 4 lines beginning `FAIL `, 36 files, 2.35s** (the
  BUG-1290 mutation-proof block). No criterion and no `verify:` grades it on a FAIL count; T-03, T-04
  and T-05 each carry the EXIT-STATUS-ONLY warning. **T-02's intent does not** — it runs the same
  command as its first verify line and says nothing about the four FAIL lines. This feature has
  already burned one cycle on a wrong measurement; inoculate T-02 too.
- SC-05 survives the merge favourably: `git merge-base main HEAD` = `8902f566` = main's tip, so
  `<merge-base>..<review_sha>` on that pole file shows feature work only — `efcebe2d`'s split arrived
  via main and does not pollute the diff.
- `check-plan-routes.py plan.yaml` → **exit 0, 0 violations**, all five tasks granted to their
  `execution_agent` (T-02/T-04 to `harness-backend-dev`, the three test tasks to `harness-qa`).
- SC-11 stays **partial**: it says "in one check", T-03 check 4 mandates two named checks. Assertions
  are all present; the letter conflicts (already open as PF-a5b9a3). T-03's letter should win.

## What the operator is re-signing that is known-false

1. **`approval: status approved / 2026-09-09 / mruangutai`** over a task set that has since gained
   T-04, T-05, D-06..D-13, REQ-09..11 and SC-12..15. `BRIEF.md` says `status: pending`. The two halves
   of the record contradict each other, and `sign-approval` can only write `approved` — no verb
   returns it to pending. Effect: **reporting only** — nothing routes on it — but INV-32 grades panel
   completeness on approved plans only, so the stale `approved` is what currently makes that check
   look satisfied.
2. **`lanes.resolved_at: 7e0c2ec`**, pre-merge, with a single `tests/**` row while the plan now edits
   two files under `.claude/skills/harness/bin/`. I diffed `team-config.yaml` across
   `7e0c2ec..HEAD`: two lines, neither touching the `tests/**` row or any lane this plan uses.
   Effect: **none on routing** (D-05 is right that `execution_agent` + `check-domain.py` binds, and
   the checker exits 0); the table is a stale report, not a hazard.
3. The four open panel findings (2 info, 2 low) are unchanged; PF-142f3a still does not reproduce
   (`check-plan-routes.py` exit 0 today), so its disposition needs a re-measure, not a fix.

## Open questions

- **Q1 (BLOCKING, operator's).** C7 — a `github:`/`factory:` key present but not a mapping — survives
  this feature and appears nowhere in the record. Amend D-06's rationale, D-08, `BRIEF ## Risk`,
  SC-15 and T-04 item 3 to name **both** surviving classes (cheap, no code change), or widen T-02 to
  close C7 (changes approved behaviour). Until one of the two, SC-15 instructs a builder to write a
  false statement. I did not touch the plan: a grader that edits what it grades has graded its own edit.
- **Q2 (non-blocking).** Add a seventh T-05 input, "`feature.json` is a directory" → `refuse` both,
  so the `OSError` arm is defended by a standing gate rather than by SC-06 inspection alone?
- **Q3 (non-blocking).** Give T-02's intent the same EXIT-STATUS-ONLY warning its three siblings
  carry for `run-unit-tests.py --kind unit`.

## Addendum — S-03 amendment

**Q1 was answered by DISCLOSURE, not by closure.** C7 — a `feature.json` whose own block key is
present but is not a mapping — is now recorded as a SECOND surviving divergence beside C6, and it
remains OPEN. No test input was added for it, no guard was changed, and T-02's behaviour is
unchanged apart from a warning about how its unit runner is graded. Re-confirmed at source before
amending: `gh-sync.py:588-594` refuses (`if not isinstance(gh, dict): raise SystemExit`),
`factory_decompose.py:127-128` accepts (`f = doc.get("factory")`, non-dict → empty factory), both
at `6cb113f4`.

Amended, 2026-09-11:

|Surface|What changed|
|---|---|
|`plan.yaml` D-06 `because`|Names BOTH surviving classes with per-side behaviour and anchors; the docstring mandate no longer says "the one input that still diverges"|
|`plan.yaml` D-08 `choice` + `because`|Exclusion now covers both classes; states C7 was found by the cycle-4 goal-check, is disclosed not closed, and that closing it would change approved T-02 behaviour|
|`plan.yaml` T-04 `intent` item 3|Builder must name BOTH classes with `file:line` on each side, and must claim no completeness beyond them — the singular wording is explicitly forbidden|
|`plan.yaml` T-05 `intent`|The exclusion comment must name both absent inputs; the set stays at SIX|
|`plan.yaml` T-02 `intent`|Gained the EXIT-STATUS-ONLY unit-runner warning its three siblings carry (Q3)|
|`BRIEF.md ## Risk`|Two surviving divergences, each with input, per-side behaviour and anchors, plus one sentence leaving the option to close C7 with the operator|
|`BRIEF.md` SC-14, SC-15|Both name both classes; SC-15 now fails a docstring naming only one or claiming completeness|

**SC-15's `not_met` grade above STANDS as recorded.** It is re-graded by the next goal-check or
plan panel, never by this amendment: a grader must not grade its own edit. Q2 (a seventh input) and
the T-01 subsumption question were deliberately not acted on, and PF-a5b9a3 (SC-11 "in one check"
versus T-03 check 4's two checks) is left exactly as it stands — its remedy is a choice about test
shape that this dispatch does not own.
