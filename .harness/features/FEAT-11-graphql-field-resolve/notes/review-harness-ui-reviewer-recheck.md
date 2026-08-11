# UI Recheck — FEAT-11 DESIGN.md + plan.yaml + BRIEF.md (Mode A, still pre-build)

**Self-scope: IN**, unchanged from the first pass (Expertise P-06): no rendered surface, but the
dispatch names the operator-facing stderr diagnostic as the designed surface, and this is a
re-review of the same contract.

## Verdict: FAIL — one new HIGH must_fix. Both original must_fix items are genuinely closed.

## 1. Original must_fix #1 (missing non-diagnosable-envelope state + criterion) — CLOSED

`DESIGN.md` `## Contract 3` now states the rule (no `value: api graphql` for any failure, including
transport/auth), `BRIEF.md` `SC-10`'s negative clause makes it checkable ("the message never contains
the string `api graphql`"), and `plan.yaml` D-03/T-01 step 3 gives concrete wording for the transport
case: `what "gh graphql call failed"`, `value owner + " project " + str(number)`, `next_step "re-run
after checking gh auth status and network access"`. I checked the rendered `what` against the forbidden
substring by hand: `"gh graphql call failed"` does not contain `"api graphql"` — confirmed, not
inferred.

**Residual, non-blocking:** this row's `what`/`value`/`next_step` exists only in `plan.yaml`, not in
`DESIGN.md`'s own Contract 2 table. A builder reading `DESIGN.md` alone (the message-contract document)
would not find the wording there.

## 2. Original must_fix #2 (query text) — CLOSED, cleanly

`plan.yaml` lines 118–134 root the query at `repositoryOwner(login: $owner)` with `__typename` and
`... on ProjectV2Owner`, matching `DESIGN.md` `## Contract 2` exactly. D-02's branch order now
separates owner-absent from organization (branches a/b) — no longer the `user(login:)` collapse my
first review faulted.

## 3. NEW must_fix — `BRIEF.md` SC-05 contradicts `DESIGN.md`'s own footnote, and BRIEF's own gaps note

`BRIEF.md` SC-05 (lines 63–70): "A fixture that returns exit 0 does not satisfy this criterion — real
`gh` does not produce that response, so it would certify a path production never takes."

`DESIGN.md`'s dagger footnote (lines 80–84) says the opposite: "an org that **does** own a reachable
board would return exit 0." `BRIEF.md`'s own Verification-gaps section (lines 120–125) concedes the
exit-1 fixture SC-05 requires "was measured against an org whose board number does not exist" — an
artifact of the unreachable board, not the general org case.

So SC-05 forbids the fixture for the transport `DESIGN.md` itself says is the real one for an org that
does have a reachable board, in a plan whose stated premise — "THE EXIT CODE IS PART OF THE FIXTURE"
(`plan.yaml` T-01 intent) — is exactly what SC-05 now violates. This is the same class of defect my
first FAIL was for (a criterion that would certify a path production doesn't take), reproduced in
reverse, inside the same feature that already flags the ambiguity elsewhere in its own text.

Not an implementation defect: `D-03`'s walk reads `__typename` before `projectV2`, so branch (b) fires
regardless of exit code — the resolver is correct either way. It is a criterion-correctness defect,
and it is checkable, which is why it gates. **Remedy is one line:** drop the "a fixture that returns
exit 0 does not satisfy this criterion" clause from SC-05, or require both the exit-0 and exit-1 org
fixtures.

## 4. Contract-table consistency (the dispatch's highest-value check) — PASS, cleanly

Row by row, `DESIGN.md` Contract 2's five rows and `plan.yaml` D-02/D-03's branches (a–d) plus the two
D-04-frozen sites: `what`/`value`/`next_step` match byte for byte, branch order matches, and the
exit-0/exit-1 transport column matches both documents and the underlying
`notes/research-FEAT-11-combined-query-probe.md` six-case table exactly. This is a large improvement
over the pre-remediation state, where `DESIGN.md` and `plan.yaml` disagreed on exit codes for the same
cases.

## 5. Q2 (row-5 grammar tension) — addressed honestly, not smoothed over; one precision gap

`plan.yaml` D-04's `because` names the tension explicitly as "ACCEPTED, not resolved" and reasons why a
reword would break the freeze. Small point: D-04 says "one of the two frozen strings states a fact
rather than an action" — by grammar it is **both** rows; row 4 is distinguished by *actionability*
(names a runnable command), not by having a verb, so a future reader could read the tension as
narrower than it is. Non-blocking.

Also: `DESIGN.md` itself — the message-contract document — still defends only row 4 in its own text;
the row-5 note lives in `plan.yaml` D-04 only. A reader who opens `DESIGN.md` alone (the more natural
place to look for a message-contract tension) will not find it there.

## 6. NEW finding — `BRIEF.md` SC-10's positive clause omits the bare-`<owner>` value shape

SC-10: "the message contains `<owner> project <number>`, the field name or the option name" — this
list does not include bare `<owner>`, which is the actual value for two of the five Contract 2 rows
(`project owner not found`, `organization-owned board not supported`). Read literally, "project owner
not found: mruangutai — check the owner login" does not satisfy SC-10's positive clause as written.

Not `must_fix`: `plan.yaml` Part B's own test instructions ("unknown owner … raises naming the owner";
"organization … raises the org refusal naming the owner") resolve it toward `DESIGN.md`'s actual
wording, so a builder following `plan.yaml` builds the right thing. But `BRIEF.md` is the stated
checkable authority, and as literally worded SC-10 would still pass an implementation that changed
those two messages' value to `<owner> project <number>` — silently breaking Contract 2's frozen rows
1–2. **One-line remedy:** add bare `<owner>` to SC-10's accepted-value list.

