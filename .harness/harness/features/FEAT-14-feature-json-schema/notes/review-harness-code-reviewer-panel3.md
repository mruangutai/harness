# Code-panel review — FEAT-14 feature.json schema (panel3)

Reviewed `1bdfe3f..cf15660` (review_sha pinned `3abaedd`; commits above the pin —
`8adac30..cf15660` — are qa/state-only, no source touched, confirmed by `git diff --stat`). No
`[harness:human]` commits in range. `git diff --stat 1bdfe3f..HEAD`: 110 files, +7154/-2545.

**Dispatch path note**: the dispatch named `notes/review-code-panel.md`; `check-domain.sh`
denies that filename for `harness-code-reviewer` (permitted pattern is
`notes/review-harness-code-reviewer-*.md`). Writing here instead — the guard is ground truth,
not the dispatch text (harness-handoff #216).

## VERDICT: FAIL

`severity_max: high`, `must_fix` non-empty. One HIGH, independently re-verified live at HEAD
(not inherited from a stale note), routes to the main session under DEC-174.

## Headline finding — check-domain.sh:894's `except ImportError:` does not fail closed

**[HIGH, hybrid: FALSIFICATION-BACKED for the Python semantics, READ-ONLY for end-to-end hook
behavior.]**

`check-domain.sh:890-894`:
```python
try:
    import feature_schema
    _sp = feature_schema.problems_for_text(content, display or rel)
except ImportError:
    _sp = ["feature_schema is not importable, so this file CANNOT be checked. ..."]
```
The comment immediately above (`:872-887`) states this `try` covers three cases: "PYTHONPATH
not exported, a syntax error, the file missing" and that on catch it "must APPEND to problems,
never raise: a raise escaping the per-file loop exits 1 ... fail open in the case the checker
exists for." Two of the three (missing PYTHONPATH entry, missing file) raise
`ModuleNotFoundError`, an `ImportError` subclass — caught. **The third, named explicitly — "a
syntax error" — is not**, because `SyntaxError` does not subclass `ImportError`.

Independently reproduced at HEAD, no file writes (a `python3 -c` inline check is not a detected
write pattern — the guard let it through):
```
$ python3 -c "print('SyntaxError subclass of ImportError:', issubclass(SyntaxError, ImportError))"
SyntaxError subclass of ImportError: False
```
and, reproducing the actual import-time failure shape with an in-memory `importlib` finder (no
tracked file touched):
```
NOT caught by except ImportError -- actual type: SyntaxError
```
Confirmed no broader enclosing `try` exists between `:888` and end of file other than the one
at `:891/894` (`awk`+`grep` over the whole tail of the script — the file's other seven
`try`/`except` pairs are all for unrelated later code, lines 963+, 1103+, 1120+, 1136+, 1167+).
So a `SyntaxError` (or any non-`ImportError` — including a half-upgraded `jsonschema` install
raising something else at `import jsonschema` time, one level down) propagates uncaught out of
`shape_problems()` to the top of the script → Python's default uncaught-exception exit → **exit
1** → per this same file's own line 14 ("Only exit 2 blocks — exit 1 is a NON-blocking error and
the write proceeds"): **the malformed feature.json lands, unvalidated, with no denial.**

**Aggravating factor on the Bash-sweep route, confirmed by reading (not independently
falsified — see limits below).** The mtime high-water-mark stamp is advanced at `:1166-1174`,
*before* the shared `for _rel, _text, _disp in targets: _problems.extend(shape_problems(...))`
loop at `:1183-1184` that would crash. If `shape_problems()` raises mid-loop, the stamp has
already moved past every file in that walk, including the one that triggered the crash — no
future interactive Bash sweep re-examines that specific occurrence. Bounded, not permanent: CI's
new "Validate feature execution state" step (`validate-feature-json.py`, no args, un-stamped
full-corpus sweep, `.github/workflows/tests.yml`) still catches it at the next push.

**This does not contradict the dispatch's "the write-time schema gate is correct at HEAD"
premise — it is a different probe.** That premise's own stated evidence is a live
invented-key-payload probe (→ exit 2), which I also reproduced (see Assignment 2 below) and
which is true. My finding is a different trigger — the checker's own module failing to import —
that probe never exercised. Both are true; they are not in tension.

**Provenance.** First reported in this feature's own `notes/review-harness-code-reviewer-panel2.md`
at the same pin (`3abaedd`), which this feature never fixed — `git diff 3abaedd..HEAD --
.claude/skills/harness/bin/check-domain.sh` is **empty**, confirming the file is byte-identical
to the version panel2 reviewed. I re-verified the core claim myself rather than forwarding it
unread. It is distinct from `STATE.md`'s open question Q9 ("the guarded-import needle misses
`except (ImportError, ...)` and `except ModuleNotFoundError`") — I checked Q9's origin
(`notes/receipt-harness-backend-dev-E1-c1.md`) and it is about a *different* mechanism: a
hygiene meta-test in `test-harness-yaml.py`, `test_exactly_one_guarded_import_in_the_tree`, that
greps the tree for the literal substring `"except ImportError"` to bound where the guarded-import
pattern is allowed to live. That test's needle would miss a *rewritten* guard spelled
`except (ImportError, ModuleNotFoundError):` — a hygiene-check fragility, not a claim about
whether `:894`'s actual clause is broad enough at runtime. Do not conflate the two; I checked
before conflating them.

Not ruled on anywhere I can find: `plan.yaml`'s `approval.rulings` has only R-01 and R-02,
neither touches this. `STATE.md`'s open questions are the orchestrator's characterization
("non-blocking" appears elsewhere in that file for other items, not for this one, and in any
case an open question is not an operator ruling).

**Remedy and routing.** `check-domain.sh` is a DEC-174 carve-out file — **this routes to the
main session, not a team fix cycle.** Mechanical fix: widen `:894` to `except Exception:`
(matching this same file's own convention at `:530-532`, which the surrounding comment there
narrates fixing the identical bug class once already for the `harness_yaml` import) or
`except (ImportError, SyntaxError):`.

**Limits of my own verification, disclosed.** I did not run the real hook end-to-end against an
actual broken `feature_schema.py` on `PYTHONPATH` — doing so needs a fixture file, and
`bash-write-guard.sh` denies every detected write pattern from `harness-code-reviewer`
unconditionally (see Probe hygiene, below). My reproduction is the same standard panel2 used:
independent confirmation of the Python semantics plus static confirmation of the code shape, not
a live run of the full hook under fault injection.

## Assignment 2 — the enforcement path (check-domain.sh :866-922), the other two questions

**Reachable on every route?** READ-ONLY for the non-crash path (Write/PRE, POST-Edit,
POST-Bash-sweep all funnel through the same single loop and single `if _problems: exit(2)` at
`:1183-1189` — one function, one accumulator, one exit, so nothing route-specific could diverge).
FALSIFICATION-BACKED for Write/PRE specifically, in the disposable worktree
(`/private/tmp/.../scratchpad/feat14-probe`, clean `git status --porcelain` before and after):
- Valid 8-required-key payload (agent `harness-orchestrator`, in-domain for
  `.harness/features/**`) → **exit 0**.
- Same payload + `invented_key` → **exit 2**, stderr: `undeclared key 'invented_key' at /`,
  naming the real path `.harness/features/FEAT-XX-probe/feature.json` (not a temp file).
- Same valid payload with `PYTHONNOUSERSITE=1` (hides both `jsonschema` and `PyYAML` — both are
  only installed at user-site on this machine, confirmed via `python3 -c "import
  X; print(X.__file__)"`) → **exit 2**, stderr: `jsonschema is REQUIRED and is not importable,
  so this file CANNOT be checked.` — not swallowed by the concurrent PyYAML bootstrap-grant
  message that also prints in this compound scenario.
- `validate-feature-json.py` (the standalone CLI), isolating jsonschema-only unavailability
  (this script has no PyYAML dependency) → exit 0 on a valid file normally, **exit exactly 3**
  with `PYTHONNOUSERSITE=1`, message names `pip install jsonschema` (SC-07).

**Message names the real path, never a temp file?** Confirmed for all three routes by reading
(`target = ti.get("file_path") or ti.get("notebook_path")` for Write/Edit/NotebookEdit; real
glob results for the Bash sweep) and confirmed live for Write/PRE above.

## Assignment 1 — vacuous-check hunt (beyond the headline finding)

**`factory_decompose.py:write_factory` can silently write a schema-invalid `feature.json`.**
[MED, READ-ONLY — reasoned from source and the test suite's own fixture default; not executed,
see Probe hygiene.]

`write_factory` (`:142-181`) does read-modify-write: `if os.path.exists(path): doc =
json.load(f) ... else: doc = {}`, then sets `doc["factory"]`, then writes the whole `doc` back.
No schema check anywhere in this function or its six call sites in `main()`
(`:356,376,388,413,435,467`), and no earlier guard requires `feature.json` to already carry the
8 required keys — `load_factory` (`:95-98`) itself returns an empty ledger when the file is
absent, never refuses. If `feature.json` is missing or already partial when this runs, the
result is `{"factory": {...}}` alone, which fails SC-01's `required` check outright. This is a
**new** failure mode this feature introduced: the pre-migration splice had the identical
"start from empty" shape and was harmless because `feature.yaml` carried no closed schema; the
migration to a closed 8-required-key schema turned a previously-inert path into a schema
violator, and no task in this feature's plan added a guard.

`test-factory-decompose.py`'s `make_feature()` defaults `feature_json_extra="{}"` — an empty
document — and roughly 20 of its ~24 cases use that default, so the code path that produces an
invalid document is exercised routinely. It is never caught: no case calls
`feature_schema.problems_for_text`/`problems_for_file` on `write_factory`'s own output (grepped
`test-factory-decompose.py`, `test-factory-claim.py`, `test-gh-sync.py` — zero hits in all
three). The one case that would catch it (case 9, "an eleven-key feature.json ... round-trips")
deliberately starts from a full eleven-key document, proving round-trip fidelity, not
schema-validity of the empty-start path. `gh-sync.py`'s sibling `save_recorded` is safer here —
it calls `harness_yaml.load_file(p)` unconditionally, no `doc={}` fallback, so a missing file
raises rather than silently writing a partial document; the two "write back into feature.json"
tools have diverged on the fail-open/fail-closed axis.

