# Handoff — FEAT-05-pyyaml-file-parsers, plan → build — written at 37a8a66, seq-1

## Next

**Step zero is the AMENDMENT BRANCH, before the signature.** Planning measured three BRIEF statements
false (Q1 REQ-01, Q2 SC-03, Q3 SC-02). If the user rules any of them amended, the next dispatch is
`harness-product-lead` -> `harness-pm` to apply them to BRIEF.md (`team-config.yaml:88` — BRIEF is
pm's, except `## Approval`), and ONLY THEN does the main session sign. Dispatching build against an
unamended BRIEF leaves SC-03 uncheckable at goal-check — an unmet SC routable to no lead.

Then, and not before: BRIEF.md and PLAN.md must BOTH carry `## Approval` / `status: approved`. Run
`gh-sync.py open` on the feature dir (`github.sync` true, repo `mruangutai/harness`), then dispatch
`harness-eng-lead` for PLAN T-01 onward — **one specialist for the helper and all six conversions**,
because `bin/**` sits in two domains and eng-lead named the split a divergence hazard. T-09's probe
must return before T-12.

## Trust

- The two PreToolUse hooks invoke a bare `python3`, which resolves here to `/opt/homebrew/bin/python3`
  where `import yaml` raises `ModuleNotFoundError` — `which -a python3` + direct import, run by me —
  verified-at 37a8a66
- `check-docs.sh` is GREEN at plan exit: exit 0, 45 patterns across 113 files, no stale statements.
  Build does not inherit a red gate — run by me — verified-at 37a8a66
- DEC-172 carries a Correction reversing both halves of its own same-ship clause — DECISIONS.md:4566-4580,
  read by me — verified-at 37a8a66. Affects FEAT-06 only; the grilling artifact is stale on it
- `cost-report.py` reads no YAML and is a state.yaml WRITER — pm verified at source, `:112` path-munge
  and `:189` in `patch_state_cost`, docstring `:170` — verified-at 37a8a66. This falsifies REQ-01
- `yaml.safe_load` silently collapses duplicate keys, so `check-domain.sh:287`'s dup-key detector
  needs a raising `construct_mapping` — eng-lead run 02 digest, tested — verified-at 37a8a66
- The governed hook path measures 80.63ms, not the grilling's 23.7ms (that was the `:48` early exit)
  — notes/receipt-harness-dev-ops-pyyaml-probe-2026-08-02.md — verified-at 37a8a66
- Session identity inside a PreToolUse hook subprocess — eng-lead run 02 Q1 — **UNVERIFIED**. T-09
  probes it and ESCALATEs if the chain resolves nothing; SC-08/REQ-05 depend on the answer
- The older-pip `--break-system-packages` branch of the install command — PLAN D-07 — **UNVERIFIED**,
  no pip < 23.0.1 exists on this machine to test against

## Dead ends

- No line-scan fallback anywhere in the converted scripts — the user rejected it explicitly, DEC-171
  am.1 — grilling artifact `## Settled` — verified-at 37a8a66
- No `requirements.txt` — DEC-171 am.1 rules the requirement lives in `harness-init`'s HARD GATE
- Do not pin `/usr/bin/python3` — macOS-only and deprecated; breaks Linux, CI, the package — DEC-171
- `validate-digest.py` and the DIGEST fence are FEAT-06, blocked on this feature — grilling `## Out of scope`
- Do NOT route `.gitignore`, `templates/**` or `harness-init/SKILL.md` to dev-ops — team-config.yaml:194-202
  grants none of them. T-10/T-11 are main-session steps — verified-at 37a8a66

## Working set

- `.harness/features/FEAT-05-pyyaml-file-parsers/PLAN.md`
- `.harness/features/FEAT-05-pyyaml-file-parsers/BRIEF.md`
- `.harness/features/FEAT-05-pyyaml-file-parsers/runs/2026-08-02-02-eng/digest.md`
- `.harness/features/FEAT-05-pyyaml-file-parsers/notes/receipt-harness-dev-ops-pyyaml-probe-2026-08-02.md`
- `.harness/features/FEAT-05-pyyaml-file-parsers/feature.yaml`
