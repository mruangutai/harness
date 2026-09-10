# T-09 receipt — record the strict digest contract

**PASS.** DEC-223 is appended at the end of `.harness/harness/docs/DECISIONS.md`, DEC-126's leads
bullet is corrected in place, and `DECISIONS-INDEX.md` is regenerated. The task's own `verify:`
block runs clean: the `--stdout` regeneration diff is empty (exit 0) and `closed digest contract`
is present in the index. `tests/integration/test-gen-decisions-index.py` — the only gate that owns
the index's completeness and ruling budgets — is 14/14 ok.

## What landed

- **DEC-223 — "The digest contract is closed, and the run-state step vocabulary with it"**
  (`.harness/harness/docs/DECISIONS.md:7092`). Body states, as current truth: the closed key set
  and the single one-shot message naming every offending key with its declaration route;
  `DOCUMENTED_OPTIONAL` keyed by RAW agent type and why not `SCHEMAS` (DEC-121 required-membership,
  plus the three reviewer agents collapsing to one canonical persona with non-interchangeable
  modes); `PASSTHROUGH` for lead roll-up fields and its reason; bidirectional mechanical agreement
  with `.omp/agents` as source of record because `.claude/agents` is generated; `adequacy_notes`
  required of every lead, closing issue 37; the closed 22-key `steps[]` shape with the governed
  free-form `evidence` container, enforced on `check-domain.sh`'s write payload path and reported at
  rest by `check-state.sh`, gated on `schema_version` 2 with creation below 2 refused and the 356
  version-1 runs left legal and unrewritten; and the open `stop_hook_active` passthrough as the
  reason the message must be one-shot sufficient. Refs line names the ten required decisions, and
  the regenerated row's `refs:` graph computed exactly those ten.
- **DEC-126 correction**, one clause, no dated note (`DECISIONS.md:2616-2617`): the validator lead's
  per-role extra is `severity_max`, and `adequacy_notes` is required of all three leads in the
  canonical block. The **devs** and **reviewers** bullets are byte-unchanged — the entry's diff is a
  single 2-line-for-2-line hunk at 2615.
- **Index row** `- DEC-223 @7092 [state,digest,dispatch,domain] refs: … :: The closed digest
  contract: …` — ruling hand-written (28 words, 168 non-whitespace chars, inside the 30-word /
  20-char band), everything left of ` :: ` generated.

## Grounding — every clause was checked against the code, not the plan

`PASSTHROUGH`, `DOCUMENTED_OPTIONAL` and the one-shot refusal message at
`.claude/skills/harness/bin/validate-digest.py:235`, `:248`, `:1415-1421`; `adequacy_notes` required
in `SCHEMAS["lead"]` at `:209`; the `stop_hook_active` short-circuit at `:1827`; the 22 step keys
(`id` … `evidence`) and the `schema_version` 2 description in
`.claude/skills/harness/bin/run-state-schema.json:23-56`; the creation-only version floor at
`check-domain.sh:1586-1612` and the at-rest sweep gate at `check-state.sh:1484-1492`; both
directions of the documented-block check in `tests/integration/test-validate-digest.py` (`:289`
forward, `:2871`/`:2936` reverse) with `.omp/agents` as the roster source at `:298-306`.

## Corrections to the plan's own premises — for the record

1. **The plan's DEC-126 anchors were stale by two lines**, as the dispatch said; I anchored on
   content (the `- **leads (3)** →` bullet) and the true lines were 2616-2617.
2. **The plan asserts the DEC-126 correction "changes the length of an entry near the middle of the
   file, so every later row's anchor shifts."** It does not: the correction is line-count-neutral
   (two lines replaced by two), so no later `@line` shifted and the index diff is a single inserted
   row. Regeneration was still required — it is what produced DEC-223's tags, refs and anchor — but
   its stated reason is false. Nothing depends on this; noted so the next reader does not look for
   an anchor shift that never happened.
3. **`git diff --stat` shows three files, not two.** The third is
   `features/FEAT-104-strict-digest-schema/plan.yaml`, whose sole hunk is `T-09 status: ready →
   building` — written by the dispatching product lead and already present at spawn (baseline
   `git status` at spawn also carried `tests/integration/test-check-domain.py` and
   `test-validate-digest.py`, both committed by a sibling as `9be1d722`/`9fc8543f` during this run,
   which is why HEAD is `9fc8543f` and not the `d873a915` the dispatch pinned). My own change is
   exactly the two contracted docs files.

## Verification, literally

```
$ python3 .claude/skills/harness/bin/gen-decisions-index.py --stdout | diff - .harness/harness/docs/DECISIONS-INDEX.md
(no output)  # exit 0 — an empty diff is the pass
$ grep -q 'closed digest contract' .harness/harness/docs/DECISIONS-INDEX.md   # exit 0
$ git diff --stat
 .harness/harness/docs/DECISIONS-INDEX.md           |  1 +
 .harness/harness/docs/DECISIONS.md                 | 46 +++++++++++++++++++++-
 .../FEAT-104-strict-digest-schema/plan.yaml        |  2 +-
 3 files changed, 46 insertions(+), 3 deletions(-)
```

The verify block was cross-checked against `plan.yaml` T-09 lines 592-595 before running: identical,
verbatim. The generator printed no `ORPHAN:` and no malformed-row error, and the index carries no
`RULING PENDING`. Nothing was committed.

## Coverage limit of the verify block

Neither clause tests the entry's substance — one asserts the index is a faithful regeneration, the
other asserts a literal phrase in the index. That DEC-223's body states every clause WRITE 1
enumerates, and that DEC-126 now says the right thing, rests on my reading and on the code citations
above. A reviewer wanting mechanical coverage would have to assert named phrases inside the DEC-223
entry, as `test_dec_210_entry_names_both_enforcement_points` does for DEC-210.
