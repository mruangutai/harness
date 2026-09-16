# Security review — B-16 fix, review_sha c488218e

## Verdict: PASS, severity_max none. Scoped IN (test-only diff, looked, found nothing gating).

## Census (per-file, per O-07)
- `tests/unit/test-factory-claim.py` (+57/-8, only changed file) — IN scope, audited below.
- `.agents/skills/harness/bin/factory_claim.py` `_BlockerCache` (~L82-149) — context only, byte-
  identical to previously-passed pin 7104aa43 (orchestrator-measured); not re-audited here.
- The five `notes/*.md` / `feature.json` files also in the commit stat are process artifacts
  (qa report, backend/dev-ops receipts, answers file) — no code, no executable content, skimmed
  for embedded secrets (none) and not further audited.

## 1. Temp-file handling
`_run_5b_scenario()` (`tests/unit/test-factory-claim.py:1189`) calls
`tempfile.mkdtemp(prefix="claim-ws-5b-")`, same as ~20 other pre-existing call sites in this file
(5a, 5c, p1–p6, etc.) — this diff adds exactly one new invocation of it, from 5g reusing the
builder. `mkdtemp` draws from a CSPRNG suffix and creates the directory `0o700` (owner-only) under
the OS temp root — no predictable path, no world-readable window. Fixture content written inside
(fleet.yaml, plan.yaml, feature.json) is synthetic test data, not secrets. No `shutil.rmtree` is
called anywhere in this file for any of these directories (pre-existing, not introduced by this
diff) — bounded accumulation, not unbounded: each CI run creates a fixed, small, per-process set
under the ephemeral `TMPDIR`, which the OS/CI runner reclaims. One additional dir per suite run is
inert. Verdict: `mkdtemp`'s guarantees make this a non-issue; the doubled invocation changes
nothing.

## 2. Monkeypatch blast radius
5g assigns `claim._BlockerCache = _FeatureOnlyIssueMapCache` then restores
`claim._BlockerCache = saved_blocker_cache` in a `finally` (L1318-1321) that wraps only the call
to `_run_5b_scenario()`; the `check()` call and its `_5b_property_holds` evaluation happen after
the `finally` has already run, so the module-global is back to the real class before any later
code executes even if `check()` itself raised. Restoration is therefore unconditional on the
scenario's outcome — no path exists where a raised exception, an early return, or a mutant that
happens to run to completion could leave the swap live. `_BlockerCache()` is freshly instantiated
per candidate-loop run inside `factory_claim.main` (`factory_claim.py:333`), never held as a
singleton across calls, so even a case AFTER 5g would get a clean class reference. 5g is in fact
the last case in the file, which is a second, redundant containment (belt-and-suspenders, not the
load-bearing one — the `finally` is). No tampering-persistence path found.

## 3. Data exposure
`check(name, cond, detail)` (L41-48) prints `detail` — here the raw `(code, out, err)` triple —
to stdout on failure, for every case in the file including 5g; pre-existing pattern, not
introduced by this diff. Content of `out`/`err` in these cases is entirely synthetic fixture data:
`AS_LOGIN = "agent-1"` (a literal placeholder, not a real account or token), fixture repo names
(`acme/widget`, `kaya-ai/...`), fixture issue numbers/titles, and library-generated absolute paths
under the process's own `TMPDIR`. Nothing derived from a real credential, real login, or
production system enters this file — the module docstring's guarantee ("nothing here spawns a
subprocess and nothing touches a real board, repository, or this repository's own
`.harness/harness/features/`") holds for 5b/5g's fixtures on inspection. No sensitive data would
reach CI output on a 5g failure.

## 4. Injection surface
No shell/subprocess calls in this file at all (confirmed by the module docstring and by grep —
none of `os.system`, `subprocess.`, `shell=` appear). No fixture-controlled string reaches a
`re.compile(...)` call: 5f's `segment_scan` regex is a static literal, not built from fixture
data. No `os.path.join` in the new code takes a fixture-controlled path component; the paths built
in 5b/5g's fixtures are the same static-string joins the rest of the file already uses (repo
names/task ids used only as dict keys and string-literal comparisons, never joined into a
filesystem path). No path-escape-the-temp-root or template/format-string injection found.

## Non-gating backlog (none new)
- No new findings. The pre-existing "no `rmtree` cleanup of `mkdtemp` dirs anywhere in this
  file" pattern is unchanged by this diff (same shape at ~20 other call sites already) and is not
  logged as a new backlog item — it predates this commit and predates this review's scope.

## must_fix: []
