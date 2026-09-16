# Goal-check — BUG-1286 plan phase, cycle 4 (post-amendment)

**BLUF: yes — the amended plan delivers the operator's stated intent; all eleven acceptance criteria
are delivered, both operator-selected fixes are closed, and no surviving gap.**

Graded from the current text at worktree HEAD `c040c319` (plan.yaml modified, uncommitted). Every
section below cites the amended text. Prior passes stand as written: c1, c2, and
`notes/review-plan-panel-c3.md` (superseded on the two amended points only).

## 1. The Destination, both negatives

- **Every tracked test-shaped file made to obey `tests/**`** — `BRIEF.md:18-21` (Goal), `:25-26`
  (REQ-01), and the clause that does it: `plan.yaml:304-318` (index-driven clause) with the
  vocabulary at `:273-275` and the shape predicate spelled as literal code at `:282-285`.
- **Product-checkout discovery unchanged** — `plan.yaml:77-97` (D-03: enforcement is scoped by a
  `.git` entry, a toplevel match and index self-ownership); `:309-311` makes a checkout that does not
  ship the predicate contribute nothing; graded by `BRIEF.md:133-139` (SC-16) and asserted by T-01
  case 9 (`plan.yaml:389-393`). Nothing in the plan names a discovery surface: the seven `lanes:`
  rows (`plan.yaml:11-31`) are the predicate, two test files, the census instrument, the audit note
  and the two decision files.
- **Implementation not begun** — `plan.yaml:3` `status: plan`, `:4-5` approval pending; every task
  `status: ready` (e.g. `:258`). `git status --porcelain` in the worktree lists only BRIEF.md,
  plan.yaml, `observations/harness-pm.md` and one untracked note — no implementation, test or config
  file is modified.

**Verdict: delivered, undrifted.**

## 2. The four blocking planning questions

| Q | Settled where | Decisive? |
|---|---|---|
| 1 vocabulary | `plan.yaml:34-65` (D-01, two groups), constants `:273-275`, predicate `:282-285`, "SOURCE_EXTENSIONS applies to RESTRICTED_NAME_PATTERNS ONLY" `:286-291`, census dispositions `:471-476`, DEC-213 text `:564-577` | yes — see below |
| 2 exception contract | `plan.yaml:67-76` (D-02), `:106-118` (D-05), registry self-policing `:319-326`, cases 6-7 `:376-385`, `BRIEF.md:106-110` (SC-10) | yes |
| 3 tracked authority + failure semantics | `plan.yaml:77-97` (D-03), `tracked_paths` `:296-302`, LookupError branch `:306-308`, cases 4/5 `:372-375`, `BRIEF.md:73-76` `:140-143` (SC-05, SC-17) | yes |
| 4 DEC-213 amendment | `plan.yaml:119-127` (D-06), T-05 `:544-608`, `BRIEF.md:121-125` (SC-13) | yes |

**Q1, the one this amendment reopened.** Implementation cannot improvise it: the two tuples and the
extension set are named constants with literal values (`plan.yaml:273-275`), the membership
predicate is given as the exact expression to write (`:282-285`), and `:286-294` forbids both
collapsing the tuples and localising them — T-03 imports the same names (`:461-463`), so audit and
guard cannot diverge. D-01's `because` (`plan.yaml:48-65`) justifies the **split**, shape by shape,
not the old blanket restriction: `probe-*` stays restricted because eight of the nine tracked
outside matches are Markdown/JSONL probe records and `probe-*` is matched by no `detect` glob at
all; `test_*` stays restricted because `detect` reaches it only as `**/test_*.py`, strictly
contained by the source-extension form; the agnostic pair is widened precisely because `detect`
carries `**/*.test.*|**/*_test.*` with no extension filter, so a restricted guard would be narrower
than discovery — the same silently-smaller-suite defect one size down.

**Verdict: all four settled decisively.**

## 3. The eleven acceptance criteria — 11 delivered / 0 partially delivered / 0 not delivered

Traceability table at `BRIEF.md:160-179`. Each AC in the ticket's own order:

