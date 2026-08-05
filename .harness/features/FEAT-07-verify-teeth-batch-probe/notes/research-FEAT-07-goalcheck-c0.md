# Goal-check — FEAT-07 · review_sha `70b0ed3`

> **Path note.** The dispatch named `notes/goalcheck-harness-pm-c0.md`; `check-domain.sh` BLOCKED it
> (`harness-pm` is granted `notes/research-FEAT-*.md`, not `notes/goalcheck-*.md`). Written here
> instead. Raised as Q1 — the grant, not the hook, is what would have to change.

**13 of 18 met, 4 partial, 1 carved out. FAIL.** Four gaps across **two lanes**: three are fixture
cases in `test-validate-digest.py` (main-session-direct, DEC-174 carve-out) and the fourth, SC-07, is
markdown rule surfaces split between the main session and `harness-documentor` (`docs/harness/SPEC.md`,
`team-config.yaml:116`). **Route as two dispatches in one cycle, not one.**
Method split re-derived from each criterion's own `verify:` line: **11 automated/unit + 7 inspection**,
matching BRIEF `## Verification gaps`.

Suite at `70b0ed3`: `run-unit-tests.sh` exit 0 — `60/60 CLI cases passed`, joint-hint case `ok`,
`14/14 hook`, `2/2 template`, `PASS test-validate-digest.py` (captured to file, not tailed).

## Gaps 1-3 — all in `.claude/skills/harness/bin/test-validate-digest.py` (one lane)

| SC | What is missing | Fix |
|---|---|---|
| SC-03 | The **`fail` half** of "n/a **or** `fail` rejected for dev-ops". Only `:1117` (`n/a`) is fixtured. Validator is CORRECT — I ran it: dev-ops `task: T-01` + `task_verify: fail` + `PASS` → exit 1, `task_verify='fail' reports a gate as FAILED…`. `GATE_FAIL_VALUES["dev-ops"]["task_verify"]="fail"` (`validate-digest.py:110`). Fixture-only gap. | One `case()`: dev-ops `task: T-01` + `task_verify: fail` + `VERDICT: PASS` → `False`, mentions `task_verify` |
| SC-18(a) | Its second sentence — the message "must state that what is rejected is a placeholder ALONGSIDE `VERDICT: PASS`, not that placeholders are disallowed". The hint DOES say it (measured), but `:1299`'s mentions list is `["task_verify","pass","fail","!genuinely not applicable"]` — nothing asserts the pairing wording, so a rewrite to "placeholders are disallowed" stays green. | Add a positive mention at `:1301`, e.g. `"ALONGSIDE"` or `"VERDICT: PASS"` |
| SC-05 | `documentor` is named in the criterion's persona list and has **no fixture in the file at any commit** (`grep -n harness-documentor` → 0 hits). qa `:1174`, reviewer `:1280`, lead `:121`, orchestrator `:741` all covered. Lowest severity of the three. | One `case()`: a `harness-documentor` digest carrying neither field → `True` |

Same lane as T-01 (`main-session-direct`, DEC-174 carve-out). All three are the **same axis the panel
already found once** — a criterion enumerating N clauses, fixtured for fewer than N (its Q2, SC-06
1-of-4). It recurred twice more.

## Gap 4 — SC-07, an inspection PARTIAL, and it is the one that spans two lanes

SC-07 requires four surfaces to name both fields **"together with the rule that binds them:
`task_verify` is required only when `task` names a real task"**. That rule is stated in prose on
**exactly one**: `docs/harness/SPEC.md:1066-1068` (dev-ops bullet). Absent from
`harness-digest-dev/SKILL.md:21-25`, `harness-dev-ops.md:75-81`, `harness-tdd-enforcement/SKILL.md`
and SPEC's eng-devs bullet (`:1054-1055`, a bare field list). `grep -rn 'required only when|omit this
field entirely'` over `.claude/` + `docs/` returns only validator source, never a rule surface.

