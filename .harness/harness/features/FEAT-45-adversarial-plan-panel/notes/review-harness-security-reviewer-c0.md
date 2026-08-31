# Security review — FEAT-45-adversarial-plan-panel — c0 (pinned d0ebbe6)

## BLUF

One MED finding: the panel finding's 32-bit truncated content-hash identity
(`panel_findings.py`) feeds directly into `check-state.sh` INV-32's overrule-matching, and
that identity mechanism is not hardened against a deliberate second-preimage from the one
component this same diff (DEC-206) already declares content-unvalidated — the wrapped
`fable-advisor` reader. A crafted summary that hash-collides with a *previously overruled*
finding's id would be silently treated as already-cleared, defeating the exact gate INV-32
exists to enforce. Everything else examined is clean: no secrets, no shell/eval injection,
no path-traversal, and DEC-206's own named compensating control (severity self-report +
`unrated` gates as `high`) is genuinely present and consistent across all four places that
state it.

## Census — every file in the 40-file inventory, examined

**Logic (read in full or diffed in full at d0ebbe6):**
- `bin/panel_findings.py` — full read. Hash construction analyzed line-by-line (see finding).
- `bin/test-panel-findings.py` — full read; confirmed no test exercises reader-field newline
  injection or collision resistance.
- `bin/check-state.sh` — diffed precisely (`git diff 1d3e5db..d0ebbe6`) to isolate the INV-32
  addition from the ~1800 pre-existing lines; INV-32 block read in full. Pure Python
  string/dict operations on parsed YAML — no `eval`, no shell-out with untrusted content.
- `bin/test-check-state.py` — new INV-32 fixture helpers (`_inv32_plan`, `_inv32_run`) read;
  `subprocess.run([script], ...)` is a fixed self-path, list-form, no injection.
- `bin/test-harness-yaml-corpus.py` — diffed; `TEAMS_EXPECTED` 2→3, a data constant, no logic.
- `bin/test-plan-panel.py` — read header + all `subprocess.run` call sites
  (`check-domain.sh --resolve <path>`); list-form argv, fixed binary, paths sourced from the
  team file's own declared outputs, not attacker input.
- `bin/run-unit-tests.sh` — diffed; exactly two new literal strings appended to
  `UNIT_SCRIPTS`. No new code path.
- `bin/sync-agent-adapters.py` — diffed; exactly one new literal string
  (`"fable-advisor"`) appended to the `SPAWNS["harness-validator-lead"]` list, plus a comment.
  Confirmed by reading `claude_adapter()`/`bootstrap_one()` that `SPAWNS` values feed the
  `spawns:` frontmatter field, never a filesystem path — no path-handling code in this
  function is touched by the diff, so "write outside the intended directory" does not apply
  to what changed here.

**Doctrine (diffed in full):**
- `skills/harness/teams/plan-panel.yaml` — full read. `should-not-exist` (fable-advisor)
  step declares `outputs: []` — the wrapped reader has no write grant; only the lead
  transcribes. `scope` step's new note path
  (`notes/review-harness-code-reviewer-planpanel-c{{cycle}}.md`) checked against
  `team-config.yaml`'s `harness-code-reviewer` domain grant
  (`.harness/*/features/*/notes/review-harness-code-reviewer-*.md`) — matches, no new write
  surface outside the existing grant.
- `skills/harness/SKILL.md`, `commands/harness-plan.md`, `skills/harness-spec-driven/SKILL.md`,
  `skills/harness/templates/plan.yaml` — diffed in full; pure doctrine prose plus the new
  `panel:` template block. Verified `panel:` is declared a sibling of `approval:`, and
  `.harness/team-config.yaml:25` (`".harness/*/features/*/plan.yaml approval:"`) is a
  pre-existing, unchanged, key-level deny-list entry read by `check-domain.sh`
  (`_yaml_key_range`, unchanged). pm's grant
  (`.harness/*/features/*/plan.yaml, upsert: true # except approval:`) is unchanged by this
  diff — the new `panel:` key rides on infrastructure that already exists and was already
  built to resist key-boundary bypass (comment at `check-domain.sh:644-648` describes three
  previously-fixed bypasses). Not a gap opened by this diff.
