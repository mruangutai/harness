# BUG-1290 — ship review, fourth pass

**Both of your directives landed. B-27 is closed, and case `5b` itself now fails under the
issue-map-cache mutation — literally, as a printed `FAIL  BUG-1290 5b` line, not as an equivalent.
Every gate is green, all nine success criteria are met, and this cycle spent ZERO rework budget.
The change is ready for your ship decision.**

Production is still **byte-identical** to the tree you were shown this morning:
`git diff --stat c488218e 72a97b99 -- .agents/ .claude/skills/ bin/` is empty — my own measurement.
The whole cycle is **two test files**.

The new `review_sha` is **`72a97b99`**. Your authorized `max_total_cycles: 11` is recorded in
`feature.json`.

---

## What you asked for, and what landed

Your directive, from `notes/answers-2026-09-06-b27.md`, had three parts. All three are delivered,
and I verified each myself before writing this.

### 1. Fix B-27 — the mutant must show its specific observable · **DONE**

`5g` used to assert a bare negation: "the property does not hold under the mutant". Anything falsy
satisfied that, including a mutant that merely raised. It now asserts the six-clause observable the
key collapse actually produces — exit 1, empty stdout, stderr naming `952` and `unresolvable
blocker`, and *not* `no plan could be read`
(`tests/unit/test-factory-claim.py:1340-1349`).

**The proof is the arm that used to pass.** Replace the mutant's delegating call with a bare
`raise`: before this cycle the suite stayed green at 125/125; now it goes red on `5g`. That is B-27,
reproduced and then closed.

### 2. The literal case-`5b` failure · **DONE, and it is not the `5g` equivalent you rejected**

You were right that the `5g`-only form did not deliver the words you wrote. It is now delivered
twice, at two different seams, because the two answer different halves of your sentence:

- **Inside the suite** — `5b`'s two verdict-producing lines are factored into one emitter,
  `_emit_5b(record)`. The intact run reports through it; the mutant arm reruns *that same emitter*
  under the collapsed cache through a non-printing shim, and asserts the verdict recorded under
  case `5b`'s own name is False. I probed the internals directly: the captured entry is keyed by
  `name_5b`, its verdict is `False`, and the real cache is restored before `5c` runs.
- **As a printed failure** — `tests/unit/test-factory-claim-mutation.py` (the file that already
  existed for exactly this purpose) gained a second arm. It patches
  `factory_claim._BlockerCache` at module level and re-executes **the whole real suite**, which then
  prints, verbatim:

  ```
  FAIL  BUG-1290 5b: same feature id on two repositories resolves per-segment, no cache bleed
  ```

**Why both.** The in-suite arm cannot print a red `5b` line without the run failing; the printed
form needs a separate run of the whole suite. Together they give you the literal observable and keep
the mutation out of `5c`–`5f`, which was your second constraint.

### 3. No leakage into `5c`–`5f` · **DONE**

Verified three independent ways, none of them "the `finally` is present": a fresh cache is
constructed per run so nothing can carry the mutation forward; `id(claim._BlockerCache)` is
identical before and after; and under a whole-suite external collapse **only `5b` reddens** —
`5c`–`5g` stay `ok`.

### The measurements — mine, not any agent's

Five arms on out-of-tree copies, so the tracked files were never touched
(`/tmp/b27-orch-control.py`, `/tmp/b27-orch-control2.py`):

| Arm | Result |
|---|---|
| intact | 125/125, exit 0 |
| **the raising mutant — B-27** | **1 of 125 FAILING on `5g`**. It was 125/125 green before this cycle |
| harness fixture's `depends_on=["T-99"]` deleted | RED — B-16's defence survived the refactor |
| harness fixture's issue map emptied | RED on `5b` — `5b`'s own fragment survived |
| the captured verdict's identity | keyed by `name_5b`, `False`, cache restored |
| **the new printed-FAIL arm, collapse neutered** | arm goes **RED** while the mutant is still *reached* — it discriminates the collapse itself, not merely that some mutant ran |

That last row is the one that matters most: it is the B-27 lesson applied to the new gate at the
moment it was written, rather than three cycles later.

---

## The gates

