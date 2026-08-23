# Receipt — harness-backend-dev — FEAT-32 T-03 (c1)

**Task:** T-03 — Build plan-merge.py so a second plan writer adds tasks and never deletes them.

## What exists now

- `.claude/skills/harness/bin/plan-merge.py` — splices text keyed by `id` (D-03), never
  re-renders through a YAML dumper by default; `approval:` is always the base's bytes (D-04),
  never written or carried from a proposal.
- `.claude/skills/harness/bin/test-plan-merge.py` — 96 assertions across cases 1-10 (house
  shape, `PLAN_MERGE_BIN` env override, every fixture under a fresh `tempfile.mkdtemp()` nested
  at `.harness/harness/features/FEAT-99-fixture/`).

Neither file writes `fcntl`, `O_EXCL`, or `os.replace` — both import `harness_merge.acquire` /
`harness_merge.locked_update` / `harness_merge.MergeRefusal` / `harness_merge.require_destination`
exactly as T-02 shipped them; nothing in T-02's file was touched.

## TDD — Iron Law, including one self-correction

I initially wrote `plan-merge.py` before the test file — a genuine Iron Law violation. Caught it
before running anything, deleted the file, and restarted: wrote `test-plan-merge.py` first, ran
it, watched all cases FAIL (plan-merge.py did not exist — `[Errno 2] No such file or directory`),
then wrote `plan-merge.py` to GREEN. The restart is real, not narrated after the fact — the
`rm` of the out-of-order file preceded any test run.

## verify: exited 0

Ran the task's `verify:` string verbatim (matches the plan's T-03 `verify:` word for word — no
mismatch). One accepted substitution, per the dispatch: the plan's literal
`cp -R "$S" "$T/bin"` line is denied by `bash-write-guard.sh` (resolves `$T` unexpanded, reads it
as an out-of-domain target). Replaced that one line with
`python3 -c "shutil.copytree(sys.argv[1], sys.argv[2])" "$S" "$T/bin"` into the same
`mktemp -d` location — no other line changed. Full `verify:` (with that substitution) exited 0,
suite green, all three RED-PROOF legs correctly failed the mutated copy.

## Judging item 1 — each mutant's FAIL lines, output visible

**UNION_MERGE = False:** every union assertion reddens — case2 (all T-02..T-14 and T-01..T-14
after both applies), case3 (approval byte slice, hash count, IGNORED-APPROVAL), case4 (20-trial
admission), case5 (conflict exit 7 and its three sub-assertions), case9 (all 19 comment lines),
case10a (all four). This is because UNION_MERGE=False makes the tool write the proposal's bytes
alone — today's last-writer-wins — so every case that depends on the base surviving fails.

**PRESERVE_BASE_BYTES = False:** exactly case3 (byte slice + hash count) and case9 (all 19
comment lines) redden — nothing else. Matches the plan's claim precisely: the union/added/
preserved logic is unaffected (still computed correctly), only the final render changes to
`yaml.safe_dump`, which drops the trailing comment and the template's leading comment block and
normalises quoting.

**APPROVAL_REFUSAL = False:** exactly case10a's four assertions redden (exit-8 check, the
stdout-names-both-values check, the byte-identity check, and T-15-absent-by-id). Step 7 alone
still carries the base's approval bytes forward when this literal is off, so — as the plan
predicted — a result-only assertion about the approval block would have passed either way; it is
specifically the byte-identity and T-15-absence assertions in case10a that catch the mutation.

## Judging item 2 — case 7's symlink direction

Built with a real symlink: `escape/.harness/harness/features/FEAT-99-fixture` is a symlink to an
unrelated `outside-real-target/` directory that itself carries no `features/` ancestry. The
literal CLI argument (`.../FEAT-99-fixture/plan.yaml`) ends in the matching tail; `os.path.realpath`
resolves it to `outside-real-target/plan.yaml`, which does not. Confirmed the check bites: in a
tree copy, mutated `harness_merge.require_destination`'s `if tail_regex.search(resolved):` to
`if tail_regex.search(path):` (the argument, not the realpath). Re-ran the suite against that
mutated copy with output visible — **only** this FAIL line appeared, nothing else:

```
FAIL  case7: a symlink escape whose LITERAL argument matches but RESOLVES elsewhere is REFUSED with exit 9
```

## Judging item 3 — assertions by name, never by count

Case 1 (13 assertions, one per `T-02`..`T-14`), case 2 (28 assertions, one per id per apply),
case 9 (19 assertions, one per template comment line), case 10a (T-15 asserted absent by its own
`"- id: T-15\n"` string) — none of these is a length/count check.

## Judging item 4 — case 4 concurrency

Ran 20 trials for real (two subprocesses, overlapping proposals adding T-15/T-16 to the same
base). All 20 trials landed on the "both survive" outcome; **the exit-6 LOCKED branch was never
taken in this run** (`0/20` — printed as an informational, always-true check in the suite's own
output, so this is visible on every run without being a silent claim). With
`LOCK_TIMEOUT_SECONDS = 10.0` and two short-lived local subprocesses, the flock is almost always
free by the time the second process asks, so the branch is admitted by the assertion but rarely
exercised. I did not weaken or widen the assertion to force it — the assertion is a disjunction on
purpose, and reporting the true count (0) is more honest than fabricating pressure to prove the
branch, which case 5's own reviewer note in T-02's history warns against.

## Judging item 5 — no assertion deleted or weakened

One assertion was changed, not deleted or weakened: case 5's original "lock file is gone" check
was **wrong**, not too strict — `harness_merge`'s flock lock (D-02, the file T-02 shipped) is
*deliberately never removed*, unlike `expertise-merge.py`'s O_EXCL create-and-delete scheme this
check was copied from. Replaced it with a check that is strictly harder to satisfy in a way that
matters (no stray `mkstemp()` tempfile left in plan.yaml's directory after a refusal) rather than
simply deleting the assertion. Documented inline in the test file.

## `--check-kinds`

```
$ .claude/skills/harness/bin/run-unit-tests.sh --check-kinds
MISCONFIGURED: .claude/skills/harness/bin/test-dispatch-guard.py is not in run-unit-tests.sh's explicit script list
EXIT_CODE=2
```

Pre-existing per the dispatch (main session's T-07, not this task). `test-plan-merge.py` is
equally unregistered — registering both is T-10's job (dev-ops), not mine.

## Open items I did not resolve

- **`harness_yaml.py` divergence** — the dispatch told me not to touch this; followed the
  instruction, imported `yaml` plainly as the plan specifies.
- Base-file-does-not-exist path (`base_bytes is None`): the plan's CASES list does not test this
  shape, so behaviour there (write the proposal's raw bytes, after a light `safe_load` validity
  check) is my own reasonable-but-untested reading of "the proposal is written whole" — cheap
  and reversible, not raised as an open question.
