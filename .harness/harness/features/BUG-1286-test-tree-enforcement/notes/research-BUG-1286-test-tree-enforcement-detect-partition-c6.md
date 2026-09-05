# GAP-1 closed — T-01 case 11's partition is now bounded by the test tree (cycle 6)

**Conclusion: the residual measured in cycle 5 is closed in the spec, and measured closed.** The
`docs/**`-for-`tests/unit/**` substitution that stayed GREEN under the old partition is RED under the
new one, and today's four globs still pass. Two files amended, nothing else: T-01's `intent:` (case 11
only) and `BRIEF.md` SC-19. Both approvals remain `pending`; the `panel:` block is byte-unchanged.

## The rule, as written into case 11

Computable from the glob string alone — no repository state, no `git ls-files`, no runner behaviour:

- **BASENAME** — final `/`-segment contains `*` or `?` **and** `segment.strip("*?")` is non-empty.
  Unchanged behaviour: synthesise `.harness/tools/<final segment with * and ? -> x>` and require the
  **imported** `suite_layout.is_test_shaped` to accept it.
- **DIRECTORY-ONLY** — everything else. Its *literal prefix* is the `/`-joined leading segments before
  the first segment carrying a wildcard.
  - **EXCUSED** iff that prefix is `tests` or starts with `tests/`.
  - **ROGUE** otherwise, the empty prefix included.
- **ROGUE set must be empty**, asserted in its own `check()` naming every offender. A rogue glob has
  no basename wildcard, so there is nothing to synthesise; the honest assertion is that it must not
  exist. Remedy when it fires: fix `detect`, or record why the new root is genuinely discoverable —
  never delete the assertion.
- The pre-existing **"exactly one excused"** count is kept, so a partition bug that excuses everything
  and empties the check still cannot pass silently.

**Why the rule is right for this repository** (checked, not assumed): `unit.cmd` is
`run-unit-tests.sh --kind unit` (`.harness/harness.json:271`) and the excluded `functional` kind's
`excluded_because` (`:279`) records that this runner splits its suite by the `tests/unit` and
`tests/integration` directories. A `unit.detect` root outside `tests/` is therefore unrunnable here by
construction. I found no legitimate counter-case; I do not believe the rule is wrong.

## MEASUREMENTS — faithful prototype, run from the worktree root

Command: an inline `python3 - <<'PY'` prototype (no file created) that read
`test_kinds.unit.detect` from the worktree's real `.harness/harness.json`, applied the three-bucket
partition and the synthesis step verbatim as specified, and judged synthesised paths with the
predicate T-01 specifies (`RESTRICTED`/`AGNOSTIC`/`SOURCE_EXTENSIONS`) — `suite_layout.is_test_shaped`
does not exist yet, T-01 being unbuilt, so the prototype spells the specified predicate. Prototype
deleted (it never touched disk).

| Config | Classification | Verdict |
|---|---|---|
| today: `tests/unit/**\|**/*.test.*\|**/*_test.*\|**/test_*.py` | 1 excused (`tests/unit/**`), 3 basename, 0 rogue | **GREEN** |
| + `**/*.spec.*` (both files) | basename; synthesises `.harness/tools/x.spec.x` | **RED** — not test-shaped |
| `docs/**` substituted for `tests/unit/**` (both files) | `docs/**` rogue, excused count 0 | **RED** — two failures, both naming the glob |

## Mechanical re-verification (worktree root)

1. `python3 -c` yaml load — loads; `status: plan`; `approval: {status: pending}`, no `rulings`;
   `panel:` identical to `HEAD:plan.yaml` both structurally and as raw lines (122 lines). Among tasks,
   `plan-merge.py` spliced only `tasks:T-01.intent` (`AMENDED tasks:T-01.intent`). T-03/T-04/T-05 also
   differ from `HEAD` — those are prior cycles' uncommitted amendments, not this spawn's.
2. `CLAUDE_PROJECT_DIR=$PWD python3 .claude/skills/harness/bin/check-plan-routes.py <plan.yaml>` →
   `0 violation(s) across 1 plan(s)`, exit 0; all five tasks carry all eleven keys.
3. `CLAUDE_PROJECT_DIR=$PWD env -u HARNESS_AGENT_TYPE .claude/skills/harness/bin/check-state.sh` →
   **no `INV-35` line**. For this feature: the expected unsigned-BRIEF violation, plus one
   pre-existing, unrelated violation — `runs/2026-09-04-17-product/digest.md` fails the lead digest
   contract (DEC-156). Not mine to write; raised as Q1.
4. 19 SCs, each with exactly one `verify:` and every `automated` one carrying `evidence:`; all 19 map
   in the traceability table, covering all eleven ACs (AC-01…AC-11); SC-19 → REQ-09 → traced by T-01.

T-01's `verify:` matches the dispatch verbatim (`repr` checked, trailing newline only).

## Open

- Q1 (non-blocking, not mine): the `2026-09-04-17-product` lead digest fails `validate-digest.py lead`.
