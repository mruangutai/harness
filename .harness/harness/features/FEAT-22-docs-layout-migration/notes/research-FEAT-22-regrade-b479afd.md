# Re-grade — FEAT-22 · seven SCs at `b479afd` · all seven met

**PASS.** `git rev-parse HEAD` = `b479afd27758c76d6ecec9c81c45b6afea0f7f0d`, exactly the pin, and
`git status --porcelain` shows **no modified tracked file** — everything below was measured on the
pin's own tree, not HEAD-plus-drift. `git show --stat b479afd` reproduces the claimed set: 5 files,
39 insertions, 4 deletions, matching the dispatch's list item for item.

Scope: SC-02, SC-06, SC-07, SC-08, SC-09, SC-10, SC-12 only. SC-01/03/04/05/11 untouched.

## Verdicts

| SC | verdict | method | evidence, at the pin |
|---|---|---|---|
| SC-02 | met | automated/unit | `test-layout-migration.py` case 21 green in the suite run; real-root detector prints `docs: CLEAN — evidence migrated` |
| SC-06 | met | automated/integration | `test_committed_index_matches_a_fresh_regeneration` green; `DECISIONS-INDEX.md:8` names `.harness/harness/docs/DECISIONS.md`, no legacy path anywhere in the file |
| SC-07 | met | automated/unit | `run-unit-tests.sh --kind unit` exit 0, 0 FAIL |
| SC-08 | met | automated/integration | `--kind integration` exit 0, 0 FAIL, 635 `ok` lines |
| SC-09 | met | automated/unit | `test-layout-migration.py:133` asserts `int(m.group(2)) > 0`; it **executes** — `ok - case 1: non-zero doc-root count` in the suite output |
| SC-10 | met | inspection | sweep re-run below; both clauses hold |
| SC-12 | met | inspection | `DECISIONS.md:5948` / `:5950` — am.1 states the new spelling `.harness/*/docs/**` |

Corroborating: `layout_migration.py` exit **0** (captured directly, not through a pipe);
`check-state.sh` exit 0.

## SC-10 — re-derived, class by class, not by arithmetic

Sweep at the pin with the plan's own two-spelling resolver
(`git grep -lE 'docs/harness|"docs", ?"harness"'`, this feature dir excluded): **173 files**.
Bucketed by path, the residual "OTHER" bucket is **empty** — every hit falls in a named class:

- 158 `.harness/harness/features/**` · 6 `.harness/notes/**` · 3 `.harness/logs/**` ·
  1 `.harness/harness/docs/` (`DECISIONS.md` alone) · 5 `.claude/skills/harness/bin/`.

The CORRECTION's 158 + 6 + 3 + 1 + 5 = 173 therefore **holds its members**, not just its sum. The
five `bin` files are `layout_fixtures.py`, `layout_migration.py`, `test-check-domain.py`,
`test-check-state.py`, `test-layout-migration.py` — every hit is a legacy fixture string, a reader-table
regex, or a tmp-fixture path join. **Clause (a):** no hit outside `bin` is live code, and
`.claude` (non-bin), `CLAUDE.md`, `.harness/expertise` and `.github` return **zero** hits;
`SPEC.md:1721` now reads `.harness/harness/docs/DECISIONS.md`. **Clause (b):** each class is named
as a survivor, and the one member that needed an explicit ruling has one —
`research-FEAT-22-docs-boundary.md:342-350`, "Disposition: `layout_migration.py:34` stays".

**Non-blocking note:** `layout_migration.py:34` is stale in two ways — "emits a slash-shaped
docs/harness/DECISIONS.md" describes a defect now fixed, and "until unit 4 rewrites" describes done
work. It is not a claim about where the docs live, so it does not touch SC-10's text, and the audit
ruled it a knowing survivor deliberately. Worth a future tense-correction; not a miss.

## Retraction — my own prior artifact's drift note is wrong

`research-FEAT-22-goalcheck-e26e628.md:67-71` claimed 173 survivors at `e26e628` with `bin` holding
3. That was measured with a **literal-only** grep. Under the plan's two-spelling command the note's
`survivors: 174` was **correct** at `e26e628`, and `bin` held **5**, verified member by member this
run. The prior drift note is superseded; the boundary note was not over-counting.

## The count trap — settled empirically, inert

`grep -rn 'feat22-verify-T10'` across `.claude/skills/harness/bin/` and `.github/workflows/` returns
**nothing**: no runner array and no CI job picks that script up. Both suites exit 0 at the pin. The
host's framing is confirmed by measurement, not accepted on assertion.

## Open questions

1. **The write guard denies pm bash-writes even inside the session scratchpad.** `sed`, `mv`, `cp`
   and `rm` were each blocked on scratch copies (matched by basename, and once on an unexpanded
   `$S`), so the P-09 mutation proof for SC-09 could not be run. SC-09 is graded on the dispatch's
   stated basis — the named assertion executes and reads the criterion's own quantity — which is
   sound but weaker than a mutant. Harness defect, non-blocking.
2. Carried forward, unresolved from the prior run: am.1's wording says the control-plane list "is
   advertised in deny messages"; `0140dce` established that `classify` **filters against** it. A
   signed entry, left standing for the operator.
