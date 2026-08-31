# Security review — c4 — B-1/M4 disposition (FEAT-45, pin `bdd5666`)

## Verdict on the central question

**B-1/M4 is CLOSED.** An adversarial-collision test is **unnecessary, not merely absent** — see
arithmetic below.

## 1. The widening is correct and complete

`git show bdd5666:.claude/skills/harness/bin/panel_findings.py` (lines 28-34):

```python
def finding_id(reader, summary):
    normalized = normalize_summary(summary)
    digest_input = f"{reader}\n{normalized}".encode("utf-8")
    digest = hashlib.sha256(digest_input).hexdigest()
    return f"PF-{digest[:32]}"
```

- Full `sha256(...).hexdigest()` is computed first (64 hex chars), *then* sliced `[:32]` — no
  truncate-before-hash bug, no double hashing, no change to `normalize_summary` (whitespace
  collapse + lowercase, byte-identical to prior cycles).
- Empirically executed the pinned module directly (not just read):
  - `finding_id("alice", "Some Finding   Summary")` → `PF-658910b040cdc64a79962249191fd09a`, length
    **35** (`PF-` + 32 hex).
  - Confirmed `digest[:32]` == the id's suffix against an independently computed
    `hashlib.sha256(...).hexdigest()` (64 chars) — the slice is exactly the first half of the real
    digest, not a shorter hash truncated further.
  - Whitespace/case-mangled summary → **same id** (stability). One-char summary change → **different
    id** (sensitivity). Both hold at the new width.
- `git diff 302ae9d bdd5666` touches exactly 3 code/doc-adjacent files:
  `panel_findings.py` (`[:8]`→`[:32]`, docstring "8"→"32"/"11"→"35"), `test-panel-findings.py` (same
  three assertions retargeted to 35/32), and this feature's `plan.yaml` D-05 + T-06 intent text
  (2 hunks, "8 hex"→"32 hex"). No other production file in the delta. Ran
  `test-panel-findings.py` at the pin directly: **9/9 PASS**, including the length-35/32-hex-suffix
  assertion — corroborates, does not merely restate, Main's reported evidence.
- Swept every tracked file under `.claude/` (working tree == pin content for `.claude`, confirmed via
  `git diff bdd5666 HEAD -- .claude` = empty) for `[:8]`, `8 hex`, `8-hex`, `length 11` — the only hit
  (`test-no-distribution.py:415`) is an unrelated `hits[:8]` list-slice for a diagnostic message, not
  an id computation. **No other place in shipped code still computes on the old width.**

## 2. Is an adversarial-collision test now unnecessary?

