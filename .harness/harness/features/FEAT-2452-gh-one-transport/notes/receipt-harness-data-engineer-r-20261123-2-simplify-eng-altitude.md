# FEAT-2452 simplify-eng, ALTITUDE angle: five findings (2 med, 3 low). Four fold-in, one leave. No settled ruling is contested.

**BLUF.** The transport itself sits at the right depth. `issue_number_from_url` goes in factory_gh (T-01), and wayfind's 404 classification stays local (T-04, one caller). The altitude problems are in how the plan states its rules:
- Two rules each get several separate statements, and those can drift: the offline sentinel confinement (3 task intents, about 8 runners) and the "label already exists" diagnosis (2 callers, matcher never specified).
- Two controls sit at the wrong depth. SC-02's absence clause has only an intent-prose search, and the check-state safety control for DEC-174 runs only at the final boundary in the docs task.
- The FACTORY_GH rationale is about to be restated across docstrings and test headers. That is the same pattern that made D-11 a 13-file removal.

Scope read: `plan.yaml` (all 331 lines, including the truncated intents read raw), `BRIEF.md`, the cycle-1 apply note, and the code the plan names (`tests/integration/gh_sync_support.py:206-216`, `tests/harness_config_support.py`, `board_lifecycle.py:91,1141`, `gh-sync.py:990`, `factory_gh.py:1076-1086`, and the INV-26 test files).

## Findings

### 1. The offline sentinel confinement rule is restated in three task intents with no shared home (med, fold-in)
- **File/line:** plan.yaml:242 (T-02), :264 (T-03), :285 (T-04). It is also pinned as behaviour in BRIEF.md:17 (SC-02).
- **Summary:** Each task re-specifies the same fixture contract and implements it separately: set only FACTORY_GH, strip GH_SYNC_GH, prepend a separate directory with a `gh` sentinel that logs argv and exits 97, then assert the log is empty. That means T-02 `gh_sync_support.run` plus each owned runner (test-factory-integration alone has 5 env sites, at :1416–1605), T-03 `fake_gh`/`_stub_env`/board-station runner, and T-04 test-wayfind. No sentinel helper exists in the tree today (grep `tests/` finds none).
- **Concrete cost:** About 8 independent copies of one safety fixture, written in 3 tasks. A copy that drifts, for example a missing GH_SYNC_GH strip or a sentinel on PATH after the fake, quietly re-opens the real-GitHub hole that SC-02 and #893 close. Nothing makes the copies agree. A reviewer has to diff every runner against prose.
- **Alternative (pm applies):** In T-02 (first in the chain, depends_on order T-02→T-03→T-04), create one tests-root helper on the existing `tests/harness_config_support.py` pattern, e.g. `tests/offline_gh_support.py` with `offline_gh_env(fake_path, tmp) -> (env, sentinel_log)`. Add it to T-02 `files` with `create: true`. T-03 and T-04 intents then say "use T-02's `offline_gh_env`; assert its sentinel log is empty" in place of the re-specified mechanics. This only moves where the confinement lives. Its behaviour, its land-first ordering and its red-run evidence stay as they are. **fold-in**

### 2. "Diagnosed already-existing label" is required in two callers, and neither task says what the diagnosis is (med, fold-in)
- **File/line:** plan.yaml:238 (T-02 mirror label create), :262 (T-03 `_ensure_abandoned_label`). BRIEF.md:21 (SC-04).
- **Summary:** The milestone path gets one exact, cited matcher (:239, the `factory_gh.create_ref` 422 + "already exists" conjunction, factory_gh.py:1086). The two label-create paths get only "a specifically diagnosed existing-label response" and "a diagnosed already-existing label". Both read the same `gh label create` response. Today both callers swallow that response (gh-sync.py:990, board_lifecycle.py:91,1141).
- **Concrete cost:** Two independently invented matchers judge the same gh output. If mirror and lifecycle disagree, a label failure is SKIPped in one and accepted as idempotent in the other: divergences (c)/(d) re-created inside the feature that removes them. The reviewer also has no stated rule to check either matcher against, so SC-04's "checked before dependent writes" cannot be inspected for false acceptance.
- **Alternative (pm applies):** State the matcher once. Option one: T-02's intent names the exact conjunction for labels (the gh `label create` existing-label text, lowercased, on a nonzero typed result), and T-03 says "the same conjunction as T-02's mirror label create". Option two, if pm prefers a code home: T-01 adds the predicate to factory_gh, which it already owns, with one unit case, and T-02/T-03 call it. Two callers make that a real seam under the one-adapter/two-adapter test. Neither option touches the settled (e) milestone "no helper" trim. **fold-in**

