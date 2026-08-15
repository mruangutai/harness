# Security review — FEAT-14 write path (gh-sync.py, factory_claim.py, factory_decompose.py)

Range reviewed: `1bdfe3f..cf15660` (review_sha pinned `3abaedd`; commits above it are state-only).
Scope: the JSON read-modify-write rewrite of the three state-file writers.

## BLUF

`write_factory` (factory_decompose.py) kept its required atomicity — verified by reading the
function and confirmed by test. `save_recorded` (gh-sync.py) did not get the same property, and
this diff was the point where that asymmetry was introduced into the plan (write_factory's task
item explicitly says "KEEP THE ATOMICITY EXACTLY AS IT IS"; save_recorded's sibling item, three
lines later in the same task, says nothing about atomicity and describes exactly the code that
shipped). I reproduced file corruption from a simulated crash mid-write. This is the primary
finding.

## Finding 1 — `gh-sync.py:298-310` `save_recorded()` is a non-atomic, truncating read-modify-write
over the whole `feature.json`. **HIGH. FALSIFICATION-BACKED.**

```python
def save_recorded(feat_dir, rec):
    p = os.path.join(feat_dir, "feature.json")
    doc = harness_yaml.load_file(p)
    doc["github"] = {...}
    with open(p, "w", encoding="utf-8") as f:
        json.dump(doc, f, indent=2)
        f.write("\n")
```

`open(p, "w")` truncates the file to zero bytes the instant it is opened. There is no
`tempfile.mkstemp` + `os.replace`, unlike `factory_decompose.py`'s `write_factory` (below), which
this same task (T-05) explicitly required to keep that property. Any process termination between
open and the final `write()` — SIGKILL, OOM, `Ctrl-C`, a CI job timeout, a network-triggered kill in
the `gh` subprocess call sequencing around it — leaves `feature.json` truncated and unparsable.

**Probe** (disposable scratch dir, no `gh` calls, no live `.harness/features/` corpus touched — see
probe hygiene note below): wrote a valid 8-key `feature.json`, monkeypatched `json.dump` to write a
few bytes then raise mid-call (simulating a kill during the write), called `save_recorded()`
directly. Result:

```
crash occurred as expected, mid-write
feature.json contents after crash: '{"partial": tr'
CORRUPTED / INVALID JSON: Expecting value: line 1 column 13 (char 12)
```

The corruption destroys the **entire** feature record — `feature_id`, `status`, `review_sha`,
`cycles_used`, `runs`, everything — not just the `github` block being written, because the write is
a whole-document truncate-and-rewrite. `save_recorded` is called up to 6+ times per `gh-sync.py open`
run (once per milestone, per parent, per task issue create, per attach), each one a fresh crash
window.

**Blast radius, verified by reading `check-state.sh`**: a corrupted `feature.json` is *not* silently
ignored — `check-state.sh:160-170`, `:541-544`, `:837-840` each catch the parse failure and report
it as a hard violation (INV-6/7/8/12/21/23 all cite "does not parse, so INV-N cannot be checked").
So the gate fails closed and loudly, which is the right shape — but the underlying data is gone from
the file itself; recovery is a `git restore` of the last committed good copy, not anything the
harness does automatically. If the corrupted file were committed before anyone noticed, recovery
requires reaching further back in git history.

**Not a new introduction, but the rewrite was the moment to fix it and didn't.** I checked the
pre-image at `1bdfe3f` (`git show 1bdfe3f:.claude/skills/harness/bin/gh-sync.py`, old
`save_recorded`): the old text-splicing writer was `open(p, "w").write(t + ...)` — also a
whole-file, non-atomic write. So this is a carried-forward defect, not a regression this diff
introduced from scratch. What the diff *did* do: it rewrote this exact function under a task
(`plan.yaml` T-05, lines 858-889) whose sibling item for `factory_decompose.py`'s `write_factory`
(same task, same file, 9 lines later) explicitly calls out "KEEP THE ATOMICITY EXACTLY AS IT IS —
tempfile.mkstemp in the same directory, then os.replace. That property is why the function exists."
The `save_recorded` item (T-05 §2, `plan.yaml:868-878`) describes the read-modify-write in detail
and says nothing about atomicity. The plan carried the property forward for one writer and dropped
it for the other in the same breath — that asymmetry, not just the code, is worth fixing at the
plan level so it isn't dropped again.