| AC | SC | Traced plan work | Grade |
|---|---|---|---|
| 01 rogue tracked file rejected | SC-01 `BRIEF.md:58-60`, SC-02 `:61-66`, SC-18 `:144-153` | T-01 clause `plan.yaml:312-318`, case 1 `:332-366`, case 10 `:394-401` | delivered |
| 02 all paths, deterministic order | SC-03 `BRIEF.md:67-69` | sorted iteration `plan.yaml:317-318`, case 3 `:369-371` | delivered |
| 03 runner refuses before any sentinel | SC-04 `BRIEF.md:70-72` | T-02 case 2's three assertions `plan.yaml:426-431` | delivered |
| 04 enumeration failure is closed | SC-05 `BRIEF.md:73-76`, SC-17 `:140-143` | `plan.yaml:306-308`, cases 4-5 `:372-375`, T-02 case 4 `:434-436` | delivered |
| 05 valid unit/integration/manual accepted | SC-06 `BRIEF.md:77-92`, SC-07 `:93-97` | exact-equality grader `plan.yaml:346-355`; SC-07 on the pre-existing assertion `tests/unit/test-suite-layout.py:105` (verified present) | delivered |
| 06 ordinary support modules accepted | SC-08 `BRIEF.md:98-99`, SC-09 `:100-105` | case 7 `plan.yaml:381-385`; `import layout_fixtures as lf` verified at `tests/integration/test-layout-migration.py:62` | delivered |
| 07 exact documented exceptions; stale/broadened/dup/unnecessary refused, with positive coverage | SC-10 `BRIEF.md:106-110` | policing `plan.yaml:319-326`, negative+positive cases 6-7 `:376-385` | delivered |
| 08 tracked-vs-untracked demonstrated | SC-11 `BRIEF.md:111-113` | case 2 `plan.yaml:367-368`, T-02 case 5 `:437-438` | delivered |
| 09 audit re-run at `review_sha`, complete set, no unexplained match | SC-12 `BRIEF.md:114-120` | T-03 instrument `plan.yaml:441-512`, T-04 note `:513-543` | delivered |
| 10 DEC-213 + index state the shipped invariant | SC-13 `BRIEF.md:121-125` | T-05 `plan.yaml:557-608`; index phrase count verified 0 today, so the verify grep is non-vacuous | delivered |
| 11 product discovery + mutation scope unchanged | SC-14 `:126-127`, SC-15 `:128-132`, SC-16 `:133-139` | `plan.yaml:402` forbids touching `harness.json`/runner; SC-15's pin re-derived: `run_pool.py --mutation-check "$BIN_DIR"` is still the sole invocation and still **line 47** at `c040c319` | delivered |

Counts sum to 11.

## 4. FEAT-44 classification — not weakened, not generalised, not relocated

D-05 as it now stands (`plan.yaml:106-118`) keeps the exact path, keeps "is not relocated", keeps the
consumer reference at `tests/manual/probe-omp-session-accessor.py` lines 54-55 (verified: the `PROBE`
assignment occupies those lines), and keeps the archival coupling **stated with its consequence** at
`:113-117` — verbatim, including "reports 'no longer tracked' on every runner invocation until
suite_layout.py … is edited". Evidence it was untouched by this amendment: `git diff -U0 HEAD` over
plan.yaml contains no added or removed line matching `FEAT-44`, `archiv` or `D-05` outside T-03's
measurement paragraph (`plan.yaml:146-152` of the diff, T-03 rows text). Carried through unchanged
at every touching site: the registry seed `plan.yaml:276-281`, case 1's rebinding rationale
`:356-366`, case 7 `:381-385`, T-04 disposition line `:535-539`, T-05 bullet `:591-594`,
`BRIEF.md:79-82` (SC-06's masking rationale) and `BRIEF.md:187-189`. Panel findings
`PF-5504924547ecd6b632f6cb1f10246055` (med) and `PF-806758dcc7e53f9217d3bfa230b272bf` (low) remain
`open` at their original severities (`plan.yaml:156-172`).

**Verdict: unchanged, as the operator directed.**

## 5. The four out-of-scope entries

| Out of scope | Evidence it is still out |
|---|---|
| redesign product-checkout discovery | `plan.yaml:309-311`, `BRIEF.md:133-139`; no discovery surface in `lanes:` `plan.yaml:11-31` |
| broaden runtime mutation snapshots | `BRIEF.md:128-132`; `plan.yaml:402` |
| rename non-test support modules | `BRIEF.md:100-105`; T-05 keeps "What this does not do" for `layout_fixtures.py` `plan.yaml:595-596` |
| implement during the planning run | `plan.yaml:3-5`; working tree carries no implementation edit |

**`harness.json` untouched — the evidence.** `git diff --stat HEAD -- .harness/harness.json` is empty
and `git status --porcelain` lists only BRIEF.md, plan.yaml, `observations/harness-pm.md` and one
untracked note. The residual is closed from the guard's side alone (`plan.yaml:57-65`,
`BRIEF.md:190-198`), which is exactly the constraint the fix was required to respect: SC-14
(`BRIEF.md:126-127`) still demands zero bytes changed.

## 6. Delivered but never asked for

Nothing out of scope. Two additions are warranted rather than creep: T-03's `--against` comparison
mode, not in the ticket, is the mechanism SC-12/AC-09's "identical fenced row set" needs (panel
`PF-ae6d643363371bf038d536934837962a`, `plan.yaml:214-220`); and SC-18, new this cycle, is not a new
AC but the falsifiable grader for the AC-01/AC-06 split the ticket's Q1 ordered settled
(`BRIEF.md:179`). Route check: `check-plan-routes.py` over this plan reports `0 violation(s)`.

