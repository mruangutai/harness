# Confirmation pass — FEAT-14 — two fixed HIGHs

**Reviewed range: `c9cd6bb..1c5fd67`** (the two fix commits, `0b33188` and `1c5fd67`).
**HEAD 12e3fa2 confirmed pin-only**: `git show --stat 12e3fa2` touches only
`.harness/features/FEAT-14-feature-json-schema/feature.json`'s `review_sha` field, 1 file / 1 line.

**Human commit in scope: `0b33188`** — made directly by the main session under the DEC-174
carve-out (`check-domain.sh` + `test-check-domain.py` are enforcement-layer files). This is its
first review of any kind; treated as fully in scope, not inherited from an earlier pass.

## Verdicts

**HIGH-1 (schema gate fail-open) — CLOSED.** `except Exception` now sits after `except ImportError`
in `check-domain.sh:894-916`, and the aggregation that decides `sys.exit(2)` is a single
accumulate-then-decide pass over every target (`:1195-1210`), so the fix holds even under the
per-invocation message dedup. See Q3.

**HIGH-2 (gh-sync zero-byte window) — CLOSED, no new hole reachable in the real pipeline.**
`save_recorded` is now mkstemp+fsync+os.replace, `load_recorded` raises on empty/non-mapping. The
one place the fix could have opened a new hole (`doc = {}` producing a schema-invalid document) is
real code but not a reachable path given call-site ordering. See Q7/Q8.

---

## HIGH-1 — detail

**Q1.** `git show --stat 0b33188` → only `.claude/skills/harness/bin/check-domain.sh` (+19) and
`.claude/skills/harness/bin/test-check-domain.py` (+75). No other files. Clean.

**Q2 — route coverage.** All three routes converge on one `targets` list and one loop
(`check-domain.sh:1099-1210`), which is the reason this is safe rather than three parallel
implementations to keep in sync:
- **Write, PRE** (`:1104-1113`): `content = (tool_input).content` — the whole file *about to be
  written*, never touches disk. This is genuine prevention.
- **Write/Edit, POST named-file** (`:1115-1129`): re-reads the file **off disk**, because an Edit
  payload carries only `old_string`/`new_string`, never whole-file content — confirmed, there is no
  `content` key read for Edit anywhere in this branch. The write has already landed by the time this
  runs.
- **Bash, POST sweep** (`:1131-1164`): globs `SWEEP_GLOBS`, re-reads each modified-since-stamp file
  off disk, appends `(rel, text, display)` for each into the same `targets` list.

All three land in `shape_problems()`, whose `RE_FEATURE_JSON` branch (`:855-941`) contains the fixed
try/except. The widened handler is reached identically from all three routes — same function, same
lines, not a copy.

**Q3 — the dedup.** Verified in the aggregating caller, not assumed:
```
_problems = []
for _rel, _text, _disp in targets:
    _problems.extend(shape_problems(_rel, _text, display=_disp))
if _problems:
    ...; sys.exit(2)
sys.exit(0)
```
(`check-domain.sh:1195-1210`). `_SCHEMA_UNAVAILABLE_SAID` is a module-level global that starts
`False` at the top of **every fresh process** (each hook firing is its own `python3` subprocess —
there is no daemon). Within one multi-target sweep, the dedup (`:919-924`) suppresses the message
text for the 2nd..Nth occurrence, but the **first** occurrence is never suppressed and is always
appended to `out`/`_problems` before the loop finishes. Because the exit decision is made exactly
once, after the whole loop, on the union `_problems`, the first occurrence alone is sufficient to
force `sys.exit(2)` for the entire invocation. **There is no per-file exit path** — confirmed by
reading the loop, not inferred. The claim's own precondition ("safe only if any single file's
finding fails the WHOLE invocation") holds.

Gap, not a live bug, and **routes to the MAIN SESSION under DEC-174, never as a fix-cycle item** —
it is new material inside `test-check-domain.py`, one of the two carve-out files, not something a
squad may pick up: `run_schema()`'s Case 3 (`test-check-domain.py:1382+`) only drives the **PRE
Write** route via `fire()` (`tool_name: Write`, no `--post`). Nothing exercises the multi-target
sweep/dedup path, or POST-Edit, against this exception branch. The safety argument above is
code-verified, not test-verified — a future change to the accumulation shape (e.g. an early exit
added to the `for _rel, _text, _disp in targets` loop for performance) would silently reintroduce
HIGH-1 for the sweep case with nothing in the suite to catch it. This is an observation about
missing coverage, not a defect in the fix itself.

