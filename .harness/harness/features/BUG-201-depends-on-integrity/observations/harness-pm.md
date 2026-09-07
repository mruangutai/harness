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
