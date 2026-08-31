```yaml
VERDICT: PASS
DIGEST:
  headline: The feature.json merge-helper gap was an unexamined omission, not a decided boundary — DEC-199's rule covers it and FEAT-32's implementation did not; all five Python writers are now on the locked core, but the incident's own silence traces to an untested OMP-bridge edit route that no code I own can reach.
  team: eng
  steps_run: 4
  cycles_used: 2
  members:
    - { step: probe, persona: harness-dev-ops, verdict: PASS, headline: "check-domain.sh's shape gate catches this exact corruption (exit 2, 'not valid JSON'); the hole is a silent zero-path in the OMP bridge's edit routing, untested end-to-end", files_touched: [".harness/harness/features/FEAT-44-omp-context-advisory/notes/receipt-harness-dev-ops-devopsprobe.md"] }
    - { step: build-c1, persona: harness-backend-dev, verdict: PASS, headline: "locked schema-validated feature.json writer shipped; gh-sync rewiring declined on a blocker that did not exist", files_touched: [".claude/skills/harness/bin/feature_json_write.py", ".claude/skills/harness/bin/feature-json-merge.py", ".claude/skills/harness/bin/test-feature-json-merge.py", ".claude/skills/harness/bin/run-unit-tests.sh"] }
    - { step: build-c2, persona: harness-backend-dev, verdict: PASS, headline: "gh-sync.py's three write sites on the locked writer, _atomic_write deleted, ratchet's dirty-base case now under test", files_touched: [".claude/skills/harness/bin/gh-sync.py", ".claude/skills/harness/bin/test-gh-sync.py", ".claude/skills/harness/bin/test-feature-json-merge.py"] }
    - { step: build-c3, persona: harness-backend-dev, verdict: PASS, headline: "factory_decompose.write_factory rewired; last unlocked Python writer of feature.json closed", files_touched: [".claude/skills/harness/bin/factory_decompose.py", ".claude/skills/harness/bin/test-factory-decompose.py"] }
  must_fix: []
  files_touched:
    - .claude/skills/harness/bin/feature_json_write.py
    - .claude/skills/harness/bin/feature-json-merge.py
    - .claude/skills/harness/bin/test-feature-json-merge.py
    - .claude/skills/harness/bin/gh-sync.py
    - .claude/skills/harness/bin/test-gh-sync.py
    - .claude/skills/harness/bin/factory_decompose.py
    - .claude/skills/harness/bin/test-factory-decompose.py
    - .claude/skills/harness/bin/run-unit-tests.sh
    - .harness/notes/analysis-stale-anchor-write-hazard.md
  branch: fix/stale-anchor-write-hazard
  open_questions:
    - { id: Q1, question: "Did the PostToolUse gate fire on the 2026-08-30 edit and go unread, or did it never run? Undecidable from a static tree — needs one live session with postDomain's runner wrapped, one real line-anchored edit against a real feature.json, logging the literal event.input. This is the single fact that discriminates 'a real hole' from 'a report nobody acted on'.", blocking: false }
    - { id: Q2, question: "DEC-199's 'exactly four consumers' clause is now false — there are six. The entry needs an amendment recording feature_json_write.py and its two callers. Decisions are approval-gated and not the squad's to write.", blocking: false }
    - { id: Q3, question: "test-factory-decompose.py's total check count fell 188 -> 160 because case 22's os.replace/open monkeypatch hooks no longer intercept a primitive that has moved into harness_merge. The property they pinned (no truncating open, no partial file) is now pinned once in the shared core rather than per-caller. Confirm that migration is acceptable rather than a coverage loss.", blocking: false }
  escalations: []
  expertise_update: []
  sc_status: []
artifact: .harness/notes/analysis-stale-anchor-write-hazard.md
```

# Stale-anchor write hazard — diagnosis and remediation

