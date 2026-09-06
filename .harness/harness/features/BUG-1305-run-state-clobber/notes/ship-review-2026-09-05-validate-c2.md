# Ship review — BUG-1305-run-state-clobber

**Reviewed revision `e77b30ca` (code-identical to your fix commit `2728aa20`). Branch
`feat/BUG-1305-run-state-clobber`, not merged, not pushed, no PR. Worktree intact.**

## Where it stands

**Every success criterion is met and one high finding is yours to rule on.** The goal-check graded
all eleven live criteria MET at the pin, re-derived from scratch rather than carried forward, and
both failure modes are independently declarable delivered. The delta panel's four readers each
returned PASS. The validator lead nonetheless returned ESCALATE, because its own union reading
found something no single reader reported — and that is the one decision left.

- **pm goal-check: 11 of 11 live SCs MET.** SC-08 and SC-12 are retired with their struck
  requirements and are not graded.
- **Delta panel: code-review PASS, security countersign PASS, qa PASS, ui CARRIED from cycle 1
  (recorded as not re-run, not as a fresh pass).**
- **qa `test_matrix` gate: PASS** — the project's only blocking gate.
- **Mechanical grade: exit 0.** The delta's one changed function grades 3, PASS.
- Suites at the pin: unit 28 files exit 0; integration 46 files exit 0; state checker exit 0,
  notes only.

**The decision: VL-01.** REQ-01 promises the seed-field refusal on both governed routes. On the
**Edit** route with an **absent** prior checkpoint, `check-domain.sh` reaches `sys.exit(0)` through
`_edit_reconstructed_content`'s `except OSError: return None` before the witness is ever consulted —
measured exit 0 at both pins, with a refusing control at exit 2 and the Write route measured closed.
SC-01(a) is *literally* met, because its FAILS-if clause does not reach this case; REQ-01's
two-route promise is not delivered. It is **pre-existing rather than introduced here**, dormant on
this host, and REQ-02 detection is unaffected. The remedy, if you want it, mirrors the F-04 fix
exactly: consult the witness for `RE_STATE_YAML` before calling `_edit_reconstructed_content` and
refuse on `None`. That file is main-session-direct, so no squad may do it — it is a thirteenth cycle
or a named residual, and both are yours.

**One fact that bounds it, measured rather than argued:** this host's `Edit` tool refuses a
nonexistent `file_path` outright ("File not found ... Use the write tool to create new files"), with
an existing-path control proving the probe shape valid. That makes the class dormant *here*. It is
not a reason to weaken the portable fix already shipped for F-04 — the hole was real by payload at
the old pin, and another host may differ.

## What the cycles bought

Twelve cycles, three Advisor extensions, and each round found something the previous one could not.
Planning replaced the Mode-A mechanism twice: session identity was killed for refusing a resumed
owner, marker-acquisition was killed by a panel `critical` showing it refused approximately only the
legitimate owner and approximately no foreign run, and the minted `run_uid` that survived is the
Advisor's own recorded fallback. In build, qa caught SC-01's Edit half asserted on Write only; the
first panel caught the witness unguarded on every route; cycle 11 closed F-04 and three evidence
gaps. **Four of the last five sharpest defects were found in the union of two readers' scopes**,
where each reader was individually correct — that is now this feature's signature failure shape and
it is worth carrying into how panels are briefed.

## How this briefing was assembled

**No report round was spawned.** I read the digests and notes from disk. First-hand:
`runs/review-c2-validator/digest.md`, `runs/goalcheck-build-c2-product/digest.md`,
`runs/review-c1-validator/digest.md`, `runs/goalcheck-build-c1-product/digest.md`,
`runs/simplify-eng/digest.md`, `notes/qa-testmatrix-c1.md`, `notes/qa-regate-sc01-c10.md`,
`notes/receipt-harness-dev-ops-editprobe-c1.md`, `notes/receipt-harness-dev-ops-diag-c1.md`,
`notes/review-harness-code-reviewer-advisor-c1.md`, and the plan-phase goal-checks and panel
digests. **The production work itself I did not execute** — every task is main-session-direct under
DEC-174 — so the account of what the code does is read from the reviewed tree and from the readers'
measurements, not from having built it.

