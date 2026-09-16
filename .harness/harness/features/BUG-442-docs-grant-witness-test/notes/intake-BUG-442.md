# Intake — BUG-442 — the operator's stated intent

This flow received no grilling or wayfinding artifact. This note IS the stated-intent
record handed through the plan door: GitHub issue #442 plus the operator's dispatch,
verbatim, plus what the orchestrator verified on disk before planning.

## The operator's words

GitHub issue #442 (body, in full):

> Residual finding from FEAT-22-docs-layout-migration, accepted at the ship briefing.
> The docs grant is correct but pinned by nothing — a witness test needs both a
> repointable root and an exhaustive assertion.

The dispatch's own statement of what a fix must do (verbatim, and this is the
acceptance the plan is graded against):

> Plan a fix: rework this test (or add a new one) so it (a) loads team-config.yaml
> through the same repointable MANIFEST_PATH mechanism the file already uses elsewhere
> rather than hand-copied literals, and (b) asserts EXHAUSTIVELY over every one of the
> 16 personas' docs-domain grant status (not just 6), so a future addition or removal
> of a docs grant on ANY persona is caught.

Note the two-sided shape of (b): **addition OR removal**. A witness that only proves
"documentor still holds it" satisfies half the sentence.

## What the orchestrator verified itself, at 6d969ed3

Method named per claim; nothing below is relayed on trust.

- `.harness/*/docs/**` is granted in **exactly one** place in the manifest —
  `harness-documentor`, `.harness/team-config.yaml:144`. Method: Grep for `docs/\*\*`
  across the manifest; two hits, both on documentor's row (`docs/**` at :143,
  `.harness/*/docs/**` at :144). So the docs domain today is a two-path grant on one
  persona.
- The **only** assertion touching it is `COLLECT_FIXTURE` in
  `tests/integration/test-harness-yaml.py`, consumed by
  `test_manifest_domains_matches_the_regex_walk_on_the_real_manifest`. Method: read.
- The fixture covers **6** persona keys — backend-dev, dev-ops, pm, documentor,
  eng-lead, orchestrator. The manifest declares **16** — 1 orchestrator, 12 members
  across three `teams[]`, 3 under `leads:`. Method: read both files end to end.
- The file **already resolves** `MANIFEST_PATH` from
  `HARNESS_PROJECT_DIR`/`CLAUDE_PROJECT_DIR` (lines 29–32) and passes it to
  `hy.manifest_domains(...)`. The repointable mechanism exists; the fixture it is
  compared against does not use it. Method: read.
- `manifest_domains(manifest_path, agent)` takes ONE agent and returns `(mine, shared)`.
  There is **no persona enumerator** anywhere in `harness_yaml.py`. Method: read
  `harness_yaml.py:392-451` and Grep for an enumerator; none exists. This is the load-
  bearing gap: "exhaustive over every persona" needs a persona list that does not exist
  yet, and where that list comes from is the plan's central design choice.
- The suite is **green** at 6d969ed3: `python3 tests/integration/test-harness-yaml.py`
  exits 0. Method: ran it. So this is a missing-witness bug, not a failing test.

## The tension the plan must resolve, not paper over

`COLLECT_FIXTURE`'s inlined literals are **deliberate**, and its own comment says so:
it is an equivalence proof that `manifest_domains()` agrees with an independent reading
of the manifest, and deriving the expectation from `harness_yaml` "would prove nothing".

So "load through MANIFEST_PATH rather than hand-copied literals" cannot mean deleting
that fixture's literals — that would destroy a different, working test. The two
assertions have different subjects:

| assertion | subject | expectation must be |
|---|---|---|
| existing equivalence fixture | does `manifest_domains()` read the manifest correctly? | literal grant text, independent of the parser |
| the BUG-442 witness | which personas hold the docs grant? | a literal **persona set**, with the grant text read live |

The witness's literal is the *answer* (`{harness-documentor}`), not a copy of the
manifest's glob strings. That is what makes it repointable: point
`HARNESS_PROJECT_DIR` elsewhere and it reads that checkout's manifest.

## The trap in "enumerate the personas from the manifest"

If the witness loops over personas discovered in the manifest and asserts "documentor
has it, the rest do not", then **deleting a persona from the manifest shrinks the loop
and the test still passes**. An exhaustive assertion whose domain of quantification is
itself derived is not exhaustive. The plan must pin the persona census (the exact
16-name set) alongside the grant expectation, or the removal half of the operator's
sentence is unmet for personas rather than for grants.

Equally: if the enumerator and the grant lookup both route through `harness_yaml`, a
parser bug that hides a persona hides it from both. The census pin closes that too.

## Out of scope

- Changing the docs grant itself. The issue says the grant is **correct**; this flow
  pins it, it does not move it.
- Rewriting or weakening `COLLECT_FIXTURE` or the equivalence test.
- Production changes to `harness_yaml.py` are not required by the stated intent and
  should be justified explicitly if a task proposes one.
