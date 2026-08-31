# Security review — FEAT-45-adversarial-plan-panel — c1 (pinned c745d3a)

**Verdict: PASS.** M1's fail-open gate is genuinely closed under adversarial input, not just under
omission. M4 is unchanged and still open at med, but demonstrably unrealized (no live signed ruling
exists anywhere in this repo to be broken by a future digest widening). No new security surface in
the fix delta.

## Scope

Full diff `1d3e5db..c745d3a` is 51 files (~41 substantive, ~10 receipts/notes — matches dispatch's
expectation). The actual **fix delta** (c0's pin `d0ebbe6` → c1's pin `c745d3a`) is 14 files, of
which **2 are code**: `check-state.sh`, `test-check-state.py`. Everything else in the 14 is
STATE.md/feature.json bookkeeping and c0 review-note landing — no runtime surface.

## 1. The INV-32 allow-list — fail-closed under adversarial input, measured

`check-state.sh:211-214` at the pin:
```python
severity = str(item.get("severity", "")).strip().lower()
disposition = str(item.get("disposition", "")).strip().lower()
if severity not in {"info", "low", "med"} and disposition != "resolved" and fid not in overruled:
```
Ran the exact normalize→compare logic against 17 adversarial `severity` values a compromised or
prompt-injected reader/transcriber could plausibly emit (all legal under `harness_yaml.py`'s
`CSafeLoader` — confirmed no unsafe YAML loader anywhere in the load path, so no exotic Python-object
injection via YAML tags is even reachable):

| input | normalized | gates? |
|---|---|---|
| absent key | `''` | yes |
| `None` (YAML null) | `'none'` | yes |
| `''` | `''` | yes |
| `'HIGH'` | `'high'` | yes |
| `'Med'` | `'med'` | **no** (legitimate — case-insensitive match to an allowed token) |
| `'  low  '` | `'low'` | **no** (legitimate — whitespace-insensitive match) |
| `'  high  '` | `'high'` | yes |
| Cyrillic homoglyph `'lоw'` | unchanged (distinct codepoint) | yes |
| fullwidth `'ｌｏｗ'` | unchanged | yes |
| `['high']` (list) | `"['high']"` | yes |
| `{'x': 'high'}` (dict) | `"{'x': 'high'}"` | yes |
| `0`, `True`, `False`, `3.14` | stringified, non-matching | yes |
| `'unrated'` | `'unrated'` | yes |

Every case that is not a genuine, case/whitespace-normalized match to `info`/`low`/`med` gates. The
two "no" rows are an attacker who already writes the severity field writing a legitimately low value
— not a bypass, since they already hold the privilege the field grants (self-report, no escalation
path). The allow-list shape is structurally fail-closed: it is a 3-member allow-list under strict
equality, not an enumerated deny-list, so nothing needs to be *named* to be rejected — only the three
low-severity spellings need to be *matched* to pass. This differs qualitatively from the pre-fix
deny-list, which required the maintainer to enumerate every dangerous term and missed the empty case.

**Threat-model row re-rated** (dispatch item 4): cycle 0's "reader severity self-report → INV-32
gating, mitigated: true" was correctly overturned at c0 for the deny-list. At the new pin it is
`mitigated: true` again, but for a different, load-bearing reason — not "the allow-list happens to
name the safe cases" but "the control is default-deny by construction, so an unnamed or malformed
value cannot pass." The distinction matters for the next reviewer: this is not the same fragile
mitigation reinstated, it is a different, robust control shape.

**Vocabulary census, re-run against the allow-list** (dispatch item: widen c0's doctrine census to
the allow-list specifically). All six severity-vocabulary sources are still byte-identical for the
token set `info, low, med, high, critical, unrated`: `.claude/skills/harness/teams/plan-panel.yaml`,
`.claude/skills/harness/templates/plan.yaml`, `.claude/agents/harness-validator-lead.md`,
`.omp/agents/harness-validator-lead.md`, `.claude/skills/harness-spec-driven/SKILL.md`,
`.claude/skills/harness/SKILL.md`. The allow-list's complement is exactly `{high, critical, unrated}`
— precisely the three tokens doctrine says must gate. No doctrine-legal severity value is spuriously
gated; no gating value is spuriously admitted. `panel_findings.py` supplies no severity (id-only), and
no JSON schema governs `plan.yaml`, so these six files are the entire universe of runtime severity
sources.

