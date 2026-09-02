# FEAT-51 · fix cycle 2, send-back 1 — the decision record now carries BOTH halves, and it is guarded

**Closed with D-15 (the instruction), T-08 (the guard), a tightened SC-09 (the grade), and D-16
(Q2, RESOLVED).** T-01..T-07, D-01..D-14, SC-01..SC-08, SC-10, SC-11, the REQ set, the lanes table
and Q1 were not touched.

## D-15 — the instruction the documentor actually needs

T-06's `intent:` is immutable and two of its bullets are now wrong: the one saying the boundary is
"refused at the check-domain.sh Write gate on the canonical artifacts", and the one saying the
boundary bites on "the last three" because the `plan.yaml` case is handled by FEAT-41's editor
denial. A documentor following them writes a DEC-209 entry with no `plan-sign-gate.sh` half and an
implicit claim that `plan.yaml` is covered by a denial on a route nobody may use — the exact belief
this cycle overturned.

**D-15 names T-06 and says in so many words that it supersedes those two bullets**, and states the
three claims the entry must carry: the `check-domain.sh` `Write`/`Edit` half on `BRIEF.md`,
`feature.json`, `STATE.md`; the `plan-sign-gate.sh` `PreToolUse` `Bash` half on the four mutating
`plan-merge.py` verbs plus `quarantine.py adopt` and `discard` (D-16); and explicitly that
`plan.yaml`'s only write route is `plan-merge.py` through `Bash`. The documentor reads the
`decisions:` block and the task intent, so a decision naming the task is the only route left.

## T-08 — added, and here is why D-15 alone is not sufficient

**D-15 fixes the instruction; nothing checks whether it was followed.** SC-09 declares
`verify: automated / evidence: integration`, and no assertion in the plan reads the DEC-209 entry's
content: T-06's `verify:` greps `DECISIONS-INDEX.md` for the token `DEC-209`, diffs a regeneration,
and runs `test-gen-decisions-index.py` — all three are green over an entry that omits the Bash half.
T-06's `verify:` and `files:` cannot be edited, so the assertion cannot live in T-06.

T-08 adds two functions to `.claude/skills/harness/bin/test-gen-decisions-index.py` (integration,
already registered — no `run-unit-tests.sh` / `harness.json` change, no `DECISIONS.md` edit, so no
index regeneration is owed). It follows the precedent already in that file at `:829`,
`test_no_amendment_construct_survives_in_the_authority`, which guards the **live** authority rather
than a fixture. Region sliced `## DEC-209` → next `^##\s+DEC-\d+` through the file's own fence
toggle at `:46`; bounded both sides (G-04). One assertion per clause (P-04):
`check-domain.sh`, `plan-sign-gate.sh`, `quarantine.py adopt`, the whole word `Bash`, and one
sentence carrying both `plan.yaml` and `plan-merge.py`. Absent heading ⇒ **FAIL, never skip**.
`depends_on: [T-06]`; lane `team` / `harness-dev-ops` (`--resolve` → `harness-backend-dev`,
`harness-dev-ops`). `change_type: scaffolding` — the deliverable is the guard.

**Baseline, observed at `ad93d43e` from the main checkout:** T-08's `verify:` block run verbatim →
**exit 1**, no output (first grep fails). Its tail conjunct alone,
`python3 .agents/skills/harness/bin/test-gen-decisions-index.py` → **exit 0**, eleven `ok -` lines.
The two greps are therefore the whole discriminator and no earlier conjunct masks them (O-04).

## Q2 — RESOLVED, recorded as D-16: `discard` IS covered

`REQ-05` is untouched either way (`discard` makes nothing canonical), so the question is REQ-04's
remedy. The boundary's promise to the operator is a **recoverable artifact**; an orphan destroying
the only copy of its own result with no wake and no operator act is the same unsupervised-durable-
state harm the feature exists to stop, and leaving it out would read to a later reader as an
oversight rather than a choice.

**It is not "one more verb in the tuple" — that was wrong in my cycle-1 note.** `discard` takes
`--dir`, not `--file`, so D-16 spells the delta: match the `--dir` value, normalise from its last
`.harness/` segment, match
`^\.harness/[^/]+/features/([^/]+)/quarantine/[^/]+/?$`, feature from group 1, refuse on
`orphan_write`, fail OPEN on an unresolvable value exactly as D-13 says for `--file`. Label string
for the new case: `an orphan quarantine.py discard of a quarantine directory is refused`. Refusal
text says discarding is the resumed parent's act, not a path to write instead. D-16 names T-07,
whose intent is immutable and today directs the opposite comment. T-07's `verify:` greps three other
labels and runs the whole suite, so the new case is gated without touching it.

## SC-09, tightened — and what turns it red

It now requires **both** script names, `check-domain.sh` and `plan-sign-gate.sh`, plus one sentence
saying `plan.yaml`'s write route is `plan-merge.py` through `Bash`, and says that resting
`plan.yaml`'s coverage on FEAT-41's editor denial is `not_met`. Shape kept: `verify: automated`,
`evidence: integration`, consistent with SC-11 (which grades the same script by name on the
behavioural side; SC-09 grades the record). **The candidate entry that turns it red:** a DEC-209
entry reproducing T-06's two bullets verbatim — it carries `check-domain.sh`, "the last three", and
FEAT-41's denial for `plan.yaml`, and carries no `plan-sign-gate.sh` token at all. T-08's clause 2
fails on it. No REQ added or reworded.

## Gate output — run from `/Users/molchairuangutai/GitHub/harness/`

- `plan-merge.py apply` → `ADDED D-15`, `ADDED D-16`, `ADDED T-08`, `APPLIED …/plan.yaml`, **exit 0**.
- `check-plan-routes.py <plan.yaml>` → **0 violation(s) across 1 plan(s)**, exit 0. **3 DEVIATION**
  lines, on **T-01, T-02, T-07** — unchanged, the DEC-174 carve-out. `OK T-08 granted to
  harness-backend-dev, harness-dev-ops`.
- `yaml.safe_load` → `YAML_OK`, exit 0; every new scalar tail survives the load (G-12 checked
  before the apply).
- `status: plan` intact · **8/8** tasks `status: ready` · `DEC-208` occurrences **0** · `approval`
  key **absent** before and after · `lanes` 17 rows at `ad93d43e` and the no-approval comment block
  both byte-present after the apply.
- REQ↔task coverage bidirectional and complete: REQ-01 T-05 · REQ-02 T-01,T-06 · REQ-03 T-03,T-05 ·
  REQ-04 T-02,T-03,T-07,**T-08** · REQ-05 T-04,T-06,T-07,**T-08** · REQ-06 T-01,T-05 · REQ-07
  T-02,T-06. Zero tasks trace zero REQs. **8 tasks, 16 decisions, 7 REQs.**

## Open questions

- **Q1 (carried, blocking, not mine):** a plan created by `plan-merge.py apply` can never acquire an
  `approval:` mapping. Untouched, as dispatched.
- **Q2 — CLOSED.** Answered by **D-16**.

Proposal applied: `notes/research-proposal-decision-record-gap-c2.md`.
