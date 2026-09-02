# BLUF — panel record, cycle 2. TRANSCRIPTION ONLY: nothing here remedies anything.
#
# THE SHAPE. This is a `set-panel --value-file`, which is the BARE panel mapping — set-panel wraps
# it itself (`yaml.safe_dump({"panel": panel})`, plan-merge.py:959) and refuses a `panel:`-wrapped
# document with exit 5, "missing required key(s): last_run, cycle, readers, findings" (observed).
# Cycle 1's notes/research-FEAT-53-panel-record.md carries the `panel:` wrapper because it was
# written as an `apply` proposal; this file is not one.
#
# THE FILENAME. YAML content under an `.md` name. The dispatch named a `.yaml` path;
# check-domain.sh refuses it — harness-pm's granted patterns are
# `.harness/*/features/*/notes/research-*.md` and nothing with a `.yaml` suffix — and
# `yaml.safe_load` does not read extensions, so `.md` is both permitted and correct, and matches
# cycle 1. Not worked around.
#
# THE BINARY. The worktree's vendored .claude/skills copy predates the verb (its plan-merge.py is
# at 6e3eda57, BUG-1128, whose subcommand list has no set-panel and exits 2 on it). The canonical
# copy in the main checkout was used against this worktree's plan.yaml by absolute path. Same tool,
# same lock, same single write route — no second route was invented.
#
# Source of truth: runs/2026-09-01-08-validator/digest.md (that run dir holds exactly two files,
# digest.md and state.yaml — there is no sibling digest). Both the fenced DIGEST and the
# `## Findings` prose were read; severity, reader and evidence anchors come from the prose, which
# is the only place they exist.
#
# Both cycle-2 readers RAN: should-not-exist (fable-advisor, PASS with findings) and scope
# (harness-code-reviewer, FAIL). Neither was skipped, so neither carries persona/reason — the
# template requires those only on a skip.
#
# IDENTITY. Every id was computed, never typed, with the same method recorded for cycle 1:
#   python3 .agents/skills/harness/bin/panel_findings.py id --reader <r> --summary <s>
# i.e. PF- + sha256(reader + "\n" + lowercased, whitespace-collapsed summary)[:32]. The method is
# unambiguous (panel_findings.py:23-33) and it REPRODUCED two cycle-1 ids from the summaries as
# they now read in plan.yaml — PF-d2fc95637db2222cfbec65f41fef202e (reader scope) and
# PF-55e28a6ee5221c9d78c8d4eb9a06dd60 (reader should-not-exist) — which is the proof the reading
# is right. Normalization collapses YAML line folding, so a re-dumped summary keeps its id.
#
# READER REPRESENTATION FOR THE MERGED FINDING. Finding 3 was found independently by both readers.
# No validator constrains a FINDING's `reader:` to an enum: check-state.sh INV-32 reads only
# `severity` and `disposition` off a finding (check-state.sh:506-518) and applies the
# {should-not-exist, scope, goalcheck} enum to `panel.readers` entries alone
# (check-state.sh:519-532); harness_yaml's plan schema does not describe `panel:` at all; and
# plan-merge.py set-panel type-checks only last_run/cycle/readers/findings
# (plan-merge.py:921-948). So the merged finding carries the composite scalar
# `should-not-exist + scope`, which names both attributions structurally instead of leaving one to
# prose, and the summary names them too.
#
# CARRY-FORWARD. set-panel REPLACES the whole mapping, so all eight cycle-1 findings are
# reproduced with their ids, severities, readers, summaries, dispositions, resolved_by and notes
# exactly as they read in plan.yaml now — those dispositions ARE the operator's cycle-1 rulings and
# normalising any of them would erase an overrule. Each simply gains `cycle: 1`.
#
# NO REMEDIATION. Under DEC-207/DEC-176 the five cycle-2 findings travel to the operator's one
# batched signature review as `disposition: open`; the single high (T-16 ordering) and the four
# lower findings are theirs to resolve or overrule, recorded in approval.rulings, which is the main
# session's write and never pm's. No task, decision, BRIEF or DESIGN text was touched, and
# `approval:` is untouched — set-panel carries it forward byte identical.

last_run: 2026-09-01-08-validator
cycle: 2
readers:
  - reader: should-not-exist
    status: ran
  - reader: scope
    status: ran