**Bottom line.** The hazard is **structural**, and it is structural in two independent places. The
place the dispatch hypothesised — `feature.json` alone among co-owned artifacts had no locked
merge helper — is real, verified, and now closed for every Python writer. The place that actually
made the 2026-08-30 incident *silent* is different and sits inside the DEC-174 boundary: the route
from an OMP `edit` tool result to `check-domain.sh --post` is a single unguarded string parse whose
empty return invokes zero gates and logs nothing, and no test in this repository exercises it.

## 1. Blast radius — every file written by BOTH a harness tool AND an agent editor

Derived from a sweep of `.claude/skills/harness/bin/` for `os.replace|json.dump|open(...,"w")`,
then read at each site. Not inferred.

| File | Tool writer(s), at source | Atomic | Locked / merge helper | Agent hand-edits it |
|---|---|---|---|---|
| `.harness/*/features/*/feature.json` | `gh-sync.py` `_record_status`/`_record_pr`/`save_recorded`; `factory_decompose.py` `write_factory:138-186` | yes — **two private copies** of mkstemp+fsync+os.replace | **NONE (was)** → now `feature_json_write.py` | **yes** — orchestrator/main session. **THE INCIDENT** |
| `.harness/*/features/*/plan.yaml` | `plan-merge.py` | yes | yes — `harness_merge` (DEC-199) | pm |
| `.harness/*/features/*/observations/*.md` | `observations-merge.py` | yes | yes | agents append |
| `.harness/expertise/*.md`, `.harness/*/expertise/*.md` | `expertise-merge.py` | yes | yes | agents, distillation only |
| inflight claim registry | `inflight_registry.py` | yes | yes (1.0 s timeout) | never |
| `.claude/settings.json` | `merge-settings.py:327-331` tmp+`os.replace` | yes | **no lock** | main session — DEC-174 |
| `.harness/harness.json` | `upgrade-config.py` generic merge | via same shape | **no lock** | dev-ops |
| `.harness/harness/docs/DECISIONS-INDEX.md` | `gen-decisions-index.py:448` — **truncating `open(...,"w")`, no atomic replace** | **no** | no | generated; agents edit `DECISIONS.md` |
| `.harness/*/features/*/STATE.md` | none found | n/a | n/a | agents only — no co-ownership |
| `.harness/*/features/*/runs/*/state.yaml` | none found | n/a | n/a | leads only — no co-ownership |
| `.harness/logs/*.jsonl` | `gh_cost_log.py:143` | append-only | no | never |
| `.harness/.shape-sweep-stamp` | `check-domain.sh:1532` | mtime only | no | never |

**The interesting cell is exactly the one the dispatch predicted**, and it is the only one:
`feature.json` was the sole file with a tool writer, no merge helper, and routine agent
line-anchored editing. Two of the batch context's starting candidates were false leads and are
recorded as such: `board-station.py` does not write `feature.json` at all (zero hits), and
`STATE.md` and `state.yaml` have no tool writer, so neither is co-owned.

**Adjacent finding, out of scope, noted not fixed:** `gen-decisions-index.py:448` writes
`DECISIONS-INDEX.md` through a truncating `open(path, "w")` — the exact shape FEAT-14 fix1
eliminated from `save_recorded` because it makes a zero-byte window observable on every call. No
agent hand-edits the generated index, so it is not co-owned and not this hazard; it is a latent
one of its own.

## 2. The central question — decided boundary, or oversight?

**Oversight.** No decision text excludes `feature.json`, and DEC-199's own ruling sentence covers
it on its face:

> "Every shared artifact two contexts can write at once goes through one locked, union-merging
> core, `harness_merge`" — `DECISIONS.md:6888`

The "exactly four consumers — `plan-merge.py`, `observations-merge.py`, `expertise-merge.py` and
`inflight_registry.py`" clause at `DECISIONS.md:6891-6893` is the scope FEAT-32 *implemented*, not
a carve-out it *ruled*. The evidence that the omission was unexamined rather than decided is in
FEAT-32's own research note, `notes/research-FEAT-32-merge-class.md:12-15`, which enumerated the
merge class as `plan.yaml`, the observation log and the expertise files and never considered
`feature.json` — while every one of that feature's handoff notes lists `feature.json` as an
artifact the run *touched*. It was in front of the feature the whole time as an object, never as a
subject. **The rule covered it and the implementation did not.** That is a stronger statement than
a design suggestion and it is what justified the remediation below, independent of the incident.

