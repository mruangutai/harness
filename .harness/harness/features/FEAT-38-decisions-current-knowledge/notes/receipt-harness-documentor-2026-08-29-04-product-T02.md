# Receipt — harness-documentor — FEAT-38 T-02 (product segment B1, run 2026-08-29-04)

**The APPEND-ONLY mandate is gone from `.harness/harness/docs/DECISIONS.md` and replaced by a
current-truth mandate. T-02's `verify:` ran verbatim from the worktree and exited `0`.** One hunk,
front matter only; no decision entry was read-modified.

## What changed

`.harness/harness/docs/DECISIONS.md`, opening blockquote. The old paragraph (`**APPEND-ONLY. Never
rewrite or renumber an existing entry.** … reversals are visible as reversals rather than as edits.`)
is replaced by four bolded runs carrying the intent's four points plus the history pointer:

1. `**Every entry states current truth, in its own voice.**` — no amendment sub-sections, no dated
   corrections; a correction rewrites the entry it corrects (intent point 1). Second sentence carries
   point 2: a falsified claim survives as one clause of current truth inside the replacing entry,
   with no date and no attribution.
2. `**Superseding is a single act.**` — the author of a superseding decision DELETES the replaced
   decision in the SAME edit; never a moment where both exist (point 3).
3. `**Numbers are never renumbered, and a deleted number is never reused**` — retired with the entry
   (point 4). Because point 4 states retirement, the `Numbering:` paragraph is **unchanged**, as the
   intent's fallback clause allows.
4. `**History is not lost; git holds it.**` — names the FEAT-22 rename (`8ad7d52`) and prescribes
   `git log --follow -- .harness/harness/docs/DECISIONS.md`.

Untouched, per non-goals: every `## DEC-` entry, DEC-188 (T-01's landed edit), the `Numbering:`
paragraph, the `What belongs here:` paragraph, the `Extracted 2026-07-26 …` provenance line,
`DECISIONS-INDEX.md`.

## Verification (all observed this run, from inside the worktree)

| Check | Result |
|---|---|
| T-02 `verify:` verbatim (cross-checked char-for-char against `plan.yaml:244-249`) | **exit `0`** |
| Same block run **before** the edit (baseline, G-03) | exit `1` — work had not already landed |
| `grep -c 'APPEND-ONLY'` whole file | `0` (was `1` at HEAD — the mandate was its only occurrence) |
| `grep -c 'a named successor exists to repoint its citations to'` | `1` — T-01 intact |
| `grep -nE '^## DEC-90 — STRUCK'` | matches, `1173:## DEC-90 — STRUCK 2026-08-21` |
| `git diff -U1` hunk headers on the file | `@@ -2,5 +2,18 @@` (mine) and `@@ -5948,5 +5961,8 @@` (T-01, pre-existing) — exactly one hunk is mine |
| worktree `git status --porcelain` | `M DECISIONS.md` + pre-existing `M plan.yaml`, `?? receipt-…-T01.md`, `?? observations/…`, `?? grilling-…md`. No new tracked file |
| main checkout `git status --porcelain -uno` | **empty** — no tracked modification. (Untracked-inclusive output lists ~11 pre-existing untracked notes/feature dirs, none mine, none touched) |
| `gen-decisions-index.py --stdout` | exit `0` (dry run only; nothing written) |
| Committed? | no |

Gate shape honoured: neither `APPEND-ONLY` nor the substring `add a new` appears anywhere in the
file (let alone lines 1-12), and `current` appears on line 3 — well inside the first 20.

## The intent's "8 amendments" figure does not reproduce

The intent justifies `--follow` with "a plain `git log` … reaches only 8 of the amendments this
feature folds." Measured at HEAD:

- plain `git log -- <path>`: 30 commits, oldest is the rename `8ad7d52` (FEAT-22) — so the mechanism
  the intent gives is **correct**: plain log stops dead at the rename.
- amendment markers (`^\*\*Amend…`) at `8ad7d52`: 5 (4 `**Amendment` + 1 `**Amended`); at HEAD: 15
  (13 + 2). So **10** markers post-date the rename (9 counting `**Amendment` only) — not 8.

I therefore wrote the mechanism and omitted the number: the prose states the rename blocks plain
`git log`, which is verified, and asserts no count. The `8` is raised as a non-blocking question for
whoever re-signs the plan text.

## Gaps / not mine

- `.claude/skills/harness/bin/gen-decisions-index.py:29-30,139` still parses amendment markers
  (`AMEND_HEADING_RE`, `AMEND_BOLD_RE`) and aggregates amendment numbers. Front-matter prose now says
  amendment sub-sections do not exist; the generator still expects them. A code task must retire that
  parsing — not a docs edit.
- My own project-tier Expertise (`P-01`, `G-01` in `.harness/expertise/harness-documentor.md`)
  instructs appending amendments inside the amended section. Falsified by this edit, but Expertise is
  writable only under a distillation dispatch — flagged, not touched.
- Prose sweep for the old convention across `CLAUDE.md`, `docs/`, `.claude/{skills,commands,agents}`,
  `.agents/`, `.harness/expertise`, `.harness/harness/docs/*.md`: no other statement of the mandate.
  The two `append-only` hits found (`merge-gitignore.sh:65`, `SPEC.md:83` on `.harness/logs/`) are
  unrelated subjects.
- My hunk adds 13 lines to the front matter, so every `@line` anchor in `DECISIONS-INDEX.md` shifts.
  Expected effect of this edit; T-11 owns regeneration.
