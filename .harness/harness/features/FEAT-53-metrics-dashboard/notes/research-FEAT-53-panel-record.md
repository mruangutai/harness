# BLUF — panel record, cycle 1, transcribed not remediated
#
# Source of truth: runs/2026-09-01-06-validator/digest.md (run 05 holds a superseded prose-only
# copy; a second Write to a run digest is refused, so 06 is the successor). Cross-checked against
# notes/review-harness-code-reviewer-planpanel-c1.md for the three scope findings (S1 high,
# S2/S3 med) — they are digest rows 3, 7 and 8.
#
# Both readers RAN. should-not-exist (fable-advisor) returned 5 findings, scope
# (harness-code-reviewer) returned 3. Neither carries persona/reason: the template requires those
# only on a skip, and recording "ran" is the load-bearing statement a findings list cannot make.
#
# All 8 findings are disposition: open — none resolved, none overruled. Severity is each reader's
# own word, unreassigned: 2 high (rows 1 and 3), 6 med. Nothing unrated.
#
# Every id was computed with, never typed:
#   python3 .claude/skills/harness/bin/panel_findings.py id --reader <r> --summary <s>
# and each --summary was the character-for-character string written below, so an unchanged finding
# keeps its id on a re-run and a reworded one correctly gets a new one.
#
# This file IS the merge proposal. It carries only panel:, so apply's top-level union adds the key
# without touching tasks:, decisions:, lanes:, status:, source_issues: or approval:. Prose above is
# a YAML comment preamble, which apply never consults and never writes into plan.yaml.
#
# Nothing here remediates anything. Under DEC-176 all 8 findings travel to the operator's one
# batched signature review; the two gating highs (row 1 KPI 4, row 3 chart-never-wired) and the
# fix-ordering constraint from digest Q2 are the operator's to rule on, recorded in
# approval.rulings, which is the main session's write and not pm's.

panel:
  last_run: 2026-09-01-06-validator
  cycle: 1
  readers:
    - reader: should-not-exist
      status: ran
    - reader: scope
      status: ran
  findings:
    - id: PF-328f8f3cf2485de796e819decb0475aa
      severity: high
      reader: should-not-exist
      summary: "KPI 4 absent-file-is-zero reports about 50 pre-instrument features as measured-zero touchpoints, 41 of which carry a signed approval date, so the launch-day autonomy tile is a fabricated record D-19 forbids"
      disposition: open
    - id: PF-6aa9faae67525aae35fe81805ee2e677
      severity: med
      reader: should-not-exist
      summary: "Shape B trend charts should not be built this increment: they render only empty states for a month to a quarter at launch yet carry two of D-08's three live triggers"
      disposition: open
    - id: PF-7408d83abbae66d18e98f0a349f00dbb
      severity: high
      reader: scope
      summary: "T-15 creates charts.tsx after T-14 creates panels.tsx and no later task touches panels.tsx, so the grading panel ships with no chart wired and both verifies stay green"
      disposition: open
    - id: PF-04c95fd65a8f1eb7b575bfee58d2b71b
      severity: med
      reader: should-not-exist
      summary: "The committed dist bundle has no ongoing src-to-dist consistency guard and is unmergeable across worktrees, so a later client edit ships a stale UI with every verify green"
      disposition: open
    - id: PF-3713534d84c8a79f7c478fb122760829
      severity: med
      reader: should-not-exist
      summary: "D-15's escaped-defect rule counts about 8 items in 5 months while excluding 32 fix commits unexamined, and is gamed in one direction because a fix commit instead of a BUG unit holds the number at zero"
      disposition: open
    - id: PF-55e28a6ee5221c9d78c8d4eb9a06dd60
      severity: med
      reader: should-not-exist
      summary: "KPI 6's four-hop attribution join buys a tile that is about 77 percent no_prefix with a roughly 6 percent resolvable remainder already knowable from 16 static agent files"
      disposition: open
    - id: PF-d2fc95637db2222cfbec65f41fef202e
      severity: med
      reader: scope
      summary: "BRIEF declares SC-07 evidence unit, but its only asserting test test-metrics-trend.py is registered in INTEGRATION_SCRIPTS, not UNIT_SCRIPTS"
      disposition: open
    - id: PF-ce8b018f5719dde6716225552ee32559
      severity: med
      reader: scope
      summary: "T-13's forbidden theme-token grep covers the 4 client files existing at its dispatch while T-14 and T-15 add 5 more that are never re-checked, so DESIGN C-3 is enforced over 4 of 9 files"
      disposition: open
