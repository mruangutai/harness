# Replan dispositions — FEAT-06 — 2026-08-04

**BLUF.** All six eng-lead `must_fix` are **applied**, two of them with a change to the specified
remedy (EMF-1's token name, EMF-6's method). All four advisories are applied. Every overridden or
superseded pm decision is marked below. The re-scope around **#24** added `REQ-07`, `REQ-08`,
`SC-14`, `SC-15`, `T-10`, `T-11` and `D-08`, and reset both `## Approval` sections to `pending`.

## The six must_fix

| id | disposition | what landed, and the reason if it differs |
|---|---|---|
| **EMF-1** — `depends_on: from_plan_order` is wrong, and PLAN order is not topological | **applied-with-change** | Both halves done. (a) The token is now `depends_on: from_task_depends_on` — reads each task's own field, falls back to file order only where a task declares none (T-04, D-03, T-09). **Change:** eng-lead did not name the token, and it specified the edit in T-04 only; T-09's expansion prose now says the same thing so the two cannot drift. (b) The header carries an explicit topological order — **recomputed**, not copied from the digest's sequence, because T-03 dropped and T-10/T-11 were added: `T-01 → T-02 → T-04 → T-10 → T-05 → T-06 → T-09 → T-11 → T-08 → T-07`. Verified against every declared `depends_on`. The interleave point (T-07 depends on the one dispatched task, T-08) is stated. |
| **EMF-2** — `filter: squad == eng` names a field PLAN tasks do not carry | **applied** | Value is now the token `eng_squad_tasks`, explicitly a **record of the orchestrator's selection**, not a predicate any lead evaluates. T-06 (orchestrator selects the ids and hands the list) and T-09 (host takes the ids it was handed) are worded to agree on the tier, and each carries a note saying so, which was the half of the finding that was about disagreement rather than about the value. |
| **EMF-3** — `steps_from:` has no `prompt:`, so the hand-composed PROMPT survives | **applied** | `prompt: from_task_intent` added to `steps_from:` (T-04) and resolved by T-09's expansion prose. T-04's verify asserts the field's value, so it cannot be quietly omitted. This is the one eng-lead flagged "read first" and it is the difference between closing #9 and moving it down a level. |
| **EMF-4** — `purpose:` says "gated by qa" while qa is Validation, not Engineering | **applied** | `purpose:` reworded verbatim in T-04 to: the qa gate "is NOT a step this team contains — it runs as an orchestrator-sequenced **validator-squad** segment after this team returns (DEC-118)". **The same vocabulary is pasted into T-11's SKILL.md passage**, because EMF-4 and #24 are one fix seen from two sides; otherwise `build.yaml`'s prose would assert orchestrator sequencing that the orchestrator's own playbook still never mentions. Propagated to T-08's SPEC notes cell. **The 7-of-8 trap was watched for and avoided:** the wording is a statement of correct bounds, not an apology, and `build.yaml` was not widened. |
| **EMF-5** — T-01's verify cannot fail on the missing deliverable | **applied** | All four parts. Presence greps on both fixtures added to T-01's verify (`review_sha: none` ≥ 2, `review_sha: 1ce886a` ≥ 1); the **third** fixture (precondition axis: `review_sha: none` with no validator run → no INV-6 line) added as T-01 Step 1(c), with T-01 Step 3 instructed to keep the `any(sq == "validator")` conjunct; registered durably as **T-07 check (10)** — eng-lead asked for an "eighth check" and the numbering moved when SC-14 and SC-15 took (8) and (9), so T-07 now runs **ten** checks and its verify asserts that count; D-06 amended to require the red-first receipt as **verbatim failing output plus invocation**, written to `notes/before-check-state-635ef14.txt`. |
| **EMF-6** — SC-03 claims automated evidence no task can produce | **applied-with-change** | eng-lead offered two routes. **Both taken, deliberately:** SC-03 is reclassified to `verify: inspection` **and** the before-capture is added as **T-01 Step 0**, ahead of everything, because an after-only run cannot assert sameness regardless of the method label. The Verification-gaps block now names what is therefore not proven by a test. **Change vs. the remedy as written:** eng-lead framed these as either/or; taking only the reclassification would have left the SC unfalsifiable in practice, and taking only the precondition would have kept an `automated` label the unit runner cannot honour. **Folded in here:** SC-03's stale premise ("`FEAT-06`'s `runs:` is empty") is corrected — `feature.yaml` now carries `plan-product` and `plan-eng`; neither is `squad: validator`, so the conclusion holds and only the reason changes. |

## The four advisories

