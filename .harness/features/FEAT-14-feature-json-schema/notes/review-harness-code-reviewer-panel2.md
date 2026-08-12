# Code review — FEAT-14, panel2

Reviewed `1bdfe3f..3abaedd` (review_sha pinned; `3abaedd..2dea9f9` is state/QA/review-routing
commentary only — checked, no source changes). Read files at the pin via `git show 3abaedd:<path>`
per G-01. Working tree is dirty only with two untracked notes files from other agents; nothing of
mine touches source.

## BLUF

**FAIL.** One high-severity fail-open in `check-domain.sh`'s write-time schema gate: the `except
ImportError:` at the `import feature_schema` call site does not catch `SyntaxError`, even though
the surrounding comment and the signed plan intent (T-06) both name "a syntax error in the module"
as a case that same `except` is supposed to deny. A syntax-broken `feature_schema.py` crashes the
whole hook uncaught → exit 1 → **non-blocking** (the file's own line 14) → the write proceeds
unchecked. This is check-domain.sh, a DEC-174 carve-out file: **the remedy is main-session's, not a
team fix cycle.**

Everything else asked for in the dispatch checks out clean: T-01's module-level jsonschema
requirement is honored in `feature_schema.py`; check-domain.sh's branch-deferral of `import
feature_schema` is a *different* statement than the one T-01 constrains, and is compliant; all
three routes (PRE Write, POST named-file, POST Bash-sweep) reach the schema check; the reported
path is always the real target, never a temp file; the "sixth vacuous check" hunt on INV-17/T-12,
`check-plan-routes.py`'s `_is_shipped`, and the CI corpus sweep found no new vacuity — all three are
sound, cited below.

## Q1 — does the enforcement path fail closed?

**T-01's module-level requirement — honored, correctly, in the right file.**
`feature_schema.py` (`git show 3abaedd:.claude/skills/harness/bin/feature_schema.py`) imports
`jsonschema` at true module level, in a `try`, setting `JSONSCHEMA_AVAILABLE`. Both
`problems_for_text` and `problems_for_file` check `if not JSONSCHEMA_AVAILABLE: return
[UNAVAILABLE_MESSAGE]` — never `[]`. This is exactly T-01's intent (plan.yaml lines 339-351, "Import
jsonschema at MODULE level inside a try... Do not import it inside a per-file function... Never
return `[]` on that path").

**check-domain.sh's branch-deferral — compliant, and it is a different claim than T-01's.**
check-domain.sh (`:892`) does `import feature_schema` **inside** `shape_problems()`, called once per
candidate file. This is a deferred import of the **module `feature_schema`**, not of `jsonschema`
itself — a different statement than the one T-01 constrains. T-06's own intent text (plan.yaml
1050-1053) states the property this preserves: "`sys.modules` caches the first import, so a POST
sweep over many candidates pays the 42.6ms ONCE per invocation, not once per file — which is the
exact property T-01's module-level jsonschema import was written to protect, and T-01 is
unchanged." Verified: `feature_schema`'s own `import jsonschema` only runs once per process
(module caching), so the once-per-file cost concern T-01 exists to prevent does not recur through
this second, lazy import. **Conflating these two imports would be a false finding; they are not the
same statement and the dispatch is right to flag that trap.**

**Reachable on all three routes.** `check-domain.sh` (`git show 3abaedd:...check-domain.sh:1120-1191`):
PRE (`Write` only), POST named-file (`Write`/`Edit`/`NotebookEdit`), and POST Bash-sweep all build a
`targets` list of `(rel, text, display)` tuples through different code paths, then feed a **single
shared loop** — `for _rel, _text, _disp in targets: _problems.extend(shape_problems(_rel, _text,
display=_disp))` — into `shape_problems()`, which contains the `RE_FEATURE_JSON` branch and the
schema-check import. All three routes reach it.

**Target path is always real.** `target = ti.get("file_path") or ti.get("notebook_path") or ""`
(`:463`) — the tool's own payload path, never reconstructed or copied to a temp location. `_show()`
(display path) and the Bash-sweep's glob results are both drawn from real on-disk paths. No
unattributable-finding regression (DEC-180) here.

### THE DEFECT — the except at check-domain.sh:894 is narrower than its own stated purpose

```
:892  import feature_schema
:894  except ImportError:
:895      _sp = ["feature_schema is not importable, so this file CANNOT be checked. ..."]
```

The comment immediately above (`:873-887`, "THE TIGHT try IS FOR feature_schema ITSELF being
unimportable — PYTHONPATH not exported, **a syntax error**, the file missing... It must APPEND to
problems, never raise: a raise escaping the per-file loop exits 1, and :14 says exit 1 is
NON-BLOCKING, so the bad write would land — fail open in the case the checker exists for") names
three cases the `except` must cover. Two of the three (missing PYTHONPATH entry, missing file) raise
`ModuleNotFoundError`, a subclass of `ImportError` — caught correctly. **The third, named
explicitly — "a syntax error" — is not.**

Verified empirically (no source edits; this is an in-memory repro using `importlib` machinery, not a
write to any tracked path):

```
$ python3 -c "
import sys, importlib.abc, importlib.util
BAD_SRC = 'def f(:\n    pass\n'
class MemLoader(importlib.abc.Loader):
    def create_module(self, spec): return None
    def exec_module(self, module):
        exec(compile(BAD_SRC, 'badmod3.py', 'exec'), module.__dict__)
