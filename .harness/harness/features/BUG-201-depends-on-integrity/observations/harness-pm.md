# Observations - harness-pm

- 2026-09-06: BUG-201 — `check-domain.sh --resolve` on a feature `notes/<name>.md` path returns
  `harness-orchestrator` ONLY, so a task whose deliverable is a note under a feature's `notes/`
  cannot be given to a dev specialist. I had planned a dev-ops task to record the before/after
  corpus verdict as a note and had to fold that proof into a permanent unit assertion (T-04) plus
  the BRIEF's recorded `af859ee8` baseline instead. Check the resolve before planning any
  note-authoring task.
- 2026-09-06: BUG-201 — `plan-merge.py` has no `--help` on `check-plan-routes.py` (it prints
  `ERROR: --help does not exist` and needs a plan path), and `run-unit-tests.sh` takes only
  `--kind unit|integration|all` with no per-file flag, so a single-file `verify:` must be
  `python3 tests/<kind>/test-<name>.py` directly.
- 2026-09-06: BUG-201 — the write route needed NO new code: `plan-merge.py:_schema_error` already
  calls `validate_plan_doc`, and its do-no-harm gate only fires when the base was legal. Measuring
  that first turned a two-file change into a one-file change and made REQ-03 free.
- 2026-09-06: BUG-201 panel transcription — a first-cycle plan.yaml is UNTRACKED, so the dispatch's mandated `git diff --stat` proof is empty and proves nothing. Took a pre-write copy BEFORE running set-panel and compared the post-write file with the panel block excised (lines 70-152, bounded by the next column-0 key) byte-for-byte: 13808 -> 17559, remainder equal. The copy must be taken first or the evidence is unrecoverable.
- 2026-09-06: computing PF- ids by importing panel_findings.finding_id inside the same script that yaml.safe_dumps the value file guarantees the hash is over the exact string that lands on disk; re-running the CLI over the reloaded summaries afterwards (10/10) is the independent check that the dump did not alter a string.
- 2026-09-07 (BUG-201 replan c1): plan.yaml's `lanes` key has NO plan-merge write route — `apply` exits 7 CONFLICT on any changed top-level non-union key (UNION_KEYS = tasks, decisions only, plan-merge.py:104) and `amend` refuses --key lanes (AMENDABLE_KEYS, :1232). A dispatch that asks for new lanes.rows is therefore unsatisfiable; I recorded the lane fact in a decision's `because` and raised the gap. Check the verb vocabulary against the key BEFORE promising a plan edit.
- 2026-09-07: BUG-201 c1 goal-check — SC-09's first clause named "the invocation reaching _projected_for" without naming it; `gh-sync status Ready` exits 2 from its own approval guard (gh-sync.py:1306-1307), so the sibling site's new stderr line would have greened it with _projected_for unrepaired. Fixed by pinning `start-task` (exits 0 unrepaired). Also: BRIEF carried two line anchors the plan had right (:190-198 vs :193-196, :1265-1267 vs :1263-1266) — the derived artifact drifted from the plan, not the reverse.
- 2026-09-07: BUG-201 panel repair — an acceptance clause reading "diff --stat names plan.yaml as the ONLY changed file" was unsatisfiable as literally written: feature.json was already dirty from a concurrent sibling before my first tool call. Capturing `git status --porcelain` BEFORE the write is what let me report the pre-existing modification as not mine instead of either denying it or claiming a false clean tree.
