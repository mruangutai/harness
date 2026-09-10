# Receipt — harness-dev-ops (arch2-eng) — FEAT-58-corpus-outside-worktree

Conclusions: the M-2 shim pattern is confirmed and specifiable without new invention; the DEC-174
lane split puts every `bin/*.py`/`bin/*.sh` candidate in **both** backend-dev's and dev-ops's
domain (a real serialization requirement for the plan), while the hooks directory, `.gitignore`
and `.claude/commands/**` are `main-session-direct`; D-5's evidence in this repo is the existing
`.github/workflows/tests.yml` run against a plain clone, with `.harness/corpus` currently ABSENT
from `.gitignore` (a real addition the plan must make), not a pre-existing gitignore entry.

## A — the hook wiring (M-2)

**`core.hooksPath` resolution.** `git config --get core.hooksPath` in this worktree returns
`.claude/skills/harness/hooks`; `--show-origin` names `.git/config` — the **shared, repo-local**
config file, not this linked worktree's own. Confirmed the resolution is inherited, not
worktree-local: `extensions.worktreeConfig` is unset and `.git/worktrees/FEAT-58-corpus-outside-worktree/`
holds no `config` file, so every linked worktree reads the one shared `.git/config`. A new hook
enabled here is enabled for every worktree simultaneously — there is no per-worktree opt-out.

**The shim.** `post-merge:20-36` delegates: it resolves `$0`'s directory (`pwd -P`, so a symlinked
checkout resolves real), walks four levels up to the repo root, builds
`$_root/.claude/skills/harness/bin/post-merge-sweep.sh`, and `exec`s it with `"$@"` unchanged
(`post-merge:36`). Missing/non-executable delegate: prints one line and `exit 0` (`post-merge:29-32`)
— never non-zero, because a post-merge hook returning non-zero reads as a broken pull
(`post-merge:25-28`). `bin/post-merge-sweep.sh` exists, mode `-rwxr-xr-x` (confirmed via `ls -la`).

**Shim pattern as a specification**, for `post-checkout` and `post-rewrite` to follow:
1. `#!/bin/sh` (POSIX, not bash — matches `post-merge:1`).
2. Root resolution from `$0`, never cwd: `_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd -P)`,
   then a fixed number of `..` hops matching the shim's own depth under the repo root.
3. Delegate path built by string concatenation onto the resolved root, one delegate per shim.
4. Missing/non-executable delegate → one diagnostic line to stdout, `exit 0` — never abort the
   git operation the hook rides on.
5. `exec "$delegate" "$@"` — full positional-argument passthrough, no reinterpretation.

