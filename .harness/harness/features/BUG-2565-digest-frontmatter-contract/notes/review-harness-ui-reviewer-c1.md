# Mode B UI review — BUG-2565

**PASS — scoped out (`in_scope: false`, `severity_max: n/a`).** Of 83 changed paths, only `.harness/harness/docs/org.html` is a directly rendered page. Its sole change is a static documentation paragraph (T-06 / SC-09, lines 282–288 at the pin), not a change to a contract-governed UI.

**Evidence.** Ran `git diff --name-only 104252db bb401aae`, inspected the page diff and pinned source, and checked design artifacts directly in `bb401aaea16b9b36a954daef3cebafb2401efe89`. The feature has no `DESIGN.md` or prototype there. The only tracked `DESIGN.md` names are the generic Harness template and the Kaya platform feature's design; neither governs `org.html`. The product paths `docs/spec.md`, `docs/decisions.md`, and `docs/architecture.md` are also absent at the pin. Under DEC-62/DEC-129 there is no visual contract to apply to this change.

The paragraph preserves its markup and place in reading order (except for replacing the old inline API names with the generator name). It introduces no controls, focus behavior, styles, theme tokens, or colour-only meaning. The changed text states the generated-frontmatter route and that an unchecked yield is refused; the page contains neither old schema key. Accessibility and dark/light design conformance are not graded. No browser/render checks, tests, or enforcement probes were run; rendered wrapping, size, and layout were not verified. No findings or open questions.

## Changed paths (grouped by exact prefix)

Only the `org.html` entry is a rendered page; other entries are documentation and feature records, agent/config/hook internals, or tests.

- `.claude/skills/`: `harness-team/SKILL.md`, `harness/bin/check-omp-port.py`, `harness/bin/digest_projection.py`, `harness/bin/gen-agent-output.py`.
- `.harness/`: `README.md`.
- `.harness/harness/docs/`: `BUILD.md`, `DECISIONS-INDEX.md`, `DECISIONS.md`, `SPEC.md`, **`org.html`**.
- `.harness/harness/features/BUG-2565-digest-frontmatter-contract/`: `BRIEF.md`, `STATE.md`, `feature.json`, `plan.yaml`, `observations/harness-pm.md`.
  - `notes/`: `answers-2026-11-27-02-plan-product.md`, `answers-2026-11-27-03-plan-product.md`, `answers-2026-11-27-04-plan-product.md`, `answers-2026-11-27-signoff.md`, `panel-c2-set-panel.yaml`, `receipt-main-session-build.md`, `research-BUG-2565-digest-frontmatter-contract-goalcheck-plan.md`, `research-answers-c3-apply.md`, `research-answers-c4-apply.md`, `research-digest-frontmatter-contract.md`, `research-frontmatter-binding-probe.md`, `research-panel-c1-apply.md`, `research-panel-c2-apply.md`, `research-panel-c3-apply.md`, `research-panel-c3-set-panel.yaml`, `research-plan-proposal.md`, `research-yield-refusal-probe.md`, `review-harness-code-reviewer-plan-c1.md`, `review-harness-code-reviewer-plan-c2.md`, `review-harness-code-reviewer-plan-c3.md`, `review-harness-ui-reviewer-plan-c1.md`.
  - `runs/2026-11-27-01-plan-product/`: `.run-identity.json`, `digest.md`, `sendback-criteria.md`, `state.yaml`.
  - `runs/2026-11-27-02-plan-product/`: `.run-identity.json`, `digest.md`, `panel-c1.md`, `state.yaml`.
  - `runs/2026-11-27-03-plan-product/`: `.run-identity.json`, `criteria.md`, `digest.md`, `panel-c2.md`, `state.yaml`.
  - `runs/2026-11-27-04-plan-product/`: `.run-identity.json`, `criteria.md`, `digest.md`, `panel-c3.md`, `state.yaml`.
  - `runs/2026-11-27-05-plan-product/`: `.run-identity.json`, `criteria.md`, `digest.md`, `panel-c4.md`, `state.yaml`.
- `.omp/agents/`: `harness-ai-dev.md`, `harness-backend-dev.md`, `harness-code-reviewer.md`, `harness-data-engineer.md`, `harness-dev-ops.md`, `harness-documentor.md`, `harness-eng-lead.md`, `harness-frontend-dev.md`, `harness-orchestrator.md`, `harness-pm.md`, `harness-product-lead.md`, `harness-qa.md`, `harness-security-reviewer.md`, `harness-ui-reviewer.md`, `harness-validator-lead.md`, `harness-visual-designer.md`.
- `.omp/`: `config.yml`, `extensions/digest-schema.ts`, `extensions/harness-hooks.ts`.
- `tests/integration/`: `test-check-omp-port.py`, `test-dispatch-guard.py`, `test-typescript-typecheck.py`.
- `tests/unit/`: `omp-hooks.test.ts`, `test-digest-projection.py`.
