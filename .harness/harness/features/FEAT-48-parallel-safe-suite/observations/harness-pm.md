# Observations - harness-pm

- 2026-08-31: FEAT-48 planning. The research note's fix direction (tempdir first on the child PYTHONPATH) cannot work for check-domain.sh: its heredoc runs sys.path.insert(0, _bin_dir) at line 125, so the real bin dir always wins. Re-derived the mechanism from the script before writing the task, and the fix became a private bin copy instead. A dispatch that hands me a fix direction is a hypothesis, not a spec.
- 2026-08-31: prototyping the guard BEFORE specifying it changed three rule decisions and cut findings 47 -> 15 -> 10 with zero false positives. Specifying a static scanner without running it once would have shipped a rule someone deletes on its first false positive.
- 2026-08-31: ran every verify block against the pre-change tree. Two of five would have passed unchanged if written the obvious way (bytes-only comparison for T-01, name-set comparison for T-02); polling during the run and adding mtime is what made them discriminating.
