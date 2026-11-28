# FEAT-2557 · T-01 security review · cycle 1

**PASS — no new security surface or weakened guard. No findings.**

**Pinned census (SC-06).** `git diff --stat` from merge base `cf7b422b2e55ae4c9129a8009e240b56c6e25035` to `5c600680e7f46af124fa3281392fa7b25623e982` reports **24 files, +995/−0**: **five shipped Markdown files, +98/−0**, and **19 feature records, +897/−0** (Markdown, YAML and JSON). No hook, gate, validator, schema, test, or executable-mode change. This is a delta review, not a security certification of the existing runtime.

| Shipped path | Security scope |
|---|---|
| `.claude/skills/harness-codebase-design/SKILL.md:57,92` | Adds layout guidance and review checks; neither tells authors to skip validation. |
| `.claude/skills/harness/bin/LAYOUT.md:12–21` | Describes importing from the entry's own directory, as `plan-merge.py:132–135` already does. No caller-controlled import path or bootstrap change. |
| `AGENTS.md:25,50` | Adds a fixed local pointer and a reading instruction; existing constraints remain. |
| `.harness/harness/docs/DECISIONS.md:8758` and `DECISIONS-INDEX.md:242` | Review-only enforcement applies to the **new layout convention**; it does not retire any guard. The approver's name and date are intentional decision attribution, consistent with the base decision record. |

**OWASP / STRIDE.** No changed authentication, authorization, input-validation, dependency or request path; no new injection sink, log or export behavior, or other runtime trust boundary. Manual inspection and a common credential-pattern screen found no secrets, access tokens or private contact details. Feature records contain approver attribution, local account paths already present in prior records, and run IDs and hashes, not credentials. T-01's `verify` clears `HARNESS_AGENT_TYPE` only inside the signed main-session verification shell; it invokes document checks, not role-gated approval or write commands, and cannot change the host's prior domain/Bash checks (`.omp/extensions/harness-hooks.ts:1784–1811`). The INV-32 routing note records the one approved task; it does not grant new permissions or instruct agents to bypass a hook.

**Open questions:** None. Static inspection only; no test or build reruns.
