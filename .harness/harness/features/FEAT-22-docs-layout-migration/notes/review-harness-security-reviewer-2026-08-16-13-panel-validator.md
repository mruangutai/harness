# Security review — FEAT-22 docs layout migration — panel step `security`

**Base `0f12f14`, review SHA `e26e628`.** Measured: `git diff --name-only 0f12f14..e26e628 | wc -l`
= **32**, `git rev-list --count 0f12f14..e26e628` = **5**. Matches the dispatch's claim exactly.

## Verdict: PASS, one `low` finding, `must_fix: []`

## Why this diff is in scope
This is not a documentation-only move. It relocates three root-resolution constants
(`factory_config._PROBE`, `harness_boundary.HARNESS_CONTROL_PLANE`, `gen-decisions-index.DOCS_DIR`)
that the write-authorization guards and the factory's own root probe depend on, and it adds a new
write grant (`team-config.yaml`) for `harness-documentor` under `.harness/`. That is authorization
surface. Audited accordingly.

## What I probed, with literal results

**Grant reach (`check-domain.sh --resolve`, no stdin, all exit 0 unless noted):**
```
.harness/harness/docs/SPEC.md              -> harness-documentor   (intended)
.harness/notes/docs/x.md                    -> harness-documentor   (unintended)
.harness/expertise/docs/x.md                -> harness-documentor   (unintended)
.harness/factory/docs/x.md                  -> harness-documentor   (unintended, adjacent to fleet.yaml)
.harness/logs/docs/x.md                     -> harness-documentor   (unintended)
.harness/codebase/docs/x.md                 -> harness-documentor   (unintended)
.harness/harness/docs/../../factory/fleet.yaml -> NOBODY            (.. traversal correctly refused)
.harness/harness/docs/agents/x.md           -> harness-documentor   (expected, under the grant)
.harness/docs/x.md (zero middle segment)    -> NOBODY               (glob_to_re's `*` needs one segment, confirmed)
```
`team-config.yaml` adds `{ path: .harness/*/docs/**, upsert: true }` to `harness-documentor`'s
domain. The `*` is a live single-segment wildcard, not the intended literal `.harness/harness/docs/**`
— it grants write into a `docs/` subdirectory under **any** first-level name inside `.harness/`,
including the harness's own reserved directories (`notes`, `expertise`, `factory`, `logs`,
`codebase`), none of which are declared repository segments.

**`HARNESS_CONTROL_PLANE`'s copy of the same string is dead code**, confirmed by reading
`is_control_plane_target`: `is_control_plane_glob(rel)` — first path segment `.harness` or
`.claude` — short-circuits before the list is ever consulted for any `.harness/**` target. The
diff's own comment says this. The live risk is entirely in the `team-config.yaml` grant, not in
`harness_boundary.py`.

**Blast-radius check — is a stray file under the ungranted-but-reachable segments read by
anything:**
- `inject-expertise.sh` (SubagentStart injector) reads `$root/.harness/expertise/$agent.md`
  by **exact filename**, never a glob into subdirectories — a file at
  `.harness/expertise/docs/harness-eng-lead.md` is never picked up. Read-verified.
- `factory_config._PROBE = os.path.join(".harness","harness","docs","SPEC.md")` is a **fixed
  literal**, checked with `os.access`, not a glob — no candidate-set confusion possible here.
  Read-verified (diff at `factory_config.py:32`).
