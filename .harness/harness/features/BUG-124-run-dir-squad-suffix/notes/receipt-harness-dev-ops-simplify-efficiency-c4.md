# SIMPLIFY — EFFICIENCY angle — BUG-124-run-dir-squad-suffix (cycle 4)

**BLUF:** One real, measured, minor finding — the new run-dir vocabulary derivation
spawns a full extra `python3` process (import `harness_boundary`+`harness_yaml`, open
and YAML-parse `team-config.yaml`) unconditionally on **every** governed dispatch,
even when the dispatch prompt contains no run-dir reference at all (the common case —
see `case_20_no_run_dir_reference_untouched`). A ~0.5ms bash regex pre-filter on the
raw payload would skip it on that path for effectively free. Everything else in scope
is genuinely cheap or already settled.

## What I measured

Worktree: `/Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-124-run-dir-squad-suffix`, HEAD `dac8f099`, clean before/after.

1. **Bare `python3 -c 'pass'` startup** (10x loop): 637ms wall / 10 → **~34ms/proc**
   (this is the floor any additional interpreter pays regardless of content).
2. **The new derivation subprocess in isolation** (`dispatch-guard.sh:37-54`'s heredoc
   body, run 10x with the real `harness_boundary.py`/`harness_yaml.py`/live
   `team-config.yaml`): 637ms wall / 10 → **~64ms/proc** (measured directly; not the
   same 637ms figure by coincidence — reran to confirm, both loops landed at 63-64ms
   avg independently).
3. **The full `dispatch-guard.sh` end-to-end**, real payload (`harness-eng-lead` →
   `harness-backend-dev`, `HARNESS-FEATURE:` first line, no run-dir reference in the
   prompt, single-flight claim path exercised): 3 runs, **104-111ms wall** each.
4. **A bash regex pre-filter** over the raw JSON payload for the same pattern
   `hb.run_dir_refs` matches (`\.harness/[^/\s]+/features/[^/\s]+/runs/[A-Za-z0-9._-]+`),
   20x loop: 11ms wall / 20 → **~0.5ms/call**. JSON string-escaping never touches `/`,
   so grepping the raw payload before parsing JSON is a faithful pre-filter for "could
   `run_dir_refs(prompt)` possibly match."

`(3) - (2) ≈ 41-47ms` for the pre-existing pipeline (single-flight claim, `python3 -I`,
registry I/O) — consistent with the `python3 -I` baseline separately measured at ~34ms
plus registry work. So the new block roughly **1.5-2x's the guard's total wall time**
on every governed dispatch, dominated entirely by the unconditional subprocess spawn +
import + parse, not by the regex matching or the tree walk (both sub-millisecond).

## The finding

- **file:** `.claude/skills/harness/bin/dispatch-guard.sh`
- **line:** 37 (the `if _globs=$(python3 -c '...' <<'PY'` block, running through line 59)
- **summary:** the run-dir vocabulary derivation subprocess runs unconditionally, before
  the guard has any idea whether the dispatch prompt references a run-dir path at all.
- **cost (measured):** ~64ms of the guard's ~105ms total is this one subprocess
  (import + YAML parse), paid on every governed dispatch across the whole factory —
  including the ordinary case where the prompt names no `.harness/.../runs/...` path
  and the derived globs are never consulted (`dispatch-guard.sh:158`'s
  `if refs and not globs` / `elif refs and globs` — both branches are skipped when
  `refs` is empty, so the derived globs are computed and then discarded).
- **alternative:** gate the `python3 -c` block behind a cheap pre-filter on the raw
  `$payload` before spawning it, e.g.
  `printf '%s' "$payload" | grep -Eq '\.harness/[^/[:space:]]+/features/[^/[:space:]]+/runs/[A-Za-z0-9._-]+' || _derived=0 _globs=''` —
  skip straight to the existing "no reference" fall-through when it doesn't match.
  Measured at ~0.5ms vs. ~64ms for the subprocess it would usually replace.

Not applying this myself (read-only angle). Scope/risk note for whoever routes it: this
touches only the bash gating, not `harness_boundary.py`'s helpers or the test-covered
`run_dir_refs`/`run_dir_slug_ok`/`run_dir_forms` API, so the blast radius is small — but
it is a change to a file every one of the 15 already-passing dispatch-guard integration
cases exercises, so re-running that suite after any apply is warranted, not optional.

## Explicitly excluded (per dispatch), not re-litigated

- The **second** `team-config.yaml` parse inside this same subprocess (`load_str` at
  line 50, then `run_dir_grant_globs`'s own `load_file` at line 848) — operator-accepted
  at signature (Q4), load-bearing for distinguishing guard case 23 from case 21. Not an
  efficiency finding.
- The lazy `import harness_yaml` inside `harness_boundary.py`'s pre-existing
  `try/except Exception: return []` — deliberate, load-bearing for synthetic-fixture
  isolation.
- Deliberate full-suite runs at boundary steps — not evaluated, not applicable here (I
  ran no suites).

## Everything else checked and found negligible

- `harness_boundary.py`'s `run_dir_grant_globs` tree `walk()`: recursive descent over
  the parsed `team-config.yaml` document, single-digit KB, sub-millisecond — not
  separately timed beyond (2) above, which already includes it.
- `run_dir_refs`/`run_dir_slug_ok`/`run_dir_forms`: pure regex/string work over a
  single prompt string and a short glob list, called once each per dispatch inside the
  already-paid-for `python3 -I` process (measurement 3) — no additional process, no
  additional I/O. Negligible.