- Both `.omp/agents/harness-validator-lead.md` and `.claude/agents/harness-validator-lead.md`
  — diffed; identical new section in both copies (byte-for-byte prose match checked by eye).
  `.omp` also gains `fable-advisor` in `spawns:`; `.claude`'s adapter format has no `spawns:`
  field at all (confirmed in `claude_adapter()`, unchanged by this diff) — this asymmetry
  predates FEAT-45 for every agent, not introduced here, so it is not a new finding.

**Decisions/docs:** `DECISIONS.md` (DEC-206, DEC-207) and `DECISIONS-INDEX.md` read in full —
text only, no executable content, no secrets.

**Everything else in the 40-file list** (`BRIEF.md`, `STATE.md`, `feature.json`, `plan.yaml`,
all `notes/*.md`, `observations/*.md`) is process bookkeeping and prior-cycle receipts, not
shipped runtime surface — grepped as part of the whole-diff secret sweep below, otherwise out
of scope for this lens.

**Secrets sweep:** `git diff 1d3e5db..d0ebbe6 -- .` piped through a case-insensitive grep for
`api[_-]?key|secret|password|token|bearer|-----BEGIN|ssh-rsa|AKIA...|gh[pousr]_...` across
all 41 files, not just the named ones (P-14). Every hit is the `{{cycle}}` template token in
prose about test coverage — no credential-shaped string anywhere in the diff.

**Dangerous-pattern sweep:** grepped the full diff's added Python/shell lines for
`shell=True|eval\(|exec\(|os\.system|subprocess\.(call|run|Popen)|pickle\.|yaml\.load\(|input\(`.
Three `subprocess.run` hits, all already covered above (list-form argv, fixed binaries or
self-paths, no shell).

## Finding — MED

**`.claude/skills/harness/bin/panel_findings.py:28-33`, gated by
`.claude/skills/harness/bin/check-state.sh:202-214`** — the panel finding identity is
`PF-` + the first 8 hex chars (32 bits) of `sha256(reader + "\n" + normalize(summary))`. That
id is the sole key INV-32 uses to decide whether an *existing* operator overrule still covers
a *current* finding (`check-state.sh:206` `overruled.add(fid)`; `:214`
`fid not in overruled` gates high/critical/unrated findings). 32 bits is a deliberate second-
preimage search of roughly 2^31 average SHA-256 evaluations — seconds to low minutes on
commodity hardware, not a cryptographic barrier — and the one component whose content this
same diff already declares "structurally unvalidated" (DEC-206, on `fable-advisor`) is
exactly the component that supplies the `summary` text this hash is computed over.

**Concrete scenario:** cycle 0, `fable-advisor` reports finding A (severity `high`,
summary S_A); the operator overrules it, and `approval.rulings` permanently records
`{finding: PF-<hash(A)>, ruling: overrule, ...}` in `plan.yaml` (visible in the repo). Cycle 1
re-runs the panel with `approval` reset to pending. If `fable-advisor`'s output for that
cycle is influenced — either the reader itself is compromised, or content in the plan/BRIEF
it reads carries an instruction crafted to make it emit a specific string verbatim — to
produce a *new, substantively different* high-severity summary S_B whose normalized form was
pre-computed offline (public algorithm, public prior id) to collide on the same 32-bit
prefix, `finding_id("should-not-exist", S_B)` equals the old, still-recorded ruling's id.
INV-32 then finds `fid in overruled` for finding B and never gates it — the operator signs a
plan carrying a genuinely new high-severity concern that the mechanical gate silently treated
as already settled. This does not re-litigate DEC-206's signed trade (that trade is about the
reader's *severity* self-report being honest); it is a second, orthogonal gap in the
*identity* mechanism DEC-206 did not name, and `test-panel-findings.py` has no case for it
(case 3 only checks that an *innocuous* one-character change produces a *different* id, never
that a *deliberately engineered* different summary cannot produce the *same* id).

**Why MED, not HIGH:** exploitation needs (a) an actual prior overrule to target — absent on
a feature's first cycle, and (b) either a compromised reader backend or reliable prompt
injection of exact-string output, both stronger preconditions than an ordinary content
manipulation. DEC-207 also leaves the operator as a human backstop who nominally reads the
digest before signing. That backstop is exactly what INV-32 exists to not have to rely on,
which is why this is a real, worth-fixing gap and not a decline.

