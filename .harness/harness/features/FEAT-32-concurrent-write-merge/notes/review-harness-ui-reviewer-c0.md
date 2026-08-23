# UI review — FEAT-32 concurrent-write-merge — c0

## Verdict: PASS (scoped out for rendered UI; operator-facing diagnostic text audited per dispatch, no gating defect)

## Census (measured, `git diff 12c66b3..5107efb --stat`, 65 files)

Extension breakdown of the 65 changed files: 41 `.md`, 14 `.py`, 3 `.yaml`, 3 `.sh`, 2 `.json`,
1 `.html`, 1 `.gitignore`. Zero `.css`/`.scss`/`.tsx`/`.jsx`/`.vue`/`.svelte`/`.less`.

**DESIGN.md**: none exists for FEAT-32 (`.harness/harness/features/FEAT-32-concurrent-write-merge/`
holds only BRIEF.md/STATE.md/feature.json/plan.yaml/notes/observations — no DESIGN.md). This is not
a gap: the repo *does* use DESIGN.md as a convention (3 hits repo-wide: FEAT-10, FEAT-11, FEAT-19,
all features with an actual rendered surface) and FEAT-32 has none to specify.

**The one `.html` hit** — `notes/ship-review-2026-08-22-build-gate.html` — is in the diff, but it is
a **generated artifact, not a shipped UI change**. `.claude/skills/harness/SKILL.md:393-396` and
`render-brief.py`'s own docstring ("DERIVED, NEVER AUTHORED... same law as render-map.py, DEC-141")
establish this is a deterministic projection of the paired `.md`, produced by a renderer that is
**unchanged in this diff** (`render-brief.py` does not appear in the 65-file stat). The pattern is
old and repo-wide — the same `ship-review-*.html` sibling exists for at least 20 other features
(FEAT-03, FEAT-10-31, confirmed via `find`). No CSS, template, or design-token change rides in this
diff; the two new files are new *content* flowing through an untouched pipeline. No UI surface to
audit here.

## Operator-facing refusal text — audited per explicit dispatch instruction (in-remit, not declined)

Traced the new stderr paths in `check-domain.sh`, `dispatch-guard.sh`, `validate-digest.py`, and the
merge-CLI family (`plan-merge.py`, `observations-merge.py`, `expertise-merge.py`,
`inflight_registry.py`).

**These messages are a *checkable contract*, not free text** — `plan.yaml:1028-1051` specifies the
literal opening markers, field order, and byte-identical `release_cmd` string, test-enforced by
`test-inflight-registry.py` cases 6/6b. That plan section is functioning as this surface's DESIGN.md.

1. **`release-all` escape hatch — printed verbatim and copy-pasteable.** `inflight_registry.py:44`:
   `RELEASE_ALL_CMD = f"python3 {CLI_REL_PATH} release-all"` →
   `python3 .claude/skills/harness/bin/inflight_registry.py release-all`. `dispatch-guard.sh`'s
   single-flight path (`refusal_lines()`, `inflight_registry.py:229-237`) prints this exact string as
   its last line — no placeholder, no truncation. Confirmed byte-for-byte against the constant.

2. **Exit-2 disambiguation — each refusal names itself in text, even though several share exit code
   2.** `check-domain.sh` alone has ~10 distinct `sys.exit(2)` sites (manifest-parse failure,
   boundary-module tamper, SHARED-path denial, worktree-placement checks, and the new T-14 approval
   guard at `check-domain.sh:562-568`) — every one opens with a distinct, specific sentence
   (`"check-domain: BLOCKED — {agent} may not change {frag} in {rel}."` for the new approval guard vs.
   `"check-domain: {agent} is writing SHARED path {rel}..."` for the pre-existing denial). Same
   pattern in `dispatch-guard.sh` (new single-flight message vs. the pre-existing model-pin denial)
   and `validate-digest.py` (new D-09 children-in-flight message at `validate-digest.py:920` vs. the
   two pre-existing schema/file-shape exit-2 paths at lines 801/958 — neither of which even shares a
   `check-digest: BLOCKED` prefix with the new one). An agent or operator reading the stderr text —
   not just the exit code — can always tell which refusal fired. No actionability defect found here.

3. **Merge-CLI refusals** (`plan-merge.py`) tag by kind — `UNPARSEABLE:`, `REFUSED:`, `CONFLICT:` —
   and each `CONFLICT`/`REFUSED` line names the field/id and prints both the base and proposal values
   (e.g. `plan-merge.py:196-202`, `:237-243`). These use exit codes 5/6/7/8/9, distinct from the
   check-domain/dispatch-guard/validate-digest family's 2, so no cross-family collision.

4. **One noted style inconsistency, checked and NOT filed as a defect.** The two brand-new refusal
   markers use a plain hyphen (`"BLOCKED - single-flight"`, `"BLOCKED - returned with children in
   flight"`) while the surrounding pre-existing convention in the same files uses an em dash
   (`"BLOCKED — {agent} passed model:"`, `"BLOCKED — {agent} may not change"`). Grepped and confirmed
   both forms exist. This is **not a drift to flag**: `plan.yaml:1030,1037` mandates the plain-hyphen
   marker literally, so the implementation matches its approved contract exactly — filing it would be
   asking to override a signed decision, not a build defect (see repository Expertise G-08 precedent).

5. **One residual, non-gating observation.** `RELEASE_ALL_CMD` is a bare relative-path invocation
   with no `--root` — `inflight_registry.py`'s own CLI (`_resolve_root`) requires either
   `CLAUDE_PROJECT_DIR` in the environment or an explicit `--root` flag it doesn't carry. Both
   `dispatch-guard.sh` and `inflight_registry.claim`'s caller already compute `root` in scope when
   the refusal fires but don't fold it into the printed command. In a plain shell without
   `CLAUDE_PROJECT_DIR` set, or a cwd other than the checkout root, the pasted command would fail with
   `inflight_registry: no root - set CLAUDE_PROJECT_DIR or pass --root` rather than the intended
   release. `plan.yaml:1050-1051` explicitly specifies the command as "built from the same constant"
   verbatim, so this is the contract as designed, not a coding slip — I'm surfacing it as an open
   question about the contract, not a build-side defect.

## Scope verdict

No rendered UI surface changed in this diff (measured: 0 style/component-file hits; the sole `.html`
hit is an unmodified renderer's mechanical output). Per explicit dispatch instruction, audited the
adjacent operator-facing refusal text instead — found it actionable, self-distinguishing at exit code
2, and matching its own written contract (`plan.yaml`) byte-for-byte on the two points that contract
pins. One non-blocking, contract-level open question about the `release-all` command's environment
dependency.
