# Goal-check — BUG-1305 plan vs stated intent — cycle 3

**Does this plan deliver the operator's stated intent? No — the mechanism is now the right shape and
closes B-11's modal collision, but three defects in its specification would ship a guard that bricks a
legitimate run directory, leaves the B-11 hand-repair action without a route for one of the three
shapes the BRIEF promises, and gives the builder two contradictory insertion points whose own test
cases assert opposite outcomes.**

**fit for the adversarial panel: yes**
**fit for signature: no**

`high`, `critical` and unrated findings are gating. F-01, F-02 and F-03 are `high`, so this plan is not
fit for signature. It IS fit for the panel: every finding below is a specification defect a reader can
settle from the plan text and `c369fb1f`, not a missing measurement, so the panel has something to
attack rather than a hole to wait on.

**I authored `BRIEF.md` and `plan.yaml` and I am grading them.** This is self-review; the compensating
control is the adversarial panel, which is the independent read, plus the operator's signature.

## Findings

| id | sev | finding |
|---|---|---|
| F-01 | high | T-02 and T-09 name contradictory insertion points for the witness seed-field compare, and their own cases assert opposite outcomes |
| F-02 | high | `conflict()`'s `run_id` row carries no recorded-non-None guard, so one legitimate first write brands a run directory unwritable forever |
| F-03 | high | REQ-01 and T-02 promise the truncated-checkpoint rewrite is permitted; it is refused at `c369fb1f` and this plan does not change that |
| F-04 | med | D-01 calls the witness "detection only" and one sentence later makes its seed fields a denial input |
| F-05 | med | SC-09 and D-13 describe a narrower invariant than T-03 specifies, so the criterion cannot fail on the paths it omits |
| F-06 | med | SC-01's FAILS-if enumeration omits case (a); the seed-field refusal can be wholly absent and SC-01 still reads met |
| F-07 | med | Nothing grades that the PostToolUse hook actually fires; SC-10's evidence is the script invoked directly |
| F-08 | low | The first-write race between two runs is disclosed as "the legacy window", not as the residual instance of the modal collision |
| F-09 | low | Retired T-04 and T-10 still carry `traces:`, so REQ coverage counted over the plan reads two dead tasks as coverage |
| F-10 | info | REQ-01 states the forgery residual is "not a risk you are being asked to accept" while it is exactly an accepted residual |

### F-01 · high · two insertion points, one compare

T-02 (`plan.yaml:306-308`) places the witness seed-field compare "After the existing prior-file identity
compare and **inside the same `if absolute_path is not None:` region (:1508-1529 at c369fb1f)**". Those
are different places: `check-domain.sh:1508` opens the region, the prior read and the
`prior_unreadable` refusal occupy `:1509-1529`, and the "existing prior-file identity compare" is the
`if prior_state:` ladder that starts at `:1530` and ends at `:1574`. **Scenario:** a builder placing it
before the ladder makes T-09's precedence case (`plan.yaml:881-882` — prior run_id A + U1, incoming
run_id B + U1, expected exit 2 with *Issue 1124* wording) fail, because the witness compare answers
first with Issue-1305 wording. A builder placing it after the ladder makes T-02's own third case
(`plan.yaml:340-341` — unparseable prior, witness for A, incoming B) non-discriminating, because
`:1539-1546` refuses the unparseable prior before the witness is ever consulted. Whichever choice is
made, one task's pinned case is wrong; the build discovers it at the second task, with the enforcement
layer already open.

### F-02 · high · the witness can be born poisoned, and it is write-once

