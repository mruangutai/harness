# Receipt — harness-documentor distillation

**Six ops applied, `check-expertise.sh` exits 0.** Four new Patterns, one new Gotcha into the last
free slot, one Gotcha sharpened in place; no entry was displaced or dropped, because neither section
hit its cap. One pre-existing over-cap entry was condensed to make the checker pass.

## Entry counts

| Section | Before | After | Cap |
|---|---|---|---|
| Patterns | 10 | 14 | 15 |
| Gotchas | 14 | 15 | 15 |
| Outcomes | 0 | 0 | 10 |
| Open | 0 | 0 | 5 |

File is 95 lines of a 150-line budget. Outcomes and Open stay empty deliberately — nothing this
feature passed the six-spawns test in those shapes, and the two live rulings still pending
(`crew_overrides` wording, the `DECISIONS.md` DEC-113 citation) are decisions, barred from Expertise.

## Accepted, by source

**From my own observations log and receipts (4):**

- **P-11** — a `verify:` clause green before the edit and green after. My log recorded the mechanism;
  the consequence relayed to me (eight PASS assertions, criterion still unmet, one fix cycle spent)
  is what made it durable. The new action is *print the matching line*, which G-01 does not carry.
- **P-12** — from the c2 receipt's "two durable lessons were deleted" inventory: name a live in-tree
  site per deleted lesson, and where none exists say so with a `git show <sha>:<path>`.
- **P-14** — from log bullet 1: the index generator recomputes `refs:` and `[tags]` from body text,
  so striking a block drops them. Designed behaviour, so it is Expertise and not an open question.
- **G-04 condensed** — housekeeping, not a new lesson. It was 53 words at HEAD (checked against
  `git show HEAD:`), over the 50-word cap before I touched anything; now 43, rule and both
  imperatives intact.

**Accepted from the three relayed candidates (2 of 3):**

- **P-13** (relayed #1) — centred on verify *coverage*, not on enumeration, which P-01 already owns:
  narrowing a claim in one file does not travel to a stronger restatement in a file no clause covers.
- **G-15** (relayed #3) — accepted only after reproducing it, and scoped narrower than reported.

## Relayed candidate #2 — the backticked-token escape

**Confirmed at source, then accepted as a `replace` on G-08 rather than as a new entry.**
`grep -nE 'Enroll = deploy \+ init'` on `docs/harness/BUILD.md` exits 1 while
`grep -n 'Enroll = deploy'` returns the live bullet at `:826`. G-08 already ruled this class
("compound patterns are blind to prose using the plain word"); adding a second entry would have been
the same rule twice. G-08 now names inline markup as the mechanism that breaks adjacency and keeps
its file-type clause, at the same length.

## Relayed candidate #3 — the contradiction, settled

**Both reports were correct. They differ by one flag, `-E`.** Measured here (git 2.50.1 Apple):

| Command | Result |
|---|---|
| `git grep -cE '\bdeploy' -- docs/harness/BUILD.md` | **exit 1, no output** |
| `git grep -c '\bdeploy' -- docs/harness/BUILD.md` (BRE) | 5 |
| `git grep -cP '\bDEC-113' -- docs/harness/DECISIONS.md` | 3 |
| `/usr/bin/grep -cE '\bdeploy' docs/harness/BUILD.md` | 5, exit 0 |

So "git grep drops `\b`" is false and "grep drops `\b`" is false. The true statement is narrow:
**`git grep -E` treats `\b` as matching nothing and exits 1 — indistinguishable from a clean sweep.**
pm's counterexample used BRE, so `\b` was honoured; nothing was overturned. A present-day
`git grep 'DEC-12\b'` exits 1 in both dialects only because DEC-12 is struck and has zero
occurrences — not a contradiction. G-15 does **not** say "drop `-E`": my own c1/c2 sweeps used
`git grep -nE 'DEC-12([^0-9]|$)'`, and dropping `-E` there would silence the alternation. The rule
is `-P`, or spell the boundary as a character class the way those receipts already did.

Not a harness defect: `/usr/bin/grep -rn '\\b' .claude/skills .claude/commands .claude/agents` and
the two `.harness/features/*/plan.yaml` hits are all Python `re` patterns, where `\b` is honoured.
No shell sweep in the tree pairs `-E` with `\b`.

## Rejected

- **Log bullet 3** (run the `awk length` check after the last edit, not before) — an instance of
  G-01's rule already, and too generic to change what a successor does.
- **No relayed candidate was rejected outright**; #2 was accepted in `replace` form rather than as a
  new entry, which the free/occupied slot arithmetic did not force — it was a rule-duplication call.

## Stale left standing — reported, not edited (all four files are off-limits to me)

1. `docs/harness/BUILD.md:826` — `**Enroll = deploy + \`/harness-init\`.**` is unstruck and describes
   a deploy step whose script was deleted in `e987c6d` (`git show --stat`, confirmed). It is the one
   surviving `Enroll = deploy`
   string in the four swept files and it evaded both T-12's and T-14's verify.
2. `docs/harness/DECISIONS.md:3986` — "deploy.sh never writes project state (by design, DEC-113)".
   DEC-113 no longer says this.
3. DEC-113's own surviving sentence names `paths.crew_overrides`; the live key is `team_overrides`.
   A pending ruling — listed, not encoded anywhere.

## One stale Expertise entry I did not fix

**G-13 contrasts `git grep`/`rg` with "plain `grep -r`" walking git-ignored paths.** In this
environment the shell's `grep` is a function exec'ing `ugrep` with `--ignore-files`
(`which grep`), so plain `grep -r` skips them too and the contrast no longer holds as written.
`/usr/bin/grep` still behaves as G-13 describes. Gotchas is at 15/15, so correcting it means a
`replace`, and the entry is outside my three candidates and my own log — flagged, not fixed.