| Gate | Result | Evidence |
|---|---|---|
| Engineering — B-27 + in-suite literal form | PASS, 0 send-backs | `runs/2026-09-06-13-eng/digest.md` |
| Engineering — printed-FAIL arm | PASS, 0 send-backs, negative-control proven | `runs/2026-09-06-14-eng/digest.md` |
| qa test-matrix (**the one blocking gate**) | **PASS**, `matrix_ok: true`, `must_fix: []` | `runs/2026-09-06-15-validator/digest.md`, `notes/qa-2026-09-06-15-validator.md` |
| Simplify (four angles) | **Empty pass** — two candidates surfaced, both declined on measured grounds; nothing applied | `runs/2026-09-06-16-eng/digest.md` |
| Validation panel at `72a97b99` | **PASS**, `must_fix: []`, `severity_max: med`, **four reviewers ran, none skipped** | `runs/2026-09-06-17-validator/digest.md` |
| Goal-check | **9 of 9 SC MET**, every row re-derived this run | `runs/2026-09-06-18-product/digest.md`, `notes/research-BUG-1290-goalcheck-b27.md` |

Three things the teams volunteered that I am passing on rather than smoothing:

- **`severity_max: med` is carried entirely by two pre-existing functions** (`build_features_root`,
  `run_main`) that this cycle did not touch. Every finding this cycle's own diff produced is `low`
  or `info`.
- **The simplify pass declined both of its own applyable findings**, and the reasons are better than
  the findings: a shared report helper would have silently rewritten the exact `KEY-COLLAPSE PROOF`
  string the directive and qa both pin, and a shared reached-marker cannot exist because production
  constructs `_BlockerCache()` internally, forcing one marker to be class-level and the other
  instance-level.
- **The panel found what no single reviewer could.** `5g` alone still cannot distinguish your key
  collapse from an unrelated always-unresolvable cache; the cause-discrimination lives in the
  *other* file. Two reviewers each held half of that. It is rows B-33/B-34 below, not a gate.

---

## One question I answered myself, so you can overrule it

The validation lead asked whether to send the ui reviewer back: its return carried
`severity_max: n/a`, which is not a valid enum value. **I accepted the trade.** The reviewer's
verdict was stated rather than inferred, its note is complete and lead-verified, and it had scoped
itself out on a measured census — so a send-back would have spent budget on a malformed field in a
return whose content is not in doubt. It is logged as row B-38.

---

## Budgets

- **Rework cycles: 9 of your raised 11 — this cycle spent ZERO.** Six runs, six clean first passes,
  no send-back anywhere. The cycle you authorized for "one unexpected send-back" was not needed.
- **Runs: 30 of an informational 20.** My read, unchanged in shape from this morning: today's six
  runs each earned their place — two delivered the two halves of your directive, one gated them, one
  looked for simplification and honestly found none, one reviewed, one graded the goal. The budget
  notices a long feature; it does not stop one.

---

## How this briefing was assembled

**No report round was spawned.** I read the run digests off disk and verified the artifacts they
cite: `runs/2026-09-06-13-eng/digest.md`, `runs/2026-09-06-14-eng/digest.md`,
`runs/2026-09-06-15-validator/digest.md`, `runs/2026-09-06-16-eng/digest.md`,
`runs/2026-09-06-17-validator/digest.md`, `runs/2026-09-06-18-product/digest.md`, plus
`notes/qa-2026-09-06-15-validator.md`, the four reviewer notes `notes/review-*-b27-c4.md`, and
`notes/research-BUG-1290-goalcheck-b27.md`. Earlier phases are as reported in the third-pass
briefing, `notes/ship-review-2026-09-06-13-ship.md`, which this supersedes rather than replaces.

The five-arm table, the empty production diff and the budget figures are **my own measurements**.
Everything else is attributed.

**One thing I cannot tell you from here.** `check-state.sh` resolves features through the project
root — the main checkout — where this feature's directory does not exist on `main`. Run from this
worktree it therefore says **nothing at all** about BUG-1290 (814 lines of output, zero mentions).
That is not a clean bill of health; it is a measurement I could not take. The standing INV-29
worktree violations it does report belong to other flows (`BUG-440`, `FEAT-55`,
`qa-bug440-c3-probe`).

---

## Proposed backlog

Strike any row by its ID. Unstruck rows become backlog issues on acceptance. **B-27 is gone — you
had it fixed, and it is closed.** Rows B-32 onward are new since this morning. Every earlier
unstruck row is carried forward verbatim; anything not listed here dies silently.

### New this cycle

