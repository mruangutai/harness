# Ship review — BUG-1305-run-state-clobber (final)

**Reviewed revision `252a18a9`. Branch `feat/BUG-1305-run-state-clobber`, not merged, not pushed, no
PR. Worktree intact. Ready to ship on your decision.**

## Ready to ship

Every gate is green and every live success criterion is met. The last two authorised cycles closed
the two findings that were open, and both closures were proven by falsification rather than by
reading.

- **pm goal-check: SC-07 MET at the pin**, and every other live criterion carries unchanged because
  `git diff 154ff2a0 252a18a9 -- .claude/skills` is empty — production code has not moved since the
  reviewed pin. Mode A and Mode B are each independently declarable delivered.
- **qa scoped review: PASS, `must_fix` empty.** The handoff PRE permit case reddens under two
  independent live mutants — the exact `RE_HANDOFF`-into-deny-by-path harmonisation the Advisor
  feared, and a forced grammar-validator failure — so neither half of the composed claim is a free
  rider.
- **Earlier gates stand:** qa `test_matrix` PASS, SIMPLIFY PASS across four angles, code grade exit
  0, the cycle-15 two-mutant probe closing panel F-1 with zero crosstalk, security countersign PASS.
- Suites at the seam: `test-check-domain.py` exit 0 (40.06s) with markers 27/27 plus the new case;
  integration 46 files, 0 FAIL, exit 0 (63.70s); state checker exit 0, notes only.

**Cycle 18 was reserved and is unspent.** The three findings that remain are non-gating citation and
provenance items, and you ruled against spending a cycle on them; they are rows below.

## What the seventeen cycles actually bought

This feature was re-founded three times, and each time by measurement rather than by argument.
Planning killed session identity as a denial input (it refused a resumed owner), then killed
marker-acquisition (a panel `critical` showed it refused approximately only the legitimate owner and
approximately no foreign run), leaving the minted `run_uid` the Advisor had recorded as its fallback.
Build then found the deeper defect: the omp bridge sends `check-domain.sh` only `{ file_path }` for
an Edit, so **every governed Edit PRE check was dormant on the host the harness itself runs on** —
not open in corner cases. The suite's exit-2 evidence was real only for payload shapes this host
never emits. Cycle 13 made reconstruction-`None` fail closed for `state.yaml`, `digest.md` and
handoff notes, and cycles 15 and 17 pinned each arm against regression.

**Five of this feature's sharpest defects were found in the union of two readers' scopes**, each
reader individually correct and the composite claim false. That is worth carrying into how panels
are briefed, and it is row B-9.

The record also contains one thing worth protecting: the cycle-4 goal-check refused to green SC-07
by demoting a true disclosure out of the note's BLUF, and the Advisor amended the criterion instead —
recording that the refusal was correct. A factory that punished that refusal would learn to
under-report.

## How this briefing was assembled

**No report round was spawned.** I read the digests and notes from disk. First-hand:
`runs/review-c5-validator/`, `runs/review-c4-validator/digest.md`, `runs/review-c3-validator/`,
`runs/review-c2-validator/digest.md`, `runs/review-c1-validator/digest.md`,
`runs/goalcheck-build-c1..c3` digests, `runs/simplify-eng/digest.md`, `notes/qa-testmatrix-c1.md`,
`notes/qa-regate-sc01-c10.md`, `notes/review-harness-qa-c4.md`, `notes/review-harness-qa-c5.md`,
`notes/research-BUG-1305-goalcheck-build-c5.md`, `notes/regression-delta-BUG-1305.md`,
`notes/receipt-harness-dev-ops-editprobe-c1.md` and the plan-phase panel record. **Two digests are
inline in their leads' returns rather than on disk** — `review-c5-validator/digest.md` and
`goalcheck-build-c5-product/digest.md` — because the claim defect in row B-10 refused those writes;
their content is otherwise complete and was assessed at source by the leads.

**I did not execute the production work.** Every task was main-session-direct under DEC-174, so the
account of what the code does is read from the reviewed tree and from the readers' measurements.

