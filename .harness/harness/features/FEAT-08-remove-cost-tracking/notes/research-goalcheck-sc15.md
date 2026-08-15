# Goal-check — FEAT-08-remove-cost-tracking — all 15 SCs

## BLUF

**The result is inverted.** The three criteria that read red are red on **rotted wording** with
correct code behind them (SC-05, SC-06). The criteria that read green are the ones with **live
violations** behind them. One criterion is genuinely false: **SC-15**.

- **12 met · 3 not_met** (SC-05, SC-06, SC-15). No `partial`.
- **REQ-08 is still violated at the graded tree.** MF-1 (`.claude/commands/harness.md:18`, `:83`) and
  MF-3 (`.harness/expertise/harness-orchestrator.md:5-7`, `:10`, `:62`) are **both live**. MF-2
  (`org.html`) is fixed.
- **Verdict: FAIL.**

## Tree graded — stated per the dispatch

| | |
|---|---|
| Graded commit | **`7d9edde`** (HEAD, branch `feat/FEAT-08-remove-cost-tracking`) |
| Working tree == HEAD? | **Yes** for every path I grepped: `git diff --quiet HEAD -- .claude/ docs/ .harness/harness.json .harness/team-config.yaml .harness/README.md` → exit 0; `git diff --quiet HEAD -- .harness/expertise/` → exit 0 |
| Base for diff clauses | `ae2443d` |

**Premise 1 — CONFIRMED, but the briefing's reasoning was wrong.** `git diff --name-only
8958840..7d9edde` returns exactly one path: `.harness/features/.../feature.yaml`. `org.html` landed
**inside** `8958840` (`git diff --name-only 8958840^..8958840` → `docs/harness/org.html` +
an observations file), not after it. The claim holds; my briefing's rebuttal of it did not.

**Premise 2 — BROKEN. The pin IS deleted; A-4 §0's "not yet done" is stale prose.** Commit
`00f3e03` landed A-4's follow-up edits. `git grep -n <5 tokens> 7d9edde -- test-validate-digest.py
test-check-state.py` → **no output**. SC-01's amended command returns exactly, verbatim:
`docs/harness/BUILD.md`, `docs/harness/DECISIONS-INDEX.md`, `docs/harness/SPEC.md`,
`docs/harness/DECISIONS.md` — the four-file expected set, nothing outside it. **SC-01 is met.**

## The fifteen — verdict, and method sufficiency on two axes

| SC | Verdict | token | scope | Sufficiency finding |
|---|---|---|---|---|
| SC-01 | met | **FAIL** | **FAIL** | The clean illustration. All five tokens are **compound**; MF-1 sat *inside* the scope path and was invisible to every one (`cost vs budget`, plain English) → **token**. MF-3 (`.harness/expertise/`) is *outside* the stated path entirely → **scope**. Met on a method that cannot detect the class it exists to detect. |
| SC-02 | met | OK | OK | Sufficient. `run-unit-tests.sh:9-24` exits 2 on any unlisted `test-*.py`, so a reinstated `test-cost-report.py` fails the same command — the absence claim is actively policed, not merely observed. |
| SC-03 | met | OK | **FAIL** | **False-negative-producing, the opposite direction from SC-01.** Repo-wide, so unrelated in-flight state can fail it. Already visible: its output's only content is 8 `note` lines, one of which is FEAT-08's own orphaned `goalcheck-product` run dir — nothing to do with cost. Hazard dormant only because FEAT-09 is in a worktree (Q6). |
| SC-04 | met | OK | OK | Sufficient. The detector was **red at `ae2443d`** for the missing required field, per its own comment (`test-validate-digest.py:765-769`) — a passing green that only the deletion can produce. |
| SC-05 | **not_met (wording)** | OK | **FAIL** | Line-granularity diff used as proxy for a semantic claim → **false positive**. Clause 1 met; clause 2 literally fails on one line. Intent fully satisfied. |
| SC-06 | **not_met (wording)** | OK | **FAIL** | The glob `*/` over-captures FEAT-08's own dir, which postdates the base. Numbers below. Delivery is correct; the glob rotted. |
| SC-07 | met | OK | OK | Sufficient — eight **enumerated** keys, both files, plus a parse check. A key surviving under a new spelling is the only escape, and D-04 named the one consumer. |
| SC-08 | met | OK | OK | Sufficient, and the strongest method in the feature: the regeneration diff makes a hand-edit that the generator would overwrite an automatic failure. |
| SC-09 | met | OK | OK | Sufficient for what it claims. `inspection` is the right method — "states its reason well enough that a future scan does not re-propose it" is a judgement no grep makes. |
| SC-10 | met | OK | OK | Sufficient. `check-docs.sh`'s registry is `DECISIONS.md` itself, so its 45 superseded patterns are the propagation check. |
| SC-11 | met | OK | OK | Sufficient — whole-suite, not per-task, which is exactly the FEAT-07 failure it was written against. |
| SC-12 | met (by content) | OK | **FAIL** | **Anchor drift is the finding.** Anchors are line numbers taken at the base; **4 of 12 are dead at the graded tree**. An `inspection` criterion anchored on line numbers is unverifiable as written after ~21 commits. Content survives everywhere — I verified by content. |
| SC-13 | met | **OK — the counter-example** | OK | **The only criterion in the feature using the plain English token** (`grep -n -i -e cost`), and it returns **empty**. This is what would have caught MF-1-class prose inside its scope. It proves the token axis is a real, fixable gap and not an unavoidable one. |
| SC-14 | met (literal) | OK | OK | I graded the **literal** reading, as asked: every one of the 6 hits carries the marker **on the same line**, so the adjacent-line loophole is not exercised. Scope is bounded to two named files by the criterion itself — deliberate, and SC-01 covers the rest. |
| SC-15 | **not_met (real)** | **FAIL** | **FAIL** | Its own leading sentence — "a dispatched agent reading only its rules finds nothing that would make it emit a cost figure" — is **false**. Expertise reaches agents by the `SubagentStart` hook and is unambiguously "its rules". The "Specifically," list enumerates five files; it does not exhaust the claim. |

### SC-12 anchor drift, enumerated

`SKILL.md:127`→**`:122`** ("cost a working day"); `:229`→**`:224`** ("square of session length");
`:110` is now `## The question round-trip`, **not a cycle-budget line**; `harness-team/SKILL.md:265`
is **past EOF** (file is 261 lines). `SKILL.md:21` and the three fixture files are correct.
Separately: A-4 §1 cites the SPEC marker at `:2129`; it is at **`:2126`**.

