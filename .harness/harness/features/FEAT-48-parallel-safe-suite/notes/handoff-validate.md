# Handoff — FEAT-48, validate → ship — written at e64e863e, seq-4

## Next

**Do not ship. One operator ruling first.** SC-03's second half — "in the same run, flags the ten
historical violating sites at `ea6f51f` … each asserted individually" — is asserted by NO gate and
**cannot be met as written**: CI runs `actions/checkout@v4` with no `fetch-depth`
(`.github/workflows/tests.yml:50`), so the default shallow clone puts `ea6f51f` out of reach, while
SC-04 requires that same file to pass in CI. Route to **pm** for a re-plan recommendation under the
operator's approval — not mine to waive, and not a fix cycle. Remedies: **(A)** add `fetch-depth: 0`
and assert the ten sites in the invariant — literal, but adds a file outside the signed plan's set
and a full-history fetch to every CI run; **(B)** amend SC-03 so the ten-site assertion is a
review-time check, which is what T-03's `verify:` block already is. Three quality items
(`code_grade`, M4, M5) need the same main-session-direct lane alongside the ruling.

## Trust

- SC-01, SC-02, SC-04..SC-10 all MET, re-verified by me at `e64e863e`, not inherited — at e64e863e.
- SC-03 half one now MET: the live-tree case asserts the root against an INLINE recomputation (not a
  call to `harness_boundary`), `discovered 63 >= 50`, zero findings —
  `bin/test-suite-independence.py:206-224` — verified-at e64e863e.
- SC-03 half two UNMET: no file under `bin/` mentions `ea6f51f`, zero grep hits — at e64e863e.
- **The scanner itself is not in doubt.** I ran it over `git show ea6f51f:` for all three files and
  asserted each of the ten sites individually: found 10, missing 0, extra 0. The capability is
  present; only its enshrinement in a CI-run gate is missing — my probe — verified-at e64e863e.
- M1 FIXED: a dangling symlink and a symlinked subdirectory each now give exit 1 with a `MUTATED`
  line, while the clean control still exits 0 — my tempdir probe, and `bin/test-run-pool.py:92-105`
  pins both legs — verified-at e64e863e.
- Suite green and stable at the new pin: ELEVEN `--kind all` runs, all exit 0, zero `MUTATED`, zero
  `FAIL`, 42.61–48.71s at 8 workers / 63 files, tree 0 modified paths at start and end. This
  re-establishes SC-05/SC-06 against the CHANGED pool; the note's original ten were taken at
  `b86ce66a`, before `snapshot()` was rewritten — my runs — verified-at e64e863e.
- SC-01 re-verified: `test-check-domain.py` exit 0, `feature_schema.py` identical in mtime_ns, size
  AND sha256, crashing-checker still asserts exit 2 with `CRASHED` (:1492) — at e64e863e.
- `code_grade` STILL `fail` and WORSE: 7 FAIL records → **9** (19 passing). New grade-1
  `test-suite-independence.py:170 run_self_tests`, new grade-2 `run_pool.py:29 snapshot` — at e64e863e.
- M4 STILL open: zero `pycache` mentions in `bin/test-run-pool.py`; T-04 intent item (g) unpinned.
  M5 STILL open: a same-size overwrite with an exact `os.utime` restore is invisible — adding
  `st_mode` did not close it — my probes — verified-at e64e863e.
- The code added by `e64e863e` has been through NO reviewer panel; only my mechanical verification
  covers `run_self_tests` and the rewritten `snapshot` — UNVERIFIED by review.

## Dead ends

- Do not route any remedy to a dev squad — all land in `bin/**`, `DECISIONS.md` or the workflow,
  every one `main-session-direct` — `plan.yaml` `lanes:`, DEC-174 — verified-at e64e863e.
- Do not re-add the six in-file cases or re-litigate SC-03's FIRST half; five of six landed and the
  live-tree case is correct — `bin/test-suite-independence.py:170-235` — verified-at e64e863e.
- Do not hand the ten-site gap back as a coding oversight. It is a wrong-premise criterion, and a
  fix dispatch yields either a red CI or a silent skip — `.github/workflows/tests.yml:50` — at e64e863e.
- Do not read a red suite as a FEAT-48 defect before clearing the environment: `HARNESS_AGENT_TYPE`
  makes `test-plan-merge.py` fail 11 checks; that file is not in the diff — my run — at e64e863e.

## Working set

- `.claude/skills/harness/bin/test-suite-independence.py` (`run_self_tests`, :170)
- `.claude/skills/harness/bin/run_pool.py` (`snapshot`, :29)
- `.claude/skills/harness/bin/test-run-pool.py` (:92-105 symlink legs; no `__pycache__` leg)
- `.github/workflows/tests.yml:50` (the shallow checkout that bounds SC-03)
- `.harness/harness/features/FEAT-48-parallel-safe-suite/BRIEF.md` (SC-03, SC-04)
