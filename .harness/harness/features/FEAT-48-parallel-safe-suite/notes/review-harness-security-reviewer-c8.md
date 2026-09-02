# Security review — FEAT-48 c8 — pin `e64e863e`

## BLUF
No new must-fix. M1 (symlink blind spot) is genuinely closed for the vectors named in c7.
Two evasions against the mutation detector remain live and reproduced, both **pre-existing**
(unchanged since `b86ce66a`, not introduced by this diff): M5 (same-size + `os.utime`-restored
content swap) and the `__pycache__`/`*.pyc` skip. The `__pycache__`/`.pyc` evasion is the more
realistic of the two — no timing precision required, just a filename convention — and is
undisclosed anywhere a reader would find it; it deserves the same disclosure treatment already
tracked for M5. The fix's own new code (`os.lstat` on symlinked dirs, `run_pool.py:38`) has one
genuine new crash edge case, but it fails **closed** (nonzero exit), and needs a true two-call
TOCTOU race to trigger — not "create a file to turn off the detector." `code_grade: fail` remains
the standing gate blocker per the lead's evidence; not this role's finding to re-litigate.

## 1. Tampering / evasion against `snapshot()` (`run_pool.py:29-54`)

State tuple: `(st_mode, st_size, st_mtime_ns)`, compared by key-union at `:107-108`.

**(a) Same-size content swap + `os.utime` restore — OPEN, restated at e64e863e.**
Reproduced live: wrote `AAAA`→`BBBB` (same 4 bytes) to a watched file, restored `st_mtime_ns`
via `os.utime`. `before == after` byte-for-byte, tuple identical
`(33188, 4, 1788341873643890123)`. No `MUTATED` line would print. Requires deliberate forge
(know the original mtime, keep the byte length constant, call `os.utime` with `ns=`) — not
something a test script does by accident. c7's M5, unchanged by this diff (adding `st_mode`
narrows nothing here — mode is also unchanged by the swap). **Ranked MEDIUM**: realistic actor
is a test/fixture deliberately gaming the gate, not an accidental collision.

**(b) `__pycache__`/`*.pyc` skip — pre-existing, NOT introduced by this diff.** Verified via
`git show e64e863e^:…/run_pool.py:29-42` (`b86ce66a`) — the `__pycache__` dir-skip and
`.pyc`-suffix skip are byte-identical in intent pre- and post-fix; `git diff b86ce66a..e64e863e`
only touches the `os.stat`→`os.lstat`/`st_mode`/symlink-entry logic (`artifact://3311`). Live
repro: created `watched/__pycache__/evil.txt` and `watched/evil.pyc` with attacker content —
neither appears in `snapshot()`'s output at all. **Ranked HIGHER exploitability than (a)**: no
timing, no size-matching, no restore step — just a filename/dirname convention any test or agent
script can hit by accident (writing a helper named `foo.pyc`) or by design. c7's M4 asked for a
test leg on this; confirmed still absent — `grep pycache|\.pyc test-run-pool.py` → no matches.

**(c) `except OSError: continue` at `:50-51` — checked, does NOT evade.** A file that vanishes
between `os.walk`'s listing and the explicit `lstat` is skipped from *that* snapshot's dict, but
the top-level comparison is `before.get(name) != after.get(name)` over the *key union*
(`:107-108`), so a name present with a tuple in one snapshot and absent (`None`) from the other
still trips `MUTATED`. Verified by reading the union-based diff, not just the try/except in
isolation — no repro needed, the logic is sufficient.

**(d) Symlinked directory now recorded as a single leaf entry (`:37-40`) instead of descended —
NOT a regression.** Both `b86ce66a` and `e64e863e` leave `os.walk`'s `followlinks` at its
default (`False`); neither version ever set it, so `os.walk` never descended into a directory
symlink's *contents* in either version — that blind spot is a pre-existing property of
`os.walk(followlinks=False)`, unchanged by this diff. What the diff adds is tracking of the
symlink *entry itself* (create/remove/retarget), which the old code recorded nowhere (old code
had no `islink` branch at all — a symlinked dir was invisible in totality). Net effect of the
diff on (d): strictly narrows the blind spot, does not widen it.

## 2. The fix's own new surface — `os.lstat` outside try/except at `run_pool.py:38`

Reproduced three scenarios directly against the live `snapshot()`:
- Dangling directory symlink present throughout the walk: no raise (`os.lstat` on the symlink
  itself succeeds regardless of target).
- Symlink loop (dir symlink pointing back at its own parent): no raise — `followlinks=False`
  means it is never traversed, just recorded as one leaf entry.
- Unreadable directory (`chmod 000`): no raise — `os.walk`'s default `onerror=None` silently
  drops directories it cannot `listdir`.
