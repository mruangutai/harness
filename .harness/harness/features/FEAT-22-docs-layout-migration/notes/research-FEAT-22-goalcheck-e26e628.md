# Goal-check — FEAT-22 · pinned e26e628 · 10 met, 2 unmet

> Path note: the dispatch named `notes/goalcheck-FEAT-22-e26e628.md`; `check-domain.sh` denies that
> path to harness-pm. Written to an owned `notes/research-FEAT-22-*.md` path instead, per the rule
> that a dispatch does not override the guard. Grant gap raised as an open question.

**FAIL, and both misses are one-line content fixes a retry can make true — not a plan-level
problem, not a code defect.** Ten criteria met. SC-10 and SC-12 are unmet, each because a live
sentence says something false, and each fixable in one edit. Recommend ONE consolidated cycle
(10/10) rather than shipping with the goal missed. Range re-confirmed: `0f12f14..e26e628` = 5
commits, 32 files.

## Verdicts

| SC | verdict | method used | evidence |
|---|---|---|---|
| SC-01 | met | inspection | `git ls-tree -r e26e628 -- docs/harness/` → 0; `.harness/harness/docs/` → BUILD, DECISIONS-INDEX, DECISIONS, SPEC, org.html |
| SC-02 | met | automated/unit | `test-layout-migration.py` case 21 `:398-399`, positive containment on real root |
| SC-03 | met | inspection | boundary note PRE-MOVE (`HEAD 0f12f14`) and POST-MOVE (`1246b06`) both `features: CLEAN — evidence migrated`. **Before-half is not re-observable** — the pre-move tree is gone; graded by inspection of the committed capture (landed 5faa832) |
| SC-04 | met | inspection | one commit `e6e74c8`, 5× R098–R100 renames; **`git ls-tree -r e6e74c8 -- docs/harness/` returns 0 entries** — the tree clause, not just the rename list |
| SC-05 | met | automated/integration | `test-check-domain.py:795-802` live `--resolve .harness/harness/docs/SPEC.md` → `harness-documentor` |
| SC-06 | met | automated/integration | qa DIGEST: regeneration-identity test green; header literal `.harness/harness/docs/DECISIONS.md` at `gen-decisions-index.py:76` |
| SC-07 | met | automated/unit | qa DIGEST: `run-unit-tests.sh --kind unit` exit 0, 15/15, 707 sub-assertions |
| SC-08 | met | automated/integration | qa DIGEST: `--kind integration` exit 0, 12/12, 652+ sub-assertions |
| SC-09 | **met, with a labelling defect** | automated/unit | see §1 |
| SC-10 | **unmet** | inspection | see §2 |
| SC-11 | met | inspection | see §3 |
| SC-12 | **unmet** | inspection | (a) met, (b) failed — see §4 |

## 1. SC-09 — behaviour proven, evidence entailed not named. Remedy one line.

**Failure shape 1: unproven labelling, not unproven behaviour.** The declared unit kind *can*
redden on the failure SC-09 guards — case 21 requires `docs: CLEAN — evidence migrated`, and cases
11/16 prove that string cannot fire on zero evidence. Detection exists inside the declared kind; a
*named* assertion does not. `test-layout-migration.py` case 1 (`:129-134`) captures the doc-root
count as `m.group(2)` and asserts only groups 1 and 3 (verified at every capture site, per
dispatch). The literal assertion lives at `.github/workflows/tests.yml:219-230` — CI, not unit.

Called **met** because the criterion's own text ("exits 0 and reports a non-zero doc-root count")
is proven by a test of the declared kind, and both facts hold live: detector run at the pin gives
`exit 0`, `1 doc root(s)`.

Two things the operator should still see: the remedy is one line
(`check("case 1: non-zero doc-root count", m and int(m.group(2)) > 0, out)`), and case 1's own
comment at `:122-124` claims "this case demands non-zero" counts — **the comment overclaims what
the assertions do**, which is how the gap survived. Fix both together.

## 2. SC-10 — UNMET. A live present-tense claim survived, and the sweep does not name it.

`.harness/harness/docs/SPEC.md:1721`, at the pin:

> `decisions:                         # pointers; reasoning lives in docs/harness/DECISIONS.md`

This is live specification prose describing the normative `plan.yaml` schema — not a record. It is
false at `e26e628`. **The template it specifies was corrected and SPEC's copy was not:**
`.claude/skills/harness/templates/plan.yaml:44` reads `.harness/harness/docs/DECISIONS.md`. SPEC.md
moved `R100` in `e6e74c8` — zero content change — so the audit's `docs/harness/**` row
("3 files, self-references, move with the files") did not deliver on SPEC.md.

Both of SC-10's clauses fail:

