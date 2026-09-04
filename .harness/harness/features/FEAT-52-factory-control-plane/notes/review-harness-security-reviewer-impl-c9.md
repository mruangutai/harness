# Security review — FEAT-52-factory-control-plane @ d8c42a9d (impl-c9)

**Verdict: PASS.** In scope. Diff base = merge-base(pin, local main) = `8ff525e2`. HEAD of the
worktree is one commit ahead of the pin (`fa6efda6`, differs only in `feature.json`'s status
field) — reviewed strictly against the pin via `git diff <base> <pin>`. No critical/high finding.
One medium (verification gap, not a live exploit), one low (defense-in-depth hardening gap,
dynamically disproven as currently exploitable).

## Census — every file in the 93-file/6646-line diff, by security relevance

| File(s) | Relevance | Disposition |
|---|---|---|
| `dispatch-guard.sh` (+42) | trust-boundary machinery | audited in depth — see findings |
| `inject-expertise.sh` (+33/-9) | trust-boundary machinery | audited in depth — clean |
| `check-instruction-paths.py` (new, 128 ln) | doc linter, CI-gated | audited — read-only, no runtime write-authorization role, clean |
| `inflight_registry.py` (+8/-1) | adds `feature-root` CLI verb, thin wrapper over unchanged `feature_root()` | audited — clean |
| `check-domain.sh`, `harness_boundary.py` | **write-authorization boundary named in scope** | confirmed **byte-identical, zero diff** in this range (`git diff --stat` empty for both) |
| `run-unit-tests.sh` (+2), `.github/workflows/tests.yml` (+18) | CI gating | audited — both correctly read the real exit code, no silent-pass pattern |
| `test-anchor-directions.py`, `test-check-instruction-paths.py`, `test-inflight-registry.py` (+66, pre-existing file), `test-inject-expertise.py` (+19/-4), `test-check-domain.py` (+42, pre-existing file) | test coverage | ran directly (not just read) — see Evidence |
| `DECISIONS.md` (+64, DEC-212), `DECISIONS-INDEX.md` (+1) | design record | audited — documents and accepts the exit-0 fail-open contract for `inject-expertise.sh`, cites the two rejected alternatives (granting the shell-less leads `Bash`; a second injected value), matches shipped code |
| `.omp/agents/*.md` (16 files), `.claude/agents/*.md` (16 mirrors) | **SC-07 claims no write-grant widened — verified adversarially, not read** | every diff hunk reviewed by hand; zero new writable-path claims; see Evidence |
| `.harness/team-config.yaml` | the actual write-grant source of truth | confirmed **zero diff** in this range |
| `.claude/skills/*/SKILL.md` (14 files), templates, references | doc-anchoring only (`<HARNESS_CONTROL_PLANE_ROOT>`/`<HARNESS_FEATURE_TREE_ROOT>` placeholders) | spot-checked, no runtime effect |
| `.harness/harness/features/FEAT-52-*/**` (BRIEF, plan.yaml, notes, observations, feature.json) | feature bookkeeping, untracked-by-design | read for context only, no code |

## Findings

### MED — dispatch-guard.sh's T-09 block ships with none of its own mandated regression tests
`dispatch-guard.sh:141-179`. T-09's own `intent:` in `plan.yaml` specifies four named test cases
(REFUSED / ALLOWED / discrimination-in-the-other-direction / MISMATCH-REFUSED) to be added to
`test-dispatch-guard.py`. **None exist**: `grep -c "HARNESS-FEATURE-TREE-ROOT" test-dispatch-guard.py`
= 0, and the file's diff against the merge-base is empty (`git diff --stat -- '*test-dispatch-guard*'`
returns nothing). T-09's `verify: python3 .../test-dispatch-guard.py` therefore runs 42 pre-existing
cases that never exercise the new block, and passes trivially regardless of whether the new logic is
correct.

