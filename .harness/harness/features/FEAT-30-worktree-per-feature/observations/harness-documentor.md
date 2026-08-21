# Observations — harness-documentor — FEAT-30

- 2026-08-21: SPEC.md's Index "Cost" column is not chars/4. Calibrated against HEAD: §2 1539 words
  → listed 1.3k, §15 934 → 0.9k, §5 2410 → 2.0k, i.e. roughly words x 0.85-0.96. Writing a new
  figure without calibrating would have overstated §15 by ~2x.
- 2026-08-21: nine of the file:line anchors I drafted from a first read of feature-worktree.py,
  bash-write-guard.sh and their tests were off by 2-12 lines. Re-deriving each with a single
  `grep -n` on the definition name caught all of them; the 12-line miss was an allow-case block in
  test-bash-write-guard.py that I had anchored to the refuse cases above it.
