# Q4 adopted — T-07 and SC-11 written

**Done.** `plan.yaml` gains **T-07** (`team` / `harness-dev-ops`, `change_type: logic`,
`depends_on: [T-02]`, `status: pending`, one file:
`.claude/skills/harness/bin/test-inject-expertise.py`). `BRIEF.md` gains **SC-11**
(`verify: automated`, `evidence: unit`), the operational criterion REQ-05 lacked. No existing task,
SC or requirement was touched; five `status: done` fields are byte-identical. Nothing staged, nothing
committed.

## The mechanism was run before it was written down

Scratch tree, `os.symlink` to a nonexistent target at `.harness/kaya/expertise/harness-qa.md`:

- the bash glob `./.harness/*/expertise/harness-qa.md` **matches** the dangling link;
- `[ -r "$f" ]` is **false** (link is followed; true for every uid, root included);
- with the guard gone, `head -n 40` prints `No such file or directory` and `wc -l <` fails, so the
  hook writes to **stderr** and emits a `kaya` header with an empty body.

That last observation is why SC-11 asserts **stderr is empty**, not the weaker "contains no
traceback". Empty stderr is clean today and dirty under the mutant — it is the discriminator.

## Why it targets the guard's unspecified duty

`inject-expertise.sh:75-77` (`case "$segment" in ''|*[!a-z0-9-]*) continue ;;`) independently rejects
an unexpanded glob word, which is the only duty the guard's own comment claims. That half is
double-covered and cannot redden — the measured result behind the operator's constraint. The
uncovered duty is **present but unreadable**, and case13 asserts only that.

## Acceptance is the proof, not the case

T-07's intent requires the doer to (1) copy the hook, delete exactly the line
`[ -r "$f" ] || continue`, assert the one-line diff applied, (2) run the suite with
`INJECT_EXPERTISE_BIN=<mutant>` and require case13 **FAIL** plus non-zero exit, (3) re-run unmutated
and require all-PASS, (4) record both runs in the receipt. The env seam already exists
(`test-inject-expertise.py:26`), so no edit to the shipped script is needed to mutate it.

**The permitted non-delivery is written in.** If case13 stays green under the mutant, the case is
removed, the file stays at twelve cases, the doer returns `FAIL` with the proof attempt, and SC-11
grades `not_met`. Never ship an assertion that cannot fail.

## Checks run

- `yaml.safe_load(plan.yaml)` parses; task ids `T-01..T-07`; statuses `done, done, done, done,
  pending, done, pending` — unchanged for T-01..T-06.
- `check-plan-routes.py plan.yaml` → exit 0, `0 violation(s)`, `OK T-07 granted to
  harness-backend-dev, harness-dev-ops`. (The pre-existing `DEVIATION T-04` line is a report, not a
  violation, and predates this edit.)
- `verify:` is a literal `|` block in T-02's shape.

## Open items

- SC-11's `verify: automated` rests on `unit`, which has a live runner — no verification gap added.
- `inject-expertise.sh` is deliberately **not** in T-07's `files:`: the guard is already shipped and
  correct, and touching the script under test would make the task's own mutant proof circular.