I do not rate this as an active vulnerability: I independently reproduced all four mandated cases
plus five adversarial ones the task didn't ask for (symlink-equivalent root, string-prefix-sibling
root, duplicate-line ordering, CRLF line endings, absolute-path-required) against the shipped script
via a synthetic checkout + subprocess harness, and every one resolved correctly — refusal on a
missing/mismatched/relative root, allow on a correct or symlinked-equivalent one, no effect on a
bash-holding persona, no string-prefix bypass. This is genuine identity-level evidence the mechanism
works *today*. The gap is that nothing in the committed suite protects it *tomorrow*: this is one of
the two gates this dispatch specifically asked to be proven un-bypassable, and it currently has zero
regression coverage of its own. Recommend landing the four cases exactly as specified in T-09's intent
before the next touch of this file.

### LOW — `dispatched` (T-09's persona-name value) is not anchored the way the identical class of value is anchored and tested in the sibling script
`dispatch-guard.sh:141-146`. `dispatched = ti.get("subagent_type") or ti.get("agent")` is checked only
with `dispatched.startswith("harness-")` (line ~62, pre-existing) before being spliced into
`os.path.join(owner_root, ".omp", "agents", dispatched + ".md")`. `inject-expertise.sh` faces the
identical threat (an attacker-influenced `agent_type` used to build a path) and anchors it with
`^harness-[a-z0-9-]+$`, with four adversarial regression cases in `test-inject-expertise.py` case12
(including a literal `harness-qa/../../etc` case) that I ran and confirmed pass. `dispatch-guard.sh`'s
T-09 block does not reuse that anchor.

**Dynamically disproven as exploitable today**, not merely argued: I built a synthetic checkout and
fired the real `dispatch-guard.sh` with `subagent_type` values containing `/../../..` sequences aimed
at real, existing off-tree files (including one, `harness-eng-lead.md`, whose real frontmatter has no
`bash` grant and should — on a naive reading — flip `has_bash` to `False` and require the
tree-root line). Every attempt resolved to `FileNotFoundError` and the safe `has_bash = True`
fallback, because `os.path.join`/`open()` require every intermediate path *component* to exist on
disk for a `..` to walk back out of it, and `.omp/agents/` (both the worktree's and the main
checkout's) contains **zero subdirectories** — confirmed with `find -maxdepth 1 -type d`. There is no
real directory to fabricate a traversal through. This is a fragile, not a live, gap: it would become
exploitable the instant any subdirectory ever appears under `.omp/agents/`. Recommend anchoring
`dispatched` with the same regex `inject-expertise.sh` already uses, for consistency and
future-proofing rather than an active fix.

### Assessed and clean — no finding
- **Command injection** in `inject-expertise.sh`'s new `control_plane_block()`: `$agent` is
  regex-anchored before use; `check-instruction-paths.py` is invoked as `python3 "$checker" "path1"
  "path2" ...` (argv, no shell eval of interpolated content) — confirmed by reading and by the
  passing `case12` adversarial suite (`harness-qa;id`, `harness-*`, path traversal — all exit 0, empty
  stdout, no leak).
- **Instruction injection**: the checker's full `VIOLATION` output (which could contain fragments of
  scanned file content) is deliberately never emitted — only `sed -n 's/^VIOLATION \([^:]*:[0-9]*\):.*/  \1/p'`
  extracted `path:line` locators reach the injected block (max 5, via `sed -n '1,5p'`), never the
  matched token or file content. This is well-designed, not merely absent-by-luck.
- **Exit-0-on-every-branch contract** for `inject-expertise.sh`: `set -uo pipefail`, no `set -e`, and
  the function is always followed by an unconditional final `exit 0`; T-14's `case14` text-scans the
  shipped script for `^[ \t]*exit [1-9]` with a proven positive control. I ran it directly: 18/18
  cases pass, including `case14`.
