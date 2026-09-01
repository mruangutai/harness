# Security review — FEAT-50-run-artifact-integrity (pinned `9f2a070..dca2d3d`)

## Headline

The tool-route checkout binding (`check-domain.sh`) is sound for every shape tested. But its
Bash-route twin (`bash-write-guard.sh`, T-09/REQ-08) omits the `feature_checkout_guard` call on
the `shared` domain outcome — **empirically confirmed**: a feature-scoped artifact classified
`shared` in `team-config.yaml` can be written straight into the MAIN checkout via `echo hi >
<path>` and exits 0, while the identical write via the `Write` tool correctly exits 2. This
directly contradicts REQ-08's claim ("the same selection the tool route uses, not a second copy
of it") and reopens the exact #1057 loss the feature exists to close, for any project that
declares a feature-scoped `shared:` path (not present in this repo's own `team-config.yaml` today,
so currently latent, but a supported and plausible shape). `must_fix`.

## Bypass table — governed write of a FEAT-50 artifact aimed at the MAIN checkout

| Input shape | Outcome | Deciding line |
|---|---|---|
| Plain absolute path, main checkout, domain `allow` | **DENY (2)**, correct | `check-domain.sh:877` `feature_checkout_guard` called on `allow` |
| Same, domain outcome `shared` (Write tool) | **DENY (2)**, correct — verified live | `check-domain.sh:881` |
| Same, domain outcome `shared` (**Bash** tool, `echo hi >`) | **ALLOW (0) — BUG** | `bash-write-guard.sh:780-787`: guard runs only for `("allow","not_a_domain_question")`, never for `"shared"` |
| `..`/`./`/doubled slashes in the path | Denies/allows exactly as the fully-resolved path implies | `real()` = `os.path.realpath(os.path.abspath(...))` applied symmetrically before both the domain match and the checkout comparison (`harness_boundary.py:242`, `:305`) — no raw traversal text survives into `RE_FEATURE_ARTIFACT` |
| Symlinked worktree, or a symlink planted along the path that resolves cross-checkout | Evaluated at its **true, resolved** landing location — correctly ALLOW/DENY per where it actually lands, never per the syntactic string | same `real()` symmetry; the filesystem's own `open()` and this guard's check necessarily resolve the same symlink the same way |
| Absolute vs relative target | Platform requires absolute `file_path` for Write/Edit/NotebookEdit, so moot on the tool route. On the **Bash** route relative targets are resolved against `root`, not the command's real cwd (`bash-write-guard.sh:~575` `ap = os.path.abspath(os.path.join(root, p))`) — pre-existing, and it fails **closed** (false-positive refusal for a legitimately-landing worktree write), never open, so out of scope here |
| Trailing slash | Normalized away by `abspath`/`realpath`; no effect | n/a |
| Case difference on case-insensitive APFS (e.g. `.HARNESS/...`, `.CLAUDE/worktrees/...`) | `real()` does **not** case-fold (Python's realpath preserves literal casing of non-symlink components) while the OS treats it as the same file. A case-mangled prefix makes `RE_FEATURE_ARTIFACT`/domain-glob matching **case-sensitive**, so it either (a) fails the *domain* match too and is denied for an unrelated reason, or (b) if the mangling sits only on a worktree-nested segment, collapses into the **already-disclosed** sibling-worktree blind spot below — does not produce a new ALLOW beyond what that disclosed gap already covers |
| Unicode NFC/NFD variant of a path segment | Same root cause and same bound as the case-folding row (`real()` normalizes neither); moot in practice — every identifier this system matches on (`FEAT-NN-slug`, `.harness`, `.claude`) is pure ASCII by convention | n/a |
| Percent-encoded traversal (`%2e%2e`) | Inert: filesystem/Python path APIs never URL-decode; creates a literally-named `%2e%2e` entry, not a traversal | n/a |
| Path that normalizes into the worktree only after resolution (a symlink inside the main checkout pointing into the worktree, or vice versa) | Resolves via `real()` before comparison on both sides, so the check and the actual landing location necessarily agree | `harness_boundary.py:checkout_relative`, `:worktree_owner` |
| **Sibling-worktree**: target's rel (computed against `root`/main checkout base) is worktree-prefixed (`.claude/worktrees/<any-id>/.harness/.../notes/x.md`), including a DIFFERENT feature's worktree | `RE_FEATURE_ARTIFACT` only matches a rel beginning `.harness/`; any worktree-nested rel begins `.claude/worktrees/...` and never matches, so `feature_checkout_guard` **never runs** for it | `check-domain.sh:723` `RE_FEATURE_ARTIFACT`; **this is REQ-03's own disclosed residual** ("the extraction the remedy uses reads a path that is worktree-prefixed for any worktree-resident target, so it cannot reach that shape") — reproduced and confirmed correct-as-disclosed via the suite's own `feature-checkout-inside` case, not re-reported as new |
| Prefix boundary: `FEAT-5` vs `FEAT-50`, or a worktree basename that is a superstring of the feature id | Correctly excluded/refused — hyphen-anchored `feature_id.startswith(basename + "-")` and exact-basename-equality only; two prefix-ambiguous candidates raise `AmbiguousWorktree`, caught and **denied (2)** on both routes | `harness_boundary.py: worktree_for_feature`; caught at `check-domain.sh:741-745` and `bash-write-guard.sh:722-723` |

## Fail-open table

| Failure mode | Gate | Behaviour | Deciding line |
|---|---|---|---|
| Any exception inside `feature_checkout_guard`'s own resolution | both guards | Silently absorbed, write **allowed**, **zero stderr** | `check-domain.sh:742-745`, `bash-write-guard.sh:723-726` — matches the established codebase convention for narrowing-check absorption (`_norm`'s `except Exception: pass` at `:1051`, `_root()`'s fallback at `:152`); not a novel inconsistency, info only |
| Feature has no linked worktree at all | both | Deliberately, testably permissive (`if expected is None: return`) — the documented "nothing to bind to" case (SC-03 `feature-checkout-absent`) | `check-domain.sh:733-734` |
| Worktree's own `.git/worktrees/<id>/gitdir` pointer is unreadable/corrupted **mid-run** | both | Silently degrades to the *same* permissive "no worktree registered" state (`linked_worktrees`'s `except Exception: continue`), not a distinguishable "broken registration" refusal | `harness_boundary.py: linked_worktrees` — functionally identical to the intentional case above but the trigger (corruption, not "never registered") is undisclosed; info/low |
| Malformed JSON hook payload | both (pre-existing, unrelated to this diff) | `d = {}` → `target=""` → exits 0 before any gate is reached | `check-domain.sh:161`, `bash-write-guard.sh:79` |
| Digest-clobber prior-content read hits `OSError` (permission error, broken symlink, EISDIR) | check-domain.sh digest guard (NEW, REQ-04) | Treated as `prior=""` → guard condition `if prior.strip()...` is false → **write allowed, clobber proceeds** — reproduces the exact #1058 loss under an unusual I/O precondition rather than "file absent" | `check-domain.sh:1146-1147` |
| Digest-clobber prior-content read: file size | same | Fully read into memory with no bound; self-inflicted DoS at most (attacker needs prior write access to have inflated it) | `check-domain.sh:1144` `.read()` |
| Digest-clobber deny message | same | Never echoes prior or new digest text to stderr/logs — no cross-agent content leakage | `check-domain.sh:1148-1150`, verified by reading |
| git command failing/returning empty | n/a | Not applicable — `harness_boundary.py` deliberately shells no git subprocess on this path (`linked_worktrees`/`worktree_owner` read `.git` files directly) | `harness_boundary.py` module docstring, `:linked_worktrees` |
| Non-UTF-8 file content | digest guard | `errors="replace"` — no crash, degraded comparison only | `check-domain.sh:1144` |

