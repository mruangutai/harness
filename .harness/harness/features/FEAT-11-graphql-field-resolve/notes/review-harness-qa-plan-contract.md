# QA plan-contract review — FEAT-11 GraphQL field resolve

**BLUF: the plan is buildable and its verify command is mostly discriminating, but it has one real
gate hole (the `git diff --quiet HEAD` clause is vacuous once the build agent commits) and one
matrix hole (SC-09's `integration` evidence is not bound by the matrix for `change_type: bugfix`).
The over-scope guard's defeater I was asked to try DOES defeat every textual clause, but it does
NOT defeat the cost property the guard exists to protect — measured delta ≈ 1 at N up to 300
aliases. SC-05/SC-10 are honest about being derived/stub-only; I could not find a live org
counter-example in three tries.**

## SHA integrity check — clean

`835b2976` exists, equals `git rev-parse HEAD`, and `git diff --stat 835b2976 -- factory_gh.py
test-factory-gh.py test-factory-integration.py` is empty. No drift; every line anchor in plan.yaml
and the probe note is against the tree I read. No process finding here.

## Q1 — the 14 verify clauses, reachability and vacuity

Traced each against the probe note's measured baselines (taken as given, not re-derived, since the
SHA check confirms the tree hasn't moved):

| # | Clause | Baseline today | Target | Vacuous? |
|---|---|---|---|---|
| 1 | `run-unit-tests.sh --kind unit` | n/a | green | no |
| 2 | `test-factory-integration.py` direct | n/a | green | no |
| 3 | quoted `"field-list"` in integration test = 0 | 1 | 0 | no, discriminates 1→0 |
| 4 | quoted `"project", "view"` in integration test = 0 | 1 | 0 | no |
| 5 | quoted `"field-list"` in factory_gh.py = 0 | 1 | 0 | no |
| 6 | quoted `"project", "view"` in factory_gh.py = 0 | 1 | 0 | no |
| 7 | `factory_gh._FIELD_QUERY` imports | doesn't exist today | exists | no — gates 8-12 |
| 8 | `field(name:` present ≥1 | n/a (gated by 7) | ≥1 | no |
| 9 | `fields(` absent | n/a | 0 | no as a literal grep, but **see Q2 — the property it's meant to stand for is defeatable** |
| 10 | `(first|last):` absent | n/a | 0 | no as a literal grep, **same caveat** |
| 11 | `user(login:` absent | n/a | 0 | no |
| 12 | `repositoryOwner(login:` = 1 | n/a | 1 | no |
| 13 | `git diff --quiet HEAD -- <3 files>` | n/a | no diff | **YES, see (a) below — vacuous once committed** |
| 14 | `echo PASS` | n/a | n/a | trivial |

No clause is a `grep -c ... = 0` over a string the file never contained (the DEC-169 vacuity
pattern) except clause 13, which is vacuous for a different reason (timing, not string absence).

### (a) `git diff --quiet HEAD` — confirmed vacuous once the edit is committed

Empirically demonstrated in a disposable scratch repo (not this repo): committed a change to a
tracked file, then ran `git diff --quiet HEAD -- <file>` → **exit 0** (no diff — the clause reads
this as "unedited" and does not fire), while `git diff --quiet <pre-edit-SHA> -- <file>` → **exit 1**
(correctly detects the change). `git diff HEAD` compares the working tree to the current tip, and a
commit moves the tip to include the edit, so the comparison becomes self-referential the moment the
agent commits before running verify. The clause as written discriminates **only a dirty working
tree**, not "was this file touched relative to the pinned baseline." Remedy is exactly what the
dispatch names: diff against the pinned `review_sha` (or the lane's `resolved_at`,
`c1d161706ab4867c00078b966e1969203ee6ca92`), never `HEAD`.
Severity: **med** — this is the sole enforcement of SC-08 (frozen public signatures), and it is
bypassable by ordinary commit-before-verify sequencing, not by malice.

### (b) shell mechanics — confirmed sound

`set -o pipefail` with no `-e`: every risky command in this script is either inside `$(...)`
(command substitution captures stdout regardless of the substituted command's own exit status) or
guarded by its own `||`. None of the risky commands sit in a literal `cmd1 | cmd2` pipeline at the
top level (the `printf | grep` pairs are themselves inside `$(...)`, so their exit status is never
examined either) — `pipefail` is present but inert here, and harmlessly so. `grep -c` exiting 1 on a
zero count does not abort the script anywhere. Confirmed by construction (traced each of the 14
lines), consistent with the probe note's own claim to have tested this.

BSD grep / POSIX bracket classes: probe note lines 68-89 report this measured directly on this
machine against the actual `repositoryOwner` document (not `\s`/`\b`, which the note flags as
unreliable on Darwin — and the shell clauses correctly avoid both, using `[[:space:]]` throughout).
I re-verified the three POSIX-class clauses (8/9/10) mechanically against the intended document and
a decoy in Q2 below; they behave exactly as the probe note states.

## Q2 — THE HIGHEST-VALUE ITEM: aliased-repetition defeats the guard text, but not its cost

**Mechanical result: yes, the candidate shape defeats all five constant-guard clauses (8-12) and
all three Part B unit regexes.** Verified directly — built the document, ran the actual grep/regex
patterns from plan.yaml against it:

```
clause8  field(name: …  → 3 matches (≥1: pass)
clause9  fields(        → 0 (pass)
clause10 (first|last):  → 0 (pass)
clause11 user(login:    → 0 (pass)
clause12 repositoryOwner(login: → 1 (pass)
Python re: field(name: present=True, fields( present=False, first/last present=False
```

Every textual guard in the plan passes on `p1: projectV2(number: 1){...} p2: projectV2(number:
2){...} ... p20: ...` — the aliased-repetition-of-a-single-node-field shape the dispatch names.

**Costed it, read-only, against `mruangutai` board 3, field `Status` (a board that resolves):**

| N aliases | `graphql.used` before | after | delta |
|---|---|---|---|
| 20 | 18 | 19 | **1** |
| 100 | 19 | 20 | **1** |
| 300 | 20 | 21 | **1** |

All three requests returned exit 0 with every alias's data populated (no node/complexity rejection
at any of the three sizes tested). Delta does **not** scale with N — flat at 1 from 20 through 300
aliases.

**Interpretation, per the dispatch's own framing: delta ≈ 1 and flat → SC-03's *structural* claim
("a selection set with no connection argument cannot fan out") is overstated as written — this
shape has no connection argument and does fan out structurally (20-300 repeated object selections)
— but the *guard is nonetheless cost-adequate*: the actual property BRIEF and SC-01 care about
(GraphQL point cost) is not defeated by this shape at any N tested. Severity: low/info**, matching
the dispatch's own predicted low branch. I would not add a guard clause for this — it would cost a
maintenance burden (yet another regex) for zero measured cost benefit, per the dispatch's own
instruction not to invite that trade blind. Worth one line in DESIGN.md/SC-03 softening "cannot fan
out" to "cannot fan out at cost" if the team wants the prose to match the measurement, but that is
advisory, not a build blocker.

**Explicit answer to "did you find a shape that defeats the guards, and what did it cost":** yes, a
mechanical defeat exists (aliased repetition of `projectV2(number: N)` under 20+ distinct aliases);
its measured cost is flat at 1 GraphQL point through N=300, i.e., it does not defeat the cost
property. This is a clean, measured result, not a hedge.

## Q3 — do the two frozen error paths survive?

**(a) No clause anywhere checks byte-identity of the frozen `next_step` strings — confirmed.**
Read `test-factory-gh.py`'s current field/option-not-offered cases (`:274-279`, `:459-464`): both
assert only a **value substring** (`"NotAnOption" in str(exc)`, `"NoSuchField" in str(exc)`), never
the `next_step` wording D-04 freezes. Plan.yaml's Part B rewrite instruction for the option case
(`:279-280`) says only "keep the behaviour assertion," which is this same substring pattern — it
does not ask for a byte-literal check. None of the 14 verify clauses touches `next_step` text
either (clauses 3-6 grep for the deleted-call tokens, not the frozen wording). **A dev could reword
either frozen string and the entire suite, including this task's verify, stays green.** This
directly confirms your reading. Severity: **med** — D-04 records the freeze as a decision precisely
because operators learn the string and the reword is hard to reverse, but nothing in the test
matrix or the task verify enforces it going forward.

**(b) The `Redy` case does NOT exercise `factory_gh.py:251-262` — confirmed, contradicting the
grilling's fact list, agreeing with the eng-lead's Q4 note.** `test-factory-decompose.py:121-125`
(`PATCHED`) includes `"project_field_options"`; `patch_gh` (`:128-132`) replaces
`factory_gh.project_field_options` with `Recorder.project_field_options`
(`:112-114`, returns `list(self.field_options)` — a fixture list, not a call into the real
module). The `Redy` case at `:1025-1048` runs through this patched recorder and asserts on
`err` (stderr), which is built by `_validate_stations` in `factory_decompose.py`, not by any
string `factory_gh.py` produces. **The real `factory_gh.py:251-262` code is never reached by this
test.** State this plainly per your instruction: the grilling's "Facts I verified" claim that this
test depends on `factory_gh.py:251-262` is wrong; the eng-lead's contrary note (architecture-review
Q4) is the one that holds up under direct reading.

