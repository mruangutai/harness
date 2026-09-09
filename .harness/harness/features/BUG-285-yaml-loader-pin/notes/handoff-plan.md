# Handoff — BUG-285-yaml-loader-pin, plan → build — written at 7e0c2ec, seq-4

## Next

Nothing dispatches until the operator signs. On `approval.status: approved` in plan.yaml, run the
eng segment for T-01: `plan-merge.py set-feature-station --station building`, then dispatch the
`build` team to `harness-eng-lead` with T-01's `intent:` carried verbatim from
`.harness/harness/features/BUG-285-yaml-loader-pin/plan.yaml`. T-01's `execution_agent` is
`harness-qa`; the lead routes, it does not revisit that. Then the qa segment, then SIMPLIFY, then
pin `review_sha` — SC-03 and SC-05 are both graded with `git show <review_sha>:<path>`, so the
builder's probe note must be in the commit the pin names.

## Trust

- plan.yaml carries one task, `approval.status: pending`, `panel.cycle: 0` with both readers `ran`
  and one `info` finding `PF-2242299b369215b13ad577fe4279d52e` open — loaded and read back myself
  through harness_yaml — verified-at 7e0c2ec
- baseline `env -u HARNESS_AGENT_TYPE python3 tests/integration/test-gh-sync.py` = exit 0, 318 `ok`,
  0 `FAIL`, 36.9s, which is what SC-04 compares against — ran it myself — verified-at 7e0c2ec
- the mutant is one token: `json.loads(text)` at `gh-sync.py:523` → `harness_yaml.load_str(text,
  path)`; `import harness_yaml` is already at `gh-sync.py:101` — read both — verified-at 7e0c2ec
- the chosen fixture `"feature_id: F1\ngithub:\n  parent: 40\n"` is YAML-mapping-valid and
  JSON-invalid — measured both parsers — verified-at 7e0c2ec
- `check-plan-routes.py` prints `OK T-01 granted to harness-backend-dev, harness-dev-ops,
  harness-qa` and exits 0 — ran it myself — verified-at 7e0c2ec
- T-01's `verify:` survived `set-panel` as a block scalar ending in exactly one newline — read back
  through the loader — verified-at 7e0c2ec

## Dead ends

- Do not re-raise the four items the panel assessed and dismissed (qa authoring-and-grading T-01,
  T-01 intent over-specification, `lanes.rows[0].surface` breadth, REQ-04 vs the delete-don't-re-pin
  rule) — `runs/2026-09-09-01-planpanel-validator/digest.md` — verified-at 7e0c2ec
- Do not edit `gh-sync.py` to make the new assertion pass. The reader already refuses the fixture;
  a red assertion against the real reader is a finding for the operator, not a licence to edit —
  `BRIEF.md ## Constraints` — verified-at 7e0c2ec
- Do not probe by editing the real `gh-sync.py`: `.agents/skills` is a symlink to `.claude/skills`,
  one inode — measured with `os.lstat` — verified-at 7e0c2ec

## Working set

- .harness/harness/features/BUG-285-yaml-loader-pin/plan.yaml
- .harness/harness/features/BUG-285-yaml-loader-pin/BRIEF.md
- .harness/harness/features/BUG-285-yaml-loader-pin/notes/intake-BUG-285.md
- .harness/harness/features/BUG-285-yaml-loader-pin/runs/2026-09-09-01-planpanel-validator/digest.md
- tests/integration/test-gh-sync.py

## Done when

Scope: T-01 built and its probe transcript landed in the commit review_sha names
Authority: approval:.harness/harness/features/BUG-285-yaml-loader-pin/BRIEF.md#Approval
Authority: plan-task:T-01.verify
Authority: brief-sc:SC-03
