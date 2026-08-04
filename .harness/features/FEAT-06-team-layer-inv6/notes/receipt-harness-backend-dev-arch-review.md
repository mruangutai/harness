# Assertion-feasibility audit — FEAT-06 PLAN at 635ef14

**BLUF:** Two of T-07's ten checks are **not satisfiable as specified**: check (6)/SC-02 breaks its
own "exactly once" invariant the moment the checker embeds the needle literally, and check (8)/SC-14
(and T-11's own second verify) impose a single-**line** predicate on prose the PLAN's own passage
does not fit on one line unless deliberately unwrapped. One more, check (9)/SC-15, is satisfiable
for the two rows it inspects but only if T-08's own added clause is drafted to avoid introducing a
second `∥`-bearing group — nothing in T-08 or T-07 says this, so it is a live risk, not a red flag
that fires today. Everything else audited is RED now and GREEN-reachable by the prescribed work,
including two line-count caps that are tighter than the prescribed content (T-09 clearly over-cap;
T-06 not independently testable, no literal text given). SC-11 is the one SC whose only assertion
is already true today, vacuously.

**Method note:** to test check (6)'s self-counting risk I copied a throwaway `test-team-catalog.py`
into `.claude/skills/harness/bin/`, ran the greps, then deleted it — `git status --porcelain
.claude/skills/harness/bin/` confirmed clean afterward. No other source file was touched; every
other test ran from `/private/tmp/…/scratchpad/`.

## Named suspicions — settled

**1. Panel-group parse (check 9 / SC-15).** Balanced-brace parser in
`/private/tmp/.../scratchpad/panel_parse2.py`, run directly against `docs/harness/SPEC.md` lines
1976-1982 (not hand-transcribed). Row 1978 (ship-feature): 2 `{...}` groups, 1 contains `∥` →
`{code, security, ui}`. Row 1980 (review): 1 `{...}` group, contains `∥` → `{code, qa, security,
ui}`. Both resolve to exactly one panel group — the rule works on rows as they stand.
**After T-08(b)'s minimal rewrite** (panel widened only): 2 groups, 1 with `∥` →
`{code, qa, security, ui}` — matches the review row and matches `review.yaml`'s parsed ids after
T-02. **But T-08(b) also instructs adding a clause distinguishing the segment from the panel step**
(`PLAN.md:529-537`). A natural drafting of that clause restates the panel set in prose — e.g. "...the
panel step re-runs the matrix... `{code ∥ qa ∥ security ∥ ui}` in gate-only mode" — and under that
variant the row now has **3** `{...}` groups, **2** containing `∥`, and check (9) FAILS LOUDLY by
its own rule (correctly — that is the rule doing its job, but nothing in T-08 or T-07 tells the
documentor not to repeat the group). **Finding: check (9) imposes an unstated constraint on T-08 —
the added clause must not introduce a second `∥`-bearing `{...}` group into the 1978 cell.**
Rows other than ship-feature/review are never fed to the ambiguous-group rule (row selection is by
team-name match first), so plan-feature/debug/understand-codebase's zero-group shape is irrelevant.

**2. Build row's lead cell (check 7 / SC-10).** Existing plain cells: debug row conducted-by =
`eng-lead` (`SPEC.md:1979`, no markup); review row = `validator-lead` (`:1980`, no markup). A naive
`cell.strip() == 'eng-lead'` matches those verbatim. **But** `PLAN.md:522` itself writes the value
as `` `eng-lead` `` (backticked), and §13's DAG/notes columns use backticks around agent names
freely — a documentor writing `` | build | `eng-lead` | `` is well within house style. Verified:
`' \`eng-lead\` '.strip() == 'eng-lead'` → `False`; stripping backticks/`**` first → `True`.
**Finding: check (7) must strip backtick/emphasis markup before comparing, or SC-10 is a coin flip
on the documentor's markup choice.** Not specified anywhere in T-07(7) or T-08(a).

**3. Single-line requirement (check 8 / SC-14, and T-11's own second verify).** T-11's prescribed
passage (`PLAN.md:640-645`), written to a scratch file and wrapped at the file's own ~95-col prose
width (matching `SKILL.md`'s existing wrap convention, verified against `SKILL.md:30-45`), produces
6 physical lines. Predicate `all(k in line for k in ('qa','validator','loop_back'))` over those 6
lines: **no line matches** (`qa`/`test_matrix` fall on line 2, `validator` on line 1,
`loop_back` on line 4 — none share a line). Joined into one unwrapped paragraph, all three tokens
co-occur. **Confirmed: as PLAN's own passage would naturally be written in the file's house style,
check (8) and T-11's second verify (`PLAN.md:656-658`, identical single-line predicate) both FAIL.**
Minimum fix demonstrated: a deliberately short, unwrapped sentence — `"The qa step is a
validator-squad segment; on failure it loop_back's to the owning dev."` (86 chars) — satisfies the
predicate on one line. **BRIEF SC-14 asks for "the matching passage" (a multi-sentence unit);
T-07 check (8) and T-11's verify both assert a single *line*.** That gap is doubled — it appears
identically in two places, not one.

**4. Check (6) self-counting (SC-02) — CONFIRMED NOT SATISFIABLE AS NATURALLY WRITTEN.**
Baseline: `grep -rn '"none", "null", "n/a"' .claude/skills/harness/bin/ | wc -l` → `1`
(`validate-digest.py:472`, pre-D-01/T-01). With a throwaway `bin/test-team-catalog.py` containing
`NEEDLE = '"none", "null", "n/a"'` (the natural way to write check (6)'s own grep subprocess call —
every other `bin/test-*.py` embeds its search literal directly) copied in and the same grep re-run:
count → **2** (`test-team-catalog.py:2` plus the original). **Check (6)'s own assertion is "exactly
once"; the checker asserting that count breaks it by existing**, if it spells the needle as a plain
string literal. This is not a hypothetical — it is the natural implementation shape for a
`bin/test-*.py` file. It also **retroactively breaks T-01's verify conjunct (2)** (`PLAN.md:253`,
same grep, same `== 1`): T-01 runs before T-07 in the topological order, so its verify is true when
T-01 executes and **false by the time T-07 lands** — a stale-passing verify, exactly the defect
class this feature exists to close. **Mitigation, so the finding is actionable:** construct the
needle from `harness_yaml.PLACEHOLDER_UNSET` (e.g. `', '.join(repr(x) for x in
harness_yaml.PLACEHOLDER_UNSET)`) rather than as a literal, or have check (6) exclude
`test-team-catalog.py` itself from the scanned set. Neither is in T-07's intent as written.

**5. T-01 / T-09 / T-11 verify commands, run at 635ef14:**
- T-01 (1) `run-unit-tests.sh` → exit 0 **already true today** (non-discriminating, but harmless —
  an AND with genuinely-red conjuncts).
- T-01 (2) `grep -rn '"none","null","n/a"' bin/ | wc -l` → `1` **already true today**
  (non-discriminating on its own; see finding 4 above for how it goes stale).
- T-01 (3) `grep -c PLACEHOLDER_UNSET check-state.sh validate-digest.py` → `0`, `0` — genuinely RED.
- T-01 (4) `grep -c 'review_sha: none'` / `'review_sha: 1ce886a'` on `test-check-state.py` → `0`, `0`
  — genuinely RED.
- T-09 verify (`python3 -c "... all(k in t for k in (...))"`) → **exit 1 at 635ef14**, genuinely RED.
- T-11 first verify (`grep -c -i test_matrix SKILL.md`) → `0`, genuinely RED (matches `>= 1` failing).
- T-11 second verify (single-line predicate) → see finding 3; RED today, and RED-after-naive-write
  too unless the passage is deliberately kept to one line.

**6. Line-count caps.**
- **T-11: feasible.** Its literal prescribed passage, wrapped at the file's own ~95-col convention,
  is **6 content lines**, well inside the ≤8 cap.
- **T-09: over cap as specified.** The prescribed subsection content, wrapped as one paragraph at
  95 cols, is **13 lines**; a heading line plus the blank line markdown requires before it (both
  needed to structure a "short subsection", not optional) brings real growth to **15 lines**.
  Base file is 259 lines (`git show 635ef14:.claude/skills/harness-team/SKILL.md | wc -l`); the
  ≤14-line growth cap ceilings at **273**; 259+15 = **274, one line over**. T-09's own intent target
  ("≤12 lines") is exceeded even in the most compact paragraph form (13 > 12), and the content
  reads as ~6 semicolon-separated bullet items, which — written as an actual bulleted list rather
  than one dense paragraph, the more legible choice — would run longer still, not shorter.
  **Finding: T-09's own two caps (≤12-line target, ≤14-line ceiling) are both under strain from
  the content T-09 itself prescribes.**
- **T-06: not independently testable.** Unlike T-11, T-06's intent describes required content
  ((a)/(b)/(c) points plus the `## You are a PHASE` conditional edit) without a literal quoted
  passage to wrap and count — any figure I produced would be my own drafting, not a measurement of
  what PLAN specifies. Flagging as unverified rather than asserting a number.

**7. SC sweep — every command run at 635ef14 (repo state; each `id | red_now | satisfiable |
evidence`):**

| id | red_now | satisfiable | evidence |
|---|---|---|---|
| SC-01 | yes | yes | `grep -c 'review_sha: none|1ce886a' test-check-state.py` → 0,0; fixtures absent |
| SC-02 | yes | **no, as naturally implemented** | see finding 4 — checker's own literal needle self-counts |
| SC-03 | n/a (inspection) | yes | before-capture is T-01 step 0; not automatable, PLAN/BRIEF both say so |
| SC-04 | yes | yes | `harness_yaml.load_file(review.yaml)` → raises (flow-seq parse error) today |
| SC-05 | yes | yes | `ls teams/` → `gate-probe.yaml review.yaml` (2, but wrong 2 — gate-probe not build) today |
| SC-06 | yes | yes | no fixture-under-`teams/` scanning exists yet (glob is `.harness/**` only) |
| SC-07 | yes | yes | `build.yaml` absent (`test -f` → missing) |
| SC-08 | yes | yes | same — `build.yaml` absent |
| SC-09 | yes | yes | `grep -n build SKILL.md \| grep -i DEC-118` → exit 1 |
| SC-10 | yes | **yes, with a fix** | `grep -c '^| .*\*\*build\*\*' SPEC.md` → 0; check (7) itself needs markup-stripping (finding 2) |
| SC-11 | **no** | yes | `run-unit-tests.sh` → exit 0 **already**, vacuously (no unregistered script exists yet); becomes discriminating only as a side effect of T-07 adding one |
| SC-12 | n/a (inspection) | yes | a reviewer-read claim over PLAN's `execution_mode`/`reason` fields, not a command |
| SC-13 | n/a (uat) | yes | user judgement, not testable |
| SC-14 | yes | **yes, with care** | `grep -c -i test_matrix SKILL.md` → 0; single-line predicate risk, finding 3 |
| SC-15 | yes | **yes, with care** | three sets differ today; panel-group rule risk under T-08(b)'s added clause, finding 1 |

No SC's only assertion was already true at 635ef14 except SC-11, and SC-11's staleness is structural
(it can only ever be discriminating once a new script exists to register), not a planning defect.

## VERDICT

PASS

DIGEST:
  headline: two of T-07's ten checks are not satisfiable as specified (SC-02 self-counts, SC-14's
    single-line predicate rejects the prescribed passage's natural wrap) and a third (SC-15) carries
    an unstated constraint on T-08's own added clause; every other check/SC is genuinely RED at
    635ef14 and reachable by the prescribed work, and SC-11 is the one SC already true today
    (vacuously, harmlessly)
  tests_added: 0
  suite: pass
  blocked_on: none
  open_questions:
    - { id: Q1, question: "check (6)/SC-02: should the needle be constructed from harness_yaml.PLACEHOLDER_UNSET (avoiding a literal string match) or should the scan explicitly exclude test-team-catalog.py? Either closes the self-count; T-07's intent specifies neither.", blocking: true }
    - { id: Q2, question: "check (8)/T-11 verify (2)/SC-14: the predicate requires all three tokens (qa, validator, loop_back) on one physical line, but BRIEF SC-14 describes 'the matching passage' (multi-sentence) and T-11's own prescribed passage does not co-locate them on one line when wrapped in the file's house style. Should the predicate be relaxed to a passage/paragraph match, or should T-11 be told explicitly to keep one unwrapped summary line?", blocking: true }
    - { id: Q3, question: "check (9)/SC-15: T-08(b)'s added clause distinguishing the qa segment from the panel step must not restate the panel set '{code ∥ qa ∥ security ∥ ui}' in prose within the same 1978 cell, or the panel-group rule sees two ∥-bearing groups and fails loudly. Should T-08's intent say this explicitly?", blocking: false }
    - { id: Q4, question: "T-09's own line-count target (≤12) and the file-growth ceiling (≤14, i.e. 273 total lines) are both under strain: the prescribed subsection content wraps to 13-15 lines depending on paragraph-vs-bullet form. Is the cap meant to bind, or is it a target to trim toward during execution?", blocking: false }
    - { id: Q5, question: "check (7)/SC-10: should the SPEC row's 'conducted by' cell comparison strip backtick/bold markup before comparing to build.yaml's plain lead: value, given the rest of §13 uses backticks around agent names freely?", blocking: false }
  files_touched: []
  expertise_update: []
artifact: .harness/features/FEAT-06-team-layer-inv6/notes/receipt-harness-backend-dev-arch-review.md
