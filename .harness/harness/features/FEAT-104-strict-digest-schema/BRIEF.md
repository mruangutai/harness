# BRIEF — FEAT-104 Strict digest and step schemas

## Problem

`validate-digest.py` silently ignores any key it does not know, and nothing at all inspects the
inside of a run `state.yaml` `steps[]` entry. Measured at the owner root on **2026-09-09**
(`notes/research-FEAT-104-triage-c0.md`): **65** distinct out-of-schema digest keys across 220 of
319 readable digests (69%), and **202** distinct `steps[]` keys across 356 runs, 132 of them
invented once and never used again — including **7 that are prose sentences used as mapping keys**.
Five weeks earlier issue #104 measured 8 and 95. The contract is not weakly enforced; below the
top level it is not enforced at all, so a typo, a deleted field (`cost`, DEC-178) and a genuinely
load-bearing signal (`adequacy_notes`, #37) are indistinguishable to every reader.

## Goal

Make the digest schema and the nested `steps[]` schema strict: a new return or a new write that
carries an undeclared key is **rejected with an actionable repair**, while every key in legitimate
use today keeps a declared home — including a governed, free-form-inside container for the per-step
evidence a dying orchestrator must not lose. Historical run artifacts stay readable and unrewritten.
`adequacy_notes` (#37) enters the contract in this feature, not after it.

## Requirements

- REQ-01: A new digest return carrying a key outside the contract for its persona is rejected, not
  ignored, at every schema tier `validate-digest.py` enforces.
- REQ-02: A new write to a run `state.yaml` whose `steps[]` entry carries a key outside the declared
  step shape is rejected, and no new run can place itself outside that rejection — creating a run
  `state.yaml` below the enforcement floor is refused. The rejection therefore binds every run
  written after the change, not only the ones that opt in.
- REQ-03: Per-step durable evidence has a declared container — governed shape, free-form contents —
  so recording it does not require inventing a key or holding it in a context that can vanish.
- REQ-04: Every key in legitimate use at the time of the change still validates; no legitimate
  return or write becomes newly rejected. "Legitimate use" is fixed by what each persona's own
  documented output block instructs, never by what observed traffic happened to contain.
- REQ-05: A rejection is immediately actionable: it names every offending key and the route by which
  a legitimate one is declared.
- REQ-06: Re-prompt behaviour is settled and written down, so strictness having exactly one shot per
  return is a decision rather than an accident.
- REQ-07: `adequacy_notes` is part of the enforced contract with a decided scope, closing #37.
- REQ-08: Historical run digests and checkpoints remain readable and are not rewritten; enforcement
  binds new returns and new writes only.
- REQ-09: A persona's documented output block and the contract declared for it agree, and the
  agreement is checked mechanically rather than by review — a field that one states and the other
  omits is found by running something, not by the next reader noticing.

## Success Criteria

- SC-01: A `lead` return that is otherwise valid but carries `foo_bar: 1` exits 2, and stderr names
  `foo_bar`. Before the change the same return exits 0.
  verify: automated      evidence: integration
- SC-02: The same rejection holds for **each** persona key in `validate-digest.py`'s `SCHEMAS`
  (`pm`, `dev`, `qa`, `reviewer`, `visual-designer`, `documentor`, `dev-ops`, `lead`,
  `orchestrator`) — one case per persona, each asserted separately, not a single global count. Each
  persona's *accepting* fixture carries its documented block's **full** field set, built from that
  block rather than hand-written: a minimal valid payload omits the 16 documented fields and is
  precisely what made this defect invisible in cycle 0.
  verify: automated      evidence: integration
- SC-03: `check-domain.sh` refuses a run `state.yaml` Write whose `steps[]` entry carries an
  undeclared key at `schema_version: 2`, and the refusal names that key.
  verify: automated      evidence: integration
- SC-04: A `steps[]` entry carrying `evidence:` with arbitrary identifier keys is accepted; the same
  entry with a non-identifier key inside `evidence:` (a key containing a space) is refused. Both
  directions asserted.
  verify: automated      evidence: integration
- SC-05: Every field a persona's DOCUMENTED output block instructs still validates — the 16
  documented-but-previously-undeclared fields, enumerated per persona with `file:line` in
  `notes/research-FEAT-104-planfix-c1.md`, plus `adequacy_notes` and each of the eight
  `PASSTHROUGH` rows on a lead return, plus each of the 21 step-schema keys and `evidence:` on a
  `schema_version: 2` write. One assertion per key, never a matching count. The grading set is the
  documented blocks under `.omp/agents/` and the two shared skill blocks — never this plan's own
  triage output, which measured lead returns only and so could not fail on a key it never saw.
  verify: automated      evidence: integration
- SC-06: The rejection half of the suite is red against the pre-change validator: copy
  `git show <base>:.claude/skills/harness/bin/validate-digest.py` into a temp tree beside its
  siblings and run the suite's unknown-key cases against it; they must fail. `<base>` is the
  absolute 40-character commit id T-01 records in `notes/base-revision-pre-T-04.txt`, never a
  relative ref, and the case re-derives both sides of the pin before using it: that blob contains
  `DOCUMENTED_OPTIONAL`, so T-01 is in it, and does not contain `undeclared digest key`, so T-04
  is not. An allow-only suite is insufficient because it passes unchanged against a validator that
  rejects nothing — exactly how issue #103's gap survived a green suite.
  verify: automated      evidence: integration
- SC-07: A return carrying three unknown keys produces **one** rejection naming all three, so the
  single re-prompt shot is sufficient; a message naming only the first is a failure.
  verify: automated      evidence: integration
- SC-08: The rejection text names the declaration route by file and symbol —
  `validate-digest.py` `SCHEMAS`/`PASSTHROUGH` for a digest key, the step-schema symbol for a step
  key — asserted as a substring, not merely non-empty.
  verify: automated      evidence: integration
- SC-09: With `stop_hook_active` set, the three-unknown-key return of SC-07 exits 0, pinning the
  one-shot property as deliberate rather than latent. This is a pin, not new behaviour, and it
  still discriminates: the plausible wrong implementation is T-04 placing the key check *before*
  the guard at `validate-digest.py:1744`, which reddens it.
  verify: automated      evidence: integration
- SC-10: `SCHEMAS["lead"]` requires `adequacy_notes`, and `run_documented_contract_cases` passes —
  i.e. `.claude/skills/harness-team/SKILL.md`'s lead block documents it (DEC-216). Omitting the
  documentation must redden the suite.
  verify: automated      evidence: integration
- SC-11: A `steps[]` entry carrying an undeclared key is **accepted** when the file declares
  `schema_version: 1` and **refused** at `schema_version: 2`. This is what makes REQ-08 true by
  construction rather than by promise.
  verify: automated      evidence: integration
- SC-12: No historical run artifact is modified by this feature — and the check can go RED. T-10
  records a `<sha256>  <path>` manifest of every run artifact under the owner root's
  `.harness/harness/features/*/runs/` — 726 files (356 `state.yaml` + 370 `digest.md`, measured
  2026-09-09) — into
  `.harness/harness/features/FEAT-104-strict-digest-schema/notes/run-artifact-manifest-base.txt`,
  before T-01. At ship, T-10's `verify:` command re-run at the owner root recomputes each
  manifested path's sha256 and exits 0. It exits 1 on any manifested file whose bytes changed or
  that vanished, and on a truncated manifest (`assert 726 <= n`). A path on disk but ABSENT from
  the manifest is ignored, so runs that other features write into that same tree concurrently
  cannot redden it. The cycle-0 form of this criterion was vacuous — see
  `notes/research-FEAT-104-triage-c0.md`,
  `## Cycle 1`. Discrimination is demonstrated, never asserted: the same command, given a copy of
  the manifest with one hexdigest character altered, must exit 1 naming that path. The default
  baseline path is worktree-scoped, and that is **accepted**: this criterion is graded inside the
  ship-decision window, while the worktree stands. A post-merge re-run passes the owner-root path
  of the baseline as `argv[1]`; the file is tracked and merges to `main`, so the pin outlives the
  worktree even though the default does not.
  verify: inspection
- SC-13: The operator reads the diff of the four carve-out files (`validate-digest.py`,
  `check-domain.sh`, `check-state.sh` and their tests) and confirms it changes nothing beyond the
  declared contract — DEC-174 requires a human to read this diff, and no automated gate substitutes.
  verify: uat
- SC-15: Creating a run `state.yaml` that declares `schema_version: 1`, that omits it, or that
  spells it as the string `"2"` is refused and the message names the floor; creating one at
  `schema_version: 2` is accepted; and a Write to an already-existing `schema_version: 1` file is
  accepted. Four fixtures, asserted separately — the last is the one that reddens if the floor is
  keyed on the write rather than on the creation, which would rewrite history's writability.
  verify: automated      evidence: integration
- SC-16: For every persona in `CONTRACT_SOURCES`
  (`tests/integration/test-validate-digest.py:297-314`), every key its documented DIGEST block
  instructs is a member of the legal set the validator computes for that persona — one assertion
  per persona, and the failure names the persona, the key and the source path. Discrimination is
  demonstrated, not asserted: with one `DOCUMENTED_OPTIONAL` row removed in-process, the case must
  fail naming that field. This is the criterion that would have caught the cycle-0 defect.
  verify: automated      evidence: integration

## Verification gaps

`test_kinds` in `.harness/harness.json` has runners for `unit` and `integration`; every `automated`
criterion above rests on `integration`, which runs. The null-`cmd` kinds (`functional`, `component`,
`ui`, `eval`, `typecheck`) cover surfaces this feature does not touch, so no criterion routes around
a missing runner.

## Constraints

- **DEC-174 (blocks):** `validate-digest.py`, `check-domain.sh`, `check-state.sh` and each gate's own
  tests are never executed-against by a harness run. Every task touching them is a declared
  `main-session-direct` step.
- **DEC-179 (supplies):** routing for every literal `files:` path is resolved at plan time by
  `check-domain.sh --resolve`; the agent templates and skills resolve to `NOBODY`, which is a
  declared main-session step, not a failure.
- **DEC-121 (blocks):** a field in `SCHEMAS` is required and must be said with an explicit `[]`.
  That is why the passthrough table is separate and optional.
- **DEC-216 (blocks):** a field required of a persona must appear in that persona's documented
  output block; for the three leads that block is `.claude/skills/harness-team/SKILL.md`.
- **DEC-191 (supplies the precedent, and one distinction):** `additionalProperties: false` over a
  closed key set, enforced on `check-domain.sh`'s write-payload path. Its refusal of a free-form
  drawer applies to `feature.json`, a permanent machine-read record; the step `evidence:` container
  is distinguished in `notes/research-FEAT-104-triage-c0.md`.
- **DEC-154 / DEC-160 (supply):** the checkpoint discipline and the existing top-level whitelist —
  this feature extends the same seam one level down, it does not open a second one.
- **DEC-208 (supplies):** the `stop_hook_active` passthrough is pre-existing and deliberate; this
  feature does not close it and answers it with a one-shot-sufficient message instead.
- **DEC-205 (supplies):** `DECISIONS.md` states current truth, so T-09 CORRECTS the one clause of
  DEC-126's Applied record that D-03 falsifies (`DECISIONS.md:2612-2613`, `adequacy_notes` named as
  the validator lead's per-role extra) instead of leaving it standing. Correcting a falsified clause
  is not the amendment-as-changelog DEC-205 forbids. **This plan touches the decision record.**
- **DEC-173 (supplies):** `NULLABLE` is the single spelling for an inapplicable scalar, so the
  visual designer's documented `prototype: <path|none>` uses it rather than a second mechanism.
- **`.omp/agents/` is the source of record (supplies):** `.claude/agents/*.md` is GENERATED from it
  by `sync-agent-adapters.py`, which copies the body wholesale — every agent-file edit in this plan
  edits the `.omp/` file and regenerates.
- **Out of scope, chosen by the operator (intake artifact, 2026-09-09):** rewriting historical run
  digests or checkpoints, and folding this into FEAT-08.
- **#44 is not in scope.** Verifying `severity_max` against `findings` becomes possible once the
  field is a declared typed passthrough; it is named as a downstream unblock, nothing more.

## Approval

status: pending