`runs` is 30 against an informational budget of 20; INV-22 notes it and never gates. My read: the
count is honest. Seventeen of the thirty are grading runs, and every rework cycle closed a defect a
later round independently confirmed closed.

## Cleanup you own

Four scratch worktrees survive and `check-state.sh` INV-29 will notice them. Removal is never a
subagent's act:

`qa-c2-c369` (`c369fb1f`), `qa-c2-dc0` (`dc0e0313`), `qa-c2-e77` (`e77b30ca`), `qa-c2-mutate`
(`e77b30ca`), all under `.claude/worktrees/harness/`. A `git worktree prune` afterwards clears any
administrative entry left by the mutant worktrees that were already removed.

## Proposed backlog

Nothing below gates. Anything not listed dies silently, so this is everything that survived
collation across seventeen cycles. Strike rows by ID.

| ID | Nature | Item |
|---|---|---|
| B-1 | bug | SEC-01 — directory-level Bash `rm`/`mv` on a run directory destroys witness, checkpoint and digest with no refusal. Already filed as **#1376** under your Advisor-delegated acceptance; listed so it is not double-filed. |
| B-2 | chore | Regression note `:9` names the removed complexity-allowlist row as `validate_digest.py:main`; the row actually removed is `("validate-digest.py", "check_artifact_file")`. Substance true, identifier false. |
| B-3 | chore | The note's unit-suite figure was measured at `dee707e9`, before three files changed — it is not a pin measurement, while the integration line is. Non-gating under the criterion as signed. |
| B-4 | chore | The reconstruction-`None` disclosure quotes its message verbatim but names only the permit cases; the message itself is pinned at `test-check-domain.py:3839` and `:4860-4864` and could be cited. |
| B-5 | chore | `check-state.sh` keeps a shadow copy of `uid_conflict`'s own guard and has already drifted on a whitespace `run_uid`. SIMPLIFY's one recommended apply, deliberately not applied. |
| B-6 | chore | `harness_boundary.py` imports `MARKER_NAME` eagerly: +6.45 ms on every governed write, measured over a 60-invocation A/B. |
| B-7 | chore | POST effective-uid selection lives in a shell heredoc with no importable function and no unit test. |
| B-8 | chore | `check-domain.sh:1240` still reads like the false PRE-only comment REQ-06 removed. True as written — its subject is the POST-sweep exclusion — and it will mislead the next reader anyway. |
| B-9 | enhancement | Brief review panels to hunt the composite claim: five of this feature's sharpest defects lived where two readers' scopes overlap, each reader correct alone. |
| B-10 | bug | Harness: worktree claims key on persona and on the shared broker pid, so a lead is refused writes into its own feature's run directory while a sibling flow holds that persona's claim — and a claim whose agent has left the roster still reads live. **Six occurrences this feature**, two of which lost a run digest to an inline-only record. |
| B-11 | bug | Harness: members emitted complete, well-formed returns that the host recorded as `failed (exit 1) — yield with null data`. |
| B-12 | bug | Harness: a pre-plan `harness-code-reviewer` cannot yield at all — `validate-digest.py` demands a binding that cannot exist before a plan is drafted. |
| B-13 | chore | Harness: no `plan-merge.py` verb reaches the `lanes:` block. |
| B-14 | chore | Harness: `check-state.sh` INV-26 reddens every signature-pending plan, demanding a mirror step that legitimately runs only after approval. |
| B-15 | enhancement | Define "exhausts" for `max_total_cycles` (BUG-1286's B-12). Undefined again here; it cost an Advisor round-trip. |
| B-16 | chore | `tests/integration/test-check-domain.py` lets `CHECK_DOMAIN_BIN` swap the guard binary under test. It is what made this feature's mutation probes possible; an env-swappable guard under test still deserves an owner's eyes. |

## What I did not do

Not merged, not pushed, no PR, no ship, no worktree removal, no distillation. No residual accepted
and no gate waived by me: SEC-01's acceptance and every cycle extension are yours under Advisor
delegation. Cycles stand at 17 of 18, with 18 reserved and unspent.
