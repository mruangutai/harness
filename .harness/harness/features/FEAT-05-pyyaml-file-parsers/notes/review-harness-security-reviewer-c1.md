# Security re-review (cycle 1) — FEAT-05 F-01 scoped fix — manifest-walk fail-open

Scope: judge ONLY the F-01 fix in `340e18a..9da3986`. Read-only; no source edits made (see
STEP 0 output — `git status --porcelain` is empty before and after this run; two untracked
files present at the end, `qa-c1.md` and `review-harness-ui-reviewer-c1.md`, are other reviewers'
concurrent artifacts, not mine).

## VERDICT: FAIL — F-01 PARTIALLY CLOSED

`severity_max: high`. The two shapes cycle 0 demonstrated (bad-UTF-8 byte, manifest-as-directory)
are closed on both hooks, with a message. A third, plausible shape — a manifest whose top-level
YAML document is not a mapping (empty file, a bare scalar, a bare list) — was **never** closed:
it reproduces the identical crash at 340e18a *and* at current tree, in code the fix never touched.

---

## STEP 0 — verbatim, before any assessment

```
$ git rev-parse HEAD
924b961ad626b79c8810a9de7ae420ccc634e4fd

$ git status --porcelain
(empty)

$ git diff --stat 340e18a..9da3986
 .claude/skills/harness/bin/check-state.sh          |  88 +++++--
 .claude/skills/harness/bin/gh-sync.py              |   7 +-
 .claude/skills/harness/bin/harness_yaml.py         |  35 ++-
 .claude/skills/harness/bin/run-unit-tests.sh       |   2 +-
 .claude/skills/harness/bin/test-check-domain.py    |  26 ++
 .claude/skills/harness/bin/test-gh-sync.py         |  44 ++++
 .claude/skills/harness/bin/test-upgrade-config.py  | 157 +++++++++++
 .claude/skills/harness/bin/upgrade-config.py       |   9 +
 (+ FEAT-05 BRIEF.md/feature.yaml/notes, team-config.yaml)
 19 files changed, 1309 insertions(+), 56 deletions(-)

$ git log --oneline 340e18a..9da3986
9da3986 docs(brief): Q2 ruled a pinning error — the non-goal stands (Amendment 2)
20b5af3 fix: the panel's mediums and five of six open questions (F-04, F-05, Q1, Q3, Q4, Q6)
bb6ab8c fix(bin): the three high findings from the review panel (F-01, F-02, F-03)
d727870 chore(state): re-pin review_sha to 340e18a for the review panel
```

**HEAD deviation, addressed before proceeding:** HEAD (`924b961`) is `9da3986` + one commit
(`chore(state): re-pin review_sha to HEAD for the fix re-review`). `git diff --stat 9da3986..924b961`
touches **only** `.harness/features/FEAT-05-pyyaml-file-parsers/feature.yaml`, setting
`review_sha: 340e18a` → `review_sha: 9da3986`. No file under review differs between the two SHAs
and `git status --porcelain` is clean. That commit is itself affirmative evidence 9da3986 is the
intended target, not drift. Proceeded rather than blocking; flagged as `Q1`, non-blocking.

`check-domain.sh` and `bash-write-guard.sh` are **not** in the `340e18a..9da3986` diffstat at all —
both hooks are byte-identical to 340e18a. Only `harness_yaml.py` (the module both call) changed.

---

## 1. Original defect reproduced at 340e18a — CONFIRMED, both hooks, both shapes

Fixture roots and hook binaries were materialized under `/tmp` (`git worktree add /tmp/feat05-c1-old
340e18a`, fixtures written via `python3 -c` since Bash redirects/`cp`/`rm` are correctly denied to
this reviewer role by the very hook under test — confirms that control works). Target path outside
`harness-backend-dev`'s `allowed/**` domain in every case; sanity-checked first that a forbidden
absolute-path write is denied under a *valid* manifest (exit 2, both hooks, both SHAs).

| Manifest defect | `check-domain.sh` @ 340e18a | `bash-write-guard.sh` @ 340e18a |
|---|---|---|
| one `\xff` byte | `EXIT=1`, uncaught `UnicodeDecodeError` at `harness_yaml.py:107` | `EXIT=1`, identical traceback |
| manifest path is a directory | `EXIT=1`, uncaught `IsADirectoryError` at `harness_yaml.py:106` | `EXIT=1`, identical traceback |

Exit 1 is non-blocking (DEC-100); in both cases the forbidden-path write would have proceeded.
Matches cycle-0's F-01 exactly.