**Suggested fix (direction, not prescription):** widen the id to the full 64 hex characters
(no truncation) or otherwise document why 32 bits is an accepted risk for a security-gating
identity, matching how `panel_findings.py`'s own docstring already reasons carefully about
the *innocuous* collision case but is silent on the *adversarial* one.

## Assessed and dismissed

- **Reader-field newline ambiguity in `finding_id`** (`panel_findings.py:31`) — `reader` is
  concatenated raw, unnormalized, so an embedded `\n` in `reader` could in principle make the
  digest_input's delimiter ambiguous against a different (reader, summary) split. Dismissed
  at info: `normalize_summary` collapses all whitespace runs (including `\n`) to a single
  space, so the summary side of the digest can never itself contain the delimiter character,
  and every real call site (the CLI usage documented across `plan-panel.yaml`,
  `harness-spec-driven/SKILL.md`, `templates/plan.yaml`) passes one of exactly three literal
  reader names with no newline. Not exploitable through any path this diff wires up.
- **Prompt injection from repo content reaching `fable-advisor`** — real in the abstract
  (repo content flows to an external LLM whose return is unvalidated by design, DEC-206), but
  architecturally identical to every other harness reader that already reads plan/BRIEF
  content, not something this diff newly introduces. Bounded further by
  `check-domain.sh`/`team-config.yaml:303-309`: `harness-validator-lead`'s write domain is
  scoped to its own run directory, its own expertise/observations files, and
  `.harness/notes/analysis-*.md` — even a fully manipulated lead cannot write outside that
  domain, so injected content reaching the lead cannot itself reach `plan.yaml`, source, or
  any other agent's files. Folded into the MED finding above rather than raised separately,
  since the concrete, demonstrable channel is the hash-collision path, not injection alone.
- **DEC-206's compensating control** — verified present, not just claimed. The exact rule
  ("`unrated` is gating-equivalent to `high`") is stated identically in
  `plan-panel.yaml` (both reader prompts), `.omp/agents/harness-validator-lead.md` and its
  `.claude` twin, and enforced mechanically at `check-state.sh:214`
  (`severity in {"high","critical","unrated"} ... and fid not in overruled`). Four
  independent statements of the same rule, all consistent, one of them load-bearing code.
- **`sync-agent-adapters.py` path handling** — the function that writes files
  (`bootstrap`/`sync`, writing to `target_dir / source.name`) is untouched by this diff; the
  one-line change only appends a string to a list consumed as YAML frontmatter data, never as
  a filename or path component. No traversal surface here to audit that the diff itself
  opened.
- **`check-state.sh` shell wrapper** (root resolution, `python3 -I -c ...`) — unchanged by
  this diff (confirmed via `git diff`); INV-32 lives entirely inside the existing heredoc's
  Python, which receives `root`/`_selfdir` as `sys.argv`, not shell-interpolated.

```yaml
VERDICT: PASS
DIGEST:
  headline: "One MED finding (32-bit truncated finding-id feeds INV-32's overrule gate, no test for adversarial collision); nothing HIGH+, ship-blocking"
  in_scope: true
  scope_reason: "New content-hash identity mechanism (panel_findings.py) gates an operator-signature invariant (check-state.sh INV-32) and is fed by a component (fable-advisor) this diff itself declares content-unvalidated (DEC-206) — squarely Tampering/Integrity, plus a new external-subagent trust boundary, secrets, and write-domain surface to check across 40 files."
  severity_max: med
  findings: 1
  must_fix: []
  threat_model:
    - { boundary: "fable-advisor summary text -> panel_findings.py hash -> check-state.sh INV-32 overrule match", stride: "T", mitigated: false }
    - { boundary: "fable-advisor return -> validator-lead context (prompt injection)", stride: "E", mitigated: true }
    - { boundary: "pm write of plan.yaml `panel:` key vs main-session-only `approval:` key", stride: "T", mitigated: true }
    - { boundary: "reader severity self-report -> INV-32 gating (DEC-206 compensating control)", stride: "T", mitigated: true }
  open_questions: []
  files_touched: []
  expertise_update: []
artifact: .harness/harness/features/FEAT-45-adversarial-plan-panel/notes/review-harness-security-reviewer-c0.md
```
