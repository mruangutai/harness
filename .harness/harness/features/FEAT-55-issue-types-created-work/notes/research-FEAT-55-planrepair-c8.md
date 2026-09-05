# Plan repair c8 — segment A — all eleven cycle-4 rulings discharged in one revision

**BLUF.** Every ruling in `notes/answers-plan-panel-20260905-c4.md` landed in `plan.yaml` in one pass:
five FIX rulings written through `plan-merge.py amend` (13 field amendments over D-08, D-14, T-01,
T-03, T-05, T-06, T-07, T-10, T-11, T-12) and the four ACCEPT rulings recorded as
`disposition: operator_accepted`. `check-plan-routes.py` over this plan: **0 violations, exit 0**.
`approval:` is untouched and still `status: pending`; BRIEF.md was not opened for writing.

**Route note.** `amend --key` accepts only `tasks | decisions` (plan-merge.py:1232), so the four
disposition strings could not go through `amend`. They went through the sibling verb `set-panel`,
which validates the mapping under the same lock. The round trip was checked: every one of the eleven
`PF-` ids still re-derives from its stored `reader` + `summary` through `panel_findings.py id`
(0 mismatches), so no summary string moved and the five fixed findings' entries are otherwise
byte-equal to what cycle 4 transcribed — the cycle-5 panel re-derivation has nothing to collide with.

## Ruling by ruling — proof strings read back out of plan.yaml

