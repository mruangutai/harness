# SIMPLIFY — ALTITUDE angle — BUG-124, cycle 4

BLUF: one altitude finding. The rest of the diff is well-placed — the four helpers sit in
`harness_boundary.py` (the shared library check-domain.sh/bash-write-guard.sh/dispatch-guard.sh
already use for exactly this kind of grant-matching primitive), the message assembly stays
single-sourced in `dispatch-guard.sh`, and none of the four is a special case bolted onto shared
infrastructure for a single caller.

## Findings

1. **file:** `.claude/skills/harness/bin/harness_boundary.py`
   **line:** 833–844 (the `walk()` closure inside `run_dir_grant_globs`)
   **summary:** `run_dir_grant_globs` re-implements a second, independent tree-walk over
   `team-config.yaml`'s grant shape (`dict`/`list` recursion collecting any list of mappings
   carrying a `path` key) rather than building on `harness_yaml.manifest_domains`
   (`.claude/skills/harness/bin/harness_yaml.py:392-416`), the existing generic walker over the
   same shape. The two walkers encode **different** filtering rules for "is this a write grant":
   `manifest_domains` excludes read-only entries (`not entry.get("read")`,
   `harness_yaml.py:408`); `run_dir_grant_globs`'s `walk()` has no such check — it accepts any
   `{path: ..., ...}` mapping regardless of a `read: true` sibling key.
   **cost:** this is exactly the drift the ALTITUDE angle asks about: two authoritative
   statements of "what counts as a write grant" that can silently diverge. Today's manifest has
   no `read: true` entry under a `/runs/` path, so it isn't live-triggered, but the moment a lead
   is given a read-only `.../runs/*-x/**` grant (the `read: true` pattern is already used 12+
   times elsewhere in `team-config.yaml` for other paths, so it's a normal, expected shape, not a
   hypothetical one), `run_dir_grant_globs` would include that squad's pattern in the write
   vocabulary, `run_dir_slug_ok` would accept a slug that squad cannot actually write, and
   dispatch-guard.sh would pass the dispatch through — a fail-open on the exact guard this task
   built to close the equivalent fail-open at write time.
   **alternative:** extract the shared shape (a predicate-parameterized walk over "list of
   mappings carrying `path`") into one generic primitive in `harness_yaml.py`, have
   `manifest_domains` call it with `name == agent and not read` and `run_dir_grant_globs` call it
   with `"/runs/" in path and not read`, so both callers read grant-shape rules from one place.
   **recommendation:** `briefing-row`. The read-filter gap traces to the plan's own T-01 intent
   (`plan.yaml:261-263`: "any mapping value that is a list of mappings carrying a path key is a
   grant list", no `read` exclusion specified), already reviewed at the plan panel. A fix here
   would change the walk's accepted-grant semantics, which is a plan-level design question, not
   mine to fold in during a read-only pass — it belongs back to the plan/next task, not this
   apply step.

No other altitude finding. The bash-side derivation preamble in `dispatch-guard.sh` (lines
27–61) exists solely because `python3 -I` excludes user site-packages (D-03, documented at the
call site) — that split is a real, load-bearing home decision, not misplaced logic, and the
second manifest parse it performs is separately settled (F-4, not an efficiency finding). The
refusal message (dispatch-guard.sh:148-186) is assembled once, in the guard, from
`run_dir_forms`/`run_dir_slug_ok`/`run_dir_refs` — no second copy of the wording or the rule
exists elsewhere.
