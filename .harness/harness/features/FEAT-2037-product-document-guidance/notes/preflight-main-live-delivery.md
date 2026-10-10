# Main live-delivery preflight — FEAT-2037-product-document-guidance

## Result and boundary

One actual harness-orchestrator was dispatched: SuccessfulCougar. Both requested normal lead/member edges were admitted and performed read-only analysis. Product probe closed PASS for probe completion with missing inputs; engineering probe closed BLOCKED using canonical close-run --refused-return after the host refused its lead return. The orchestrator returned ESCALATE. This is not a clean end-to-end preflight pass, SC grading, UAT, formal validation, or ship readiness. No production, policy, manifest, fixture, approval, model, hook, schema, commit, PR or merge change was performed by this preflight. Neither the known failing suite nor other test suites were rerun.

Evidence verified by MAIN: feature.json contains ended_at for preflight-product and preflight-eng, verdicts PASS and BLOCKED respectively, cycles_used 0, and review_sha none. Orchestrator transcript records accepted close-run outputs for both, including refused-return for engineering; its final yield was accepted. The product digest has a host-appended fenced return; the engineering digest is analysis text, not an accepted bound return.

## Actual roots and injected skill sources

Observed injected HARNESS_CONTROL_PLANE_ROOT:

/Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2037-product-document-guidance

HARNESS_FEATURE_TREE_ROOT was not explicitly injected into the orchestrator context, and its environment probe showed no HARNESS_* root variables. The existing inflight_registry.py feature-root --feature FEAT-2037-product-document-guidance command resolved the feature root to that same worktree. That resolved root was propagated in real HARNESS-FEATURE-TREE-ROOT markers, not installed as an environment/configuration override. PRODUCT remained /Users/molchairuangutai/GitHub/harness.

MAIN inspected the actual JSONL custom_message/skill-prompt records, not just dispatch quotations. All five personas received the exact phrase `Consult the assigned product, not Harness` in their injected harness-principles content.

Common actual absolute source paths for all five:

- /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2037-product-document-guidance/.agents/skills/harness-handoff/SKILL.md
- /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2037-product-document-guidance/.agents/skills/harness-expertise/SKILL.md
- /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2037-product-document-guidance/.agents/skills/harness-principles/SKILL.md

Additional source-labelled delivered skills have that exact same absolute `.agents/skills/` prefix and the literal suffix `<name>/SKILL.md`:

- orchestrator: harness
- product-lead: harness-zero-micro-management, harness-team
- pm: harness-spec-driven, harness-craft, harness-brief
- eng-lead: harness-zero-micro-management, harness-team, harness-codebase-design
- dev-ops: harness-tdd-enforcement, harness-code-risk-grading, harness-craft, harness-codebase-design, harness-digest-dev

Persona-definition absolute source paths are not established by these skill records. No inferred role-named SKILL.md is claimed. The pm's own receipt listed only its three common skills; MAIN's transcript inspection additionally established its spec-driven/craft/brief delivery.

## Genuine nested dispatch and PRODUCT read ordering

Actual admitted edges and host IDs:

- MAIN → harness-orchestrator: SuccessfulCougar
- orchestrator → harness-product-lead: SuccessfulCougar.ProudWildebeest
- product-lead → harness-pm: SuccessfulCougar.ProudWildebeest.CurrentWombat
- orchestrator → harness-eng-lead: SuccessfulCougar.QuietSwordfish
- eng-lead → harness-dev-ops: SuccessfulCougar.QuietSwordfish.ProvincialFlea

The pm's actual nested prompt retained assigned PRODUCT identity, all three absolute pointers as read inputs, task:none, and the real feature marker. Its transcript proves these attempts, in order, before its missing-path answers and terminal return:

1. 2026-10-05T04:26:57.278Z — /Users/molchairuangutai/GitHub/harness/docs/spec.md:1-100 — not found.
2. 2026-10-05T04:27:00.126Z — /Users/molchairuangutai/GitHub/harness/docs/decisions.md:1-100 — not found.
3. 2026-10-05T04:27:03.161Z — /Users/molchairuangutai/GitHub/harness/docs/architecture.md:1-100 — not found.

Consequently empty-export return, adopted record separator, and participating components are all unanswered, tied respectively to those exact missing paths. No PRODUCT section was available. No CONTROL governance fallback supplied product answers.

Canonical evidence pointers:

- notes/research-preflight-product.md
- runs/preflight-product/digest.md (includes real nested prompt and accepted return)
- notes/receipt-harness-dev-ops-preflight-eng.md
- runs/preflight-eng/digest.md (analysis only; host refused binding)
- history://SuccessfulCougar and the four child IDs above

## Baseline mechanism and present-state discrepancy

The six integration failures reported by the operator remain ground truth; this preflight did not rerun them. Read-only engineering inspection confirmed the mechanism in `.agents/skills/harness/bin/check-plan-routes.py`: _owner_root follows legitimate worktree ownership, resolution_manifest uses the owner root and computes manifest deviation, and main counts deviation as a violation. The owner is /Users/molchairuangutai/GitHub/harness, not a replacement root chosen by this preflight.

However, the engineering reads found the two named manifests presently identical. MAIN independently ran only `cmp` on those exact two manifest paths; exit 0 established current byte equality. This does not establish that the earlier failures never occurred, authorize an owner update, or prove the suite now passes. The child consulted an older verification note claiming an operator-authorized fast-forward and later green integration result. That historical claim is not adopted as authorization or a green receipt for this request; MAIN did not execute or independently observe such recovery.

Supported non-bypass resolution IF the owner is stale: the upstream manifest-carrying baseline must be present on owner main, normally via an explicitly operator-authorized fast-forward-only owner refresh. Preserve dirty user logs and untracked Kaya artifacts; stop on conflict. Stash/reset/clean/checkout replacement/non-fast-forward alternatives require separate authorization. Root overrides, branch-only grants, policy edits, and weaker assertions are not resolutions. Because the manifests currently compare equal, this preflight does not recommend blindly performing another owner mutation or declare the prerequisite resolved.

## Host blocker, authorization and conduct limits

The engineering lead's real host refusal was:

`check-digest: REFUSED harness-eng-lead's return: authorization has no trusted hook-owned digest binding`

The child transcript also records released-claim messages and refused subsequent messages due to missing matching lineage. Its analysis exists on disk, but no accepted engineering lead return was manufactured. Diagnosing/restoring host digest binding is outside this feature's four Markdown edits and this preflight's authorization. Any enforcement/host repair needs separate explicit operator authorization and the applicable non-self-enforcement route; no repair was attempted here.

The orchestration was not wholly compliant with the requested bounded conduct: both cross-squad leads were batched in one task call despite resident playbook sequencing guidance; the engineering branch read older notes beyond the named archival receipt; the lead retried yielding after binding refusals rather than stopping after the first refusal. These deviations are reported, not converted into clean receipts. STATE.md and child artifacts contain historical recovery/next-step claims; they do not authorize further execution under this request.

STOP after this preflight. No SC is met or waived, no UAT pass is claimed, and no simplify, commit, formal validation, PR or merge is authorized.