## Ranked findings

1. **[HIGH, must_fix]** `bash-write-guard.sh` omits the checkout-binding check on the `shared`
   domain outcome. Concrete scenario: a project's `team-config.yaml` declares any feature-scoped
   `shared:` path (e.g. `.harness/*/features/*/notes/shared-plan.md` — a realistic shape given
   this repo already has feature-scoped per-agent domains at that same depth). Any governed agent
   writing that path with `echo hi > <main-checkout-path>` lands the write in the main checkout
   and exits 0, silently reproducing #1057; the identical `Write`-tool call is correctly refused.
   Reproduced live (fixture + both hooks fired, transcript available on request). Fix: call
   `feature_checkout_guard(rel, ap)` in the `shared` branch too, mirroring `check-domain.sh:881`.
   `bash-write-guard.sh:780-787`.
2. **[MED]** Digest-clobber guard (REQ-04) treats an `OSError` while reading the prior
   `digest.md` identically to "file does not exist yet," allowing the clobber it exists to
   prevent under a plausible precondition (permission change, broken symlink) rather than only
   the genuinely-new-file case. `check-domain.sh:1146-1147`.
3. **[LOW]** A worktree registration that becomes unreadable mid-run (corrupted `gitdir`
   pointer) silently collapses to the same permissive "unregistered" state as a feature that was
   never given a worktree, rather than a distinguishable refusal — undisclosed trigger for an
   otherwise-intentional permissive state. `harness_boundary.py:linked_worktrees`.
