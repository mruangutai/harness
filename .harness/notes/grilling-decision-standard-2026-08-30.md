# Grilling — a standard for what constitutes a decision (FEAT-46)

Origin: the operator read `DECISIONS.md` and judged that FEAT-38, which folded amendments into their
entries, left a file that is still overwhelmingly prose commentary rather than decisions. That is a
different defect from the one FEAT-38 was scoped to fix, and both readings are correct: the fold can
be sound while the thing folded was never a decision.

All figures measured against `git show 635cd3ba:.harness/harness/docs/DECISIONS.md` — 188 entries,
6,240 lines of entry body. Two measurement bugs were found and corrected mid-grilling: zero-padding
(`DEC-04` vs `DEC-4`) and index-row contamination inflating every citation count by one. Corrected
numbers are the ones below. `/usr/bin/grep` on this machine is `pi-uu-grep 0.2.0`, where a
line-leading `+` matches every line, so every count here was done in Python.

**Round 3 re-pinned the measurement.** `635cd3ba` is superseded: FEAT-38 merged at 18:06:57Z
(PR #996) and `origin/main` is now `3331559`, carrying 33 more lines from the FEAT-44 amendment
fold. Re-measured against the merged file — 188 entries, 77 clause-clean, 14 with a prose tail,
97 zero-clause. The structure holds; the 13/98 split above is now 14/97.

## The destination

`DECISIONS.md` states decisions and nothing else. One ruling per entry, in a fixed clause form, with
commentary capped at a tenth of its length. History lives in git. Every entry is citable precisely,
because a citation names one ruling rather than one of nine.

## Settled

| # | Ruling | Consequence |
|---|---|---|
| 1 | **Two axes, not one.** Failing the *form* means rewrite; failing the *substance* means strike | All 94 form-failing entries are durably cited, 29 heavily. A form-based prune would delete `DEC-120`, `DEC-203`, `DEC-138`, `DEC-182` — the constitution |
| 2 | **Substance test: `DEC-23` verbatim, plus forward force.** A choice stays; an observation about behaviour goes; a choice that no longer binds anything is also struck | `DEC-105` (token baseline) is an observation → strike. `DEC-94` (pilot host) was a real choice with no forward force → strike |
| 3 | **Form: `Chose` and `Because` mandatory. `Over` and `Tradeoff` only when real** | Refused all-four-unconditionally: `DEC-190` has no rejected alternative, and forcing one invites a fabricated `Over:`, worse than prose |
| 4 | **Prose cap 10%** of an entry's non-blank lines; prose is any block not opening with a clause marker | The threshold is inert — 10% and 20% fail the identical 111 entries. The distribution is bimodal: entries score ~0% or 100% |
| 5 | **Displaced prose is deleted; `git log --follow` holds it** | `DEC-205`'s own accepted cost, reused rather than re-argued. No relocation project, no sidecar rationale files |
| 6 | **Strike triage is agent-run; every strike needs a second independent reader** | Only strikes both readers agree on reach the operator; disagreements arrive as a pair with both arguments |
| 7 | **Rewrites get full per-entry read-back by one reader — 100% coverage** | FEAT-38's proven side-by-side method, but at 98/98 rather than its 10-of-15 sample. Coverage beats independence here because the failure is *undetectable*, not contested (see the asymmetry below) |
| 8 | **`DEC-205` wins the purpose conflict; `DEC-158`'s history clause is rewritten** | The file states current truth only. `DEC-158` keeps its skill-side ruling and loses its claim that history lands here |
| 9 | **The omnibus entries are fully split, and every affected durable citation is repointed** | 30 entries → 164 successors. Entry count 188 → 322. 331 citations across 84 files redirected to the successor each one actually meant |
| 10 | **The FEAT-38 UAT pass does not exempt anything.** `DEC-138`, `DEC-174` and `DEC-181` are all in scope | That review asked only whether an entry reads as current truth. `DEC-181` is 100% prose, `DEC-138` carries 11 rulings, `DEC-174` carries 7 |
| 11 | **Still one feature, phased** — reaffirmed after the true size was known | **Phase order corrected by ruling 17.** Capture the citation-precision baseline → standard → checker in warn mode → strike triage → 30 splits → author the 164 successors and the remaining 67 in clause form → repoint the live surfaces + family check → anchor verifier → re-run the citation-precision test → checker blocking, then the write-time hook |
| 12 | **Sequential numbering — `DEC-206` … `DEC-369`.** The 30 parents are deleted, not kept as umbrellas | Needs no new convention. Sub-numbering would widen 6 regexes in `gen-decisions-index.py` and 1 in `check-expertise.sh`, and a prose `DEC-138.4` still matches `DEC-\d+`, tripping `DEC-205`'s own refs clause |
| 13 | **Repoints get a split map, a mechanical family check, and 100% single-reader read-back** | Cross-family error is impossible from the map plus the diff; wrong-sibling is the residual and gets ruling 7's treatment. 331 reads on top of the rewrite read-backs |
| 14 | **The anchor checker is wired standing AND run as a migration verifier** | `check-decision-anchors.py` ships in FEAT-38 and nothing invokes it — CI, `check-state.sh` and `settings.json` are all silent; only its *test* is registered. The split moves every line number in the file, so it is needed during the work, not just after |
| 15 | **CI step in `integration` now; write-time hook as the LAST phase** | 2.5 ms against a 114–258 s job, so the cost is the three-outcome wrapper, not the clock. A hook installed first would refuse the very rewrites that fix the file |
| 16 | **Citation-precision test against a baseline drawn pre-migration** | Measures the destination's own sentence. ~20 durable sites; admitted-ruling count must fall to exactly 1. The baseline must be captured at `3331559` or it is unrecoverable |
| 17 | **Split BEFORE rewrite** — triage, split, then author everything in clause form | Ruling 11's order had no legal intermediate state: a clause-form rewrite of `DEC-203` would stack 9 `Chose:` blocks under one number. Saves 30 read-backs |
| 18 | **No prose-cap exemption for tables** | The cap counts a block as clause when its first line opens with a marker, so a 15-line `Because:` costs nothing and only unmarked blocks bite. A table is the reasoning behind a choice, not the choice |
| 19 | **Cycle budget 30** | FEAT-38 used 16 of 30; FEAT-43 exhausted 29 of 29. The default 10 would stall mid-migration, with the file half-migrated |
| 20 | **The split map is filed as feature evidence, not published** | No legacy ids in `DECISIONS.md` or the index. `DEC-188` is satisfied without rewrite — successors exist, durable citations are repointed, and the map *is* the strike record, git-tracked in the feature's `notes/` |
| 21 | **FEAT-41 ships first; FEAT-46 inherits its three clause corrections** | FEAT-41 deferred them here (`plan.yaml:88`): `DEC-203` §6, `DEC-191`, `DEC-182`, plus a new station-vocabulary entry. All three are already zero-clause and in the rewrite set, so this is content input, not new work — and FEAT-41's 21 live `DEC-203` citations become historical at ship |

## The root cause, which is not what the critique assumed

**`DEC-158` and `DEC-205` disagree about what this file is for, and neither cites the other.**

- `DEC-158` — *"skills carry the rule, DECISIONS carries the rule's history"* — deliberately moved
  25–30% of the two largest skills into this file, because *"history, incident detail, and superseded
  reasoning live in DECISIONS.md only."*
- `DEC-205`, shipped by FEAT-38 — *"This file states current truth."*

FEAT-38 landed `DEC-205` without reconciling `DEC-158`, and the refs graph did not catch it because
neither entry references the other. **Half the file reads as commentary partly because it is
*obeying* `DEC-158`.** Ruling 8 resolves it. Until it did, an author had two live and opposed
instructions and no way to tell which governed.

## The asymmetry that drove ruling 7

| | If it goes wrong | Detectable afterwards? |
|---|---|---|
| A wrong **strike** | Entry gone, citations dangle | **Yes** — a dangling citation is the failure `DEC-205` says a reader can detect |
| A wrong **rewrite** | Entry survives, reads clean, a load-bearing clause is silently gone | **No.** Nothing points at it, ever |

The strike — the *more* detectable failure — got two readers first. The rewrite is 98 entries of the
less detectable one and had no protection until ruling 7.

## Corrected mid-grilling — my errors, recorded

1. **"No standard exists."** Wrong. `DEC-23` is the standard, approved, ten lines. It was scoped to
   `PLAN.md` and mental models and never pointed at the authority file. `DEC-105` is `DEC-23`'s own
   counter-example wearing a DEC number. FEAT-46 extends an approved boundary rather than authoring one.
2. **Citation count offered as a prune proxy.** Wrong. It would delete `DEC-75`, which the operator
   had named as an exemplary decision, and `DEC-74`, `DEC-89`, `DEC-33`. A decision can be
   implemented without being cited by number.
3. **"Zero citation refactoring", listed as settled.** Conflated two things. The 6,986 citations in
   runs, notes, logs and feature dirs are historical record and must never change — rewriting them
   falsifies what was believed when written. The durable citations in skills, agents, `bin/` and docs
   are *live pointers*, and repointing one is exactly what `DEC-205` requires of a strike. Ruling 9
   is compliant; grandfathering would have been the deviation.

## The measurement that reframed the ask

The operator's opening summary was that *much of the decisions and their prose can be removed*. The
file disagrees:

| Bucket | Count | Remedy |
|---|---|---|
| Clause form, ~0% prose | 77 | keep |
| Clauses **plus** a prose tail — `DEC-95` 67%, `DEC-99` 78% | 13 | cut the tail, no judgement needed |
| Zero clauses, durably cited | 85 | mostly rewrite; strike only on the substance test |
| Zero clauses, uncited | 13 | cheapest strikes — but the list still holds `DEC-205` and `DEC-190` |

**The removal set is small; the rewrite set is large.** The file is mostly decisions in the wrong
clothes with a commentary minority, not the reverse.

## The omnibus finding

30 entries carry four or more independent rulings under one number. `DEC-138` carries **11**;
`DEC-203` carries **9** and is literally enumerated *"1. What 'open' means / 2. Who writes `Done` /
3. Which cards ship moves / 4. The parent rule."* A citation to `DEC-203` already means one of nine
things — the operator's "not a useful citation" complaint, inverted: too broad, not too narrow.

Two things were measured rather than assumed:

- **The prose cap catches all 30 today** — zero entries both pass the cap and are omnibus, because
  omnibus entries happen to be written as prose sections. **It will not catch them tomorrow:** nine
  `Chose:`/`Because:` pairs in one entry score 0% prose and sail through. The checker therefore needs
  a **one-ruling-per-entry rule** that is redundant during the migration and load-bearing after it.
- **Removing history does not dissolve the problem.** After history sections go, 0 of 30 collapse to
  a single ruling. Only `DEC-174` shrinks materially, 7 → 3.

## Derived, not asked

- **Zero renumbering, ever.** `DEC-205`: a deleted number is never reused. Reuse makes a historical
  citation actively wrong rather than merely dangling, and dangling is the failure a reader detects.
- **A strike owes a named successor.** `DEC-205` as amended by FEAT-38. Of the 98 zero-clause
  entries, 85 are durably cited, so a strike there is not free.
- **Struck records and umbrella entries are exempt from the form check.** `DEC-90` is a tombstone
  with no clauses to carry and must not be forced into one.
- **Tables count as prose.** This is why `DEC-105`'s measurement table scores 100%.
- **The checker requires rewriting `DEC-205`.** It states *"one mechanical check guards this file,
  and only one"* and records two refused checks so nobody re-suggests them. A form-and-prose checker
  survives that clause's own logic — mechanical, zero judgement, inspects the file's shape rather
  than the world — but the rewrite must be explicit. Amendments are ended, so `DEC-23`, `DEC-158` and
  `DEC-205` are *rewritten*, not annotated.
- **`harness-documentor` owns `DECISIONS.md`** (`check-domain.sh --resolve` exit 0). The 98 rewrites
  and 30 splits are delegable; only the checker is `main-session-direct` under the `DEC-174` carve-out.
- **FEAT-38 lands first.** It owns the shipped text of `DEC-205` and `DEC-181`.
- **The repoint set is an explicit include-list of live surfaces, never a heuristic.** A
  skills/agents/bin/docs filter misses five live pointers: `team-config.yaml` (31 citations),
  `harness.json` (14), `.omp/extensions/harness-hooks.ts` (6), `.github/workflows/tests.yml` (5)
  and `.harness/expertise/` (4, injected at every spawn). Those are exactly the files where a dead
  citation is load-bearing.
- **A correction rewrites the entry it corrects; no in-place clause strike.** This answers the form
  question FEAT-41 deferred, by mechanism rather than by a new ruling — ruling 8 and `DEC-205`
  already settle it, and all three corrected entries are being rewritten anyway.
- **`DEC-158`'s homeless skill history is deleted, per ruling 5.** Recoverable from git only. This
  was listed as fog; ruling 5 already decided it.

## Fog — named, not resolved

- **How many entries fail the substance test is unmeasured.** It needs the rubric applied per
  entry, which is the triage itself. The 13 uncited zero-clause entries are a floor, not an estimate.
- **The membership of the 30 omnibus entries is not reproducible by any script.** An independent
  proxy — entries carrying four or more enumerated ruling markers — finds **5**, not 30. The 30 rests
  on judgement, so triage must write the list down explicitly or the split's scope cannot be verified
  and the 164 successor count cannot be checked.
- **Whether a 10% cap is survivable is narrower but still untested.** Ruling 18's mechanism removes
  most of the risk: clause blocks cost nothing, so only unmarked blocks can fail. Whether 164
  successors each state cleanly will only be known during authoring.

## Out of scope, explicitly

- **Rewriting historical citations.** Prohibited, and it would erase the record.
- **A propagation checker.** Struck whole under `DEC-188`; not revived.
- **The referenced-file watch (M3) and the periodic LLM audit (M4).** Refused in `DEC-205` with
  reasoning. FEAT-46's checker is a third thing and does not re-litigate them.
- **`DECISIONS-INDEX.md`'s full generation contract.** Issue 686 stays open in part; FEAT-46 needs
  only that a struck entry's row and a split entry's successors behave.
- **FEAT-38's UAT.** Answered and passed on its own question. See ruling 10 for its bounds.

## Facts I verified in round 3 (so pm does not re-derive them)

- FEAT-38 merged 2026-08-30 18:06:57Z, PR #996 `MERGED`; `origin/main` = `3331559` and `706e897`
  is an ancestor. **The operator's hold on FEAT-46 planning is released.**
- Re-measured at the merged snapshot: 188 entries, 77 clause-clean, 14 prose-tail, 97 zero-clause.
- **Every current entry carries 0 or 1 `Chose:` blocks.** A one-ruling check keyed on `Chose:`
  count is mechanical today and passes all 90 clause-bearing entries, so it is redundant during the
  migration and load-bearing after it — exactly as the omnibus finding predicted.
- `check-decision-anchors.py` is invoked by **nothing**. `run-unit-tests.sh` and `harness.json`
  register `test-check-decision-anchors.py`, the test. Issue #133's shape on `DEC-205`'s own clause.
- `gen-decisions-index.py` is the only non-test parser of DEC ids (6 `DEC-\d+` regexes);
  `check-expertise.sh` has one more.
- Runtime: the form/prose/one-ruling check is **2.5 ms** over 188 entries; the anchor checker is
  **70 ms** (`examined 20 anchor(s), 0 failed`); the `integration` job runs **114–258 s**.
- Branch protection requires exactly one context, `integration`, which is the job id — the job
  carries no `name:` key. A new job would emit a context nobody requires.
- Citation census outside the authority: feature notes 3,122 · BRIEF/plan/feature.json 1,857 ·
  skills/agents/bin/docs 963 · observations 257 · logs 145 · STATE.md 88 · live config 60.
- `DEC-174` alone carries 1,132 historical citations, `DEC-138` 235, `DEC-203` 81 — none of which
  are rewritten, and none of which resolve after ruling 12 except through the filed split map.

## Platform defect found during this grilling — backlog, not scope

`feature-worktree.py behind` exits **2** on this repository: *"repository not in fleet"*. The
`/harness-ship` precondition treats a non-zero exit as meaningful, and exit 2 here means the tool
cannot answer rather than that the worktree is behind. The behind-check was done directly with
`git rev-list --left-right --count main...HEAD` instead. A gate whose failure mode is
indistinguishable from its answer is the shape this project keeps finding.