- **True TOCTOU** — removal of the symlink strictly *between* `os.path.islink`'s internal
  `lstat` (`:37`) and the code's own explicit `lstat` (`:38`, no try/except): reproduced by
  monkeypatching `os.lstat` to delete the link on its second call for that path.
  `FileNotFoundError` propagates uncaught out of `snapshot()`, through `main()` (`before =
  snapshot(root)` at `:82` has no try/except), and out of the process as an unhandled exception.

This is real but is **not** "a file creation turns off the detector": it needs a second thread
or process to unlink the exact symlink in the sub-microsecond window between two specific syscalls
inside `snapshot()`. It is also **not fail-open** — an unhandled exception exits nonzero
(CPython default), the same polarity as a genuine `MUTATED` failure; the CI gate still reddens.
The real cost is diagnostic, not a bypass: a crash mid-"after"-snapshot discards the `MUTATED`
report and the summary line, so a reader sees a traceback instead of an attributed mutation.
**Ranked LOW** — narrower and less reachable than either evasion in §1, and it fails closed.

## 3. `_fixture_findings` — checked, parses only

`scan_file` (`test-suite-independence.py:126-133`) calls `ast.parse` only; grepped the whole file
for `exec(`, `eval(`, `subprocess`, `os.system`, `__import__` — zero matches. `_fixture_findings`
(`:157-161`) writes into the `tempfile.TemporaryDirectory()` passed in by `run_self_tests`
(`:170-172`), never the live checkout. Verified by running, not just reading: `git status
--porcelain` identical before/after a direct run (only a sibling reviewer's pre-existing untracked
note present both times), exit 0, all six `ok self-test …` lines present, `discovered 63`.

## 4. `run_self_tests` — checked negative, no shell

`:216-231` reads the live checkout via `os.path.isfile`/`resolve_scan_root`/`scan_directory`
only — no `subprocess`, no shell interpolation anywhere in the file (grep, above). Confirmed
explicitly as a checked negative, not by omission.

## 5. c7 reconciliation (this lens)

| Finding | Disposition | Evidence |
|---|---|---|
| HIGH — symlink blind spot (M1) | **closed** | §2 above; dangling + linked-dir both now produce `MUTATED`, clean control does not (matches lead's P3); pre-fix (`b86ce66a`) copy verified blind to both. |
| HIGH — zero durable self-test | **closed** | §3; six self-tests run unconditionally in `main()`, all discriminate (lead's P1/P2 accepted — independently re-confirmed exit 0 / six `ok` lines here). |
| HIGH — `code_grade: fail` | **open, not this lens** | Not a security-shaped defect; deferred to code-reviewer/lead evidence (9 records, was 7). |
| MED — same-size/same-mtime swap (M5) | **open, restated** | §1(a). |
| MED — no `__pycache__` leg in test-run-pool.py (M4) | **open, restated, and higher exploitability than M5** | §1(b). |

**M5 disclosure, checked separately from the defect:** not written down anywhere a reader of the
gate would find it. Grepped `run_pool.py` (docstring + the `MUTATED`/REQ-01 message text at
`:114`) — no mention of the size/mtime-only tuple or a swap limitation. Grepped `DEC-211`'s
"coverage boundary" paragraph (`DECISIONS.md:6596-6608`) — it discloses the *static-scan's*
taint blind spots (relative-literal `__file__`, content-derived targets) in detail, and closes
with "No broader coverage is claimed than these two mechanisms deliver," but never names the
runtime `snapshot()`'s own size/mtime collision specifically. Grepped `BRIEF.md` — no mention.
The only place this is written down is `STATE.md:52-54`, an internal validate-cycle note, not a
reader-facing artifact — so from the gate's own documentation, this limitation is **undisclosed**.
Same conclusion applies to the `__pycache__`/`.pyc` skip: no docstring, message, or DEC-211
sentence names it as a deliberate exclusion versus an oversight.

## Open questions
None blocking for this lens — M4/M5 disclosure is a documentation gap the pm/lead already track
(STATE.md), not a new discovery.

```yaml
VERDICT: PASS
DIGEST:
  headline: "M1 symlink fix holds under repro; M5 and the __pycache__/.pyc skip remain live, pre-existing, undisclosed evasions — no new must-fix"
  in_scope: true
  scope_reason: "Diff is a mutation-detection security control (run_pool.py snapshot) plus its self-test harness; STRIDE-Tampering surface against a file-integrity gate, not a web/authn surface"
  severity_max: med
  findings: 4
  must_fix: []
  threat_model:
    - { boundary: "watched-root mutation detector vs. concurrent test/agent writer", stride: T, mitigated: false }
    - { boundary: "snapshot() lstat on symlinked dir vs. concurrent unlink (TOCTOU)", stride: D, mitigated: false }
    - { boundary: "self-test fixture writes vs. live checkout", stride: T, mitigated: true }
  open_questions: []
  files_touched: []
  expertise_update: []
artifact: .harness/harness/features/FEAT-48-parallel-safe-suite/notes/review-harness-security-reviewer-c8.md
```