**Q4 — DENY semantics per route, stated honestly.** Already handled candidly in the code itself,
not something this fix changed: `VERB = "OVER BUDGET (already written)" if _post else "BLOCKED"`
(`:781`, comment says the same). PRE-Write: genuine prevention. POST (Write/Edit/Bash-sweep): the
write has already landed; `sys.exit(2)` is a loud report to the agent's stderr, never a rollback.

**Q5 — the `SystemExit` residual.** `grep -n "sys.exit\|raise SystemExit\|argparse\|__main__" feature_schema.py`
→ only `import sys` used for `sys.path.insert` (lines 41-43). No `sys.exit`, no argparse, no CLI
guard — the module cannot raise `SystemExit` on the call path check-domain.sh takes
(`import feature_schema` → `feature_schema.problems_for_text`). Its one lazy dependency,
`harness_yaml.load_file`/`load_str`, does not call `harness_yaml.require_or_die` (the only
`sys.exit` in that file, at `:455`) — confirmed by grep, that function is unreferenced from
`feature_schema.py`. `except Exception` is sufficient; no live `BaseException` gap.

**Q6 — temp-path attribution.** `_show(path)` (`:759-766`) is `os.path.relpath(abspath(path),
abspath(root))`, called with `target` (== `tool_input.file_path`, the real destination the agent
named) on the Write/Edit routes and with the glob-matched real path `_p` on the sweep route. No
route ever constructs or reports a hook-internal temp path. `display or rel` in `shape_problems`
falls back to `rel` (worktree-stripped) only if `display` is falsy, which never happens on any of
the three call sites — all three pass a non-empty `_show(...)` result.

---

## HIGH-2 — detail

**Note on `1c5fd67`'s diff surface:** the dispatch describes "~230 changed lines across `gh-sync.py`
and `test-gh-sync.py`"; the commit also touches this feature's own `feature.json` (cycles_used
4→5, a new run entry) and adds `notes/receipt-harness-backend-dev-fix1-c1.md`. Both are expected
harness bookkeeping for a routed-back fix cycle (DEC-157), not code — seen, dismissed, recorded so
the next reader does not re-derive it.

**Q7 — first-sync path, both branches.** `load_recorded` (`gh-sync.py:245-329`):
- absent file → `if not os.path.exists(path): return rec` (no exception) — confirmed at source.
- present, dict, no `github` key → `if "github" not in doc: return rec` (no exception) — confirmed
  at source, distinct branch from the absent-file one.

Both proceed. Confirmed independently in `test-gh-sync.py` rows 1a/1b (`:773-786`).

**Q8 — the `{}` seed, reachability not possibility.**
```
if os.path.exists(p):
    doc = json.load(f)
    if not isinstance(doc, dict):
        doc = {}
else:
    doc = {}
```
`grep -n "save_recorded(\|load_recorded(" gh-sync.py` shows every `save_recorded` call site
(`cmd_open` lines 424/434/443/462/473/475) is inside a function that calls `load_recorded` first
(`cmd_open:397`). `cmd_close_task`, `cmd_abandon`, `cmd_ship` are the same shape or don't call
`save_recorded` at all (`cmd_ship` writes nothing per its own docstring; `cmd_backlog` never touches
`feature.json`). Since `load_recorded` raises `SystemExit` before returning on any non-mapping
document, by the time `save_recorded` runs in the same process the file — if present — was already
proven to parse as a dict. **The non-mapping branch inside `save_recorded` is dead in normal
operation**; the only live branch is the absent-file one, matching the dispatch's own claim.

Whether that live branch is *itself* reachable in the deployed pipeline: `gh-sync.py open` fires
"right after the approval gate passes" (`SKILL.md:173`), and `feature.json` is orchestrator-owned,
created and written from feature init onward (`harness-orchestrator.md:46-56`, "only you may write"
`feature.json`) — well before ship. I did not find a call site where `gh-sync.py open` runs against
a feature directory with no `feature.json` yet, but this is a static-reading conclusion, not a
runtime trace, so it does not clear the bar of "new evidence" against the panel's own reachability
call. **Ranked the same as panel item 4 — MED, non-blocking — no new evidence to move it either
way, in either direction.**

