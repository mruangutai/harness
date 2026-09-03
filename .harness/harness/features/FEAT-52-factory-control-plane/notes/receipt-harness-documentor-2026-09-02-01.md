# Receipt — harness-documentor — FEAT-52 T-13

**DEC-212 records the two-anchor path contract; one entry, one index row, one commit `53fca4d8`.
The task's signed `verify:` clause names a flag that does not exist and can never exit 0 — its
intent is met by the equivalence the script itself documents.** Two findings need a tier above me:
the unsatisfiable verify clause, and a rotten anchor in the signed intent.

## What landed

| | |
|---|---|
| Entry | `.harness/harness/docs/DECISIONS.md:6563` — `## DEC-212 — Instruction paths take two anchors…` (64 lines appended at EOF) |
| Index row | `.harness/harness/docs/DECISIONS-INDEX.md:211` |
| Commit | `53fca4d8aeb35263b4b704998719da0dccc04104`, marker `[harness:T-13]`, exactly the two declared files |

Appended at EOF deliberately (repo P-02): it leaves every pre-existing `@line` anchor untouched, so
the regenerated index shows a single added row and zero removed ones.

## Why DEC-212 was the free number

The worktree's log tops out at **DEC-210**, but `git show main:.harness/harness/docs/DECISIONS.md`
already carries **DEC-211** ("The suite runs in parallel…") — merged after this branch was cut. Had
I read the ceiling from my own branch, as the intent's "read the highest existing one" literally
says, I would have allocated a number already taken on the integration branch.

`feat/FEAT-46-decision-standard` also contains a `## DEC-212`, but that branch is a **wholesale
renumber** — 396 entries topping out at DEC-535, its DEC-212 being a renumbered DEC-07. It reserves
nothing in the sequential scheme and will conflict on merge regardless of my choice. Not treated as
an allocation.

## The two anchors, as recorded

- `<HARNESS_CONTROL_PLANE_ROOT>` — **injected** by the `SubagentStart` hook, prefixes every READ.
- `<HARNESS_FEATURE_TREE_ROOT>` — **not injected**, prefixes every WRITE into a feature directory.

The asymmetry, the tool-grant predicate, both rejected alternatives, the spawn-time assertion and
the issue 356 / 357 citations are all in the entry. Every factual claim in the intent was checked
against the shipped code before transcription, and all held: the injected line and
`HARNESS_PATH_DRIFT` (`inject-expertise.sh:61-85`, `exit 0` at `:161`); `feature-root` /
`worktree_for_feature` (`inflight_registry.py:268,649`); the exit-2 refusal keyed on `has_bash`, a
**tool grant and not a name list** (`dispatch-guard.sh`, the `if not has_bash:` branch);
inline-plus-fenced enforcement and the control-plane-anchored-feature-path violation class
(`check-instruction-paths.py:76-88`); required CI step (`.github/workflows/tests.yml:205`). Issue
356 comment 2 confirms the five path families and comment 4 the `CLAUDE_PROJECT_DIR` UNSET
measurement.

## Anchor rot in the signed intent — corrected, not copied forward

The intent anchors the always-exits-0 hook contract at **`DECISIONS.md:1503`**. That line, **in both
the worktree and `main`**, is `check-domain.sh`'s `/**` `startswith` bug. The contract actually lives
in a table row at `DECISIONS.md:1388`, owned by **DEC-101**. I cited DEC-101 **by number** and did
not reproduce the rotten line reference.

Note this class is invisible to DEC-205's guard: its anchor-rot check is existence-plus-range only,
and DEC-205 itself records that it "cannot see the failure that matters most: a line that still
exists and now says something unrelated." This is that failure, in an unchecked file (plan.yaml).

## Verification

The plan's `verify:`, run **verbatim** in the worktree:

```
gen-decisions-index: unrecognized argument(s): --check. Wrote nothing.
...
There is no --check: to check for drift without writing, pipe the read-only mode into
diff — `gen-decisions-index.py --stdout | diff - .harness/harness/docs/DECISIONS-INDEX.md`
PLAN VERIFY EXIT: 2
```

**`--check` exists in neither script copy** (`.agents/` and `.claude/`), and no sibling task adds it;
T-13 is the only task in plan.yaml naming it. I ran this clause **before my first edit** — it exited
2 then too, so its exit code grades nothing about my prose. The `&&` also short-circuited the test
runner away entirely.

The intent, via the equivalence the script's own usage text prescribes:

```
python3 .agents/skills/harness/bin/gen-decisions-index.py --stdout | diff - .harness/harness/docs/DECISIONS-INDEX.md
DRIFT EXIT: 0        # diff emitted zero bytes; emptiness is the pass condition
python3 .agents/skills/harness/bin/test-gen-decisions-index.py
TESTS EXIT: 0        # ok 14, not ok 0
```

**Red-proved, because a green check that was never seen red proves nothing:** mutating the new row's
anchor to `@9999` drove the drift check to exit 1; restoring returned it to 0. The ruling measures
162 non-whitespace characters and 25 words, inside the band asserted at
`test-gen-decisions-index.py:428-432` (≥20 chars, ≤30 words) and nowhere else.

Row/entry consistency: row `@6563` resolves to the `## DEC-212` heading; the generated refs graph is
exactly `DEC-64 DEC-101 DEC-116 DEC-204`, the four cited, each with a live heading; tags
`[plan,dispatch,expertise,worktree]` are generator-computed.

`DECISIONS.md` is **not** in `check-instruction-paths.py --list-scope` (62 files), so the entry's
`<HARNESS_CONTROL_PLANE_ROOT>/…` and bare `.harness/…` prose raises no violation in T-12's new
required CI step. Checked before writing.

## Station

```
STATION T-13 -> done
APPLIED …/FEAT-52-factory-control-plane/plan.yaml
```

`plan.yaml` was already dirty at spawn from sibling station writes (hunks at lines 7, 102, 161 …
893). None are mine and it was **not** staged in my commit.

## Open questions

- **Q1 (blocking the task's own gate).** T-13's signed `verify:` can never exit 0: it invokes a
  nonexistent `--check`. A member cannot repair it — plan.yaml is write-only through `plan-merge.py`,
  and re-scoping a signed clause is not mine. Fix is one of: change the clause to
  `gen-decisions-index.py --stdout | diff - .harness/harness/docs/DECISIONS-INDEX.md && …`, or add a
  `--check` flag to the script. Anything re-running T-13's verify at ship will read FAIL.
- **Q2 (non-blocking).** The intent's `DECISIONS.md:1503` anchor is rotten and remains so in the
  signed plan text. Worth a re-signature to `DEC-101` so a later reader does not follow it.