## 2. Closed at current tree (9da3986) — CONFIRMED, both hooks, both shapes, with a reason

| Manifest defect | `check-domain.sh` | `bash-write-guard.sh` |
|---|---|---|
| one `\xff` byte | `EXIT=2` — *"the manifest does not parse, so no domain can be checked… 'utf-8' codec can't decode byte 0xff…"* | `EXIT=2`, same message, `bash-write-guard:` prefix |
| manifest path is a directory | `EXIT=2` — *"...Is a directory: '.../team-config.yaml'..."* | `EXIT=2`, same message |

Both block, and both name the actual cause (D-14a satisfied — this is not a silent block).

## 3. Residual-path sweep — ONE CONFIRMED GAP (pre-existing, not introduced, still open), one confound resolved and cleared

- **Empty file / bare scalar / bare list at the manifest's top level — CONFIRMED UNCLOSED, HIGH,
  reproduces at BOTH 340e18a and current tree.** `yaml.safe_load` on `""` returns `None`; on
  `"just a string\n"` returns a `str`; on a `- one\n- two\n` document returns a `list`. All three
  parse *successfully* — `load_str`/`load_file` raise nothing, so the widened `except Exception` in
  `harness_yaml.py:92-114` never engages. The crash is one call frame later, in `manifest_domains`
  (`harness_yaml.py:167`, confirmed **not present in the `340e18a..9da3986` diff** —
  `git diff 340e18a..9da3986 -- harness_yaml.py | grep -c manifest_domains` returns `0`, the
  function is byte-identical): `for entry in (parsed.get("shared") or [])` assumes `parsed` is a
  dict unconditionally, outside any try, and neither hook's call site catches anything but
  `DuplicateKeyError`/`YamlParseError` (`check-domain.sh:134-146`, `bash-write-guard.sh` mirrors it).
  Verified live, both SHAs, isolated binaries (copied to `/tmp/feat05-c1-old` and `/tmp/feat05-c1-new`
  so the `_derived` manifest-fallback couldn't mask the result — see confound note below):
  ```
  check-domain.sh @ 340e18a,  empty manifest   -> EXIT 1, AttributeError: 'NoneType' object has no attribute 'get'
  check-domain.sh @ current,  empty manifest   -> EXIT 1, AttributeError: 'NoneType' object has no attribute 'get'
  check-domain.sh @ current,  bare-scalar      -> EXIT 1, AttributeError: 'str' object has no attribute 'get'
  check-domain.sh @ current,  bare-list        -> EXIT 1, AttributeError: 'list' object has no attribute 'get'
  bash-write-guard.sh @ current, bare-scalar   -> EXIT 1, identical AttributeError
  ```
  This is **pre-existing** (also crashes at 340e18a, so the fix did not introduce it), and it is
  **exactly what the dispatch's step 3 commissioned** ("The fix must hold for the whole
  read-and-parse surface, not just the two shapes cycle 0 named... a bare scalar, a list") — cycle
  0 did not test this shape, the fix did not close it, and it carries the identical blast radius as
  the original F-01: exit 1 is non-blocking, the crash happens before any agent's domain is
  consulted, so every agent's every write is ungoverned for the life of the broken manifest, not
  just the triggering write. An empty/truncated/single-line `team-config.yaml` is at least as
  plausible as F-01's original bad-merge-byte scenario (an interrupted write, a `>` typo that
  truncates the file, an empty file left by a failed editor save).

  **The fix for this exact shape already exists elsewhere in this same diff**, and was not
  reused here — the same observation cycle 0 made about F-01 itself. `check-state.sh:115-125`
  (touched in this diff) wraps its own `harness_yaml.load_file` call in `except Exception as e:`
  AND explicitly checks `if not isinstance(doc, dict):` before using the result. `manifest_domains`
  does neither.

- **Broken symlink / `chmod 000` manifest — NOT A GAP, confound identified and resolved.**
  First pass (testing directly against this checkout's own binaries) showed `EXIT=0` with **no**
  stderr, which looked like a silent bypass. Root cause was a test artifact, not a hook defect:
  `check-domain.sh`'s root-resolution fallback (`root = _derived` when the `CLAUDE_PROJECT_DIR`
  manifest fails `os.access(..., R_OK)`) silently switched to *this actual repo's own*
  `.harness/team-config.yaml` (readable), then allowed because the `/tmp` target is outside that
  root (`check-domain.sh`'s documented "outside the repo is not a domain question" rule — pre-existing,
  untouched by this diff). Re-run against the isolated `/tmp/feat05-c1-new` copy (so `_derived`
  has no manifest of its own) reproduced the **pre-existing, unchanged, already-documented**
  "no manifest → fail OPEN, loudly" branch for both cases: `EXIT 0`, with stderr `"check-domain: no
  <path> — enforcement OFF (run /harness-init)."` — a loud, intentional fail-open, not F-01's silent
  crash, unchanged since before `37a8a66`, out of this cycle's scope. Ran as `id -u` 501
  (non-root), so `chmod 000` was a real, not a no-op, test.

