# Operator ruling R-7 — merge-gate refusal copy, and the cap raised to 17 — BUG-1309 — 2026-09-08

**BLUF: the operator authorized ONE cycle beyond the exhausted 16/16 budget (`max_total_cycles`
raised 16 → 17) and chose the operator-facing refusal sentence verbatim. The change is
main-session-direct by the plan's own signed lanes rows: no agent may edit `merge-gate.py` or
`tests/integration/test-merge-gate.py`. It needs NO BRIEF amendment and NO re-signature — SC-04 and
SC-10 are satisfied by the new copy as written — and exactly ONE additive plan decision (D-19),
because `T-05`'s intent quotes the OLD sentence verbatim at `plan.yaml:1249-1251`. Two product-owned
artifacts move: `plan.yaml decisions:` (D-19) and the UAT's Steps 3 and 3b.**

## 1. The authorization, recorded

- **Budget.** `feature.json` `max_total_cycles` 16 → **17**, on the operator's explicit
  authorization of one further focused cycle. `cycles_used` stays **16** until this cycle's work
  lands. Raising a budget is a user decision recorded in feature.json (DEC-157); this note is the
  attribution for that write.
- **Scope of the authorization.** The refusal COPY only. Not the gate's logic, not its ordering, not
  the era set, not the ambiguity branch, not the unpinned-repo branch, not the exception branch.
- **The chosen sentence, operator's words:**

  > `<feature>` needs its GitHub mirror recovery completed before this merge can continue.

## 2. The exact production string

`merge-gate.py:192` — the single-owner "receipt owed, repo pinned" deny, and nothing else:

```python
        deny(f"merge-gate: {feat} needs its GitHub mirror recovery completed before this merge can continue. Run: {command_line}")
```

Rendered for the UAT fixture (station resolves `open`):

```
merge-gate: FEAT-9001-uat-scratch needs its GitHub mirror recovery completed before this merge can continue. Run: python3 .claude/skills/harness/bin/gh-sync.py open /private/tmp/bug1309-uat/.harness/harness/features/FEAT-9001-uat-scratch
```

**What it preserves** — the two things the technical contract requires: the feature is NAMED
(`{feat}`), and the recovery command is COPYABLE and complete (`{command_line}`, which
`feature_schema.recovery_command_for` renders as `gh-sync.py open <dir>` or
`gh-sync.py recover-terminal <dir> --yes`). **What it removes** — `github.build_entry=<value>` and
"no Build entry receipt exists for it", the two jargon phrases the operator judged unreadable.

**One micro-decision, mine, reversible, recorded so it can be struck:** the `merge-gate: ` prefix
stays. Every other message this file emits carries it, and the UAT's observation steps identify the
speaking gate by it. Strike it in the edit if unwanted; nothing else depends on it.

## 3. What does NOT change — checked, not assumed

| Artifact | Verdict | Evidence |
|---|---|---|
| `BRIEF.md` SC-04 | **no amendment** | it requires "a reason naming the feature and the re-run command" (`BRIEF.md:108-111`). Both survive verbatim. It never required the recorded value be printed |
| `BRIEF.md` SC-10 | **no amendment** | it requires "a message they can act on without reading the source" (`:157-159`). The new copy strengthens it; this change is that criterion's whole point |
| `BRIEF.md` approval | **no re-signature** | no criterion text moves. Contrast R-6, which re-signed because SC-11 was NEW |
| `T-05` `verify:` | **unchanged** | it matches case NAMES with `grep -qF "ok    $n"` (`plan.yaml:1063-1073`). No case is renamed, so all 26 names still match |
| `merge-gate.py:188` (repo unpinned) | **untouched** | different remedy, and `test-merge-gate.py:70` asserts `"open" not in reason.lower()` on it |
| `merge-gate.py:174` (ambiguity) | **untouched** | `gh-sync.py` must stay absent there — `test-merge-gate.py:162,174` |
| `merge-gate.py:194` (exception) | **untouched** | carries `T-05 empty plan fails closed` (`:127`) |
| `merge-gate.py:180` (era-exempt stderr) | **untouched** | `:93` asserts no `open` token in stderr |
| `post-merge-sweep.sh:230-231` | **untouched** | its own "records github.build_entry" text is asserted ABSENT by `test-hooks-install.py:434`; editing it would be a different task |
| docs / `references/github-mirror.md` | **no change** | grepped: no copy of the deny sentence outside `plan.yaml`, the UAT note and the gate |

## 4. The one plan amendment — D-19, additive

`T-05`'s intent, step 6, quotes the old sentence **verbatim** as the specification
(`plan.yaml:1249-1251`). Left alone it would contradict the shipped code, and a later grader would
read that as drift.

**Route: one new decision, appended.** `plan-merge.py apply` unions by id and leaves the approval
bytes byte-identical (`plan-merge.py` steps 7/7b), so this needs no re-plan, no panel re-run and no
re-signature. **Not** an `amend` of T-05's intent: rewriting an executed, approved specification to
match code written afterwards erases that the operator changed their mind, and PRINCIPLES rule 15
forbids exactly that. The intent stays as the historical record; D-19 names it superseded.

