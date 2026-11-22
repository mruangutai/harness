# Must-fix — BUG-2294 — validate c1 over 70981edd6f9f110965a0148b4490ed2673d262dc

Routed to the main session: T-01 is `execution_mode: main-session-direct` (DEC-174), so no
engineering persona owns the fix. One round inside the signed ruling (1 round / 45 min).

## SEC-01 — substance / med / T-01 / security-reviewer — CONFIRMED BY PROBE

Source: notes/review-harness-security-reviewer-c1.md; lead digest
runs/2026-11-22-02-validate-validator/digest.md.

The reviewer's trace was static. The orchestrator executed it (probe script
`/tmp/bug2294-probe-sec01.py`, fixture: a PASS-kept `validate-c2-validator` with `ui/`, a
run-dir symlink `runs/build-alias -> validate-c2-validator`, and `runs/evil-alias -> <outside
dir>` carrying a `ui/`; feature.json pins a review_sha):

| subject | rc | stdout | kept ui survives | outside ui survives |
|---|---|---|---|---|
| pinned 70981edd `prune-run-evidence.py` | 0 | `removed runs/build-alias/ui`, `removed runs/evil-alias/ui` | **False** | **False** |
| base c1724230 (run with `PYTHONPATH=<bin>`) | 1 | `removed runs/build-alias` then `OSError: Cannot call rmtree on a symbolic link` | True | True |

So the escape is newly reachable at the pin: `keep_set` admits directory symlinks into
`present` (`os.path.isdir` follows links), `_ui_targets` follows them, and `rmtree(alias/ui)`
deletes the link target's real `ui/`. SC-01's kept-UI guarantee and destructive-scope clause
are violated for the symlink shape; the FEAT-2229 digest guarantee (SC-02) is unaffected.

## Remedy (T-01 owns both paths)

- `.claude/skills/harness/bin/prune-run-evidence.py`: do not follow a run-directory symlink
  into a deletion — exclude symlinked run entries from the UI targets (or refuse the run with
  a named message), and never pass a path beneath a link to `rmtree`. Keep
  `_passing_validate_runs`, pin-run selection, `--keep`, refusals, CLI and ship invocation
  unchanged (SC-03).
- `tests/unit/test-prune-run-evidence.py`: red-first regressions — a run symlink to a kept
  run and a run symlink to an outside directory, asserting destination `ui/` bytes survive
  prune (and dry-run prints no target through a link). Record the red run against the
  70981edd pruner in notes/red-first-T-01.md (append a c1 section), as fail_first for qa.
- Commit on `feat/BUG-2294-prune-keeps-run-digests`; the orchestrator re-pins on resume.

Everything else in the panel passed: qa matrix ok with genuine fail_first for SC-01/SC-02,
code PASS, ui scoped out, goal-check both perspectives pass, DEC-238 disposition met.
