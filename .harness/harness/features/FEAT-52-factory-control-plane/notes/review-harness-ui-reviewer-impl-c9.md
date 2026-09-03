# UI Review — FEAT-52-factory-control-plane — impl-c9 (pinned d8c42a9d)

## Verdict: decline (measured), plus an advisory pass on the one named adjacent surface

## 1. Census — changed-file count

`git diff --name-only 8ff525e2..d8c42a9d` (merge-base main..pin) = **93 files**.

## 2. Census — UI-surface count

Extension census over all 93 paths:

| ext | count |
|---|---|
| .md | 80 |
| .py | 7 |
| .sh | 3 |
| .yml | 1 |
| .yaml | 1 |
| .json | 1 |

`grep -E '\.(html|css|scss|tsx|jsx|vue|svelte|less)$'` over the same list → **0 hits**.

No file in the diff is a template, stylesheet, component, or rendered-markup surface. The 80
markdown files are: 16 `.omp/agents/*.md` + 16 `.claude/agents/*.md` persona instruction pairs, 15
`harness*/SKILL.md` skill files, 2 templates (`PLAN.md`, `README.md`), 1 reference doc
(`debug-mission.md`), 2 decision docs (`DECISIONS.md`, `DECISIONS-INDEX.md`), and the remainder are
this feature's own `BRIEF.md`/`plan.yaml`/`STATE.md`/`feature.json`/notes/observations — all agent-
and operator-instruction prose read by LLM personas and by the humans debugging the factory, never
rendered markup. **Borderline candidates, named and ruled out:** `.claude/skills/harness/templates/PLAN.md`
and `README.md` look template-shaped by name but are markdown authoring scaffolds for future
plans/repos, not a rendered contract for an end-user surface — no spacing/colour/state vocabulary,
no DESIGN.md-style checkable assertions. `.github/workflows/tests.yml` is CI config, not UI.
`DECISIONS.md`/`DECISIONS-INDEX.md` are the decision log, prose only. None of these are treated as
in-scope UI surfaces.

## 3. DESIGN.md

`git cat-file -e d8c42a9d:.harness/harness/features/FEAT-52-factory-control-plane/DESIGN.md` →
**absent** (fatal: path does not exist at that commit). No Mode A contract exists for this feature.

**Ruling: this diff contains zero rendered UI surfaces. `in_scope: false` for Mode A/B in the
classic sense (no templates/styles/components/markup, no DESIGN.md).**

## 4. The named adjacent surface — audited, not skipped

Dispatch named two human/agent-read text emitters and asked for an explicit ruling rather than a
skip. Ruling: **in remit as advisory** — these are exactly "terminal/CLI output presented to a
human" per my own scope definition (an operator debugging a blocked dispatch or a stuck spawn reads
this stderr/preamble text directly), even though their primary consumer is an LLM agent, not a
human at a keyboard.

**`inject-expertise.sh` preamble** (`.claude/skills/harness/bin/inject-expertise.sh:57-84`) — live-
executed against this tree (not just read): confirmed byte-identical output for the clean case —
```
## Harness control plane

HARNESS_CONTROL_PLANE_ROOT: <root>
HARNESS_PATH_DRIFT: none
```
Checked against plan.yaml's binding spec for this block (T-03 item 5, `plan.yaml:373-386`): drift
status must land "immediately after the HARNESS_CONTROL_PLANE_ROOT line" — confirmed true in both
source and live output. The `UNRESOLVED` branch (`inject-expertise.sh:60`) matches T-03 item 3's
literal text verbatim, including the `VERDICT: BLOCKED` remedy instruction. The five-pointer cap
(`sed -n '1,5p'`) and the `HARNESS_PATH_DRIFT: <n> unanchored path(s)` / `none` / `unknown` triad
all match `plan.yaml:373-390` and SC-01/SC-02 (`BRIEF.md:96-104`) exactly. Every branch's remedy
action is concrete (return `VERDICT: BLOCKED`, or "say so in your DIGEST") — no bare-fact-only
withhold message.

One non-blocking wording gap, advisory only: T-03 item 1's illustrative block text
(`plan.yaml:322-330`) includes an explanatory sentence — "Every Harness-owned path in your
instructions is written as `<HARNESS_CONTROL_PLANE_ROOT>/...`. Substitute the value above. It is
absolute and it is NOT your working directory." — that the shipped `control_plane_block()` does not
emit anywhere. I judge this **not a defect**: item 1 and item 5 of the same task's own intent
textually conflict (item 5 requires `HARNESS_PATH_DRIFT` to sit *immediately* after the root line,
leaving no room for item 1's sentence between them), no SC (`SC-01`/`SC-02`) or committed test
asserts the sentence's presence, and the identical substitution rule already ships to every one of
the 16 agents via `harness-handoff/SKILL.md:62-63` (preloaded, confirmed present, SC-09-covered).
The information reaches the agent through the channel the plan itself designates as authoritative
for the contract (SC-09); dropping the duplicate is the correct resolution of the two items'
conflict, not a completeness gap. Flagging as an `open_question` per the "wording matches an
approved plan's own text → plan question, not a defect" rule rather than filing a fix.

**`dispatch-guard.sh` stderr** (`.claude/skills/harness/bin/dispatch-guard.sh:140-181`) — read
against T-09's binding spec (`plan.yaml:747-765`) for its three exit-2 branches:
- no-tree-root-line: names the persona, spells `HARNESS-FEATURE-TREE-ROOT: ` literally, names the
  remedy command `inflight_registry.py feature-root --feature <declared>` — matches spec verbatim.
- non-absolute value: states "must be absolute" and `%r`-quotes the given value — matches spec.
- resolver mismatch: names both the declared and resolved paths — matches spec ("naming BOTH
  paths"); test spec (`plan.yaml:777-778`) only requires both values present in stderr, which holds.

No accessibility concerns apply to either surface (plain-text stderr/stdout, no colour-only state
encoding, no theme). No fidelity or interaction findings.

## Conclusion

- `in_scope: false` for the core UI-review remit (no rendered surface, no DESIGN.md) — measured,
  not predicted.
- The one adjacent surface the dispatch named was audited in full; both emitters are faithful to
  their governing plan clauses. One wording deviation found, ruled non-blocking and advisory
  (redundant channel already carries the same information; the plan's own two items conflict).
- Nothing here gates. No `must_fix`.

```yaml
VERDICT: PASS
DIGEST:
  headline: "No rendered UI surface in the 93-file diff (0 html/css/scss/tsx/jsx/vue/svelte/less hits, no DESIGN.md); the one named adjacent text surface (inject-expertise.sh preamble + dispatch-guard.sh stderr) audited and found faithful to plan.yaml, one non-blocking wording note."
  mode: B
  in_scope: false
  severity_max: low
  findings: 1
  must_fix: []
  states_unspecified: []
  contract_violations: []
  a11y: []
  open_questions:
    - { id: Q1, question: "inject-expertise.sh's control_plane_block() omits T-03 item 1's illustrative explanatory sentence ('Every Harness-owned path in your instructions is written as <HARNESS_CONTROL_PLANE_ROOT>/...'); item 5 of the same task's intent requires HARNESS_PATH_DRIFT immediately after the root line, textually conflicting with item 1's placement, and the identical rule already ships via harness-handoff/SKILL.md:62-63 (SC-09-covered). Is the dropped sentence an intentional resolution of the plan's own internal conflict, or should plan.yaml's T-03 intent be amended to match?", blocking: false }
  files_touched: []
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-52-factory-control-plane/.harness/harness/features/FEAT-52-factory-control-plane/notes/review-harness-ui-reviewer-impl-c9.md
```
