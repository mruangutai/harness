# A-4 — SC-01 redraft after the user's ruling (FEAT-08)

**BLUF.** A-4 is drafted in both signed artifacts. **SC-01 is now REACHABLE, conditional on two
main-session-direct follow-up edits landing** — it does not pass at `5ce3b13`. A-2 is marked
SUPERSEDED BY A-4 in place. **One correction to the dispatch's own premise:** the cited
replacement-coverage anchor is two comment lines, not assertions; the real coverage was measured and
is thinner than claimed. The ruling still holds.

## The 6 → 4 decomposition (the central claim)

`git grep -ln <5 tokens> 5ce3b13 -- .claude/ docs/ .harness/harness.json .harness/team-config.yaml
.harness/README.md` → **6**, and the working-tree grep with `--exclude-dir=worktrees` returns the
same 6 (two independent methods, one tree — not the `6 == 6` cross-SHA coincidence A-2 warned about).

- **4 survivors:** `DECISIONS.md`, `DECISIONS-INDEX.md` (REQ-06/constraint 3);
  `BUILD.md`, `SPEC.md` (every hit carries the `(cost-report.py removed — DEC-178)` marker — verified
  at BUILD `:191/:224/:225/:333/:578`, SPEC `:2129` — which **SC-14 mandates**).
- **2 that leave — verified by ENUMERATING every hit, not by arithmetic:**
  `bin/test-validate-digest.py` → `:749`, `:753`, **`:769`**; `bin/test-check-state.py` → `:205`,
  `:326`. **`:769` is the trap:** it is the comment on the fixture that SURVIVES and it carries the
  literal `cost_usd`. Deleting the pin alone leaves the file in the sweep and re-creates A-2's
  defect. T-01's amendment therefore requires TWO edits — delete the pin case, and reword `:769` off
  the literal spelling, which is the repo's existing house style (`check-state.sh:331-334`,
  `validate-digest.py`'s orchestrator schema comment).

Discriminating: **18 at `ae2443d`, 14 of them outside the four-file set** (re-derived, not relayed).

## Worktree flag

`78` without the flag / `6` with, working tree at `5ce3b13`. **78 is not SHA-pinnable** —
`.claude/worktrees/` is gitignored (`.gitignore:21`). The flag is a **no-op at `ae2443d`** as a fact
about the disk: `ae2443d` committed `2026-08-05T06:06:25-07:00`; `.claude/worktrees/FEAT-09` born
`Aug 5 07:02:15 2026`. The 18-file base measurement stands.

## REQ-04 disposition — a ruling on a requirement, not just a criterion

SC-04's second half ("a return still carrying it is also accepted") is dropped with its fixture.
REQ-04's second clause is **retired by the ruling** — with zero producers there is no in-flight run
to break. Pointers added at `BRIEF.md` REQ-04, SC-01, SC-04 and the settled fact; **no signed text
overwritten**. **D-01 is unamended**: tolerance is structural and still what makes removal safe.

## The correction — dispatch §C does not hold

`test-validate-digest.py:1213` / `:1233` are **comments**. `:1212-1215` explains a case was green at
SHA `4091b36` because `task` was then unknown (it is in the dev schema now); `:1232-1234` names
"unknown key ignored" as the **bad** shape its detector rules out.

Measured instead: a strict-unknown-key **mutant** of `validate-digest.py` (from `git show 5ce3b13:`,
`headline`/`artifact` allowed since they are checked outside the schema map) run through the real
suite via `VALIDATE_DIGEST_BIN` → **2 FAILING**:
1. `orchestrator digest with the reconciled schema` — the pin. The only **deliberate** assertion.
2. `[hook] DEC-156: … a dev's artifact is not read` — its dev payload carries `branch: none`, a
   lead-only field (`validate-digest.py:165`). **Incidental.**

**Residual: after the pin is deleted, the suite asserts unknown-key tolerance only incidentally.**
Behaviour safe, coverage thin. No test was added — that is new mandate beyond the ruling. Raised as
Q1.

## Falsifiability closure

T-02's `verify:` clauses check `check-state.sh`, not `test-check-state.py`, so nothing in T-02
catches the prose rewording. **The amended SC-01 (superset-prohibited, subset-allowed) is the
falsifier for both follow-up edits.**

## Open questions

- **Q1 (non-blocking):** add one orchestrator fixture carrying `bogus_extra_key`, asserted accepted,
  to replace the pin's coverage generically? Cheaper than the pin and not cost-shaped. User's call.
- **Q2 (non-blocking):** the two follow-up edits (`test-validate-digest.py` pin deletion;
  `test-check-state.py` `:205`/`:326` rewording) are **outstanding, main-session-direct**. SC-01 fails
  until both land.

## Not touched

SC-14, D-07, T-10, T-11, D-01–D-10, A-1, A-3 (its "SPEC.md is already among the six" conclusion holds
— the six becomes four and SPEC.md remains in it). No renumbering, no `## Approval`, no commit, no
`cost:` block.
