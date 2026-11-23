# FEAT-2397 T-05: doctrine landing table (SC-08 / SC-09)

Built main-session-direct (DEC-174) in this worktree on top of `afcb9816`. Every entry was rewritten in
place (DEC-205); no dated appendix was added. Each amended entry cites its plan-local successor as
`FEAT-2397-omp-native-cleanup, .harness/harness/features/FEAT-2397-omp-native-cleanup/plan.yaml, decisions[id=D-NN]`.
No bare D-NN and no new DEC number appear. Line anchors are the ones `gen-decisions-index.py` wrote at
this edit; read the current anchor from `DECISIONS-INDEX.md`.

## Amend and strike rows (`decisions_affected`)

| DEC | Disp. | Successor | What changed, and where |
|---|---|---|---|
| DEC-11 | amend | D-04 | `DECISIONS.md` DEC-11: the capability list is the native `.omp/agents` frontmatter (`spawns`, role-alias `model`, `thinking-level`, `blocking`, `autoloadSkills`), and "OMP resolves agents by name". The clause "Domain enforcement is registered in `.claude/settings.json`" now reads: the OMP extension calls `check-domain.py` on native write/edit/bash. The policy/capability split is kept. |
| DEC-59 | amend | D-04 | "Claude Code does not parse it" now reads "no host parses it". The `## Skills` deletion is recorded as history (DEC-63), not restored. |
| DEC-63 | amend | D-04 | `skills:` is now native `autoloadSkills:` delivered by OMP. Heading retitled to "native frontmatter skill preload". The no-obedience rationale is kept, and the Claude documentation evidence is marked as history. |
| DEC-64 | amend | D-01 | Heading and Chose now say: the `before_agent_start` handler sends the `SubagentStart` request label and gets back one `{"context": ...}` response, delivered unchanged. There is no `hookSpecificOutput` envelope. |
| DEC-81 | amend | D-04 | The intro marks the exit-2 and stdin rows as the current policy-script contract. The interpolation row is historical. The concurrency row says Claude's 20/200 is history and cites omp 19.1.0 `task/settings.ts` `task.maxConcurrency` default **32** (not overridden in `.omp/config.yml`). |
| DEC-101 | amend | D-01 | The table's Purpose column is native, and the request labels are internal. The Verified column, the zero-dependency figure and the settings INV-9 finding are framed as original measurements. The "domain hook belongs in frontmatter" lesson is marked as overturned by DEC-110. |
| DEC-110 | amend | D-04 | "Fix: register in `.claude/settings.json`" now reads "Fix, at the time…", and current deployment is the extension's `tool_call` handler. The main-session and non-harness pass-throughs are restated natively. Root resolution: the policy stays cwd-independent and now goes through `harness_boundary` (`HARNESS_PROJECT_DIR`). Heading retitled. The three-attempt evidence table is untouched. |
| DEC-111 | strike | DEC-233 | Replaced by a DEC-188 strike record: heading `STRUCK: … successor DEC-233`, with the number retained. Live citation repointed: DEC-202's supersession sentence no longer lists DEC-111 as live and names DEC-233 as governing its provisioning. No SPEC citation of DEC-111 existed. |
| DEC-112 | amend | D-04 | Of the three merge scripts, two survive (`merge-gitignore.py`, `upgrade-config.py`). The settings merge and the basename matching are history. The zero-dependency claim is in past tense. Onboarding evidence is kept. |
| DEC-127 | amend | D-04 | Item 3: the nine original hook cases are history, and the `stop_hook_active` pass-through is deleted. Item 4: "exactly one rejection deep" is rewritten — the yield path validates **every** yield, with no retry bypass. The harness-team §e claim is marked as since rewritten (DEC-237). |
| DEC-144 | amend | D-04 | "Registration is unconditional — the fifth `settings.json` prerequisite" now reads "Gating is unconditional": a historical settings note, and current gating through the extension on governed branch-creating Bash. |
| DEC-151 | amend | D-04 | "(sixth settings.json prerequisite; snippet template updated)" now reads: a Bash write gate (request label `PreToolUse`, tool `Bash`) that the extension runs on every governed `bash` call. The Bash policy and caller-bound Expertise text are unchanged. |
| DEC-155 | amend | D-02 | The "Mechanized at DEC-156: dispatch-guard.py…" paragraph is replaced by native `task.perCallModel: "off"` for every session, Main included. The project-narrows-operator rule is stated. Both former refusals (`dispatch-guard.py` model check, `taskModelOverride`) are deleted. The regression test is named (`tests/integration/test-check-omp-port.py`). The escalation route stays agent-visible. Pinned role models are retained. |
| DEC-156 | amend | D-02 | The whole dispatch-guard model bullet (registration, Main exemption, INV-9) is replaced by a "Per-call model authority" bullet. The digest, INV-15 and INV-16 checkpoint bullets are unchanged. |
| DEC-173 | amend | D-04 | The trigger paragraph describes the forced-retry bypass as former Claude behaviour. Open item 2 (the `stop_hook_active` pass-through) is recorded as closed: every yield validates. Honest gate reporting is unchanged. |
| DEC-198 | amend | D-03 | New "How the figure is read" paragraph: `ctx.getContextUsage()` at the same orchestrator `task` result wake, finite numeric `usage.tokens` only, the existing `resolveContextWarnTokens`/`resolveBudgetNumber` 200000 fallback, strict greater-than, advisory only. It explains that the session-accounting estimate comes before the provider anchor, and states there is no JSONL fallback. The stale `harness.json :169/:170` line pins are removed. Threshold, default and resolver policy are unchanged. |
| DEC-199 | amend | D-04 | The single-flight paragraph replaces the `SubagentStop`/`PreToolUse` hook wording and the one-hour TTL with extension dispatch/settle and supervisor-pid liveness (24h backstop). Both stop-sequence paragraphs are rewritten: every terminal yield with a live child is refused, and there is no `stop_hook_active` bound. Locking, the core and the union table are unchanged. |
| DEC-201 | amend | D-03 | The self-identification paragraph now describes the native `ctx.getContextUsage()` advisory. The JSONL/`getSessionFile` workaround and the #10097 limitation are recorded as a second retired scheme. The evidence paragraph separates **source evidence** (#10097 closed by `can1357/oh-my-pi#10098`, released v18.0.11; floor **omp ≥ 18.0.11**; published 19.1.0 source) from **host evidence**, which it does not assert: it names FEAT-2397's T-06 receipt as the place for it. The original 2026-08-28/29 measurements, no-wait scope, concern bands and watchdog data are kept. |
| DEC-208 | amend | D-04 | "It does not close the digest hook's `stop_hook_active` passthrough, which stays pre-existing and deliberate" now reads: no retry bypass, every yield meets these rules. The append-only, worktree-binding and INV-32 clauses are kept. |
| DEC-214 | amend | D-01 | Injection is by the extension's agent-start handler (request label `SubagentStart`; delivered context). The `settings.json` measurement is historical. The env-var reason is generalised (then `CLAUDE_PROJECT_DIR`). The spawn-time assertion runs the four-file checker **in process** (`harness_boundary.load_repo_module`, CLI kept), with states none / count-of-unanchored / unknown (any failure). Both anchors are retained. |
| DEC-218 | amend | D-04 | Heading drops "compatibility hosts". The compatibility-matching clauses are removed. "The two persona residues remain only on compatibility hosts" is rewritten as removed history. Liveness is one rule (OMP supervisor proof, 86400 s backstop, non-`omp` expired). The non-OMP binding horizon, `CLAIM_TTL_SECONDS` and the quarantine wording are recorded as removed (DEC-233). Exact OMP lineage and the unreadable-registry policy are kept. |
| DEC-222 | amend | D-04 | The `.claude/commands` generated-adapter rationale and the symlink "Over" are removed (they did not survive DEC-233); doors live only in `.omp/commands`. The `.claude/settings.json` precondition now reads: templates, the tracked hooks directory and `.omp/` configuration. The two-skill seam is kept. |
| DEC-233 | amend | D-04 | The dispatch-guard sentence now says the `claude` default is gone and a missing runtime is refused with the existing non-omp message, and that the `subagent_type`/`prompt` aliases are deleted. New "Leftover Claude arms (FEAT-2397)" bullet covers `stop_hook_active`, `CLAUDE_CODE_*`, `CLAUDE_PROJECT_DIR` and the snippet lines. New "retained internal Python ABI" paragraph covers the `PreToolUse`/`PostToolUse`/`SubagentStart`/`SubagentStop` labels, `agent_type`, capitalised tool names, and `hookSpecificOutput` policy-decision objects where live (the branch/gh-close/merge gates). It says these are extension-to-Python contracts, not Claude hosting, and that injection answers with context only. Authored `.claude` dirs, optional `CLAUDE.md` and Anthropic model IDs are retained. |

