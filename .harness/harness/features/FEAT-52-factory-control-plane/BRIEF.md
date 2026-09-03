# BRIEF — FEAT-52 Factory control-plane root

## Problem

Every Harness instruction that names a Harness-owned path names it *relatively* — `.harness/harness.json`,
`.harness/expertise/<agent>.md`, `.claude/skills/harness-systematic-debugging/SKILL.md`. Until the
factory, the agent's working directory was always the Harness checkout, so those paths resolved. A
factory worker stands in a **product checkout**, where the same string resolves against the product.
Issue #356 swept the instruction surface and found **five path families at risk**, two of them carried
by skills preloaded into all 16 agents. Three severities: a denied write (loud), a wrong read (silent
and dangerous — the qa gate applies the wrong matrix), and a **missing read with no signal at all** —
a doer told to read the debugging protocol from a product clone finds nothing, because FEAT-12 ended
skill distribution, and debugs without the discipline it was told to use. The obvious anchor is
foreclosed: `CLAUDE_PROJECT_DIR` is session-scoped and measured **unset** in an agent's own tool shell
(#356 comment 4), so an agent cannot anchor its own paths with it. #496's first real kaya-ai factory
proof is blocked on this, and four #498 destination criteria depend on that run.

## Goal

A factory worker operating in a product checkout can reliably use Harness's control plane: it is told,
in its own starting context, the absolute control-plane root; every Harness-owned path in the
instructions it receives is written against that root; and a new relative path cannot silently
re-enter the instruction surface.

## Requirements

- REQ-01: A factory agent can read the absolute Harness control-plane root from its own starting
  context, without depending on a session-scoped environment variable or on its working directory.
- REQ-02: Every Harness-owned path in an instruction a factory-dispatched agent can receive is written
  so it resolves to the control plane rather than to the agent's working directory.
- REQ-03: A factory agent may read Harness-owned skills and rule files through that root, read-only,
  and no product-checkout write permission is widened to achieve it.
- REQ-04: A relative Harness-owned path newly introduced into a factory-reachable instruction is
  rejected by an automated check before it ships.
- REQ-05: A spawn whose control-plane root cannot be resolved is visible to the agent itself rather
  than silent, and the spawn is still never blocked.
- REQ-06: An instruction distinguishes a READ of a Harness-owned file from a WRITE into a feature
  directory, and each resolves to the checkout that holds it: a read to the Harness control plane,
  a write to the checkout that holds that feature's directory — the feature's own worktree where
  one exists, and the control plane where none does. The write anchor is **resolvable by every
  persona the anchor binds**, including the personas that hold no shell and therefore cannot run
  the resolver themselves; a persona left unable to resolve it is refused loudly rather than left
  to guess a root.

## Constraints

Named by number; each says whether it BLOCKS or SUPPLIES.

- DEC-100 SUPPLIES: `SubagentStart` fires for nested spawns, so the one registered hook reaches
  lead-spawned members, not only top-level agents.
- The `inject-expertise.sh` contract BLOCKS one design: `DECISIONS.md:1503` and the script's own
  header fix it at "always exits 0 so it can never block a spawn", and all seventeen of its existing
  cases assert exit 0. An assertion that exits 2 from that hook contradicts a signed contract.
- FEAT-42 T-16 SUPPLIES the resolver: `harness_boundary.resolve_root(<bin dir>)`, reached through the
  script's own directory, never from cwd or the environment. The root is already computed; what is
  missing is carrying it to the agent.
- DEC-174 BLOCKS team execution of most of this work: hooks, validators and gate scripts — and the
  test file of each — are changed directly by the main session, never dispatched through a team run
  whose gates are the thing being changed.
- DEC-183 SUPPLIES the enforcement route for a new checker: a required step of the `integration` CI
  job, the precedent `check-plan-routes.py` set.
- DEC-182 SUPPLIES the plan format; `plan-merge.py` is the only write route.
- DEC-204 SUPPLIES the feature identity a write anchor needs: the FIRST line of every governed
  dispatch is exactly `HARNESS-FEATURE: FEAT-NN-slug`, refused by `dispatch-guard.sh` when absent,
  so an agent always holds its own feature id with certainty. The same decision BLOCKS the
  hook-side alternative: `dispatch-guard.sh:76-80` records the measurement that `tool_input.prompt`
  exists only on the dispatch payload and reaches no other hook, so `inject-expertise.sh` cannot
  know which feature a spawn belongs to.
- DEC-116 BLOCKS the obvious remedy for the shell-less case: `harness-product-lead`,
  `harness-eng-lead` and `harness-validator-lead` hold no `Bash` **by design**, so a lead cannot do
  a member's work — and all three write into a feature directory as normal operation (the run dir
  and the team digest, `harness-team/SKILL.md:44-52`). Granting them a shell to fix a
  path-resolution defect is out of scope here for the same reason D-05 refuses widening a domain
  to fix one.