class MemFinder(importlib.abc.MetaPathFinder):
    def find_spec(self, name, path, target=None):
        return importlib.util.spec_from_loader(name, MemLoader()) if name == 'badmod3' else None
sys.meta_path.insert(0, MemFinder())
try:
    import badmod3
except ImportError as e:
    print('CAUGHT as ImportError:', e)
except Exception as e:
    print('NOT caught as ImportError -- actual exception type:', type(e).__name__, '-', e)
"
NOT caught as ImportError -- actual exception type: SyntaxError - invalid syntax (badmod3.py, line 1)

$ python3 -c "print(issubclass(SyntaxError, ImportError))"
False

$ python3 -c "raise SyntaxError('simulated syntax error during import')"; echo "EXIT CODE: $?"
Traceback (most recent call last):
  ...
SyntaxError: simulated syntax error during import
EXIT CODE: 1
```

And confirmed no enclosing `try` exists anywhere between the `import feature_schema` call and the
script's exit (`awk 'NR>=892' check-domain.sh | grep -n '^try:\|^except'` → no output; the file's
only other `try/except` blocks are all earlier, at lines 218, 304, 338-346, 502, 530-532). So a
`SyntaxError` (or any exception that is not `ImportError`) raised at `:892` propagates uncaught to
the top of the script → Python's default uncaught-exception behavior → **exit 1** → per the file's
own line 14, "Only exit 2 blocks — exit 1 is a NON-blocking error and the write proceeds." **The
malformed feature.json lands, unvalidated, with no denial and no visible signal that enforcement was
skipped** (the agent may see a traceback in stderr, but nothing routes it to a block).

**This is not a hypothetical edge case invented by me — the plan's own T-06 intent text prescribes
this exact mechanism for this exact case and it does not achieve what it says it achieves.**
plan.yaml lines 1057-1063: "WHAT THE TIGHT try IS FOR IS A DIFFERENT FAILURE: feature_schema itself
being unimportable - PYTHONPATH not exported, a syntax error in the module, the file missing. On
`except ImportError` append a problem line naming feature_schema as unimportable... so that case is
DENIED with exit 2 as well." The code faithfully implements the plan's literal instruction
(`except ImportError`); **the instruction itself cannot achieve the stated requirement** for the
syntax-error branch, because `SyntaxError` is not an `ImportError` subclass. This is a defective
spec clause, not implementer drift (not P-06) — flagging it precisely, per Expertise P-15, so the
lesson routes correctly rather than becoming a re-litigated nit.

**In-file convention this deviates from.** Precisely, not overstated: `check-domain.sh` has one
other guarded import of exactly this shape — `:528-532`, `try: import harness_yaml; ... except
Exception: _no_parser = True` — which the surrounding comment (`:498-513`) explicitly narrates
fixing *the same bug class* once already: "that import raised and the process exited 1 INSTEAD of
printing 'enforcement OFF' and exiting 0... what was lost was DEC-101's deliberate, loud fail-open
becoming a silent crash." (Lines `:338` and `:502` are unguarded `import harness_yaml` calls with no
try at all, in contexts where a raise there is a different, already-fail-closed shape — I am not
claiming those as the convention, only `:530-532`.) The one place in this file that has already
learned "guard an import broadly or a crash silently disables the gate" uses `except Exception:`;
the new feature-schema import added by this feature reverts to the narrower, already-known-wrong
`except ImportError:`.

**The consequence is worse than "one write lands unchecked" on the interactive Bash-sweep route.**
In `check-domain.sh`'s no-named-file (Bash sweep) branch, the mtime high-water-mark stamp is
advanced *after* the glob walk that builds `targets` but *before* `shape_problems()` is called on
each target (`:1153-1163` writes/advances `STAMP`, then the shared `for _rel, _text, _disp in
targets:` loop at `:1184` calls `shape_problems`). If `shape_problems()` crashes mid-loop on a
syntax-broken `feature_schema.py`, the stamp has already advanced past every file in that sweep,
including the one that triggered the crash. **No future PostToolUse Bash sweep will re-examine that
specific file**, even after `feature_schema.py` is repaired — the file's own comment guards
precisely this permanent-miss shape for the unrelated `OSError`/`_unreadable` case (`"NOT ADVANCED
AT ALL IF ANY CANDIDATE COULD NOT BE READ"`) but has no equivalent guard for a crash inside
`shape_problems()` itself.