| # | disposition | one line |
|---|---|---|
| 1. `steps_from:` declares no `on_fail:` | **applied** | `on_fail: loop_back` added to T-04 with a comment that it restates eng-lead's existing build fix-loop rule rather than inventing one. Cheap, and build is where a future runner looks first. |
| 2. verifies use `yaml.safe_load`, the gate uses `load_file` | **applied** | T-02 and T-04's verifies now use `harness_yaml.load_file` (T-03 is gone). "A gate more permissive than the thing it protects is not a gate" — already recorded at `test-harness-yaml-corpus.py:35-40`. |
| 3. T-05 under-specifies `scan()`'s return shape | **applied** | Contract stated: `scan(root)` keeps its two-value `(errors, n_files)` shape for the six existing `_, nb = scan(d)` call sites; a new `scan_roots(roots)` returns `(errors, {root: n_files})` to supply the per-root counts. A hand executor can no longer pick the other implementation. |
| 4. T-06's uncriterioned "only if it contradicts" | **applied** | Criterion stated: amend `:211` only if it names a build-phase dispatch mechanism other than the `build` team. T-06 and T-11 both carry mechanical added-line caps (12 and 8, combined 20) checked by `git diff --numstat`. |

## Overridden / superseded pm decisions

| item | disposition | reason |
|---|---|---|
| **D-02** (`gate-probe.yaml` fixed in place) | **overridden by the user (Q3)** | Marked overridden in PLAN with its consequences carried in full. **T-03 dropped and its id retired**, replaced by **T-10** (the deletion — a repo change still needs a task). **SC-05 is the SC that carried the wrong count and it is named and reworded from three files to two.** T-05's `depends_on` becomes `T-02, T-04, T-10` and its prose loses the gate-probe reference; the `## Verify receipts` SC-05 row was rewritten too. pm's judgement on the DECISIONS.md question: **amend, do not delete** — T-08(c) adds one line noting the deletion at `DECISIONS.md:2307-2325`. A decision record describing a file that no longer exists, with nothing saying so, is this feature's own through-line. |
| **EQ-1 / Q2** (accept-or-widen the 7-of-8 bound) | **superseded by the re-scope** | Not a choice; the feature is re-scoped around #24. Q2 rewritten in PLAN as "a correct bound, not a shortfall". No SC apologises for 7-of-8; `build.yaml` untouched on that axis. |
| **D-05** (carve-out extension) | **kept — user-confirmed (Q5), not re-litigated** | `bin/test-check-state.py`, `bin/run-unit-tests.sh`, `bin/test-team-catalog.py` stay main-session-direct. |
| **D-03 / T-09** (`steps_from:` as an expansion rule) | **kept — user-confirmed (Q8)** | Which is precisely why EMF-1/2/3 are live rather than moot. T-09 remains load-bearing: without it `build.yaml` is prose only. |
| **Q10 / the routing wall** | **out of scope, per the user** | Belongs to issue #20 with the two new instances. Recorded in PLAN Q4 and not absorbed. |
| **#19** (nothing runs a PLAN `verify:`) | **known, filed, not re-derived** | Recorded once as PLAN Q11 so the build does not assume verifies self-execute. |

## The re-scope — what #24 added, and the one thing that makes it falsifiable

- `closes_issues`: `#8 #9 #16` → **`#8 #9 #16 #24`**.
- **REQ-07** (the obligation is stated where its owner reads it) and **REQ-08** (exactly one account
  of where the gate runs).
- **SC-14** — `grep -c -i 'test_matrix'` on `.claude/skills/harness/SKILL.md` returns ≥ 1, plus a
  line carrying `qa`, `validator` and `loop_back`. It returns **0** at `635ef14`. **This is the SC
  that goes RED if `SKILL.md` is never touched, and `review.yaml` alone cannot satisfy it.**
  Registered as T-07 check (8) so it is `evidence: unit`, not a hand grep.
- **SC-15** — the panel step set stated in SPEC's ship-feature row, in SPEC's review row, and parsed
  out of the shipped `review.yaml` must be the same set. Today they are three different sets. This
  turns the three-descriptions problem itself into a regression test.
- **T-11** — the playbook edit, `domain-ungranted` and **not** `carve-out`: `SKILL.md` is not one of
  CLAUDE.md's five enforcement files. Getting that reason right is what keeps #20's evidence clean.
- **D-08** — one decision, both readings, a recommendation, and the flip-delta. Surfaced as the
  blocking `open_question` Q8. **SC-04's coupling is handled explicitly** rather than left silent:
  it is marked contingent on D-08 and the branch that changes it is named, along with T-02 and
  T-07(1).

## What is NOT in this plan, on purpose

Issue #19, issue #20 and the two new routing-wall instances, issues #18 and #21–#23, and the
prototype gate (settled by visual-designer: no end-user interaction, no prototype — not re-opened).