T-01 specifies `record_seed` to store `str(doc.get(k))` "when the key is present and **None when it is
not**" (`plan.yaml:158-161`), and `conflict()` to compare `str(marker.get("run_id")) !=
str(doc.get("run_id"))` **unconditionally** (`plan.yaml:170`) — the recorded-non-None guard exists only
for `feature, squad, host` (`plan.yaml:171-172`). **Scenario:** a lead's first checkpoint Write omits
`run_id` (nothing refuses it — the Issue-1106 missing-`run_id` refusal at `check-domain.sh:1553-1565`
fires only when a prior exists, and `run_id` is not required by `ALLOWED` at `:1450`). POST records a
witness with `run_id: null`. The lead's next write, correct and carrying `run_id: A`, hits
`str(None) != "A"` and is refused on Write and Edit; `record_seed` is write-once so the witness cannot
be corrected; `bash-write-guard.sh:744-767` refuses a Bash write or `rm` of a run artifact; and T-03
then reports the directory to the operator as a clobber. The run directory is permanently unwritable by
its own owner, by a guard added to stop exactly the opposite thing. T-01's case list names only
"conflict returns None when the marker recorded None for **a** field the doc now supplies"
(`plan.yaml:227`), which does not resolve which field, so the contradiction survives the test list too.

### F-03 · high · "truncated" is promised and not delivered

REQ-01 (`BRIEF.md:73-75`) and T-02 (`plan.yaml:319-321`) both assert that rewriting a **truncated**,
zeroed or hand-deleted checkpoint passes. Zeroed and absent do pass — the `if prior_state:` ladder is
not entered. Truncated does not: a non-empty prior that will not parse is refused at
`check-domain.sh:1539-1546` ("run state already exists but does not parse") today, and no task in this
plan touches that branch. SC-01(d) grades only the zero-byte and absent forms (`BRIEF.md:242-246`), so
nothing catches the gap. **Scenario:** a lead whose `state.yaml` was truncated by an interrupted write
follows REQ-01, attempts the Write, is refused; the Edit route reconstructs against the same
unparseable prior and is refused; `rm` is refused by the Bash guard. The B-11 recovery action — the one
this feature exists to keep open — has no route for that shape, and the operator signed a requirement
saying it does. Either narrow REQ-01's sentence to zeroed/absent and say plainly that a truncated
checkpoint needs a human outside the guards, or add the task that opens it.

### F-04 · med · D-01 contradicts itself inside one entry

D-01 states the marker "survives as a WITNESS for **detection only**", then closes with "The complete
set of denial inputs is: **the seed fields conflict() compares** (run_id, feature, squad, host), and
the prior checkpoint run_uid against the incoming one." `conflict()` compares the incoming write
against the **witness** (T-01, `plan.yaml:174-177`), so the witness is a PRE denial input. **Scenario:**
a builder implementing from D-01's first clause omits T-02's PRE witness compare entirely; SC-01(a) has
no failure condition of its own (F-06), so nothing catches it.

### F-05 · med · SC-09 pins a narrower invariant than T-03 builds

SC-09 (`BRIEF.md:332-334`) and D-13 (`plan.yaml:102`) both say the invariant "judges a run directory
only when its witness AND its checkpoint both carry a `run_uid`". T-03 also reports an unreadable
witness (`plan.yaml:395-397`) and a witness/checkpoint seed-field disagreement (`plan.yaml:398-403`),
neither of which requires a `run_uid` on either side. **The day-one claim still holds** — every reported
path requires a witness, no witness exists before this feature's POST hook writes one, and I confirmed
631 witness-less run `state.yaml` files across this root and its worktrees today against the 630 the
BRIEF records at `c369fb1f`, so the population is honestly baselined and growing. What fails is the
criterion: its FAILS-if names two tests and one control-plane run, none of which exercises the
unreadable-witness or seed-conflict paths. **Scenario:** a later change makes the seed-field path fire
on a legacy-shaped directory; SC-09 is still met, because it can only fail on the two cases it names.

### F-06 · med · SC-01 case (a) has no failure condition

SC-01 opens "Six cases, each pinned by its own test" and then its FAILS-if names only (b), (c), (d) and
(e) (`BRIEF.md:251-252`). **Scenario:** the build ships without the seed-field refusal; one grader reads
the leading sentence as binding and returns `not_met`, another reads the explicit enumeration as
exhaustive and returns `met`. Two competent readers, opposite verdicts, from the criterion text alone.

### F-07 · med · the whole guarantee rests on a hook nobody grades firing

Prevention is inert until POST mints, and detection is inert until POST writes a witness. SC-10 says
"After a checkpoint Write into a fresh run directory has landed and the PostToolUse hook has run"
(`BRIEF.md:345-346`), but its evidence is an `integration` test over an `isolated_bin` root that invokes
`check-domain.sh --post` directly. **Scenario:** the hook registration is correct today
(`.claude/settings.json` PostToolUse `Write|Edit|Bash`) and INV-9 asserts registration, but a host that
does not deliver PostToolUse for the Write tool — the same uncertainty T-11 exists to measure for
NotebookEdit — leaves every directory permanently legacy, refused by nothing and reported by nothing,
with every criterion green. Either SC-10 states that the direct invocation is the evidence, or a task
observes one real end-to-end mint.

### F-08 · low · the first-write race is disclosed under the wrong name

T-02 (`plan.yaml:301-304`) states the legacy window honestly. It frames it as "today's behaviour
exactly". **Scenario:** two runs choose the same fresh slug within the same window — the modal B-11
shape — and the second lands before the first's POST. The prior carries no `run_uid`, `uid_conflict`
returns None by the legacy row, the clobber is permitted and is invisible to T-03 forever. That is
correctly *unchanged* from today, and it is also the exact defect this feature is named for occurring
inside the new mechanism's blind spot. It deserves to be named as that, not only as a legacy window.

### F-09 · low · retired tasks still trace

T-04 (`status: abandoned`) traces REQ-01; T-10 traces REQ-02 and REQ-03. No live task depends on either
(verified by loading the plan), and both verifies assert their notes do not exist, so the graph is
inert. **Scenario:** a REQ-coverage count taken over `traces:` reports REQ-03 covered by two tasks when
one of them will never run.

### F-10 · info · the residual is accepted while saying it is not

REQ-01 (`BRIEF.md:99-105`) says the copy-the-`run_uid` forgery case "is not a risk you are being asked
to accept". It is one: the operator signs a mechanism whose stated residual is an undetectable clobber.
Saying so plainly costs nothing and keeps the record honest.

## What works, and where the collision stops

The modal collision stops at `check-domain.sh`, PRE, `RE_STATE_YAML`, inside the `if prior_state:`
ladder immediately after the Issue-1124 `run_id` compare (`:1566-1574` at `c369fb1f`), on both the Write
route and the Edit route — Edit because `:1905-1923` reconstructs `RE_STATE_YAML` content from
`old_string`/`new_string` before the shape phase. The foreign run carries no `run_uid`,
`uid_conflict(prior_doc, doc)` returns the missing-value reason, and the writer sees exit 2 with the
Issue-1305 head, U1 named, and the two ways forward. The three writes that must not stop: the owner's
ordinary upsert passes because it carries U1 out of the file it is updating; the resumed owner passes
identically, with no session input anywhere in the ladder (D-01's denial-input list is exhaustive and
correct on this point); the owner recovering a zeroed or absent checkpoint never enters the ladder at
all, and POST restores its original U1 from the witness by the effective-uid ordering at
`plan.yaml:286-291`. Cycle 2's session-keyed defect and the panel's acquisition defect are both
genuinely gone, not renamed. Routes and lanes are clean: `check-plan-routes.py` exits 0 with only the
expected DEC-174 deviations.

## REQ → task → SC

- **Mode A.** REQ-01 → T-01, T-02, T-09, T-11 → SC-01, SC-10, SC-11. REQ-02 → T-01, T-03 → SC-02,
  SC-09. REQ-03 → T-03 → SC-03. REQ-08 → T-07 → SC-08.
- **Mode B.** REQ-04 → T-05 → SC-04. REQ-05 → T-06 → SC-05. REQ-06 → T-06 → SC-06.
- **Both.** REQ-07 → T-02, T-05, T-06, T-08, T-09 → SC-07.
- Every REQ has at least one live task and at least one SC; every SC has a live task producing its
  evidence; every live task traces a REQ that still exists. Retired: T-04, T-10 — no live dependents,
  no unique REQ, no unique SC (F-09).

## Signature-blocking residue

| residue | visible? | framed as a choice? | priced? |
|---|---|---|---|
| forgery residual | yes, REQ-01 | no — and correctly so, nothing can be done; but see F-10 | yes, by nature |
| DEC-145 partial supersession | yes, Constraints | yes | yes — collision frequency, not correctness |
| DEC-208's false scope clause | yes, Constraints + D-04 | yes, two named options | yes |
| dropped-`run_uid` refusal | yes, REQ-01 | no — stated as the mechanism's price, which is right: the alternative deletes branch (c) | yes, three bounds; bounds 1 and 3 are delivered by T-09, bound 2 helps only after a landing, not at the refusal |
| striking REQ-08 | yes, REQ-08 | yes | yes |

The dropped-`run_uid` refusal is proportionate: it is the same branch that catches the foreign run, so
declining it deletes the mechanism. The mitigation is real — T-09 writes the message that names the
line to carry forward, and `harness-team/SKILL.md:54-55` is the single seeding doctrine surface in the
tree (grepped), so amending it there is complete rather than partial.

## Open questions

- Q1 (blocking): F-01's insertion point — before or after the `if prior_state:` ladder. The answer
  decides which of two pinned test cases is correct.
- Q2 (blocking): F-03 — narrow REQ-01 to zeroed/absent, or add the task that gives a truncated
  checkpoint a repair route.

## Working tree

```
?? .harness/harness/features/BUG-1305-run-state-clobber/
```

No tracked-file modification. The only path listed is the untracked feature directory, which was
already untracked before this run; this run wrote one note inside it and nothing else.
