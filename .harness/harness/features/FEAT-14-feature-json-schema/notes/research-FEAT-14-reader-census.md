# Research — FEAT-14 reader census for feature.yaml keys

**BLUF.** Twelve top-level keys survive a real reader check: SPEC §11.3's ten, plus `github` and
`factory`. The dispatch's predicted 11-vs-16 fork does not arise — **list (b) is empty.** No key
beyond the ten is kept alive by a prose instruction either, so the code-reader boundary and the
prose-reader boundary give the same answer.

Census run with `git grep` at pinned ref **`3569a20`**, never the working tree (FEAT-12 has
`bin/check-plan-routes.py`, `bin/factory_config.py`, `bin/upgrade-config.py`, `bin/wayfind.py`
modified and `bin/deploy.sh` deleted). No cited reader below is in a file FEAT-12 removes —
`deploy.sh` reads no feature.yaml key.

## (a) Keys with a CODE reader

| key | reader | expression that consumes it |
|---|---|---|
| `runs[].id`, `.squad`, `.verdict` | `bin/check-state.sh:184-190` | `entry.get("id"/"squad"/"verdict")` into the INV-6/7/8 run tuples |
| `review_sha` | `bin/check-state.sh:195` | `val("review_sha")` vs `PLACEHOLDER_UNSET` |
| `cycles_used` | `bin/check-state.sh:203` | `val("cycles_used")` vs the FAIL-run count |
| `max_total_runs` | `bin/check-state.sh:249` | `_as_budget(val("max_total_runs"))` (INV-22) |
| `phase` | `bin/check-state.sh:450` | `str(_doc.get("phase",""))` for the phase invariants |
| `status` | `bin/check-plan-routes.py:427` | `str(doc.get("status","")).split()[0] in SHIPPED_STATUSES` |
| `github` | `bin/gh-sync.py:247-260`; `bin/check-state.sh:729-737` | `load_recorded` returns `milestone/parent/parent_origin/attached/issues`; INV-21 reads `gblk.get("issues"/"parent")` |
| `factory` | `bin/factory_decompose.py:94-138`; `bin/factory_claim.py:116-131`; `bin/check-state.sh:758-798` | `doc.get("factory")` then `repo/parent/parent_origin/issues/items/edges` |

`factory` is **read and written by code but present in zero feature.yaml files today** — the
factory tooling writes it on first decompose. Omitting it from the schema would make the factory's
own write invalid.

## (b) Keys kept only by a prose instruction — EMPTY

Every prose site that names a feature.yaml field names one of the ten:
`.claude/skills/harness/SKILL.md:15,23,26,61,271` (`STATE.md`/`feature.yaml`, `max_total_cycles`,
`max_total_runs`, `runs`, `cycles_used`, `phase`), `.claude/agents/harness-orchestrator.md:52`
(`cycles_used`/`max_total_cycles`), `.claude/commands/harness.md:18` (id, status, cycles used, last
run). Nothing instructs any agent to consume `mission`, `effort`, `briefing`, `tasks`, `baseline`,
`gate_status`, `receipts`, `posture` — the grilling's "likely genuine" list was a hypothesis and it
does not survive the check.

## Recorded observation: four of the ten have no reader at all

`feature_id`, `branch`, `pr`, `max_total_cycles` have neither a code reader nor a prose consumer at
`3569a20`. They survive because the ruling starts the schema at the ten and puts the burden of proof
only on keys **beyond** them. Not proposed for removal; recorded so a later reader does not mistake
their presence for evidence of readership.

## Corpus, measured on the working tree at `bbfc9bb`

Fourteen feature dirs now carry a `feature.yaml`; the union is **75 distinct top-level keys**.
At the pinned ref `3569a20` only **eleven** are tracked (65 distinct keys) — FEAT-12, FEAT-13 and
FEAT-14 landed after it. Both figures are true of different trees; migration scope is **14 files**,
including FEAT-14's own.

- `cost_usd` (top-level, 8 files; inside `runs[]`, **75 entries**) and `max_cost_usd` (8 files) have
  **zero** readers anywhere at `3569a20`. Largest single drop.
- `runs[]` entry keys observed include `"3 must_fix at med"`, `"flips to met"`, `"one send-back"`,
  `"25 ops"` — prose written as YAML mapping keys inside a run entry. Closing `runs[]` items to
  `id|squad|verdict` is as load-bearing as closing the top level. `note` (14) has no reader.
- `github` sub-keys observed beyond the five `load_recorded`/`save_recorded` handle:
  `closed`(2), `open`(1), `filed`(1), `perf_row_10`(1), `q18_ruled`(1). `save_recorded`
  (`gh-sync.py`) emits exactly `milestone, parent, parent_origin, attached, issues`, so closing the
  block does not break the writer.
- Presence of the ten: only `phase` (absent in FEAT-01, FEAT-02) and `max_total_runs` (absent in 9
  of 14) are ever missing. Every other one of the ten is present in all 14.

## Line budgets after conversion

Reduced to the twelve keys and dumped as `json.dumps(indent=2)`: worst case is FEAT-10 at
**173 lines** (32 runs), against check-domain.sh's 200-line budget for this path
(`check-domain.sh:506` SWEEP_GLOBS, message at `:636`). Roughly 5 JSON lines per run entry, so
FEAT-10 breaches at ~38 runs. The 20-comment-line half of that budget becomes unreachable — JSON
has no comments.

## Template and dependency facts

- `.claude/skills/harness/templates/` at `3569a20` has no `feature.yaml`/`feature.json`, while
  `check-state.sh:487` (INV-18) and `.claude/skills/harness/SKILL.md:23` both instruct
  instantiation from it. Both instructions point at nothing.
- There is **no `requirements.txt` and no `pyproject.toml`** in this repo. PyYAML is declared in
  `.claude/skills/harness-init/SKILL.md:48-55` and installed at
  `.github/workflows/tests.yml:58`. `jsonschema` must follow those two, not a manifest file.
- `import jsonschema` raises at `3569a20` (grilling, verified).
- A JSON document is accepted by `yaml.safe_load`, so one loader spans both formats and the
  validator needs no migration mode.
