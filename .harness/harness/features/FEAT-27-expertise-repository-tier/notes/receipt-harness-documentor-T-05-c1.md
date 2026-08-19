# Receipt — harness-documentor — T-05 — c1

**Done. `DOCS-OK`, exit 0.** The two documents now describe the two Expertise tiers as the code
builds them, and three stale one-tier statements outside the named passage were fixed too.

## What changed

`.harness/README.md` (1 hunk) — the single Expertise row became two, same three-column shape:
`expertise/<agent>.md` (craft, 150 lines, true wherever the agent works) and
`<repo>/expertise/<agent>.md` (one repository only, 40 lines). Both rows state injection at every
spawn by the `SubagentStart` hook, that the agent never reads either itself, and the same owner rule
("each agent, its own file only").

`.harness/harness/docs/SPEC.md` (4 hunks) — §5.2's format paragraph now names both tiers and paths
(`.harness/expertise/` and `.harness/<repo>/expertise/`), both budgets (150-line / 40-line) as
enforced at authoring time by `bin/check-expertise.sh` and re-applied as a truncation backstop in
the hook, the injection order (global craft → project craft → every repository tier present, sorted
by segment), scope-only labelling, the precedence rule in the hook's own words, and the
not-your-segment caveat. The repository-token scan is stated as ADVISORY only, never a violation,
with the token list left in the script rather than restated.

Three stale statements the task did not name, all in SPEC and all one-tier:

- §5.6 was titled "Two tiers of Expertise — project and global" and its bullet read "**Project wins
  on conflict.**" — the exact claim the intent forbids, phrased so the negative greps miss it.
  Retitled, table extended to global / project / repository with budgets, bullet replaced by a
  pointer to §5.2's precedence rule.
- The §5 contents row ("project vs global tiers") and the §5 **Location:** paragraph both asserted a
  single per-project path. Both now point at §5.2 / §5.6.

## Grounded in the code, not the plan

- Order, sorting, labels and the precedence sentence: `.claude/skills/harness/bin/inject-expertise.sh`
  (global block, project block, then repository blocks sorted by segment; the precedence line is
  emitted **only when at least one repository block exists** — SPEC says so, rather than claiming it
  is always present).
- Budgets, tier classification by resolved absolute path, and the advisory-only token scan:
  `.claude/skills/harness/bin/check-expertise.sh` (`CRAFT_LINE_BUDGET=150`, `REPO_LINE_BUDGET=40`,
  advisories never appended to `problems`, so the exit code cannot flip).

## Verify

Run verbatim from the repo root, before and after the three extra fixes. Final line `DOCS-OK`,
exit status 0 both times.

## Open

- Nothing blocking. For whoever closes FEAT-27: the verify's negative clauses are literal, so
  paraphrases of the struck claims elsewhere in the tree are covered by no gate here — §5.6's
  "Project wins on conflict" was one, and it survived a green run at 89787e6.