## Closure of the two operator-selected fixes

| Fix | Closed? | Citation that proves it |
|---|---|---|
| **1 — T-03 `--against` output contract** | **closed** | `plan.yaml:478-489`: the fenced row block and the `TOTAL <n> OUTSIDE <n> VIOLATIONS <n>` line print "on EVERY invocation, with `--against` and without it", "BEFORE any comparison or verdict output", nothing about `--against` "suppresses, truncates, filters or replaces either", and a diff-only implementation is named as violating the task. `:493-503` makes MISSING/EXTRA additive and states the combined exit rule. **T-04's `verify:` read literally** (`plan.yaml:524`): `out=$(… --against <note>)` takes the census exit status, which is 0 iff the note's rows equal the measured rows **and** no violation row exists; on a correct note over a clean tree that is 0, and `printf … \| grep -q 'probe-session-accessors\.ts.*documented-exception'` then matches because the FEAT-44 row is a `documented-exception` row (`:470`) inside a block that prints unconditionally. Under no spec-compliant reading can it fail on a correct note. |
| **2 — the `unit.detect` residual** | **closed, not reworded** | The old blanket claim is gone, not restated: D-01 scopes the extension policy to "group one within that clause alone" and denies it is repository-wide (`plan.yaml:41-47`); T-01 states "SOURCE_EXTENSIONS applies to RESTRICTED_NAME_PATTERNS ONLY" (`:286-291`); T-05 forbids writing that the restriction "covers the whole vocabulary, or that it holds everywhere" (`:574-577`). A grep of BRIEF.md for `extension`/`residual`/`detect` returns no surviving blanket assertion — `BRIEF.md:190-198` now reads "No residual remains on this surface" and gives the two reasons. **Falsifiable, named grader:** SC-18 (`BRIEF.md:144-153`), `verify: automated  evidence: unit`, naming T-01 case 10 and case 8. **Both directions asserted:** agnostic pair refused at a NON-source extension — case 10 tracks `.harness/tools/session_test.md` and `.harness/evidence/run.test.jsonl` and requires each to be named by its own finding (`plan.yaml:394-401`); `probe-*` at a NON-source extension NOT refused — case 8 requires `probe-something.md` to produce no finding while `probe-something.py` does (`:386-388`). SC-18's "what fails it" clause rejects a one-directional assertion, either direction stated only as the other's negation, and a single merged case. |

The only text still describing the residual as merely disclosed is inside the `panel:` block
(`plan.yaml:194`, `:202-203`, `:232-234`) — a verbatim cycle-3 transcription that the amendment
supersedes and that must not be edited (`plan.yaml:133-136`). Advisory, not a gap.

## Independent census re-measurement

Re-measured with a **different enumeration than the amendment note used** — `git ls-tree -r
--name-only HEAD` (the plumbing T-03 itself mandates, `plan.yaml:466`) rather than the note's
`git ls-files`, at `c040c319`, with `fnmatch` over both pattern tuples:

```
python3 -c "import subprocess,fnmatch,os; paths=git ls-tree -r --name-only HEAD;
  R=('test-*','test_*','probe-*'); A=('*_test.*','*.test.*');
  sel=basename matches R+A; out=[p for p in sel if not p.startswith('tests/')];
  ag=[p for p in out if matches A]"
```

Result: `TRACKED 2693`, `TOTAL 85`, `OUTSIDE 9`, **`AGNOSTIC_OUTSIDE 0`**. The 9 outside rows are the
FEAT-44 `.ts` documented exception plus eight `probe-*` Markdown/JSONL records — all nine match
`probe-*` only, none matches an agnostic pattern. Exactly **one** tracked path anywhere matches the
agnostic pair, `tests/unit/omp-hooks.test.ts`, and it is inside the test tree (`in-tests-tree`), so
it is also a live positive control that the widened shapes match something real.

**Widening `*_test.*` and `*.test.*` to any extension creates no new violation and changes no row's
disposition** — my own measurement, matching `plan.yaml:505-512` and `BRIEF.md:199-205`. Nothing to
report to the operator.

## Surviving gaps

**No surviving gap.** Two advisory observations, neither gating and neither requiring a plan edit:

1. T-03 does not say what the `--against` parser does with a fenced line that is not
   `path<TAB>disposition`. The contract places `TOTAL` after the block (`plan.yaml:489`), so a
   compliant note cannot contain one — implementation latitude, correctly left weak.
2. The `panel:` block's cycle-3 residual findings now read as superseded history; that is by design
   under the transcription rule and is the orchestrator's routing note, not a defect.