- **Next free decision id: `D-19`** (highest present is D-18).
- pm drafts the `choice:`/`because:`/`dec: DEC-174` body; the orchestrator applies it verbatim
  through `plan-merge.py apply` (plan.yaml has one write route, and it is a verb).

## 5. The direct implementation packet — main session only

**Lane authority:** `plan.yaml:47-49` (`merge-gate.sh and merge-gate.py` → `main-session-direct`),
`:73-75` (`tests/integration/test-merge-gate.py` → `main-session-direct`), `T-05
execution_mode: main-session-direct` (`:1047-1048`), D-11 (`:139-157`). `check-domain.sh --resolve`
returns `harness-backend-dev`/`harness-dev-ops`/`harness-qa` for these paths and the signed
carve-out rows OVERRIDE it. **No agent edits either file.**

Worktree: `/Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-1309-mirror-build-entry`.

### 5.1 Source — one line

`.claude/skills/harness/bin/merge-gate.py:192` → the string in §2. Nothing else in the file.

### 5.2 Tests — exactly two assertions re-anchor

`tests/integration/test-merge-gate.py`. **Case names are byte-frozen** (T-05's `verify:` matches
them with `grep -qF`). Only the predicates move:

1. **`:64-65` `T-05 recovery-required denies`** — `"recovery-required" in reason` no longer holds;
   the value is deliberately gone from the copy. Re-anchor it onto the copy contract itself, which
   is what the operator now cares about and what no case asserts today:
   `r.returncode == 0 and d == "deny" and "needs its GitHub mirror recovery completed" in reason`.
   The fixture stays `entry="recovery-required"`, so the case still proves that state denies.
2. **`:99-102` `T-05 unresolvable gh falls back and denies a locally owed receipt`** —
   `"absent" in reason` no longer holds. Re-anchor onto the two contract tokens:
   `r.returncode == 0 and d == "deny" and "FEAT-9001-fixture-non-era" in reason and "gh-sync.py open" in reason`.

Every other reason assertion in the file survives unedited — verified line by line:
`:68` (feature + `gh-sync.py open`), `:70`, `:93`, `:96-97`, `:122`, `:127-128`, `:159-163`,
`:172-174`, `:181-182`, `:205-206`, `:217`, `:226`, `:234`.

### 5.3 UAT — pm's, routed through product lead in this cycle

`notes/uat-BUG-1309-mirror-build-entry.md`: the Step 3 quoted block (`:159-164`) and the Step 3b
observe line (`:209-211`, which names `github.build_entry=recovery-required`). Step 6's expectation
(`:300`, "a `deny` naming `recover-terminal … --yes` — **not** `open`") stays TRUE under the new copy
and must not be touched. No step renumbered, no step added, PASS/FAIL rules otherwise unchanged.

### 5.4 Validation — after the source and test edits, in this order

```bash
cd /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-1309-mirror-build-entry
out=$(python3 tests/integration/test-merge-gate.py); echo "rc=$?"; printf '%s\n' "$out" | grep -c '^FAIL'
```

- Expect `ALL PASSED`, `rc=0`, `0` FAIL lines, 36 `ok` lines (the c18 baseline —
  `notes/qa-c18.md` §1). Read the count from a variable, never a pipe.
- **Discrimination:** on a scratch copy of `merge-gate.py`, drop `{feat}` and then `{command_line}`
  from the new string; `T-05 non-era absent build_entry denies naming feature and re-run command`
  must redden each time. Drop the sentence itself; the re-anchored `:65` case must redden. Restore
  and byte-verify with `git status --porcelain` before committing.
- **T-05's own `verify:`** (`plan.yaml:1063-1073`) end to end — it also runs
  `tests/unit/test-omp-hooks.py`, `merge-settings.py --check`, and the `code-grade.py` floor
  (min grade ≥ 4 over `git_merge`/`words`/`direct_merge`/`gh_merge`). A string edit cannot move the
  grade, but the verify is the gate of record and should print `VERIFY-PASS`.
- **Re-pin `review_sha`** to the commit carrying this change before any validator sees it (INV-6,
  P-02). The current pin `9fe5cf31` predates it.

### 5.5 Non-goals for this cycle

No ship, no merge, no PR, no `gh-sync.py` station write, no validator panel, no formatter, no linter,
no project-wide suite. The three backlog remedies recorded in
`notes/research-BUG-1309-c18-sc04-ruling.md` (the clause-(f) `"branch" in reason` conjunct, the gap-B
fixture ordering) are NOT in this cycle and stay open.

## 6. Order of operations

1. D-19 drafted (pm) → applied by the orchestrator through `plan-merge.py apply`.
2. UAT Steps 3/3b amended (pm) to the §2 string.
3. **Main session** edits `merge-gate.py:192` and the two assertions; runs §5.4; commits; re-pins.
4. SC-10 hand test — still owed, still the ship blocker.