**Q9 — regression sweep over the ~230 lines.**
- Unrelated keys preserved: `save_recorded` loads the *whole* document and only overwrites the
  `github` key before re-serializing all of it — confirmed at source and by the pre-existing "review
  finding 2" round-trip test (`test-gh-sync.py:862-886`), unmodified by this diff, still asserting
  `feature_id`/`status`/etc. survive.
- `except BaseException` cleanup: correct as written — `os.unlink(tmp)` wrapped in its own
  `try/except OSError`, then re-raise. Nothing executes after a successful `os.replace`, so no
  double-cleanup path; if `os.replace` itself fails, `tmp` still exists at its original path and the
  unlink succeeds.
- **New, unflagged elsewhere:** `os.replace(tmp, p)` moves a `tempfile.mkstemp` file onto
  `feature.json`. `mkstemp` creates files mode `0600`. `os.replace`/rename carries the **source's**
  permission bits onto the destination inode — it does not preserve the destination's prior mode.
  Neither `gh-sync.py` nor `factory_decompose.py`'s `write_factory` (the pattern this fix
  deliberately converged with, per the commit) calls `os.chmod` to restore the original mode.
  `grep -n "chmod" gh-sync.py factory_decompose.py` → no hits in either. Confirmed by absence: no
  test in `test-gh-sync.py` asserts `feature.json`'s mode after a write. Net effect: every
  `save_recorded` call (and every `write_factory` call) silently narrows `feature.json` to
  owner-only `0600`, where the old truncating `open(p, "w")` preserved whatever mode the file
  already had. Low practical severity in a single-operator local checkout, but it is a real,
  unasserted behaviour change shared by both writers, not unique to this diff — flagging once here
  rather than as a new gate item.

---

## Findings (ranked, none gate)

1. **low** — `check-domain.sh`'s new crash-branch is code-verified reachable and safe on all
   three routes (Write-pre, Edit/Write-post, Bash-sweep) and under the per-invocation message dedup,
   but the regression test added at `0b33188` (`run_schema` Case 3) only drives the PRE-Write route.
   Discrimination exists for that one route; reachability for the other two and for the
   multi-target-sweep aggregation is established by reading, not by a test that can fail. **Routes
   to the MAIN SESSION under DEC-174** — `test-check-domain.py` is a carve-out file, not a fix-cycle
   surface. Not blocking; the aggregation invariant is simple and shared by other shape checks, so
   it is not uniquely fragile today.
2. **low** — `os.replace` from `tempfile.mkstemp` silently narrows `feature.json` to `0600` on
   every `gh-sync`/`factory_decompose` atomic write, with no `chmod` restore and no test asserting
   mode. Shared by both writers, pre-existing pattern this fix converged with rather than
   introduced. Not blocking.
3. **med** — `doc = {}` in `save_recorded` is reachable only via the absent-`feature.json` branch.
   Ranked identically to panel item 4 per the dispatch's own instruction ("same rank unless you have
   new evidence") — my reachability argument (orchestrator creates `feature.json` before ship) is a
   static reading, not a runtime trace, so it is not new evidence and does not move the rank in
   either direction. Non-blocking, as item 4 was.

No `must_fix`. `severity_max: med` (finding 3, matching panel item 4's own rank — `med` does not
gate per this feature's own established threshold for that item).

## What I did not verify myself (read-only role, per dispatch)

- Did not execute `test-check-domain.py` or `test-gh-sync.py` — code-read only. Dispatched in
  parallel to `harness-qa` for runtime probing (schema-crash and atomicity fixtures specifically).
  Any claim above phrased as "the suite asserts X" is a claim about what the test source contains
  and whether it can fail by inspection, not a claim that I ran it green.
- Did not independently confirm "gh-sync.py open never runs before feature.json exists" via a
  runtime trace — this is a static-reading conclusion from `SKILL.md` + `harness-orchestrator.md`,
  not a grep-proven call graph. Carried into `open_questions` (non-blocking) for the team to settle
  empirically if they want finding 3 moved off `med`.
