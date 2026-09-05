# Goal-check — plan phase, cycle 7 (after the operator's THIRD signature-gate amendment)

**BLUF — does this plan deliver the operator's stated intent? YES: all six clauses of the third
ruling are closed in the current text, all seven cycle-6 findings are closed by contract, my
independent STEP 0 reproduces `tracked=2706 / counted-outside-tests=0` exactly, and an exhaustive
search over 108,510 candidate `detect` widenings found no mutant that defeats the rebuilt case 11 —
with one surviving gap: a legitimate detect NARROWING reddens case 11's tripwire assertion.**

## 1. Destination and both negatives — MET

Destination (`grilling…2026-09-04.md:4`) = an approved BRIEF and plan, no product-checkout
discovery change, no implementation begun. `plan.yaml:3-5` `status: plan`, `approval.status:
pending`; `BRIEF.md:271-275` pending. Negative 1 (discovery unchanged): D-03 (`plan.yaml:110-130`),
SC-16 (`BRIEF.md:152-157`), T-01's self-ownership bullet (`plan.yaml:426-428`) and case 9
(`plan.yaml:506-510`). Negative 2 (not implemented): `git status --short` at `cab6adb2` shows only
`BRIEF.md`, `plan.yaml`, `observations/harness-pm.md` modified and one untracked note — no
implementation, test, decision or config file.

## 2. The four blocking planning questions — all still settled decisively

| # | ticket question | settled at |
|---|---|---|
| 1 | authoritative vocabulary, extensions, probe records | D-01 `plan.yaml:34-98`; REQ-09 `BRIEF.md:40-50`; SC-18 `BRIEF.md:163-172` |
| 2 | exception contract + FEAT-44 classification | D-02 `plan.yaml:100-109`, D-05 `plan.yaml:139-151`; SC-10 `BRIEF.md:117-121` |
| 3 | tracked authority + fail-closed semantics | D-03 `plan.yaml:110-130`; SC-05/SC-17 `BRIEF.md:84-87,159-162` |
| 4 | DEC-213 amendment + index regeneration | D-06 `plan.yaml:152-160`; T-05 `plan.yaml:812-888` |