`runs` is 23 against an informational budget of 20; INV-22 notes it and never gates. My read: the
count is honest work, not churn — thirteen of the twenty-three are grading runs, and every one of
the eight rework cycles closed a defect a later round confirmed closed.

## Proposed backlog

Nothing below gates. Anything not listed dies silently, so this is everything that survived
collation. Strike rows by ID.

| ID | Nature | Item |
|---|---|---|
| B-1 | bug | **VL-01, if you accept it rather than fix it:** REQ-01's seed-field refusal is absent on the Edit route with an absent prior. Pre-existing, dormant on this host, Write route closed. |
| B-2 | bug | SEC-01 — directory-level Bash `rm`/`mv` destroys witness, checkpoint and digest with no refusal. Already filed as **#1376** under your Advisor-delegated acceptance; listed so it is not double-filed. |
| B-3 | enhancement | A portable regression for the Edit-creates path that does not depend on any one host's `Edit` semantics. |
| B-4 | chore | `check-state.sh:1502-1514` keeps a shadow copy of `uid_conflict`'s own guard and has already drifted on a whitespace `run_uid`. SIMPLIFY's one recommended apply, deliberately not applied. |
| B-5 | chore | `harness_boundary.py:22` imports `MARKER_NAME` eagerly: +6.45 ms on every governed write, measured over a 60-invocation A/B. |
| B-6 | chore | POST effective-uid selection lives in a shell heredoc with no importable function and no unit test. |
| B-7 | chore | Two citation-rot lines in `notes/regression-delta-BUG-1305.md` (a case renamed at cycle 11; the composed digest case uncited). Non-gating; you ruled against spending a cycle. |
| B-8 | chore | `check-domain.sh:1240` still reads like the false PRE-only comment REQ-06 removed. Its subject is the POST-sweep exclusion and it is true; it will mislead the next reader anyway. |
| B-9 | chore | Sweep the remaining criteria for the pattern that produced two highs: a criterion's test grading a materially easier case than the criterion's own body describes. |
| B-10 | bug | Harness: worktree claims are keyed per persona globally, so a lead correctly dispatched at BUG-1305 was refused writes into its own BUG-1305 run directory while holding a claim on another feature. Blocked three digests this feature. |
| B-11 | bug | Harness: members emitted complete, well-formed returns that the host recorded as `failed (exit 1) — yield with null data`. A good return looks like a crashed member. |
| B-12 | bug | Harness: a pre-plan `harness-code-reviewer` cannot yield at all — `validate-digest.py` demands a binding that cannot exist before a plan is drafted. |
| B-13 | chore | Harness: no `plan-merge.py` verb reaches the `lanes:` block, so late-added surfaces are recorded in a task's `execution_reason` instead. |
| B-14 | chore | Harness: `check-state.sh` INV-26 reddens every signature-pending plan, demanding a mirror step that legitimately runs only after approval. |
| B-15 | chore | Stale scratch worktrees: `.claude/worktrees/harness/qa-regate-sc01-baseline-c10` stands, and a `.git/worktrees` entry may survive `qa-redproof-sc13-c1`. `git worktree prune` plus a removal, both yours. |
| B-16 | enhancement | Define "exhausts" for `max_total_cycles` (BUG-1286's B-12). Undefined again here and it cost two Advisor round-trips. |

## What I did not do

Not merged, not pushed, no PR, no ship, no worktree removal, no distillation. No residual was
accepted and no gate waived by me: SEC-01's acceptance is yours under Advisor delegation, and VL-01
is unruled. Cycles stand at 12 of 12 — a thirteenth needs a fresh ruling.