**Argument shapes**, confirmed against `git help hooks` run in this worktree (`/tmp/f58-do-hooks.txt`,
this machine's installed git doc, not memory):
- `post-checkout` (`/tmp/f58-do-hooks.txt:167-184`): three positional args — previous-HEAD ref,
  new-HEAD ref, branch-vs-file flag (1/0). On `git worktree add` (no `--no-checkout`): first arg is
  the all-zero ref, flag is always 1 (`:177-180`). The shim forwards all three unmodified — the
  body script is what needs to distinguish flag=1 from flag=0, not the shim.
- `post-rewrite` (`/tmp/f58-do-hooks.txt:497-512`): ONE positional arg, the command name
  (`amend`|`rebase`); the rewritten-commit list `<old-oid> SP <new-oid> [SP extra-info] LF` arrives
  on **stdin**, not argv. The shim's `"$@"` passthrough covers the arg; stdin needs NO shim
  handling at all — `exec` preserves the calling process's stdin automatically, so the existing
  four-line pattern is already sufficient for `post-rewrite` with zero additions.

**Probe — post-checkout fires on worktree creation, reproduced independently** (not the note's
claim taken on faith): synthetic `git init` repo under `/tmp/f58-do-WLn3` (removed after), a
printing `post-checkout` installed at `.git/hooks/post-checkout`, then
`git worktree add --detach <tmp>/wt1 main`. Observed:
`cwd=/private/tmp/f58-do-WLn3/wt1 args=0000000000000000000000000000000000000000 bd74c287… 1`
— matches the note's line exactly and matches the doc's stated shape (null-ref, new-ref, flag=1).
Worktree and tmp dir removed from outside afterward (`git worktree remove --force` run from the
repo, not from inside `wt1`); `rm -rf "$TMP"`.

**One body vs three.** Rule: **three separate delegates, one shared shim pattern** — not one body
script for all three hooks. Deletion test: `post-checkout`'s useful work (repair the new tree) and
`post-rewrite`'s useful work (restore state after a rebase already in place) both reduce to the
same idempotent `worktree-state.py --repair` call M-1 already defines (see DoD lines 105-115) — so
a "shared body" would be a single-line pass-through with no branching logic of its own; the
interface (three shim files, one delegate call each) is already smaller than a fourth dispatch
layer would be. Keep three thin shims each `exec`-ing the SAME `worktree-state.py --repair`
command directly (no separate three `*-sweep.sh` bodies needed for the new two — `post-merge`'s
sweep is a distinct, pre-existing concern from FEAT-34 and stays its own body).

**Shim-integrity test — found and cited.** `tests/integration/test-hooks-install.py`:
- `case_sc08_before_and_after` (`:286-310`) asserts existence + exec bit only: `core.hooksPath`
  resolves to the tracked dir (`:303-305`) and `post-merge` there `os.path.isfile(...) and
  os.access(..., os.X_OK)` (`:306-309`). This is necessary but NOT the missing-delegate case.
- The actual "shim pointing at a missing file cannot pass" proof is the SC-14 RED-PROOF branch of
  `_run_merge_and_check` (`:397-447`), invoked at `:502` with a shim repointed at a nonexistent
  sweep: it asserts the shim's own diagnostic text `"missing or not executable"` appears in
  combined output (`:441-443`) AND, decisively, that the **effect never happens** — the worktree
  `os.path.isdir(dest)` is still True, i.e. survives the merge (`:444-446`). That second assertion
  is what makes it a real discriminator rather than a string-match on stdout.
- **What the extended assertion must add** for `post-checkout`/`post-rewrite`: the identical
  two-part pattern (diagnostic string present + observable effect absent) run against a fixture
  where EACH new shim's own delegate is repointed at a missing path — e.g. for `post-checkout`,
  assert a freshly `git worktree add`-ed tree keeps its pre-repair broken cone/skip-bits (the
  effect `worktree-state.py --repair` would have fixed) rather than merely checking the shim file's
  own exit code, mirroring `:441-446` exactly.

## B — DEC-174 lane split

`check-domain.sh --resolve <path>` exists and prints one agent name per line, or the literal
`NOBODY`, exit 0 either way (confirmed: ran `--resolve` on a real path first before trusting the
flag). Resolutions actually run in this worktree, then lane:

| Path | Resolution (verbatim) | Lane |
|---|---|---|
| `.claude/skills/harness/hooks` | `NOBODY` | `main-session-direct` |
| `.claude/skills/harness/hooks/post-merge` | `NOBODY` | `main-session-direct` |
| `.claude/skills/harness/hooks/post-checkout` (new) | `NOBODY` | `main-session-direct` |
| `.claude/skills/harness/hooks/post-rewrite` (new) | `NOBODY` | `main-session-direct` |
| `.claude/skills/harness/bin/post-merge-sweep.sh` | `harness-backend-dev`, `harness-dev-ops` | team lane, BOTH |
| `.claude/skills/harness/bin/worktree-state.py` (proposed) | `harness-backend-dev`, `harness-dev-ops` | team lane, BOTH |
| `.claude/skills/harness/bin/check-state.sh` | `harness-backend-dev`, `harness-dev-ops` | team lane, BOTH |
| `.claude/skills/harness/bin/merge-gate.py` | `harness-backend-dev`, `harness-dev-ops` | team lane, BOTH |
| `.claude/skills/harness/bin/feature-worktree.py` | `harness-backend-dev`, `harness-dev-ops` | team lane, BOTH |
| `.claude/skills/harness/bin/check-domain.sh` | `harness-backend-dev`, `harness-dev-ops` | team lane, BOTH |
| `.gitignore` | `NOBODY` | `main-session-direct` |
| `tests/integration/test-hooks-install.py` | `harness-backend-dev`, `harness-dev-ops`, `harness-qa` | team lane, THREE-way |
| `tests/integration/test-post-merge-sweep.py` | `harness-backend-dev`, `harness-dev-ops`, `harness-qa` | team lane, THREE-way |
| `.github/workflows/tests.yml` | `harness-dev-ops` (sole) | team lane, dev-ops |
| `.github/CODEOWNERS` | `harness-dev-ops` (sole) | team lane, dev-ops |
| `.claude/settings.json` | `NOBODY` | `main-session-direct` (confirms DEC-174's own framing; not touched by this feature otherwise) |
| `.claude/commands/**` | not re-run — already ruled per dispatch | `main-session-direct` |

**Every `bin/*.py`/`bin/*.sh` candidate — including the still-to-be-written `worktree-state.py` —
resolves to BOTH `harness-backend-dev` and `harness-dev-ops`.** Per the division of labour in this
run (BackendArch owns the command's internals; DevOpsArch owns wiring), this is a genuine
serialization requirement for the plan, not a routing ambiguity: two agents hold write grants on
the same file, so the plan must sequence their tasks on it (one lands, the other's task starts from
that commit) rather than dispatch them concurrently — a concurrent pair would collide on the same
path under the domain guard's own terms. The two test files add `harness-qa` as a third co-owner,
so any task touching `test-hooks-install.py`/`test-post-merge-sweep.py` needs the same
serialization against QA's task, not just backend/dev-ops.

## C — D-5, fresh clone and CI unchanged

**What differs a fresh clone from a worktree, and what would need inspection/change:** nothing in
`git clone` itself replicates prior worktrees — replication is exclusively a property of
`.claude/skills/harness/bin/feature-worktree.py`'s sparse-checkout setup plus (per M-2) the
proposed hook repair running on worktree creation. A fresh clone never runs `git worktree add`
against itself, so the corpus-replication mechanism this feature targets is never invoked by clone
alone; nothing needs inspection there beyond confirming the new hooks are inert (exit 0, no-op)
outside a worktree context, which `worktree-state.py --verify`'s own scope (not this receipt's —
BackendArch's) would need to guarantee.

**`.harness/corpus` gitignore state — a CHANGE, not already true.** `.gitignore` in this worktree
is 46 lines; grepped in full for `corpus` and for a bare `.harness/` prefix — six existing
`.harness/**` entries (`:7,13,29,34,40,46`), none matching `corpus`. The symlink path the DoD
proposes is **not yet gitignored**; the plan must add a new `.gitignore` line for it (D-1's positive
control in the DoD's test matrix already requires this — the symlink read costs "no materialised
bytes" AND `git status --porcelain` empty, which fails today with no entry present).

**CI surface.** One workflow under `.github/`: `.github/workflows/tests.yml` (the only file under
`.github/workflows/`), plus `.github/CODEOWNERS` (not a workflow, no CI behaviour). A CI runner
checks out via `actions/checkout` — a fresh, non-worktree clone by construction — so it would
observe a difference ONLY if the new hooks or `.gitignore` change altered behaviour for a plain
clone (e.g. a hook shim that assumed worktree-specific state and errored non-zero outside one).
The M-2 shim pattern above (exit 0 on any not-applicable condition) is what keeps that surface
unchanged; this is a property the plan should trace to a concrete assertion in
`tests.yml`-equivalent CI conditions, but the workflow file's own content was not altered by this
segment and was not re-read line-by-line beyond confirming its sole existence.

**Strongest D-5 evidence, in this repo's terms:** the DoD's own instruction — the existing suite,
run in a plain (non-worktree) clone, untouched by this change. Concrete entry point a plan would
cite: `.github/workflows/tests.yml` is the CI-facing entry; the local-equivalent runner referenced
elsewhere in this repo's Expertise is `run-unit-tests.sh` (project-tier dev-ops Expertise, G-10),
which is the suite entry point a D-5 task would name — NOT run here, per the dispatch's
project-wide-suite prohibition.

## Revert proof

No production file was edited or probed in place; all git/hook probing ran against synthetic
repos under `/tmp/f58-do-*`, each removed after use (`rm -rf`, worktree removed from outside via
`git worktree remove --force`). `git -C <worktree> status --porcelain` after this receipt write:

```
 M .harness/harness/features/FEAT-58-corpus-outside-worktree/STATE.md
 M .harness/harness/features/FEAT-58-corpus-outside-worktree/feature.json
?? .harness/notes/dod-worktree-corpus-2026-09-10.md
?? .harness/harness/features/FEAT-58-corpus-outside-worktree/notes/receipt-harness-dev-ops-arch2-eng.md
```

The three non-receipt entries predate this dispatch (STATE.md/feature.json modified, the DoD note
untracked) — none touched by this segment; only the fourth line is this receipt.

## Open questions

- Q1: Whether the plan should also gitignore `.harness/corpus` in the SAME task that lands the
  symlink-creation logic, or as a separate `.gitignore`-only `main-session-direct` step ahead of
  it — a sequencing choice, not something this segment can decide alone since `.gitignore` is
  `main-session-direct` and the symlink creator is BackendArch's/DevOpsArch's team-lane work.
  (blocking: false)
- Q2: Whether `.github/workflows/tests.yml`'s content needs a new assertion for D-5 or is fully
  covered by the existing suite running unmodified — this receipt did not open the workflow file's
  body (out of the "do not run/inspect deeply, just name it" instruction) and cannot rule on its
  content. (blocking: false)
