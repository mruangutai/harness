# Security review — FEAT-48 c9 — pin `27f8105b`

## BLUF
**FAIL.** A single, deterministic, non-racy bypass of the mutation-detection gate (`run_pool.py`'s
`--mutation-check`, the control this whole feature exists to build) lets any test/subprocess with
ordinary same-user code execution — exactly SC-10's own threat actor — plant a permanent, arbitrary
payload under the watched `bin/` tree with **zero detection**, in one pass, with no timing window.
Demonstrated end-to-end through the real CLI (below). This directly falsifies REQ-01/REQ-02/SC-10's
"a new file created under DIR" guarantee and DEC-211's amended coverage claim. It is a correction to
c8's own dismissal of `except OSError: continue`, not a re-litigation of anything already gated on.
The already-known `__pycache__`-skip evasion (M4, c8 §1b) remains open, unchanged, still MED —
restated, not re-gated. M5 (same-size/mtime-restore) is now accurately disclosed by DEC-211.

## 1. NEW — `_record`'s `except OSError: return` is a deterministic, single-pass blind spot (MUST FIX)

`run_pool.py:29-34`:
```
def _record(state, root, path):
    try:
        entry = os.lstat(path)
    except OSError:
        return
    state[...] = (entry.st_mode, entry.st_size, entry.st_mtime_ns)
```
reached from both the file loop (`:48-49`) and the directory-symlink branch (`:43-44`) that
993ac997 introduced to close c8's M1/M2.

**c8 checked this exact line and concluded "does NOT evade"**, reasoning only about a file that
*vanishes between listing and lstat*: present in one snapshot, absent from the other, still caught
by the key-union diff. That reasoning is correct for the **asymmetric** case and is the only case
c8 tested. It does not cover the **symmetric** case: an `OSError` that fires identically on *both*
the before- and after-snapshot calls, which needs no race at all — a directory lacking the execute
(search) bit lets `os.walk`/`os.listdir` enumerate filenames (`readdir` only needs read
permission) while the explicit `os.lstat(dir/name)` on each of those names fails (traversal
needs execute permission on `dir`). Both snapshot calls hit the identical failure, so
`before.get(name)` and `after.get(name)` are both `None` — never a diff.

**End-to-end reproduction, through the actual CLI, single test file, no pre-existing state, no
timing:**
```python
# one ordinary "test" the pool runs, exactly as run-unit-tests.sh invokes run_pool.py
import os
d = ".../watched/.tmp_cache"
os.makedirs(d)
open(os.path.join(d, "backdoor.py"), "w").write(
    "import os; os.system('echo BACKDOOR RAN')\n")
os.chmod(d, 0o600)          # rw-------: readable listing, un-lstat-able contents
```
```
$ python3 run_pool.py --mutation-check <watched> -- evil_test.py
----- evil_test.py (exit 0, 0.02s) -----
PASS evil_test.py
pool: 8 workers, 1 files, 0.02s wall
slowest: evil_test.py 0.02s
```
Exit **0**. No `MUTATED` line. `backdoor.py` persists on disk after the run (verified by
`chmod 0o700` afterward and re-`stat`ing it: present, unchanged). A minimal library-level probe
confirms the general shape: `before == after == {}` for the whole subtree, versus a single-shot
(one-call) race on the same path, which *is* still caught (`mutated == [name]`) — the blind spot
needs the durable condition, not luck.

**Reachability / privilege:** the actor is a test file the pool itself runs — the literal, only
threat model REQ-01/SC-10 target. `run-unit-tests.sh` execs every test as a plain `python3`
subprocess with no sandboxing, no uid change, no seccomp (read `run-unit-tests.sh` directly — the
only isolation anywhere in this feature is `isolated_bin()`'s copy-to-tempdir, which the mutation
check does not use). `os.chmod` on a directory the process just created is ordinary, unprivileged.
No elevation, no race window, no size-matching, no mtime forgery — strictly easier to execute than
M5 and the `__pycache__` skip, and it defeats detection **even when content, size, and mtime all
change**, which is exactly the property DEC-211's amended text (below) claims is sufficient for
capture.

