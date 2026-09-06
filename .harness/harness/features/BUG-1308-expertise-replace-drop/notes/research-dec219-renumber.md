# BUG-1308 amendment — DEC-218 → DEC-219 (second renumber)

**Done. All 11 live self-references now read DEC-219 in `plan.yaml`, and SC-10 in `BRIEF.md`. One
DEC-218 token survives, inside D-16, naming it as BUG-1304's property. The DEC-216 panel finding is
byte-identical. Neither approval block was written.**

## Why 219

`DECISIONS.md` on this rebased worktree carries `## DEC-216` (BUG-1303), `## DEC-217` (BUG-1303) and
`## DEC-218 — Claim-set membership binds governed writes to assigned worktrees on both routes`
(BUG-1304, landed on origin/main). `grep 'DEC-219'` over `DECISIONS.md` + `DECISIONS-INDEX.md` exits
1 — the slot is free.

## Baseline, measured before any write

- `grep -c 'DEC-218' plan.yaml` → `11`; lines `125 141 185 779 793 796 802 819 820 833 837` — matches the lead's baseline exactly.
- `grep -n 'DEC-216' plan.yaml` → one line, `246:      sentence, T-04 omits SPEC's 10/11/12 and DEC-216's Over/Because/Tradeoff content.`
- `grep -n 'DEC-218' BRIEF.md` → one line, `115:` (SC-10).

## What changed

Every write through `plan-merge.py amend --expect-sha256 --value-file`; no Edit, Write or redirect
touched `plan.yaml`. Fields amended: `D-11.choice`, `D-13.choice`, `T-04.title`, `T-04.verify`,
`T-04.intent` (pure `DEC-218`→`DEC-219` substitution, 1/1/1/3/4 = 10 tokens), plus `D-16.choice` and
`D-16.because` rewritten to record the second renumber (1 further DEC-219 token → 11).

**Machine proof the diff is nothing else** (`/tmp/bug1308-verify.py`, loads `HEAD:plan.yaml` vs the
worktree and walks every node): five fields differ *only* by the substitution; exactly two —
`D-16.choice`, `D-16.because` — are rewritten; `approval` and `panel` mappings compare equal; task
and decision id lists are unchanged; D-16 key order is `id, choice, because, dec`, identical to HEAD
and to its siblings. `T-04` holds **zero** DEC-218 tokens, and each pinned literal
(`replace and drop through the ops subcommand`, `DEC-66`, `DEC-95`, `DEC-145`, `10 MISSING TARGET`,
`11 AMBIGUOUS TARGET`, `12 MALFORMED OPS`, `expertise-merge.py ops`) still occurs twice
(verify + intent), unchanged.

## Trap hit and closed — hyphen folding (new gotcha)

`amend` re-emits a folded `>-` scalar as one long line. Re-wrapping it with `textwrap.fill` broke
`main-session-direct` across the fold, and YAML folding turned the break into a space:
`'main-session- direct'`. Caught by comparing the loaded value against HEAD's, fixed with
`break_on_hyphens=False`, and re-proved equal. **Any re-wrap of a folded scalar must be verified by
loading the value, not by reading the diff.**

## Acceptance, as measured after the writes

- `grep -c 'DEC-219' plan.yaml` → `11` (equals the baseline DEC-218 count).
- `grep -n 'DEC-218' plan.yaml` → one line only, `184`, inside D-16: `originally carried: BUG-1303 landed 216 and 217 and BUG-1304 landed DEC-218, its claim-set` — the continuation reads `membership entry, on origin/main before this feature merged`. Foreign reference, expected.
- `grep -n 'DEC-216' plan.yaml` → `248:      sentence, T-04 omits SPEC's 10/11/12 and DEC-216's Over/Because/Tradeoff content.` — byte-identical to HEAD's line 246; the number moved only because D-16 grew two lines.
- `grep -n 'DEC-219' BRIEF.md` → one line (SC-10); `grep -c 'DEC-218' BRIEF.md` → `0`.
- `check-plan-routes.py <plan.yaml>` → `0 violation(s) across 1 plan(s)`, **exit 0**; `yaml.safe_load` parses.
- `approval:` reads `status: approved` / `approved_by: mruangutai` / `date: '2026-09-05'`; BRIEF `## Approval` reads `status: approved`. **Neither was written by me** — `plan-merge.py` carries the block forward and I issued no `sign-approval`.
- `git status --porcelain` → the two target files modified, nothing else. No commit, no test suite.

## Open

- `STATE.md:17/31/47` still narrates the first renumber and instructs "Do NOT renumber
  plan.yaml:246 to DEC-218". Out of my grant and out of this dispatch's scope; the number in that
  instruction is now stale. Orchestrator's call.
- `notes/`, `runs/` and `observations/` retain DEC-216/218 as transcribed history. Correctly left
  alone — the record is not rewritten.
