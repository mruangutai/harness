## BLUF

`quarantine.py` does everything T-04 specified — it imports `inflight_registry.CANONICAL_ARTIFACTS`
and delegates `plan.yaml` adoption to `plan-merge.py apply`; no violation there. But the reverse
direction the dispatch asked me to check independently turns up a real one: `check-domain.sh` and
`plan-sign-gate.py` hand-write the *same four-clause refusal sentence* twice, verbatim except for
the label prefix. I also found two more reuse gaps on my own pass: a hardcoded canonical-artifact
tuple in `test-quarantine.py` that should import the constant it is testing against, and a
self-acknowledged duplicated fence-toggle scanner in `test-gen-decisions-index.py`. Four findings
total, three writable, one report-only.

## Lead 1 — quarantine.py's REUSE obligations: VERIFIED, no finding

- `CANONICAL_ARTIFACTS`: imported and consulted, never restated —
  `quarantine.py:107-108` (`if basename not in inflight_registry.CANONICAL_ARTIFACTS:` /
  `legal = ", ".join(inflight_registry.CANONICAL_ARTIFACTS)`), sourced from
  `inflight_registry.py:23`.
- `quarantine_rel`: `quarantine.py` never needs the forward direction (it is handed an
  already-quarantined path, not building one), so there is nothing to reuse there. Its
  `_split_agent_session` (`quarantine.py:62-69`) is a legitimate *inverse* used only for
  display in `cmd_list`, not a restatement of `quarantine_rel`'s construction logic.
- `plan.yaml` adoption: delegated, not reimplemented — `quarantine.py:117-140` shells out to
  `plan-merge.py apply --file <canonical> --proposal <quarantined>` via `subprocess.run` and
  surfaces both exit code and both streams verbatim. No union-by-id or approval-merge logic is
  duplicated in `quarantine.py`.
- `_resolve_root` correctly delegates to `harness_boundary.resolve_root` (`quarantine.py:44-53`)
  rather than reimplementing checkout discovery.

**Answer to lead 1: quarantine.py does import both `CANONICAL_ARTIFACTS` and rely on the
`quarantine_rel` naming convention correctly, and does delegate plan.yaml adoption to
plan-merge.py — verified at `quarantine.py:107-108`, `:117-140`.**

## Lead 2 — check-domain.sh vs plan-sign-gate.py refusal messages: DUPLICATE, report-only

Both files, on the same orphan-write-to-canonical-artifact condition, hand-construct a message
asserting the same four facts: (1) the path is canonical, (2) the agent holds no live claim for
the feature, (3) the parent is gone and a replacement may be racing, (4) adoption is the resumed
parent's exclusive act.

- `check-domain.sh:1695-1702`:
  `f"check-domain: BLOCKED — {_show(target)} is canonical, but {agent} holds no live claim for "`
  `f"{_feature}. Its parent is gone and a replacement may already be writing.\n"`
  `f"  Write the completed result to {_quarantine} instead.\n"`
  `f"  It becomes canonical only when the resumed parent runs quarantine.py adopt on that file.\n"`
- `plan-sign-gate.py:408-414`:
  `f"Refused: {rel} is canonical, but {agent} holds no live claim for "`
  `f"{feature}. Its parent is gone and a replacement may already be writing.\n"`
  `f"{remedy}\n"`
  `"A quarantined result becomes canonical only when a resumed parent runs "`
  `"quarantine.py adopt.\n"`

The middle sentence — `"is canonical, but {agent} holds no live claim for {feature}. Its parent
is gone and a replacement may already be writing."` — is character-for-character identical
between the two files; only the label (`check-domain: BLOCKED` vs `Refused`) and the remedy
clause differ.

**Concrete cost:** these are two independent hand-written copies of one operator-facing
sentence, verified with `git diff 0bc57c88..HEAD` to both be new additions in this diff (neither
existed before). If the wording is ever revised — to add detail, fix a typo, or match a future
message elsewhere — an editor working from either file has no signal that the other one exists,
and the two gates will silently start telling the operator two different stories about the same
refusal. `plan-sign-gate.py`'s own file-header comment already states this exact principle
("ONE refusal text, used verbatim for EVERY denial. A second wording would drift") for its
`sign-approval` refusal (`REASON`, line 51-52) — the same file breaks its own rule three hundred
lines later for the quarantine refusal.

**Alternative:** hoist the shared sentence into one function in `inflight_registry.py` (the
module both callers already import), e.g. `orphan_refusal_reason(target_or_rel, agent, feature)`
returning the canonical-but-no-claim clause, called from both `check-domain.sh` and
`plan-sign-gate.py`; each site keeps its own label prefix and remedy line, which are the only
parts that legitimately differ by tool surface.

**`applicable: report-only`** — both `check-domain.sh` and `plan-sign-gate.py` are on the DEC-174
no-edit list; this is filed for the record, not for this pass to apply.