- FEAT-12 SUPPLIES the fact that makes family five silent: products carry no Harness skills.
- Out of scope, and untouched: running or testing kaya-ai product code; widening product-checkout
  write permissions for control-plane records; the `bin/` -> `src/` source-location question (#357,
  which is neither upstream nor downstream of this).

## Success Criteria

The five path families are #356 comment 2's enumeration. F2 and F3 share one file, so the five
families name FOUR distinct sites; a fifth is added because it reaches `harness-pm` and
`/harness-init`. THIS FIVE-SITE LIST IS CANONICAL — every criterion and every task below uses it
by name, and no substitution is permitted:

- S1 `.claude/skills/harness-qa-gate/SKILL.md` — F1, `harness.json`
- S2 `.claude/skills/harness-expertise/SKILL.md` — F2 Expertise, and F3 the observations log
- S3 `.claude/skills/harness-handoff/SKILL.md` — F4, the receipt
- S4 `.omp/agents/harness-backend-dev.md` — F5, the debugging skill read from a product clone
- S5 `.claude/skills/harness/templates/PLAN.md` — control-plane paths reaching `harness-pm`

S2's F3 and S3's F4 are WRITE targets and anchor to the feature tree under REQ-06. Every other
path in this list is a READ target and anchors to the control plane.

- SC-01: A harness agent spawn receives an injected block whose first line is
  `HARNESS_CONTROL_PLANE_ROOT: <absolute path>`, and that block is emitted even when the agent has
  no Expertise file at any of the three tiers — the case where the hook emits nothing today. The
  asserted case runs with the process working directory set to a temporary directory that is NOT
  the resolved root, and the test asserts the injected path DIFFERS from that working directory. A
  case in which the two coincide cannot fail for the reason this feature exists.
  verify: automated        evidence: integration
- SC-02: When the root cannot be resolved, the hook still exits 0, and the injected block says the
  root is UNRESOLVED and instructs the agent to return `VERDICT: BLOCKED`. Both branches are
  asserted. The no-non-zero-exit clause carries its own assertion: the committed test greps the
  shipped script for `^[[:space:]]*exit [1-9]` and asserts ZERO matches, and in the same case
  asserts the SAME pattern DOES match a one-line fixture reading `exit 2` — the positive control,
  without which a search that errored reads as an absence.
  verify: automated        evidence: integration
- SC-03: The lint's scope is demonstrably complete: `check-instruction-paths.py --list-scope` prints
  one factory-reachable instruction file per line, and the test asserts the presence of EACH of the
  five canonical sites S1-S5 above with five separate assertions. A count is not evidence; the Nth
  file is named individually.
  verify: automated        evidence: integration
- SC-04: `check-instruction-paths.py` exits 0 over the whole declared scope at the reviewed sha, and
  each of the five canonical sites S1-S5 separately shows its path written with the correct anchor
  prefix for its direction — one assertion per site, read via `git show <review_sha>:<path>`, never
  the working tree.
  verify: automated        evidence: integration
