# Independence verification — cycle-9 panel-fix closure — FEAT-51

**BLUF: PASS.** F-A, F-B, F-C and F-F are all genuinely closed at source. T-02's amended `verify:`
block is a real, non-vacuous, independently-discriminating gate (exits 1 today; its new third
conjunct alone also exits 1). All 26 of T-01's re-measured line anchors land on exactly what the
intent claims. The converse sweep for a surviving unqualified "orphan writes are quarantined" claim
found none. Question 5's structural checks (panel-finding immutability, REQ text, SC/task coverage,
approval state) all pass. Two small, real, out-of-scope observations are recorded at the end; neither
gates.

Every claim below is marked READING or RUNNING with a `file:line` citation, per the dispatch contract.

## Q1 — F-A: is the hole admitted everywhere the panel said it must be, and nowhere claimed shut?

READING. All five mandated locations verified present and correctly qualified:

- **D-19**, `plan.yaml:247-250` — "bounds exactly the two GOVERNED write routes... does NOT bound a
  generic Bash write... no artifact this feature ships may assert the boundary without that
  qualification."
- **REQ-04**, `BRIEF.md:41-46` — "quarantined instead of landing **on the two governed write routes
  the harness gates**... A generic `Bash` write... is NOT covered (D-19)."
- **`## Goal`**, `BRIEF.md:24-30` — "cannot race a replacement writer **on the two governed write
  routes the harness gates** — a generic `Bash` write... is not covered, and `## Verification gaps`
  names that route."
- **New `## Verification gaps` bullet**, `BRIEF.md:230-244` — "A generic `Bash` write to a canonical
  artifact is NOT covered by the quarantine boundary, which is why REQ-04 and the `## Goal` now name
  their two governed routes," with the `PF-c7ab6506…` measurement and the backlog filing.
- **T-06's mandated claim list**, `plan.yaml:693-716` — the "what the boundary does NOT cover" bullet
  (`plan.yaml:705-713`) states the D-18 discard hole and the D-19 generic-Bash hole in the same terms.

**The converse sweep — this is what actually decides the question.** I grepped `BRIEF.md` and
`plan.yaml` whole with these patterns, verifying each pattern first matches a known positive instance
before trusting an absence:
- `quarantined|is quarantined|are quarantined` (verified positive: matches REQ-04 and the gaps
  bullet, both qualified) — 15 hits in `BRIEF.md`, 20+ in `plan.yaml`.
- `orphan|boundary covers|write boundary|writes to canonical|canonical write` — cross-check pass,
  10 more hits in `BRIEF.md`, several dozen in `plan.yaml` (mostly test-label strings and decision
  `because:` text).

Every hit falls into one of three buckets:
1. **Qualified in place** — REQ-04, the Goal, the gaps bullet, D-19, T-06's list, SC-04/SC-05/SC-11
   (each names `Write`, `check-domain.sh`, or `plan-sign-gate.sh` specifically), and every T-03/T-07
   test-label string (`an orphan canonical write is quarantined` etc.) — qualified by the task's own
   title/gate context (T-03's title is literally "…at the check-domain.sh Write gate"; T-07's is
   "Close the Bash route…").
2. **Not a coverage claim at all** — adoption/sandbox mechanics ("adoption of a quarantined
   `plan.yaml` goes through…", "a quarantined write reaches disk without twelve new grants",
   "`quarantine.py list/adopt/discard`" descriptions). These say what happens to something already
   quarantined; they assert nothing about which routes get quarantined.
3. **The one legitimate historical quote** — D-15's own `choice:` field (`plan.yaml:240`) names the
   two superseded bullets by their opening words *in order to describe the supersession*; this is
   the single occurrence of "refused at the check-domain.sh Write gate on the canonical artifacts"
   in the whole file, and it is inside D-15's description, never inside T-06's actual mandated list
   (confirmed by a targeted grep restricted to `plan.yaml:653-733`, T-06's `intent:` block: zero
   hits for that phrase or for "bites on the last three").