**Yes — genuinely unnecessary, not just absent.** The id is `PF-` + 32 hex characters = **128 bits**
of a full SHA-256 digest (not a separately truncated weaker hash — SHA-256 restricted to its first
128 output bits inherits that construction's collision/preimage hardness with no known shortcut).

- **Random/birthday collision** (two unrelated findings landing on the same id by chance): the
  birthday bound for an *n*-bit space is ~2^(n/2) items for 50% collision probability → **2^64**
  findings. A realistic population — every panel finding ever recorded across every feature's
  `panel.findings[]` in this repo, cumulatively, forever — is on the order of 10²–10⁴, not
  10¹⁹. At n≈10³, expected accidental-collision probability ≈ n²/2^129 ≈ (10³)²/6.8×10³⁸ ≈ 10⁻³³.
  Zero practical risk.
- **Targeted/adversarial forgery** (the actual M4 threat: a compromised or prompt-injected reader
  crafts a *new* finding's `reader`+`summary` text so its hash collides with a specific *existing,
  already-overruled* finding's id, so the new finding silently inherits the stale ruling and INV-32
  never re-asks the operator): this is a **second-preimage** problem against one fixed 128-bit
  target, not a birthday search — it does not get a square-root speedup from having many findings to
  aim at (even granting the attacker their pick of every overruled id ever recorded, ~10³ targets,
  the work drops from 2^128 to ~2^128/10³ ≈ 2^118, still cryptographically infeasible). At the old
  8-hex/32-bit width this was the opposite story: birthday collision needed only ~2^16 (65,536)
  findings — plausible given this repo already has 40+ features × multiple review cycles × several
  findings each — and a *targeted* forgery needed only ~2^32 trial hashes, computable in well under
  an hour on a single CPU core. That gap is exactly what M4 was raised against, and it no longer
  exists.
- No executable test can usefully close a 2^128 hardness claim — a test can only ever brute-force a
  vanishingly small corner of that space and would prove nothing about the tail (unlike the ReDoS or
  race-condition cases where a runnable measurement is expected practice). The closure here is
  structural: SHA-256 is unbroken, and 128-bit truncations of unbroken hashes are the field-standard
  security margin (comparable to a 128-bit UUIDv4, or Git's own SHA-256 object-id transition). SC-13
  never pinned a width, so it doesn't need a new test either — it already covers
  stability/change-sensitivity, which this review re-confirmed above.

**Residual surface: none rising to a finding.** See §4 for two doc-only staleness items, both
IMPROVEMENT-grade, not risk-bearing.

## 3. INV-32's stale-override match — string equality confirmed, no prefix risk

`check-state.sh:184-206` (unchanged by this delta — confirmed via `git diff 302ae9d bdd5666`
touching only `panel_findings.py`, its test, and `plan.yaml` text, not `check-state.sh`):

- `finding_ids = {str(item.get("id","")).strip() for item in findings ...}` (line 185-188) — a
  Python `set` of exact strings (`.strip()` only, no `.lower()`, no slicing).
- `fid = str(ruling.get("finding","")).strip()` (line 198); the test is `if fid not in finding_ids`
  (line 201) — `in` against a `set` is exact hash/equality membership, **never** substring or prefix
  matching. Same construction for `overruled` (line 193, populated at line 206) and its use at line
  216 (`elif fid in overruled`).
- Since `hexdigest()` always emits lowercase hex, there is no case-folding hazard either.
- Net: at either the old or new width, a partial/prefix id can never match a full id here — the
  widening closes the *hash-forgery* surface (§2) without depending on any matching-side fix, and the
  matching side introduces no new risk of its own at the wider width.

## 4. OWASP/STRIDE pass over `git diff 302ae9d bdd5666`

Full diff is 5 files / 10+11 lines: `panel_findings.py` (2-line change: `[:8]`→`[:32]`, docstring),
`test-panel-findings.py` (3 assertions retargeted), `plan.yaml` (D-05 choice text + one task intent
line), and two `ship-review-2026-08-31.{md,html}` edits removing the now-resolved B-1 backlog row
(consistent — the enhancement it tracked has shipped). **No security surface beyond what §§1-3 already
cover**: no new input path, no auth/session code, no secrets, no injection surface, no dependency
change, no data-exposure change. Nothing further to flag.

## Findings

| # | Item | DEFECT / IMPROVEMENT | Why |
|---|---|---|---|
| 1 | `plan.yaml` T-09's own `verify:` clause (line 1019: `test 11 -eq "${#A}"`) and its `intent:` text (lines 1031, 1052) still describe the 8-hex/length-11 scheme; line 641 similarly says "8 hex" | **IMPROVEMENT** (backlog, not this review's file to fix) | Confirmed unreachable by the currently-passing suite (rc=0, 433 script-result lines, no KIND-DRIFT reported at the pin) — these are stale prose/verify-text on an already-`done` task, not a live gate. Not itself exploitable. Worth flagging because a future engineer who trusts the stale `verify:` text over the actual shipped code could "fix" `panel_findings.py` back toward the 8-hex scheme to satisfy it — that would silently reintroduce the exact M4 surface this cycle just closed. PM/documentor domain to correct; not a security must_fix today because nothing currently executes or trusts that text. |
| 2 | `.claude/skills/harness/templates/plan.yaml:56` example `id: PF-0123abcd` (8 hex) | **IMPROVEMENT** (backlog) | Documentation example only; D-05 states the id is computed exactly once by `panel_findings.py` and never hand-assigned, so a stale example cannot produce a real 8-hex id in practice. Cosmetic drift, not a security gap. |

No DEFECT-grade findings. `must_fix: []`.

## Answers, plainly

- **Is B-1/M4 closed?** Yes.
- **Is an adversarial-collision test now unnecessary, rather than merely absent?** Yes — 128-bit
  SHA-256-derived preimage resistance (~2^128 targeted-forgery work) is beyond what any executable
  test can meaningfully probe or falsify; the closure is structural, on the same footing as any
  128-bit content-addressed identifier in production use elsewhere.

```yaml
VERDICT: PASS
DIGEST:
  headline: "B-1/M4 CLOSED — id is a correctly-sliced 128-bit SHA-256 prefix (2^128 targeted-forgery work vs the old 2^32); INV-32 matches by exact string equality with no prefix risk; delta carries no further security surface."
  in_scope: true
  scope_reason: "Delta changes the width of a content-hash identity that feeds an approval-overrule trust boundary (INV-32) — squarely a security surface; verified by reading and executing the pinned module."
  severity_max: low
  findings: 2
  must_fix: []
  threat_model:
    - { boundary: "approval.rulings[].finding vs panel.findings[].id (INV-32 stale-override match)", stride: T, mitigated: true }
    - { boundary: "panel_findings.py hash-forgery of a finding id to inherit a stale overrule", stride: S, mitigated: true }
  open_questions: []
  files_touched: []
  expertise_update: []
artifact: .harness/harness/features/FEAT-45-adversarial-plan-panel/notes/review-harness-security-reviewer-c4.md
```
