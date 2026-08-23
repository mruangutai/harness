# Receipt — harness-documentor — FEAT-33 T-19 — c1

**DEC-196 amendment 4 is appended, the index row is regenerated at 29 words, and no other entry
needed a strike.** Two files touched, both mine.

## What landed

`.harness/harness/docs/DECISIONS.md` — appended immediately before `## DEC-197`, matching amendment
3's voice (bold `**Amendment N (date) — ...**`, opening `DEC-196 amendment 4.`, italic section leads):

`**Amendment 4 (2026-08-23) — the station lifecycle is event driven, and every station has exactly one named writer**`

Nine sections, all eight required points: the six-row writer table plus `Abandoned` has no writer;
ruling 1 and its accepted cost; the INV-26 consequence and the single gate-script edit; the Review
measurement; what did not change; the caused-write ceiling; the closed hole; `Ready`'s one meaning and
board 2's lost signal; and the claim queue as settled.

`.harness/harness/docs/DECISIONS-INDEX.md` — row 214, hand-written text replaced then regenerated:
`am.1-am.4` and `DEC-138` now appear on the generated left side automatically.

## Verified, not assumed

- Every anchor in the amendment was re-derived in this worktree: `cmd_status` at `gh-sync.py:878`
  (Ready moves sub-issues only, Review moves parent + sub-issues, `_record_status` first and
  unconditional); `factory_claim.py:302` ready-station poll; `factory_decompose.py:414` ready write and
  `:393` "The parent is NEVER added"; `derive_station` returns building / review / None
  (`gh_board.py:88`); INV-26's `_EXPECT` — cited **by symbol**, because it sits at
  `check-state.sh:1275` here, not the `:1234` the plan and D-24 cite.
- The board-3 measurement (539 items, zero Review, zero Ready, `f5f5185`), the 490–506 GraphQL points,
  the `SKILL.md:191` hole and FEAT-32's 9-of-17 are quoted from
  `notes/research-FEAT-33-station-writers.md`; no board read was performed.
- `gen-decisions-index.py --stdout | diff -` → exit 0. `test-gen-decisions-index.py` → 9/9 ok.
- Index row = 29 words by `len(text.split())`.

## Two things the next reader needs

1. **The plan's `verify:` for T-19 is wrong at this SHA.** It says
   `gen-decisions-index.py --check`; there is no `--check` and the script exits **2** printing so.
   The real check is the `--stdout | diff` pipe, which I ran.
2. **INV-26's widening (T-22) has not landed.** `check-state.sh` is unmodified in this worktree
   (`git status`, and `git log -- check-state.sh` tops out at `5135ed6`), and `_EXPECT` still maps
   `done` to the done station. The amendment records the widening on ruling 4's warrant, which is
   recorded; the code change is still `status: building`. If T-22 is abandoned, amendment 4's INV-26
   paragraph becomes false and needs an amendment of its own — not an edit.

## Falsified prose found elsewhere, NOT fixed (not my file)

`.claude/skills/harness/SKILL.md:206-211`, the paragraph headed **"THE ORDER IS NOT A STYLE POINT"**.
It instructs ordering relative to a per-commit `close-task` and warns that "after the last task the
parent sits in `Building` forever" — both mechanisms D-23 removed. The same file's own table row
twelve lines above now says `close-task` is **no longer run per commit**, so the file contradicts
itself. T-14 owns it.