findings:
  - id: PF-328f8f3cf2485de796e819decb0475aa
    cycle: 1
    severity: high
    reader: should-not-exist
    summary: "KPI 4 absent-file-is-zero reports about 50 pre-instrument features as measured-zero touchpoints, 41 of which carry a signed approval date, so the launch-day autonomy tile is a fabricated record D-19 forbids"
    disposition: resolved
    resolved_by: T-11
    note: "DEC-4 ruling: KPI 4 scoped by D-21's post-instrumentation predicate; T-11 carries both branches, T-20 the call sites"
  - id: PF-6aa9faae67525aae35fe81805ee2e677
    cycle: 1
    severity: med
    reader: should-not-exist
    summary: "Shape B trend charts should not be built this increment: they render only empty states for a month to a quarter at launch yet carry two of D-08's three live triggers"
    disposition: overruled
    note: "DEC-3 ruling: the alpha is accepted with a documented rollback, so Shape B is built this increment"
  - id: PF-7408d83abbae66d18e98f0a349f00dbb
    cycle: 1
    severity: high
    reader: scope
    summary: "T-15 creates charts.tsx after T-14 creates panels.tsx and no later task touches panels.tsx, so the grading panel ships with no chart wired and both verifies stay green"
    disposition: resolved
    resolved_by: T-21
    note: "DEC-4 ruling: T-21 mounts the charts and gates on a rendered getByTestId; T-22 makes it a suite and CI gate"
  - id: PF-04c95fd65a8f1eb7b575bfee58d2b71b
    cycle: 1
    severity: med
    reader: should-not-exist
    summary: "The committed dist bundle has no ongoing src-to-dist consistency guard and is unmergeable across worktrees, so a later client edit ships a stale UI with every verify green"
    disposition: overruled
    note: "Backlog ruling: accepted as backlog row B-1, filed at ship with label Dashboard"
  - id: PF-3713534d84c8a79f7c478fb122760829
    cycle: 1
    severity: med
    reader: should-not-exist
    summary: "D-15's escaped-defect rule counts about 8 items in 5 months while excluding 32 fix commits unexamined, and is gamed in one direction because a fix commit instead of a BUG unit holds the number at zero"
    disposition: overruled
    note: "Backlog ruling: accepted as backlog row B-2, filed at ship with label Dashboard"
  - id: PF-55e28a6ee5221c9d78c8d4eb9a06dd60
    cycle: 1
    severity: med
    reader: should-not-exist
    summary: "KPI 6's four-hop attribution join buys a tile that is about 77 percent no_prefix with a roughly 6 percent resolvable remainder already knowable from 16 static agent files"
    disposition: overruled
    note: "Backlog ruling: accepted as backlog row B-3, filed at ship with label Dashboard"
  - id: PF-d2fc95637db2222cfbec65f41fef202e
    cycle: 1
    severity: med
    reader: scope
    summary: "BRIEF declares SC-07 evidence unit, but its only asserting test test-metrics-trend.py is registered in INTEGRATION_SCRIPTS, not UNIT_SCRIPTS"
    disposition: overruled
    note: "Backlog ruling: accepted as backlog row B-4, filed at ship with label Dashboard"
  - id: PF-ce8b018f5719dde6716225552ee32559
    cycle: 1
    severity: med
    reader: scope
    summary: "T-13's forbidden theme-token grep covers the 4 client files existing at its dispatch while T-14 and T-15 add 5 more that are never re-checked, so DESIGN C-3 is enforced over 4 of 9 files"
    disposition: overruled
    note: "Backlog ruling: accepted as backlog row B-5, filed at ship with label Dashboard"
  - id: PF-45518258bbae0f20d051abf3a4970419
    cycle: 2
    severity: high
    reader: scope
    summary: "T-16 (plan.yaml:909) builds and commits the production dist bundle but depends only on T-12 and T-15, so the bundle can be committed before T-21 (plan.yaml:1066) mounts the chart and no later task reruns npm run build"
    disposition: open
  - id: PF-3b85f18809cf5c4ad01b9008e1eace1c
    cycle: 2
    severity: med
    reader: should-not-exist
    summary: "D-21's runtime instrumentation has no planned git disposition: neither .harness/metrics/instrumented_at nor T-20's touchpoints.jsonl lines are committed by any task or covered by T-02's ignore set (templates/gitignore.snippet:8-11), so an untracked marker dirties the tree and a second clone writes a later epoch and reports a fabricated zero"
    disposition: open
  - id: PF-0f3f4101447923844b00515e7312ce0e
    cycle: 2
    severity: med
    reader: should-not-exist + scope
    summary: "The spliced trailing comment block contradicts the live YAML twice, found independently by both readers: plan.yaml:1285-1286 says no task touches tests.yml while T-22 lists it (plan.yaml:1168) and adds flask to that job (plan.yaml:1217-1221), and plan.yaml:1339-1341 quotes T-21's verify as the reporter=verbose grep form while live T-21.verify (plan.yaml:1078-1080) is the reporter=json form"
    disposition: open
  - id: PF-aa9c41f6ef1f6c977d02645dc095d2d5
    cycle: 2
    severity: med
    reader: scope
    summary: "SC-17 declares verify automated evidence integration (BRIEF.md:216-224) but its aggregate not-tracked-count clause is asserted only in test-metrics-kpi.py, which T-06 registers in UNIT_SCRIPTS (plan.yaml:405) per T-11's intent (plan.yaml:695-699), so that clause has no integration-kind assertion under CI's split (.github/workflows/tests.yml:83-92)"
    disposition: open
  - id: PF-ed0712ea279a7c0ba45f4acb3ce97f6e
    cycle: 2
    severity: low
    reader: should-not-exist
    summary: "T-12's 8.0s ceiling is vacuous in CI because tests.yml checks out with bare actions/checkout@v4 (.github/workflows/tests.yml:50), so the timed permanent integration case measures the fast unavailable-with-reason branches rather than the real per-request cost D-09 stakes its no-cache deferral on"
    disposition: open
