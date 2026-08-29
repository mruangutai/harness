# Receipt — harness-dev-ops — T-18 — run 2026-08-29-07-eng

## Task

T-18: Register the two new checkers in the harness test-kind config (`.harness/harness.json`
integration `detect` string only). Verified against `plan.yaml` T-18 verify: block before running
— byte-identical to the dispatch's quoted copy.

## Change

Appended, in the order given, to the end of `test_kinds.integration.detect` (pipe-separated
string, not converted to a list, nothing reordered):

```
.claude/skills/harness/bin/test-check-decision-anchors.py
.claude/skills/harness/bin/test-check-decision-claims.py
```

No other field touched. `cmd` fields for functional/component/ui/eval/typecheck untouched
(confirmed by normalized-JSON diff below — only one line differs across the whole file).

## Verify command — verbatim run from worktree root

```
cd "$(git rev-parse --show-toplevel)"
python3 - <<'PY'
import json, sys
d = json.load(open('.harness/harness.json'))
det = d['test_kinds']['integration']['detect'].split('|')
need = ['.claude/skills/harness/bin/test-check-decision-anchors.py',
        '.claude/skills/harness/bin/test-check-decision-claims.py']
missing = [n for n in need if n not in det]
if missing:
    print('MISSING:', missing); sys.exit(1)
print('registered:', len(det), 'integration paths')
PY
```

Output:
```
registered: 30 integration paths
```
Exit status: `0`

## Structural-integrity proof — normalized JSON before/after diff

Captured `json.dumps(json.load(...), sort_keys=True, indent=2)` before the edit (`/tmp/before.json`,
196 lines) and after (`/tmp/after.json`, 196 lines). Line-by-line diff shows exactly one line
changed (line 98, the `integration.detect` value), tail comparison:

```
BEFORE tail: ...test-hooks-install.py|.claude/skills/harness/bin/test-gh-close-gate.py",
AFTER  tail: ...test-hooks-install.py|.claude/skills/harness/bin/test-gh-close-gate.py|.claude/skills/harness/bin/test-check-decision-anchors.py|.claude/skills/harness/bin/test-check-decision-claims.py",
```

Same line count (196) both sides; no key added, removed, or reordered; no other kind's `cmd`
touched.

## git diff — .harness/harness.json (worktree)

```diff
diff --git a/.harness/harness.json b/.harness/harness.json
index 95a1d29..aa21850 100644
--- a/.harness/harness.json
+++ b/.harness/harness.json
@@ -116,7 +116,7 @@
       "signed": "DEC-187"
     },
     "integration": {
-      "detect": "tests/integration/**|...|.claude/skills/harness/bin/test-gh-close-gate.py",
+      "detect": "tests/integration/**|...|.claude/skills/harness/bin/test-gh-close-gate.py|.claude/skills/harness/bin/test-check-decision-anchors.py|.claude/skills/harness/bin/test-check-decision-claims.py",
       "exclude": ".claude/worktrees/**|node_modules/**|vendor/**|.venv/**",
       "cmd": ".agents/skills/harness/bin/run-unit-tests.sh --kind integration",
       "status": "active"
```

(Middle of the pipe-string elided here for readability only — the full untruncated line was
diffed programmatically above and confirmed to have exactly the two new segments appended at the
tail, nothing else changed.)

## Test-file existence check

Both paths named in the dispatch exist on disk in the worktree, executable:

```
-rwxr-xr-x  .claude/skills/harness/bin/test-check-decision-anchors.py  (8788 bytes)
-rwxr-xr-x  .claude/skills/harness/bin/test-check-decision-claims.py   (9166 bytes)
```

## Isolation check (known environment defect guard)

- `git -C <worktree> status --porcelain` after edit: shows `M .harness/harness.json` — the change
  landed in the worktree.
- `git -C /Users/molchairuangutai/GitHub/harness status --porcelain` captured before and after this
  task's edit: byte-identical (`diff` empty). No file in the MAIN checkout changed. The 11
  pre-existing untracked entries there (feature dirs, logs, notes under `.harness/`) predate this
  task and are unrelated to `harness.json`.

## Scope

Did not touch `run-unit-tests.sh` (T-19), `.github/workflows/tests.yml`, or any checker source. Did
not run `run-unit-tests.sh`. Committed nothing.
