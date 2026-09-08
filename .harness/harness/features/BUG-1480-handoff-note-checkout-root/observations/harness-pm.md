# Observations - harness-pm

- 2026-09-07: BUG-1480 plan — self-checked both approval artifacts by piping a PostToolUse payload (HARNESS_HOOK_MODE=post, tool_name Write, file_path only) into check-domain.sh; the post route reads what landed and reports shape without the PRE domain denial that refuses an agent's plan.yaml write, so it is the only way to grade your own plan.yaml shape. Both exited 0.
- 2026-09-07: goal-checking a plan whose fix INSERTS lines above cited anchors: every SC line anchor
  below the insertion point rots at review_sha. Grade anchor freshness against the insertion the plan
  itself specifies, not against the tree as read (BUG-1480 SC-05, ~+14 lines at check-domain.sh:1149).
- 2026-09-07: a negative control that is green pre- AND post-fix proves non-vacuity, never that the
  fix's mechanism ran. BUG-1480 T-01 row 3 claimed the latter; the needle set carried only the id, and
  handoff_done_when._unresolved embeds the TARGET PATH, so a path needle was the one-line remedy.
- 2026-09-07: BUG-1480 c0 remedies. A dispatch mandated `plan-merge.py apply` to REVISE T-01; apply
  exits 7 CONFLICT on any changed value, so the only route for a revision is
  `amend --field --expect-sha256 --value-file`. Second time this shape has cost a round trip.
- 2026-09-07: F-05 came from the c0 LEAD digest, not from the goal-check note (whose own F-05 is a
  different finding). Dispatch renumbering means finding ids are only meaningful with their source
  named; I had to read the note to discover the note's F-05 was the dispatch's F-06.
- 2026-09-07: BUG-1480 panel s3 — the dispatch specified PF ids as sha256(summary)[:8]; panel_findings.py computes sha256(reader+"\n"+normalized)[:32] and every other panel in the tree uses the 32-hex form. Took the canonical route and flagged the deviation; a non-canonical id would surface later as INV-32 STALE RISK ACCEPTANCE.
- 2026-09-07: plan-merge amend on a LIST field needs --yaml-value on the --show call too, otherwise it exits 4 ("is a list, not text") before printing the sha256 you need for --expect-sha256.
- 2026-09-08: BUG-1480 goal-check. SC-05 named `_resolved_rel` as a `_norm` call site; at review_sha it does not call `_norm` at all (check-domain.sh:1866-1893) — the real caller nearby is `_hardlink_plan` (:1920). Citing by FUNCTION NAME cured the line-number rot F-02 found but introduced a name that was simply the wrong function; verify a by-name anchor against the tree too.
- 2026-09-08: SC-02 quantified over 42 rows from seven builders. Enumerating them from the builder bodies (test-check-domain.py:4171-4399) and matching each name in the output took one read; the suite prints no per-group total for handoff, so a FAIL count would have been the only alternative and would have been blind per row.