| ID | Nature | Finding |
|---|---|---|
| B-32 | bug | **The mutation suite's diagnostic `FAIL` lines are byte-identical to genuine ones.** A CI log grep for `^FAIL` reports four failures on a run that is a clean exit-0 pass. No gate in this tree reads bare `^FAIL `, so it cannot mislead a machine today — the hazard is a human or tool reading the log in isolation. Remedy: prefix them (`[mutant] FAIL …`). Raised by the ui reviewer and qa independently. |
| B-33 | enhancement | **`5g` alone cannot discriminate the CAUSE.** An unrelated always-unresolvable cache satisfies all six of its conjuncts identically; the discrimination lives in the other file's arm. Deleting the mutation arm would leave `5g` looking adequate while your requirement quietly lapsed. Bind the two files. |
| B-34 | enhancement | **Nothing asserts that ONLY `5b` reddens under the collapse.** That it does is verified-today, not pinned. A future collapse that reddened every case would still print `FAIL 5b` and pass. |
| B-35 | chore | **The comment at `test-factory-claim.py:1308-1310` overstates its proof.** `5c`–`5f` run *before* `5g` and never touch the issue-map cache, so their passing is guaranteed by construction and is not evidence about restoration. The restoration IS proven — by three other measurements. Precision only. |
| B-36 | chore | `tempfile.mkdtemp` fixture directories are never removed; they accumulate in CI `/tmp`. Mode 0700, synthetic content only. |
| B-37 | chore | **Two pre-existing grade-2 functions** — `build_features_root` (`:324`) and `run_main` (`:403`) — carry this cycle's `severity_max: med`. Unchanged by this diff, reasoned and accepted by the grader, transcribed at its own severity rather than re-rated. |
| B-38 | bug | **A reviewer return carried `severity_max: n/a`, not a valid enum value.** Recorded rather than sent back (see above). The digest contract has no `n/a` for this field and nothing rejects it at the reviewer tier. |

### Product residue — carried forward

| ID | Nature | Finding |
|---|---|---|
| B-1 | chore | **REQ-08 has no committed defender.** Deleting the `factory_config.py` features reader row entirely still yields `CLEAN`; only T-04's probe discriminates, and it lives in `plan.yaml`'s verify block, which CI never re-runs. Promote it into a committed case. |
| B-2 | chore | **Mutation depth is one seam.** `features_root` has a dedicated mutation proof; `segment_of` does not. A `segment_of` mutant *does* redden case `5d`, so the property is caught — only the committed proof is missing. |
| B-4 | chore | **`factory_claim.py:38` `_BIN_DIR` is dead within its module.** Its only reader is unit case `5d`. A later cleanup deletes it and reddens `5d` for an unrelated reason. Repoint `5d` at `fc._BIN_DIR`. |
| B-5 | chore | **`features_root`'s join is not traversal-safe in isolation.** `"owner/../../etc/passwd"` escapes the harness root. **Not attacker-reachable today** — candidate filtering matches exact `fleet.yaml` membership first. Defence in depth only. |
| B-6 | bug | **The `feature`-label-derived join is unvalidated, and `feature` IS attacker-influenced** (`factory_claim.py:170,190`). **Pre-existing**; belongs to the factory owner, not this diff. |
| B-7 | chore | **`segment_of`'s docstring claims to be "the one home of that rule" and the tree disagrees.** Four identical derivations survive (`post-merge-sweep.sh:163`, `quarantine.py:109`, `worktree_terminal.py:107-129`, `feature_schema.py:231`). |
| B-8 | chore | `_BlockerCache._plan` and `.issue_number` build the `(repo, feature)` key inline in two places rather than through one accessor. |
| B-9 | chore | `features_root(repo)` is resolved at three call sites in `_BlockerCache`. Measured inert (13.32 µs per call). Shape note only. |
| B-10 | chore | **REQ-05's wording correction.** The requirement says the segment rule is called by `factory_claim.py`; measured, it reaches it transitively through `features_root`. SC-06 is met on its own words. You have declined to rule on it three times; queued here so it survives. |
| B-17 | chore | **`build_features_root()`'s docstring overstates the fixture.** It presents both segments' issue maps as load-bearing; measured, only the harness side discriminates. |
| B-28 | enhancement | **`_5b_property_holds` is a single point of failure for both cases.** Weakening it to `payload.get("issue") == 952` alone leaves both green with kaya-ai's half of the proof gone. Requires editing the assertion itself. |
| B-29 | enhancement | **A failing `5g` renders a detail tuple shaped exactly like a passing `5b`'s.** Legibility only. |
| B-30 | chore | **`_5b_property_holds`'s "never raises" docstring is imprecise** — non-dict JSON reaches `.get()` past the guard. Unreachable in practice. |