## 3. Structural or operator error?

**Structural, on evidence, and the incident is not what establishes it.**

- The class is established by §1's enumeration: `feature.json` had **two** unlocked whole-document
  read-modify-writers (`gh-sync.py`, `factory_decompose.py:138-186`) over one file plus routine
  agent editing. Two whole-document writers interleaving is a lost update regardless of whether one
  has ever been observed. One data point does not establish a class; the source enumeration does.
- **The detection layer is not the weak part.** `harness-dev-ops` reproduced the incident's exact
  damage (a deleted closing brace at line 33 of a real `feature.json`) and both the PostToolUse
  named-`Edit` route and the PostToolUse `Bash` sweep route exited **2** with
  `not valid JSON: Expecting ',' delimiter: line 33 column 5 (char 764)`. `jsonschema` 4.26.0 is
  importable; `validate-feature-json.py` scans 40 files at exit 0. This is not an environment where
  the checker is silently absent.
- **The weak part is the delivery route, and it is untested.**
  `.omp/extensions/harness-hooks.ts:258-263` routes an `edit` tool result through
  `extractEditPaths(input.input)` and `.map()`s the result into runner calls. An empty array
  produces zero runner invocations, `firstBlock([])` returns `undefined`, and nothing is logged —
  no error, no stderr, no exit code, because no process was ever spawned. `omp-hooks.test.ts` has
  43 passing cases; **none** constructs a `tool_result` with `toolName: "edit"` and asserts the
  gate is reached, although the same file does exactly that for `toolName: "task"` at `:265` and
  `:299`. A silent zero matches the incident's description ("nothing refused it") far better than a
  suppressed report does.
- **The operator-error reading is not supported.** No skill or doc names this failure mode. There
  is no guidance saying "re-read a co-owned state file before applying a line-anchored edit", and
  before this change there was no structured writer to point at instead. Guidance that does not
  exist cannot have been ignored.
- Two candidate suppressors were checked and ruled out: `SWEEP_SKIP_CLEAN_TRACKED` skips only
  files byte-identical to HEAD, and the incident's file was modified-vs-HEAD; the
  `.shape-sweep-stamp` high-water mark suppresses only files older than the last sweep, and a
  fresh corrupting write is never older than the mark.

**Honest residual (Q1).** I cannot discriminate "the gate never ran" from "the gate ran and its
report was not acted upon" from a static tree. The discriminating probe is named in Q1 and in the
dev-ops receipt.

## 4. Findings, each labelled by boundary and owner

### OUTSIDE the DEC-174 boundary — executed by this squad, tests green

| # | What | Evidence |
|---|---|---|
| F1 | `feature_json_write.py` — one public locked read-modify-write on `harness_merge.locked_update`, `require_destination`-checked to `.harness/*/features/*/feature.json`, validating the candidate with `feature_schema.problems_for_text` **before** the atomic replace and refusing without writing. Plus `feature-json-merge.py` (`set-key`/`append-run`/`set-github`) so no caller hand-edits the document. | `test-feature-json-merge.py` **34/34**, incl. concurrency, JSON-decode refusal, schema refusal, destination refusal, byte-identical-after-refusal |
| F2 | `gh-sync.py`'s three write sites rewired; `_atomic_write` and its `tempfile` import deleted, no shim. Absent-file tolerance, `save_recorded`'s verbatim `SystemExit`, and `pr` idempotence all preserved, each re-checked inside the lock against the new TOCTOU window. | `test-gh-sync.py` **273 → 273** checks, ALL PASSED |
| F3 | `factory_decompose.py:write_factory` rewired; its private mkstemp/fsync/os.replace deleted. Absent-file contract converged onto `save_recorded`'s refusal after checking every caller — none is a legitimate first writer of a `feature.json`. | `test-factory-decompose.py` **160/160**, + 3 red-first regression guards (fork-based lost update, schema-ratchet refusal, destination refusal) |