**Not a DEC-174 carve-out file** — `gh-sync.py` is not `check-domain.sh`/`bash-write-guard.sh`/
`validate-digest.py`/`check-state.sh`, so the remedy is an ordinary fix cycle, not the main
session's. Minimum fix: mirror `write_factory`'s pattern exactly (`tempfile.mkstemp(dir=dirpath)` →
write → `fsync` → `os.replace`).

## Finding 2 (confirmation, not a defect) — `write_factory()` (`factory_decompose.py:142-186`) kept
its required atomicity. **READ-ONLY, quoted.**

```python
dirpath = os.path.dirname(path) or "."
fd, tmp = tempfile.mkstemp(prefix=".feature.json.", suffix=".tmp", dir=dirpath)
try:
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        f.write(text)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)
except BaseException:
    try:
        os.unlink(tmp)
    except OSError:
        pass
    raise
```

Temp file in the same directory (so `os.replace` stays on one filesystem), `fsync` before replace,
`os.replace` for the atomic swap, cleanup on any exception including `BaseException` (covers
`KeyboardInterrupt`/`SystemExit`, not just `Exception`). This is the correct pattern and it is what
Finding 1 should have matched. `test-factory-decompose.py:754-796` monkeypatches `os.replace` and
asserts it is called with a same-directory source and the real destination — a real assertion, not
a shape check.

Neither writer validates the resulting document against the schema before writing — but since both
writers only ever set one top-level key they own (`factory` / `github`) from internally-constructed,
type-safe Python state, there is no path here for either writer to write a document that violates
the schema on its own account. That gap is the schema-regression finding already established by qa
(SC-04/05/16, no automated schema-rejection fixtures) — out of scope for me per the dispatch, not
re-derived here.

## Injection / shell surface — assessed, no finding

All `gh` invocations in the diff are list-form `subprocess.run([GH] + args, ...)` with no
`shell=True`; no string-built shell command exists anywhere on this path. One low-signal item,
not a finding: `gh-sync.py:345-346` builds a `jq` filter with `brief["feat"]` (the feature
directory's basename) interpolated unescaped into a `-q` string:
`f'[.[] | select(.title == "{brief["feat"]}") | .number] | first'`. `jq` has no shell/command
execution, so a crafted value can at most break the filter's own syntax (surfacing as the existing
"milestone create failed and no existing one matches" SKIP, never a gate). The value is a feature
directory name, chosen by the operator/harness tooling, not externally-supplied. Assessed and
dismissed — noting it so a later reviewer doesn't re-raise it from scratch.

## Path traversal — pre-existing, unchanged, assessed

`factory_claim.py`'s `_BlockerCache` joins a GitHub issue's `feature:` label value directly into
`os.path.join(FEATURES_ROOT, feature, "plan.yaml"/"feature.json")` with no validation — a label
value containing `../` would be joined as-is. Confirmed via `git diff` that this diff's only change
to `factory_claim.py` is the filename rename (`feature.yaml` → `feature.json`) — the join logic
itself is untouched, so this is pre-existing and out of scope for this rewrite. It also stays
read-only (`harness_yaml.load_file`, `harness_yaml.load_plan`, both wrapped in
`try/except ... YamlParseError: return None`) — no write, no content returned to the caller, worst
case is a local file-existence/parseability probe gated by whoever already has label-write access
on the fleet's repos. Not reported as a finding; recorded here so it isn't re-derived.

## Concurrent-write clobbering