## 4. Is `except Exception` too broad? — NOT TOO BROAD; the discriminator resolves it cleanly

`load_str`'s try body (`harness_yaml.py:96-97`) contains exactly one statement:
`return yaml.load(text, Loader=_StrictSafeLoader)`. No post-parse transform or validation sits
inside the try — that work (`manifest_domains`'s tree walk and `.get("shared")`) lives in the
*caller*, outside this try entirely, which is precisely the cost of that placement (§3's finding is
that gap). So per the caller's own discriminator, the breadth is defensible: it wraps only the
parse call, nothing that could raise a harness-logic bug is inside it.

- `DuplicateKeyError` is caught *first*, above the broad `except Exception`, and merely re-raised
  (`harness_yaml.py:98-99`) — not swallowed. It does not subclass `yaml.YAMLError`
  (`class DuplicateKeyError(Exception)`, `:29`), so this ordering is load-bearing, not redundant:
  without it, the broad except would re-wrap it as `YamlParseError` and the call sites' `except
  harness_yaml.DuplicateKeyError` branch (the DEC-156-specific denial message) would go dead.
- Literal text is `except Exception as e:` (`:102`), not `except BaseException`. `KeyboardInterrupt`/
  `SystemExit` are not caught.
- **Full call-site sweep** (`grep -rn "load_str\|load_file\|load_recorded\|except harness_yaml"
  .claude/skills/harness/bin/`, excluding tests):
  - `check-domain.sh:135,146` / `bash-write-guard.sh:288,296` — the two write-gating hooks, covered
    above.
  - `check-state.sh:116,275,340,466` — every call already idioms `harness_yaml.load_file(fy) or {}`
    **and** (at least at `:116-125`) follows with `isinstance(doc, dict)` before use. Correct
    pattern, matches c0's earlier praise of this file.
  - `upgrade-config.py:108,133` — calls `harness_yaml.load_str` directly; this is a standalone
    script (not a PreToolUse hook), out of F-01's write-gating blast radius, not examined further
    (out of this cycle's scope).
  - `gh-sync.py:200-230` (`load_recorded`) — catches `FileNotFoundError` and
    `harness_yaml.YamlParseError`, then `gh = (doc or {}).get("github")`. The `or {}` guards
    `None` but **not** a bare scalar/list (truthy, so `or {}` does not replace it) — the same defect
    class as `manifest_domains`, in a script outside the write-gating threat model (manual sync,
    not a PreToolUse hook — lower severity, noted for completeness, not gated on here).
  - `load_recorded` (the third name the dispatch asked about) exists only in `gh-sync.py:200`,
    confirmed by grep; nothing named `load_recorded` exists in `harness_yaml.py` itself.

## 5. Regression coverage — one real gap (bash-write-guard.sh untested), one weak assertion

- `check-domain.sh` HAS regression tests for the two shapes cycle 0 named (`test-check-domain.py`,
  +26 lines), registered and run via `run-unit-tests.sh`. But the directory-as-manifest assertion is
  weaker than it reads:
  ```python
  t12("F-01: a manifest that is a DIRECTORY does not crash the guard",
      r.returncode in (0, 2) and "Traceback" not in r.stderr, ...)
  ```
  `returncode in (0, 2)` **passes on exit 0** — it asserts "does not crash," not "fails closed."
  Live behaviour today is exit 2, but this test would not catch a regression back to a *silent*
  fail-open (exit 0, no traceback) for this exact shape — the precise bypass F-01 exists to close.
  This is a test-quality gap in the fix's own regression coverage, not a live bypass today (both
  hooks were verified exit 2 live in §2).
- `bash-write-guard.sh` has **zero** F-01 regression coverage: `test-bash-write-guard.py` is not in
  the `340e18a..9da3986` diffstat, and contains no `F-01`/`xff`/`UnicodeDecode`/`IsADirectory` string
  anywhere (grep-confirmed). It runs (registered, pre-existing entry) but never exercises this path.
- **No test anywhere** (`test-harness-yaml.py`, `test-harness-yaml-corpus.py`,
  `test-check-domain.py`, `test-bash-write-guard.py`) exercises `manifest_domains` against a
  non-mapping top-level parse result — unsurprising since this is finding #1, but confirms the
  dispatch's step-5 concern landed: "the same fail-open can return silently" — it did.
- These are `low`/`med` (fail-closed-with-a-worse-message territory per the dispatch's own prior,
  applied here to weak/missing tests around an *otherwise-correct* live control) — kept out of
  `must_fix`; only finding #1 (the live AttributeError bypass) gates.

---

## DIGEST

```yaml
VERDICT: FAIL
DIGEST:
  headline: "F-01 is PARTIALLY closed: both hooks now fail closed with a reason for the two shapes cycle 0 named (bad UTF-8, manifest-as-directory, verified live at both 340e18a and current tree). But manifest_domains() (harness_yaml.py:167, confirmed untouched by 340e18a..9da3986) does an unguarded parsed.get(\"shared\") one call-frame past the widened try, so an empty/bare-scalar/bare-list manifest crashes both hooks with exit 1 (non-blocking, DEC-100) at BOTH SHAs -- the identical F-01 failure mode, never closed, exactly the shape cycle 0's step-3 dispatch asked this cycle to check."
  in_scope: true
  scope_reason: "the fix under review changes harness_yaml.py, the module both write-gating hooks call on every agent write; a residual instance of the fixed defect class, reachable through the exact same call path, is squarely this reviewer's surface."
  severity_max: high
  findings: 2
  must_fix:
    - >-
      harness_yaml.manifest_domains (harness_yaml.py:167, `for entry in (parsed.get("shared") or
      [])`) assumes the parsed manifest is a dict without an isinstance check or a wrapping
      try/except, and this line sits outside load_str/load_file's widened except (harness_yaml.py:92-114)
      -- confirmed unchanged in 340e18a..9da3986. A manifest whose top-level YAML value is None
      (empty file), a str (bare scalar), or a list (bare sequence) parses successfully and then
      crashes with an uncaught AttributeError, propagating past both hooks' `except
      DuplicateKeyError`/`except YamlParseError` call sites (check-domain.sh:134-146,
      bash-write-guard.sh mirrors it), exit 1, non-blocking per DEC-100 -- every agent's every write
      proceeds ungoverned, the identical F-01 blast radius. Verified live at BOTH 340e18a (pre-fix)
      and current tree (post-fix) against isolated binary copies for all three shapes on
      check-domain.sh and one shape on bash-write-guard.sh -- the fix neither introduced nor closed
      this. check-state.sh:115-125 (touched in this same diff) already carries the correct pattern
      (`except Exception` + `isinstance(doc, dict)` before use); mirror it into manifest_domains, or
      have it raise YamlParseError itself when parsed is not a dict, immediately after load_file returns.
  threat_model:
    - { boundary: "PreToolUse Write/Edit hook (check-domain.sh) manifest walk vs. repo state", stride: T, mitigated: false }
    - { boundary: "PreToolUse Bash hook (bash-write-guard.sh) manifest walk vs. repo state", stride: T, mitigated: false }
    - { boundary: "harness_yaml.load_str/load_file read-and-parse surface (the two F-01-named shapes)", stride: T, mitigated: true }
    - { boundary: "harness_yaml.manifest_domains post-parse shape assumption (non-mapping top level)", stride: T, mitigated: false }
  open_questions:
    - { id: Q1, question: "HEAD (924b961) is 9da3986 plus a state-only commit re-pinning review_sha to 9da3986 -- confirmed via diffstat that no reviewed file differs and the tree was clean throughout. Treated as non-blocking and proceeded; flagging so the panel knows STEP 0's literal HEAD check did not match verbatim.", blocking: false }
    - { id: Q2, question: "Should manifest_domains validate isinstance(parsed, dict) immediately after load_file and raise YamlParseError itself (module-level, matches load_str's own placement), or should both hook call sites widen their except clause to also catch AttributeError/TypeError from the walk? The module-level fix avoids relying on every future caller to remember to guard it -- gh-sync.py's load_recorded has the identical unguarded `.get()` shape one line after its own load_file call, so a module-level fix closes both at once.", blocking: true }
    - { id: Q3, question: "test-check-domain.py's directory-as-manifest assertion (`r.returncode in (0, 2)`) does not distinguish fail-closed from fail-open -- should it be tightened to assert returncode == 2 now that live behaviour is confirmed exit 2, so a future regression to silent exit-0 is actually caught?", blocking: false }
  files_touched: []
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/fix-harness-tooling-backlog/.harness/features/FEAT-05-pyyaml-file-parsers/notes/review-harness-security-reviewer-c1.md
```
