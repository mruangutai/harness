# Receipt — T-14 cycle 2 — finish the DEC-113 strike to SC-08

**DEC-113 is now nothing but its override-precedence ruling: one title, one provenance anchor, one
paragraph, no subheadings.** The two blocks cycle 1 scoped out (`### What the fixture caught that
reading did not`, `### Safety properties, and why each exists`) are deleted, along with the
`/harness-deploy` claim and the pre-rewrite live-risk measurement. Verify exits 0 (`STRUCK`),
generator clean with no ORPHAN, `run-unit-tests.sh` exit 0 with `PASS test-gen-decisions-index.py`.
Nothing committed, staged or pushed.

**Scope note for a later goal-check: SC-08 governs, and it is wider than T-14's `intent:` in
`plan.yaml`.** The intent named only the title, ruling 2's justification, and rulings 1 and 3;
SC-08 requires DEC-113 to retain *only* its override-precedence ruling. The operator accepted that
divergence explicitly in the cycle-2 dispatch. This is approved-but-unmet, not a plan change — no
re-signature, pm not involved.

## The survivor — line range and the map

`docs/harness/DECISIONS.md` **1964-1972**, followed by the `---` at 1974.

| Element | Lines | One line |
|---|---|---|
| `## DEC-113 — Team and crew overrides live outside the tool tree, and are resolved first` | 1964 | title, unchanged from c1 |
| Body, one paragraph | 1966-1972 | `Task 13.` provenance + the override-precedence ruling and its justification |

**Subsections remaining: none.** After the fold there is no `###` under the `##` at all. That is the
honest map, not an omission.

### The presence half — the surviving precedence sentence, verbatim

> The precedence rule BUILD asked for ("project-local overrides global") only holds if the
> override sits there. Recorded in both manifests as `paths.crew_overrides`; the runner (task 10)
> resolves it first.

`.claude/skills/harness-team/SKILL.md:37` and `.claude/skills/harness/templates/team-config.yaml:47`
both cite DEC-113 for exactly this rule, and both still land on text that states it.

## The two calls that were mine