`write_factory` and `save_recorded` each do a whole-document read-modify-write with no file lock.
`write_factory`'s atomicity prevents *corruption* from a concurrent writer (each write is atomic;
last writer wins cleanly), but not *lost updates*: if `factory_decompose.py` and `gh-sync.py` ever
run concurrently against the same `feature.json` (they touch disjoint top-level keys — `factory` vs
`github` — but each reads-then-writes the *whole* document), whichever finishes last silently
discards the other's most recent change to its own key if that writer read before the other wrote.
I did not find evidence in `plan.yaml` or the docstrings that these two tools are ever dispatched
concurrently for the same feature — `gh-sync.py` is described as a "one-way, outbound... never a
gate" mirror (DEC-138) distinct from the factory publish flow, and I have no falsifying probe for
concurrent invocation given the probe-hygiene constraint against running these against the live
corpus. Recording as **MED, READ-ONLY, unconfirmed reachability** — worth a file lock or an
advisory `.lock` companion if concurrent dispatch of `gh-sync.py` alongside `factory_decompose.py`
for the same feature is ever a real deployment shape; not blocking given the reachability is
unconfirmed.

## Probe hygiene

- No `gh-sync.py`, `factory_claim.py`, `factory_decompose.py` run against the live
  `.harness/features/` corpus. The one probe run imported `gh-sync.py` as a module and called
  `save_recorded()` directly against a throwaway directory under the scratchpad — no `gh` subprocess
  was ever invoked (the crash was injected before any `gh` call in the flow this function is part
  of), and no live corpus file was touched.
- `git status --porcelain` before and after the probe: identical (two pre-existing untracked notes
  files from the pm/uat roles, unrelated to me).
- No DEC-174 carve-out file (`check-domain.sh`, `bash-write-guard.sh`, `validate-digest.py`,
  `check-state.sh`) was edited — I read `check-state.sh` and `check-domain.sh` only, to confirm
  blast radius and gate coverage.
- No `git worktree` was needed — the probe never touched a tracked file.

## Note on target path

The dispatch named `.harness/features/FEAT-14-feature-json-schema/notes/review-security-panel.md`
as this artifact's path. `bash-write-guard`/`check-domain.sh` deny that path for this role and name
the permitted pattern `notes/review-harness-security-reviewer-*.md`; this file is written there
instead, per the handoff skill's own rule that a dispatch-named receipt path does not override the
domain guard.

```yaml
VERDICT: FAIL
DIGEST:
  headline: "gh-sync.py's save_recorded() truncates feature.json in place with no tempfile/os.replace — a crash mid-write destroys the whole feature record, unlike write_factory which correctly kept the atomic-write pattern this same task required for it."
  in_scope: true
  scope_reason: "The dispatch's primary surface is the JSON read-modify-write rewrite of gh-sync.py and the two factory_* tools; this diff rewrote the exact non-atomic writer flagged."
  severity_max: high
  findings: 4
  must_fix:
    - "gh-sync.py:298-310 save_recorded() — non-atomic truncating write over the whole feature.json; reproduced corruption from a simulated crash mid-write. Fix: mirror factory_decompose.py's write_factory (tempfile.mkstemp in the same dir, fsync, os.replace)."
  threat_model:
    - { boundary: "process crash / kill during gh-sync.py's feature.json write", stride: "T", mitigated: false }
    - { boundary: "process crash / kill during factory_decompose.py's feature.json write", stride: "T", mitigated: true }
    - { boundary: "gh CLI invocation argv (list-form, no shell)", stride: "T", mitigated: true }
    - { boundary: "GitHub issue feature: label value -> os.path.join in factory_claim.py (pre-existing, unchanged, read-only)", stride: "I", mitigated: true }
    - { boundary: "concurrent write_factory + save_recorded on the same feature.json (no lock)", stride: "T", mitigated: false }
  open_questions:
    - { id: Q1, question: "Is gh-sync.py ever dispatched concurrently with factory_decompose.py for the same feature? If yes, the lost-update risk (no file lock, disjoint keys but whole-document RMW) needs a probe; if no, it can be closed as unreachable.", blocking: false }
  files_touched: []
  expertise_update: []
artifact: .harness/features/FEAT-14-feature-json-schema/notes/review-harness-security-reviewer-panel.md
```