### The feature's record — pre-existing

| ID | Nature | Finding |
|---|---|---|
| B-23 | bug | **The plan-panel record is incomplete** — readers `scope`, `should-not-exist` and `goalcheck` are unrecorded. `plan.yaml` is byte-identical to the approval commit, so this predates every cycle since. Only the product manager may write `panel:`. |
| B-24 | chore | **No `notes/handoff-build.md` exists** — the build seam was crossed without one, by a predecessor. Confirmed absent again today. Deliberately **not** fabricated after the fact; writing a "working memory" note for a phase nobody ran would falsify the record. |
| B-25 | chore | **Run bookkeeping fails its own contracts.** Forbidden `run_uid` keys in `state.yaml`; older run digests failing the lead digest contract. Systemic lead behaviour across cycles. |

### Harness defects observed during these runs

Defects in the factory itself, not in the change. Listed because this repository *is* the harness.

| ID | Nature | Finding |
|---|---|---|
| B-11 | bug | **`check-domain` matches inflight claims by bare agent-type across every linked worktree, with no session scoping.** No recurrence today. |
| B-12 | bug | **Nothing stops a lead writing its digest into a run directory another run already owns**, and `runs/` is gitignored, so the overwrite is unrecoverable. |
| B-13 | bug | **Edit-tool/filesystem desync on hardlinked files.** |
| B-14 | bug | **Lead dispatches return a null yield while complete, correct work sits on disk. Recurred again today** — the eng lead's simplify return exited 1 at the return validator with its digest already written and its `PASS` unambiguous. Fourth consecutive cycle affected. Work survives only because I verify artifacts on disk rather than routing on job status. |
| B-15 | bug | **Agents leak edits into the main checkout via relative paths.** *No recurrence in the last three cycles — re-checked today.* |
| B-18 | chore | **The test matrix keys a required test kind on a directory label, not on the changed surface.** Exactly the mis-scoping shape this test-only cycle presented, and qa had to reason around it again. |
| B-19 | bug | **The write-guard refuses an agent a shell append to its own in-domain path while permitting an editor write to the same path.** |
| B-20 | bug | **Reviewer digests are parsed from the assistant-text fence rather than from `yield`'s structured data.** |
| B-21 | bug | **Panel reviewers return `files_touched: []` while their notes land at the cited paths.** |
| B-22 | chore | **State the test matrix's diff object in the protocol.** A fix cycle is not a change type; the matrix grades the feature's change. |
| B-26 | chore | **Agent scratch worktrees are not cleaned up and escape the invariant's naming.** No new one this cycle — I checked, and the `qa-c2-*` trees standing in the layout predate today (created 2026-09-05 20:43 and 20:46). `qa-bug440-c3-probe` is still red under INV-29 and no removal command can be composed for it. |
| B-31 | chore | **`test_matrix.bugfix` carries a permanently inert leg.** `match_bug_class` has no bug-class taxonomy anywhere in this repository, so it can never fire — **third consecutive grading**, re-raised by qa unprompted. Retire the leg or supply the taxonomy. |

---

## What the factory still cannot tell you

Unchanged, and worth repeating because it is easy to misread as a failure:

- **A live claim run from `main` still reports `no_plan` for FEAT-04.** That feature tree exists only
  in the FEAT-04 worktree. The brief disclosed this before you signed.
- **The panel verifies the resolver and its tests, not the multi-repository lane end to end.**
- **The coverage is one mutation operator per seam.** Other cache-isolation failure shapes —
  wrong-repo population, eviction — remain untested.

---

## Your decision

**Ship** — nothing is shipped, merged or PR'd. On acceptance the main session runs `gh-sync.py ship`
from the **main** checkout with this file as the body (it refuses from inside a worktree, at exit 1,
before any write), then `gh-sync.py backlog` for every unstruck row, then the merge, then
feature-close distillation.

**Fix something first** — say which row and I route it. Nothing in the backlog gates, and you have
**two** rework cycles left of your raised 11, all of them unspent this cycle.

**Re-scope or stop** — also available; everything is preserved on the branch.
