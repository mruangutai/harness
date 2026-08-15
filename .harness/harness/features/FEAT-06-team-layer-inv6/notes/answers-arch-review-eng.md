# User answers — FEAT-06 architecture-review gate, run `arch-review-eng` — 2026-08-04

Taken by the main session from the user directly. Both blocking questions answered YES. All six
AMF findings are now pm's to fix in one run.

## Q1 / AMF-4 — the freeze is LIFTED for defects. pm edits the T-08 text.

**The freeze was the main session's wording error, and it is corrected here.** The instruction in
`notes/answers-replan-product.md` — "T-02, SC-04, T-07(1) and T-08 stand exactly as written" —
meant *do not apply D-08's alternative branch*. It was read as *do not touch this text at all*,
which is why a defect inside T-08 came back as a question instead of a fix.

**Standing clarification for the rest of this feature and for future runs:** a freeze on a signed
decision freezes the DECISION, not the prose around it. Defects found inside frozen text are
fixed, and the fix is reported. A freeze is never a reason to ship a known error.

**Severity note, so pm scopes the fix correctly.** The main session verified `PLAN.md:530-540` at
source. The text is a CONDITIONAL — "If the user signs D-08's ALTERNATIVE branch instead, narrow
`:1980` … and leave `:1978` alone" — and its antecedent is resolvably false from `PLAN.md:127-132`,
which reads "D-08 (DECIDED 2026-08-04) … Signed by the user on pm's RECOMMENDED branch … The
flip-delta below is therefore NOT applied." So this is a **stale conditional in a signed plan**,
not a live instruction that would have built the wrong branch. It is worth deleting because this
feature's own REQ-08 is that shipped accounts agree — but the digest's framing ("a live ACTION
INSTRUCTION telling the documentor to build the UNSIGNED branch") overstated it, and pm should not
plan a larger repair than the defect warrants.

## Q2 / AMF-5 — YES. Reshape SC-14's predicate. It is a defect, not a design choice.

**Keep unchanged:** `grep -c -i 'test_matrix'` on `.claude/skills/harness/SKILL.md` returns >= 1.
This is the half the user hand-verified, it returns 0 at `635ef14`, and it is what makes #24
falsifiable — no other check in this feature fails if `SKILL.md` is never touched for qa.

**Change:** the co-occurrence half. It currently requires ONE PHYSICAL LINE carrying `qa`,
`validator` AND `loop_back` (`PLAN.md:483-484`, `:657-658`, `BRIEF.md:196-201`). Replace with a
windowed match — the tokens appear within a bounded span of lines — so the check tests content and
not markdown line-wrapping.

### Demonstrated, not argued

The main session rendered T-11's own prescribed passage (`PLAN.md:640-645`) and ran both halves:

| Line | Width | Tokens |
|---|---|---|
| 1 | 97 | `qa`, `validator` |
| 2 | 98 | `qa`, `test_matrix` |
| 3 | 93 | `qa` |
| 4 | 93 | `loop_back` |
| 5 | 96 | — |
| 6 | 53 | `validator` |

`test_matrix` half PASSES. Co-occurrence half returns **zero matching lines**. **SC-14 is RED on
the correct passage.** The passage is already 93-98 chars against the file's 87-char mean, so
satisfying the one-line rule means a ~130-150 char line or a contrived sentence, in the one file
preloaded at every orchestrator spawn — and a later reflow turns the gate red with content
unchanged.

`SKILL.md:38-39` shows the file's own habit: `validator` already sits alone on a wrapped
continuation line. T-11's passage inherits that habit because it was written to match the file.

### Where the error came from — recorded so the pattern is not repeated

T-07 has nine checks. **Seven parse structured data** (YAML step-id sets, `personas:` lists, table
cells) where token-presence is exactly right because structure carries meaning. **Two grep markdown
prose.** Check (5) established the idiom — "`SKILL.md` contains a line matching both `build` and
`DEC-118`" — which holds by luck at two tokens in one sentence. Check (8) reused it at **three**
tokens across a six-line passage without re-running it against the text pm itself prescribed in
T-11.

pm named this exact weakness at `BRIEF.md:217` — "**Markdown behaviour has no runner.** SC-09,
SC-10, SC-14 and SC-15 assert that `SKILL.md` and…" — and did not apply the caution to its own
predicate. The intent was right and stated correctly; only the mechanism is wrong.

**Both `PLAN.md` and `BRIEF.md` carry the predicate, so both change.** SC-14's stated intent does
not change and must not be weakened.

## AMF-1, AMF-2, AMF-3, AMF-6 — pm's outright, no user input needed

Fix as the architecture review specified. All six land in ONE pm run.

## Re-review after the fix — DELTA, not a second full pass

The user's standing instruction — they sign a plan an architect has passed end to end — is
satisfied: the full review ran and cleared the re-scope, the eight decisions, all six EMF remedies
and the qa two-places shape. This pass changes six known sites, not the structure.

Scope the delta to the six AMF sites only. Estimated 10-19 against `arch-review-eng`'s 28.19 for
the full pass.

## Budget — no change. $160 stands.

90.10 measured of 160; 102-135 including the segment-1 band that can never now be measured. Not a
crossing. Report it again at the next gate; do not quietly overrun.

## Terminus

If the delta re-review PASSes, return so the user signs BRIEF and PLAN together. The user has now
spent three gates on this plan phase; do not send back anything that is not a real decision.