Mitigated, not absent: a governed agent running `factory_decompose.py` via Bash triggers
`check-domain.sh`'s POST sweep on its next Bash call (fresh mtime), reporting the corruption
after the fact; CI's `validate-feature-json.py` (no args) is a second backstop. Kept at MED
rather than HIGH because of these two backstops and because I could not confirm from the diff
whether factory_decompose ever actually runs before a feature's `feature.json` exists in
practice.

What would prove it: a `test-factory-decompose.py` case starting from `feature_json_extra=None`
(file absent) or the current `"{}"` default, running `publish`, then asserting
`feature_schema.problems_for_file(<result>) == []` — it will not be, today.

**Minor — SC-17's literal claim doesn't hold literally.** [INFO, READ-ONLY.] SC-17 (BRIEF:459)
says "the literals `shipped` and `abandoned` appear nowhere in the file"
(`check-plan-routes.py`). Grepped at HEAD: `shipped` appears 7 times, `abandoned` 2 times, all
in prose/comments/the function name `_is_shipped`, none as a compared status value. The
functional claim (no such value is legal input to the finished-status check;
`FINISHED_STATUSES = ("Done",)`, tested case-by-case in `test-check-plan-routes.py` case 24) is
true and well tested; the literal-text claim has no automated assertion behind it (grepped for
a source-sweep test, found none). Not a functional defect — flagging as imprecise BRIEF wording
riding inside a `verify: automated` tag.