## Keep rows (preserved, not edited)

DEC-65, DEC-123, DEC-126, DEC-145, DEC-174, DEC-188, DEC-202 (apart from the DEC-111 citation repoint, which DEC-111's strike row requires), DEC-205, DEC-219, DEC-234, DEC-237, DEC-253 and DEC-256 were not edited.

## Index

`DECISIONS-INDEX.md` was regenerated with `gen-decisions-index.py`. The 23 affected ruling tails were rewritten; each is 30 words or fewer and cites its successor durably. DEC-111's tail is the strike tail naming DEC-233. `--stdout | diff` is empty.

## Other owned surfaces

- **`.omp/rules/harness-constraints.md`:** new bullet. Never pass a per-call `model`, because `task.perCallModel: "off"` is pinned and omp's error does not name the route. A stronger model goes to `open_questions` with evidence, is decided above the dispatcher and is recorded (DEC-155).
- **`SPEC.md`:**
  - Index rows §4 and §7.
  - §1 overview: OMP host, autoloadSkills, extension.
  - §3.1 manifest comment and capability table, and §3.2 Supabase/Astryx provider wording.
  - §4.0 native frontmatter schema: `spawns`, alias `model`, `thinking-level`, `blocking`, `autoloadSkills`; no hook field; the model pin.
  - §4.1 native tool names.
  - §4.2 settings JSON example replaced by the extension gate and its retained payload; Claude interpolation removed; root resolution through `harness_boundary`.
  - §5.1 Expertise delivery: request, context-only response and the drift states.
  - §5 rule row, §6 delivery row, §7 `autoloadSkills`.
  - §8.3: every yield validated; `SubagentStop` as an internal label.
  - §10.1 model authority.
  - §10.2 depth: `task.maxRecursionDepth: 3`, members `spawns: []`, concurrency 32.
  - §12 `task` call with `agent`/`task`/`tasks[]`, concurrency 32, lead tools, member leaves.
- **`.omp/commands/harness.md` §3:** one blocking `task` call with `agent: harness-orchestrator`, N flows as `tasks[]`, no per-call `model`, and the first line of `task` carries the marker.
- **`org.html`:** the depth and model prose now names `task.maxRecursionDepth: 3`, `spawns: []`, the role aliases `@deep`/`@strong`/`@review`/`@standard` and `perCallModel: "off"`. The digest host-boundary sentence was updated. Markup and styles are unchanged.
- **Owned bin modules (comments and docstrings only, no logic change):**
  - `check-domain.py`: the #749 import note is in past tense; the `_edit_reconstructed_content` docstring names the retained ABI payload. The historical `/tmp` CLAUDE_PROJECT_DIR measurement and the CLAUDE.md budget logic are kept.
  - `check-plan-routes.py`: the root-precedence docstring names `HARNESS_PROJECT_DIR` and `resolve_root`.
  - `check_state/ctx.py`: the root comment.
  - `check_state/run_state.py`: the INV-15 comment names validate-digest on the extension yield.
  - `check_state/worktrees.py`: the root comment.
  - `feature_schema.py`: the #749 docstring is in past tense.
- **`gitignore.snippet`:** only `.claude/settings.json.harness-bak` and `.claude/settings.local.json` were dropped.

## Left alone, as instructed

BUILD.md §0b and DEC-108/109 history, the authored `.claude/` directories, `disabledProviders: [claude]`, the optional `CLAUDE.md` reading and the Anthropic model IDs.

## Outside the file list (not edited; needs a ruling if wanted)

- `.harness/harness/docs/BUILD.md:948` still cites DEC-111 in its settings prerequisites row. BUILD is not in T-05's files and §0a/§0b are history.
- `.harness/team-config.yaml:96,163` and `templates/team-config.yaml:82,131` still say "Claude Code plugin" and "NOT a Claude capability" in `provision:`. SPEC §3.1/§3.2 now say "host integration"/"host capability".