| Finding | What changed | Content string that proves it landed |
|---|---|---|
| PF-1f968f2cd73a799708e4be589d48e61b | new discriminating case on all three creation routes, each with a new fake capability state `nobug` (declares Feature + Task, **Bug absent**) so the creation side cannot refuse and the sole undeclared type is the backfill candidate's | T-03 intent `K. THE BACKFILL IS THE SOLE SOURCE OF A MISSING TYPE`; T-05 intent `H. THE BACKFILL IS THE SOLE SOURCE OF A MISSING TYPE, on this route`; T-07 intent `J. THE BACKFILL IS THE SOLE SOURCE OF A MISSING TYPE, on the factory route`. Verify loops now read `for c in A B C D E F G H H2 I J K`, `for c in A B C D E F G H`, `for c in A B C D E F G H I J`; each required-string loop gained the literal `nobug` |
| PF-e02dcbdf60fdf5eede40feb6066e8a08 | D-14 `because` rewritten; `choice` untouched | `A GraphQL createIssue with issueTypeId IS possible` … `and it is DELIBERATELY UNUSED`. The old `so the CLI cannot set a native type at all` is gone |
| PF-452948136bf467869d223e027191ae49 | T-06 verify gains the gated line; intent no longer asks for a hand-run | verify line 2 `python3 tests/integration/test-gh-issue-types.py \|\| exit 1`; intent `BOTH ARE IN YOUR VERIFY, which runs test-gh-issue-types.py itself` |
| PF-62b2b8ae0acc3509b474b744469137dc | T-10 §6 third bullet folded into the second — one `query_failed` bullet, one SKIP wording | `THAT ONE WORDING COVERS EVERY NON-ANSWER, and there is no second one:` … `an authorisation error, a NOT_FOUND, and gh being unable to reach the TARGET's host`. `SKIP gh cannot reach` no longer occurs anywhere; §6 carries exactly 2 bullets; §7 still carries the four tokens `LIVE PASS, CAPABILITY PRESENT, CAPABILITY ABSENT or SKIP` |
| PF-383a1a92195cf2cdfba9828bda854195 + PF-9a71cb9a0c590b06b890ff1517b80385 | D-08 + T-11 + T-12 + T-01 amended in lockstep (below) | pinned row now **394 chars** (was 511) and byte-identical between T-11 §3 and T-12 §1 (checked by extracting both with T-12's own regex) |
| PF-56a2ce7a053111a3aff62a4b97c5902e, PF-0c12a033f69bb6bc60b8f96134f94fd0, PF-e27f1c3018b6b8477547a1b028607f96, PF-d8a7b516b793e1227b17d61c754240c7 | `disposition: operator_accepted`, authority `notes/answers-plan-panel-20260905-c4.md`. The four accepted SURFACES (the `adopted` marker, T-05 case F's tripwire, T-10 §6's residue) were not touched | four `operator_accepted` strings in `panel.findings`; the other seven still read `batched_to_signature_review` |

## A5 — the design choice, and why

**Chosen: SPLIT, not drop.** The pinned, character-for-character row now names **only the reads this
feature introduces** — the capability-and-declared-names query, the `gh_issue_types.node_id_args`
node-id read immediately before a type-apply, and the probe's opt-in type read-back. The retroactive
enumeration of the **pre-existing** `gh_issues.internal_id_args` reads is out of the pin and survives
as **one unpinned prose sentence in `DECISIONS.md` alone** (T-11 §2), written in no second file.

Why split rather than drop outright: DEC-138's "write-only mirror" reading is false today, before this
feature ships, and dropping every mention would leave a live falsehood in the entry this task exists
to correct. One sentence in one file is the weakest form that keeps the record honest, and it costs no
duplication, no lockstep and no drift guard. Why the node-id read STAYS pinned: it is new in this
feature, so omitting it would make the enumeration incomplete about a read this change actually adds —
the defect the row exists to prevent.

**Durable guard: a new standing unit test, `tests/unit/test-issue-types-pin.py`, written by T-01.**
`run-unit-tests.sh` globs `tests/unit/test-*.py`, so it runs forever. It asserts presence in
`DECISIONS.md`, presence in `github-mirror.md`, and identity between the two **as three separate
failures** — a comparison alone would pass when both copies are missing (two absent extractions
compare equal), which is exactly the state the guard exists to catch. T-01's verify greps for
`DRIFTED` to keep both failure modes real, and T-12's verify keeps its own regex compare and now also
runs the guard.

**Why a second file rather than an assertion group inside `test-issue-types.py`:** T-02's verify runs
`test-issue-types.py` and requires it GREEN, and T-02 lands long before T-11/T-12 write the row.
Folding the guard into that file makes T-02's gate unpassable for a reason unrelated to T-02. The
separate file is red from T-01 until T-12 greens it — the same red-then-green shape the plan already
uses — and no other task's verify runs it in between.

**T-11's greps re-checked against the amended wording:** `which native issue types a repository
declares` ✅ (kept verbatim in the new row), `the native type assigned to an issue Harness created` ✅,
`EIGHT purposes` ✅ (still exactly one row added). No grep needed amending.

**T-01 `traces:` — REQ-09 added, and it is truthful.** REQ-09 is "the record states the new
authority"; the guard asserts permanently that both copies of the record carry that authority and
agree. T-01 now traces `[REQ-02, REQ-03, REQ-04, REQ-09]` and `files:` carries both test files.

## Backlog candidate — exactly one

- **B-1** (`chore`): the other seven rows of the read-back list are duplicated across
  `.harness/harness/docs/DECISIONS.md` and `.claude/skills/harness/references/github-mirror.md` with
  no drift protection at all; only the eighth row is guarded. Not this feature's — it predates it.

## Not done, and why

- `panel.findings` for the five FIXED findings left exactly as cycle 4 wrote them, per dispatch: the
  cycle-5 panel re-derives that block.
- No `resolved_by:` markers added for the same reason.
- `approval:`, BRIEF.md, `review_sha`, GitHub: untouched, as instructed.

## Open question for the operator (non-blocking)

T-06 §3 already computes the backlog refusal over "the WHOLE item list", recorded items included, so
the new T-05 case H fails an implementation that narrows the required set to items it will create.
That clause was not amended — it was already correct. Flagging it because the equivalent clause on the
other two routes is stated explicitly ("THE REQUIRED SET IS NOT ONLY WHAT WILL BE CREATED", T-04 §4;
"THE REQUIRED SET ALSO COVERS THE BACKFILL", T-08 §6) and on the backlog route it is implicit.

## Send-back (c8, single clause) — PF-e02dcbdf60fdf5eede40feb6066e8a08 finished in T-02

The c8 goal-check graded the revision `yes` with one residue: the ruling was discharged in D-14, but
the identical overclaim survived in **T-02's `intent:`** — the builder-facing dispatch, which is where
the finding's stated risk actually lives (a builder noticing the contradiction and defecting to
`createIssue`-with-`issueTypeId`, unwinding the receipt ordering the remnant cases pin). D-14 was
already correct and was not touched.

One field amended, through `plan-merge.py amend --key tasks --id T-02 --field intent` with
`--expect-sha256`. The string `so the type can only be applied after the create` now occurs **nowhere**
in `plan.yaml`. Proof the new wording landed — content string, in T-02's intent:

> `issueTypeId is a measured input field of BOTH CreateIssueInput and UpdateIssueInput, so a create CAN carry the type; this plan deliberately does not use it.`

The passage now keeps the measured fact (gh 2.92.0 has no `--type` flag on `issue create` or
`issue edit`, so the CLI path itself cannot carry the type), states that the create stays on the gh CLI
path deliberately, and names the create-then-type window as a design choice whose ordering the
D-10/D-20 provenance receipt and the remnant cases pin.

Every other line of T-02's intent is byte-identical (diffed against the pre-amend `--show` output: the
only hunk is the three replaced lines). `APPLY_TYPE_MUTATION`, the `apply_type_args` signature and its
returned list, and `missing_types` are intact — T-01 assertion 10 and T-02's own verify grep them.
`check-plan-routes.py`: **0 violations across 1 plan**. `approval:` still `status: pending`; BRIEF.md
untouched.