## 7. Doc-quality note, non-blocking

`notes/research-FEAT-11-combined-query-probe.md`'s closing section ("Where this contradicts
DESIGN.md") describes, in present tense, a contradiction `DESIGN.md`'s own "Correction, 2026-08-10"
paragraph has since retracted. Not wrong, but a reader of the research note alone could believe
`DESIGN.md` still asserts the old claim.

## 8. Terminal-surface parity — unchanged, fully auditable from source

No colour-only state, no width/truncation risk beyond the existing project-wide `factory_cli.body`
grammar. Unlike a rendered UI this dimension needs no "human/UAT eyes" caveat — a plain-text stderr
line is fully readable from source.

## Closure check (third pass) — the one must_fix from section 3 above

**Verdict: PASS.** The must_fix is closed in `BRIEF.md` itself, not merely narrated.

**Q1 — must_fix closed?** Yes. `BRIEF.md` SC-05 (lines 63-79) no longer forbids the exit-0 org
fixture; it now *requires* both (a) exit-1/`errors[]` (measured, probe case 4) and (b) exit-0/
`projectV2` populated/no `errors` key (derived from `DESIGN.md:80-84`). This is the exact reversal
my FAIL called for. `plan.yaml` matches: the T-01 preamble (lines 96-103) states "ONE ROW CARRIES
TWO ENVELOPES, and it is the only exception" and Part B (lines 243-245) repeats "exactly ONE
exception... the exit-0 organization fixture." Both documents now agree with each other and with
`DESIGN.md`'s footnote.

**Q2 — "derived, not measured" honest, and Verification-gaps consistent?** Yes on both. SC-05(b)
says plainly "no such board is reachable from this account... it is `DESIGN.md:80-84`'s reasoning
that fixes its shape" — not dressed up as measured. `notes/research-FEAT-11-combined-query-probe.md:97`
("No such board is reachable from this account") backs the claim; checked directly, the anchor
resolves correctly. The Verification-gaps bullet (now at line 132, "The organization path is never
exercised against a real org...") independently repeats the same "derived... never observed at all"
characterization. Consistent, not smoothed over.

**Non-blocking, found while checking Q2:** `DESIGN.md:84` says `"BRIEF.md:120 records the same
gap"` — that line pointer is now stale. SC-05's growth (~9 new lines) pushed the Verification-gaps
org-fixture bullet from its old position down to line 132; line 120 is now inside SC-12. Not a
criterion, doesn't certify a wrong path, purely a cross-reference gone stale from an unrelated
edit growing the file above it. One-line remedy: update the pointer to `BRIEF.md:132` (or drop the
line number and just say "BRIEF.md's Verification gaps section").

**Q3 — did the T-01 preamble edit or the sixth fixture introduce a new inconsistency?** No.
Checked three places it could have broken:
- Preamble vs. Part B vs. SC-05 all describe the same single carve-out (the org row's two
  envelopes) in matching terms — no drift between the three restatements.
- The fixture count: six siblings added (unknown-owner, org-unreachable, org-reachable/
  `GRAPHQL_ORG_OK_JSON`, board-absent, field-absent, field-not-single-select). `plan.yaml:274`'s
  "the three exit-1 fixtures must put the envelope on STDOUT" still counts correctly against the
  six — org-unreachable, board-absent, field-absent are the three exit-1 rows; the new sixth
  fixture is exit-0 and doesn't touch that count. No stale "FIVE" fixture-count references remain
  anywhere in `plan.yaml` (checked by grep).
- `plan.yaml:265` says "Unlike the other five rows this envelope was NOT measured" — read against
  the six-row measured-transport table this is off-by-one in the same low-precision way as the
  D-04 note flagged in section 5 above (it means "the other five *sibling fixtures*," not "the other
  five rows of the measured-transport table," which itself has six rows counting the success row).
  Doesn't mislead a builder — the referent is clear from context — but same class of imprecision.
  Non-blocking.

One additional non-blocking tension surfaced by cross-reading `DESIGN.md:82` against `BRIEF.md`'s
new SC-05: `DESIGN.md` says the exit-0 org envelope "is not load-bearing," while SC-05 calls fixture
(b) "the discriminating half." Both are true under different frames — `DESIGN.md` means the
*message* fires either way (not load-bearing for correctness of the string), SC-05 means the *test*
only catches the dead-branch defect via this fixture (load-bearing for the test suite) — but placed
side by side they read as contradictory, which is the same shape as my original FAIL. It does not
block: `plan.yaml:266-267` ("Build it anyway... the criterion it serves is SC-05") leaves no path by
which a builder skips fixture (b). One-line remedy if picked up later: qualify `DESIGN.md`'s clause
as "not load-bearing for the message contract" to disambiguate from "not load-bearing for the test."

**SC-10 bare-`<owner>` gap (section 6 above):** also closed. SC-10's positive clause now reads
"the message contains bare `<owner>`, `<owner> project <number>`, the field name or the option
name," closing the finding without being asked to.

No new contract-table drift, no colour/reading-order/terminal-parity change — section 4 and 8 above
still hold as measured.
