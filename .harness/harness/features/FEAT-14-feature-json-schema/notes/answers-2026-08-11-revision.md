# Operator answers — FEAT-14 — the single board vocabulary — 2026-08-11

These supersede the plan where they conflict. Everything not named here stands.

## The ruling

**`phase` and `status` collapse into ONE field, and its values are the GitHub board's columns.**
Not a mapping layer between two vocabularies — a replacement. The old values are used once, as
input to the migration, and no mapping table survives.

```
Backlog → Plan → Ready → Building → Review → Done
```

| Value | Means |
|---|---|
| `Backlog` | filed, not yet planned |
| `Plan` | planning: BRIEF and plan.yaml being authored, not yet signed |
| `Ready` | plan signed, waiting to be dispatched |
| `Building` | build running |
| `Review` | validating, **or waiting on the operator** |
| `Done` | merged and closed, **or abandoned** |

**Two states fold in, by the operator's explicit call.** `awaiting_user` → `Review`, and
`abandoned` → `Done`. The cost was named and accepted: `Review` cannot distinguish "the panel is
running" from "waiting on Mike", and `Done` cannot distinguish shipped from given up on. One
feature is affected by the second — FEAT-01 — so the loss is one record.

**`ship` folds into `Review` too.** The ship phase is built-validated-and-waiting-on-you; it begins
before the PR and before the merge, so it is not `Done`. `Done` stays honest: merged and closed,
which is also what the board's auto-close workflow writes.

## Why this replaces the plan rather than amending it

The plan carries `phase` AND `status` as separate schema keys, pins `phase` to
`check-state.sh:437`'s `PHASE_ORDER = ["plan", "build", "validate", "ship"]`, and adds a test
asserting the two stay equal as sets. **That test now has nothing to pin, and `PHASE_ORDER` becomes
dead.** The schema is a different schema and the migration is a different migration.

## What this ADDS that the plan does not have

**`check-plan-routes.py:386` must change in this feature.**

```python
SHIPPED_STATUSES = ("shipped", "abandoned")
```

Neither value will exist. Its own documented rule is that a feature it cannot classify is **checked
rather than skipped**, so left alone every finished feature is route-checked forever. This is a
REQUIRED CI gate silently changing what it examines, which is exactly the class of defect this
project keeps finding, so it needs a task and a criterion rather than a follow-up.

The new equivalent is `Done`. Note the collapse means an abandoned feature is also `Done`, which is
the behaviour that tuple already had — it skipped both.

## Verified facts, so pm does not re-derive them

Measured 2026-08-11.

- **Both boards already carry the six-value vocabulary.** The board work is DONE, ahead of the plan,
  and verified by counting items per column before and after rather than by trusting the mutation:

  | Board | Before | After |
  |---|---|---|
  | 3 Harness | Backlog 88, Ready 5, Done 111 — **204** | unchanged, plus `Plan` — **204** |
  | 2 kaya-ai | Todo 82, In Progress 11, Done 118 — **211** | Backlog 82, Building 11, Done 118 — **211** |

  Zero item writes: renaming a single-select option preserves assignment. Every pre-existing option
  id was re-sent unchanged, because `updateProjectV2Field` REPLACES the whole list and an omitted
  option deletes it and strands its items.
- **`Plan` is a new option** — `cf630356` on board 3, `51284156` on board 2 — placed between
  `Backlog` and `Ready`.
- **SPEC §11.3 is already violated by the corpus today.** It declares four values; the 17 features
  carry seven: `in_progress`, `in_review`, `shipped`, `abandoned`, `shipping`, `complete`,
  `awaiting_user`. So this is not four-versus-six — it is which set gets ENFORCED, and every value
  the schema rejects is a file someone must edit.
- **The corpus is 17 features, not the 12 the plan measured.** T-04 and T-08 already resolve it by
  glob at build time, so this needs no plan change — recorded so nobody re-hardcodes a count.
- **CI does not assert a specific plan count.** The workflow asserts the count is NOT ZERO, a guard
  against a checker that runs and looks at nothing. So features moving out of the route check's set
  does not redden CI.
- `jsonschema` **4.26.0 is installed** to the user site-packages. Q4 is discharged.

## Still binding, unchanged

- **The enforcement point is signed:** an importable `bin/feature_schema.py` that `check-domain.sh`
  imports IN PROCESS and LAZILY, inside the `feature.json` branch only. Measured: a module-level
  import costs +42.6 ms against a 17.3 ms bare interpreter, so it is deferred and other writes pay
  nothing. This does not widen the DEC-174 carve-out, which already names four scripts.
- **The build precondition is a WAIT, not a decision.** FEAT-16 and FEAT-17 are `in_progress` and
  writing `feature.yaml` live. The migration runs when both have returned for signature. No feature
  may cross from signature into build during the migration.
- The burden of proof stays on KEEPING a field. The 41 keys measured as unread die without further
  argument.
- Prose still has named destinations rather than a `notes:` drawer: operator rulings →
  `plan.yaml approval.rulings`; run narrative → that run's digest; current state and open questions
  → `STATE.md`; measurements and receipts → `notes/`.