## Confirmations run (evidence, not findings)

- `test-validate-feature-json.py` (34 cases), `run-unit-tests.sh --kind unit`, `--kind
  integration`: all green at HEAD, run directly.
- `gen-decisions-index.py --stdout` vs `docs/harness/DECISIONS-INDEX.md`: byte-for-byte match
  (`diff <(...) ...`, no file write) — SC-14's base assertion holds even though qa separately
  proved the check itself is blind to a prose-only mutant.
- `validate-feature-json.py` (no args) over the live corpus: 17 files, exit 0.
- `templates/feature.json` validates clean (SC-12); both instruction sites (`check-state.sh`
  INV-18, `harness/SKILL.md:23`) name it by filename.
- SC-13 repo sweep: every surviving `feature.yaml` string outside `.harness/features/**`
  matches exactly the R-01 carve-out list (BUILD.md:335/353/357, check-plan-routes.py:405,
  check-domain.sh + test-check-domain.py comments, DECISIONS*.md prose, test-harness-yaml-corpus.py's
  three dated citations). No unsanctioned reference found.
- DEC-190/191/192 present in `docs/harness/DECISIONS.md` (the three decisions SC-14 requires).

## Not re-raised

SC-04/SC-05/SC-16 lacking automated schema-rejection fixtures in `test-check-domain.py` — already
FAILED by qa (HIGH), remedy in a DEC-174 carve-out file, main session's. I independently
falsified that the underlying mechanism is correct for the "invented key" and "jsonschema
unavailable" triggers (narrows the eventual fix to "add tests"), but found a *third*, uncovered
trigger (broken `feature_schema.py` itself) where the mechanism is **not** correct — that is my
headline finding above, not a restatement of qa's.