**Last remaining executable proof of the option-not-offered wording:** `test-factory-gh.py`'s
rewritten `:269-280` case (Part B) is the only test anywhere in the tree that calls the real
`project_field_set` with an unoffered option — and, per (a), it only proves the **value** is
named, not that the frozen `next_step` bytes match D-04. `test-factory-integration.py` never drives
this case at all (grepped for "not offered"/"does not offer" — zero hits). So after the rewrite,
D-04's freeze rests entirely on human review of the diff, not on any automated check.

## Q4 — `change_type: bugfix` matrix

`harness.json` `test_matrix.bugfix`: `"always": ["unit"]`, `"when": [{"kind": "__bug_class__", "if":
"match_bug_class"}]` verbatim. `__bug_class__` is a **judgment placeholder that resolves to no
concrete `test_kinds` entry** (confirmed via DECISIONS.md ~line 5447: "a predicate placeholder that
exists in no `test_kinds` and can therefore never resolve" mechanically — it is qa's judgment call
at gate time, not an automatic binding). `run-unit-tests.sh:17-18` confirms
`test-factory-integration.py` is in `INTEGRATION_SCRIPTS`, absent from `UNIT_SCRIPTS`; `--kind
unit` does not run it.

**This is the actual state, confirmed:** the bugfix matrix mechanically requires only `unit`.
SC-09's `evidence: integration` is carried **solely by T-01's own task-local verify command**
(the explicit second line), not by any matrix binding that would re-fire on a later, unrelated edit
to `test-factory-integration.py` or to the code path it exercises. If a future qa run judges
`match_bug_class` to apply to a later change touching this same code, it would add `integration`
back — but that is a per-run judgment call, not a standing gate. **Also confirmed: yes, the qa gate
at build time, mechanically applying the matrix for `change_type: bugfix` with no invoked judgment
extension, runs `--kind unit` only and would report green on a tree where `test-factory-integration.py`
is red**, because that file is never in the unit run's scope.
Severity: **med** — this is a known, designed feature of the harness (DEC-35's judgment-predicate
scheme), not a defect unique to this plan, but it is a real coverage gap this plan's own SC-09
inherits: once T-01 closes, nothing *mechanical* re-runs `test-factory-integration.py` against a
later regression in this code path unless a future qa agent's judgment call brings it back in.