**No surviving unqualified universal claim found.** Two sentences are worth naming even though I
judge neither a violation: the TTL bullet in `## Verification gaps` (`BRIEF.md:216-219`, "…the write
is quarantined and adoption is required") and SC-10's UAT text (`BRIEF.md:166-168`, "no canonical
feature artifact was overwritten by the orphan") don't re-state the two-route qualifier inline. Both
sit downstream of the already-qualified REQ-04 (read earlier in the same document) and immediately
beside (TTL bullet, two bullets later in the same list) or describe (SC-10, a live-demo criterion
that necessarily exercises the governed routes an agent's tools actually use) the explicit D-19 gap.
I do not treat either as a surviving unqualified claim, but I record them so a future stricter sweep
doesn't have to re-derive this judgment call.

**F-A: CLOSED.**

## Q2 — F-C: does T-06 still contradict D-15?

READING `plan.yaml:653-733` (T-06's full `intent:` block).

T-06's mandated claim list now contains, verified bullet by bullet: the `check-domain.sh`
`Write`/`Edit` half (`:694-696`); the `plan-sign-gate.sh` `PreToolUse` `Bash` half naming all four
mutating verbs and `quarantine.py adopt` (`:696-698`); the `plan.yaml`-only-write-route-is-`plan-merge.py`-through-`Bash`
sentence (`:699-703`); the D-18 discard-uncovered clause (`:705-708`); and the D-19
generic-Bash-uncovered clause (`:708-713`). The two bullets D-15 supersedes are confirmed **absent**:
I grepped the exact phrases `bites on the last three` and `refused at the check-domain.sh Write gate
on the canonical artifacts` against the whole file — the first has zero occurrences anywhere; the
second has exactly one, inside D-15's own `choice:` at `plan.yaml:240` (a legitimate description of
what was superseded), and zero occurrences inside T-06's `intent:` block itself.

**The decisive question: could a documentor writing DEC-210 from the bullet list ALONE satisfy
T-06's own `verify:` and SC-09?** Walking both conjunct by conjunct / clause by clause: **no, not from
the ten-bullet "carries exactly these claims" enumeration alone** — two things `verify:`/SC-09 demand
sit in the paragraph *after* the bullet list, not inside it:
- `verify:` conjuncts 3-5 (`grep DEC-210` in `DECISIONS-INDEX.md`; `gen-decisions-index.py --stdout`
  diff-clean; `test-gen-decisions-index.py` green, `plan.yaml:665-667`) require actually *running*
  the regeneration, which is instructed only in the trailing paragraph ("Then run python3
  gen-decisions-index.py to regenerate DECISIONS-INDEX.md…", `plan.yaml:730-733`).
- SC-09's clause that the index row "names the compatibility host in the hand-written ruling half"
  (`BRIEF.md:152`) is satisfied only by the hand-written ruling clause the *same trailing paragraph*
  separately instructs ("write a ruling clause that names the Claude Code compatibility host…",
  `plan.yaml:732-733`) — this sentence is not among the ten bullets.
- SC-09's clause that the claims be "Asserted in the suite by `test-gen-decisions-index.py`… each
  clause is its own assertion" (`BRIEF.md:154-156`) is fulfilled by **T-08**, a separate dependent
  task, not by T-06 at all.

This is **not a new defect** and does not reopen F-C: the split between "bullet-list content" and
"surrounding regeneration mechanics" predates the c9 amendment (the amendment edited bullet *content*
only, per the product-lead's own account, which I independently confirmed above), and the documentor
executing T-06 reads the *whole* `intent:` block, not the bullet enumeration in isolation — so in
practice nothing is missed. I record the literal answer to the posed question because it is precise
and the assignment asked for it, not because it changes the disposition.

**F-C: CLOSED.**

## Q3 — F-B: is T-02's amendment buildable, and does its verify DISCRIMINATE?

Cross-checked the verify block text against `plan.yaml:356-360` — **identical, byte for byte**, to
what I ran below.

RUNNING, from the worktree root, the exact four-line block:
```
grep -q 'def case_29_orphan_write' .agents/skills/harness/bin/test-inflight-registry.py &&
grep -q 'def case_33_orphan_write_omp_runtime_is_never_orphaned' .agents/skills/harness/bin/test-inflight-registry.py &&
grep -q 'the children refusal names SUSPENDED and never says a repeated return ships' .agents/skills/harness/bin/test-inflight-registry.py &&
python3 .agents/skills/harness/bin/test-inflight-registry.py
```
**Exit code: 1.** Non-zero — the task grades RED before T-02 is built, as it must.

RUNNING the third conjunct **alone**:
```
grep -q 'the children refusal names SUSPENDED and never says a repeated return ships' .agents/skills/harness/bin/test-inflight-registry.py
```
**Exit code: 1.** Also non-zero on its own — the new conjunct is a genuine, independent
discriminator, not one that merely rides along behind conjunct 1's failure.

READING `inflight_registry.py:521-537` (confirmed via `grep` with line numbers, not recall): the
function `children_refusal_lines` runs from `def children_refusal_lines(agent, children):` at
`:521` to `return lines` at `:537` — exactly the span the plan claims. Its last appended block is the
`lines.append(...)` call at `:532-536`, whose text at `:533-535` reads verbatim "this refusal fires
at most once per consecutive stop sequence; an immediate second identical return ships, and it
re-fires on a later wake while a child is still live — correct any claim about a child you cannot see
and end the turn again." **True span: 521-537 (whole function); the targeted last-appended text sits
at 532-536.**

**F-B: CLOSED** (verify discriminates; target text confirmed at the cited location).

## Q4 — F-F: are T-01's re-measured anchors correct?

READING `plan.yaml:220-302` (T-01's full `intent:`, read `:raw` to rule out any elision) for the
anchor list, then READING each cited line in `validate-digest.py` and `test-validate-digest.py` at
HEAD, one at a time, via `grep` with line numbers (not manual counting alone — cross-checked).

**26 anchors checked total.**

`test-validate-digest.py` (9 anchors) — all correct:
`:18` (`VALIDATE_DIGEST_BIN` env var name, used in the `VALIDATE = os.environ.get("VALIDATE_DIGEST_BIN")…`
line) ✓ · `:239` `def case(...)` ✓ · `:1227` `def t09(...)` ✓ · `:1231` `def _reg_module()` ✓ ·
`:1241` `def _t09_root()` ✓ · `:1249` `def _t09_fire(...)` ✓ · `:1286` `def claims(root, agent):`
inside `run_t09` ✓ · `:3571` `def main():` ✓ · `:3578` `fails += run_t09()` ✓.

`validate-digest.py` (17 anchors) — all correct:
`:35` `VERDICTS = {...}` ✓ · `:1565` `def hook_mode():` ✓ · `:1598` `if "agent_type" not in d or
not d.get("agent_type"):` ✓ · `:1604` `if not agent.startswith("harness-"):` ✓ · `:1606`
`if d.get("stop_hook_active"):` ✓ · `:1610` `# T-09 — issue #551. TWO steps, in THIS order…` ✓ ·
`:1622` `except Exception as _e:` — the except-clause header for the "registry unavailable" handler;
the literal print text is one line below at `:1623`, so this anchor lands on the start of the correct
block rather than the print statement itself. I count this correct (it identifies the right code
region) but note the one-line offset for completeness ✓ (near-exact) · `:1635`
`if _root is None:` ✓ · `:1639` `# STEP ONE — THE RELEASE.` ✓ · `:1646` `_released = _reg.release(` ✓
· `:1656` `except Exception as _e:` (release failure swallowing) ✓ · `:1661`
`# STEP TWO — THE D-09 RETURN CONTRACT.` (em dash, as flagged) ✓ · `:1675`
`_kids = _reg.live_children(` ✓ · `:1687` `for _line in _reg.children_refusal_lines(agent, _kids):`
✓ · `:1698` `"  %s" % _reg.release_cmd(` ✓ · `:1706` `return 2` ✓ · `:1714`
`raw = d.get("last_assistant_message", _ABSENT)` ✓.

**Zero anchors land on the wrong code.** One (`:1622`) lands on the except-header rather than the
literal print line one below it, immaterial to a builder using it as a navigation anchor.

**F-F: CLOSED.**

## Q5 — did the amendment break anything it was not meant to touch?

**Seven cycle-5 findings byte-identical?** READING two sources (no git history exists for this
comparison — the whole feature directory is untracked; confirmed by RUNNING
`git status --porcelain` from the worktree root, which returned `?? .harness/harness/features/FEAT-51-…/`
for the whole directory):
- `id`/`severity`/`reader`/`summary` compared against `notes/plan-proposal-panel-c5.yaml:26-60`, the
  original cycle-5 panel proposal — **byte-identical** for all seven
  (`PF-2b48984b…`, `PF-5d8bf4a5…`, `PF-ba976e85…`, `PF-e050d475…`, `PF-e380f685…`, `PF-7f73167a…`,
  `PF-6ac0675c…`).
- `disposition`/`resolved_by` cross-checked against `runs/plan-panel-c9-validator/digest.md`'s own
  disposition census ("high 4/4 resolved… med 4 resolved + 1 open (`PF-e380f685`)… low 2 resolved + 2
  open"), computed by that reader **before** the panelfix amendment ran. I independently recomputed
  the same census from the current `plan.yaml` (13 findings total: the seven cycle-5 plus the six
  cycle-9 F-A..F-F) and it matches exactly — 4/4 high resolved, 4-of-5 med resolved with
  `PF-e380f685` open, 2-of-4 low resolved. Disposition/`resolved_by` for the seven are unchanged.

**Valid topological order?** READING `plan.yaml` task-order and `depends_on` fields (`plan.yaml:253,
345, 434, 511, 578, 651, 737, 923, 1032`). All 9 task ids (T-01..T-08, T-10) exist and every
`depends_on` target resolves to a real id — the graph has **no cycles** (a genuine DAG). It is,
however, **not sorted in list order**: T-06 (`plan.yaml:651`, 6th task) lists `T-07` in its
`depends_on` (`plan.yaml:657`), but T-07 is listed later, as the 7th task (`plan.yaml:737`). This
predates the c9 amendment — T-06's `depends_on:` field was not part of the F-A/F-C remedy, only its
`intent:` bullets were — so it is not something this amendment broke. Recorded below as an
out-of-scope observation, not a `must_fix`.

**12 SCs graded, every task traces a live REQ?** READING `BRIEF.md`'s 12 criteria (SC-01..SC-11,
SC-13; SC-12 deliberately withdrawn per `BRIEF.md:220-229`) against `plan.yaml`'s tasks: every SC
maps to at least one task (SC-01/02/03→T-01, SC-04/05→T-03, SC-06→T-04, SC-07→T-02/T-03/T-04/T-07
jointly, SC-08→T-05, SC-09→T-06+T-08, SC-10→uat, no dedicated task as expected, SC-11→T-07,
SC-13→T-10), and every task's `traces:` field names only REQ-01..REQ-07, all live. Zero orphans.

**REQ-01..03, REQ-05..07 unchanged?** READING `BRIEF.md:34-52` — all six read as expected, coherent
with the tasks and SCs that cite them; only REQ-04 (`:41-46`) carries the amendment.

**Approval state?** READING `plan.yaml:1-6` — no top-level `approval:` key anywhere in the file
(confirmed by a whole-file grep for `^approval:`), `status: plan` at `:3`. READING `BRIEF.md`'s
`## Approval` section — `status: pending`, unsigned.

**Q5: no breakage found.**

## Out-of-scope observations (not gating)

1. `plan.yaml:651-657` — T-06 lists `T-07` as a dependency though `T-07` (`:737`) appears later in
   file order. The graph itself is acyclic and this predates the c9 amendment, but a strict
   "topologically listed" convention would want T-07 moved before T-06 or the dependency documented
   as forward-looking.
2. `BRIEF.md:216-219` (TTL bullet) and `BRIEF.md:166-168` (SC-10) state quarantine outcomes without
   repeating the two-route qualifier inline. I judged neither a violation (see Q1), but flag them for
   a future stricter pass.

```yaml
VERDICT: PASS
DIGEST:
  headline: "F-A, F-B, F-C and F-F are all genuinely closed at source: the five-location F-A remedy is present and qualified everywhere, no unqualified 'orphan writes are quarantined' claim survives the whole-file sweep, T-02's verify discriminates (exit 1 full block, exit 1 third conjunct alone), all 26 of T-01's re-measured anchors land correctly, and Q5 finds no breakage — panel findings, DAG, REQ/SC coverage and approval state all intact."
  code_grade: n_a
  severity_max: n/a
  findings: 2
  must_fix: []
  spec_violations: []
  reviewed: "none (plan phase, no review_sha; feature.json:5 is review_sha \"none\")"
  human_commits_in_scope: []
  t02_verify_exit_full_block: 1
  t02_verify_exit_third_conjunct_alone: 1
  t01_anchors_checked: 26
  t01_anchors_wrong: 0
  open_questions:
    - { id: Q1, question: "T-06 (plan.yaml:651) lists T-07 (plan.yaml:737) as a dependency though T-07 is listed later in file order. The DAG is acyclic and this predates the c9 amendment (T-06's depends_on field was untouched by the F-A/F-C remedy) — not a defect introduced by this cycle, but worth a future pass considering whether task-list order should match dependency order.", blocking: false }
  files_touched: []
  expertise_update: []
artifact: .harness/harness/features/FEAT-51-claude-code-lifecycle-safety/notes/review-harness-code-reviewer-panelverify-c9.md
```
