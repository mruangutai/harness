# Receipt — harness-documentor — T-13 (record the decision, regenerate the index)

**DEC-199 is appended and the index row carries its ruling. The verify block as signed cannot pass:
`gen-decisions-index.py` has no `--check` flag.** The equivalent documented check —
`--stdout | diff - .harness/harness/docs/DECISIONS-INDEX.md` plus the same token asserts — exits 0.

## What was written

- `.harness/harness/docs/DECISIONS.md` — ONE entry appended at the end, `## DEC-199`, **60 lines**,
  heading carries the literal `harness_merge`. 61 insertions, 0 deletions: no other entry touched.
  DEC-198 was the last entry at `016be31`, so 199 is the next free number.
- `.harness/harness/docs/DECISIONS-INDEX.md` — regenerated with `gen-decisions-index.py`. One row
  added. **The ruling text right of ` :: ` is hand-written by design**, not generated: the
  generator's usage text says "everything right of ' :: ' is hand-written and preserved verbatim
  across regeneration", and its module docstring says the author writes the ruling in the same commit
  that appends the entry. A new heading with no authored ruling regenerates as `⚠ RULING PENDING`,
  which would have failed the verify's index-row assert. Nothing left of ` :: ` was hand-edited.

## The five approved items, and where the late facts landed

Item 2 carries both lock divergences — the `O_EXCL`→`flock` rewire of `expertise-merge.py`, and the
non-uniform deadline (registry 1.0s, the four file-merge callers 10.0s, `timeout` optional on
`acquire`/`locked_update`), on DEC-193's "one shared implementation, divergences recorded" precedent.
Item 4 carries the registry root (hook payload `cwd`, one registry per worktree, same precedence in
both hooks) as the reason "on one checkout" is true, and the escape hatch as **exercised, not
hypothetical** — that clause survived the 60-line cap only in short form; the leaked-claim incident
detail was cut, the "exercised" claim was not.

## Verified before it was written

- `validate-digest.py:703` is the `RANK = {"PASS": 0, "FAIL": 1, "ESCALATE": 2, "BLOCKED": 3}` line.
  Cited alone; 702 and 705 are not cited.
- `harness_merge.py:36` `LOCK_TIMEOUT_SECONDS = 10.0`; `inflight_registry.py`
  `LOCK_TIMEOUT_SECONDS = 1.0`, `CLAIM_TTL_SECONDS = 3600`, `SINGLE_FLIGHT_AGENTS = ("harness-pm",)`
  — hence "today the product manager alone" rather than a plural set the code does not hold.
- All four consumers import `harness_merge`; `dispatch-guard.sh` is the `PreToolUse` Task hook and
  `validate-digest.py --hook` the `SubagentStop` hook, per `.claude/settings.json`.
- `148c8c5` exists; `runs/2026-08-21-2-product/digest.md:28` is occurrence 8's write-up; run dirs are
  gitignored (`.gitignore:7`, confirmed with `git check-ignore -v`).
- DEC-90's entry **and** its index row both carry the 2026-08-21 strike under DEC-188. The branch is
  not behind on that point. Nothing in DEC-199 mentions DEC-90.
- `BRIEF.md` line 16 still reads "seven measured occurrences" — untouched, and the entry says so and
  names which document is authoritative for what.

## Left out on instruction (not decided here)

`claim()`'s contention-raise correction and the guard's check ordering are absent, and the entry says
nothing that implies either — no claim about what can or cannot make a claim fail, and no ordering of
the model check against the claim step. Both are raised as open questions instead.