- `layout_migration._evidence()` is the one consumer that globs
  `.harness/*/docs/SPEC.md`. Executed in-memory (monkeypatched `glob.glob`, **zero disk writes**)
  planting a stray `.harness/notes/docs/SPEC.md` alongside the legitimate
  `.harness/harness/docs/SPEC.md`:
  ```
  declared segments: {'kaya-ai', 'harness'}
  shapes: {'migrated'} count: 1 undeclared: ['.harness/notes/docs/SPEC.md']
  ```
  The stray is classified `undeclared`, not folded into `migrated`/`CLEAN`. Traced onward in
  `scan()`: `if undeclared: ... CANNOT_VERIFY, cause="undeclared-segment"`, which
  `cause_text()` renders as `"evidence under undeclared segment: <path> — declare the repository
  in .harness/factory/fleet.yaml or move this out of .harness/"`. Loud, named, self-diagnosing —
  never silent, never a false CLEAN. This exact scenario also has a **standing test**,
  `test-layout-migration.py` case 19 ("evidence under an UNDECLARED segment -> exit 2, phrase +
  path named"), which passed in the full suite run below.
- Only a file literally named `SPEC.md` is read by anything under this grant's reach; any other
  filename planted in `.harness/{notes,expertise,factory,logs,codebase}/docs/` is inert — nothing
  in this repo reads it.

**Suites run (no redirects — my role is enforced read-only by `bash-write-guard.sh`, which
correctly blocked a `>` redirect attempt with `harness-security-reviewer is READ-ONLY`; verified
via `$(...)` capture instead):**
- `python3 .claude/skills/harness/bin/test-check-domain.py` — 117 `ok`, 0 `FAIL`, exit 0.
  (One transient `FAIL` on `schema/probe restored feature_schema.py byte-identically` appeared
  on an earlier, concurrently-run invocation and did not reproduce on immediate rerun — noted for
  honesty, not a security finding; looks like a flaky tempfile-restore self-check, unrelated to
  the migration.)
- `python3 .claude/skills/harness/bin/test-layout-migration.py` — all cases `ok` including the
  new case 21 (SC-02 pin: "real root's harness/docs surface is CLEAN with migrated evidence") and
  case 19 (undeclared-segment), exit 0.

**Finding — LOW: over-broad write grant, bounded blast radius**
`.harness/team-config.yaml`'s new entry `{ path: .harness/*/docs/**, upsert: true }` grants
`harness-documentor` write access to `.harness/<any-existing-or-future-top-level-name>/docs/**`,
not only the intended `.harness/harness/docs/**`. This was a **deliberate, signed spelling**
(`DECISIONS.md` DEC-189 amendment 1, committed in this diff) mirroring the established
`.harness/*/features/*/...` multi-repo idiom used elsewhere in `team-config.yaml` — but the
amendment reasons only about the "two of four" arithmetic correction and the string's
redundancy in `harness_boundary.py`; it does not reason about the wildcard also matching the
harness's own reserved subdirectories, which are not declared repository segments. Today
`harness` is the only self-segment and `kaya-ai` the only product segment
(`_declared_segments()` output above) — no repo is named `notes`, `expertise`, `factory`,
`logs`, or `codebase`, so no live collision exists. `SC-05`'s standing test
(`test-check-domain.py`) pins only the intended path; nothing pins that the grant is confined to
declared segments.

Threat model: the actor is `harness-documentor` itself (already a broadly-trusted upsert role
over `docs/**` and several named harness files) — not privilege escalation to a new actor, but a
least-privilege gap: the grant reaches further than REQ-04 states and further than any SC
verifies. Exploitability is low because (a) the one filename anything reads there (`SPEC.md`) is
already caught loudly by `_evidence()`'s undeclared-segment path with a standing test, and (b)
every other filename planted under the unintended segments is inert. Remedy, stated as a
constraint per the "name the exact provenance" gotcha: the grant should resolve no target whose
`.harness/<segment>/` is not a declared repository segment — today that means the literal
`.harness/harness/docs/**`, widened only when a second repository actually onboards and needs its
own docs path. `team-config.yaml` is data/config, not one of the four DEC-174 carve-out files, so
this remedy is in the operator's or a build agent's hands, not routed to main session.

## Assessed and dismissed (checked, not skipped)
- **Fail-open in the guards**: no logic in `check-domain.sh` or `check-state.sh` changed — both
  diffs are single-line message-text literal updates (`docs/harness/DECISIONS.md` ->
  `.harness/harness/docs/DECISIONS.md`). Read in full; confirmed no branch, exit code, or
  control-flow touched. Nothing here routes to the operator under DEC-174 — there is no change to
  report.
- **Confused deputy via `_PROBE`**: `factory_config._PROBE` is a hardcoded literal path checked
  with `os.access`, moved atomically with the other two resolvers in the same commit (git rename
  detection confirms `docs/harness/{SPEC,DECISIONS,DECISIONS-INDEX,BUILD}.md` and `org.html` are
  100%-similarity renames into `.harness/harness/docs/`, zero orphaned legacy files — SC-01/SC-04
  satisfied by inspection). No glob-based root resolution exists to confuse.
- **Path traversal**: `.harness/harness/docs/../../factory/fleet.yaml` resolves to `NOBODY` —
  `harness_boundary.real()` normalizes via `os.path.realpath` before every comparison, confirmed
  by the resolve above.
- **Symlink escape**: not retested live (already covered by the diff's own updated fixture,
  `test-check-domain.py`'s "SYMLINK PAIR" case, which passed in the suite run above) — this class
  was the subject of a prior fix (`harness_boundary.py`'s `real()` docstring), unchanged logic
  here, only the illustrative path literal updated.
- **Secrets/credentials**: `git diff 0f12f14..e26e628 | grep -iE` for API keys, tokens, private
  key markers, bearer tokens, AKIA/ghp_/sk- prefixes — one match, `TOKEN_RE = re.compile(...)` in
  `test-no-distribution.py`, a regex *variable name* matching deploy-related literal strings
  (`harness-deploy`, `deploy.sh`, `harness-registry`, `registry.json`), pre-existing test logic,
  not a credential.
- **Expertise-file poisoning**: `inject-expertise.sh` reads by exact filename only (see above) —
  the two touched Expertise files (`harness-backend-dev.md`, `harness-documentor.md`) carry only
  literal path-string updates inside existing prose, no new content, no secrets.
- **`org.html`**: 100%-similarity rename (0 diff lines against the pre-move file), no `<script>`
  element, static CSS-only page — no XSS-relevant surface.
- **`.harness/notes/audit-decisions.py`**: two `pathlib.Path(...).read_text()` literal updates,
  no subprocess, no shell interpolation, no eval — not a hook, not on any untrusted-input path.
- **Log files** (`2026-08-15.md`, `2026-08-16.md`): administrative narrative only, no secrets, no
  injected content.
- **Stale-checkout skew** (advisor's item, and the BRIEF's own named residual): a worktree still
  on a pre-move commit would have a `_PROBE`/grant mismatch against a freshly-moved main — this is
  the exact hazard the one-atomic-commit constraint and the "run from the worktree" rule in
  `CLAUDE.md` exist to prevent. Not a defect in this diff; a known operational precondition,
  already named in the BRIEF's Verification gaps ("nothing stages two repository segments").

## Probe hygiene
No working-tree writes. One redirect attempt (`>` into a scratch temp file) was correctly refused
by `bash-write-guard.sh` for this read-only role — reported as evidence the guard enforces
read-only on this role, not worked around. All command-substitution (`$(...)`) captures used
instead. The in-memory `layout_migration` probe monkeypatched `glob.glob` in a Python process and
touched no file. `git status --porcelain` at the end shows only pre-existing untracked artifacts
from other agents' prior runs on this feature (BRIEF.md, plan.yaml, other reviewers' notes) —
none created by this review.

```yaml
VERDICT: PASS
DIGEST:
  headline: "Docs-move root-resolution literals are consistent and atomic; one LOW over-broad write grant (.harness/*/docs/** reaches reserved harness dirs beyond the intended .harness/harness/docs/**), blast radius bounded and already partly self-diagnosing — nothing gates."
  in_scope: true
  scope_reason: "Diff moves three root-resolution constants read by the write-authorization guards (factory_config._PROBE, harness_boundary.HARNESS_CONTROL_PLANE, gen-decisions-index.DOCS_DIR) and adds a new team-config.yaml write grant — this is authorization surface, not prose."
  severity_max: low
  findings: 1
  must_fix: []
  threat_model:
    - { boundary: "team-config.yaml domain grant -> check-domain.sh/harness_boundary.py PreToolUse guard", stride: E, mitigated: false }
    - { boundary: "harness_boundary.HARNESS_CONTROL_PLANE list -> is_control_plane_target", stride: T, mitigated: true }
    - { boundary: "factory_config._PROBE root resolution", stride: S, mitigated: true }
    - { boundary: "layout_migration._evidence() undeclared-segment classification", stride: T, mitigated: true }
    - { boundary: "SubagentStart Expertise injection (inject-expertise.sh)", stride: I, mitigated: true }
    - { boundary: "check-domain.sh / check-state.sh (DEC-174 carve-out)", stride: T, mitigated: true }
  open_questions: []
  files_touched: []
  expertise_update: []
artifact: .harness/harness/features/FEAT-22-docs-layout-migration/notes/review-harness-security-reviewer-2026-08-16-13-panel-validator.md
```
