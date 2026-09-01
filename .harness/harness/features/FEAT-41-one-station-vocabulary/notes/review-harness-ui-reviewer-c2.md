# UI Reviewer — FEAT-41 — cycle 2

review_sha `39477a502cd6726f01ad403dbdb4222c26969d2e`, base `7c4f0bd`. Scoped IN: this cycle's
fixes are entirely operator-facing text/messages in PreToolUse/PostToolUse hooks and CLI gates —
squarely this role's remit, no rendered UI exists (confirmed again by all three prior cycles;
no DESIGN.md, no html/css/tsx in this diff's file list). **Every item RUN, not read** — actual
`bash`/`python3` invocations against throwaway `$TMPDIR` fixtures, per the dispatch's own
instruction. Worktree left clean (`git status --porcelain` after every run showed nothing of
mine).

## VERDICT: PASS, with one MED finding cycle 1 did not check for

### 1. H-01 PRE — CONFIRMED CLOSED, message quality high

Built a `$TMPDIR` fixture (manifest + `.harness/harness/features/FEAT-99-fixture/plan.yaml` +
`notes/innocent.md -> ../plan.yaml`) and fired `check-domain.sh` for real:

```
check-domain: DENIED — .harness/harness/features/FEAT-99-fixture/notes/innocent.md — the write
would land in .harness/harness/features/FEAT-99-fixture/plan.yaml, which it links to: plan.yaml
has exactly ONE writer, plan-merge.py, because every station value must be validated against the
vocabulary before it lands on disk. ...
```

Names the path the operator typed **and** what it resolves to **and** why the route is closed,
plus four copy-pasteable remedy commands. Exactly what the dispatch's Q1 asked for. Direct writes
to the real path get the same treatment (no `_via` clause when link==target). `check-domain.sh:1524-1528`.

### 2. H-01 POST — MED, not caught by cycle 1, not caught by this feature's own new test

**The reporter's detection is correct; its message names the wrong file.**

Confirmed with the same fixture, `status: Building`→content mutated to an illegal value and
fired as a `PostToolUse` event through the symlink:

```
check-domain: OVER BUDGET (already written) — .harness/harness/features/FEAT-99-fixture/notes/innocent.md:
plan.yaml station vocabulary (FEAT-41 REQ-01).
  top-level status 'Building' is not a station
  ...
```

The header names `notes/innocent.md` — the literal, innocent path the write was addressed to —
**never the plan.yaml it actually landed in.** This is the exact failure mode H-01's PRE fix was
written to prevent ("Refusing `innocent.md` with no explanation reads as a malfunction" —
`check-domain.sh:1518-1521`), reintroduced one checkpoint over.

