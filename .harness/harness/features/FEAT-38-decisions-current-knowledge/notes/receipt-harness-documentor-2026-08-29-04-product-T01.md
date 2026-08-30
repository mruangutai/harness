# Receipt — harness-documentor — FEAT-38 T-01 — run 2026-08-29-04-product

**DEC-188's retention clause is struck and replaced with the successor-exists rule. T-01's `verify:`
block, run verbatim from the worktree, exited `0` (observed). The feature's deletion gate is open.**

## What changed — one hunk, one file

`.harness/harness/docs/DECISIONS.md`, inside `## DEC-188 — A contradicted decision is struck, not
marked` (the entry's last paragraph, located by content per the intent's warning; it sat at 5949 at
spawn). Deleted, not marked — DEC-188's own procedure ("struck from the record", not marked stale,
not left standing with a marker beside it), so the struck text does not survive anywhere in the file:

- **Out:** `**Struck decisions keep their heading and a strike record.** They are not deleted from the
  file. …` (3 lines)
- **In:** the narrower rule as current truth, no date and no attribution, opening
  `**A struck decision is DELETED only when a named successor exists to repoint its citations to.**`,
  plus the boundary clause: DEC-90 is the one entry this rule keeps, its successor being a SPEC
  section rather than a decision and its historical citations not editable.

`git diff -U1` is exactly that one hunk (6 insertions, 3 deletions). DEC-188's strike procedure, its
"enforcement is a human reading a diff" sentence, and its `bin/check-docs.sh` deletion record are
byte-identical. No entry deleted, no entry authored, opening blockquote untouched,
`DECISIONS-INDEX.md` untouched (T-11 owns it).

## Wording divergence — the plan disagrees with itself, and the gate broke the tie

T-01's `intent:` quotes the replacement as "…a named successor exists **for a reader to land on**",
while T-01's `verify:` requires the literal substring "…a named successor exists **to repoint its
citations to**". Both are in the signed plan; they cannot both be in the prose. I wrote the `verify:`
form — a gate is the tie-breaker over prose, and the dispatch independently mandates that literal.
The meaning is identical (a citation lands on the successor). The intent's remaining three sentences
are transcribed as written. Raised as a non-blocking question so the plan text can be reconciled.

## Facts checked rather than transcribed

- **DEC-90's successor is a SPEC section.** `DECISIONS.md` §DEC-90 (struck 2026-08-21) states "The
  single-operator boundary now lives in SPEC §15.1 alone". The clause I added is true, not repeated.
- **`## DEC-90 — STRUCK 2026-08-21` heading still matches** `grep -nE '^## DEC-90 — STRUCK'`. Its
  strike record is untouched — this feature's one recorded exception.
- **No generator marker token** opens the new bold run, so nothing here can make a live decision's
  index row read as superseded. The index row for DEC-188 will recompute (body changed, downstream
  `@line` anchors shift by +3) — that is an effect of this edit, for T-11, not a generator defect.

## Stale surface this strike leaves behind — not mine to edit

`.harness/harness/expertise/harness-documentor.md:15` (repository tier, harness) still asserts the
struck unconditional form: "A struck decision keeps its heading and a strike record so old citations
still land somewhere." It is now false in the general case. Expertise is written only under a
distillation dispatch, so I left it. Repo-wide sweep for the struck wording (`git grep`, excluding
`*/features/*`, `DECISIONS.md`, `DECISIONS-INDEX.md`) found **that one file and nothing else** —
`CLAUDE.md`, `docs/`, `.claude/`, `.agents/` are clean.

## Verification — observed

| Check | Result |
|---|---|
| T-01 `verify:` cross-checked against `plan.yaml` (lines 194-200) | identical to the dispatch, no mismatch |
| `verify:` run before first edit (baseline) | exit `1` — work had not landed |
| `verify:` run verbatim from worktree after edit | exit **`0`** |
| `grep -nE '^## DEC-90 — STRUCK'` | matches, line 1160 |
| `git status --porcelain` | `DECISIONS.md` is the only tracked file *I* modified |
| commits | none; HEAD still `204b469` |

No formatter, linter, project test suite, or index regeneration was run.

## Incident — a stray edit landed in the MAIN checkout and was reverted

My first edit used the repo-relative path, which resolved against the session cwd
(`/Users/molchairuangutai/GitHub/harness`) rather than the worktree. The main checkout's
`DECISIONS.md` received the hunk. I caught it on the same `verify:` run (it still failed in the
worktree), confirmed via `git diff -U1` that the stray change was that hunk and nothing else, and
reverted it **by content edit** — not `git checkout -- <path>`, which is forbidden here.
`git status --porcelain .harness/harness/docs/DECISIONS.md` in the main checkout is now **empty**:
main is clean and no other file there was touched. Every subsequent path was absolute.

## Not mine, flagged for the record

`git status` in the worktree also shows `plan.yaml` modified and
`.harness/notes/grilling-decisions-current-knowledge-2026-08-24.md` untracked. The `plan.yaml` diff
is five `status: pending` → `status: building` flips (`git diff -U0`) — dispatch bookkeeping present
at spawn, not authored by me.

## Caveat on what the gate proves

All three `verify:` clauses are literal presence/absence greps. None tests that the replacement
states the successor-exists rule *correctly* — prose reversing the rule while carrying the required
substring would still exit `0`. The substance is covered only by my reading of DEC-188 and of the
intent block.
