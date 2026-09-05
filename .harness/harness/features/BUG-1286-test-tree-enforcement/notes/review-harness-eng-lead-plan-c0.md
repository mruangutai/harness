```yaml
VERDICT: PASS
DIGEST:
  headline: "Plan is architecturally sound — five of six design questions resolve SOUND; three findings would make a task fail as written (T-03's --against, T-03/T-04 vacuous verifies, SC-09 ungradeable), and one design claim (self-ownership protects a product checkout) rests on an unverified premise"
  team: eng-simplify-plus-architecture
  steps_run: 5
  cycles_used: 0
  members:
    - { step: simplify-reuse, persona: harness-backend-dev, verdict: PASS, headline: "2 findings: T-03's --against cannot reuse baseline()'s row parser; T-01 adds a 4th vocabulary spelling", files_touched: [".harness/harness/features/BUG-1286-test-tree-enforcement/notes/receipt-harness-backend-dev-simplify-reuse.md"] }
    - { step: simplify-simplification, persona: harness-dev-ops, verdict: PASS, headline: "T-05 hand-copies D-01..D-04 into DECISIONS prose and will ship stale wording; SC-05/06/11 each bundle independently-failable claims", files_touched: [".harness/harness/features/BUG-1286-test-tree-enforcement/notes/receipt-harness-dev-ops-simplify-simplification.md"] }
    - { step: simplify-efficiency, persona: harness-data-engineer, verdict: PASS, headline: "No findings — hot-path pair measured at ~46ms (25+21) over 2670 tracked files against a ~15s suite and 2 CI call sites", files_touched: [".harness/harness/features/BUG-1286-test-tree-enforcement/notes/receipt-harness-data-engineer-simplify-efficiency.md"] }
    - { step: simplify-altitude, persona: harness-dev-ops, verdict: PASS, headline: "Cost (a) closed; cost (b) narrowed with its compensating argument written nowhere; vocabulary and exception-reason text restated across intents", files_touched: [".harness/harness/features/BUG-1286-test-tree-enforcement/notes/receipt-harness-dev-ops-simplify-altitude.md"] }
    - { step: architecture-review, persona: harness-eng-lead, verdict: PASS, headline: "5 of 6 design questions SOUND; D-03's self-ownership clause is sound for worktree/vendored/nested-fixture but its product-checkout premise is unverified", files_touched: [".harness/harness/features/BUG-1286-test-tree-enforcement/runs/2026-09-04-01-eng/digest.md"] }
  must_fix:
    - "R1 (T-03 intent, plan.yaml:258-261): --against must not reuse baseline()'s row parser — it matches zero tree-audit rows, so --against would compare against an empty set and T-04's verify would report every measured row EXTRA."
    - "R2 (T-03 verify, T-04 verify): both verifies exit 0 on a vacuous audit (zero selected paths prints TOTAL 0 OUTSIDE 0 VIOLATIONS 0 and exits 0; an empty measured set against an empty parsed block also exits 0). Add a non-vacuity anchor."
    - "R6 (SC-09, BRIEF.md:88-92): as written the criterion cannot pass — T-05 commits after T-04, so the note's recorded 40-char SHA is necessarily an ancestor of review_sha and never equal to it."
  files_touched:
    - .harness/harness/features/BUG-1286-test-tree-enforcement/notes/receipt-harness-backend-dev-simplify-reuse.md
    - .harness/harness/features/BUG-1286-test-tree-enforcement/notes/receipt-harness-dev-ops-simplify-simplification.md
    - .harness/harness/features/BUG-1286-test-tree-enforcement/notes/receipt-harness-data-engineer-simplify-efficiency.md
    - .harness/harness/features/BUG-1286-test-tree-enforcement/notes/receipt-harness-dev-ops-simplify-altitude.md
    - .harness/harness/features/BUG-1286-test-tree-enforcement/runs/2026-09-04-01-eng/digest.md
  branch: "unknown — lead holds no shell and no branch was supplied on dispatch"
  open_questions:
    - { id: Q1, question: "Does an onboarded PRODUCT checkout track `.claude/skills/harness/bin/suite_layout.py` at that exact relative path? templates/settings.snippet.json installs seven hooks as ${CLAUDE_PROJECT_DIR}/.claude/skills/harness/bin/<script>, so a product checkout does carry that directory. If suite_layout.py is among the installed, tracked files, D-03's self-ownership clause is SATISFIED in a product checkout and is not what keeps it unaffected — what actually protects it is that violations() has exactly one caller (run-unit-tests.sh:33, pinned by an existing assertion) and that a product root already fails the pre-existing 'tests/unit contains no test-*.py' clause. Not answerable in this checkout: .harness/ holds only harness.json and team-config.yaml, so there is no fleet declaration and no second checkout to inspect. Bears on D-03's `because`, T-05's amendment bullet 3, and SC-11.", blocking: false }
    - { id: Q2, question: "eng-lead holds no write grant under `.harness/*/features/*/notes/**` (team-config.yaml:314-320 grants runs/*-eng/**, the two Expertise tiers, the observations log and .harness/notes/analysis-*.md). The dispatch instructed 'write your artifact under the feature's notes/ directory' and 'no file outside notes/ may be modified'; those two are mutually unsatisfiable for this persona, so the artifact went to the run dir this lead owns. Note that .harness/*/features/*/runs/** is gitignored, so this digest is on disk but will not be committed — if the panel needs it tracked, the orchestrator should copy it.", blocking: false }
  escalations: []
  expertise_update: []
  sc_status: []
artifact: .harness/harness/features/BUG-1286-test-tree-enforcement/runs/2026-09-04-01-eng/digest.md
```

# Pass 1 — the four angles, one line each

| angle | reader | result |
|---|---|---|
| reuse | backend-dev | **1 accepted finding** (R1: `--against` cannot reuse `baseline()`), 1 **rejected** (see below), no finding on 3 of 5 checks |
| simplification | dev-ops | **1 accepted, merged** (T-05 hand-copies D-01..D-04 → R3) + **3 SC-bundling splits** (R11); citations and `files:`/`traces:`/`change_type` clean |
| efficiency | data-engineer | **EMPTY PASS, measured**: `git ls-files -z` 25ms + `git rev-parse --show-toplevel` 21ms = ~46ms per runner invocation over 2670 tracked files, against a ~15s integration kind and exactly 2 scripted call sites (`.github/workflows/tests.yml:86,92`) plus `validate-digest.py:1613-1665`. Cost justified; no cheaper shape that does not lose fail-closed behaviour |
| altitude | dev-ops | **1 accepted, corrected** (R5: cost (b) is narrowed, not closed, and the compensating control is written nowhere) + **1 accepted, reduced** (R13) + **1 rejected** (seam), residuals in `## Verification gaps`, D-04 and D-05 each `leave` |

**Two member findings rejected at this tier, with reasons:**

- **REUSE check 3** — deriving `test_shapes` (`suite_layout.py:20`) and the bin glob tuple (`:30`) from the new `NAME_PATTERNS`/`SOURCE_EXTENSIONS` is **not** de-duplication, it is a behaviour change. `NAME_PATTERNS` includes `probe-*`; feeding it into the under-`tests/` misplacement clause makes `violations()` report `tests/manual/probe-omp-session-accessor.py` as "test file is not selected by the runner", which contradicts DEC-213 (probes live in `tests/manual/**`) and reddens the real-root assertion at `tests/unit/test-suite-layout.py:38`. The bin tuple's extension-free `probe-*` is likewise deliberate (issue #1286 planning question 1 names it). Three spellings, three different vocabularies, one per clause. **No plan change; recorded so a later reader does not re-derive it.**
- **ALTITUDE Q3** — a `violations(root, tracked_paths_fn=...)` injection point is one adapter across a seam nothing varies across except the tests, and it would weaken exactly the coverage issue #1286 demands ("coverage demonstrates the tracked-file distinction rather than planting only an untracked filesystem file"). A test handed a path list proves nothing about `git ls-files`. **Declined; the five real-git fixtures are the point, not the cost.**

# Pass 2 — architecture review of the planned design

**SOUND, resolved from the code:** D-03's activation for a Harness worktree; D-03 for a vendored copy; D-03 for a nested fixture root; D-04's de-duplication is expressible; the T-01→{T-02,T-03}→T-04, T-05←{T-01,T-02} DAG. **Not settled:** whether self-ownership is what protects a product checkout (Q1 above).

- **D-03, worktree — SOUND.** `.gitignore` excludes only `.claude/settings.local.json`, `.claude/worktrees/` and the settings backup, so `.claude/skills/harness/bin/suite_layout.py` is tracked; in a linked worktree `git ls-files` lists the branch's set and `rev-parse --show-toplevel` is the worktree root. The clause is live in this very checkout, which is what makes `tests/unit/test-suite-layout.py:38` real coverage.
- **D-03, vendored copy — SOUND.** A harness vendored at `vendor/harness/**` leaves the outer index carrying `vendor/harness/.claude/skills/.../suite_layout.py`, never that path relative to the outer root; and `vendor/harness/.git` does not exist, so the clause is inert twice over.
- **D-03, nested fixture root — SOUND, and the toplevel check is load-bearing (severity: low, protective).** `git ls-files` is cwd-scoped, so an outer index cannot be *scanned*; the real risk the toplevel check closes is different from the one T-01's intent states — with `TMPDIR` inside a checkout, a `.git`-replaced-by-empty-dir fixture would enumerate empty, fail self-ownership, and go **silently inert**, which is the opposite of SC-04 and would redden T-02 case 4. **R10:** pin this in D-03 so a future optimizer does not move the toplevel comparison after the self-ownership membership test.
- **D-04 de-duplication — SOUND, wording gap (severity: low-med).** The bin clause emits absolute `Path` objects (`suite_layout.py:29-33`), the new clause emits repo-relative POSIX strings; "is not already reported by the bin clause" (plan.yaml:143) crosses that type boundary without naming the bridge, and the cheapest wrong reading is a substring test. **R8.** The two clauses' vocabularies also differ deliberately, so dedup only bites on the intersection: `bin/probe-x.md` is reported by the bin clause only, `bin/test_x.py` by the new clause only.
- **D-01 versus `harness.json` `test_kinds.unit.detect` — DIVERGENCE, currently empty (severity: med).** `detect` is extension-agnostic (`**/*.test.*`, `**/*_test.*`); D-01 is extension-restricted. A tracked `notes/session_test.md` or `evidence/run.test.jsonl` is therefore discovered as a `unit` test by the kind map **and** legal under the new vocabulary **and** executed by no runner — the exact defect BRIEF.md's Problem section names, surviving in a narrower form. It is empty at the pinned SHA: all eight out-of-vocabulary rows are `probe-*`, which no `detect` glob matches. The compensating control exists and is not stated: T-03's audit selects **without** the extension filter, so any such file appears as an `out-of-vocabulary` row and is dispositioned in T-04's note. **R5** records it truthfully. This corrects the altitude reader's stronger claim that the glob becomes vacuous — it does not.
- **D-05 coupling to FEAT-44's evidence — real, and deliberate; one consequence unmanaged (severity: med).** Archiving or removing `.harness/harness/features/FEAT-44-omp-context-advisory/evidence/probe-session-accessors.ts` makes `violations()` emit "documented exception is no longer tracked" on **every** `run-unit-tests.sh` invocation, repository-wide, until `suite_layout.py` is edited — a file granted only to backend-dev and dev-ops, not to whoever archives a feature. That loudness is D-02's stated intent and should stay. What should not stay is T-01 unit case 7 pinning the FEAT-44 path as a literal: archival then produces two failures, one of them a puzzling test failure. **R7** makes the case derive the path from the registry; **R12** puts the failure mode and its remedy owner into D-05's `because`.
- **The DAG — SOUND.** Acyclic, a real topological order, and no `verify:` asserts something a predecessor deletes or a successor must make true. T-01's `--check-layout` clause is satisfiable at T-01 time because T-01 itself seeds the registry entry; T-04's `--against` compares a working-tree note against `git ls-tree HEAD` and passes with the note uncommitted, since the note is not test-shaped.
- **The five `verify:` commands — three sound, two vacuously passable (severity: med).** T-01 (0.1s unit file + `--check-layout`) and T-02 (~4s, measured basis 1.36s for five existing cases) return real pass/fail well under 60s from the root. T-05's `grep -q "Amended by BUG-1286-test-tree-enforcement"` is **non-vacuous — measured, that string occurs zero times in `DECISIONS.md` today** — and its `gen-decisions-index.py --stdout | diff -` clause genuinely binds index sync; but nothing in it asserts SC-10's requirement that the **DEC-213 row** state the repository-wide invariant, because the row's tail right of `" :: "` is hand-written (`DECISIONS-INDEX.md:213` today reads "one layout predicate guards the tree"). **R4.** T-03 and T-04 are the two that can pass on nothing: **R2**.

# Recommendations, routed to pm verbatim

Each names the artifact, the exact id, and the replacement wording.

**R1 — `plan.yaml`, T-03 intent, lines 258-261 (med, must_fix).** Replace with:
> With `--against`, extract the fenced text block from the given note using the same `` ```(?:text)?\n(.*?)\n``` `` pattern `baseline()` uses at `suite-census.py:24`, but parse each line as `path` then a tab then `disposition` — do **not** call `baseline()`, whose row regex `(test-.*\.py)\s+(\d+)` matches no tree-audit row and would silently compare the measurement against an empty set. Compare the row set to the measured rows, print each row present in one side only prefixed MISSING or EXTRA, and exit 1 on any difference.

**R2 — `plan.yaml`, T-03 `verify:` and T-04 `verify:` (med, must_fix).** Both need a non-vacuity anchor; a zero-match selection prints `TOTAL 0 OUTSIDE 0 VIOLATIONS 0` and exits 0. T-03:
> ```
> out=$(python3 tests/manual/suite-census.py tree-audit --ref HEAD) && printf '%s\n' "$out" | grep -q 'probe-session-accessors\.ts.*documented-exception'
> ```
T-04, same shape, preserving the `--against` exit code:
> ```
> out=$(python3 tests/manual/suite-census.py tree-audit --ref HEAD --against .harness/harness/features/BUG-1286-test-tree-enforcement/notes/qa-tree-audit.md) && printf '%s\n' "$out" | grep -q 'probe-session-accessors\.ts.*documented-exception'
> ```
Keep both as literal `|` blocks (DEC-182).

**R3 — `plan.yaml`, T-05 intent, lines 316-333 (med).** Merged from the simplification and altitude readers. Do not have the documentor re-enumerate five patterns and seven extensions in a decision record — that is precisely how DEC-213's bin-only enumeration went stale. Replace amendment bullets 1 and 3's enumerations with:
> - the predicate additionally refuses every tracked test-shaped file outside `tests/`, where the authoritative vocabulary is `NAME_PATTERNS` and `SOURCE_EXTENSIONS` in `.claude/skills/harness/bin/suite_layout.py` — name the module as the authority and do not re-list the patterns or extensions here; state only the consequence, that records of probes carrying a non-source extension (Markdown, JSONL) are deliberately out of scope;
> - the authoritative tracked set is the Git index read in the root, active only under the three conditions `suite_layout.py`'s repository-wide clause tests (see that module), which scope enforcement to a checkout that ships this rule;

**R4 — `plan.yaml`, T-05 `verify:` (med).** Add a clause binding SC-10's second half, and instruct the documentor to confirm the asserted string occurs zero times in `DECISIONS-INDEX.md` before the edit:
> ```
> grep -q "Amended by BUG-1286-test-tree-enforcement" .harness/harness/docs/DECISIONS.md && grep -q '^- DEC-213 @.* :: .*tracked test-shaped file outside' .harness/harness/docs/DECISIONS-INDEX.md && python3 .claude/skills/harness/bin/gen-decisions-index.py --stdout | diff - .harness/harness/docs/DECISIONS-INDEX.md && python3 .claude/skills/harness/bin/check-decision-anchors.py
> ```

**R5 — `BRIEF.md`, `## Verification gaps` (med).** Add:
> `harness.json`'s `unit.detect` remains extension-agnostic (`**/*.test.*`, `**/*_test.*`) while D-01's vocabulary is restricted to source extensions, so a tracked `*_test.md` or `*.test.jsonl` outside `tests/**` would be discovered as a `unit` test by the kind map, permitted by the guard, and executed by no runner. That class is empty at the reviewed revision — every out-of-vocabulary match is `probe-*`, which no `detect` glob matches — and it is measured rather than unseen: T-03's audit selects without the extension filter, so any such file appears as an `out-of-vocabulary` row and is dispositioned. Correcting the `detect` text is out of scope (SC-11 freezes `harness.json`); this records the residual and its control.

**R6 — `BRIEF.md`, SC-09 (med, must_fix).** T-05 commits after T-04, so the note's recorded SHA is an ancestor of `review_sha`, never equal. Replace the grading sentence with:
> Graded by reading `git show <review_sha>:.harness/harness/features/BUG-1286-test-tree-enforcement/notes/qa-tree-audit.md` against a re-run of the audit at `review_sha`: the fenced row set must be identical, and the SHA the note records must be an ancestor of `review_sha` with no tracked vocabulary match added or removed between them.

**R7 — `plan.yaml`, T-01 intent case 7 (line 179-181), and `BRIEF.md` SC-07's last sentence (med).** T-01 case 7:
> 7. the live registry is load-bearing: read the single entry's path from `suite_layout.DOCUMENTED_EXCEPTIONS` first and assert against that value rather than a literal, so a later registry change cannot redden this case; with `DOCUMENTED_EXCEPTIONS` temporarily set to `()` assert `violations(ROOT)` contains that path, and with it restored assert `violations(ROOT) == []`.
SC-07 last sentence:
> Removing the registry's single live entry makes the real root report that entry's own path.

**R8 — `plan.yaml`, T-01 intent line 143 (low-med).** Name the bridge across the type boundary:
> …is not already reported by the bin clause — compute that set once as `{p.relative_to(root).as_posix() for p in set(planted)}` and test membership against it, never a substring of the bin clause's message, which carries an absolute path…

**R9 — `plan.yaml`, D-03 `because`; T-05 amendment bullet 3; `BRIEF.md` SC-11 (low-med, pending Q1).** Do not credit self-ownership alone with keeping a product checkout unaffected. Name both controls:
> …the ownership condition scopes repository-wide enforcement to a checkout whose own index carries this predicate at that exact relative path, and `violations()` has exactly one caller — Harness's own `run-unit-tests.sh` — so a product checkout is reached by neither the clause nor the runner.

**R10 — `plan.yaml`, D-03 choice (low).** Append:
> …the toplevel comparison is a precondition of enumeration and must not be moved after the self-ownership test: a fixture root nested inside another checkout enumerates empty, which would fail self-ownership and go silently inert instead of fail-closed.

**R11 — `BRIEF.md` SC-05, SC-06, SC-11 (low).** Split each into independently reportable criteria as the simplification receipt sets out — with one correction: **do not drop** SC-05's second clause. "No `active` entry in `test_kinds` matches `tests/manual`" is the only criterion binding REQ-04's manual-discovery half, and "`harness.json` is unchanged" does not assert it (the property could be false and unchanged). Keep it as its own criterion, `verify: automated evidence: unit`.

**R12 — `plan.yaml`, D-05 `because` (low).** Append:
> …and the coupling is accepted with its consequence stated: if that evidence file is ever archived or removed, the registry entry reports "no longer tracked" on every runner invocation until `suite_layout.py` — granted to backend-dev and dev-ops, not to whoever archives a feature — is edited.

**R13 — `plan.yaml`, T-04 intent line 289 (low).** Reduced from the altitude reader's ask; keep the note in the author's own words, add the authority:
> …for the FEAT-44 probe, that it is the documented exception carried by D-05 and consumed by `tests/manual/probe-omp-session-accessor.py`, citing `suite_layout.DOCUMENTED_EXCEPTIONS` as the authority for the classification…

# Record

No `state.yaml` was seeded for this run: the four angle dispatches went out as one wave before a run directory existed, and writing a checkpoint after the fact would falsify the ordering it exists to record. The per-angle detail lives in the four receipts under the feature's `notes/`, which are tracked; this digest is the only file in the run dir. One cosmetic defect worth naming: `receipt-harness-data-engineer-simplify-efficiency.md` ends with leaked tool markup (`</content>`, a `parameter name="i"` line) after its last section — content is complete, the tail is noise.
