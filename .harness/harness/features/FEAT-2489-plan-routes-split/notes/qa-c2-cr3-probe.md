# FEAT-2489 validate c2 — QA whole-process CR-3 probe and seam replay (measurement only)

Run r-20261124-9-validate-validator · review_sha 25132b7ec29e9cdfaddfafeca7b7cd7d4c803cbd · base 261fdf726428bd8325fbd3d4beccad23b67e83cc.
Measurement-only follow-up to notes/review-harness-qa-c2.md (that gate run, its receipts and manifests are untouched;
nothing under runs/ written, no git writes, no source edits in any checkout).

## BLUF

| Item | Prediction | Result |
|---|---|---|
| P1 | CR-3 `import math as json` in retained `_clean`: canonical base exit 2 (`_classification_document json_file: artifact row absent from AST`), pin exit 0 (`0 unresolved ... across 103`) | **CONFIRMED** whole-process. Consolidation 0/0, default route mode 0/0 |
| P2 | a perturbation clean at base, finding-triggering at the pin, via the same alias leak | **CONFIRMED (constructed)**. base exit 0, pin exit 2 with `check-plan-routes.py::_clean json_string ... live AST row absent from migration inventory`; both single-plant controls behave as designed |
| P3 | seam-receipt appendix driver replays byte-for-byte modulo temp paths and PIN sha | **CONFIRMED**. 93/93 output lines identical after normalising the temp dir; `diff` exit 0 |
| P4 | (b) run in-tree by each side's own entry: both exit 1; pin stderr adds import-traceback frame(s) | **CONFIRMED**. Exits 1/1; the pin adds exactly 4 lines (Traceback header + the `check-plan-routes.py` line 44 import frame: File line, source line, `^` underline) |

Consequence for the seam receipt (inference from measured P1/P2, `[INFERENCE]` only as to scope): the receipt's
conservation item 5, "No tree clean at base gains a finding, and none that triggers at base goes clean at the pin",
does not hold for `--canonical-reader-audit`. P1 is a base-triggering tree that goes clean at the pin; P2 is a
base-clean tree that gains a finding at the pin. Both use the file-wide, last-write-wins alias map of
`_ReaderAliasCollector` (canonical_reader_audit.py:114-142 at the pin), applied per file by
`reader_candidates_from_source` (:199-210): after the split, a function-local import binding in one file no longer
reaches the reader calls that the move placed in the other file. Exit-code divergence 2→0 and 0→2 respectively.

## Method

- Interpreter: /opt/homebrew/opt/python@3.15/bin/python3.15, Python 3.15.2.
- Env: launched with `env -u CLAUDE_PROJECT_DIR -u HARNESS_PROJECT_DIR -u HARNESS_AGENT_TYPE PYTHONDONTWRITEBYTECODE=1`;
  each child additionally scrubs those three, sets PYTHONDONTWRITEBYTECODE=1 and HARNESS_PROJECT_DIR=cwd=the perturbed tree.
- Trees: fresh `git archive <rev> | tar -x` per variant per side under `tempfile.mkdtemp()`; removed at driver end.
- Entry: the perturbed tree's own `.claude/skills/harness/bin/check-plan-routes.py` for every P1/P2/P4 run.
- Plants: by AST, as the target function's first statement after its docstring, at the body indent (same `plant()`
  as the seam receipt driver).
- Drivers: /tmp/feat2489-cr3probe/probe.py (sha256 148f6207…6e1e, source in Appendix A) for P1/P2/P4;
  /tmp/feat2489-cr3probe/receipt.py (sha256 29cf9f87…e1cf) = notes/seam-straddle-receipt.txt lines 179-303
  extracted verbatim by awk, for P3. Neither committed.
- Commands:
  - `python3 receipt.py /Users/molchairuangutai/GitHub/harness 261fdf726428bd8325fbd3d4beccad23b67e83cc 25132b7ec29e9cdfaddfafeca7b7cd7d4c803cbd` → driver exit 0, stderr empty
  - `python3 probe.py /Users/molchairuangutai/GitHub/harness 261fdf726428bd8325fbd3d4beccad23b67e83cc 25132b7ec29e9cdfaddfafeca7b7cd7d4c803cbd` → driver exit 0, stderr empty

## P1 — CR-3 whole-process (CONFIRMED)