### 3. SC-02's "absent from scoped files" clause has no mechanical check; the search lives only in T-05 intent prose (low, fold-in)
- **File/line:** BRIEF.md:17 (SC-02, `verify: automated evidence: integration`). plan.yaml:331 (T-05 intent: "Search the scoped active code/test/reference surface for GH_SYNC_GH … expect no occurrences"). T-05 verify at plan.yaml:305-324 does not search.
- **Summary:** SC-02 promises that GH_SYNC_GH and D-11 dual-pin prose are absent from production modules, test support, test headers and manual-probe comments. That is a grep fact, not an integration outcome. The only instruction to check it is a sentence in the last task's intent.
- **Concrete cost:** One leftover header or comment, like the 13 that exist today (`test-board-station.py:10-13`, `test-gh-sync-record.py:221`, `probe-issue-types.py:10,44`, …), passes every verify command and is caught only if the final reviewer remembers to grep. The clause is accepted without a control.
- **Alternative (pm applies):** Add one assertion to T-05's verify heredoc. Iterate the task-owned paths from T-01..T-05 `files`, plus `tests/manual/probe-issue-types.py`, and assert `'GH_SYNC_GH' not in text` and `'D-11' not in text` for those files (the unrelated D-11 decisions live outside them). Then the clause has a check at the verify depth. **fold-in**

### 4. The check-state safety control behind DEC-174 runs only at the final boundary, named in the docs task (low, fold-in)
- **File/line:** plan.yaml:331 (T-05: "Include check-state's existing INV-26 coverage because the shared library is its dependency"). plan.yaml:200-201 (T-01 verify: only `test-factory-gh.py` and `test-gh-cost-log.py`). DEC-174 keep row :133-137.
- **Summary:** T-01 is the task that changes factory_gh's launch entry and import graph (the function-local gh_cost_log import, alias removal). factory_gh is in check-state's dependency chain, and that is the reason every task is main-session-direct. The control that proves check-state still imports and runs is attached to the docs task's final gate.
- **Concrete cost:** An import-order or alias-removal break in check-state's chain (that is, in an enforcement executor) only shows up after T-02..T-05 have landed on top of it. Bisecting four tasks of cutover to find it costs more than one extra file in T-01's pool. Today `tests/integration/test-check-state-inv26.py` and `tests/unit/test-check-state-inv26-routing.py` exist and are cheap to name.
- **Alternative (pm applies):** Add `tests/integration/test-check-state-inv26.py` (and optionally the unit routing file) to T-01's `verify` pool. T-01 does not edit them, so file ownership stays disjoint. Keep the T-05 sentence as the cumulative re-proof. **fold-in**

### 5. FACTORY_GH-only rationale is to be rewritten into module docstrings and test headers instead of pointing at the one reference (low, leave)
- **File/line:** plan.yaml:263 (T-03: "replacing it with the single FACTORY_GH contract" in `board_lifecycle`/`gh_board` docstrings, and "every lifecycle test header/comment"). :242 (T-02: owned integration headers). :327 (T-05: github-mirror.md "Explain FACTORY_GH only").
- **Summary:** After the build, the override rule is stated in github-mirror.md and again in two module docstrings and several test headers. D-11 was spread the same way, which is why deleting it touches 13 files in this plan.
- **Concrete cost:** The next override change repeats this sweep. Divergent restatements also become a source of stale doctrine (compare OQ-1's DEC-138 sentence).
- **Alternative:** T-02/T-03 replace each removed D-11 block with a one-line pointer ("binary override: FACTORY_GH only — see references/github-mirror.md") rather than a restated contract. **leave** is recommended: the cost lands only on a future change. It is cheap to adopt if pm is already rewriting those lines, but it does not justify another panel cycle.

## Considered, not flagged
- `issue_number_from_url` in factory_gh (T-01 :208), consumed by T-02/T-04: the right home, with two real callers.
- Wayfind 404-absence classification kept local (T-04 :282): one caller, so a shared seam would be hypothetical. Right altitude.
- SC-04's milestone matcher detail (BRIEF.md:21) is implementation-level for an SC. It is the cycle-1 PF-e4b1875d applied result, so it is not re-raised.
- Live-probe receipt in T-05 (PF-f10c24fc, applied). Its trace to SC-05/BRIEF verification gaps is implicit (T-05 traces only SC-02/06/07). This is noted for pm and is not a finding.
- Subprocess deadlines, the enforcement ticket and DEC-138 OQ-1 are settled.

## Principles applied
- **harness-codebase-design** (one adapter = hypothetical seam, two = real): F2 recommends a shared label matcher, and wayfind's 404 classification is left local.
- **harness-simplify / angle-altitude** ("one authoritative statement of a rule"; "residual accepted without its compensating control"): F1, F5 and F3, F4.