## Loose ends to tidy in the same pass

- **SC-07's prose says "exits non-zero" where its own test asserts exit EXACTLY 3.** The mechanical
  assertion is correct so nothing ships wrong; tighten the wording.
- `check-state.sh`'s `PHASE_ORDER` becomes dead with `phase`. Remove it, or say why it survives.

---

# SIGNATURE — 2026-08-11 — the three rulings taken at approval

**1. FEAT-15 migrates to `Plan`, not `Review`.** Its plan is unsigned and it holds zero handoff
notes, so `Review` would assert seams it never crossed. Dry-run measured **0 INV-17 violations at
`Plan`, 2 at `Review`**. It is the only one of six `awaiting_user` features that departs, and it
departs by the same general rule rather than as an exception.

**2. `cycles_used` stays 3.** DEC-157's test is mechanical — a FAIL routed back, an unmet-SC
re-dispatch, or a lead-reported send-back — and an operator re-spec of an UNSIGNED plan is none of
the three. Zero send-backs were reported. Seven cycles remain for a build whose fix loops are real.

**3. The `handoff-validate.md` seam moves to `Done`, accepted, with NO second mechanism added.**

Because `Review` absorbs both validate and ship, the checker cannot tell which a feature is in, so
demanding `handoff-validate.md` at `Review` would demand it of a feature that just STARTED
validating. The demand therefore lands at `Done`.

**Measured before accepting, rather than assumed.** All **ten** features that reached `ship` carry
all three handoff notes — none missing. FEAT-06 at `validate` correctly has plan and build and not
validate. So the note is produced reliably by the validate close-out; **INV-17 has never been what
CAUSES it**, only the backstop that catches a flow which skipped it.

| | Before | After |
|---|---|---|
| Who writes it, and when | validate close-out, at the validate→ship seam | **unchanged** |
| When it is CHECKED | on entering `ship` | on entering `Done` |
| Cost of a miss | caught before the ship decision | caught after the merge |

**No second enforcement point is added.** That would be the two-copies drift this schema exists to
remove. `Done` still demands the note, so a feature cannot finish without it, and the run digest's
`files_touched` shows it at the moment it is written. **If the check-at-`Done` ever fires, that is
the signal to revisit** — and it firing would be the first time in seventeen features.

The `handoff-build.md` demand at `Review` is UNCHANGED. Nothing was lost at the build→validate seam.

---

# CORRECTION — 2026-08-11 — ruling 1 was wrong, and it hid a general defect

**Ruling 1 above is WITHDRAWN.** It said FEAT-15 migrates to `Plan` because "its plan is
approval:pending and it holds zero handoff notes." Both halves were read off a STALE file.

**Measured at `a29ad06`:**

| | `feature.yaml` says | Actually true |
|---|---|---|
| status | `awaiting_user` | signed, built, panel-reviewed PASS |
| phase | `plan` | **PR #263 MERGED, issue #239 CLOSED** |

FEAT-15 shipped. `plan.yaml` reads `approval: approved`. Migrating it to `Plan` would record a
merged feature as being planned, and the one field meant to mirror the board would disagree with
the board on its first day.

**FEAT-15 migrates to `Done`.**

## The defect the stale value was hiding

FEAT-15 has **zero handoff notes, and that is CORRECT**. All five of its tasks are
`execution_mode: main-session-direct` under DEC-174 — `check-domain.sh` is a carve-out file, so no
squad ran, no seam was ever crossed, and no handoff note was ever owed.

**INV-17 demands the notes of every prior state with no exemption for execution mode.** So placing
FEAT-15 at `Done` raises three violations for notes that should never have existed. The dry-run
that measured "0 violations at `Plan`" was measuring the stale value being conveniently early, not
correctness.

**This generalises and will recur.** Every DEC-174 carve-out feature — anything touching
`check-domain.sh`, `bash-write-guard.sh`, `validate-digest.py` or `check-state.sh` — is built
main-session-direct and produces no handoff notes. FEAT-15 is the first. **FEAT-17 is already
planned as main-session-direct and will be the second.**

Measured now: FEAT-15 is the only feature today whose tasks are ALL main-session-direct. FEAT-01,
FEAT-02, FEAT-15, FEAT-16 and FEAT-17 currently hold zero handoff notes — the last two because they
are still planning.

## What FEAT-14 must add

**INV-17 gains an exemption: a feature whose tasks are all `main-session-direct` owes no handoff
notes.** No squad, no seam, no note.

Two things this must NOT become:

1. **Not a blanket skip for missing notes.** The exemption keys on the PLAN's execution modes, not
   on the notes' absence — otherwise INV-17 is satisfied by the very condition it exists to detect,
   which is the vacuous-gate shape this project keeps finding.
2. **Not silent.** A feature exempted must be REPORTED as exempted with its reason, so an exemption
   granted wrongly is visible rather than looking like a pass.

The criterion needs both directions from one fixture: an all-main-session-direct feature with no
notes does NOT violate, and a squad-built feature with a missing note still DOES.
