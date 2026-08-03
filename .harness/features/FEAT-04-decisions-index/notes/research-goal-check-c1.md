# Goal-check — FEAT-04 decisions index @ `363b539`

**All 12 success criteria are met.** Every `verify:` method is the BRIEF's own. Two stale-prose notes,
zero unmet criteria, no edits to BRIEF/PLAN. Tree left clean (`git status --porcelain docs/harness/`
empty; the generator was exercised via its read-only `--stdout` mode, never its write path).

## Re-derived counts (nobody's on report)

- Authority `docs/harness/DECISIONS.md`: raw `^## DEC-NN` = **171**; fence-guarded live = **170**
  (170 distinct). The one-off is the fenced re-occurrence documented in PLAN D-04.
- Index `docs/harness/DECISIONS-INDEX.md`: **170** `^- DEC-` rows, **170** distinct ids → equality holds.
- Index shape: **190** physical lines; rows occupy lines **21–190** contiguously; zero non-blank
  non-row lines in that span → exactly one physical line per row.
- Rulings after ` :: `, stripping `— SUPERSEDED BY DEC-NN` and `<!-- ok-stale -->`: max **30** words
  (DEC-69), **0** rows over the 30-word cap; min **72** non-whitespace prose characters, **0** rows
  under the 20-character floor; `RULING PENDING` occurrences **0**.
- Runner: `run-unit-tests.sh` exit **0**, 7 `PASS` lines including `PASS test-gen-decisions-index.py`,
  and `grep -c '^MISCONFIGURED'` over stdout+stderr = **0** (anchored at the emission site
  `run-unit-tests.sh:19`, not a substring — `ok  … FAIL …` lines in the output are test-case names).
- `test-gen-decisions-index.py` direct: exit 0, all six cases `ok`.

## Per-SC verdicts

| SC | method (BRIEF) | verdict | evidence |
|---|---|---|---|
| 01 | automated | PASS | `test-gen-decisions-index.py:139-141` run-time compare, case `ok`; live 170 = rows 170. Prose's "169 at `f723194`" is stale (DEC-170 landed); operative "counted at run time" is satisfied |
| 02 | automated | PASS | absence `:356` (`RULING PENDING` 0) + presence floor `:379` (min 72 non-ws chars); case `ok` |
| 03 | automated | PASS | `:350-352`; token emitted from `gen-decisions-index.py:53` `HEADER`, so not editable away |
| 04 | automated | PASS | `:150-213` preserve-by-DEC, `:216-286` ok-stale, `:407-451` orphan both directions — three cases `ok` |
| 05 | inspection | PASS | `gen-decisions-index.py --stdout` exit 0, `diff` vs committed index → identical; `git status --porcelain docs/harness/` empty. Equivalence to the criterion's write-path command is exact, not assumed: both branches emit the same `output` computed at `gen-decisions-index.py:348` (`:351` stdout, `:354-355` file) |
| 06 | automated | PASS | `:312-320` planted-unmarked → exit 1 naming the index path and the owning DEC; `:322-329` same line marked → exit 0. Both halves |
| 07 | inspection | PASS | `check-docs.sh` exit 0, `checked 45 superseded pattern(s)` (run as the final action of this check) |
| 08 | inspection | PASS | receipt cited, not re-run: `observations/harness-documentor.md:118-138` — landing `file:line` in `docs/harness/SPEC.md`, exit 0→1→0, exactly one hit attributed to `DEC-120`, `git status --porcelain` empty on that path, `--audit` exit 0 with zero inert markers |
| 09 | inspection | PASS | presence `CLAUDE.md:36,43` (2 hits, both now point at the index); both widened absence greps exit 1 / 0 hits over `CLAUDE.md .claude/skills .claude/agents .harness/expertise` |
| 10 | inspection | PASS | `harness-handoff/SKILL.md:64` carries `floor`; four numbered triggers `(1)…(4)` at `:72-75` |
| 11 | automated | PASS | **structural:** 190 ≤ 260 lines, asserted at `:353`; one-per-line re-derived (rows 21–190, no continuation lines), row parse is per-physical-line at `:373`. **per-ruling:** 0/170 over 30 words, max 30, asserted at `:381-397`. Both axes measured at `363b539`; the "82 of 169 … max 165" figure in BRIEF is the pre-remediation `ce2cd17` measurement |
| 12 | automated | PASS | runner exit 0, `PASS test-gen-decisions-index.py`, 0 lines matching `^MISCONFIGURED`; script listed in `run-unit-tests.sh:6` |

## Stale prose reported, not fixed (no BRIEF edit)

1. **SC-01** cites 169; the live count is 170 after DEC-170. Criterion as written ("counted at run
   time rather than against a frozen number") is satisfied, so this is a note, not a gap.
2. **SC-11's** amendment paragraph quotes a pre-remediation measurement at `ce2cd17`; current state
   is 0 rows over cap. It reads as rationale for the work, not a current-state claim.

Neither warrants a third re-signature. Backlog items named in the dispatch (DEC-102's missing
supersession clause, the frozen 171/170 literals at `test-gen-decisions-index.py:115,120`, the two
row grammars) are unchanged and out of scope here.

## SC-08 handling

Not re-run. The pinned plant phrase is deliberately not reproduced anywhere in this note and no
`check-docs.sh` hit block is pasted; the receipt is referenced by path and line range only.
