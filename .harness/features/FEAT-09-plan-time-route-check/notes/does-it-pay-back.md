# Does FEAT-09 pay back? — the performance question, measured

FEAT-09 is issue **#20, a performance item**. The cost it was built to remove is the routing wall:
a task dispatched to an agent whose domain denies the write, discovered mid-build with the build
spine already open. Recorded cost: **four recurrences, and one real ESCALATE at FEAT-04 run 10 —
$16** — with the lead attributing it to its own dispatch error.

Judged against enforcement it looks thin. Judged against **the cost it exists to remove**, which is
the right yardstick, it works — with two real limits. Everything below was run, not reasoned.

## Test 1 — would it have caught the actual recurrences?

The historical PLANs predate the `## Lanes` / `execution_mode` format, so pointing the checker at
them tests backward compatibility, not detection. Restaged in the new format instead — FEAT-05's
"third recurrence" (dev-ops denied `.gitignore`, `templates/**`, `harness-init/SKILL.md`) and
FEAT-04's T-09/T-10 shape:

```
VIOLATION T-01: .gitignore ungranted (NOBODY); execution_mode is team
VIOLATION T-01: .claude/skills/harness/templates/PLAN.md ungranted (NOBODY); execution_mode is team
VIOLATION T-01: .claude/skills/harness-init/SKILL.md ungranted (NOBODY); execution_mode is team
OK T-02 granted to harness-documentor
3 violation(s) across 1 plan(s)   exit=1
```

**It catches all three, names each path, and exits non-zero — before dispatch.** That is the $16
escalate prevented, and the mechanism is demonstrated rather than asserted.

## Test 2 — the false-positive rate (answers backlog B-4, previously UNMEASURED)

Run against all 8 PLANs in the tree:

| Plan | exit | `no files:` artifacts | real ungranted hits |
|---|---|---|---|
| FEAT-02 | 0 | 0 | 0 |
| FEAT-03 | 1 | 8 | 0 |
| FEAT-04 | 1 | 10 | 0 |
| FEAT-05 | 1 | 17 | 0 |
| FEAT-06 | 1 | 0 | 1 — **FALSE POSITIVE** |
| FEAT-07 | 0 | 0 | 0 |
| FEAT-08 | 1 | 0 | 1 — **FALSE POSITIVE** |
| FEAT-09 | 0 | 0 | 0 |

**35 format artifacts and 2 false positives across 5 legacy plans.** The false positive is
diagnosed, not guessed: FEAT-06 T-08 writes `files:` on its own line with paths as a markdown list
beneath, so the checker reads the literal path `- docs/harness/SPEC.md` — dash included — which
resolves to NOBODY. `--resolve docs/harness/SPEC.md` returns `harness-documentor`, so the file is
plainly granted and the verdict is wrong.

**It fails CLOSED, not open** — same direction as B-1. Safer, still wrong, and it costs a planner
time chasing violations that are not there.

## The honest ledger

**Pays back:** on a well-formed plan it catches the path-write collision class that produced three
of the recorded recurrences, before any dispatch. The rule reaching the planner is not
best-effort either — `harness-spec-driven` is in `harness-pm`'s `skills:` preload
(`harness-pm.md:8-12`), so it loads at every spawn rather than depending on someone opening a file.

**Does not pay back, and this is the sharp limit:** the **fifth** recurrence happened *during this
feature* — the `run-unit-tests.sh` collision — and the checker cannot see that class by design,
because it is a tool the plan USES, not a path a task WRITES. So the control covers the recurrences
it was scoped from and not the most recent one.

**Costs, today:** legacy-format plans produce noise, and nothing verifies the planner ran it
(issue #133).

## What would raise the payback, in order

1. **B-11 / the format bug** — strip list-form `files:` entries so the false positives stop. Cheapest,
   and it is the only item here that currently makes the checker cost time rather than save it.
2. **#133 + B-7** — wire it, so compliance is verified rather than instructed. B-7 first: an
   argv-less run reports "0 violations across 0 plans" and exits 0.
3. **The fifth-recurrence class** — decide whether a plan's *tool* dependencies belong in scope at
   all. Unresolved, and it is a scoping question rather than a defect.
