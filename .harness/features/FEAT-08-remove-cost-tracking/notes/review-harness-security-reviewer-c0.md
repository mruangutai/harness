# Security review — FEAT-08-remove-cost-tracking — c0

**Verdict: PASS.** No security findings. Diff reviewed at the pin `942505e` (against base `ae2443d`),
not the working tree (working HEAD is `ebea32e`; see Provenance for the full drift list, none of
which touches this feature's paths).

## Scope

In scope: this diff removes an *invariant* from `check-state.sh` (INV-11: completed runs must carry
a `cost:` block) and a *required schema field* (`cost_usd`) from `validate-digest.py`'s orchestrator
schema. Both are guards other agents' returns route on, so a loosened guard is a trust-boundary
question (STRIDE: Tampering) even though the feature is a deletion, not new input handling. That is
why this panel is in scope rather than n/a, despite the diff having no new user input, auth, or
network surface (this codebase has none — Expertise P-01). Confirmed against `validate-digest.py`'s
own schema for the `reviewer` persona group (`harness-security-reviewer` maps to it, line 192): it
allows `severity_max: n/a` + PASS only for a genuinely-declined judgment (DEC-173, e.g. a UI reviewer
on a non-UI diff); since I judged two live guards and reached a conclusion, `n/a` is not the honest
value here — `info` is.

## What I checked, and result

1. **`check-state.sh` INV-11 removal** (`.claude/skills/harness/bin/check-state.sh`) — the check that
   rejected a `status: complete` run with no `cost:` block is gone. This is a business-logic
   completeness check, not an authorization or input-validation gate — nothing an attacker controls
   changes state. `cost` stays in `CHECKPOINT_KEYS` for backward parse-compatibility with 67
   pre-FEAT-08 `state.yaml` files; this widens what is *accepted*, but only to admit a
   spelling already legal before the change, never a new shape. Not a finding.
   - Checked for a fail-open regression from the deletion specifically: the deleted hunk contained
     `import datetime`, used only by the removed staleness check. Grepped the pin
     (`git show 942505e:.claude/skills/harness/bin/check-state.sh | grep -n datetime`) — zero
     remaining references anywhere in the file. Then went beyond the grep and **ran** the fixture
     suite rather than trusting static inspection alone (the panel's own T-10 lesson — a defect that
     reading missed was found only by running): `python3 .claude/skills/harness/bin/test-check-state.py`
     → `ALL PASSED`, exit 0, including case (k) which exercises both the "no cost: block" and "with a
     cost: block" completed-run paths against the live script. No `NameError`, no non-2 exit, no
     silent fail-open (Expertise G-01 checked and clear, now by execution not just by reading).
   - The working tree under `bin/` equals the pin for this purpose: `git log --oneline --name-only
     942505e..ebea32e -- .claude/skills/harness/bin/` is empty and `git status --porcelain` shows no
     dirty file under `bin/`, so running the tests against the working copy is running them against
     `942505e`.

2. **`validate-digest.py` schema loosening** — `cost_usd: str` dropped from the required
   `orchestrator` schema. A digest that still carries the field is *ignored*, not rejected (comment
   confirms this is measured behaviour, not new). No security-relevant field (status, routing,
   `feature`) was touched; nothing bypasses type-checking. Ran the fixture suite:
   `python3 .claude/skills/harness/bin/test-validate-digest.py` → `ALL PASSED` (62/62 CLI, 14/14
   hook, 2/2 template), including the paired case asserting a digest missing `cost_usd` now passes
   where it previously failed. Measured, not inferred.

3. **Deleted `cost-report.py` — dangling invocation / orphaned reader check.** Re-ran the sweep
   pinned at `942505e` (not the working tree, per dispatch instruction), excluding `worktrees`:
   `git grep -n "cost-report" 942505e -- .claude/ docs/ .harness/`. Every hit is in `docs/harness/{DECISIONS,SPEC,BUILD,DECISIONS-INDEX}.md`
   (sanctioned survivors, A-4) or in feature-history Markdown (`BRIEF.md`, `PLAN.md`, `STATE.md`,
   `feature.yaml`, `logs/`) — no live code, agent definition, or skill file references it.
   `run-unit-tests.sh`'s `SCRIPTS` array no longer names `test-cost-report.py`, and both the script
   and its test are deleted (`git show 942505e` — files absent). No commits land between the pin and
   current HEAD that touch `bin/` (confirmed empty, above), so the pin and the current tree agree on
   this surface.

4. **Orphaned transcript-reading / data-exposure code.** `cost-report.py` was the only consumer that
   read transcript JSONL for cost attribution; it is fully deleted. Swept
   `.claude/skills/harness/bin/` at the pin for `transcript`/`.jsonl`: only `harness_yaml.py`
   (unmodified by this diff — session/transcript-path resolution for an unrelated bootstrap purpose)
   and one unrelated comment in `check-state.sh` remain. Nothing left reachable that derives cost
   data from transcripts.

5. **Deserialization / YAML loader.** `harness_yaml.py` is not in this diff's file list
   (`git diff --stat ae2443d..942505e`); no loader, `safe_load` call, or untrusted-YAML entry point
   changed.

6. **Secrets sweep.** Full diff swept for credential/token/key patterns
   (`api[_-]?key|secret|token|password|BEGIN (RSA|OPENSSH|PRIVATE)|Bearer |AKIA...`) — every hit is
   prose about token *pricing* (input/output/cache tokens) or grep search-token discussion in
   BRIEF/PLAN, not a credential. Nothing to report.

7. **Config/docs diffs** (`.harness/harness.json`, `templates/harness.json`, `build.yaml`,
   `review.yaml`, `harness-orchestrator.md`, `harness-team/SKILL.md`, `harness/SKILL.md`) — all
   consistent, symmetric removal of `cost_model`/`budgets.per_*_usd`/`cost_usd` fields and the
   matching prose. The cycle-budget hard-bound (`max_total_cycles`, `BLOCKED` on exhaustion) is
   explicitly preserved and untouched in every file — the one guard with real teeth is not weakened.

## Open question (non-blocking)

Dispatch said 22 commits in the range; `git log --oneline ae2443d..942505e` returns **21**. Does not
change any conclusion above (content reviewed by path/content, not by commit count) — flagged so it
does not silently propagate into the orchestrator's digest as a reviewed-and-confirmed number.

## Provenance

- `git rev-parse HEAD` = `ebea32e3c6b923943773494bf3fa1c86d54cd35b` (branch
  `feat/FEAT-08-remove-cost-tracking`).
- `git status --porcelain`, re-checked after writing this artifact: `.harness/notes/perf-review-agent-workflow-2026-08-04.md`
  modified; untracked: `.harness/logs/2026-08-05.md`, `.harness/notes/perf-roadmap-2026-08-05.md`,
  and three sibling panel artifacts (`review-harness-qa-c0.md`, `review-harness-ui-reviewer-c0.md`,
  this file) written concurrently by other panel members / by me. None are FEAT-08 source paths;
  none touch anything reviewed above.
- All decisive greps, file reads and test runs for the checks above were re-run pinned at `942505e`
  explicitly (or, for the two test suites, against the working copy of `bin/`, confirmed identical
  to the pin — see check 1).