- SC-05: The lint can report RED, on BOTH shapes it must see. Run against a negative fixture whose
  scope files hold exactly two relative `.harness/` instruction paths — one inside a
  backtick-delimited inline span, one inside a fenced code block opened by three backticks — the
  checker exits non-zero, its output names the fixture file AND the offending line number for EACH,
  and its summary reports two violations. The fenced case is required, not decorative: S2 carries
  the observations write path inside a fenced block, and a fixture exercising only the inline shape
  leaves that blind spot untested and green.
  verify: automated        evidence: integration
- SC-06: F5 is answered by anchoring PLUS read-through, proven in both directions: with the process
  working directory set to a temporary product-shaped checkout carrying no Harness skills, the
  debugging-skill path as written in a doer's instruction resolves against the injected root and
  opens; and the same path with the placeholder stripped — the pre-change spelling — does not
  exist relative to that working directory. The second half is what makes the first discriminating.
  verify: automated        evidence: integration
- SC-07: No write permission widened. Between the base sha and the reviewed sha, the set of
  write-granted path patterns in `.harness/team-config.yaml` is unchanged, and no agent file gains a
  writable-path claim naming a control-plane path.
  verify: inspection
- SC-08: The lint is enforced, not merely present: the `integration` job in
  `.github/workflows/tests.yml` runs the checker and fails the job on its non-zero exit — asserted
  by a test that reads the workflow file, the precedent `test-check-plan-routes.py` case 25 set —
  and that assertion is itself shown able to report RED. The same committed test feeds it two mutant
  workflow files materialised into a temporary path: one with the checker step deleted, one with the
  step present but its non-zero-exit failure branch removed. It asserts the assertion FAILS on each.
  An assertion never shown red is not evidence that the job can fail.
  verify: automated        evidence: unit
- SC-09: The contract is discoverable by the agents it binds: `harness-handoff/SKILL.md`, preloaded
  into all 16 agents, states BOTH placeholder rules — `HARNESS_CONTROL_PLANE_ROOT` for reads and
  `HARNESS_FEATURE_TREE_ROOT` for feature-directory writes, with the command that resolves the
  second — and the read-only policy; and a signed `DEC` entry records the ruling with an index row.
  verify: inspection
- SC-10: The write anchor resolves to the checkout that HOLDS the feature directory, and cannot
  collapse onto the control-plane root when that feature has its own checkout. Against a temporary
  owner root carrying a linked worktree whose basename is `FEAT-90-alpha`,
  `inflight_registry.py feature-root --feature FEAT-90-alpha` prints that worktree's absolute path
  and the test asserts the printed value DIFFERS from the owner root; for `FEAT-91-beta`, which has
  no worktree, it prints the owner root. The first assertion is the discriminating one — it goes red
  the moment the resolver answers with the control plane for a feature held somewhere else.
  verify: automated        evidence: integration
- SC-11: No instruction anchors a feature-directory WRITE to the control-plane root.
  `check-instruction-paths.py` reports a VIOLATION for any span beginning
  `<HARNESS_CONTROL_PLANE_ROOT>/.harness/<repo>/features/`, proven RED against a negative fixture
  holding exactly that span — exit non-zero, naming the fixture file AND line. The checker exits 0
  over the whole declared scope at the reviewed sha, and S2 and S3 are each separately shown
  writing their feature-directory paths under `<HARNESS_FEATURE_TREE_ROOT>/`, read via
  `git show <review_sha>:<path>`.
  verify: automated        evidence: integration
