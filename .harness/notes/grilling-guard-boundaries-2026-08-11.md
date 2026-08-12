# Grilling — issues #261 and #103, the guards' boundary rules — 2026-08-11

## Destination

There are exactly **two** places code is written under harness's authority, and both are governed
identically on **both** write surfaces. Anything else gets a verdict rather than silence. An agent
refused through one route cannot succeed through the other, and the third location cannot be
created in the first place.

## Settled

- **ONE feature, covering #261 and #103 together.** Both land in `bash-write-guard.sh` and
  `check-domain.sh`, both are DEC-174 carve-out files and therefore `main-session-direct`, and both
  are the same defect class: the guards disagree at their edges. Split across two features, the
  second pass edits functions the first just changed.

- **The two legitimate locations are already correct, and this feature does not touch them.**
  Verified at `a29ad06`:

  | Location | Purpose | Measured |
  |---|---|---|
  | `.claude/worktrees/<id>/` | harness developing itself, in-repo | out-of-domain **2**, in-domain **0** |
  | `workspace_root/<product>` | the factory working on a separate product | product globs apply, control-plane globs do not |

  The operator's architecture statement is the frame: harness develops itself in the live checkout
  and in worktrees under it; the factory works on products under `workspace_root`. Work is NOT done
  on harness in `workspace_root` — DEC-174 am.1 removed `mruangutai/harness` from the fleet and
  `test-no-distribution.py` asserts the absence.

- **A worktree outside `.claude/worktrees/` is a MISTAKE, not a supported shape.** It is neither
  location. That ruling settles #103's option list: **refuse it, do not resolve it.** Consulting
  `git worktree list` to map sibling worktrees back onto the globs was offered and declined — it
  adds a git call to every governed write in order to legitimise a location the architecture says
  should not exist, and it leaves any other prefix-dependent machinery still broken there.

- **BOTH doors are refused, not one** (operator, 2026-08-11):
  1. **Creating** a worktree outside `.claude/worktrees/` is refused at the Bash route. Today
     `git worktree add --detach ~/GitHub/harness-SIBLING HEAD` passes both hooks at exit 0 —
     neither guard has any notion of worktree creation. Catching the mistake afterwards is worth
     less than preventing it.
  2. **Writing** into one is refused with a verdict naming where worktrees belong. Today it is
     exit 0 in silence.

- **`bash-write-guard.sh` learns the SAME rule from the SAME source, not a fourth copy.** It
  currently holds **zero** references to `fleet`, `workspace_root` or `factory_config`, and carries
  its own separate worktree rule at `:405`. `check-domain.sh` already exposes `real()`,
  `resolve_fleet()`, `select_base()`, `is_control_plane_glob()` and `is_control_plane_target()` at
  module scope precisely so a second caller can reach them. Two copies of a boundary rule is the
  drift this org keeps finding; the guards already share `harness_yaml.manifest_domains` for the
  same reason.

## Not yet specified

- The mechanism by which `bash-write-guard.sh` reaches those functions. `check-domain.sh` is a bash
  file with an embedded Python heredoc, so it cannot simply be imported. Extracting the shared rule
  into an importable module is the obvious answer and is a real refactor of a carve-out file.
- Whether the creation refusal keys on `git worktree add` specifically, or on any command whose
  effect is a checkout outside the two locations. The narrow version is easy to route around; the
  broad version risks refusing ordinary git.
- Whether `check-state.sh` should also report a pre-existing sibling worktree at entry, so an
  environment that already has one is not silently half-governed.
- What happens to a sibling worktree that exists **today**. Refusing writes into it strands
  in-flight work rather than migrating it.

## Out of scope

- Changing how `.claude/worktrees/` or `workspace_root/<product>` are governed. Both are correct.
- Re-adding `mruangutai/harness` to the fleet. DEC-174 am.1, asserted by a test.
- The `Permitted for you:` stderr line (review-panel finding 2). The operator skipped it
  deliberately; it costs an agent retries, never a wrongful permit.
- `harness.json`'s `github.repo`, and the factory's per-repo board — that is #262 / FEAT-16.

## Facts I verified (so pm does not re-derive them)

Measured 2026-08-11 at `a29ad06`, after FEAT-15 merged.

- **#261 is live.** With `src/**` granted to `harness-backend-dev` and the target
  `<root>/src/main.py`: **Write exits 2, Bash `echo hi >` exits 0.** This is the DEC-151 failure
  shape — that guard exists *because* an agent routed around `check-domain.sh` via Bash.
- **#103 is live, and FEAT-15 did not touch it.** A sibling worktree is outside the harness root
  AND outside every workspace base, so it falls to the fourth branch, unchanged by design. That
  branch's comment — "`/tmp` is not the repo, is not deployed, and is not state" — is true of
  `/tmp` and false of a sibling worktree, which is the same repository, the same manifest, the same
  agents.
- **Creating one is unguarded.** `git worktree add --detach ~/GitHub/harness-SIBLING HEAD` returns
  exit 0 from `bash-write-guard.sh` and exit 0 from `check-domain.sh`.
- **Writing into one is unguarded**, measured against a real sibling worktree with three payloads,
  each of which exits 2 in the real checkout:

  | Write into the sibling | Exit |
  |---|---|
  | `harness-documentor` → `.claude/skills/harness/bin/x.py` | **0** |
  | `harness-documentor` → `.claude/agents/x.md` | **0** |
  | `harness-orchestrator` → `.harness/features/X/feature.yaml` | **0** |

- **The third row is the expensive one.** DEC-150's shape caps live in the same hook —
  `feature.yaml` 200 lines, `STATE.md` 120, handoff notes 60 — and go dark with the domain check.
  FEAT-09's orchestrator wrote a 205-line `feature.yaml` from a sibling worktree, unblocked, and
  reported the caps as "prose-only, not mechanically enforced": a correct conclusion from inside
  that tree, and wrong.
- `bash-write-guard.sh` contains **0** occurrences of `fleet`, `workspace_root` or
  `factory_config`, and its worktree rule is `re.match(r"^\.claude/worktrees/", rel)` at `:405`.
- `check-domain.sh` exposes `real()`, `resolve_fleet()`, `select_base()`, `is_control_plane_glob()`
  and `is_control_plane_target()` at module scope; the hook path and the `--resolve` path already
  share them, which is why those two cannot drift.
- **It fails in the safe-looking direction.** Every write succeeds and every log looks normal. An
  allow-list test cannot distinguish a working guard from an absent one — #103 records that three
  *permitted* writes were checked against a sibling worktree, all returned 0, and that was read as
  "the hooks are fine." **Whatever ships needs a FORBIDDEN write asserted refused.**
