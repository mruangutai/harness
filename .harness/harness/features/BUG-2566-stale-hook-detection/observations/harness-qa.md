# Observations — harness-qa — BUG-2566-stale-hook-detection

- 2026-11-27: SC-01 expectStale uses toContain(H); a reason rooted at process.cwd() ("../../var/.../.omp/extensions/harness-hooks.ts") still contains H, so a display-root mutant survives while the fingerprint-root mutant is caught — a substring check on a relative path does not pin the root.
- 2026-11-27: Pinned new omp-hooks tests over a git-archived 87efcd8a tree reproduce the build RED list exactly (26 fail) and also red typecheck (TS2554 on the 3-arg registerHarnessHooks), giving SC-08 a natural pre-fix red.
- 2026-11-27: c2 FIFO-probe closure: a failed mkfifo exits the probe 3, but mkfifo on another path exits 1 (lstatSync ENOENT throws before the isFIFO check) — both red; the exit-3 claim covers only the spawn-failure leg.
