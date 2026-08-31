```yaml
VERDICT: PASS
DIGEST:
  headline: >-
    Fix cycle (83282dea..fbaa7fec) touched only the S2 advisory string, three new tests, and
    a test-only stderr-parsing helper — no source path changed. S2 stays a fixed literal (no
    interpolation), the PRE-route file_path never reaches argv/shell (stdin JSON only, both
    unchanged), and cycle 0's two MED gaps plus the gh-sync never-create gap all re-confirmed
    present and still unreachable through today's production callers. No new finding.
  in_scope: true
  scope_reason: >-
    The fix cycle touches the domain-gate advisory text and its test coverage — a
    security-relevant enforcement path — plus a validator's own regex-parsing test helper.
    Both are this role's surface even though the delta is small; dispatch requires re-checking
    exactly this range, not the full diff cycle 0 already cleared.
  severity_max: med
  findings: 3
  must_fix: []
  threat_model:
    - boundary: "S2 advisory text (tool_result POST handler, edit route, harness-hooks.ts:852-854)"
      stride: I
      mitigated: true
    - boundary: "extractEditPaths(input.input) -> preDomain's file_path -> check-domain.sh (harness-hooks.ts:219-234, spawnSync stdin-JSON, not argv)"
      stride: T
      mitigated: true
    - boundary: "write_feature_json's caller-supplied tail_regex parameter (feature_json_write.py:84)"
      stride: T
      mitigated: false
    - boundary: "monotonic non-regression baseline, exact-string parse-error collision (feature_json_write.py:145-176)"
      stride: T
      mitigated: false
    - boundary: "write_feature_json has no core allow_create gate; a future gh-sync-shaped caller could mint a schema-complete feature.json (feature_json_write.py, gh-sync.py:534-736)"
      stride: E
      mitigated: false
  open_questions:
    - id: Q1
      question: >-
        write_feature_json still has no core-enforced allow_create parameter (code-reviewer
        c0 Finding B's alternative). factory_decompose.py's feat_id opt-in is caller-side
        discipline only, added in the base diff, unchanged this cycle. Worth a follow-up
        feature adding the gate to the core rather than trusting every future caller to
        replicate the convention — not gating this ship.
      blocking: false
    - id: Q2
      question: >-
        Tool defect, not a BUG-1030 finding: a relative `write` path issued from this session
        (cwd'd into the worktree via `bash`'s `cwd` param) resolved against the OUTER
        main-branch checkout instead of the worktree, silently creating
        `.harness/harness/features/BUG-1030-stale-anchor-write-hazard/notes/
        review-harness-security-reviewer-c1.md` there. `read`/`grep`/`glob` on relative paths
        showed the same worktree/outer-repo confusion in both directions during this run.
        Caught via `git status`/`find`, corrected with an absolute worktree path, stray copy
        removed. `xd://report_issue` itself refused the report (outside this persona's write
        domain) — routing here instead. Worth the harness owner's attention; not this role's
        call to fix.
      blocking: false
  files_touched: []
  expertise_update: []
artifact: .harness/harness/features/BUG-1030-stale-anchor-write-hazard/notes/review-harness-security-reviewer-c1.md
```

# Security review-c1 — BUG-1030-stale-anchor-write-hazard

Short cycle on `83282dea..fbaa7fec` only (review_sha `fbaa7fec`, base `6d6d1cea`; HEAD `e024599`
adds only the pin record — confirmed by `git log`, **executed**). Read-only per DEC-174; every
mutation below ran against pure-Python scratch copies under `/tmp`, built and torn down with
`open()`/`shutil.rmtree` (no shell `cp`/`mv`/`tee`, which `bash-write-guard.sh` correctly blocked
on a first attempt — reported to myself in this note, not evaded). `git status --porcelain` in
the worktree is clean of my writes now; a first `write` attempt landed in the OUTER
(`main`-branch) checkout's untracked `.harness/harness/features/BUG-1030-stale-anchor-write-
hazard/` directory instead of the worktree's — a tool path-resolution defect (see DIGEST Q2) —
corrected by rewriting with the worktree's absolute path and removing the stray copy.

`git diff --stat 83282dea..fbaa7fec` touches exactly: `omp-hooks.test.ts` (+52), 
`test-validate-feature-json.py` (+27), `.omp/extensions/harness-hooks.ts` (+9/-2, advisory text
only), the four c0 review notes, `review_sha`, and two handoff docs. **No production
`.py` source changed** — `feature_json_write.py`, `harness_merge.py`, `gh-sync.py`,
`factory_decompose.py`, `check-domain.sh` are byte-identical to `83282dea` (**executed**,
`git diff --stat` over each path is empty).

## 1. S2 advisory reword — clean, no leakage [executed]

Read `.omp/extensions/harness-hooks.ts:840-855` directly. The new text is two fixed string
literals concatenated (`"Harness: no target path..." + "neither the pre-write nor the
post-write..."`), replacing the old two-literal concatenation — no template literal, no
`${}`, no variable feeds it. Confirmed by direct source read, not by trusting the diff
context. **Answer: no, it does not interpolate any path, content, patch text, or stack
trace.**

## 2. Attacker-influenced `file_path` reaching `check-domain.sh` — no argv/shell surface [executed]