### SC-05 — the literal failure, so nobody routes a fix at correct code

`git diff ae2443d..HEAD -- check-state.sh SKILL.md | grep -E '^[-+].*cycles_used'` returns:

```
-    "cycles_used", "cost",
+    "cycles_used",
```

A changed line mentioning `cycles_used`. **Intent is satisfied**: `max_total_cycles` and
`_max_total_cycles_rationale` are present and byte-identical in both configs
(`.harness/harness.json:137-138`, `templates/harness.json:139-140`), and the change only split
`"cost"` onto its own line under a four-line HISTORICAL-ONLY comment (`check-state.sh:331-335`) —
whose own text says it avoids the quoted spelling *because a `verify:` counts that spelling*.
**Red on wording, not on delivery.**

### Q5 — SC-06, both numbers, and the call

| Reading | `feature.yaml` hits | `state.yaml` with `^cost:` |
|---|---|---|
| Glob **as written** (`.harness/features/*/`) | **92** | **69 of 75** |
| Restricted to `FEAT-01..07` | **89** ✓ | **67 of 67** ✓ |

**Verdict on the plain reading of the glob as written: not_met.** **The criterion means
`FEAT-01..07`**, and its own text pins that: it states 89 as "its value at `ae2443d`" and 67 as
"67 of 67" — FEAT-08's own directory did not exist at `ae2443d`, so it cannot be in a figure taken
there. FEAT-09 is in a worktree and contributes nothing; the entire delta is FEAT-08 itself.
**The historical record IS byte-identical. Only the glob rotted.**

### Q18, SC-04 — coverage state as a fact, no proposal

The pin is deleted and gets no replacement (RULED, issue **#104**). SC-04's surviving half is met on
the named passing test. Consequence, stated not softened: **the committed suite now asserts
unknown-key tolerance only incidentally** (A-4 §4's mutant run). Behaviour is safe; coverage is thin.
No fixture proposed.

## The two live violations — REQ-08 is not closed

- **MF-1 — `.claude/commands/harness.md:18`** (`cost vs budget` column) **and `:83`**
  (`Log every return (one line: feature, verdict, status, cost)`). Instructs the **main session** —
  the user channel — to render figures that no longer exist. Inside SC-01's scope, invisible to all
  five tokens. Routing: **MAIN-SESSION-DIRECT** (`.claude/commands/` is in no domain).
- **MF-3 — `.harness/expertise/harness-orchestrator.md:5-7`** (P-01, `by_agent` cumulatives, "the
  reporter … exits 1 on unpriceable models"), **`:10`** ("Staged runs owe no cost append"), **`:62`**
  ("Put comments on the verdict or cost line instead"). Injected into **every** orchestrator spawn.
  Routing: an **orchestrator distillation op**, whose window closes at feature close — now.
- **MF-2 — CLOSED.** `org.html:167` now reads "feature-wide cycle budget"; the "Cycles bound; cost
  informs" card is gone; `:302` is the context budget (protected by REQ-10).

## Open questions

- **Q1 (not an SC) — `.claude/commands/harness.md` is in no criterion's scope.** SC-15 enumerates
  five rule surfaces and omits the most user-visible file in the repo. A reasonable reader calls
  this part of "done"; the BRIEF never said so. **Recommend: fix MF-1 before ship.** Blocking.
- **Q2 (not an SC) — `.harness/expertise/` should join the standing sweep scope** (panel Q4). It is
  the most-executed rule surface in the repo and no criterion in this feature searched it. This is a
  harness-design call, not a FEAT-08 fix. Non-blocking.
- **Q3 — SC-05 and SC-06 need a wording correction, not a fix cycle.** Both are red on their own
  text with correct code behind them. Editing a signed criterion is the user's call; the alternative
  is shipping with two `not_met` that mean nothing. Non-blocking.
- **Q4 (not an SC) — SC-12's line-number anchors are dead.** Recommend inspection criteria anchor on
  **content strings**, never line numbers. Non-blocking.
- **Q5 — SC-03 is repo-wide and false-negative-producing.** It passed here. Naming it, not fixing
  it. **The `CLAUDE_PROJECT_DIR` re-root is forbidden by user ruling and is not proposed.**
  Non-blocking.

## Not proposed, deliberately

No fix authored. Nothing committed. `must_fix` is **not a key in the `pm` DIGEST schema**
(`validate-digest.py:141-144`), so the two live violations ride up as `blocking: true` open
questions plus the headline. No `cost:` key written anywhere.
