# Security review — FEAT-37 (lead-stop-and-wake) — scoped OUT, PASS

**Verdict: PASS, `severity_max: n/a`.** This diff has no security surface for this role to judge.
It is governance prose (a never-wait/refusal-bound rule for leads and orchestrators), one docstring
wording fix, one static test-list array entry, a new pure-stdlib test file with no I/O beyond
reading fixtures under the test's own temp dir, and a backlog note. No input it did not author, no
output a human/system will interpret differently, no credentials, no data belonging to someone else.

## Base-sha correction (measured, not the dispatch's stated command)

The dispatch named "9 changed files" but its own suggested command, `git diff --stat
8fc87f8..4e652f9`, returns **141** files — it pulls in an unrelated `git merge main` that landed
the whole FEAT-42-one-root-resolver feature into this branch between those two points (confirmed:
`git merge-base --is-ancestor 8fc87f8 4e652f9` → yes, but the file list includes `.omp/agents/*`,
`FEAT-42-one-root-resolver/*`, etc. — none of which the dispatch describes).

I derived the correct base by finding the commit whose diff to `4e652f9` reproduces exactly the 9
named files: **`766d7b6`** (parent of `8a3653e`, the commit that added the backlog note — needed as
the base precisely because the note must appear as an *addition* in the reviewed diff).
`git diff --stat 766d7b6..4e652f9` yields exactly:

```
.claude/skills/harness-team/SKILL.md
.claude/skills/harness/bin/inflight_registry.py
.claude/skills/harness/bin/run-unit-tests.sh
.claude/skills/harness/bin/test-inflight-registry.py
.claude/skills/harness/bin/test-lead-stop-and-wake.py
.harness/harness/docs/DECISIONS-INDEX.md
.harness/harness/docs/DECISIONS.md
.harness/harness/docs/SPEC.md
.harness/notes/backlog-orchestrator-inoculation-2026-08-27.md
```

All 9 files reviewed against this base. Logged as an observation for the next spawn
(`observations/harness-security-reviewer.md`).

## Census (commands run, counts)

Diff-added lines across the 9 files, checked for:

- `subprocess|os\.system|eval\(|exec\(|\.\./|shell=True` → **1 hit**, and it is negative evidence:
  `test-lead-stop-and-wake.py:24`'s own docstring — *"Stdlib only, no subprocess."*
- `api[_-]?key|secret|password|token|bearer|-----BEGIN|ssh-rsa|AKIA...` → **5 hits**, all in
  `DECISIONS-INDEX.md`'s `@NNNN` line-anchor rows referencing *context* "token" counts (e.g.
  `~15.3k tokens`, `budgets.orchestrator_context_warn_tokens`) — no credential material.
- `DECISIONS-INDEX.md` diff itself: confirmed pure line-anchor (`@NNNN`) churn, zero content-line
  changes, matching the dispatch's own framing ("three rows... rest is anchor churn" — the three
  content rows, DEC-70/199/201, live in `DECISIONS.md`/`SPEC.md`, not the index).
- `test-lead-stop-and-wake.py` (641 new lines): grepped for `subprocess|os\.system|eval\(|exec\(|
  pickle|yaml\.load|requests\.|urllib|socket|shell=True` → only the negative docstring hit above.
  Its one `open(` is a read of a path built from the file's own `__file__`-derived repo root
  (test fixture pattern), not attacker-influenced input.

## The one file worth a real look — `inflight_registry.py`

Read the file whole (`git show 4e652f9:.claude/skills/harness/bin/inflight_registry.py`, 350
lines) rather than just its diff, since the dispatch flagged it as the process/state registry.
**The change in this diff is a 4-line docstring/message wording fix in `children_refusal_lines`**
(correcting a "fires once" claim to the measured "at most once per consecutive stop sequence,
re-fires on later wake" bound) — no logic changed.

Whole-file check, since it was in scope regardless of diff size:

- **Path construction**: `_registry_path(root)` is `os.path.join(root, ".harness/.inflight-claims.json")`
  — `REGISTRY_REL` is a module constant, never built from caller input. `root` comes from
  `harness_boundary.resolve_root` or an explicit `--root` CLI arg (operator-supplied, not
  attacker-reachable from a hook payload).
- **Untrusted content it reads**: the registry JSON itself. `_parse` treats anything that isn't a
  parseable JSON object as an *empty registry* and reports to stderr rather than raising —
  correctly fails toward "no claims exist," not toward trusting attacker-shaped structure.
  `_expire` treats a non-dict claim entry or a non-numeric `started_at` as expired rather than
  crashing (also correct: a malformed entry is dropped, not trusted).
- **Fail-open vs. fail-closed**: `release()` explicitly refuses (returns `0`, releases nothing)
  when more than one live claim exists for an agent, rather than guessing which to release —
  documented as the fix for issue #628 (a prior wrong-claim-released defect). This is the
  fail-*closed* direction on a control action. The one deliberate fail-open is `LOCK_TIMEOUT_SECONDS
  = 1.0` causing `claim()`/`release()` to raise on contention rather than hang — callers are
  required by docstring to wrap it, consistent with D-07's stated fail-open posture for this
  registry (a defence-in-depth question about caller compliance, not a defect in this file, and
  unchanged by this diff).

No finding here. This is whole-file due diligence on an unchanged-logic file, not a gap in the diff.

## Threat model

Nothing in this diff crosses a trust boundary: no new input source, no new output consumer, no new
credential, no new cross-user data path. STRIDE table is empty by construction.

```yaml
VERDICT: PASS
DIGEST:
  headline: "No security surface — prose/rule-text + docstring wording fix + one static test-list entry + a stdlib-only test file; base-sha in the dispatch was wrong (141-file range pulled in an unrelated merge), corrected to 766d7b6..4e652f9 which reproduces the stated 9 files exactly"
  in_scope: false
  scope_reason: "9-file diff (verified against corrected base 766d7b6): governance/decision prose (SPEC.md, DECISIONS.md), pure line-anchor churn (DECISIONS-INDEX.md), a playbook markdown edit (SKILL.md), a 4-line docstring wording fix in inflight_registry.py, one hardcoded string appended to a bash array (run-unit-tests.sh), two test files (one wording-assertion tweak, one new stdlib-only fixture-based test), and a backlog note already settled per dispatch. No input, output-to-interpret, credential, or cross-user data path touched."
  severity_max: n/a
  findings: 0
  must_fix: []
  threat_model: []
  open_questions:
    - { id: Q1, question: "The dispatch's stated diff command (git diff --stat 8fc87f8..4e652f9) returns 141 files including an unrelated merged-in feature (FEAT-42), not the 9 described. I derived and reviewed against the base that reproduces the stated 9 (766d7b6). Confirm 766d7b6..4e652f9 was the intended round, or point me at the actual intended range if this was meant to cover more.", blocking: false }
  files_touched: []
  expertise_update: []
artifact: .harness/harness/features/FEAT-37-lead-stop-and-wake/notes/review-harness-security-reviewer-panel-2026-08-27.md
```