Plant `import math as json  # FEAT-2489 CR-3 probe` in `_clean` (base check-plan-routes.py before line 177; pin
check-plan-routes.py before line 182). At base the file's only `json` reader (`_classification_document`,
`json.load(source)`, base line 1257) is rebound to `math.load`, so the inventory row loses its AST site. At the pin
check-plan-routes.py has no `import json` and no json reader; `_classification_document` lives in
canonical_reader_audit.py, whose own alias map is untouched.

- canonical: base exit **2**, pin exit **0** (whole output in Appendix B, "P1 ['--canonical-reader-audit']").
- consolidation: base exit 0, pin exit 0 (`0 consolidation finding(s) under bin/` both).
- default route mode: base exit 0 (`0 violation(s) across 1 plan(s)`, 37 dirs examined), pin exit 0
  (`0 violation(s) across 2 plan(s)`, 38 examined). The extra plan and the 4 DEVIATION lines on the pin side come from
  this feature's own directory being present in the pin archive (its plan.yaml), not from the plant; DEVIATION lines
  are not counted as violations at either side.

## P2 — reverse direction (CONFIRMED, constructed)

Tree: two plants in the same archive.
1. Reader, in retained `_clean` (base before line 177; pin before line 182):
   `import json as probe_json` + `probe_json.loads("{}")` — a `json_string` reader with no inventory row.
2. Mask, in moved `_normalized_reader_name` (base check-plan-routes.py before line 1056 — later in source than plant 1,
   so it is the last write for `probe_json`; pin canonical_reader_audit.py before line 146): `import math as probe_json`.

A fresh alias name (`probe_json`) is used so no existing rowed reader is masked; the p2mask control proves it.

| variant | base exit | pin exit | finding |
|---|---|---|---|
| p2 (reader + mask) | **0** | **2** | pin only: `check-plan-routes.py::_clean json_string remedy=artifact_accessors.parse_gh_json: live AST row absent from migration inventory` |
| p2reader (reader alone) | 2 | 2 | same `_clean` line on both sides (base audit does see this reader when unmasked) |
| p2mask (mask alone) | 0 | 0 | none: the mask touches no existing rowed reader |

## P3 — seam receipt replay (CONFIRMED)

The bin/ and tests/ trees at 25132b7e equal the receipt's recorded TREE ids (`d542c641…` and `3f8731cd…`, `git rev-parse`
on both revs); 778ea992..25132b7e changes only 7 files under this feature's notes/. Comparison:
`diff <(receipt lines from "TMP " up to the closing ===== rule, temp dir → <TMP>) <(replay stdout, temp dir → <TMP>)`
→ exit 0 over 93 lines. Every exit ((a) 1/1, (b) 2/2, (b2) 2/2, (r) 2/2, controls 0/0 ×2), every PLANT line and every
stdout/stderr line reproduces; the only differences are the temp dir name (recorded `seam-ru07p2r0`, replay
`seam-71db9cvf`). The PIN sha appears only in the receipt header, not in driver output. Replay stdout in Appendix C.

## P4 — runner substitution for (b) (CONFIRMED)

Plant `def probe_unparseable(:` in moved `_normalized_reader_name` (base check-plan-routes.py before line 1054; pin
canonical_reader_audit.py before line 146); run each side's own perturbed entry, `--canonical-reader-audit`.
Both exit **1**, stdout empty on both. stderr whole:

base:
```text
  File "<TMP>/p4-base/.claude/skills/harness/bin/check-plan-routes.py", line 1054
    def probe_unparseable(:  # FEAT-2489 seam-straddle probe
                          ^
SyntaxError: invalid syntax
```
pin:
```text
Traceback (most recent call last):
  File "<TMP>/p4-pin/.claude/skills/harness/bin/check-plan-routes.py", line 44, in <module>
    from canonical_reader_audit import LEGAL_MAIN_SESSION_TOKEN, _run_canonical_reader_audit  # noqa: E402
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "<TMP>/p4-pin/.claude/skills/harness/bin/canonical_reader_audit.py", line 146
    def probe_unparseable(:  # FEAT-2489 seam-straddle probe
                          ^
SyntaxError: invalid syntax
```
(`<TMP>` = /var/folders/y3/nd_jssrd5dq8lbds73f0fy5m0000gn/T/cr3-9813kcrg.) Exactly what differs: (1) the pin adds
4 lines not present at base — `Traceback (most recent call last):` and the import frame (`File ".../check-plan-routes.py",
line 44, in <module>`, the `from canonical_reader_audit import ...` source line, its `^^^…` underline); base has no
Traceback header because the SyntaxError is raised compiling the entry script itself. (2) Locators in the shared last
4 lines: file path (check-plan-routes.py → canonical_reader_audit.py) and line (1054 → 146). The offending source line,
caret line and `SyntaxError: invalid syntax` are byte-identical.

