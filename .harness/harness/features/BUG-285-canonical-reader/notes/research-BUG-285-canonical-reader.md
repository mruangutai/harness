# Research — BUG-285-canonical-reader

## Live authority

- Issue #1594 supersedes #285. The #285 inverse comment-bearing `feature.json` fixture remains valid but is subsumed by central `load_feature_json` coverage rather than retained as a `gh-sync.py`-only contract.
- The two #1594 operator rulings require Option B: one accessor module above `harness_yaml.py`; an AST-based checker built before migration; one hand classification of every genuine call it reports; and coverage of every parse category rather than a frozen site count.
- The live scope is Python parse sites under `.claude/skills/harness/bin/`. Shell parse sites remain excluded until #1674 converts the embedded Python to `.py`; no token scan or heredoc parser is allowed.

## Current checkout at 84ecff4a7bdef5008057036b3579cf4c62bd2714

- `harness_yaml.py` currently owns low-level strict YAML plus `load_plan` and `manifest_domains`; `factory_config.py` owns `load_fleet`; `feature_json_write.py` owns `write_feature_json`. There is no single artifact accessor module.
- Genuine current raw parses occur across all ruled categories: explicit files (`feature.json`, `harness.json`, `plan.yaml`, fleet/team/OMP YAML and frontmatter), hook/stdin payloads, GitHub subprocess output, in-memory validation text, and bytes inside locked writer callbacks. The last category is already behind canonical writers and is a checker exemption, not migration work.
- Current divergent examples include `factory_decompose._feature_factory` using `harness_yaml.load_file` for `feature.json`, `gh-sync.load_recorded` using stdlib JSON, `handoff_done_when._resolve_plan` using `yaml.safe_load`, and two independent frontmatter parsers in `sync-agent-adapters.py` and `check-omp-port.py`.
- Current gate/validator parse sites include `validate-digest.py`, `check-plan-routes.py`, `plan-sign-gate.py`, `merge-gate.py`, `gh-close-gate.py`, `check-omp-port.py`, `check-skill-weight.py`, and their tests. DEC-174 makes their cutovers and gate tests main-session-direct; an imported accessor library remains dispatchable.
- Existing tests already defend strict YAML, plan schema validation, fleet validation, frontmatter adapters, and individual gate behavior. The plan must migrate those callers and tests rather than create a second contract. Unit and integration runners are active in `.harness/harness.json`.

## Planning consequences

- No stale count or line number belongs in the contract. The first task makes the AST checker enumerate current `Call` nodes, distinguishes prose, hand-classifies every result, proves the checker red on the pre-migration tree, and turns that output into the migration list.
- Semantic bypass cutovers and mechanical relocations are separate tasks and review units. Gate cutovers are additionally separated from dispatchable call sites.
- The final guard reports each offending file and symbol plus the canonical accessor remedy and reaches zero only after all classified in-scope Python sites are migrated. It must continue flagging a second `state.yaml` reader while leaving the current sole reader alone.
