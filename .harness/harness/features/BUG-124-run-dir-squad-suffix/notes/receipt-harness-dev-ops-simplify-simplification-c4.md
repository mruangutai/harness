# SIMPLIFICATION angle — BUG-124 — c4

**Verdict: one small, non-blocking finding. Everything else in the +76/+100 wiring is
proportionate to the anchoring semantics it implements; no redundant conjunct, no
stale-narration comment, no simplifiable pipeline beyond the one below.**

## Findings

### F-1: duplicated `refs` guard across the `if`/`elif` in the run-dir shape check

- **file**: `.claude/skills/harness/bin/dispatch-guard.sh`
- **line**: 158 and 166 (HEAD `dac8f099`)
- **summary**: `if refs and not globs:` / `elif refs and globs:` re-checks `refs` truthiness
  in both branches instead of nesting once.
- **cost**: a reader has to hold both conditions side by side to see they're mutually
  exclusive only on `globs`. If a third `globs` state is ever added (e.g. partially-derived
  vocabulary), the pattern invites a third copy-pasted `refs and ...` conjunct rather than a
  clean third nested branch — cheap now, compounding maintenance cost later.
- **alternative**: nest on `refs` once:
  ```python
  if refs:
      if not globs:
          ...  # the two SKIPPED prints, unchanged
      else:
          ...  # the bad/forms/exit(2) block, unchanged
  ```
  Behaviorally identical (falls through silently when `refs` is empty, same as today); no
  assertion is touched, so this is a normal apply candidate, not `backlog_only`.
- **backlog_only**: false

## Not flagged (checked and rejected)

- `harness_boundary.py`'s `walk()` iterating the same list up to three times (`all(...)`
  then extraction then recursion) — that's a repeated-work/efficiency concern, not a
  simplification of control-flow shape; belongs to the EFFICIENCY angle, not this one.
- `run_dir_forms`'s `not segment.startswith("*") or segment == "*"` — looked redundant at
  a glance but the two disjuncts cover genuinely distinct cases (fixed-literal segment vs.
  bare-wildcard-with-no-suffix segment); a naive single-condition rewrite would silently
  keep bare `*` segments. Not filed.
- All BUG-124-tagged block comments (the T-01/T-02 rationale banners in both files) state
  present design facts and load-bearing constraints (fail-open policy, ordering
  requirement, sys.path precedent) — not narration of the diff itself. Per O-1, these are
  the sole documented rationale for non-obvious ordering/precedent decisions; left alone.
- The `.harness/` literal anchor, `checkout_relative()` non-use, and the synthesized `/x`
  leaf in `run_dir_slug_ok` — settled per the shared context; not re-litigated, no counter-
  example input found that would justify reopening them.