**A deliberate policy choice inside F1, recorded because it is a real trade-off.** Literal
"any schema problem refuses" would refuse nearly every `feature.json` already on disk — documents
predating DEC-191's eight required keys. The module therefore refuses only a problem **not already
present on the base**; an absent or unparseable base gives a zero baseline and is strict. This is
the same "enforce going forward, not retroactively" shape `feature_schema.py`'s own
`RUNS_AGENT_EXEMPT`/D-23 already uses for this schema. Its discriminating dirty-base behaviour is
pinned by cases 11–13, added after cycle 1 shipped it untested.

**None of this closes the literal incident, and the squad says so first.** A line-anchored edit
splices bytes and never enters Python; no library placed at a Python call site can intercept it.
F1–F3 close the DEC-199 implementation gap and the lost-update hazard between Python writers. They
make the *correct* path exist so guidance has somewhere to point.

### INSIDE the DEC-174 boundary — specified, main session must execute

**S1 — the missing integration assertion.** File
`.claude/skills/harness/bin/omp-hooks.test.ts`. Add a case firing a `tool_result` event through
`registerHarnessHooks` with `toolName: "edit"` and
`input: { input: "*** Begin Patch\n[a.ts#A1B2]\nPUT 1.=1:\n+x\n*** End Patch\n" }` against a fake
runner; assert exactly one recorded call with script `check-domain.sh`, args containing `--post`,
and `payload.tool_input.file_path === "a.ts"`. Mirror the `toolName: "task"` cases at `:265-268`
and `:299-302`. Proof: `bun test ./.claude/skills/harness/bin/omp-hooks.test.ts` goes 43 → 44.

**S2 — make the zero-path case observable.** File `.omp/extensions/harness-hooks.ts`, `postDomain`
edit branch `:258-263`. Today `extractEditPaths` returning `[]` is byte-for-byte indistinguishable
from a gate that ran and passed. Behaviour: when `toolName === "edit"` and the extraction yields no
paths, append a **non-blocking** advisory to the tool result naming the tool and the fact that no
target path could be extracted, so the gate's absence is visible in the transcript. It must not set
`isError` — an advisory must never cost a gate, the property `:797-801` already protects. Proof: a
`tool_result` with `toolName: "edit"` and `input: { input: "not a patch" }` appends the advisory
and the fake runner records **zero** `check-domain.sh` calls; the existing well-formed-patch case
appends nothing.

**S3 — the guidance that does not exist.** `.claude/skills/harness/**/SKILL.md` is in no agent's
`domain:` and absent from `shared:`, so it is writable by no agent — main-session-direct by
construction, not by preference. Add to the orchestrator playbook (`skill://harness`), which owns
`feature.json` per DEC-119: *never hand-edit `feature.json`; use
`.claude/skills/harness/bin/feature-json-merge.py`, which takes the lock, validates and refuses
rather than corrupting. A line-anchored edit's anchors are stale the moment any tool rewrites the
file, and `gh-sync.py` rewrites it on every status transition.* This is the one remedy that
addresses the literal incident.

**S4 — DEC-199 amendment (Q2).** The "exactly four consumers" clause is now false; there are six.
Decisions are approval-gated and belong to the operator, not to this squad.

## 5. Process defects observed, for the harness owner

- `harness-dev-ops` wrote its receipt into the **main checkout**, not its assigned worktree —
  `/Users/molchairuangutai/GitHub/harness/.harness/harness/features/FEAT-44-omp-context-advisory/notes/receipt-harness-dev-ops-devopsprobe.md`,
  where its DIGEST reported a worktree-relative path. `harness-backend-dev` made the same mistake
  twice mid-run and caught and reverted it. This is precisely the failure mode DEC-199's
  first-line feature declaration exists to name: an agent's process working directory does not
  follow its assignment, and a relative path silently resolves against the wrong tree. A dispatch
  instruction to use absolute paths is prose, not an instrument.