The plan's own `panel.open_questions` Q1 ("which matcher semantics does *counts* denote?",
`plan.yaml:334-343`) is now **answered by measurement and by contract** — D-01 GOVERNING SEMANTICS
(`plan.yaml:48-61`) names `code_grade._is_test_path` as the sole mechanical consumer and REQ-09
restates the obligation in those terms. Q2 (F-01's *severity*) is untouched and remains the
operator's `sign-approval --overrule`; that is a ruling, not a planning gap.

## 3. Eleven acceptance criteria — 11 mapped, 11 delivered, 0 partial, 0 not delivered

`BRIEF.md:213-233` maps every AC-01…AC-11 to at least one falsifiable SC, and every SC traces to
work: AC-01→SC-01/02/18/19 (T-01), AC-02→SC-03 (T-01 case 3), AC-03→SC-04 (T-02 case 2),
AC-04→SC-05/17 (T-01 cases 4,5; T-02 case 4), AC-05→SC-06/07 (T-01 case 1), AC-06→SC-08/09/18
(T-01 cases 8,10), AC-07→SC-10 (T-01 cases 6,7), AC-08→SC-11 (T-01 case 2), AC-09→SC-12 (T-03,
T-04), AC-10→SC-13 (T-05), AC-11→SC-14/15/16. No AC rests on a null-runner kind
(`BRIEF.md:237-243`).

## 4. FEAT-44 classification — carried through, not weakened

D-05 `plan.yaml:139-151` (exact path, not relocated, consequence stated); seeded registry entry
`plan.yaml:384-389`; live-registry load-bearing case 7 `plan.yaml:498-502`; audit disposition
`plan.yaml:803-807`; DEC-213 text `plan.yaml:871-874`; both T-03/T-04 `verify:` blocks anchor on
that row (`plan.yaml:680-681, 774-775`).

## 5. Four out-of-scope entries — undrifted

`BRIEF.md:61-63` carries the ticket's three verbatim; the fourth ("no implementation this run") is
held by `status: plan`. `harness.json` untouched — SC-14 `BRIEF.md:145-146`, T-01's closing line
`plan.yaml:630-631`, and measured: it is absent from `git status`. Product-checkout discovery
unreached — section 1's negative 1. Mutation-snapshot scope unwidened — SC-15 `BRIEF.md:147-151`.

## 6. Anything delivered the intent never asked for — none

REQ-09/SC-19 exceed the ticket's letter, but the operator ratified that surface in all three
signature-gate rulings. T-03's `--ref`/`--against` instrument is AC-09's own "instrument anyone can
re-run". No task touches a surface outside the seven `lanes:` rows.

## The operator's THIRD ruling, clause by clause

| # | clause | verdict | citation |
|---|---|---|---|
| 1 | REQ-09 keeps BROAD intent, not narrowed to basename-only | CLOSED | `BRIEF.md:40-50` — all running kinds, full-relative-path `fnmatch`, superset + probe rule |
| 2 | F-01 FIXED not overruled: normalized prefix, `..` rejected outright | CLOSED | `plan.yaml:563-569` (reject before any compare); red case (i) `plan.yaml:608-614`; measured RED below |
| 3 | contract re-based on actual `fnmatch` semantics AND probe source-name rule retained | CLOSED | D-01 `plan.yaml:48-61` + `:58-60`; REQ-09 `BRIEF.md:46-48`; T-05 `plan.yaml:841-853` |
| 4 | permanent assertion exercises the real matcher; RED on both escape and non-final wildcard; no final-segment synthesis, no cardinality pin | CLOSED | `plan.yaml:519-604`; measured GREEN/RED/RED/RED below |
| 5 | SC-12 / T-03 / T-04 separate zero-block from multi-block; exit 2 not globally reserved | CLOSED | `BRIEF.md:132-138`; `plan.yaml:728-739`; `plan.yaml:793-801` |
| 6 | case 11 survives repaired (F-07 KEEP honoured) | CLOSED | `plan.yaml:519-631` — rebuilt in place, "This case is ADDITIVE" `:628-629` |

## F-01…F-07 closure

| F | sev | closed | citation |
|---|---|---|---|
| F-01 | high | mechanism CLOSED (severity ruling still the operator's, Q2) | `plan.yaml:563-569`, red case (i) `:608-614` |
| F-02 | med | CLOSED | D-01 `plan.yaml:48-61`; case 11 SHARED SETUP `:523-535` |
| F-03 | med | CLOSED — cardinality struck, replaced by partition + non-empty bucket | `plan.yaml:598-604` |
| F-04 | low | CLOSED — same edit | `plan.yaml:598-604` |
| F-05 | low | CLOSED | `BRIEF.md:132-138`; `plan.yaml:728-739` |
| F-06 | low | CLOSED — reserved-exit-2 claim removed and forbidden | `plan.yaml:738-740`, `:799-801` |
| F-07 | info | HONOURED — repaired, never deleted | `plan.yaml:519-631` |

## Independent STEP 0 — reproduced exactly

Command, verbatim (throwaway written to `/tmp/bug1286_c7_probe.py`, self-deleted via `os.remove`):

    python3 /tmp/bug1286_c7_probe.py

Operative core: `sys.path.insert(0, ROOT + "/.claude/skills/harness/bin"); import code_grade`,
`TK = json.load(open(ROOT + "/.harness/harness.json"))["test_kinds"]`,
`tracked = git ls-files -z (cwd=ROOT)`,
`[p for p in tracked if not p.startswith("tests/") and code_grade._is_test_path(p, TK)]`.

    STEP0 tracked=2706 counted-outside-tests=0   (HEAD cab6adb2)
    running kinds: handoff_comprehension, integration, omp_session_accessor, unit
    CTRL True .harness/tools/test_dir/gen.py | True .harness/tools/x.test.md
    CTRL True docs/a/b/test_x.py | False .harness/notes/probe-a.md | True .harness/tools/test_rogue.py

**Agrees with the amendment's recorded measurement.** No finding.

## The sufficient-condition substitution — (a) TRUE, (b) SOUND, (c) residual CARRIED

(a) **TRUE.** On the unmutated `detect`, `**/test_*.py` certifies GUARD-COVERED (core `test_*.py`
carries no `/`) while `_is_test_path` returns True for `.harness/tools/test_dir/gen.py`, whose
basename `gen.py` the vocabulary cannot refuse (positive control above). So the universal form is
already false on today's own value; a hygiene half asserting it could never be green.
(b) **SOUND.** It is a shape test that fails loudly on anything uncertified, and it gives up
exactly one class: a directory-component match. Both sites state that limit
(`plan.yaml:575-590`, `BRIEF.md:187-195`).
(c) **CARRIED, measured.** Corrected prototype over RUNNING kinds only:
unmutated GREEN; `tests/../evil/**` RED (`..` rejected); `**/test_*/**` RED (core spans `/`);
`**/*.spec.*` RED (escaping `x.spec.y`, `x.spec.tsx`, `x.e2e.spec.ts`). Every hygiene-GREEN widening
that actually counts real non-shaped paths is caught behaviourally — `**/*t.md` counts 82,
`**/a*.md` counts 104, both RED via the behavioural half over the real tracked set. **No class is
missed by both halves**; the residual is a timing property only (caught on the commit that adds the
file rather than on the `detect` edit), which is what `BRIEF.md:255-261` discloses.

## Attempt to defeat case 11 — failed

Exhaustive: 108,510 candidate single-segment cores generated from every `/`-suffix of all 2,706
tracked paths (prefix/suffix lengths 0-8), each appended to `unit.detect` as `**/<core>` and graded
against the full rebuilt case 11. **Survivors that are case-11 GREEN and newly count a real
outside-`tests/` path: 0.**
Named mutants tried and measured: `**/test_*.p*` → **GREEN but counts nothing new (n=0)** — the
closest miss, and it opens no live gap; `**/probe-*.py`, `**/test-*.py`, `**/x_*.py` → GREEN, n=0;
`**/*t.md` → **RED** (82 offenders); `**/a*.md` → **RED** (104). No fourth green mutant exists on
this tree.

## Stale-text check — six sites, all current

D-01 `because` `plan.yaml:62-98` (withdrawal explicit, residual assigned to the behavioural half);
BRIEF `## Verification gaps` closure bullet `BRIEF.md:244-254` and residual bullet `:255-261`;
T-05's DEC-213 bullets `plan.yaml:841-853`; SC-06's exact-equality assertion `BRIEF.md:88-103`
matching T-01 case 1 `plan.yaml:463-472` (one-element list, agnostic pair deferred to case 10);
T-03/T-04 `verify:` blocks `plan.yaml:680-681, 774-775`; AC table `BRIEF.md:213-233` (19 rows, all
11 ACs). No stale text found.

## Surviving gaps

1. **A legitimate `detect` NARROWING reddens case 11.** Case 11's tripwire assertion
   (`plan.yaml:554-559`) requires `offenders(synthetic + ".harness/tools/test_dir/gen.py") ==
   [".harness/tools/test_dir/gen.py"]`, which holds only while some pattern counts that path.
   Measured: dropping `**/test_*.py` from `unit.detect` gives `trip=[]` → **RED**, with no invariant
   broken and no gap opened (narrowing discovery cannot escape the guard). This is the same species
   as the excused-cardinality pin F-03/F-04 struck — a property of today's `detect` value pinned
   inside the assertion — and the stated three-item remedy (`plan.yaml:624-627`) covers none of the
   three legitimate responses. Dropping `**/*.test.*` instead stays GREEN, so the exposure is
   specific to whichever pattern reaches the synthetic directory-component path.
2. **Advisory, not a defect: activating any null-runner kind reddens case 11.** Measured with
   `status` flipped to `active`: `component` RED (3 uncertified), `ui` RED (`e2e/**`,
   `**/*.e2e.spec.ts`), `typecheck` RED (`**/*.ts`, `**/*.tsx`, and behaviourally the FEAT-44
   documented exception becomes a counted offender). For `typecheck` the red is a TRUE positive
   under REQ-09; for `component`/`ui` it is anticipatory. Consequence worth stating where the
   operator signs: the DEC-163 dev-ops task that adds a `ui` or `typecheck` runner will be blocked
   until the vocabulary is widened or DEC-213 records the scope. Nothing in the plan discloses this.

Both are reported, not applied. Neither is a `panel:` edit and neither changes an approval.
