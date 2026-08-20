# REUSE angle — FEAT-30 plan.yaml — receipt

BLUF: two findings, both cheap-to-note lockstep-drift risks. Neither blocks the plan; both are
briefing rows, not feature cycles. Everything the operator flagged as settled (D-01..D-08, the
BRIEF criteria, the layout_fixtures.py exclusion) was left alone.

## Finding 1 — the 16-agent roster walk is about to get a second, hand-written copy

- **File/line:** `.claude/skills/harness/bin/check-domain.sh:219-229` defines `_roster(node)`, a
  closure that walks `team-config.yaml`'s parsed tree for every node carrying both `name` and a
  list-valued `domain`, at every nesting level (members under teams, leads under `leads:`,
  `harness-orchestrator` as a bare top-level key). `plan.yaml` T-03 (line ~474-480) instructs the
  new `test-check-domain.py` cases to perform "the same walk the resolve path performs at
  eeabc59" by re-implementing it from the intent's prose rather than importing it.
- **Cost:** two independent spellings of the roster-discovery algorithm. If a future team-config
  shape change (a new nesting level, a renamed key) updates the production walk in
  `check-domain.sh` but not the test's hand-copied walk, the test keeps reporting "16 agents
  found" against stale logic — silently vacuous rather than red — which is exactly what T-03's own
  16-agent-count assertion exists to catch, and can't, if its own walk has drifted from the one it
  is supposed to be checking.
- **Alternative:** lift `_roster` out of `check-domain.sh` into `harness_yaml.py` as an importable
  function (e.g. `roster_with_domains(parsed)`), have `check-domain.sh --resolve` call it, and have
  T-03's new cases import and call the same function instead of re-deriving the walk. This is a
  small, mechanical extraction and does not touch any behavior T-04 depends on.
- **Judgment:** briefing row. The duplication is real but the walk is short and rarely changes;
  worth a one-line note to pm/dev-ops, not a dedicated cycle.

## Finding 2 — T-06's section caps are a second spelling of DEC-145's caps

- **File/line:** `.claude/skills/harness/bin/check-expertise.sh:39`, `CAPS = {"Patterns": 15,
  "Gotchas": 15, "Outcomes": 10, "Open": 5}`, inside the embedded `python3 - <<'PY'` block that
  script runs. `plan.yaml` T-06 (line ~873-875) has `expertise-merge.py` enforce "a section cap -
  15 Patterns, 15 Gotchas, 10 Outcomes, 5 Open" as literals in the new tool, rather than reading
  the same constant `check-expertise.sh` already enforces.
- **Cost:** DEC-145's four cap numbers now live in two places. `check-expertise.sh`'s copy is
  embedded in a heredoc (not an importable module today), so there is no zero-cost import path —
  but that is the reason the numbers get typed twice rather than a reason it's safe: a future cap
  change (DEC-145 amendment) has to be applied in both files, and the one nobody remembers is the
  one inside a 400+-line bash script's python heredoc, not the new standalone tool everyone will
  be looking at.
- **Alternative:** either (a) have `expertise-merge.py`'s cap check shell out to
  `check-expertise.sh` after the union write instead of re-asserting the cap itself, or (b) extract
  `CAPS` into a small importable module (e.g. a `expertise_format.py` sibling) that both
  `check-expertise.sh`'s heredoc and `expertise-merge.py` import. Either removes the second
  spelling; this plan does neither.
- **Judgment:** briefing row. DEC-145's caps are a fixed, rarely-touched contract; flag it for
  pm/dev-ops to fold into the same task's file list if they agree, not worth reopening the plan
  for on its own.

## Not flagged (checked and confirmed correct per the operator's settled list)

- `layout_fixtures.py` exclusion — confirmed correct, not re-examined beyond the instruction.
- T-01/T-02's shared `--repo` resolver ("through the same functions... do not add a second
  resolver") — already anti-duplication by design.
- T-05's parser extension ("extend the existing parser... do not add a second one") — already
  anti-duplication by design.
- T-09's cross-reference-not-restate instruction across the three instruction files — already
  anti-duplication by design.
- CLI `list` (T-01, git-porcelain) vs guard `linked_worktrees` (T-04, pointer-file read, no git
  subprocess) — different implementations for different consumers, justified by D-03
  (DEC-193 forbids a git subprocess on the governed-write path); not a duplication, a deliberate
  split.
- `run-unit-tests.sh`'s drift detector (union-of-arrays check) is exercised by T-08's verify as-is,
  not hand-rolled a second time; the harness.json `detect`-list check in T-08's verify has no
  existing equivalent script to reuse — confirmed by grep, no finding.
