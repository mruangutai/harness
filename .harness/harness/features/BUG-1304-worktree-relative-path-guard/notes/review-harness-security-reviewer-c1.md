Security review — BUG-1304, panel-c1, pinned `af5ddd7a` (verified byte-identical to worktree HEAD
`7cf52bc5` for all four reviewed code files: `git diff af5ddd7a -- <the 4 files>` = empty; the
`bash-write-guard.sh` behaviour tests below therefore evidence `af5ddd7a`'s own behaviour, not a
later edit).

## Headline

`bash-write-guard.sh`'s write-pattern detector does not recognize a bare `python3
inflight_registry.py {release,release-all}` invocation as a write, so ANY governed agent —
including a nominally read-only reviewer — can mutate or wipe the claim registry this feature's
whole authorization decision is keyed on, over Bash, with zero denial. That is a full,
single-session bypass of the claim-set binding BUG-1304 adds, strictly wider than the two residues
DEC-218 accepts as the cost of doing business.

## Finding 1 (HIGH, must_fix) — claim registry is a first-class attack surface bash-write-guard.sh does not see

**Scenario A — self-unbind.** Agent `harness-backend-dev` is dispatched for feature `FEAT-A`, holds
a live claim bound to worktree `FEAT-A`, and has `src/**` granted in `team-config.yaml`. Before
writing outside its own worktree, it runs, via its own Bash tool:

```
python3 .agents/skills/harness/bin/inflight_registry.py release --agent harness-backend-dev --feature FEAT-A --root <checkout>
```

Verified live against the pinned script (`bash-write-guard.sh:af5ddd7a`, byte-identical to
worktree): payload `{"agent_type":"harness-backend-dev","tool_name":"Bash","tool_input":{"command":
"python3 .agents/skills/harness/bin/inflight_registry.py release --agent harness-backend-dev
--feature FEAT-1 --root /tmp/xyz"}}` → **exit 0, empty stderr**. The command matches none of the
detector's patterns (redirect, `sed`/`perl -i`, `tee`, `mv`/`cp`, `rm`, `sponge`, `awk -i`, `git
worktree add/move`), so `findings` stays empty and the script exits at `if not findings:
sys.exit(0)` (`.claude/skills/harness/bin/bash-write-guard.sh` — the `findings` build block,
followed by the empty-findings exit near the end of the file) — before the domain walk, before
`claim_checkout_guard`, before even the reviewer read-only deny.

Once that claim is gone, the agent's *own next write* (Write/Edit or Bash, either route) computes
`harness_boundary.claim_worktrees(root, agent, destination)` over an empty claim set, and both
routes' `claim_checkout_guard` short-circuit: `if not claim_set: return` (check-domain.sh
`claim_checkout_guard`) / `if not claim_set: return []` (bash-write-guard.sh `claim_checkout_guard`).
Empty S = unbound = allowed, by REQ-01's own design — except this S was emptied by the agent
itself, mid-session, through a channel the guard never inspects. The agent can now write its
granted domain into ANY worktree or the main checkout, which is exactly the cross-feature leakage
BUG-1304 exists to close, and it needs no concurrent second session — DEC-218's two accepted
residues (FALSE-ALLOW, FALSE-REFUSE) both require a **concurrent same-persona session**; this does
not. It is a strictly wider hole than what was signed off.

**Scenario B — release-all, wider blast radius.** `release-all` needs no `--agent` at all:
`inflight_registry.py:main` dispatches it unconditionally to `release_all(root)`, which sets
`claims: []`. Verified live with `agent_type: harness-security-reviewer` (a role the guard's own
header calls "READ-ONLY: any detected write pattern is denied outright") — same payload shape,
`python3 .../inflight_registry.py release-all --root /tmp/xyz-doesnotexist` → **exit 0, empty
stderr**. This clears every claim for every agent and every feature in whatever `--root` is given
(any path the caller can name, not only its own), so one governed session — of any persona,
including read-only reviewers — can unbind every OTHER concurrently running session sharing that
registry in one call.

This is not a hypothetical the codebase is silent on: DEC-199 records `release-all` was "already
exercised, not hypothetical" and calls it dangerous enough that "a fix that can brick every later
dispatch is worse than the defect it prevents"; DEC-204 records the deliberate mitigation as
"recovery instructions and refusals print only feature/agent/claim-targeted commands, never
`release-all`. The older command remains an operator escape hatch but is not an automated remedy."
That mitigation stops the guard's *own refusal text* from suggesting it. It does nothing to stop an
agent from choosing to run it, and `bash-write-guard.sh` — the artifact whose entire stated purpose
is "close the casual Bash write bypass" (DEC-151) — still does not.

**Why this is not the accepted "arbitrary shell is unwinnable" residue.** The guard's own header
concedes generic obfuscated shell is out of scope and caught post-hoc. But `inflight_registry.py
release`/`release-all` is not obfuscation — it is the named, first-class, unobfuscated management
CLI for the exact security-critical store this new feature's authorization decision is keyed on
(`release_cmd()` even builds and prints this exact invocation as the *sanctioned* remedy in
single-flight refusal text today, for `harness-pm`). A feature whose whole job is "bind writes to
claim-set membership" has to treat claim-registry mutation as inside its own threat model, not as
generic shell noise.

**Anchors (af5ddd7a):**
- `.claude/skills/harness/bin/bash-write-guard.sh` — finding-pattern block (redirect/sed/tee/mv/cp/rm/sponge/awk/git-worktree only) and the `if not findings: sys.exit(0)` short-circuit ahead of the reviewer deny and the domain walk.
- `.claude/skills/harness/bin/harness_boundary.py:claim_worktrees` / `claim_set_refusal` — `if not claim_set: return` (empty-S-is-allowed).
- `.claude/skills/harness/bin/inflight_registry.py:release_all`, `main()` `release`/`release-all` dispatch, `RELEASE_ALL_CMD`.
- `.harness/harness/docs/DECISIONS.md` DEC-199 ("already exercised, not hypothetical"), DEC-204 ("never `release-all`. The older command remains an operator escape hatch").

## Finding 2 (MED, advisory) — claim_checkout_guard fails open on any exception besides AmbiguousWorktree/UnreadableRegistry

`harness_boundary.claim_worktrees` calls `worktree_for_feature(owner_root, claim.get("feature"))`
with **no default** for a missing `"feature"` key. `live_claims`'s v2 read path
(`schema_version==2` shape) does not validate individual claim dicts beyond "is a list" — a v2
registry with `{"claims": [{"agent": "X", "started_at": ...}]}` (no `"feature"` key) passes the
`UnreadableRegistry` shape check untouched. If that agent's own claim set is otherwise non-empty
(≥1 real worktree exists), `worktree_for_feature`'s list comprehension evaluates
`feature_id.startswith(...)` with `feature_id is None` → uncaught `AttributeError`.

Both routes' `claim_checkout_guard` catch `AmbiguousWorktree` (deny) and `UnreadableRegistry`
(deny), but any *other* exception — this one included — hits the generic
`except Exception as exc: ... print("...passing through..."); return` and the write is **allowed
unenforced**, with only a stderr line an agent has no reason to read twice. This is the same
fail-open shape SC-10 was written specifically to close for the unreadable-registry case; a
malformed-but-readable claim entry is a sibling failure mode SC-10's fixture does not cover, and no
test in `tests/unit/test-harness-boundary.py` or `tests/integration/test-inflight-registry.py`
exercises a claim missing `"feature"`.

Reachability is lower than Finding 1: it requires writing a malformed registry entry directly
(bypassing the sanctioned CLI, which always sets `"feature"` via `claim_with_receipt`'s
`feature=LEGACY_FEATURE` default), which is the generic "arbitrary shell" gap DEC-151 already
accepts. Reported because the failure mode is silent and structurally identical to the one L-01/F1
were fixed for, so it is worth the same hardening (catch the narrower set of exceptions the code
actually expects, or treat any exception in this specific guard as fail-closed the way
`UnreadableRegistry` already is).

**Anchors:** `.claude/skills/harness/bin/harness_boundary.py:claim_worktrees` (`worktree_for_feature(owner_root, claim.get("feature"))`, `worktree_for_feature`'s `feature_id.startswith`), `check-domain.sh:claim_checkout_guard` and `bash-write-guard.sh:claim_checkout_guard` (`except Exception as exc:` blocks).

## Probe 3 (Information disclosure) — assessed, low/advisory only

`claim_set_refusal`'s `held` list is built only from claims matching the refused agent's own
`agent_type` (`inflight_registry.live_claims(root, agent)` filters on `agent=` alone), so it never
names another persona's claims. It DOES, however, list every worktree the *same persona's other
concurrent sessions* hold — which is precisely DEC-218's accepted FALSE-ALLOW shape made visible:
a session refused for writing outside worktree A learns, from the refusal text itself, that a
sibling session of the same persona currently holds worktree B, and could then deliberately target
B rather than merely stumbling into it. This does not create the residue (D-03/DEC-218 already
accept it) but it turns an accidental one into a discoverable one. Advisory only, not must_fix: the
information is same-trust-level (an agent already learns feature ids and worktree layout from
`git worktree list`), and the residue itself is signed off.

## Probe 4 (Input validation / injection) — assessed, no finding

- `_git_subcommand`/`_worktree_destination`/`_moves_head` and the `git -C <checkout>` calls in
  `harness_boundary.linked_worktrees`/`worktree_owner` all use list-form `subprocess.run`, never
  `shell=True`; no attacker-controlled string reaches a shell.
- `worktree_for_feature`'s prefix rule (`feature_id.startswith(basename + "-")`) is exercised by
  `tests/unit/test-harness-boundary.py:case_worktree_for_feature` for exact-match, short-form
  prefix, unrelated-id, the hyphen-boundary edge (`FEAT-XY` vs. `FEAT-X` correctly returns `None`,
  not a false match), and the two-candidate ambiguity (refuses rather than guesses). No CLI command
  exposed by `inflight_registry.py` *creates* a new claim (`claim`/`claim_with_receipt` are Python
  API only; `attach` only attaches identity to an *already-matching* existing claim), so a crafted
  `feature` string cannot be introduced through the sanctioned CLI to abuse this prefix rule —
  fabricating one requires the same raw-registry-write precondition as Finding 2.
- No regex is compiled from attacker-influenced input; `glob_to_re` compiles only
  `team-config.yaml` patterns (operator-owned).

## Threat model

| boundary | stride | mitigated |
|---|---|---|
| governed agent → claim registry (release/release-all via Bash) | T, E | false — Finding 1 |
| governed agent → claim registry (malformed entry → AttributeError) | T | false — Finding 2 |
| refusal message → same-persona sibling session's worktree/feature id | I | false — advisory only, pre-accepted residue (DEC-218), not gating |
| destination path resolution (prefix match, symlinks, git pointer parse) | T | true |
| git subprocess argv construction | T (injection) | true |

## Settled matters, not re-litigated

Unreadable-registry fail-closed (including OSError), quarantine machinery's own fail-open, the two
accepted DEC-218 identity residues as *described* (both match plan.yaml D-03/DEC-218 wording
verbatim), and the payload-identity constraints (no `feature`/`session_id` on write payloads).

```yaml
VERDICT: FAIL
DIGEST:
  headline: bash-write-guard.sh's write-pattern detector does not see `inflight_registry.py release`/`release-all` over Bash, so any governed agent (incl. read-only reviewers) can empty or wipe the claim registry BUG-1304's whole binding decision depends on, with zero denial — verified live, exit 0 both ways
  in_scope: true
  scope_reason: this diff is the authorization boundary itself (claim-set membership decides allow/deny on every governed write); reviewed all twelve files plus the claim-registry CLI surface they call into
  severity_max: high
  findings: 2
  must_fix:
    - "bash-write-guard.sh's finding detector must treat `inflight_registry.py {release,release-all}` (and any other direct mutator of `.harness/.inflight-claims.json`) as a write, gated at least as strictly as domain/claim enforcement — otherwise claim-set binding is opt-out for any governed agent over Bash. Anchors: bash-write-guard.sh finding-pattern block; harness_boundary.py:claim_worktrees `if not claim_set: return`; inflight_registry.py release/release-all."
  threat_model:
    - { boundary: "governed agent -> claim registry (release/release-all via Bash)", stride: "T,E", mitigated: false }
    - { boundary: "governed agent -> claim registry (malformed entry -> AttributeError fail-open)", stride: "T", mitigated: false }
    - { boundary: "refusal message -> sibling same-persona session's worktree id", stride: "I", mitigated: false }
    - { boundary: "destination path resolution (prefix match / symlink / git pointer)", stride: "T", mitigated: true }
    - { boundary: "git subprocess argv construction", stride: "T", mitigated: true }
  open_questions:
    - { id: Q1, question: "Should bash-write-guard.sh's finding detector be extended to recognize inflight_registry.py CLI invocations (release/release-all/reconcile) as writes needing at least the same claim-checkout scrutiny as any other governed write, or should claim-registry mutation be restricted to a non-Bash-reachable seam entirely (e.g. only invoked in-process by dispatch hooks, never as an agent-issued CLI)?", blocking: true }
  files_touched: []
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-1304-worktree-relative-path-guard/.harness/harness/features/BUG-1304-worktree-relative-path-guard/notes/review-harness-security-reviewer-c1.md
```