- SC-12: The spawn-time assertion can report RED on PATH DRIFT for the agent actually spawning, not
  merely on an unresolved root. `inject-expertise.sh` scans the four instruction files every harness
  agent receives — `.omp/agents/<agent_type>.md` and the three always-preloaded skills
  `harness-handoff`, `harness-expertise`, `harness-principles` — with the lint's own rule, and emits
  either `HARNESS_PATH_DRIFT: none` or `HARNESS_PATH_DRIFT: <n> unanchored path(s)` followed by up
  to five `<file>:<line>` lines. Two committed cases against a fixture root: a clean agent file
  yields `none`; the SAME file with one relative `.harness/` span yields the count line naming that
  file AND that line number. Exit status is 0 in both, so DECISIONS.md:1503's contract is unbroken.
  verify: automated        evidence: integration
- SC-13: A persona that holds no shell is never left to guess its write anchor, and the refusal is
  observable at runtime. Against a temporary owner root carrying `.omp/agents/` entries for one
  shell-less persona (`harness-product-lead`, tools `read, glob, grep, task, write`) and one that
  holds `bash` (`harness-backend-dev`), `dispatch-guard.sh` is fired with four payloads and
  asserted separately on each: a dispatch to the shell-less persona carrying no
  `HARNESS-FEATURE-TREE-ROOT:` line exits 2 with stderr naming that persona AND the missing line;
  the same dispatch carrying the line with the value `inflight_registry.feature_root` resolves
  exits 0; the SAME omission in a dispatch to the `bash`-holding persona exits 0; and a
  tree-root line naming some other absolute path exits 2 with stderr naming both paths. The third
  assertion is what makes the first discriminating — without it a guard that refuses everything
  passes — and the whole criterion goes RED the moment a persona bound to the write prefix has no
  route to resolve it.
  verify: automated        evidence: integration
- SC-14: The shell-less route is stated where the personas it binds actually read it. Read via
  `git show <review_sha>:<path>`, EACH of `.omp/agents/harness-product-lead.md`,
  `.omp/agents/harness-eng-lead.md` and `.omp/agents/harness-validator-lead.md` states that the
  persona holds no shell, that its feature-tree anchor arrives on the dispatch line, and that an
  absent line is `VERDICT: BLOCKED` rather than a guessed root; `.omp/agents/harness-orchestrator.md`
  states the matching emit duty; and `harness-handoff/SKILL.md`, preloaded into all 16 agents,
  carries the exception beside the self-resolution command. Four separate per-file findings, never
  a count.
  verify: inspection
- SC-15: The anchored feature-directory WRITE is allowed from where a factory worker actually
  stands, not only from the harness checkout. `check-domain.sh` is fired with a `Write` whose
  `file_path` is the ABSOLUTE receipt path under the feature tree root, with the process working
  directory set to a temporary product-shaped checkout that is NOT that root, and the test asserts
  exit 0. That half alone is not evidence: exit 0 is also what a path outside every base returns,
  so the SAME fixture and the SAME working directory fire the in-product twin of that path and
  assert exit 2. The pair is what discriminates — an allow-all guard fails the refusal half, and a
  guard that stops adjudicating from a foreign working directory passes the allow half for the
  wrong reason. This is the write-side twin of SC-06 at the same level of proof: every existing
  allow case inherits the harness checkout as its working directory, and the only two cases that
  set one assert REFUSE, so the conjunction ALLOW x product-shaped cwd is measured nowhere else.
  verify: automated        evidence: integration

## Verification gaps

- `component`, `ui`, `eval` and `typecheck` carry `cmd: null` in `.harness/harness.json`, and
  `functional` is `excluded` under DEC-187. This feature touches none of their surfaces; every SC
  above rests on `unit` or `integration`, and both are active.
- **No factory worker has ever run.** SC-06 proves the read from a *simulated* product-shaped cwd, not
  from a real factory workspace at `workspace_root/<product>`. What is therefore NOT proven here is the
  end-to-end behaviour of a real factory dispatch; #496 carries that, and this feature is its
  precondition, not its substitute.

## Approval

status: approved
approved-by: mruangutai
date: 2026-09-02