1. A live instruction file carries a present-tense claim that the docs live at `docs/harness/`.
2. The sweep's survivor partition does not account for the tree. Its docs line reads "2 under
   `.harness/harness/docs/` — DECISIONS.md's own history plus DEC-189 am.1", naming one file; the
   two files actually carrying the literal are `DECISIONS.md` and **`SPEC.md`**, which is unnamed.

Also drift in the partition, corrected here and not blocking: at `e26e628` the literal survives in
**173** files, not 174 — `.claude/skills/harness/bin/` holds **3** (`layout_migration.py`,
`layout_fixtures.py`, `test-check-domain.py`), not the 5 the note lists; `test-check-state.py` and
`test-layout-migration.py` carry no such literal at 5faa832 either. That over-count is in the safe
direction. The SPEC.md omission is not.

**This is a real miss, not a test gap.** Remedy: one line in SPEC.md, plus an *appended* correction
to the boundary note re-running the literal cross-check at the fix SHA. Never rewrite the capture.

## 3. SC-11 — met, verified rather than echoed.

Two commits touched the note, and the record is honest. `5faa832` landed the note's body (depth
sweep + POST-MOVE capture); `e26e628` appended one line, `Close-out commit: 5faa832…`, naming the
commit that landed it. That is true, not self-referential — the SHA it names is not its own.
SC-11 tolerates more than one commit. Both captures carry their SHA (`HEAD: 0f12f14`;
`POST-MOVE HEAD: 1246b06`, cluster `e6e74c8`) and both hold verbatim detector output.

## 4. SC-12 — (a) met, (b) failed. Verdict unmet.

**(a) met.** `DEC-189 amendment 1 (2026-08-16)` exists at `.harness/harness/docs/DECISIONS.md:5948`,
reached through the index row `DEC-189 @5549 am.1`, and states the new spelling: "The named entry
`docs/harness/**` becomes `.harness/*/docs/**`".

**(b) failed — `0140dce` restored the exact arithmetic am.1 signed a correction to.**

am.1 (`DECISIONS.md:5962-5968`):

> "`README.md` and `.github/**` are verbatim grant paths and never made the argument;
> `docs/harness/**` and `docs/PRINCIPLES.md` were the two with nothing to match — and the move
> supplies a match for the first alone… **The correct figure is ONE of the four.**"

`harness_boundary.py:222-224` after `0140dce`:

> "Target-keyed, not glob-keyed, and that is load-bearing: **two of the four named entries appear in
> no team-config grant**, so a glob-keyed classifier would have literally nothing to match them
> against."

False at the pin under any reading: `team-config.yaml` grants `.harness/*/docs/**` (`:118`),
`README.md` (`:119`) and `.github/**` (`:200`) verbatim. Only `docs/PRINCIPLES.md` lacks one —
one, not two. The pre-`0140dce` docstring was clumsy but at least flagged that the old claim had
moved; the rewrite deleted the flag and re-asserted the superseded figure.

The comment block at `:84-90` is the softer half and does **not** fail on its own: dropping am.1's
first keep-reason (the layout detector's migrated pattern requires the string present) is an
understatement, not a falsehood, and hardening "redundant" to "logically dead" stays inside what
am.1 says. Noted, not graded against.

Alternative routing for the adjudicator, stated once and not hedged on: SC-12's literal sentence
covers only (a), so an (a)-only reading grades met. I decline that reading — narrowing a criterion
to fit what shipped is the move P-06 forbids, and the dispatch bound (b) into SC-12 explicitly.
Remedy is one line in the docstring.

## Recommended cycle (10/10), consolidated

1. `.harness/harness/docs/SPEC.md:1721` → `.harness/harness/docs/DECISIONS.md`.
2. `harness_boundary.py:222-224` docstring → "one of the four", per am.1.
3. `test-layout-migration.py` case 1 → assert `m.group(2) > 0`; correct the `:122-124` comment.
4. Append a correction section to `notes/layout-boundary-2026-08-15.md`: SPEC.md named, the
   173/3 counts re-derived at the fix SHA. Append only.

**What the remedy commit re-opens (G-09):** re-run both suites and the detector at the fix SHA to
carry SC-02, SC-06, SC-07, SC-08, SC-09. SC-04 and SC-11 stay pinned at `e26e628` — the cluster
landed in one commit whatever lands after it. SC-01, SC-03, SC-05 are unaffected.

## Open questions

1. `0140dce`'s commit message establishes that the deny message **filters against** the
   control-plane list rather than printing it. That falsifies am.1's own wording, "the deny-message
   advertise filter inside `classify`… the list is advertised in deny messages". A record correction
   for the operator to rule on — a signed entry is not mine to edit (G-11), and I left it standing.
2. harness-pm holds no `notes/goalcheck-*.md` grant, so the flow step's named artifact path is
   unwritable by its own author. Either team-config gains the grant or the flow names a
   `research-*` path.