Traced the full path: `extractEditPaths` (harness-hooks.ts:70-84, pure regex match on
`input.input`, agent-authored patch text) → `preDomain`'s edit branch
(`:219-234`, unchanged this cycle) builds `{ tool_input: { file_path: filePath } }` → passed as
the `payload` argument to `runner(cwd, "check-domain.sh", [], payload)` → `runPolicy`
(`:198-222`, also unchanged) calls `spawnSync(gatePath(script), args, { ..., input:
JSON.stringify(payload) })` — **`args` is the literal empty array `[]`; `filePath` is never
placed in `args`**, only inside the JSON string handed to the child's **stdin**.
`check-domain.sh:75` reads it back with `payload=$(cat)`, exports it as `HOOK_PAYLOAD`, and the
embedded Python heredoc (`:160`, `:334-336`) does `json.loads(...)` then
`ti.get("file_path")` — a data read, never a shell substitution or `exec`/`eval` of the value.
**Answer: no, an attacker-influenced `file_path` cannot reach argv or a shell string; it only
ever reaches a JSON parse.** This mechanism is identical to `postDomain`'s pre-existing edit
route and to `preDomain`'s own write-tool branch — not new, not touched by this fix cycle, and
already matches the list-form-argv discipline cycle 0's own security review confirmed for
`gh-sync.py`'s `subprocess.run` calls.

## 3. Mutation-proof of the commit's "2 tests reddened" claim [executed]

Built a scratch copy (`.claude/skills/harness/bin/omp-hooks.test.ts` +
`.omp/extensions/harness-hooks.ts` + the two `.jsonl` fixtures, correct relative depth) under
`/tmp`, ran `bun test` unmutated first: **50 pass / 1 fail** (the 1 fail is an environmental
artifact of the scratch copy missing `check-domain.sh` on disk, present identically with or
without the mutation — not a false claim in the source). Then mutated only `preDomain`'s edit
branch to `return [];` unconditionally (the exact pre-fix silent-zero shape) and reran:
**48 pass / 3 fail** — exactly 2 new failures, both the two new PRE-route tests
("a hashline edit is gated BEFORE it lands", "every file of a multi-section edit is gated
before it lands"). **Confirms the commit's claim precisely.** Scratch dirs removed after
(`shutil.rmtree`), confirmed absent by glob.

## 4. The "S2 fires end-to-end even though PRE is silent" correction [executed]

Both the existing tool_result test ("a non-string patch spawns no gate, and SAYS SO (S2)")
and the new tool_call test ("a non-string patch reaches no pre-write gate and does not block
the edit") drive the **identical** `editResult({ sections: ["a/one.json"] })` input through
`editCtx`. The full 51/51 green run (**executed** above) confirms both hold simultaneously for
that one input: `tool_call` spawns nothing and does not block; `tool_result` spawns nothing but
does append the advisory. **The dispatch's correction is verified, not just plausible**: cycle
0's "NO signal" is true of the PRE gate considered alone; end-to-end, for the same edit, S2
still tells the operator once, after the fact. This is an informational, post-hoc signal, not a
preventive one — it does not change that the edit already landed unchecked.

## 5. Cycle 0's two MED gaps, re-rated at `fbaa7fec` [executed]

Neither `feature_json_write.py` nor any of its 5 production call sites
(`gh-sync.py` ×3, `factory_decompose.py` ×1, `feature-json-merge.py` ×1 — confirmed by grep,
unchanged) moved this cycle.

- **`tail_regex` unvalidated** (`feature_json_write.py:84`, `harness_merge.require_destination`
  does a bare `.search()`): still true at source. **Reachability unchanged**: both live callers'
  regexes (`FEATURE_JSON_TAIL`, `FEATURE_JSON_BASENAME_TAIL`) still anchor the literal filename
  `feature.json`. **Still MED, still unreachable through today's callers.**
- **Exact-string baseline collision** (`:145-176`): still true at source (unchanged bytes,
  confirmed by empty diff). **Reachability unchanged**: all 5 callers still build their
  candidate via `json.loads(base)` themselves before ever calling `write_feature_json`, so an
  unparseable base still crashes the caller's own transform first, every time. **Still MED,
  still unreachable through today's callers.**

## 6. gh-sync's never-create guarantee — confirmed still gapped, MED [executed, live repro]

Reproduced code-reviewer c0's Finding B directly against `fbaa7fec` in an isolated scratch
copy (pure-Python file I/O, no shell writes): a closure shaped exactly like a gh-sync call site
— `base is None` → return a full 8-key schema-complete document, using gh-sync's own default
`tail_regex` — handed straight to `feature_json_write.write_feature_json` **succeeds with zero
refusal** and creates `feature.json` on disk. Confirms: **no parameter on
`write_feature_json` distinguishes "gh-sync-shaped caller" from "factory_decompose-shaped
caller"; `factory_decompose.py`'s `feat_id` opt-in (added in the base diff, unchanged this
cycle) is entirely caller-side, not core-enforced.** Not reachable today — all 3 real gh-sync
closures raise/return before `base is None` ever reaches `write_feature_json` — and no test
anywhere binds the never-create guarantee to the core. **MED, unchanged from c0, still
latent.**

## 7. `scanned_count()` — no security surface [executed]

`test-validate-feature-json.py:26-42` — a fixed regex (`SCAN_COUNT_RE`) parsed against a
`subprocess.run` result's own `stderr`, inside a test file, replacing a substring check with an
integer comparison. No untrusted input, no eval, no injection-shaped construction; it fixes a
test that could not fail (`"41 file(s)"` contains `"1 file(s)"`), not a security control. **No
finding.**

## Sweep for new secrets/credentials across the full fix-cycle diff [executed]

Grepped all 11 changed paths for key/token/password/PEM-shaped strings (per Expertise P-14,
beyond just the dispatch-named files) — none found; the four new `notes/review-*-c0.md` files
and two handoff docs are prose only.