## Principles applied

- Build the Lever: one throwaway driver (Appendix A) builds every perturbed tree and records every run, rather than
  hand-run commands; the receipt driver itself was replayed unchanged for P3.

## Appendix A — probe.py (throwaway, /tmp/feat2489-cr3probe/probe.py, not committed)

```python
"""Throwaway CR-3 whole-process probe driver (FEAT-2489 validate c2; never committed).

Usage: python3 probe.py <checkout> <BASE> <HEAD>
Extracts `git archive <rev>` into fresh temp trees, plants text by AST into named
functions, runs each side's own entry in-tree, prints argv/exit/stdout/stderr WHOLE.
"""
import ast, os, shutil, subprocess, sys, tempfile

CHECKOUT = sys.argv[1]
BASE, HEAD = sys.argv[2], sys.argv[3]
BIN = ".claude/skills/harness/bin"
ENTRY = BIN + "/check-plan-routes.py"
SCRUB = ("CLAUDE_PROJECT_DIR", "HARNESS_PROJECT_DIR", "HARNESS_AGENT_TYPE")
SPLIT = ("check-plan-routes.py", "canonical_reader_audit.py", "structure_audit.py")

ALIAS_JSON_MATH = ["import math as json  # FEAT-2489 CR-3 probe"]
# P2: retained _clean binds its own alias to json and calls a reader with no inventory row;
# moved _normalized_reader_name (later in source at base) rebinds the same alias to math.
P2_READER = ["import json as probe_json  # FEAT-2489 CR-3 reverse probe",
             "probe_json.loads(\"{}\")  # FEAT-2489 CR-3 reverse probe: a reader with no inventory row"]
P2_MASK = ["import math as probe_json  # FEAT-2489 CR-3 reverse probe mask"]
UNPARSEABLE = ["def probe_unparseable(:  # FEAT-2489 seam-straddle probe"]


def extract(rev, root):
    os.mkdir(root)
    archive = subprocess.Popen(["git", "archive", rev], cwd=CHECKOUT, stdout=subprocess.PIPE)
    subprocess.run(["tar", "-x", "-C", root], stdin=archive.stdout, check=True)
    archive.stdout.close()
    assert archive.wait() == 0


def defining_file(root, name):
    hits = []
    for base in SPLIT:
        path = os.path.join(root, BIN, base)
        if not os.path.isfile(path):
            continue
        tree = ast.parse(open(path, encoding="utf-8").read())
        hits += [(path, node) for node in tree.body
                 if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == name]
    assert len(hits) == 1, (name, hits)
    return hits[0]


def plant(root, name, lines):
    path, node = defining_file(root, name)
    body = node.body
    first = body[1] if (len(body) > 1 and isinstance(body[0], ast.Expr)
                        and isinstance(getattr(body[0], "value", None), ast.Constant)
                        and isinstance(body[0].value.value, str)) else body[0]
    source = open(path, encoding="utf-8").read().split("\n")
    indent = " " * first.col_offset
    at = first.lineno - 1
    source[at:at] = [indent + line for line in lines]
    open(path, "w", encoding="utf-8").write("\n".join(source))
    return f"{os.path.relpath(path, root)}::{name} (inserted before line {first.lineno})"


def run(runner, scanned, argv):
    env = {k: v for k, v in os.environ.items() if k not in SCRUB}
    env.update(PYTHONDONTWRITEBYTECODE="1", HARNESS_PROJECT_DIR=scanned)
    result = subprocess.run([sys.executable, os.path.join(runner, ENTRY), *argv], cwd=scanned,
                            env=env, capture_output=True, timeout=600)
    return result.returncode, result.stdout.decode(), result.stderr.decode()


def record(title, side, tree, argv):
    code, out, err = run(tree, tree, argv)
    print(f"----- {title} {side}: argv={[sys.executable, os.path.join(tree, ENTRY), *argv]} cwd=HARNESS_PROJECT_DIR={tree}")
    print("--- stdout (whole)")
    print(out, end="" if out.endswith("\n") or not out else "\n[no trailing newline]\n")
    print("--- stderr (whole)")
    print(err, end="" if err.endswith("\n") or not err else "\n[no trailing newline]\n")
    print(f"exit={code}")
    return code, out, err


def main():
    tmp = tempfile.mkdtemp(prefix="cr3-")
    revs = {"base": BASE, "pin": HEAD}
    variants = ("p1", "p2", "p2reader", "p2mask", "p4")
    trees = {}
    for variant in variants:
        for side, rev in revs.items():
            trees[variant, side] = os.path.join(tmp, f"{variant}-{side}")
            extract(rev, trees[variant, side])
    print(f"TMP {tmp}")
    print(f"PYTHON {sys.executable} {sys.version.split()[0]}")
    for side in revs:
        print(f"PLANT p1 {side}: {plant(trees['p1', side], '_clean', ALIAS_JSON_MATH)}")
        print(f"PLANT p2 {side}: reader {plant(trees['p2', side], '_clean', P2_READER)}")
        print(f"PLANT p2 {side}: mask {plant(trees['p2', side], '_normalized_reader_name', P2_MASK)}")
        print(f"PLANT p2reader {side}: reader {plant(trees['p2reader', side], '_clean', P2_READER)}")
        print(f"PLANT p2mask {side}: mask {plant(trees['p2mask', side], '_normalized_reader_name', P2_MASK)}")
        print(f"PLANT p4 {side}: syntax error {plant(trees['p4', side], '_normalized_reader_name', UNPARSEABLE)}")
    print()
    print("===== P1 `import math as json` first statement of retained _clean")
    for argv in (["--canonical-reader-audit"], ["--consolidation-audit"], []):
        for side in revs:
            record(f"P1 {argv or '[default route mode]'}", side, trees["p1", side], argv)
    print()
    print("===== P2 reverse: reader `probe_json.loads` (alias bound in retained _clean) + mask `import math as probe_json` in moved _normalized_reader_name")
    for variant in ("p2", "p2reader", "p2mask"):
        for side in revs:
            record(f"{variant} --canonical-reader-audit", side, trees[variant, side], ["--canonical-reader-audit"])
    print()
    print("===== P4 syntax error in moved _normalized_reader_name; each side's OWN perturbed entry in-tree")
    for side in revs:
        record("P4 --canonical-reader-audit", side, trees["p4", side], ["--canonical-reader-audit"])
    shutil.rmtree(tmp)


main()
```

