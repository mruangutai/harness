# Fail-first receipt — BUG-1716 T-04 (signed task hashes, record-amendments, approval reset narrowing)

The five new `case_b1716_*` cases run with PLAN_MERGE_BIN pointed at the parent commit's plan-merge.py (1fbf8471, pre-change) in a throwaway worktree. Captured 2026-09-16T05:58Z by Main.

```
FAIL  b1716/sign: exits 0 and prints HASHED
FAIL  b1716/sign: one hash per task, lowercase sha256 of the canonical JSON
FAIL  b1716/sign: a changed value changes only that task's hash
FAIL  b1716/sign: a refused signature leaves feature.json byte-identical
FAIL  b1716/285: exits 0 naming each target
FAIL  b1716/285: intent, verify and files carry the digest's now values
FAIL  b1716/285: the `|` verify body keeps its block form
FAIL  b1716/285: three amendment judgements in digest order, by the orchestrator
FAIL  b1716/285: reasons are the digest's, and every `at` is distinct and increasing
FAIL  b1716/285: a rerun is refused (exit 6) naming the already-applied state
FAIL  b1716/refuse/no amendments: exit 2 naming the fault
FAIL  b1716/refuse/absent amendments: exit 2 naming the fault
FAIL  b1716/refuse/not a mapping: exit 5 naming the fault
FAIL  b1716/refuse/extra key: exit 5 naming the fault
FAIL  b1716/refuse/missing key: exit 5 naming the fault
FAIL  b1716/refuse/SC id: exit 5 naming the fault
FAIL  b1716/refuse/decision id: exit 5 naming the fault
FAIL  b1716/refuse/bad field: exit 5 naming the fault
FAIL  b1716/refuse/empty reason: exit 5 naming the fault
FAIL  b1716/refuse/long reason: exit 5 naming the fault
FAIL  b1716/refuse/intent as list: exit 5 naming the fault
FAIL  b1716/refuse/files as string: exit 5 naming the fault
FAIL  b1716/refuse/line anchor: exit 5 naming the fault
FAIL  b1716/refuse/absent task: exit 3 naming the fault
FAIL  b1716/refuse/stale was: exit 6 naming the fault
FAIL  b1716/refuse/duplicate target: exit 5 naming the fault
FAIL  b1716/refuse/second entry stale: exit 6 naming the fault
FAIL  b1716/refuse/no feature.json: exit 2 naming the ledger path
FAIL  b1716/approval: record-amendments exits 0
FAIL  b1716/approval: amend on an existing task no longer resets the signature
FAIL  b1716/approval: apply replacing a field on an existing task keeps the signature
FAIL  b1716/approval: adding a task still resets approval to pending
```

28 `b1716` checks pass pre-change: they are the byte-identity halves of each refusal (a verb that does not exist writes nothing) and are kept because they bind the refusal to a no-write once the verb does.
