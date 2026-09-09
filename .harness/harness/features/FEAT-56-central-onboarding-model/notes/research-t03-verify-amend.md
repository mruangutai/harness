# T-03 `verify:` — amended to the re-homed path

**BLUF: amended, and the amended block runs green in full (exit 0).** Clause 4's path only:
`tests/integration/test-check-state.py` → `tests/integration/test-check-state-records.py`. One line of
plan.yaml changed. `approval:` untouched, T-03 still `done`, `check-plan-routes.py` still exactly
`1 violation(s)`.

## Judgement — why amending is the right act, not falsification

The argument against treats `verify:` as a record of a past run. It is not: it is a **standing
specification**, carried verbatim to whoever re-checks the task and cited as evidence in the
goal-check. Rule 15 protects the *record of what happened* — the `done` status, the receipts, the
observed outcomes — and none of those are touched here. What clause 4 asserts is a predicate over
file **content**: that the onboarding premise comment says "read from that repository's own
harness.json". origin/main moved that content, it did not change it — the line is verified in place at
`tests/integration/test-check-state-records.py:522`. Amending the pointer to the moved subject
preserves the assertion's meaning; refusing would preserve only its syntax while the assertion became
unrunnable, which is the more dangerous falsification because it looks fine until someone runs it.
Rule 7 settles the balance: a verify that can never exit 0 is a dead gate, and a dead gate cited as
evidence teaches the factory it verified something it did not. Doctrine agrees explicitly —
**DEC-205** (`DECISIONS.md:6326`) ends the amendment convention in favour of records that "state
current truth", and its own worked precedent is exactly this case: three file-and-line anchors naming
"a path the tree no longer has" were **repaired**, not preserved as history. The feature's own
**REQ-06** and T-03's item 4 make the point sharper still — T-03 exists partly to re-anchor citations
*because line citations rot*. Leaving a dead path inside that task would ship a rot instance in the
task that fixed rot.

## Evidence

**Pre-amend string cross-checked byte for byte** against the dispatch via `yaml.safe_load` + `repr` —
identical, including `\n` placement and the mixed double/single quoting. `--show` sha256
`b3aee234a9d6189279659c78e531d36d3fb4f71df48ea781649a744071fc7897`, passed to `--expect-sha256`.

**Premises re-derived:** `tests/integration/test-check-state.py` → ABSENT; the six split files exist;
`grep -nF` finds the premise line at `test-check-state-records.py:522`.

**The amend** (only route used; no editor write, no redirect):

```
plan-merge.py amend --key tasks --id T-03 --field verify \
  --expect-sha256 b3aee234... --value-file /tmp/t03-verify-amend.txt
AMENDED tasks:T-03.verify
APPLIED .../FEAT-56-central-onboarding-model/plan.yaml
```

**My diff is one line** (`git diff` on plan.yaml):

```
-      grep -qF "read from that repository's own harness.json" tests/integration/test-check-state.py &&
+      grep -qF "read from that repository's own harness.json" tests/integration/test-check-state-records.py &&
```

The other hunk in that diff — `D-08  dec: DEC-220` → `DEC-221` — is the **sibling's landed decision
renumber**, present before I ran and preserved by `plan-merge` across the splice. Not mine.

Shape preserved: still `verify: |` (literal, not folded), same six clauses in the same order, same
`&&` placement, clause 4 double-quoted, clauses 5–6 single-quoted, same trailing newline.

**Amended verify run in full, from the worktree root, `env -u HARNESS_AGENT_TYPE`** — all three suites
executed (~21s), no clause skipped:

```
test-layout-migration.py   -> 42 ok lines, EXIT=0
test-hooks-install.py      -> 32 PASS lines, EXIT=0   (incl. both red proofs)
test-post-merge-sweep.py   -> 55 PASS lines, EXIT=0   (incl. self-exclusion red proof)
grep clause 4 (records)    -> match
! grep SKILL.md:73 (x2)    -> absent in both
EXIT=0
```

**Approval and status intact:**

```
done {'date': '2026-09-09', 'approved_by': 'molchairuangutai', 'status': 'approved'}
```

**`check-plan-routes.py`, run by relative path from the worktree root** (never the main checkout's
copy — that would grade the wrong tree): `1 violation(s) across 5 plan(s)`, the accepted D-14
owner-manifest DEVIATION. Baseline held; no second violation introduced.

**`git status --porcelain`** — plan.yaml present and modified; everything else is siblings' landed
work I did not touch: `DECISIONS.md` / `DECISIONS-INDEX.md` (DEC citation fixes),
`tests/integration/test-check-state-records.py` (the test re-home), `BUILD.md`, `SPEC.md`, `org.html`,
both `README.md`, `test-onboarding-split.py`, `test-no-distribution.py`, the two `observations/` files,
and four untracked `notes/receipt-*.md`. No commit; HEAD still `bb39d5c4`.

## Open questions

- **Q1 (non-blocking):** T-03's `files:` list (`plan.yaml:895`) still names the deleted
  `tests/integration/test-check-state.py`. Same rot, different field, out of this dispatch's scope.
  Whether a dead path in a done task's `files:` is worth a second amend is the lead's call.
- **Q2 (non-blocking):** T-03's `intent:` item 2 still names the old filename in prose. Left
  deliberately per dispatch. Note that intent prose is the literal dispatch string, so a future
  re-dispatch of T-03 would send its doer to a file that does not exist.

Both are the same family as clause 4 and would be one amend each. Neither affects the green verify.