- A member declined the largest half of its task on a stated domain blocker that did not exist —
  it holds `.claude/skills/harness/bin/**`, which covered the file it believed was ungranted. One
  send-back resolved it. Cost: one member spawn, at lead tier, rather than a feature cycle.

---

# Cycle 4 — the c3 regression, and its fix

```yaml
VERDICT: PASS
DIGEST:
  headline: c3's PASS was false — it rewired write_factory onto the shared core while hand-copying two of gh-sync's caller policies onto it, breaking 18 checks in test-factory-integration.py; both policies are now genuinely caller-owned and the full unit suite runs clean at 0 FAIL.
  team: eng
  steps_run: 1
  cycles_used: 1
  members:
    - { step: build-c4, persona: harness-backend-dev, verdict: PASS, headline: "write_factory takes an explicit feat_id opt-in to create a schema-clean feature.json and passes its own laxer tail_regex; gh-sync's never-create guarantee untouched because it never lived in the shared core", files_touched: [".claude/skills/harness/bin/feature_json_write.py", ".claude/skills/harness/bin/factory_decompose.py", ".claude/skills/harness/bin/test-factory-decompose.py", ".claude/skills/harness/bin/test-feature-json-merge.py", ".harness/harness/features/FEAT-44-omp-context-advisory/notes/receipt-harness-backend-dev-c4.md"] }
  must_fix: []
  files_touched:
    - .claude/skills/harness/bin/feature_json_write.py
    - .claude/skills/harness/bin/factory_decompose.py
    - .claude/skills/harness/bin/test-factory-decompose.py
    - .claude/skills/harness/bin/test-feature-json-merge.py
    - .harness/harness/features/FEAT-44-omp-context-advisory/notes/receipt-harness-backend-dev-c4.md
    - .harness/notes/analysis-stale-anchor-write-hazard.md
  branch: fix/stale-anchor-write-hazard
  open_questions:
    - { id: Q4, question: "check-domain.sh grants harness-backend-dev only .harness/*/features/*/notes/receipt-harness-backend-dev-*.md, so the flat .harness/notes/ path this whole effort uses for its receipts is writable by no member. c4's receipt therefore landed under FEAT-44-omp-context-advisory while c2/c3's sit in .harness/notes/. Either team-config.yaml grants the flat path or the earlier receipts move; a manifest grant is not a lead's call.", blocking: false }
    - { id: Q5, question: "C3-3 was deliberately retired: 'write_factory refuses a path outside a features directory' is no longer true, by design. The property it pinned (the SHARED core's default is strict and creates nothing) is now pinned in test-feature-json-merge.py case_14. Confirm that relocation is acceptable rather than a coverage loss — same shape as Q3.", blocking: false }
  escalations: []
  expertise_update: []
  sc_status: []
artifact: .harness/notes/analysis-stale-anchor-write-hazard.md
```

**Bottom line.** c3 was right to share the lock/tempfile/fsync/replace core and wrong about which
policies belong to it. It hand-copied `gh-sync.py`'s **never-create** rule into `write_factory`
and inherited the shared **path-shape** regex, neither of which is true of `factory_decompose`.
The result passed `test-factory-decompose.py` and broke the factory's end-to-end suite.

## What was actually wrong — three policies, not two

1. **Never-create.** c3's docstring justified the refusal with "no caller of `write_factory` is
   ever legitimately the FIRST writer … the orchestrator instantiates it well before decompose
   ever runs." **That premise is false.** `factory_decompose` is a standalone CLI entry point and
   its own fixtures run `decompose` against a dir holding only `plan.yaml`
   (`test-factory-integration.py:867-870`).
2. **Path shape.** `FEATURE_JSON_TAIL` demands `.harness/(<repo>/)?features/(FEAT|BUG)-*/`.
   Other fixtures point the CLI at a bare `<tmp>/feature/` dir (`:635-636`, `:708-709`).
3. **The trap nobody had hit yet.** `write_feature_json`'s baseline is *monotonic non-regression*,
   and an absent base contributes an **empty** baseline — so a created document must be fully
   schema-clean. Lifting the never-create rule alone would have traded `MergeRefusal(9)` for
   `MergeRefusal(11)`. This was stated in the dispatch precisely so the fix would not stop halfway.

