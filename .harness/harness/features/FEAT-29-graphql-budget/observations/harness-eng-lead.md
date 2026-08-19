# Observations — harness-eng-lead — FEAT-29-graphql-budget

- 2026-08-19: Re-dispatch of T-03 c3 arrived stating "nothing landed" and citing an empty
  `git diff --stat` on `.claude/skills/harness/bin/`. Both halves were false at read time.
  `factory_gh.py:151` held `if True:  # MUTATION PROBE 1: gh_cost_log.measured() wrap removed`
  — an unreverted probe, with `_cost.returncode = r.returncode` also gone — and
  `test-gh-cost-log.py:262-379` already carried the complete eight-check wrap-site section
  (`_load_gh_sync()` via importlib, `_counting_fake()`, four ON/OFF blocks). The receipt was
  genuinely absent, which is what the "nothing landed" inference was built on. Lesson: an absent
  receipt is evidence about the RECEIPT, not about the working tree. A member killed mid-run
  leaves source behind and, worse, may leave it MUTATED — so read the wrap sites before
  re-dispatching a mutation-proof task, never infer tree state from artifact absence.

- 2026-08-19: I passed `model: opus` in the T-03 dispatch and `dispatch-guard.sh` blocked it
  (DEC-152/155). My predecessor lead made the identical error on the identical dispatch one run
  earlier (recorded in `runs/2026-08-19-05-eng/digest.md`, "Dispatch note"), and my own Expertise
  already carries G-16 telling me to audit dispatch parameters before sending. A gotcha I hold
  did not fire at the moment it applied. Two independent lead contexts hitting the same guard on
  the same task suggests the pull is situational — a task framed as hard invites reaching for a
  stronger model — not a personal slip. The guard caught it both times, which is the guard
  working; the cost is one wasted dispatch turn each time.

- 2026-08-19: `gh-sync.py`'s `gh()` calls `skip()` on non-zero rc, and `skip()` is `sys.exit(0)`
  (`gh-sync.py:79-82`). So a failing-rc fixture driven through that wrapper terminates the test
  script with exit 0 — it would read as a clean pass while silently truncating every later check.
  The rc=0-only fixture in the wrap-site tests is therefore forced, not a coverage gap. Related
  trap for mutation 2: deleting only the `with` at `gh-sync.py:115` leaves `_cost.returncode` at
  `:117` referencing an undefined name, which raises inside the test and ABORTS the suite rather
  than reddening a named check — and an abort is not evidence. The wrap removal must drop both
  lines, which is exactly what probe 1 did to `factory_gh.py`.