## Q5 — are SC-05/SC-10 honest about what they prove?

Judged against BRIEF's own `## Verification gaps` (BRIEF.md:126-144), which already states this
plainly and does not oversell: SC-05(a) is measured (org, unreachable board, exit 1); SC-05(b) is
**derived**, never observed — no reachable org-owned board exists from this account. SC-10's
negative clause (never contains `"api graphql"`) is stub-only because provoking a genuine transport
failure requires breaking auth, which is out of bounds here.

What each **does** honestly prove even on a derived/stub envelope: SC-05(b) proves the
implementation's org-check does not live only inside `except GhError` — i.e., it distinguishes
reading-before-projectV2 from reading-only-on-failure, which is the actual dead-branch defect class
(D-03) the fixture targets, independent of whether the envelope's exact JSON shape is exactly
right. SC-10's negative clause proves the transport-failure branch does not fall through to
`_value_from_argv`'s generic `"api graphql"` fallback — a property of the code's control flow, not
of GitHub's real behaviour. Both are honestly framed as "this discriminates a control-flow shape,"
not "this proves gh's real response." BRIEF says this already; I found no overselling to flag.

**Timeboxed live attempt (3 tries, as instructed):** probed `github`, `cli`, `vercel` at
`projectV2(number: 1)` read-only — all three organizations exist and are readable, but none has a
board reachable at that number (`NOT_FOUND`, exit 1, same shape as the already-measured case 4).
**Could not find a public org-owned board reachable from this account in three tries.** Stopping
here per instruction; SC-05(b) remains derived, not observed.