## The fix, and why it is not a weakening

Both policies are now **caller-owned**, which is where they always belonged — the deep, genuinely
shared part is the lock/tempfile/fsync/replace machinery, not the caller's admission rules.

- `write_factory(feat_dir, factory, feat_id=None)` — `feat_id` is the creation opt-in. Omit it and
  an absent base still refuses, code 9 (`factory_decompose.py:194-195`). All five internal call
  sites supply it, derived from `plan.yaml`'s validated `feature:` key.
- Creation builds a genuine eight-required-key document (`factory_decompose.py:196-206`) matching
  `templates/feature.json`'s defaults, so it passes the **unmodified** validator honestly. No
  schema bypass, no special-case.
- `write_feature_json(..., tail_regex=None)` — additive, defaulting to `FEATURE_JSON_TAIL`
  (`feature_json_write.py:84, 144-146`). `write_factory` passes its own basename-only regex; the
  resolved path must still be named `feature.json`, and `require_destination`'s realpath resolution
  still defeats a symlink/`..` escape.

**`gh-sync.py` was not edited at all**, and its never-create guarantee is unaffected *by
construction*: that rule never lived in the shared core — each of its three call sites refuses
before ever producing candidate text — and the one new parameter has an unchanged default, so its
call sites are byte-for-byte unaffected. Verified at source by the lead, not taken on report.

**The guard test that would redden if the guarantee were removed:** `test-gh-sync.py`'s
`_dabsentT02` case, ~`:2079`, *"save_recorded refuses, loudly, when feature.json is absent"*.
Untouched by this fix.

## Evidence

| Check | Observed |
|---|---|
| `test-factory-integration.py` | **18 of 123 failing → 131/131 pass** |
| `test-factory-decompose.py` | 163/163 |
| `test-gh-sync.py` | ALL PASSED |
| `test-feature-json-merge.py` | 37/37 |
| `test-harness-merge.py` | 18/18 |
| `run-unit-tests.sh` (full, `--kind` defaults to `all`) | **exit 0, `FAIL` count = 0** |

New cases were confirmed RED first, failing as `TypeError: unexpected keyword argument` — red for
the intended reason. Both directions are pinned: C4-1 (creation with `feat_id` succeeds,
schema-clean) and C4-2 (the same call without `feat_id` still refuses, code 9, nothing created),
plus `test-feature-json-merge.py` case_14 on the shared core's own default.

**Evidence form, stated plainly.** Leads hold no shell, so the suite numbers above were observed by
`harness-backend-dev` and reported verbatim. What the lead verified independently, at source:
(a) `test-factory-integration.py` is in `INTEGRATION_SCRIPTS` and `--kind` defaults to `all`, so
the full-suite run genuinely **executes the file that regressed** — the coverage question c3's
narrow verification got wrong; (b) the runner's failure line is literally `echo "FAIL $s"` with
`failures>0 → exit 1`, so `^FAIL ` is the correct counting expression and exit 0 corroborates it
independently; (c) the `tail_regex` default and the `write_factory` creation path, read directly.

**One unexplained discrepancy, recorded rather than smoothed:** the ticket reported 19 pre-fix
failures; the reproduction found 18 of 123, with both refusal shapes and both root causes matching.
The member attributed the delta to concurrent sibling work. That explanation is unverified. It does
not affect the verdict — the post-fix state is the whole suite green — but it is not a fact.

## Advisory, not blocking

`factory_decompose` can now write a `feature.json` anywhere its CLI positional points, subject only
to the basename check. This is a real loosening, and it is justified: the positional argument was
always unconstrained, every other file the tool reads and writes there (`plan.yaml`, `BRIEF.md`)
was always unconstrained, and the narrower rule was an artifact of c3 rather than a decided
boundary. The strict default remains in force for every other caller.

`.agents/skills/harness/bin/factory_decompose.py` — the duplicate copy — was left untouched and
now drifts from this fix, the same accepted gap c3 recorded.