**Root cause, at `check-domain.sh:1561-1575`:** the POST branch resolves `_rel` through
`_route_candidates(target)` (the H-01 fix) to decide *which shape rules apply* — that part is
correct, which is why the vocabulary violation fires at all. But line 1575 builds the reported
tuple as `(_rel, _f.read(), _show(target))` — `_show(target)` is the **unresolved, literal**
path (`check-domain.sh:974-980`: `_show` is deliberately un-stripped and un-resolved, "the path a
human can act on"... except here it names the wrong one). `_head()` at `check-domain.sh:1127`
prints `display or rel` — `display` wins, so the operator always sees the symlink's name, never
the file the vocabulary net actually read.

**This is reachable, not theoretical:** the PRE route denial closes this exact write for `Write`/
`Edit` before it lands, so under normal single-call operation this branch is a backstop — but the
developers built and tested it as one on purpose ("the reporting side... cannot drift apart",
commit 707b547), which means they consider it live surface, not dead code.

**Confirmed the feature's OWN new test has the identical blind spot cycle 1's mutation-class
findings were about.** `test-check-domain.py:2762-2769`'s case for this exact scenario asserts
only:
```python
r9c.returncode == 2 and "Sideways" in r9c.stderr
```
— it checks the illegal *value* appears, never that the *resolved path* does. Contrast with the
PRE case three lines above it (`test-check-domain.py:2717-2719`), which explicitly asserts
`".../FEAT-99-fixture/plan.yaml" in r9.stderr`. **The asymmetry in the fix is mirrored exactly by
an asymmetry in its own test** — a mutation that reverted line 1575 to use `_rel` instead of
`_show(target)` would pass this suite unchanged, exactly the "guard that passed review but was
provably deletable" shape this cycle was asked to hunt for.

**Failure scenario:** any write that reaches this POST branch with a symlinked route (a real
Bash-created symlink pointing at `plan.yaml`, or a race between PRE and the actual write) leaves
an operator reading "notes/innocent.md: plan.yaml station vocabulary ... is not a station" with
no way to tell, from the message alone, that the real problem is in `plan.yaml`, not in a file
called `innocent.md`. The exit code is still 2, so nothing ships silently — this is a message
fidelity gap, not a bypass, which is why it's MED and not HIGH.

**BLOCKS: no.** Detection and refusal both function; only the operator-facing attribution is
wrong. Needs a written reason if left open: a one-line fix (`_show(target)` → the resolved
`_rel`'s display form, mirroring what `_via` already does for PRE) plus tightening the existing
test assertion to check the path, not just the value.

### 3. H-02 (plan-sign-gate.py) — CONFIRMED CLOSED, no quoting concern

Fired the exact evasion (`plan-merge.py \<newline>sign-approval`) through `plan-sign-gate.py`
directly: exit 2, refused. The dispatch asked whether the refusal echoes the command "as bash
reads it" or as typed, and whether that could be confusing — **it does neither.** `REASON`
(`plan-sign-gate.py:46-57`) is a single static string, verbatim for every denial, that never
interpolates the command line at all. It names the verb (`sign-approval`, four times) and the
sanctioned route (the other four verbs, plus the main-session-only remedy command). No quoting
form to be confusing about — this closes the dispatch's question cleanly in the fix's favor.

### 4. plan-merge.py `_verify_signature` (med-2) — CONFIRMED, message is fully actionable

Ran `plan-merge.py sign-approval` against a real fixture plan carrying a duplicate
`approved_by: null` / `approved_by: stale-signer` block:

```
REFUSED: the signature does not reload as written — approval.approved_by would not say what was
signed.
  asked for: 'Mike Ruangutai'
  reloads as: 'stale-signer'
```

Exit 5, plan left byte-identical on disk. Names the field (`approval.approved_by`) and both
values. `plan-merge.py:271-306`. No finding.

### 5. check-plan-routes.py's top-level `status` VIOLATION (F-13, cycle 0, still open) — RE-MEASURED, unchanged

Built two independent fixture plans (different feature ids `FEAT-98-fixture-a` /
`FEAT-97-fixture-b`, different task ids) both carrying `status: Sideways`, ran the real
`check-plan-routes.py <path-a> <path-b>` binary:

```
VIOLATION top-level status 'Sideways' is not one of ('backlog', 'plan', 'ready', 'building', 'review', 'done', 'abandoned') (case sensitive)
OK T-01: declared main-session-direct (notes/x.md ungranted)
VIOLATION top-level status 'Sideways' is not one of ('backlog', 'plan', 'ready', 'building', 'review', 'done', 'abandoned') (case sensitive)
OK T-09: declared main-session-direct (notes/y.md ungranted)
```

**Confirmed byte-identical**, still — `check-plan-routes.py:385-387` unchanged since cycle 0
(untouched by this cycle's fix commits). Same low/non-blocking disposition cycle 0 and cycle 1
both gave it: exit code still correctly fails, the value itself is correctly named, only the
"which plan" identity is missing in a batch run. Not new, not regressed, no action needed this
cycle — carrying it forward as still-open rather than re-filing it.

### 6. check-state.sh INV-33 line — CONFIRMED GOOD content; one LOW convention gap

Built a real two-commit git fixture (`plan.yaml` v1 committed, `feature.json.review_sha` pinned
to that commit, `plan.yaml` v2 committed with an added task) and ran the real `check-state.sh`
against it:

```
VIOLATION  FEAT-96-fixture: review_sha da3554b55ac39c0e34c770d37aa5ac63272d4bb0 is STALE —
plan.yaml has changed since it was pinned, last at 9cb3102, so the review claim covers text that
is no longer there (INV-33).
```

Names the feature, the pinned sha, the file, and the last commit that touched it —
`check-state.sh:556-558`. **No task id or value, and that is correct, not a gap**: INV-33 is
FEATURE-scoped (about the review_sha pin), not task-scoped, so there is no task/value to name.
Do not conflate this with INV-26 (task-scoped: feature, task id, issue #, and the plan-vs-board
value, confirmed present at `check-state.sh:1849-1885` and matching BRIEF.md's SC-13 wording
exactly, which at this pin correctly cites INV-26, not INV-33 — the conflation my own cycle-1
artifact flagged does **not** recur here).

Is it "distinguishable at a glance" from FEAT-45's INV-32 lines? Yes, but by an inconsistency:
grepped every `bad.append` call in the file (`grep -oE 'bad\.append\(f?"INV-[0-9]+'`) — **every
other** numbered invariant (INV-9, 15, 24, 25, 26, 27, 29, 30, 31, 32 — 20+ call sites) opens
with `"INV-NN: ..."` as a **prefix**. INV-33 is the only one that puts its own number in a
**parenthesized suffix** at the end of the sentence instead (`...(INV-33).`). Confirmed by direct
count, not assumption (repo Expertise P-14). **LOW, non-blocking**: a bare `grep INV-33` still
finds the line; only a habitual `grep "INV-33:"` (matching the house convention) would miss it.
Worth a one-line style fix, not a gate.

### 7. BUG-1055 / SC-08 surface — nothing operator-facing says it, confirmed by grep

Grepped `check-state.sh`, `check-plan-routes.py`, `check-domain.sh` for `1079` and `BUG-1071`:
zero hits for `1079` anywhere; `BUG-1071` appears only in code **comments** for the unrelated
INV-32 era guard, never in a printed string. Separately confirmed `BUG-1071-inv32-era-guard`'s
`feature.json` really does carry `"status": "Review"` with no `plan.yaml` beside it — exactly the
one-file exception the handoff describes. **No check, invariant, or CLI message an operator would
actually run says anything about this exception or points at issue #1079** — it lives only in
`notes/handoff-build.md` and `BRIEF.md` prose. Judged legitimate, not a hole: the Dead Ends list
gives a reasoned, three-way argument against each alternative (deleting the key destroys the only
non-terminal record; fabricating a plan.yaml for another feature is not this feature's business;
amending SC-08 is a scope call the builder doesn't own), and the exception is already
ticket-tracked (#1079). Advisory only, does not gate.

## Accessibility / theme parity

N/A, unchanged from cycle 0/1 — every surface audited above is stderr/CLI text, no colour-only
encoding, no rendered theme.

## Unexamined

- Did not re-audit `gh_board.py`, `worktree_terminal.py`, `board_lifecycle.py`, or `gh-sync.py`'s
  operator-facing text — cycle 0/1 already passed these and this cycle's fix commits
  (`707b547`, `5dc5374`, the BUG-1055 migration) never touch them; confirmed via
  `git log --oneline 7c4f0bd..39477a50 -- <path>` for each before excluding it.
- Did not independently re-verify the security-carried finding about `set-feature-station`/
  `set-task-station` lacking caller-identity binding — that is a security-reviewer question about
  who may call a verb, not what its output says; out of my lens.
- Did not run the full unit/integration suites (QA's exclusive domain per the dispatch's
  serialization rule) — all measurements above are single-script invocations against
  hand-built `$TMPDIR` fixtures, never `run-unit-tests.sh` or any `test-*.py`.

```yaml
VERDICT: PASS
DIGEST:
  headline: H-01 PRE and H-02 both hold up under live re-fire with high-quality messages; H-01's POST backstop resolves the right file but reports the wrong one (MED, non-blocking) — and its own new test has the identical blind spot cycle 1's mutation findings were about.
  mode: B
  in_scope: true
  severity_max: med
  findings: 4
  must_fix: []
  states_unspecified: []
  contract_violations:
    - { path: ".claude/skills/harness/bin/check-domain.sh:1570-1575,1127", actual: "POST-mode vocabulary VIOLATION header names _show(target) — the literal symlink path as typed — even when _rel (used for matching) resolved through the link to plan.yaml; test-check-domain.py:2762-2769's own assertion only checks the violated value, never the reported path, so this exact regression shape is untested", specified: "H-01's own PRE fix (check-domain.sh:1518-1521) states the standard: a denial/violation naming only the innocent path 'reads as a malfunction' and must name where the write actually landed" }
    - { path: ".claude/skills/harness/bin/check-state.sh:556-558", actual: "INV-33's message puts its invariant number in a parenthesized suffix, '...(INV-33).'", specified: "every other numbered invariant in this file (20+ call sites: INV-9,15,24,25,26,27,29,30,31,32) opens the message with 'INV-NN: ' as a prefix" }
    - { path: ".claude/skills/harness/bin/check-plan-routes.py:385-387", actual: "two independently-fixtured failing plans (different features, different tasks) render byte-identical VIOLATION lines with no path or feature id — re-measured live, unchanged since cycle 0", specified: "carried forward as F-13, low/non-blocking, per cycle 0 and cycle 1's own disposition; not touched by this cycle's fix commits" }
  a11y: ["not applicable — every surface reviewed is stderr/stdout CLI text, no colour-only encoding, no rendered theme"]
  open_questions:
    - { id: Q1, question: "Should check-domain.sh:1575's POST-mode display use the resolved candidate (mirroring H-01's PRE _via clause) instead of _show(target), and should test-check-domain.py:2766-2769 assert on the reported path the way its PRE sibling (case r9) does?", blocking: false }
    - { id: Q2, question: "check-state.sh's INV-33 line is the only numbered invariant using a suffix '(INV-NN)' marker instead of this file's universal 'INV-NN: ' prefix convention — worth a one-line normalization, or intentional because INV-33's sentence reads better with the number at the end?", blocking: false }
  files_touched: []
  expertise_update: []
artifact: .harness/harness/features/FEAT-41-one-station-vocabulary/notes/review-harness-ui-reviewer-c2.md
```
