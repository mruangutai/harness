# QA gate — BUG-2295 T-01 — pin 7d76c1ce (fix c4c93ef1) vs base dd04e52a (run qa-c2)

BLUF: matrix_ok true; C1 closure confirmed by my own execution at the pin. Mixed-case cycle names (Build-c1, build-C1, VALIDATE-C12) are refused via Write and Edit with the exact lowercase canonical diagnostic. No tests authored, no source changed.

## Phase 1 (BRIEF + plan only)
Expect: suffixed names refused for several phases and multi-digit cycles, via Write and Edit; case variants refused; canonical accepted; cap/section/Done-when retained. All have named tests (below); no gaps.

## Matrix
bugfix: always []; when unit (touches_runtime_code: check-domain.py, gh-sync.py changed -> triggered), integration (BRIEF binding kind). Both run. component/ui/typecheck null runners; eval/functional excluded (DEC-187); locally_run probes' detect surface untouched (not_applicable).

## Per-kind (pin 7d76c1ce, env -u HARNESS_AGENT_TYPE -u HARNESS_CONTROL_PLANE_ROOT; my execution)
- integration T-01 verify `python3 tests/integration/test-check-domain-post.py`: rc=0, 117 ok, 0 FAIL.
- unit `run-unit-tests.py --kind unit`: rc=0, 63 files.
- integration `run-unit-tests.py --kind integration`: rc=0, 91 files.
Logs (Bash cp into runs/ denied by write-guard): /tmp/qa-c2-{red,green,unit,integration}.out; this note is the durable record.

## fail_first (natural RED, my reproduction; tier: pin tests over prior production)
Second pinned checkout at 7d76c1ce with only check-domain.py restored to 253cdf2a (verified `git diff --quiet 253cdf2a -- check-domain.py`). RED rc=1, 105 ok, exactly 12 assertion FAILs (exit 0 where refusal wanted, plus the "names notes/handoff-<phase>.md exactly" rows): Build-c1, build-C1, VALIDATE-C12, each Write and Edit, each exit + exact-name. Lowercase stems all ok. The 12-FAIL signature matches the main-session receipt claim in notes/red-first-T-01.md; this run is my own, not a transcription. The original lowercase red (6 FAIL vs dd04e52a) was executed in c1 (notes/review-harness-qa-c1.md) and claimed in red-first-T-01.md; not re-executed in c2.
GREEN at pin: rc=0, 117 ok, 0 FAIL; all 12 rows ok plus lowercase build-c1/validate-c12/plan-c305 rows, "refused Edit leaves file unchanged" rows, canonical build/validate/plan accepted.
Retained shape cases ok: SWEEP handoff cap (DEC-159), missing sections, Done when missing/valid, edit with/without Done when, no per-section cap, symlink escapes.
Test location: tests/integration/test-check-domain-post.py `_handoff_cycle_suffix_cases`, called from `run_handoff_done_when`.

## Limits
- "Edit leaves file unchanged" and canonical rows are baseline-green (discrimination unshown, not useless).
- Diagnostic lowercasing not separately mutation-probed beyond the 12 reds.
- SC-03/04 inspections not graded by me. DEC-252 commentary discrepancy is outside T-01, not a finding.