1. **`Task 13.` kept, folded onto the ruling's opening line.** Siblings carry a provenance anchor
   (`DEC-112` "Task 12 delivered:", `DEC-114` "Task 3."), but every sibling anchor is followed by
   substance on the same line — a bare `Task 13.` alone would be unique in the file. Folding it onto
   the bolded ruling keeps the anchor and asserts nothing. Checked first that
   `gen-decisions-index.py` keys no marker or tag off line-initial bold (only ```` ``` ```` is
   matched by a `startswith`, `:114`), so the shape is safe.
   **Hard constraint met:** no surviving sentence asserts anything about `/harness-deploy`,
   `bin/deploy.sh`, or wholesale replacement — the whole `/harness-deploy` sentence and the live-risk
   paragraph are gone.
2. **`### The deviation worth naming` folded away (heading deleted, body kept).** Not merely that it
   was the only subheading left: the word *deviation* had its antecedent in the deploy material this
   edit deletes, so the heading was semantically dangling, not just structurally lonely. Cheap and
   reversible.

## Two durable lessons were deleted, and the asymmetry is real

Removing `### What the fixture caught that reading did not` deletes two genuinely durable engineering
lessons. Per the dispatch's hard constraint they were **not** preserved by moving them anywhere.

- **`printf … | python3 - <<'PY'` silently discards the pipe.** Still alive: enacted in live code at
  `.claude/skills/harness/bin/check-domain.sh:97` and `bash-write-guard.sh:35` (data via argv),
  covered by a live case at `.claude/skills/harness/bin/test-bash-write-guard.py:60`, and recorded at
  `.harness/features/FEAT-05-pyyaml-file-parsers/observations/harness-backend-dev.md:19`.
- **`set -u` with `"${empty_array[@]}"` aborts on macOS bash 3.2.** Survives in **git history only**
  after this edit. Its enactment site was `deploy.sh`, deleted in `e987c6d`; the operator grepped the
  tree for `${ARR` / `bash 3.2` and found no other site, and it is not in `.harness/logs/2026-08-03.md`.
  A reader who needs it: `git show 65d40cb:docs/harness/DECISIONS.md`.

## Index — DEC-113's row, before and after

```
- was: - DEC-113 @1964 [state,deploy,plan,skills] refs: DEC-112 :: Team and crew overrides live outside the tool tree, in project-owned state that harness development never edits, and are resolved first.
- now: - DEC-113 @1964 [skills,state] refs:  :: Team and crew overrides live outside the tool tree, in project-owned state that harness development never edits, and are resolved first.
```

The hand-written half is unchanged and still describes what survives (precedence only) — checked
before regenerating, no fix needed. Both expected generator effects **confirmed, not surprising**:

- `refs:` lost `DEC-112` — the only `DEC-1NN` mention in the section sat in the deleted fixture block
  (`gen-decisions-index.py:221-229`, refs computed from body text).
- `[tags]` dropped `deploy` and `plan` — computed from body word counts (`:244-252`); the deploy and
  safety-property prose that scored them is gone.
- Every other changed index row differs **only** in its `@NNNN` anchor. Verified mechanically: strip
  the diff sign and normalise `@NNNN`, and the only row appearing once instead of twice is DEC-113's.

## Gates

| Check | Result |
|---|---|
| T-14 `verify:` (cross-checked verbatim against `plan.yaml:915-924`, no mismatch) | **exit 0**, printed `STRUCK` |
| `python3 .claude/skills/harness/bin/gen-decisions-index.py` | exit 0, **emitted changes** to `DECISIONS-INDEX.md`, **no ORPHAN** |
| `bash .claude/skills/harness/bin/run-unit-tests.sh` | exit 0, `PASS test-gen-decisions-index.py` |
| SC-08's DEC-12 clause, wider than the verify's four files | `git grep -nE 'DEC-12([^0-9]\|$)' -- docs/` → **0 hits** |

`.claude/skills/harness/bin/check-docs.sh` does **not exist on this branch** (`git ls-files` returns
nothing for it) — it could not be run; noted so nobody records it as skipped.

`git diff --numstat docs/harness/DECISIONS.md`: `7 48` — one `-U1` hunk, entirely inside the old
1964-2014 span, so no collateral damage outside the section (P-08/G-10). `DECISIONS-INDEX.md`
regenerated. `.harness/features/.../feature.yaml` was already modified at spawn — not mine (P-03).

## Stale left standing — reported, not edited

Re-grepped DEC-113's inbound citations after this wider cut (`git grep -n 'DEC-113' -- docs/ .claude/
CLAUDE.md README.md`). All precedence citations remain valid. These cite DEC-113 for things it no
longer says:

0. **Inside the survivor itself:** `paths.crew_overrides`. `git grep -n 'crew_overrides' -- .claude
   docs .harness/README.md` returns **exactly one hit — this sentence**. The live key is
   `team_overrides` (`.claude/skills/harness/templates/team-config.yaml:47`, `docs/harness/SPEC.md:277`),
   and "both manifests" is deploy-era vocabulary. **Not edited on purpose:** the dispatch protects
   ruling 2's claim text and requires this exact sentence quoted verbatim as the presence half, so
   rewriting it would cross a LEAVE bound. Someone else's call, and the one stale item that sits in
   DEC-113's own body rather than another entry.
1. `docs/harness/BUILD.md:200`, `:776`, `:797`, `:829` — cite DEC-113 for the distribution command /
   the `agent_skills` ruling. **Ruled out of scope by the operator**; `:200`/`:776`/`:797` sit in
   already-struck rows that state the mechanism is deleted. Listed for the record only.
2. `docs/harness/DECISIONS.md:3986` — "deploy.sh never writes project state (by design, DEC-113)",
   inside another decision's incident narrative. DEC-113 no longer says this and `deploy.sh` is gone.
   Outside T-14's scope (T-14 touches only the DEC-12 and DEC-113 sections). Not caught by the
   verify's absence pattern, which greps `never touches project state`, not `never writes`.
