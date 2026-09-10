# Receipt — harness-dev-ops — altitude-eng (invocation & CI surface)

## BLUF

**4 of the 5 scripts already run as wired CI gates today**, at the repo root (non-sparse,
untriggered by path filters) — only `board_lifecycle.py` has no CI wiring, by a prior, still-valid
operator ruling (network cost). The worktree-local invocations of the other four are all **prose**,
not wired: an agent is *instructed* to run them, nothing blocks on the exit code locally. Losing
those prose invocations costs real immediacy for exactly **one** case — `check-state.sh`'s grading
of the **active in-flight feature itself** (the D-12 hazard) — because that feature isn't pushed
continuously and CI never sees it until the first push/PR. Every other immediacy loss is already
absorbed by either the existing CI gate or, for `validate-feature-json.py`, a **separate per-write
hook** that needs no corpus read at all. No source, workflow, or config file was touched; this file
is the only write.

## 1. Invocation inventory

| Script | Surface (`path:line`) | Where it runs in practice | Prose or wired | Gate or advisory |
|---|---|---|---|---|
| `check-state.sh` | `.github/workflows/tests.yml:292-311` (Repository-state gate) | CI root checkout | wired (`bash .../check-state.sh`, exit code captured) | **GATE** — required check `integration` |
| | `.claude/commands/harness.md:12` | wherever `/harness` is invoked — in practice the active feature's worktree, mid-build | **prose** ("Run `check-state.sh`. Violations are surfaced...") | advisory — agent may or may not run it, nothing blocks |
| | `check-state.sh:2519` `import layout_migration as _lmod` | in-process, inside whichever of the two rows above is executing | wired | folds into check-state.sh's own exit code (INV-27) |
| `board_lifecycle.py` | `.claude/skills/harness-add-repo/SKILL.md:113,137` (`provision`, `audit`) | onboarding flow, not tied to a feature worktree — control-plane root [INFERENCE, no grep-provable cwd] | **prose** ("read the exit code") | advisory — agent reads the exit code manually |
| | *(no CI, no hook — see below)* | — | — | — |
| `check-plan-routes.py` | `.github/workflows/tests.yml:148-198` (Plan-route gate) | CI root checkout | wired (subprocess, summary-line parsed, `exit "$rc"`) | **GATE** — required check `integration` |
| | `.claude/skills/harness-spec-driven/SKILL.md:91` | plan-signing time, inside the feature's own worktree [INFERENCE per feature-tree convention] | **prose** ("run ... and fix every violation") | advisory |
| `validate-feature-json.py` | `.github/workflows/tests.yml:94-101` (Validate feature execution state) | CI root checkout, sweeps every `feature.{json,yaml,yml}` on disk | wired (no args) | **GATE** — required check `integration` |
| | `.agents/skills/harness/bin/feature_schema.py:5-8` — imported **in-process by `check-domain.sh`**, one of the nine registered hooks (contract fact 1) | wherever the write happens — the feature's own worktree, at write time | wired | **GATE** — but this is `check-domain.sh` validating the single file just written, not `validate-feature-json.py`'s CLI; note the distinction, don't conflate the two |
| `layout_migration.py` | `.github/workflows/tests.yml:226-273` (Layout gate) | CI root checkout | wired (`python3 .../layout_migration.py .`) | **GATE** — required check `integration` |
| | `check-state.sh:2519,2519-2542` (in-process import, INV-27) | wherever check-state.sh runs (both rows above) | wired | folds into check-state.sh's exit code |

None of the five appear in any of the nine `.claude/settings.json` hook registrations — confirmed by
re-grep against `.claude/skills/harness/hooks` and `.agents/skills/harness/hooks`, zero hits (matches
contract fact 2). `board_lifecycle.py` is explicitly excluded from `check-state.sh` by name:
`harness-add-repo/SKILL.md:147-150`, "this check runs ONCE, here, and never in `check-state.sh`...a
network call there would fire dozens of times per build" — a prior operator ruling, still live, not
mine to relitigate.

## 2. Does CI have a complete record by construction? — **holds**

- Checkout: `.github/workflows/tests.yml:50` — bare `uses: actions/checkout@v4`, no `with:` block
  anywhere in the file. Default fetch-depth (shallow, depth 1) but **no `sparse-checkout` step exists
  anywhere in this workflow** — the working tree at that commit is materialized in full. Shallow
  history is irrelevant here: none of the five scripts read `git log`, all read files off disk.
- Triggers: `tests.yml:19-22` — `push: branches:[main]` + `pull_request` (every base branch), **no
  `paths:`/`paths-ignore:` filter present anywhere in the file** — a record-only change (a
  `feature.json` or `plan.yaml` edit with no code) triggers the job exactly like a code change.
- The workflow's own comments independently corroborate this: `tests.yml:135-143` measured (at
  1c95e81, post-move) `git ls-files '.harness/harness/features/*/PLAN.md' ...'` returns 20 and
  `git check-ignore -v .harness/harness/features` exits 1 — the corpus is tracked and un-ignored, so
  checkout cannot produce a zero-file view.
