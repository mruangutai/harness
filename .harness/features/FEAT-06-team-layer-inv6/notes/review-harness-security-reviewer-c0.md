# Security review — FEAT-06-team-layer-inv6 — c0

**Diff:** `635ef14..9f87c48` (review_sha pinned; confirmed `git rev-parse HEAD` = `9f87c48dae0ced97e7655dffb9daddeba4708324` before diffing, per instructions)

## Verdict: PASS — real security-adjacent surface reviewed, no findings

This diff does have surface worth a real look (it modifies the data-trust
boundary check in `check-state.sh`, the YAML loader constant, and the corpus
scanner's root set), so `in_scope: true`. Having reviewed those surfaces and
found nothing exploitable, the correct severity is `info` (reviewed, clean) —
not `n/a` (nothing here to judge at all). `n/a` is reserved for a diff with no
surface for this role, e.g. a pure-UI change; that is not this diff.

## Scope reasoning

This diff is INV-6 hardening (`review_sha: none` no longer reads as a pinned
SHA), a new `build.yaml` team-expansion file, a `qa` step added to
`review.yaml`, `gate-probe.yaml` deleted, new/expanded test files, and prose
(SKILL.md, SPEC.md, DECISIONS.md, BRIEF/PLAN/observations, daily log). No
network I/O, no auth surface, no new dependency, no credentials. Everything
reads or compares repo-local YAML/Markdown that the harness's own agents
authored in a prior, equally-trusted step — per Expertise P-01/P-02, that is
not an untrusted-input boundary and controlling a value one already has
access to is not an escalation. That reasoning is why severity lands at
`info` rather than higher, not why the review is out of scope.

I checked the four areas the dispatch specifically named:

1. **`check-state.sh:156`** — the new `_sha = (val("review_sha") or "").strip().lower()`
   and `_sha in harness_yaml.PLACEHOLDER_UNSET` are pure Python string comparisons.
   `val()` stringifies a YAML scalar; nothing from `feature.yaml` is interpolated
   into the heredoc as *code* — it flows in only as data compared against string
   literals. Same for `INV-6/7/8` above and below in the file (`val("cycles_used")`,
   `runs` fields) — every use is `.strip()`/`.lower()`/`==`/`.isdigit()` on a typed
   `str()`, never `eval`, `exec`, `format`-into-shell, or f-string built into a
   subprocess argv. Confirmed with `git diff ... | grep -E "eval\(|exec\(|os\.system|subprocess|shell=True"` → no hits anywhere in the diff.

2. **`harness_yaml.py`** — only addition is the `PLACEHOLDER_UNSET = ("none", "null", "n/a")`
   tuple, a plain constant. `load_file` still routes through the existing
   `_StrictSafeLoader(yaml.SafeLoader)` (unchanged in this diff, confirmed by
   `grep -n safe_load` showing the same subclass at line 102 pre- and post-diff).
   No `yaml.load`/`unsafe_load`/`FullLoader` introduced. `validate-digest.py`'s new
   `import harness_yaml` reuses the same constant rather than duplicating it — a
   correctness fix (single source of truth, per the file's own comment), not a
   security change.

3. **`test-harness-yaml-corpus.py`** — the widened scan replaces `glob(**)` (which
   silently skips dotted directories, a real pre-existing correctness gap the diff
   fixes) with `os.walk`, but the walk roots are the two hardcoded constants
   `ROOTS = [".harness", ".claude/skills/harness/teams"]` joined under
   `REPO = os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()` — no user-controlled
   path, no symlink-following concern beyond what `os.walk` does by default (it does
   not follow directory symlinks unless `followlinks=True`, which is not set here).
   The new fixture helper `_fixture_teams()` writes into `tempfile.mkdtemp()`, a
   throwaway directory outside the repo tree — it does not touch
   `.claude/skills/harness/teams/` (the file's own docstring calls this out
   explicitly: mutating the guarded tree to test the guard would be the guard
   testing itself with itself disabled).

4. **`test-team-catalog.py`** (new) — read-only throughout: `harness_yaml.load_file`,
   plain `open(...).read()`, `os.listdir(BIN)`. No writes, no subprocess, no network.
   Reads only fixed repo-relative paths built from `REPO`/`TEAMS`/`BIN`/`SKILL_MD`/`SPEC_MD`.

## Team YAML content (`build.yaml`, `review.yaml`)

`build.yaml` (new) and the added `qa` step in `review.yaml` are prompt/config text
consumed by an LLM orchestrator elsewhere in the harness (not present in this
diff) — not executed as shell or Python. Templated tokens (`{{feat}}`, `{{task_id}}`,
`{{cycle}}`, `{{persona}}`) feed into output *paths*, and the diff's own comments
(`build.yaml` lines documenting the `harness-` prefix requirement) note that
`check-domain.sh` — unmodified by this diff, out of scope per DEC-174 and per this
dispatch's own "settled ground" — already blocks an unmatched write path at exit 2.
`gate-probe.yaml`'s deletion removes a probe team, not a control; its rulings are
explicitly preserved in `DECISIONS.md` per this diff.

## Data exposure / secrets sweep (the dispatch's fourth scope item)

Ran the credential regex unfiltered over the whole diff (not path-filtered to
`*.md`/`*.yaml`), plus a check for embedded absolute home paths and email
addresses, since the diff also adds `.txt`, `.py`, `.sh`:

```
git diff 635ef14..9f87c48 | grep -inE "api[_-]?key|secret|password|BEGIN (RSA|OPENSSH|PGP)|Authorization: Bearer|AKIA[0-9A-Z]{16}|ghp_...|sk-..."
git diff 635ef14..9f87c48 | grep -inE "/Users/[a-zA-Z0-9_.-]+|[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"
```

Both return zero hits. Specifically read `notes/before-check-state-635ef14.txt`
(30 lines, a captured test-run receipt) and `.harness/logs/2026-08-04.md`'s new
entries (operational narrative about the FEAT-06 plan/build cycle) — both are
clean: run ids, cost figures, file:line anchors, no credentials, no PII, no
absolute developer-machine paths.

## No findings

No injection, auth, secrets, input-validation, or data-exposure issue found. No
speculative findings recorded — an empty result is the correct call here, not a
missed audit (dispatch's own instruction: "a manufactured finding is the defect
in review form").

```yaml
VERDICT: PASS
DIGEST:
  headline: "FEAT-06 diff (635ef14..9f87c48) touches real security-adjacent surface (INV-6 pin check, YAML-loader constant, corpus scanner roots) — reviewed all four dispatch-named areas plus a full-diff secret/PII sweep, found nothing exploitable."
  in_scope: true
  scope_reason: "Dispatch named four plausible surfaces (check-state.sh Python-in-shell, harness_yaml loader, widened yaml-corpus scan, new test-team-catalog.py); all four checked directly and confirmed to be string-data comparisons / SafeLoader-unchanged / hardcoded-root os.walk / read-only, none reachable by an untrusted actor beyond the trust tier that already authored the input. Plus an unfiltered secret/PII sweep of the whole diff, including the new .txt log capture and daily log."
  severity_max: info
  findings: 0
  must_fix: []
  threat_model:
    - { boundary: "check-state.sh Python heredoc over .harness/**/feature.yaml", stride: T, mitigated: true }
    - { boundary: "harness_yaml.load_file (SafeLoader) over widened .claude/skills/harness/teams glob", stride: T, mitigated: true }
    - { boundary: "test fixtures writing throwaway tempfile roots", stride: T, mitigated: true }
  open_questions: []
  files_touched: []
  expertise_update: []
artifact: .harness/features/FEAT-06-team-layer-inv6/notes/review-harness-security-reviewer-c0.md
```
