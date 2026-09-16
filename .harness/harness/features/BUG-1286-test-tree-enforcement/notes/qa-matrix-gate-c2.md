PASS

# QA test_matrix gate — BUG-1286-test-tree-enforcement (c2, probe only)

**BLUF: hypothesis CONFIRMED.** Integration case 3 (`git three tracked rogues reported in sorted
path order`, `tests/integration/test-run-unit-tests-layout.py:97-112`) cannot fail on the ordering
property it names. A unit case (`test-suite-layout.py` case 3) independently and correctly binds
the same property, so this is a demonstration gap, not a protection gap. The case-11 `INAPPLICABLE`
advisory is confirmed real.

## 1. The probe

Scratch copy: `/tmp/bug1286_c2_probe/probe_case3.py` (copy of the tracked integration test; ROOT
hardcoded to the real worktree since the copy lives outside it). Mutation: after `misconfigured` is
built from `p.stderr`, reversed it before `ordered` is computed — simulating a runner that emits the
three `MISCONFIGURED:` lines in reverse (unsorted) order.

Debug output confirmed the mutation actually took effect on real production output:
```
PROBE misconfigured(reversed)= ['...c/test_three.py', '...b/test_two.py', '...a/test_one.py']
PROBE ordered= ['.harness/a/test_one.py', '.harness/b/test_two.py', '.harness/c/test_three.py'] sorted(rogue_paths)= [same]
PASS git three tracked rogues reported in sorted path order
```
Full run: 14/14 PASS, exit 0 — **case 3 stayed GREEN under a reversed line order.**

**Hypothesis CONFIRMED.** `ordered` is built by iterating `rogue_paths` (the outer loop, already
alphabetical by construction) and merely testing presence of each `rel` in *some* `misconfigured`
line — it never reads the position of the matching line, so it carries zero information about the
order the runner printed the lines in. The assertion reduces to "each rogue appears in exactly one
MISCONFIGURED line," already mostly covered by the preceding `all(any(...))` clause.

Scratch copy and `/tmp/bug1286_c2_probe` directory deleted after the run (confirmed:
`ls` reports "No such file or directory").

## 2. What SC-03 is left with — demonstration gap, not protection gap

`suite_layout.py` itself sorts: `tracked_paths()` returns `tuple(sorted(...))`
(`suite_layout.py:76`), and `violations()` iterates `sorted(tracked)` (`suite_layout.py:139`) — the
production ordering guarantee is real and independent of this test.

**`tests/unit/test-suite-layout.py` case 3 (lines 209–230) independently binds the property for
real**: it calls `suite_layout.violations(td)` directly, filters the return list *in the order
`violations()` produced it* (`rogue_findings = [g for g in got1 if g.startswith(...)]`), and compares
against `expected` built from a genuinely independent `sorted([...])` over three paths created in
non-alphabetical order (tools, notes, evidence). If `violations()` ever emitted rogues in creation
order instead of sorted order, `rogue_findings` would read `[tools, notes, evidence]` against
`expected = [evidence, notes, tools]` and redden. This case was part of cycle 1's corroborated
341/0/27 unit run.

So: the ordering property is genuinely protected at the unit layer. The integration case-3 defect is
that it duplicates unit case 3's *claim* one layer up (through the runner's stderr) without actually
re-testing anything beyond presence — a **demonstration gap** at integration, not a hole in
production protection.

## 3. Case-11 `INAPPLICABLE` advisory — confirmed YES

By inspection (`test-suite-layout.py:519–526`): when `select_control_candidate` finds no qualifying
member of the hardcoded `CANDIDATE_CORPUS` under the live `test_kinds_cfg`, it takes the `else`
branch, which only `print()`s `INAPPLICABLE ...` — no `check()` call, so no PASS/FAIL line and no
`failures.append`. The suite exits 0 regardless. The two remaining case-11 behavioural checks
(lines 506–517) both assert `offenders(...) == []` over a synthetic/real tree that is offender-free
*by construction/current reality* — they pass whether or not `offenders()` can actually detect a
real offender. So yes: a future `test_kinds` change that disqualified the whole corpus would reduce
case 11's behavioural half to two vacuous `== []` checks with the suite still green. This is
advisory, not gating — matches the dispatch framing.

## Worktree state

`HEAD` = `d2ccea0a686bbff06f2b3782e7fe346340bcb503`, confirmed unchanged. `git status --porcelain`
shows only this feature's own tracking dir (STATE.md/feature.json modified, cycle-1 note and two
sibling observations untracked) — pre-existing, not touched by this cycle. No tracked file was
read-then-written; the only mutated bytes were in `/tmp/bug1286_c2_probe`, now deleted.

## Open questions

None.