## must_fix (severity-tagged)

- **plan.yaml:77** — the `git diff --quiet HEAD -- test-factory-decompose.py test-factory-claim.py
  test-factory-land.py` clause is vacuous once the build agent commits before running verify
  (empirically demonstrated). Diff against the pinned SHA (`review_sha` or
  `c1d161706ab4867c00078b966e1969203ee6ca92`), never `HEAD`. **med**.
- **plan.yaml Part B (`:269-280`, `:446-463`) / BRIEF.md SC-04** — D-04's byte-identical freeze on
  the two `next_step` strings has no automated enforcement anywhere in the tree; only a value
  substring is asserted. A future reword of either frozen string ships green. **med**.
- **`.harness/harness.json` `test_matrix.bugfix` / plan.yaml T-01** — SC-09's `evidence: integration`
  is carried by task-local verify only; the matrix does not mechanically bind `integration` for
  `change_type: bugfix`, so a build-time qa run applying only the "always" kinds is green on a red
  `test-factory-integration.py`. This is the harness's designed judgment-predicate behaviour
  (DEC-35), not unique to this plan, but SC-09 should say so explicitly rather than implying matrix
  coverage. **med**.
- **Q2 defeat shape** — mechanical, not a blocker: aliased-repetition of `projectV2(number:)` under
  distinct aliases passes all 8 textual guard clauses but costs a flat 1 GraphQL point through
  N=300 (measured). SC-03's prose ("cannot fan out") is technically imprecise for this shape; the
  cost property the feature actually needs is not defeated. **low/info** — no guard clause change
  recommended.

## SC evidence map (for pm's goal-check, once built)

- SC-02: `test-factory-gh.py` rewritten `:255-267`+`:282-306` cases (two-call assertion; dispatching
  fake on `("api","graphql")`) plus verify clauses 3-6.
- SC-03: verify clauses 8-12 (constant-level) + Part B over-scope-guard regex block (emitted-argv
  level). Both present; both defeated by the Q2 shape at the textual layer only, not at cost.
- SC-04: `test-factory-gh.py` rewritten field/option-not-offered cases — proves the value slot, not
  the byte-frozen wording (see Q3a gap).
- SC-05: `test-factory-gh.py` new org cases (both fixtures, per plan.yaml Part B "ADD FOUR NEW
  CASES"). Stub-only, as BRIEF discloses.
- SC-06: new board-absent case, same block.
- SC-07: implicit across every new-case assertion of "zero item-edit calls."
- SC-08: `test-factory-decompose.py`, `test-factory-claim.py`, `test-factory-land.py` passing
  unedited — gated by the now-flagged `git diff --quiet HEAD` clause (Q1a).
- SC-09: `test-factory-integration.py` run directly by the task verify (not by the matrix — Q4).
- SC-10: the rewritten `:309-328` transport-failure case + the "never contains api graphql" clause
  across every new case. Stub-only, as BRIEF discloses.
- SC-11: the unknown-owner new case.
- SC-12: the not-single-select (`field: {}`) new case, explicitly required by M-4/architecture
  review and present in plan.yaml Part B.
- SC-01: `verify: uat`, not in this plan review's scope — correctly excluded from automated
  evidence per BRIEF.

## cycles_used: 0
