# pm — FEAT-45 consolidated fix cycle c1 — plan.yaml + BRIEF.md

Applied against the c0 draft at HEAD `1d3e5db`. Every finding from the four-angle simplify pass, the
architecture re-check and the ui-reviewer is applied; nothing declined. Plan is 11 tasks / 13
decisions, loads, topological, `0 violation(s)` from `check-plan-routes.py`. `approval.status:
pending` in both artifacts.

**BLUF — the measured A-02 fix is not the one the dispatch described, and the difference matters.**
The dispatch asked for a task that edits `SPAWNS` in `sync-agent-adapters.py` and "regenerates the
agent adapter files that map derives". Measured end to end: `SPAWNS` is read **only** by
`bootstrap_one()`, reachable only via `--bootstrap-from-claude`, and `bootstrap()` raises
`canonical agents already exist; refusing to overwrite` while `.omp/agents/harness-*.md` exist
(`sync-agent-adapters.py:244-245`) — so that map regenerates nothing. And `claude_adapter()` emits
`name, description, tools, color, model, effort, skills` only (`:210-218`), so `.claude/agents/**`
carries **no `spawns:` key at all**; a grep for one there could never pass. The shipped allowlist the
host enforces is the `spawns:` frontmatter of `.omp/agents/harness-validator-lead.md` — byte-identical
in shape to `harness-orchestrator.md`'s list, which is exactly what the observed refusal string
enumerated. So the load-bearing edit went into **T-06** (which already owns that file, `NOBODY` →
`main-session-direct`), and the map is kept in step by **T-11**, labelled as consistency-not-runtime.

## Dispositions

| Finding | Applied where |
|---|---|
| **A-02** blocking | T-06 edit 1 (canonical `spawns:` + the refusal string, quoted); T-11 (new, `team`/`harness-dev-ops`, lane row added for `sync-agent-adapters.py`); T-10 case 8 (standing assertion, both places, two checks); T-02 step-one paragraph; **D-14**; BRIEF **SC-15** (content, `automated`/`unit`) + **SC-16** (live spawn, `uat`), REQ-02 clause, `Verification gaps` bullet, corrected Constraints bullet |
| **A-01** blocking | id assignment struck from T-06's SHAPE list (replaced by an explicit `never IDENTITY:` line) and from T-02's closing comment; dedupe key made explicit (normalized summary + reader id) in both; D-05 `choice` now names pm-at-transcription as the single computer. T-06's `verify` greps `unrated`/`plan-panel`/`never CONTENT` — none touched the struck text |
| **ALT-01** | T-02 return contract: top-level mapping has exactly one key, `findings`; mirrored in T-06's SHAPE line |
| **SIMP-01** | D-10 struck, content folded into the `lanes:` comment; **ids not renumbered**, the D-10 gap is stated there |
| **EFF-01** | eight false edges dropped; policy comment on `tasks:` names the only two that bought throughput (`T-02<-T-01`, `T-09<-T-05`); `T-10<-T-09` kept with a write-lock comment on `run-unit-tests.sh` `UNIT_SCRIPTS`; new `T-10<-T-11` is a content edge, so T-11 is placed before T-10 to keep file order topological |
| **UI-F1** (stale-override half only, per the lead's amendment) | T-07 check 4 must contain the literal words `reworded` and `asked again` in an explaining sentence; T-08 case 6 asserts those words, not only the id; T-08 verify token list extended |
| **UI-F2** | BRIEF SC-11 now grades the zero-findings case explicitly: an empty `findings` list, reported as empty with the reader named, PASSES |

## Two defects found in this cycle that no reader filed

1. **T-06's `verify` could not pass.** `python3 sync-agent-adapters.py` with no argument exits 2
   (`argparse` mutually-exclusive group, `required=True`) — measured. And `git diff --quiet -- <a
   file this task just edited>` is non-zero by construction at verify time, since the task's edits
   are uncommitted. Replaced with `--apply && --check`, which proves the same idempotence and does
   not depend on commit state. Both forms run clean here.
2. `plan-merge.py` cannot express this cycle: it unions by id with no delete op (D-10) and exits 7 on
   a changed value for an existing id. Edits were made surgically instead; no sibling pm held the file.

## Evidence

- `check-domain.sh --resolve .claude/skills/harness/bin/sync-agent-adapters.py` → `harness-backend-dev
  harness-dev-ops` (exit 0). `.omp/agents/**` and `.claude/agents/**` → `NOBODY`.
- Nothing on disk validates a `spawns:` **entry**: `check-omp-port.py:95` requires only a list;
  `bootstrap_one():166-169` requires only that a non-empty list comes with the `task` tool. A
  non-harness name is structurally accepted.
- `general-purpose` is an observed real platform subagent type in this repo:
  `test-dispatch-guard.py:110` passes it as `subagent_type`, `test-context-watch.py:178` records it as
  a member `agent_type`, `validate-digest.py:877` names it as a platform agent sharing the hook.
- T-11's `verify` probe run against this tree: `AssertionError: ['harness-qa',
  'harness-code-reviewer', 'harness-security-reviewer', 'harness-ui-reviewer']`, exit 1 — it
  discriminates, and it will only green once the fix is built.
- `git status --porcelain`: no path under `.claude/` modified.

## Open for the operator (blocking, at signature)

Whether the host **resolves** `general-purpose` to a runnable agent once the allowlist admits it is
not determinable from disk — the observed refusal fired at the allowlist, before resolution. SC-16 is
the only thing that can settle it, and it is a `uat`. If the operator already knows the answer is no,
the persona in T-02/T-06/T-11 and D-14 must be repinned before signature.