**RED-capability**: not re-derived (already orchestrator-verified with a stated revert/re-diff
methodology); corroborated instead by running the live suite at the pin —
`python3 test-check-state.py`: **146 `ok -` lines, 0 `^FAIL` lines**, including
`ok - INV-32 unrated severities fail closed` and `ok - INV-32 plan panel fixtures, including
inv32-red`. M3's new fixture `case_inv32_unrated_severity_fails_closed` covers exactly the three
directions claimed: literal `unrated`, absent key, explicit `None`.

## 2. M4 — 32-bit truncated finding id — unchanged, carried at med, still unrealized

`panel_findings.py` is **byte-identical** between `d0ebbe6` and `c745d3a` (empty diff). `finding_id()`
still returns `PF-` + `sha256(...)[:8]` (32 bits). `check-state.sh` treats the id as an opaque string
throughout (`str(item.get("id","")).strip()`) — confirmed unchanged, no new consumer added.

Checked the ordering-cost concern directly: searched the full worktree for any `plan.yaml` carrying a
real `approval.rulings` entry keyed to a `PF-` id. **None exists.** FEAT-45's own `plan.yaml` has no
top-level `panel:` key at all (the mechanism it builds hasn't been run against itself yet — this
feature ships the panel, it doesn't yet carry one). Other features' `rulings:` fields in this repo
predate this schema entirely (free-text or a different `R-01`-style schema, never a `PF-` id). The
only `PF-` occurrences outside `panel_findings.py`'s own tests are a fixture literal (`PF-deadbeef`)
and prose in c0's UI review illustrating the risk hypothetically. **No signed plan today carries a
ruling this defect could invalidate; the cost-of-delay is real but still fully deferred.** Carried
forward at med, unchanged from c0.

## 3. Fix-delta sweep — no new surface

Swept the full 14-file fix delta (not just the 2 code files) for secrets and dangerous patterns:
- Secrets (`api[_-]?key|secret|password|token|bearer|-----BEGIN|AKIA...|ghp_...|xox[baprs]-`,
  case-insensitive): all hits are the English word "token" in prose about the `{{cycle}}` template
  placeholder and prior reviewers' secret-sweep methodology — **no credential-shaped strings**.
- Dangerous patterns (`eval\(|exec\(|os\.system|subprocess.*shell=True|pickle\.loads|yaml\.load\(|__import__|input\(`)
  against the 2 code files: **no matches**.
- `feature.json`/`STATE.md` diff: pin bump, cycle count, one new validator run entry — ordinary
  bookkeeping, no leaked internals.

## Assessed and carried forward from c0 (unchanged at this pin, none gating)

- M5 (med, qa), M6 (low, code), M7 (low, ui): not security-owned; no re-derivation performed.

```yaml
VERDICT: PASS
DIGEST:
  headline: "M1's fail-open gate is closed under adversarial input, not just omission — allow-list is structurally fail-closed, doctrine vocabulary census clean; M4 unchanged, med, unrealized (no live plan.yaml ruling exists to be broken)"
  in_scope: true
  scope_reason: "Fix delta touches an operator-signature invariant gate (check-state.sh INV-32) whose input is a reader/transcriber-controlled field — self-scoped IN for adversarial-input fail-open/closed analysis, per the dispatch's explicit hunt."
  severity_max: med
  findings: 1
  must_fix: []
  threat_model:
    - { boundary: "panel reader/transcriber severity self-report -> check-state.sh INV-32 allow-list", stride: T, mitigated: true }
    - { boundary: "panel_findings.py digest[:8] (32-bit) -> INV-32 overrule id matching", stride: T, mitigated: false }
  open_questions: []
  files_touched: []
  expertise_update: []
artifact: .harness/harness/features/FEAT-45-adversarial-plan-panel/notes/review-harness-security-reviewer-c1.md
```
