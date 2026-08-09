# Receipt — FEAT-10 final2-product — narrow named edits to plan.yaml and BRIEF.md

**BLUF: all eleven named items closed except the E-1 hierarchy half, which is closed as a STATED
RESIDUAL rather than fixed — deliberately, because the `sub_issues` endpoint is unmeasured. No
task's `id`, `depends_on`, `files` or `verify` changed. Counts unchanged: 12 tasks, 15 decisions,
20 `- SC-NN:` criteria. Both artifacts remain `status: pending`.**

T-04's `verify:` was cross-checked against the dispatch before any edit and matches byte for byte,
including the trailing newline the literal block carries.

## Per item

| Item | Verdict | Where |
|---|---|---|
| E-1 dependency half | closed | T-04 step 7b, the ONE NARROW EXCEPTION paragraph |
| E-1 hierarchy half | closed as a stated residual, not fixed | same paragraph, final clause |
| E-2 atomic ledger write | closed | T-04 step 8, temp file plus `os.replace` |
| D-14 factual error | closed in both places | `decisions` D-14 `choice` + `because`; T-04 step 4 |
| `edges_skipped` (A-2) | closed | T-04 step 8 payload keys + the skip test case |
| `internal_id` cache (A-3) | closed | T-04 step 7b(a) |
| degradation clause (A-4) | closed | T-04 step 5b |
| SC-07 traces | closed | `BRIEF.md` SC-07 → `[REQ-01, REQ-03, REQ-04, REQ-05]` |
| coverage paragraph | closed | `BRIEF.md`, two qualification paragraphs after the coverage line |
| REQ-07 note | closed | same block, second qualification |
| SC-01 wording | closed | `BRIEF.md` SC-01, ledger-conditional clause; `verify`/`evidence`/`traces` untouched |

## The two judgement calls worth reading

**The E-1 narrowing discriminates on the exception's captured output, not on a status attribute.**
`run_gh` raises `GhError` on a non-zero `gh` exit, and the class carries the exit status, captured
stdout and captured stderr as attributes (T-03's `factory_gh.py` contract in this plan). `gh api`
prints the HTTP error body on stdout, so the predicate is the token `422` in captured stdout or
stderr AND the phrase "already been taken" in either — the same shape `create_ref` already uses to
tell a lost race from an authentication failure. Nothing about the clause needed T-03's `files:` to
widen, which is what would have made it not-closable.

**Three test cases were added, not one.** The already-drawn `blocked_by` case would pass on a build
that swallowed every `GhError`, and it would also pass on a build that generalised the narrowing
across both endpoints. So that case also asserts the attach twin still exits 2 with no parent
receipt, and a separate case asserts a non-422 `GhError` stays fatal on the dependency call. The
E-2 case asserts against a monkeypatched `os.replace` (same-directory source, source parses as
complete YAML) plus a recorded `open` showing `feature.yaml` is never opened truncating — a
before/after content check cannot see a kill *during* a write, because that failure leaves no end
state to compare.

The self-describing count in T-04's intent moved with the additions: "Eight cases carry the DAG"
now reads "Eleven cases carry the DAG and the ledger that makes it idempotent", verified at 11
bullets.

## One edit the dispatch did not name

`BRIEF.md` `## Verification gaps` carried the same superseded measurement claim D-14 carried — that
re-posting either edge endpoint is unmeasured. Correcting D-14 and SC-01 while leaving it would have
left the document contradicting itself at the signature. The clause the sc-delta validator relied on
to downgrade its SC-01 finding — *"SC-01's 'the second run mutates nothing' rests on that ledger and
not on any API property"* — is preserved verbatim; only the measurement half changed, plus one
sentence naming the unnarrowed `sub_issues` residual.

## Not done, on purpose

Advisory **A-1** (T-08's INV-24 collecting `factory.parent` into its duplicate-pair set) is a `med`
in the same eng digest and was outside the dispatched scope. It remains unclosed and is recorded
nowhere in the plan. Nothing on the leave list was touched, no criterion was renumbered, and no
approval status was written.

## The one edit with a consumer outside T-04

`edges_skipped` changes `factory_decompose`'s stdout payload, so the plan's other payload readers
were checked rather than assumed. T-12's forked end-to-end case takes each step's issue number from
the previous step's parsed payload by NAME (`plan.yaml:1514-1516`) and asserts no exact key set;
SC-11's and T-04's own stdout cases assert only that the whole stream parses in one `json.loads`.
No consumer breaks on an added key.

## Gates

`safe_load` parses `plan.yaml`; `check-plan-routes.py` reports 0 violations across 1 plan (its T-08
DEVIATION line is pre-existing and informational, present before these edits); `check-docs.sh`
reports no stale statements across 277 files.
