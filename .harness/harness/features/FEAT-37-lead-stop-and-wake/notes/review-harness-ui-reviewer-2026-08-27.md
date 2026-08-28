# UI review — FEAT-37 scope check at pinned sha (review_sha `4e652f9`)

**Verdict: scoped out, PASS.** No design-authored, rendered UI surface exists in the diff measured
by the exact command the dispatch specified. This is a measured decline, not a predicted one.

## The census I ran

Worktree: `.claude/worktrees/harness/FEAT-37-lead-stop-and-wake` (HEAD `50863b6`, not moved).
All reads via `git show`/`git diff` against the pinned commit objects.

```
git diff --stat 8fc87f8..4e652f9      # exactly as the dispatch specified
```

**This range is 141 files changed (11452 insertions, 982 deletions), spanning ~34 commits** — the
full FEAT-37 replan-and-rebuild plus FEAT-42's plan/build/validate history, not the 9-file set the
dispatch narrates (SKILL.md, `inflight_registry.py`, a shell test runner, two test files, three docs,
one backlog note). I can locate that 9-file set as a plausible subset —
`.claude/skills/harness-team/SKILL.md`, `inflight_registry.py`, `run-unit-tests.sh`,
`test-inflight-registry.py` (+ one more test file), `DECISIONS-INDEX.md` + `DECISIONS.md` + `SPEC.md`,
and `.harness/notes/backlog-orchestrator-inoculation-2026-08-27.md` — but the literal command given
does not isolate it. **Flagging the mismatch below as a non-blocking open question**; it does not
change my finding either way (see next section).

**Extension census on the full measured 141-file diff** (html/css/scss/sass/less/tsx/jsx/vue/svelte):

```
git diff --name-only 8fc87f8..4e652f9 | grep -Ei '\.(html|css|scss|sass|less|tsx|jsx|vue|svelte)$'
```

6 hits, all `notes/ship-review-*.html`:
- `FEAT-37.../notes/ship-review-2026-08-26-02-product.html`
- `FEAT-37.../notes/ship-review-2026-08-27-01.html`
- `FEAT-42.../notes/ship-review-2026-08-26-2-plan-product.html`
- `FEAT-42.../notes/ship-review-2026-08-26-3-plan-product.html`
- `FEAT-42.../notes/ship-review-2026-08-27-plan.html`
- `FEAT-42.../notes/ship-review-2026-08-27-validate.html`

Each is a rendered document with real theming CSS (custom properties, `prefers-color-scheme` +
`data-theme` override, a type/spacing scale via `clamp()`) — on its face, a UI surface this role
would normally audit.

**But it is not new design work in this diff.** Each `.html` is a 1:1 sibling of a `.md` file also
in the diff, and both are produced by `.claude/skills/harness/bin/render-brief.py`, which is
**unchanged** in this range (`git diff --stat 8fc87f8..4e652f9 -- .../render-brief.py` returns
nothing; the file exists byte-for-byte the same at `8fc87f8`). The script's own docstring: *"DERIVED,
NEVER AUTHORED... Zero judgment, so it needs no owner and no freshness policy... The law (DEC-141):
no agent writes HTML, ever."* No one made a design decision in this diff — the same fixed,
already-shipped template was mechanically re-run over new markdown content. There is no
`DESIGN.md` and no `notes/prototypes/` anywhere for FEAT-37 or FEAT-42 to hold such a decision
against even if there were one:

```
git ls-tree -r --name-only 4e652f9 | grep -i 'DESIGN.md'   # FEAT-10, FEAT-11, FEAT-19, FEAT-40 only
git ls-tree -r --name-only 4e652f9 | grep -i 'prototypes/' # no hits anywhere
```

No other extension in the census category appears anywhere in the 141-file diff.

## The one judgement I could have taken, and am declining

`.claude/skills/harness-team/SKILL.md` is read by an agent, not a human — it shapes lead-tier
conduct, not a rendered page. Conventional readability/accessibility review (contrast, spacing,
states, focus) has no object to apply to here. I am declining this explicitly rather than
straddling: "is this instruction text unambiguous to its reader" is a prompt-quality lens, and it
belongs with the code reviewer (or the eval/UAT criterion DEC-70 already routes `ai_behavior`
changes through), not with UI review.

## What this does NOT resolve

- I did not re-derive whether the 9-file description matches some other, narrower diff the
  dispatcher had in mind — the file names given are plausible members of the 141-file set but the
  literal command does not select them. Recorded as an open question, non-blocking: it does not
  change the verdict, since none of the plausible 9 files carry a rendered-UI extension either.
- I have not rendered the `ship-review-*.html` files; source-level inspection only. If a human ever
  needs to judge their actual visual/contrast output, that is outside what a source-level audit can
  confirm — noted for completeness, not because it is live in this diff (the template did not change).