- **Caveat, and it is the one that matters**: CI's completeness is a property of *pushed* commits.
  Convention in this project keeps a feature's worktree (`.claude/worktrees/**`) local until it
  ships; nothing pushes it continuously. CI's complete-record guarantee therefore never covers the
  in-flight feature **for the duration of its own build** — this is the D-12 hazard restated in CI
  terms, not a new finding.

## 3. Pricing: CI placement vs. root-checkout placement

**CI — only `board_lifecycle.py` is a new addition; the other four are sunk cost, already paid on
every push/PR.**

| Script | New CI cost |
|---|---|
| `check-state.sh`, `check-plan-routes.py`, `validate-feature-json.py`, `layout_migration.py` | **zero** — already steps in the single `integration` job (`tests.yml:83-311`), same job as the required branch-protection context. No new job, no new step. |
| `board_lifecycle.py` | Real: needs `gh` against GitHub's Projects v2 API with credentials — `tests.yml:57-66` states this workflow carries **no `secrets.*`** by design (DEC-201), the same reason the `locally_run` test-kind status exists in `harness.json:297-317` for host-only probes. Adding it means wiring a new secret plus a new step (or accepting the SKILL.md-documented per-build network multiplication the operator already rejected at `harness-add-repo/SKILL.md:147-150`). Not a "just add a step" cost. |

**Root checkout — candidate enforcement instruments, rated on what actually sticks in this repo:**

| Instrument | Enforcing or advisory | Reason |
|---|---|---|
| Self-refusal inside the script when it detects a linked worktree | would be enforcing **if built** | not implemented today — grepped all five for worktree-linked self-detection logic (`check-state.sh` has INV-25/29, but those flag *stray* worktrees outside `.claude/worktrees/**`, never "I am running from inside one, refuse"). Building this is new logic, out of scope for me to spec. |
| Wrapper/launcher | n/a | none of the five have one today |
| `verify:` clause on a task | enforcing, but narrow | only runs when that one task's verify runs — never a standing, ongoing corpus-drift catch |
| CI job | **enforcing** | the one proven mechanism here — branch protection requires exactly the `integration` context (`tests.yml:110-116`), and 4/5 scripts are already inside it |
| Agent-facing prose (`.claude/commands/harness.md:12`, `harness-spec-driven/SKILL.md:91`) | **advisory** | exactly what runs today for the worktree-local half; nothing blocks if skipped |
| Git hook via `core.hooksPath` | **enforcing, but locally bypassable** | precedented — `post-merge` (`.claude/skills/harness/hooks/post-merge`) already ships this way, and its registration is itself gated by `check-state.sh` INV-31 so an unconfigured `core.hooksPath` is caught. A new `pre-push` hook running these scripts at root before push would restore local immediacy without touching the worktree, but `git push --no-verify` bypasses it — weaker than CI, stronger than prose. |

## 4. Immediacy ruling, per script

| Script | Detected today | Delay under CI-only | Acceptable? | Gap-filler |
|---|---|---|---|---|
| `check-state.sh` | At every `/harness` door entry, inside the worktree (fastest possible) + CI on push/PR | Next push/PR — for an in-flight feature that can be the **entire build duration** (worktree stays local until ship) | **UNACCEPTABLE** for the active feature's own checkpoint/budget invariants — this is exactly why D-12 exists | Keep D-12's caller-side union (grade the active feature locally), or add the `pre-push` hook above so the full script still runs at root before the feature is ever pushed. Reintroducing the corpus into the worktree is not the cheaper option here — a pre-push hook is. |
| `board_lifecycle.py` | Only on manual `provision`/`audit` during onboarding — already the slowest of the five, accepted as such (`SKILL.md:147-150`) | No change — it isn't gated today either way | **ACCEPTABLE**, no regression | none needed |
| `check-plan-routes.py` | At plan-signing (prose, worktree) + CI on push/PR (required check, already blocks merge) | Delay = time between drafting and first push, typically short; a malformed plan can still be worked on locally in the meantime | **ACCEPTABLE** — the CI required check is the correctness backstop; the SKILL.md prose only saves rework, it was never load-bearing | none needed |
| `validate-feature-json.py` | Per-write, immediately, via `check-domain.sh`'s in-process import of `feature_schema.py` — a **registered hook**, not one of the corpus sweeps, and needs no cross-feature read at all + CI sweep on push/PR as backstop | CI sweep delay only affects edits made *outside* the guarded tool path | **ACCEPTABLE** — the real-time enforcement here was never the sweep script, it is the per-write hook, which is untouched by this whole question | none needed |
| `layout_migration.py` | Via `check-state.sh`'s in-process import at every `/harness` door (worktree) + CI Layout gate on push/PR | Next push/PR | **ACCEPTABLE** — a half-migrated layout surface is, by the module's own remedy text (`check-state.sh:2541-2542`), meant to be "finished or reverted inside one atomic commit" — there is no mid-session local action this feedback enables that push-time feedback doesn't equally enable | none needed |

**Net:** only `check-state.sh`'s active-feature grading needs a genuine local answer. Everything else
already has adequate coverage from the existing `integration` CI job or, for `validate-feature-json.py`,
a hook that was never part of the corpus-sweep problem in the first place.

## Non-goals honored

No workflow, settings.json, source, test, plan.yaml, or BRIEF.md edited. No worktree created or
removed. No project-wide suite or linter run. This receipt is the only file written.