- **check-domain.sh / harness_boundary.py — the write-authorization boundary**: confirmed
  byte-for-byte unchanged in this diff. SC-15 ("an absolute feature-tree path is allowed from a
  foreign working directory") is **pre-existing behavior**, not new capability — the diff only adds a
  test proving it. I ran that test directly (`_feat52_foreign_cwd_receipt_pair` in
  `test-check-domain.py`, executed via `importlib`, not just read): it fires `check-domain.sh` with a
  `Write` to the absolute worktree receipt path from a foreign product-shaped `cwd`, asserts exit 0,
  and fires the SAME payload against the in-product twin path, asserting exit 2. Result: **True** — the
  pair discriminates correctly. No write permission is widened by this feature.
- **SC-07 (no write permission widened)**: `.harness/team-config.yaml` has zero diff in this range
  (confirmed via `git diff --stat`). Read every diff hunk of all 16 changed `.omp/agents/*.md` files
  (and confirmed the `.claude/agents/*.md` mirrors carry identical line-count deltas, consistent with
  `sync-agent-adapters.py` regeneration): every change is either a bare-path-to-`<HARNESS_CONTROL_PLANE_ROOT>`/`<HARNESS_FEATURE_TREE_ROOT>`
  anchoring edit, or an added sentence explicitly stating "Reading it is permitted and read-only; your
  write grants are unchanged" / "You hold no shell... `HARNESS-FEATURE-TREE-ROOT:`... arrives on your
  dispatch". Zero new writable-path claims naming a control-plane path.
- **Secrets/exposure**: the newly-injected `HARNESS_CONTROL_PLANE_ROOT: <absolute path>` block reaches
  only the same trusted local agent that already has `read` access to that path and everything under
  it (it's the agent's own control-plane root) — not a secret, not a new audience. No credential-shaped
  strings found in the diff outside the four named files (swept the full diff, not just those named in
  the dispatch, per this role's own P-14 pattern).
- **DoS on legitimate dispatches**: every new hard-block path in `dispatch-guard.sh` (missing/relative/
  mismatched `HARNESS-FEATURE-TREE-ROOT`) requires the *dispatcher* to have omitted or gotten wrong a
  value the same commit updates the orchestrator/lead doctrine to always supply; every parse failure
  on the guard's own side (`dispatched`'s tools file missing/unreadable/no `tools:` key) fails **open**
  (`has_bash = True`), consistent with the file's pre-existing documented posture that only the
  missing-`HARNESS-FEATURE:`-line branch fails closed. No new DoS vector found.

## Reconciling two open panel items (`plan.yaml:panel.findings`) — not new findings of mine, not re-raised

- `PF-4ea5b56692f0684ae2a69722b19bc74f` (open, med, reader `should-not-exist`): questions whether
  T-14's literal-text `exit [1-9]` scan can prove `inject-expertise.sh` always exits 0, since a bare
  `set -u` abort produces no literal `exit` statement. Still open, still in my domain (the exit-0
  contract), not independently re-verified further here — flagging for the validator-lead's awareness
  rather than duplicating.
- `PF-109101235d1aa59cc5da112515d9e256` (open, med, reader `goalcheck`): states no test fires
  `check-domain.sh` on the anchored absolute receipt path with the agent standing in a product base.
  **This appears to already be addressed**: `test-check-domain.py`'s `_feat52_foreign_cwd_receipt_pair`
  (added in this diff, see SC-15 above) does exactly that, and I ran it directly and confirmed it
  passes. Recommend the panel/goalcheck disposition be reconciled against this evidence rather than
  treated as still-open.

## Tooling note
The built-in `grep`/`read` tools returned false negatives/"path not found" against files I could read
directly with `bash cat`/`grep` at the same cwd in this worktree (e.g. a literal, confirmed-present
string in `dispatch-guard.sh` reported "No matches found"). Worked around by using `bash` directly for
all file reads and searches after the first occurrence. Everything in this report was verified through
`bash`, not the flaky tool path.