## Probe hygiene

All probes ran in the pre-existing disposable worktree
(`/private/tmp/claude-501/-Users-molchairuangutai-GitHub-harness/cd83b531-.../scratchpad/feat14-probe`,
already clean at HEAD, left clean — `git status --porcelain` empty before and after). No edits
to any DEC-174 carve-out file — `check-domain.sh`, `check-state.sh`, `check-plan-routes.py` and
their test files were READ and RUN only.

`bash-write-guard.sh` denies every detected write pattern from `harness-code-reviewer`
unconditionally (no path analysis, by design), and the Write tool is domain-restricted to two
paths. This blocked fabricating POST-route (Edit-lands-on-disk, Bash-sweep) fixtures and a
shadow-`jsonschema.py`/broken-`feature_schema.py` PYTHONPATH fixture (the technique
`test-check-domain.py` uses for PyYAML, and what would be needed to run the headline finding
end-to-end through the real hook). I used `PYTHONNOUSERSITE=1` (an env var, not a write) for a
real jsonschema-unavailable probe on the PRE/Write route and the standalone CLI, and `python3
-c` inline snippets (not a detected write pattern) for the SyntaxError-semantics reproduction. A
`tempfile`-based Python-heredoc workaround would have evaded the guard's shell-level pattern
match but not its evident intent, and I did not use it.

**Disclosure — a gitignored marker was left in the probe worktree.** The
`PYTHONNOUSERSITE=1` compound run (jsonschema + PyYAML both hidden) printed "PyYAML is not
importable... allowing this session once," which writes
`.harness/.pyyaml-bootstrap` as a side effect of the hook itself (not of anything I did
directly). Confirmed present: `ls -la .../feat14-probe/.harness/.pyyaml-bootstrap` → exists, 36
bytes, and it is listed in the worktree's own `.gitignore`, so `git status --porcelain` correctly
shows nothing — the worktree is git-clean but not byte-identical to its pre-probe filesystem
state on this one gitignored path. I could not remove it (`rm` is a denied write pattern for
this role). Disclosing rather than silently leaving "restored byte-identically" to imply
otherwise.

## Open questions

- { id: Q1, question: "Should reviewer agents get a scoped, disposable write allowance for
  POST-route enforcement fixtures (e.g. a notes/probes/ domain in a worktree only), so the
  headline finding above can be upgraded from static+semantic reproduction to a full live run
  of check-domain.sh against a broken feature_schema.py?", blocking: false }