## Appendix B — probe.py stdout, whole (stderr of the driver: empty; driver exit 0)

```text
TMP /var/folders/y3/nd_jssrd5dq8lbds73f0fy5m0000gn/T/cr3-9813kcrg
PYTHON /opt/homebrew/opt/python@3.15/bin/python3.15 3.15.2
PLANT p1 base: .claude/skills/harness/bin/check-plan-routes.py::_clean (inserted before line 177)
PLANT p2 base: reader .claude/skills/harness/bin/check-plan-routes.py::_clean (inserted before line 177)
PLANT p2 base: mask .claude/skills/harness/bin/check-plan-routes.py::_normalized_reader_name (inserted before line 1056)
PLANT p2reader base: reader .claude/skills/harness/bin/check-plan-routes.py::_clean (inserted before line 177)
PLANT p2mask base: mask .claude/skills/harness/bin/check-plan-routes.py::_normalized_reader_name (inserted before line 1054)
PLANT p4 base: syntax error .claude/skills/harness/bin/check-plan-routes.py::_normalized_reader_name (inserted before line 1054)
PLANT p1 pin: .claude/skills/harness/bin/check-plan-routes.py::_clean (inserted before line 182)
PLANT p2 pin: reader .claude/skills/harness/bin/check-plan-routes.py::_clean (inserted before line 182)
PLANT p2 pin: mask .claude/skills/harness/bin/canonical_reader_audit.py::_normalized_reader_name (inserted before line 146)
PLANT p2reader pin: reader .claude/skills/harness/bin/check-plan-routes.py::_clean (inserted before line 182)
PLANT p2mask pin: mask .claude/skills/harness/bin/canonical_reader_audit.py::_normalized_reader_name (inserted before line 146)
PLANT p4 pin: syntax error .claude/skills/harness/bin/canonical_reader_audit.py::_normalized_reader_name (inserted before line 146)

===== P1 `import math as json` first statement of retained _clean
----- P1 ['--canonical-reader-audit'] base: argv=['/opt/homebrew/opt/python@3.15/bin/python3.15', '/var/folders/y3/nd_jssrd5dq8lbds73f0fy5m0000gn/T/cr3-9813kcrg/p1-base/.claude/skills/harness/bin/check-plan-routes.py', '--canonical-reader-audit'] cwd=HARNESS_PROJECT_DIR=/var/folders/y3/nd_jssrd5dq8lbds73f0fy5m0000gn/T/cr3-9813kcrg/p1-base
--- stdout (whole)
CLASSIFICATION .claude/skills/harness/bin/check-plan-routes.py::_classification_document json_file: artifact row absent from AST. PLAN AMENDMENT REQUIRED
0 unresolved reader site(s) across 101 Python file(s)
--- stderr (whole)
exit=2
----- P1 ['--canonical-reader-audit'] pin: argv=['/opt/homebrew/opt/python@3.15/bin/python3.15', '/var/folders/y3/nd_jssrd5dq8lbds73f0fy5m0000gn/T/cr3-9813kcrg/p1-pin/.claude/skills/harness/bin/check-plan-routes.py', '--canonical-reader-audit'] cwd=HARNESS_PROJECT_DIR=/var/folders/y3/nd_jssrd5dq8lbds73f0fy5m0000gn/T/cr3-9813kcrg/p1-pin
--- stdout (whole)
0 unresolved reader site(s) across 103 Python file(s)
--- stderr (whole)
exit=0
----- P1 ['--consolidation-audit'] base: argv=['/opt/homebrew/opt/python@3.15/bin/python3.15', '/var/folders/y3/nd_jssrd5dq8lbds73f0fy5m0000gn/T/cr3-9813kcrg/p1-base/.claude/skills/harness/bin/check-plan-routes.py', '--consolidation-audit'] cwd=HARNESS_PROJECT_DIR=/var/folders/y3/nd_jssrd5dq8lbds73f0fy5m0000gn/T/cr3-9813kcrg/p1-base
--- stdout (whole)
0 consolidation finding(s) under bin/
--- stderr (whole)
exit=0
----- P1 ['--consolidation-audit'] pin: argv=['/opt/homebrew/opt/python@3.15/bin/python3.15', '/var/folders/y3/nd_jssrd5dq8lbds73f0fy5m0000gn/T/cr3-9813kcrg/p1-pin/.claude/skills/harness/bin/check-plan-routes.py', '--consolidation-audit'] cwd=HARNESS_PROJECT_DIR=/var/folders/y3/nd_jssrd5dq8lbds73f0fy5m0000gn/T/cr3-9813kcrg/p1-pin
--- stdout (whole)
0 consolidation finding(s) under bin/
--- stderr (whole)
exit=0
----- P1 [default route mode] base: argv=['/opt/homebrew/opt/python@3.15/bin/python3.15', '/var/folders/y3/nd_jssrd5dq8lbds73f0fy5m0000gn/T/cr3-9813kcrg/p1-base/.claude/skills/harness/bin/check-plan-routes.py'] cwd=HARNESS_PROJECT_DIR=/var/folders/y3/nd_jssrd5dq8lbds73f0fy5m0000gn/T/cr3-9813kcrg/p1-base
--- stdout (whole)
scanning /var/folders/y3/nd_jssrd5dq8lbds73f0fy5m0000gn/T/cr3-9813kcrg/p1-base/.harness/*/features/*/{plan.yaml,PLAN.md}
MANIFEST /var/folders/y3/nd_jssrd5dq8lbds73f0fy5m0000gn/T/cr3-9813kcrg/p1-base/.harness/team-config.yaml
OK T-01: declared main-session-direct (apps/web/package.json, apps/web/tsconfig.json, apps/web/next.config.ts, apps/web/next-env.d.ts, eslint.config.mjs, apps/web/vitest.config.ts, playwright.config.ts, .node-version, .npmrc, .env.example, .gitignore ungranted)
OK T-02 granted to harness-backend-dev, harness-data-engineer, harness-dev-ops, harness-frontend-dev, harness-qa
OK T-03 granted to harness-backend-dev, harness-frontend-dev
OK T-04 granted to harness-data-engineer
OK T-05 granted to harness-backend-dev, harness-frontend-dev
OK T-06 granted to harness-backend-dev, harness-frontend-dev
OK T-07 granted to harness-backend-dev, harness-frontend-dev
OK T-08 granted to harness-backend-dev, harness-dev-ops, harness-qa
OK T-09: declared main-session-direct (.harness/harness.json ungranted)
OK T-10 granted to harness-documentor
0 violation(s) across 1 plan(s)
examined 37 feature dir(s); 36 skipped as shipped
--- stderr (whole)
exit=0
----- P1 [default route mode] pin: argv=['/opt/homebrew/opt/python@3.15/bin/python3.15', '/var/folders/y3/nd_jssrd5dq8lbds73f0fy5m0000gn/T/cr3-9813kcrg/p1-pin/.claude/skills/harness/bin/check-plan-routes.py'] cwd=HARNESS_PROJECT_DIR=/var/folders/y3/nd_jssrd5dq8lbds73f0fy5m0000gn/T/cr3-9813kcrg/p1-pin
--- stdout (whole)
scanning /var/folders/y3/nd_jssrd5dq8lbds73f0fy5m0000gn/T/cr3-9813kcrg/p1-pin/.harness/*/features/*/{plan.yaml,PLAN.md}
MANIFEST /var/folders/y3/nd_jssrd5dq8lbds73f0fy5m0000gn/T/cr3-9813kcrg/p1-pin/.harness/team-config.yaml
DEVIATION T-01 tests/integration/test-check-plan-routes.py, .harness/harness/features/FEAT-2489-plan-routes-split/notes/red-t01-canonical-self-test.txt, .harness/harness/features/FEAT-2489-plan-routes-split/notes/green-t01-default-run.txt granted to harness-backend-dev, harness-dev-ops, harness-orchestrator, harness-qa but declared main-session-direct
DEVIATION T-02 .harness/harness/features/FEAT-2489-plan-routes-split/notes/split-equivalence.py granted to harness-orchestrator but declared main-session-direct
DEVIATION T-03 .claude/skills/harness/bin/check-plan-routes.py, .claude/skills/harness/bin/canonical_reader_audit.py, .claude/skills/harness/bin/structure_audit.py, .claude/skills/harness/bin/plan_merge/check.py, tests/integration/test-check-plan-routes.py, tests/integration/test-checker-structure-locks.py, tests/integration/test-structure-audit-single-pass.py, tests/unit/test-structure-audit-index.py, tests/unit/test-broad-catch-census.py, .harness/harness/features/FEAT-2489-plan-routes-split/notes/red-t03-stale-inventory.txt granted to harness-backend-dev, harness-dev-ops, harness-orchestrator, harness-qa but declared main-session-direct
DEVIATION T-04 tests/integration/canonical-reader-classification.json, .harness/harness/features/FEAT-2489-plan-routes-split/notes/equivalence-final.txt, .harness/harness/features/FEAT-2489-plan-routes-split/notes/green-t04-suites.txt granted to harness-backend-dev, harness-dev-ops, harness-orchestrator, harness-qa but declared main-session-direct
OK T-01: declared main-session-direct (apps/web/package.json, apps/web/tsconfig.json, apps/web/next.config.ts, apps/web/next-env.d.ts, eslint.config.mjs, apps/web/vitest.config.ts, playwright.config.ts, .node-version, .npmrc, .env.example, .gitignore ungranted)
OK T-02 granted to harness-backend-dev, harness-data-engineer, harness-dev-ops, harness-frontend-dev, harness-qa
OK T-03 granted to harness-backend-dev, harness-frontend-dev
OK T-04 granted to harness-data-engineer
OK T-05 granted to harness-backend-dev, harness-frontend-dev
OK T-06 granted to harness-backend-dev, harness-frontend-dev
OK T-07 granted to harness-backend-dev, harness-frontend-dev
OK T-08 granted to harness-backend-dev, harness-dev-ops, harness-qa
OK T-09: declared main-session-direct (.harness/harness.json ungranted)
OK T-10 granted to harness-documentor
0 violation(s) across 2 plan(s)
examined 38 feature dir(s); 36 skipped as shipped
--- stderr (whole)
exit=0

===== P2 reverse: reader `probe_json.loads` (alias bound in retained _clean) + mask `import math as probe_json` in moved _normalized_reader_name
----- p2 --canonical-reader-audit base: argv=['/opt/homebrew/opt/python@3.15/bin/python3.15', '/var/folders/y3/nd_jssrd5dq8lbds73f0fy5m0000gn/T/cr3-9813kcrg/p2-base/.claude/skills/harness/bin/check-plan-routes.py', '--canonical-reader-audit'] cwd=HARNESS_PROJECT_DIR=/var/folders/y3/nd_jssrd5dq8lbds73f0fy5m0000gn/T/cr3-9813kcrg/p2-base
--- stdout (whole)
0 unresolved reader site(s) across 101 Python file(s)
--- stderr (whole)
exit=0
----- p2 --canonical-reader-audit pin: argv=['/opt/homebrew/opt/python@3.15/bin/python3.15', '/var/folders/y3/nd_jssrd5dq8lbds73f0fy5m0000gn/T/cr3-9813kcrg/p2-pin/.claude/skills/harness/bin/check-plan-routes.py', '--canonical-reader-audit'] cwd=HARNESS_PROJECT_DIR=/var/folders/y3/nd_jssrd5dq8lbds73f0fy5m0000gn/T/cr3-9813kcrg/p2-pin
--- stdout (whole)
CLASSIFICATION .claude/skills/harness/bin/check-plan-routes.py::_clean json_string remedy=artifact_accessors.parse_gh_json: live AST row absent from migration inventory. PLAN AMENDMENT REQUIRED
0 unresolved reader site(s) across 103 Python file(s)
--- stderr (whole)
exit=2
----- p2reader --canonical-reader-audit base: argv=['/opt/homebrew/opt/python@3.15/bin/python3.15', '/var/folders/y3/nd_jssrd5dq8lbds73f0fy5m0000gn/T/cr3-9813kcrg/p2reader-base/.claude/skills/harness/bin/check-plan-routes.py', '--canonical-reader-audit'] cwd=HARNESS_PROJECT_DIR=/var/folders/y3/nd_jssrd5dq8lbds73f0fy5m0000gn/T/cr3-9813kcrg/p2reader-base
--- stdout (whole)
CLASSIFICATION .claude/skills/harness/bin/check-plan-routes.py::_clean json_string remedy=artifact_accessors.parse_gh_json: live AST row absent from migration inventory. PLAN AMENDMENT REQUIRED
0 unresolved reader site(s) across 101 Python file(s)
--- stderr (whole)
exit=2
----- p2reader --canonical-reader-audit pin: argv=['/opt/homebrew/opt/python@3.15/bin/python3.15', '/var/folders/y3/nd_jssrd5dq8lbds73f0fy5m0000gn/T/cr3-9813kcrg/p2reader-pin/.claude/skills/harness/bin/check-plan-routes.py', '--canonical-reader-audit'] cwd=HARNESS_PROJECT_DIR=/var/folders/y3/nd_jssrd5dq8lbds73f0fy5m0000gn/T/cr3-9813kcrg/p2reader-pin
--- stdout (whole)
CLASSIFICATION .claude/skills/harness/bin/check-plan-routes.py::_clean json_string remedy=artifact_accessors.parse_gh_json: live AST row absent from migration inventory. PLAN AMENDMENT REQUIRED
0 unresolved reader site(s) across 103 Python file(s)
--- stderr (whole)
exit=2
----- p2mask --canonical-reader-audit base: argv=['/opt/homebrew/opt/python@3.15/bin/python3.15', '/var/folders/y3/nd_jssrd5dq8lbds73f0fy5m0000gn/T/cr3-9813kcrg/p2mask-base/.claude/skills/harness/bin/check-plan-routes.py', '--canonical-reader-audit'] cwd=HARNESS_PROJECT_DIR=/var/folders/y3/nd_jssrd5dq8lbds73f0fy5m0000gn/T/cr3-9813kcrg/p2mask-base
--- stdout (whole)
0 unresolved reader site(s) across 101 Python file(s)
--- stderr (whole)
exit=0
----- p2mask --canonical-reader-audit pin: argv=['/opt/homebrew/opt/python@3.15/bin/python3.15', '/var/folders/y3/nd_jssrd5dq8lbds73f0fy5m0000gn/T/cr3-9813kcrg/p2mask-pin/.claude/skills/harness/bin/check-plan-routes.py', '--canonical-reader-audit'] cwd=HARNESS_PROJECT_DIR=/var/folders/y3/nd_jssrd5dq8lbds73f0fy5m0000gn/T/cr3-9813kcrg/p2mask-pin
--- stdout (whole)
0 unresolved reader site(s) across 103 Python file(s)
--- stderr (whole)
exit=0

===== P4 syntax error in moved _normalized_reader_name; each side's OWN perturbed entry in-tree
----- P4 --canonical-reader-audit base: argv=['/opt/homebrew/opt/python@3.15/bin/python3.15', '/var/folders/y3/nd_jssrd5dq8lbds73f0fy5m0000gn/T/cr3-9813kcrg/p4-base/.claude/skills/harness/bin/check-plan-routes.py', '--canonical-reader-audit'] cwd=HARNESS_PROJECT_DIR=/var/folders/y3/nd_jssrd5dq8lbds73f0fy5m0000gn/T/cr3-9813kcrg/p4-base
--- stdout (whole)
--- stderr (whole)
  File "/var/folders/y3/nd_jssrd5dq8lbds73f0fy5m0000gn/T/cr3-9813kcrg/p4-base/.claude/skills/harness/bin/check-plan-routes.py", line 1054
    def probe_unparseable(:  # FEAT-2489 seam-straddle probe
                          ^
SyntaxError: invalid syntax
exit=1
----- P4 --canonical-reader-audit pin: argv=['/opt/homebrew/opt/python@3.15/bin/python3.15', '/var/folders/y3/nd_jssrd5dq8lbds73f0fy5m0000gn/T/cr3-9813kcrg/p4-pin/.claude/skills/harness/bin/check-plan-routes.py', '--canonical-reader-audit'] cwd=HARNESS_PROJECT_DIR=/var/folders/y3/nd_jssrd5dq8lbds73f0fy5m0000gn/T/cr3-9813kcrg/p4-pin
--- stdout (whole)
--- stderr (whole)
Traceback (most recent call last):
  File "/var/folders/y3/nd_jssrd5dq8lbds73f0fy5m0000gn/T/cr3-9813kcrg/p4-pin/.claude/skills/harness/bin/check-plan-routes.py", line 44, in <module>
    from canonical_reader_audit import LEGAL_MAIN_SESSION_TOKEN, _run_canonical_reader_audit  # noqa: E402
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/var/folders/y3/nd_jssrd5dq8lbds73f0fy5m0000gn/T/cr3-9813kcrg/p4-pin/.claude/skills/harness/bin/canonical_reader_audit.py", line 146
    def probe_unparseable(:  # FEAT-2489 seam-straddle probe
                          ^
SyntaxError: invalid syntax
exit=1
```

## Appendix C — P3 replay stdout (receipt.py, HEAD=25132b7e), whole; driver stderr empty, exit 0

Identical to notes/seam-straddle-receipt.txt from its `TMP` line to the closing rule after replacing
`/var/folders/y3/nd_jssrd5dq8lbds73f0fy5m0000gn/T/seam-ru07p2r0` with `/var/folders/y3/nd_jssrd5dq8lbds73f0fy5m0000gn/T/seam-71db9cvf`
(`diff` exit 0, 93 lines; raw replay at /tmp/feat2489-cr3probe/receipt-replay.out, sha256 f520b3bf…6deb, transient).
Exits reproduced: (a) base 1 / pin 1; (b) 2 / 2; (b2) 2 / 2; (r) 2 / 2; CONTROL consolidation 0 / 0, canonical 0 / 0
(`101` / `103` Python files). Every PLANT line reproduced (base _clean 177, _may_be_program 2529, _normalized_reader_name
1054/1056; pin _clean 182, structure_audit.py _may_be_program 846, canonical_reader_audit.py _normalized_reader_name 146).
The stdout bodies are the receipt's recorded bodies verbatim (not re-pasted here to keep a single source; the diff is the
evidence of identity).