**Outcome if left:** a dev on a no-PLAN-task dispatch reads `harness-digest-dev`, sees
`task_verify: pass|fail|n/a` listed as required with no omission escape, writes `task: none` +
`task_verify: pass`, and is REJECTED by the very conditional the surface never mentioned — REQ-07's
own defect ("no site is left stating the superseded field set") one clause over. PLAN T-02's intent
specified the line `# Omit this field entirely when task: none — there is no command.`; it is not in
the file. **Surfaces to change, by lane:**
- *main session* (ungranted paths, PLAN lane table line 13) — the comment line in
  `harness-digest-dev/SKILL.md` after `:25`, the matching one in `.claude/agents/harness-dev-ops.md`
  after `:81`, and a clause in `harness-tdd-enforcement/SKILL.md` §"Your task's `verify:` and its
  receipt".
- *`harness-documentor`* (`team-config.yaml:116`, PLAN lane table line 11) — `docs/harness/SPEC.md`
  §8.1 **eng-devs bullet** `:1054-1055`, which SC-07 names explicitly and which is a bare field list.
  The dev-ops bullet `:1063-1068` is already correct and must not be touched.

## SC-11 — reading taken, and the residue

I took the **operational reading the criterion supplies inline**, not a commit count. Measured:
`git log main..70b0ed3 --` over both files returns **two** commits, `d6fa0a8` and `70b0ed3`; between
them `4fce46f`/`4e2b57f`/`3a81701`/`29b612e` leave both files byte-identical (`git diff --stat` empty
at each). Suite run in a detached worktree at `d6fa0a8`: **exit 0, `57/57 CLI cases passed`**; at
`70b0ed3`: exit 0, 60/60. So there is no commit at which the two files disagree about the field set.
**Named residue:** the literal "ONE commit" reading is false — there are two — but each carries BOTH
files together, so the invariant the clause exists to protect never broke.

## SC-12 — carved out, per the orchestrator's ruling

Reporting half: `harness-documentor` executed T-09 and holds no `notes/receipt-*` write grant
(`team-config.yaml:144,158,171,184,199` grant it to the five dev specialists only). Confirmed by
absence: the feature's `notes/` holds `receipt-harness-backend-dev-arch-review.md` and no documentor
receipt. Not a build defect — no agent could have satisfied it as written.
Other half measured and **clean**: `DECISIONS.md:4738/4837/4859` (DEC-175/176/177), index rows
`DECISIONS-INDEX.md:195/196/197`, and `gen-decisions-index.py` re-run → `git diff` on the index is
**0 lines**. Substance captured: precondition ran pre-edit, exit 0, index clean, nothing absorbed.

## Verified, no action

- **SC-16 re-measured, not inherited.** `70b0ed3` deletes the duplicate from `harness-digest-dev`
  (diff read). Bare `grep -rln 'receipt'` over `.claude/skills/*/SKILL.md` + `.claude/agents/*.md`:
  three files — `harness-handoff` (the PATH, D-06's intended split), `harness-expertise` (unrelated
  sense), `harness-tdd-enforcement:110-123` (the only REQ-08 content clause). `grep -ln
  harness-tdd-enforcement .claude/agents/*.md` → exactly the five dev specialists. **The `task: T-NN`
  scoping clause is SATISFIED, not soft:** it is scoped by its own premise — "Your dispatch carries
  the task's `T-NN` id and its `verify:` command" (`:115`) — so a `task: none` dispatch never
  triggers it, and `:91-93` states that distinction explicitly in the same file. This is the contrast
  that makes SC-07 partial and SC-16 met: SC-07's omission causes a wrong action (a dev writes
  `task_verify: pass` and is rejected); SC-16's implicit scoping causes none.
- **SC-05's documentor clause is falsifiable, so the partial is a real gap and not a category error:**
  `documentor` has its own `SCHEMAS` entry (`validate-digest.py:153`) and `ALIAS` row (`:181`). It is
  still the lowest-severity of the four — a leak into that schema would also have to escape the qa,
  reviewer, lead and orchestrator cases that ARE fixtured.
- **SC-07's field blocks survived the SC-16 deletion** — `git show 70b0ed3 -- harness-digest-dev`
  removes only the receipt paragraph, nothing else.
- **Neither ACCEPTED residue is re-reported as a defect.** `dev-ops` `suite: fail` + `PASS` accepted
  (D-03) is pinned by `:1262` and is correct at this SHA. `task: none` self-declaration is unchanged.