**Severity: high.** Deterministic (not probabilistic), single invocation, zero special privilege,
complete bypass of the control this entire feature builds, falsifies a literal SC-10 clause
("a new file created under DIR ... is what a `git ls-files` watched set cannot see at all" — this
*is* that vector, uncaught). Not remote/credential-shaped, so not `critical`.

**Minimal correct remedy** (not applied — this is a validate mission): `_record` must distinguish
"target vanished" (legitimately a race, arguably ignorable) from "target unreadable because an
ancestor directory denies traversal" (a `PermissionError` on a directory whose existence `os.walk`
itself proved), e.g. treat `PermissionError` as a hard failure (`raise` or record a sentinel that
always compares unequal) rather than a silent `return`. A first cut: only swallow
`FileNotFoundError`, not the general `OSError`.

## 2. `__pycache__` directory-name skip — unchanged, still open, MED (restated from c8 §1b)

`run_pool.py:40`: `if name == "__pycache__": continue` — keyed purely on the directory's literal
**basename**, checked before the `os.walk` recursion decision and before the symlink check.
Confirmed still admits, via direct `snapshot()` probes:
- an arbitrary-extension payload (`evil.py`, not `.pyc`) nested directly under a `__pycache__`
  dir, newly created mid-run — invisible;
- arbitrary nesting depth under `__pycache__` — invisible;
- content mutation of a file *already inside* a pre-existing `__pycache__` dir — invisible with no
  size/mtime constraint at all (strictly broader than M5's same-size requirement);
- a **symlink literally named `__pycache__`** pointing at any target — the name check at `:40`
  fires before the `:43` `islink` check, so the symlink-entry tracking 993ac997 added for M1 is
  itself defeated whenever the symlink is named `__pycache__`; the entry is never recorded, in
  contrast to a plain-file/directory-symlink under any other name.

Mechanism is byte-for-byte unchanged since `b86ce66a` (pre-dates this whole feature); `test-run-pool.py`'s
new `case_cache_exclusion` (added in 993ac997, closing c8's M4 "no test leg") only exercises the
narrow, intended `.pyc`-creation case and does not discriminate it from the broader,
undisclosed shape above — a narrower skip (suffix-gated, not directory-gated) would pass the same
test. Not escalating past c8's MED: same actor, same reachability, already twice reviewed and
accepted as advisory, unchanged by this diff.

## 3. DEC-211's amended coverage claim — accurate for M5, still incomplete (direct ask)

`DECISIONS.md:6599-6604` at the pin now reads: *"A content-derived write inside bin is caught only
when it changes an entry's mode, size or observed nanosecond mtime. A same-size rewrite that
restores the original mtime is outside this metadata snapshot's coverage... No broader coverage is
claimed."* This is a genuine, accurate fix of the prior overclaim for **M5** specifically (verified:
`_record`'s tuple is exactly `(st_mode, st_size, st_mtime_ns)`, matching the sentence).

It is **not fully accurate**: §§1–2 above are both writes that are never even evaluated against
mode/size/mtime — they are omitted from the snapshot entirely, which is a categorically different
(and in §1's case, strictly worse) gap than "caught only when metadata changes." The sentence's
literal claim ("caught only when...") reads as a completeness statement over the metadata
dimension; §1 shows metadata changing (mode+size+mtime all differ) and still not being caught. A
reader relying on this paragraph as the coverage boundary is misled on both counts, one of them a
`high`-severity one this cycle first demonstrates deterministically.

## 4. Files examined, no finding beyond §§1–3

| file | disposition |
|---|---|
| `run_pool.py` | IN — §§1–2 above |
| `test-run-pool.py` | examined — `case_cache_exclusion` (new) validates only the intended `.pyc` shape, doesn't discriminate the broader skip (§2); no case exercises directory-permission blinding (§1) at all — a coverage gap mirroring the code gap, not a separate defect |
| `test-suite-independence.py` | examined — fixture writer (`_fixture_findings:198-200`) only ever `ast.parse`s and writes text into the caller's own `tempfile.TemporaryDirectory()`; grepped whole file for `exec(`/`eval(`/`subprocess`/`os.system`/`__import__` — zero hits; fixture names are fixed literals, no traversal |
| `test-check-domain.py` | examined — 993ac997's diff is a pure decomposition (`run_schema` split into `_schema_case`/`_inject_schema_crash`/`_schema_copy_control`/`_schema_crash_control`/`_schema_crash_cases`), byte-identical behavior; `isolated_bin()` usage unchanged |
| `test-check-fixture-secrets.py` | examined — pure decomposition of `run_sk_ant_red_proof`, no behavior change; all key-shaped literals carry `synthetic`/`THIS-IS-A-SYNTHETIC-CONTROL-VALUE` markers, none real |
| `run-unit-tests.sh` | examined — confirms §1's reachability: every test runs as a plain `python3` subprocess, no sandbox, no uid drop; argv/env wiring to `run_pool.py` unchanged from c8 |
| `isolated_bin.py` | examined — unchanged since c7 (not touched by 993ac997/27f8105b); `dest_root` is always a fresh `tempfile.mkdtemp()` from test code, never external input; c7's finding (`symlinks=False`, `copy2`, no issue) still holds |
| `plan.yaml` T-03 `ea6f51f` blob handling | examined (`plan.yaml:605-618`) — `names` is a fixed 3-item literal list, blobs written only under a fresh `tempfile.mkdtemp()`, no traversal, no symlink following, no cleanup of any real path (no `rmtree` at all here — minor hygiene leak of a small tempdir per run, not a security issue) |

## 5. T-06 `verify:` failing on `post == ["0"]` — disposition (security lens)

Not a security finding: no code path here has any security surface, and the discrepancy is a
verify-clause/documentation-shape mismatch, not a data-integrity or trust-boundary question. My
disposition: **the verify clause is the wrong artifact.** The carrier note
(`measurements-parallel-suite.md`) is doing exactly what T-06's own intent mandates — a fenced
verbatim transcript **and** a parsed summary line both containing `post-fix broken reads 0` — so
two occurrences of the same figure is the correct, intended shape, not a defect to fix in the note.
`findall` then seeing two matches and comparing against a literal one-element list `["0"]` is an
over-narrow assertion. Minimal correct remedy: assert `set(post) == {"0"} and post` (or dedupe
before compare), not list identity. Not a security must_fix; a backlog-row-shaped test-infra defect
for the code-reviewer/pm lens to own.

```yaml
VERDICT: FAIL
DIGEST:
  headline: "run_pool.py's OSError-swallowing _record (:29-34) is a deterministic, single-pass, non-racy bypass of the mutation-detection gate — a malicious test chmods a new dir to 0600 and its payload is never detected, reproduced end-to-end through the real CLI"
  in_scope: true
  scope_reason: "Diff's central artifact is a file-integrity/tamper-detection control (run_pool.py snapshot) guarding a shared trust boundary (bin/ vs. concurrently-run tests); STRIDE-Tampering surface squarely in scope, plus the DEC-211 documentation claim this task asked to verify for accuracy"
  severity_max: high
  findings: 5
  must_fix:
    - "run_pool.py:29-34 (_record) — a directory lacking the execute bit lets os.walk/os.listdir enumerate a filename while os.lstat(dir/name) raises PermissionError identically on both before- and after-snapshot calls, so the entry is silently omitted from both dicts and never compared. A single test file (the pool's own threat actor) creates a new dir under the watched bin/, writes an arbitrary payload into it, chmods it 0o600, and exits — run_pool.py --mutation-check reports exit 0, no MUTATED, and the payload persists on disk. Reproduced end-to-end through the real CLI (§1 of artifact). Falsifies REQ-01/REQ-02/SC-10's 'new file created under DIR' guarantee and the literal claim in the amended DEC-211 paragraph that a content-derived write is caught whenever mode/size/mtime change — here they all change and it is still uncaught."
  threat_model:
    - { boundary: "watched bin/ mutation detector vs. a test/subprocess that chmods a directory it just created", stride: T, mitigated: false }
    - { boundary: "watched bin/ mutation detector vs. a write nested under a directory literally named __pycache__ (any depth, any content)", stride: T, mitigated: false }
    - { boundary: "self-test fixture writes vs. live checkout (test-suite-independence.py)", stride: T, mitigated: true }
    - { boundary: "isolated_bin() private copies vs. shared live bin tree", stride: T, mitigated: true }
  open_questions: []
  files_touched: []
  expertise_update: []
artifact: .harness/harness/features/FEAT-48-parallel-safe-suite/notes/review-harness-security-reviewer-c9.md
```