## Additional findings (my own pass)

### F-3 — `test-quarantine.py:198` hardcodes the canonical-artifact list instead of importing it

`test-quarantine.py:198` asserts
`for legal in ("plan.yaml", "BRIEF.md", "feature.json", "STATE.md"):` — a literal restatement of
`inflight_registry.CANONICAL_ARTIFACTS` (`inflight_registry.py:23`), even though the file this
test targets, `quarantine.py`, already imports that exact constant and the test file has no
reason not to (`test-quarantine.py` imports only stdlib + `yaml`, no `inflight_registry`).

**Concrete cost:** the test exists to prove the refusal message names every legal basename. If
`CANONICAL_ARTIFACTS` ever grows a fifth entry, `quarantine.py`'s refusal message updates
automatically (it derives from the constant), but this test's hardcoded tuple does not — the test
keeps asserting only the original four and silently stops covering the new one, with no failure
to flag the gap.

**Alternative:** `import inflight_registry` (same `sys.path.insert` pattern `quarantine.py` uses)
and iterate `inflight_registry.CANONICAL_ARTIFACTS` instead of the literal tuple.

**`applicable: writable`** — `test-quarantine.py` is squad-writable.

### F-4 — `test-gen-decisions-index.py`'s `_dec_region` duplicates `fence_guarded_dec_headings`'s fence-toggle scan

`_dec_region` (added this diff, `test-gen-decisions-index.py:~889-903` per the diff hunk) and the
pre-existing `fence_guarded_dec_headings` (`test-gen-decisions-index.py:46-61`) both implement the
identical line-scan: toggle `infence` on a ```` ``` ```` line, skip lines while fenced, then
regex-match `## DEC-\d+` on the rest. `_dec_region`'s own docstring admits it: "Mirrors
fence_guarded_dec_headings's fence toggle exactly." They differ only in what happens after a
match — one collects every heading, the other captures the slice between two matching headings.

**Concrete cost:** the fence-guard rule is the correctness-sensitive part of both functions (it
exists so a `## DEC-210` shown as a formatting example inside a fenced code block is never
mistaken for a live entry) — exactly the kind of rule that gets a fix later. A fix to the toggle
logic in `fence_guarded_dec_headings` (e.g. handling `~~~` fences, or indented fences) has no
mechanical link to `_dec_region`, so the two can silently diverge on which headings are "live",
and the new function's own docstring promise ("exactly") goes stale without either function's
tests catching it.

**Alternative:** factor the shared scan into one generator, e.g.
`_unfenced_lines(text)` yielding `(index, line)` pairs with the fence toggle applied, and have
both `fence_guarded_dec_headings` and `_dec_region` iterate it instead of each carrying its own
copy of the toggle.

**`applicable: writable`** — `test-gen-decisions-index.py` is squad-writable.

## Not flagged (considered, ruled out)

- `plan-sign-gate.py`'s new `_invocation` (tool/verb-adjacency-past-`--`) loop echoes the shape of
  the pre-existing `denies` loop (`plan-sign-gate.py:277-300` vs `:309-321`, both skip a `--`
  separator token the same way before checking the next token). Real, but `plan-sign-gate.py` is
  DEC-174 report-only and this shape-echo is thinner than F-2/F-4 (five lines, one skip-loop, not
  a whole restated multi-clause block); noted here for completeness, not raised as a numbered
  finding — flagging every echoed five-line loop in a report-only file would bury the two that
  matter.
- `test-harness-yaml.py`'s six repeated `.harness/*/features/*/quarantine/**` literals and
  `test-check-domain.py`'s matching YAML fixture text are intentional, independently-derived test
  oracles against `team-config.yaml`'s one real glob (`team-config.yaml:79`) — hardcoding the
  expected value is correct test design here, not restatement of a helper; confirmed against
  `receipt-harness-dev-ops-fix-collectfixture-c1.md`, which built these fixtures deliberately for
  this reason.
- `quarantine.py`'s prose docstring mentioning `(plan.yaml, BRIEF.md, feature.json, STATE.md)` is
  comment text, not code with a lockstep-edit cost — skipped.

```yaml
VERDICT: PASS
DIGEST:
  headline: quarantine.py reuses inflight_registry/plan-merge.py correctly; check-domain.sh and plan-sign-gate.py hand-duplicate one refusal sentence, plus two test-file duplications found independently
  findings_count: 4
  open_questions: []
  files_touched:
    - .harness/harness/features/FEAT-51-claude-code-lifecycle-safety/notes/receipt-harness-backend-dev-simplify-reuse-c1.md
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-51-claude-code-lifecycle-safety/.harness/harness/features/FEAT-51-claude-code-lifecycle-safety/notes/receipt-harness-backend-dev-simplify-reuse-c1.md
```
