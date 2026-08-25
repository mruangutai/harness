# Security review — FEAT-34 Act 3 (worktree lifecycle enforcement)

Pin: `513c4a46e34cbe327d96922c01cebdd18e85d62e`. Diff base `9165162be80e6b39055cff6b989227ce1b875172`.
All content read via `git show 513c4a4:<path>`, never the working tree.

## Verdict: PASS, no findings that gate

The named surfaces (git-hook RCE, shell injection, destructive filesystem action, `gh` subprocess
use, log/output data exposure) were each checked against the pinned content. All subprocess
construction in the scoped files uses list-form argv with no `shell=True` on any attacker- or
config-derived value, no `eval`, no `os.system`. The destructive path (worktree removal) has a
tested self-exclusion guard with both a green and a red proof, and the actual deletion re-verifies
dirtiness/landed-artifact state independently at execution time (`feature-worktree.py remove`,
unchanged by this diff), so the sweep's own snapshot is advisory, not authoritative — no TOCTOU.

## Per-surface findings

**1. Arbitrary code execution via the git hook — assessed, not a new finding.**
`core.hooksPath` (set by `harness-init/SKILL.md`'s per-clone step, prose not scoped-in code) makes
`.claude/skills/harness/hooks/post-merge` (36 lines, pure `$0`-derived path resolution, no logic)
exec `post-merge-sweep.sh` on every `git merge`/`pull` — including ones a human runs directly in a
terminal, outside Claude's own tool-permission gating. This is a genuinely new *automatic-trigger*
surface (previously, harness scripts in this same `bin/` tree only ran when Claude's own
PreToolUse/PostToolUse hooks fired via `settings.snippet.json`, i.e. mediated by an agent's Bash
call). The content itself is repo-tracked and reviewed at the same trust level as every other
script already wired into those Claude hooks, so this does not create a *new* population of
attackers — anyone who can merge malicious code to the default branch already controls
`check-state.sh`, `merge-settings.py`, etc. — but it does mean that code now runs unconditionally,
without even Claude's tool-permission prompt as a speed bump, for every clone with `core.hooksPath`
set. `D-08`'s signed decision names "core.hooksPath takes over hook resolution for the WHOLE
clone" as an accepted cost, but that clause is about *other hooks stopping*, not about this new
unconditional-execution property. Recording as **info**, assessed-and-dismissed: same trust
population as pre-existing hook-wired scripts, no privilege escalation, but flag for a human
signer to confirm the "no Claude-mediation" property was in view when D-08 was signed — it reads
like it wasn't stated in those terms.

**2. Shell injection / word-splitting — none found.**
`post-merge-sweep.sh`'s heredoc passes exactly two values through the shell layer
(`POST_MERGE_SWEEP_BIN_DIR`, `POST_MERGE_SWEEP_DRY_RUN`, both script-derived, not attacker input);
everything downstream is Python `subprocess.run([...])` list-argv (`git worktree list`,
`git config`, `gh-sync.py ship`, `feature-worktree.py remove`, `gh api`). `check-state.sh`'s
INV-29/INV-30 additions are the same embedded-Python-heredoc style as the rest of the file, with no
new shell string construction. `test-hooks-install.py` uses `shell=True` (lines ~1247–1265 of the
full diff) but only against three hardcoded constant command strings lifted verbatim from
`harness-init/SKILL.md` — never against fixture- or attacker-derived data. Feature ids and repo
segments used to build `feature-worktree.py remove --repo/--id` guidance strings are always drawn
from real, existing `git worktree list` paths or from `git ls-tree` names of the landed default
branch (git disallows `.`/`..` tree entries), so there is no path-traversal vector into the
constructed `feat_dir` (`worktree_terminal.classify`, `post-merge-sweep.sh:_handle_record`).

**3. Destructive filesystem action — bounded, tested, fails toward inaction.**
Removal only happens after (a) `gh-sync.py ship` exits 0 with no `"gh-sync: SKIP"` in its combined
output (the positive-signal gate), and (b) `feature-worktree.py remove` independently re-checks a
clean tree and every landed artifact present — unchanged by this diff, so its own refusal logic
was not re-audited here but its behavior is exercised by the fixtures. Self-exclusion
(`cwd_real == path_real or startswith`) prevents the sweep from deleting the worktree it is
currently running inside, and `test-post-merge-sweep.py::case_self_exclusion` proves both the
guarded and unguarded (red-proof, deletes itself) behavior. `D-11`'s harness-checkout-only scoping
rests on a checkable architectural fact (served repos never carry the `.claude/skills/harness/`
bin tree — consistent with `docs/PRINCIPLES.md`'s "not a framework installed into repositories"),
not merely asserted.

**4. `gh` subprocess use (INV-30) — no token exposure, no SSRF.**
`gh api --paginate repos/%s/milestones?state=open...` — `%s` is `github.repo` from
`.harness/harness.json` (operator config, not remote-attacker-controlled), never from a landed
`feature.json`'s fields. `gh auth status`'s output is never printed (only `.returncode` is used).
`INV-30`'s offline-silent posture is explicitly excepted by the dispatch (matches INV-26's
precedent at `check-state.sh:1205`) — not re-filed.

**5. Data exposure in logs/output — none new.**
`post-merge-sweep.sh` echoes `gh-sync.py ship`'s stdout/stderr verbatim into the hook's own output
(visible after a `git pull`), but `gh-sync.py cmd_ship` (unchanged by this diff) only ever prints
milestone/PR/parent-issue numbers and status strings — no credentials, no verbose `gh` internals.
Grepped the full 41-file diff for secret-shaped strings (`ghp_`, `github_pat`, `-----BEGIN`,
`password`, etc.) — zero hits outside comments discussing the concept.

## Threat model

| Boundary | STRIDE | Mitigated |
|---|---|---|
| `git merge`/`pull` triggers tracked-repo code via `core.hooksPath`, unconditionally, outside Claude's tool-permission gating | Elevation of privilege (new unconditional trigger, same trust population) | assessed, not newly introduced privilege — info only |
| Sweep target-path derivation (worktree removal) | Tampering / DoS (wrong-directory deletion) | yes — self-exclusion tested, argv list-form, ids bounded to real git-reported names |
| `gh-sync ship` fail-open before removal | Repudiation (removal without recorded terminal status) | yes — positive-signal gate (D-04) requires exit 0 AND absence of the SKIP string |
| INV-29/INV-30 import or lookup failure | Tampering (gate silently stops refusing) | yes for INV-29 (import/exception failures are `bad.append`ed, blocking); INV-30 offline-silent is a signed, cited exception (not re-filed) |
| `gh api` milestone list construction | Injection / SSRF | yes — repo string is operator config, list-argv, no shell |

## Not re-derived / out of scope

`harness-init/SKILL.md`'s per-clone `core.hooksPath` install step is prose an agent executes
manually — no code to statically audit for injection; its "STOP and ask before overwriting a
foreign hooksPath" instruction is well-formed but its actual enforcement depends on agent
compliance, which this static review cannot verify. `test-hooks-install.py` is the automated proof
for the two literal command strings only (by the file's own docstring) and was read to confirm it
does not shell out on untrusted data — it doesn't.

```yaml
VERDICT: PASS
DIGEST:
  headline: "No exploitable defect in the named surfaces; all subprocess construction is list-argv, destructive removal is guarded and tested, gh/token handling introduces no new exposure."
  in_scope: true
  scope_reason: "Feature adds a git post-merge hook (native code execution on merge), a worktree-deleting sweep, and two check-state.sh invariants with gh subprocess calls — a real trust-boundary surface, not process record."
  severity_max: info
  findings: 1
  must_fix: []
  threat_model:
    - { boundary: "git merge/pull triggers tracked-repo code via core.hooksPath, unconditionally, outside Claude's tool-permission gating", stride: "E", mitigated: false }
    - { boundary: "sweep worktree-removal target path derivation", stride: "T", mitigated: true }
    - { boundary: "gh-sync ship fail-open before removal (positive-signal gate, D-04)", stride: "R", mitigated: true }
    - { boundary: "INV-29/INV-30 import or lookup failure", stride: "T", mitigated: true }
    - { boundary: "gh api milestone list construction (INV-30)", stride: "I", mitigated: true }
  open_questions:
    - { id: Q1, question: "D-08's signed cost names 'core.hooksPath takes over hook resolution for the whole clone' (other hooks stop firing) — was the separate property that post-merge code now runs unconditionally on every merge/pull, without Claude's own tool-permission gating as a speed bump, explicitly in view when that was signed? If not, worth a one-line addendum, not a blocker.", blocking: false }
  files_touched: []
  expertise_update: []
artifact: .harness/harness/features/FEAT-34-worktree-act3-enforced/notes/review-harness-security-reviewer-c0.md
```