**This is bounded, not permanent, at the system level — say so precisely.** CI's independent
"Validate feature execution state" step (`.github/workflows/tests.yml`, `git show
3abaedd:.github/workflows/tests.yml`) runs `validate-feature-json.py` with no arguments — a full,
un-stamped sweep of every `feature.{json,yaml,yml}` on disk, on every push/PR — so the malformed
file is still caught at the next CI run, independent of the local hook's stamp. And in practice a
syntax-broken `feature_schema.py` would very likely fail CI's earlier "Unit suite" step outright
(any test importing the module), catching the *cause* before the *effect* reaches this branch. The
real exposure window is **local and interactive**: between an agent introducing a syntax error into
`feature_schema.py` and that agent running tests or pushing, any concurrent write to a `feature.json`
(by that agent or another, especially via Bash — bulk migrations, scripted edits) is silently
unchecked at write time, and if it lands through the Bash-sweep route specifically, that occurrence
is never re-examined by the interactive hook again.

**One more trigger surface, not just "someone edits feature_schema.py":** the same narrow `except
ImportError:` also guards against a non-`ImportError` raised *from inside* `import jsonschema`
itself (a half-upgraded or corrupted install raising some other exception at import time) —
propagates through the identical path, same fail-open, same fix.

**Remedy and routing.** `check-domain.sh` is a DEC-174 carve-out file (T-06 is
`execution_mode: main-session-direct`) — **this finding routes to the main session, not a team fix
cycle.** The fix is mechanical: widen `:894`'s `except ImportError:` to `except Exception:` (matching
`:530-532`'s existing convention in the same file), or explicitly `except (ImportError,
SyntaxError):`.

**Established finding, not re-reported, and how mine differs.** qa's `runs/qa-final2-validator`
already FAILED on SC-04/SC-05/SC-16 having no automated assertion — that finding is about missing
*test coverage* for schema-rejection generally, including the "jsonschema unimportable" case (SC-16,
which is the `except ImportError` **inside** `feature_schema.py` catching jsonschema's own absence —
already correct, verified above). Mine is narrower and is a live *correctness bug*, not a coverage
gap: even a fully-implemented SC-16 fixture (inject a fake `jsonschema.py` that raises `ImportError`)
would not exercise this path, because that scenario is caught correctly one level down. This defect
sits specifically at check-domain.sh's own `import feature_schema` statement and needs its own
fixture (a syntax-broken `feature_schema.py` on `PYTHONPATH`) to discriminate — `grep -n
"feature_schema\|SyntaxError" test-check-domain.py` confirms no such fixture exists today.

## Q2 — the sixth vacuous check (not found beyond Q1; three surfaces probed, all sound)

- **T-12 / INV-17 rebuild** (`check-state.sh`, `git show 3abaedd:...check-state.sh:433-593`): sound.
  `STATUS_ORDER`/`SEAM_NOTES` replace `PHASE_ORDER` exactly per D-12 (lowercase stem literals, not
  derived from status values — the case-insensitive-filesystem trap D-12 names is avoided).
  `_handoff_exempt()` fails closed on every read/parse error (`except Exception as e: return "",
  f" (its plan.yaml does not parse...)"` — returns *not exempt*, never silently exempt). **Not just
  reachable — discriminating**: `test-check-state.py` `case_g` (`:264`) is titled "INV-17 RAISES on
  Review with handoff-build.md absent, and names it" and its comment (`:259-264`) is explicit about
  M-01, a prior regression where this exact assertion crashed instead of firing — this is a positive
  test that a violation is actually raised, not merely that the script exits clean, satisfying
  Expertise P-12's reachable-vs-discriminating distinction.
- **`check-plan-routes.py`'s `_is_shipped`** (`:394-433`): sound and fail-checked by construction —
  unreadable/absent `feature.json`, any exception, or a non-dict document all `return False` (not
  finished → still checked, the safe direction). `D-11`'s case-sensitivity is honored
  (`token[0] in FINISHED_STATUSES`, no lowercasing).
  I did not independently re-verify a discriminating test exists for this predicate beyond reading
  the source; noting as a gap in my own coverage, not as a finding — the logic itself is
  unambiguous and fail-checked on its face.
- **CI `Unit suite` / corpus-sweep reachability**: sound. `tests.yml`'s "Validate feature execution
  state" step runs `validate-feature-json.py` with no args (an un-stamped, full-corpus sweep) on
  every push/PR, and is a plain `run:` step whose non-zero exit (0 clean / 1 file-failed / 3
  checker-could-not-run, all non-zero except clean) fails the step under GitHub Actions' default
  `bash -e` behavior — no swallowed exit code, no `|| true` around it.

## Sanctioned exclusions honored

Did not flag any `feature.yaml` string at `docs/harness/BUILD.md:335/353/357`,
`check-plan-routes.py:405`, dated comments in `check-domain.sh`/`test-check-domain.py`, or
`DECISIONS.md`'s 52 occurrences — all covered by R-01's tense split.

## Stage 1 — spec compliance

Every file touched in `1bdfe3f..3abaedd` traces to a task in `plan.yaml` (T-01 through T-13) and its
`REQ`/`D` citations; I found no scope creep and no omission beyond the already-established
SC-04/SC-05/SC-16 gate failure. The eleven-key schema (`feature-schema.json`, verified at the pin)
matches D-01/D-02 exactly: eight required keys named, three optional, `additionalProperties: false`
at top level and inside `runs` items/`github`/`factory`, no `phase` key, no `notes` key anywhere.
D-09/D-10/D-11's six board-column values and case sensitivity are present verbatim in the schema
enum. I did not do a line-by-line diff of all 17 migrated `feature.json`/receipt pairs (D-06/D-07)
given the review budget — flagging as a boundary of this review, not a finding.

## Ranked findings

1. **[high]** `check-domain.sh:894` — `except ImportError:` does not catch `SyntaxError` (or any
   non-`ImportError` exception) from `import feature_schema`, contradicting the same comment's and
   T-06's own stated intent that this exact `except` must deny a syntax-broken module with exit 2.
   Uncaught → exit 1 → non-blocking (`check-domain.sh:14`) → the write proceeds unchecked. On the
   Bash-sweep route the mtime stamp has already advanced past the triggering file when the crash
   happens, so that specific occurrence is never re-examined by a future interactive sweep (bounded
   by CI's independent full-corpus sweep at the next push, not permanent system-wide). **Routes to
   the main session** — `check-domain.sh` is a DEC-174 carve-out file. Remedy: widen the `except` to
   `Exception` (matching this same file's own `:530-532` convention) or `(ImportError, SyntaxError)`.
2. **[info]** No independent verification of a discriminating test for `check-plan-routes.py`'s
   `_is_shipped`, beyond reading the source (which is unambiguous and fail-checked). Not a finding —
   noted as a review-coverage boundary.

## Findings explicitly not re-raised

- SC-04/SC-05/SC-16 lack of automated assertion — already FAILED at `runs/qa-final2-validator`,
  main session's to resolve under the DEC-174 carve-out. Confirmed still true at the pin
  (`test-check-domain.py` has zero fixtures mentioning `feature_schema`/`SyntaxError`) and my
  finding #1 above is narrower than and independent of that gap.
