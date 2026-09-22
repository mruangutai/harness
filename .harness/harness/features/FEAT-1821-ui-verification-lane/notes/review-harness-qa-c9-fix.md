# QA revalidation — V9-01 T-14 fix

**BLUF: PASS at immutable pin `ea4916518eea1c8f73901d372ad8e1e38595e64b`.** The real gate rejects the exact corrupt local-header mutant because `zipfile.is_zipfile` cannot read it; all eight committed FEAT-53 trace ZIPs are accepted. No T-14 regression was found.

## Scope and matrix

`git rev-parse HEAD` returned `ea4916518eea1c8f73901d372ad8e1e38595e64b`; `git cat-file -e ea4916518eea1c8f73901d372ad8e1e38595e64b^{commit}` exited 0. Review scope was only the T-14 diff after baseline `c5fab95615c035e97109f90bd4aa91fc2e4b78a5`: `ui_contract.py`, `test-ui-verification-contract.py`, and the T-14 receipt (16 insertions, one deletion). T-14 is `logic`, whose matrix floor is `unit`.

Phase-1 expectations: the trace parser and gate must preserve path containment, non-empty and same-run-`ui/` requirements; distinguish traced and untraced records; honor the Traces table as sole authority; preserve SC-04 pixel-baseline opt-in enforcement; and preserve location-based ignore behavior. The focused test covers these rules at `tests/unit/test-ui-verification-contract.py:182-188,326-394`; the signed verify includes the ignore probe.

## Executed proof

T-14 signed verify command, carried verbatim, exited 0:

```sh
python3 tests/unit/test-ui-verification-contract.py && python3 -c "from pathlib import Path; s=Path('.harness/harness/features/FEAT-1821-ui-verification-lane/notes/receipt-main-direct-T-14-c0.md').read_text(); assert all(x in s for x in ('SC-04','test_to_have_screenshot_requires_pixel_baseline_opt_in','fail-first','nonzero'))" && probe_run=".harness/harness/features/FEAT-1821-ui-verification-lane/runs/ignore-probe-$$/ui" && scratch=".claude/skills/harness/bin/dashboard/client/test-results/ignore-probe-$$" && published="$probe_run/traces/listed-check--chromium.zip" && nonlisted="$probe_run/test-results/non-listed--chromium.zip" && raw="$scratch/trace.zip" && trap 'rm -rf "$probe_run" "$scratch"' EXIT && mkdir -p "$(dirname "$published")" "$(dirname "$nonlisted")" "$(dirname "$raw")" && touch "$published" "$nonlisted" "$raw" && ! git check-ignore -q -- "$published" && git check-ignore -q -- "$nonlisted" && git check-ignore -q -- "$raw"
```

Result: `Ran 27 tests ... OK` (27/27); receipt-token and all three location-based ignore assertions passed.

The exact mutant was installed only in a throwaway `Workspace`, then passed through the real `ui_contract.py gate` CLI:

```sh
python3 -c "import runpy, zipfile, subprocess; n=runpy.run_path('tests/unit/test-ui-verification-contract.py'); w=n['Workspace'](); w.design.write_text(n['design_text'](traces=['C1-HEADER-GEOMETRY','SRC-TOKENS'])); w.results(traced=('C1-HEADER-GEOMETRY','SRC-TOKENS')); p=w.ui_dir/'traces'/'C1-HEADER-GEOMETRY--desktop-1920.zip'; p.write_bytes(b'PK\\x03\\x04'+bytes([0xFF])*64); assert not zipfile.is_zipfile(p); r=subprocess.run([n['sys'].executable, str(n['uc'].__file__), 'gate', '--design', str(w.design), '--results', str(w.ui_dir/'results.json'), '--feature', n['FEATURE'], '--run-id', n['RUN'], '--served-bundle-commit', n['SHA'], '--repo-root', str(w.root), '--client-package', str(w.client), '--changed', 'client/src/tiles.tsx'], text=True, capture_output=True); print('zipfile.is_zipfile=False'); print(r.stdout, end=''); assert r.returncode == 1 and 'C1-HEADER-GEOMETRY@desktop-1920' in r.stdout and 'is not a ZIP' in r.stdout; w.tmp.cleanup()"
```

Result: exit 0 for the probe; `zipfile.is_zipfile=False`; CLI gate exit 1 with `C1-HEADER-GEOMETRY@desktop-1920 ... is not a ZIP`. The extra summary-status reason is the expected consequence of corrupting an otherwise passing temporary bundle. This discriminates the former prefix-only false acceptance.

Scoped Python complexity command:

```sh
python3 /Users/molchairuangutai/GitHub/harness/.agents/skills/harness/bin/code-grade.py --base c5fab95615c035e97109f90bd4aa91fc2e4b78a5 --head ea4916518eea1c8f73901d372ad8e1e38595e64b
```

Result: `PASSING: 1`. The changed test-local mutant helper at `test-ui-verification-contract.py:361` is grade 5, bar 3; no below-bar record exists.

## Independent committed-bundle gate

Without starting a service or replaying the lane, I ran:

```sh
python3 .claude/skills/harness/bin/ui_contract.py gate --design .harness/harness/features/FEAT-53-metrics-dashboard/DESIGN.md --results .harness/harness/features/FEAT-53-metrics-dashboard/runs/FEAT-1821-initial-red/ui/results.json --feature FEAT-53-metrics-dashboard --run-id FEAT-1821-initial-red --served-bundle-commit e94bc953d13e97c0443f1875f63884bf075143ee --repo-root . --client-package .claude/skills/harness/bin/dashboard/client --changed .claude/skills/harness/bin/dashboard/client/src/tiles.tsx
```

It exited 1 only because this is the intentionally RED FEAT-53 predicate bundle. Independent classification against the real gate returned: `zip_traces=8/8`, `reasons=22`, `predicate=18`, `inspection_setup=4`, and `extra_trace_structural_title_provenance_screenshot_accounting=0`. All eight trace paths are unique and `zipfile.is_zipfile` accepts each. Thus no trace, structural, title, provenance, screenshot, or accounting reason was added.

## Receipt and prior-rule audit

`receipt-main-direct-T-14-c0.md:3-20` records the original pinned red-before-fix command, nonzero result, named failing trace and SC-04 tests, and 27/27 green. Its V9-01 section (`:29-35`) specifically records the c5 fail-first `PK\\x03\\x04` + 64-byte `0xFF` mutant, the named trace test failure, `zipfile.is_zipfile` fix, and post-fix 27/27 green. Prior containment, non-empty, in-run, traced/untraced, Traces-table, SC-04, and ignore-policy requirements remain covered as above.

No substantive finding remains.