4. **[INFO]** Unbounded read of the prior digest file on every `Write` to a `runs/*/digest.md`
   path; self-inflicted blast radius only. `check-domain.sh:1144`.
5. **[INFO]** `feature_checkout_guard`'s absorbing `except Exception: return` prints nothing —
   consistent with this file's existing convention, not a new inconsistency, but noted because it
   sits on an authorization boundary rather than a cosmetic path helper.

## Confirmed NOT re-litigated (already ruled / disclosed)

- Sibling-worktree checkout-binding blind spot (REQ-03) — reproduced above, matches the BRIEF's
  own disclosure verbatim.
- REQ-04 is `Write`-route-only (Edit/NotebookEdit/`cat >` unenforced) — disclosed in
  `## Verification gaps`; confirmed the digest-clobber code path is reached only from the PRE
  `Write` branch (`check-domain.sh:1418-1426`).
- T-03's domain binding requires a YAML parser (`_run_domain and not _no_parser`) — disclosed.
- REQ-01's `stop_hook_active` passthrough — pre-existing, out of scope, confirmed untouched.
- No secrets, absolute-home-path leakage, or shell/command injection found in the diff:
  `harness_boundary.py`'s new functions shell no subprocess; no new path is interpolated into a
  shell string or an unescaped regex anywhere in the reviewed files.

## Open questions

None blocking.

```yaml
VERDICT: FAIL
DIGEST:
  headline: "bash-write-guard.sh's T-09 checkout binding skips the `shared` domain outcome — a feature-scoped shared path can be written straight into the main checkout via Bash while the Write-tool route correctly refuses it (verified live); REQ-08's route-completeness claim is false for that outcome."
  in_scope: true
  scope_reason: "Dispatch names this diff's write gates and path resolution as the assignment; both files are PreToolUse authorization boundaries."
  severity_max: high
  findings: 5
  must_fix:
    - "bash-write-guard.sh:780-787 — feature_checkout_guard is never called on the `shared` outcome, unlike check-domain.sh:881; a feature-scoped path classified `shared` bypasses the main-checkout refusal via Bash. Reproduced live."
  threat_model:
    - { boundary: "PreToolUse Write/Edit/NotebookEdit -> check-domain.sh checkout binding", stride: T, mitigated: true }
    - { boundary: "PreToolUse Bash -> bash-write-guard.sh checkout binding, allow/not_a_domain_question outcome", stride: T, mitigated: true }
    - { boundary: "PreToolUse Bash -> bash-write-guard.sh checkout binding, shared outcome", stride: T, mitigated: false }
    - { boundary: "digest-clobber prior-content read on OSError", stride: T, mitigated: false }
    - { boundary: "worktree_for_feature prefix/ambiguity resolution", stride: E, mitigated: true }
  open_questions: []
  files_touched: []
  expertise_update: []
artifact: .harness/harness/features/FEAT-50-run-artifact-integrity/notes/review-harness-security-reviewer-feat50-pinned.md
```
