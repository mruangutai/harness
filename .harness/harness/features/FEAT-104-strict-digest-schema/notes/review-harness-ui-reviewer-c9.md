# UI Review (Mode B) — FEAT-104-strict-digest-schema — corrected pin `168f875f`, panel c9

Re-grade at the corrected pin, own view formed independently of the c7 note and the superseded
panel digest. Diff reviewed: `origin/main..168f875f` (verified `git rev-parse HEAD` on the worktree
= `71040f1c`, two bookkeeping commits ahead of the pin — read via `git show`/`git diff` against pin
objects, HEAD never touched).

## Scope — measured, not predicted

`git diff origin/main..168f875f --name-only` → 62 files (superset of the c7 diff, unchanged file
mix). Extension census: `md`×44, `py`×6, `html`×4, `sh`×2, `json`×2, `yaml`×2, `txt`×1, `fixture`×1.
Zero `css/scss/less/tsx/jsx/vue/svelte`. The 4 `.html` hits are the same
`notes/ship-review-plan-signature-c{1,2,3,4}.html` files graded at c7 — confirmed untouched between
6126ac07 and 168f875f (`git diff 6126ac07..168f875f --stat` lists 11 files, none of them these four),
so the c7 finding (generated ship-review artifacts, regenerate-footer confirmed, not authored
product UI) carries forward unchanged.

**No `DESIGN.md` for this feature** — `glob **/DESIGN.md` under the feature tree returns nothing.
Candidate 4 is OUT, by direct object check, not inference.

**Ruling: no rendered UI surface in this diff. IN SCOPE: the operator-facing rejection-message
surface (candidates 1–3), each independently re-graded below.**

## F3 — SC-08 file-naming gap — FALSIFIED (fixed at this pin, confirmed with verbatim text)

I did not inherit the c7 note's claim or the test's expectation. I loaded
`.claude/skills/harness/bin/validate-digest.py` as a module at this pin and ran
`validator.validate("harness-eng-lead", <digest carrying rogue_alpha/rogue_beta/rogue_gamma>)`
directly. Emitted text, captured verbatim:

> undeclared digest key(s): 'rogue_alpha', 'rogue_beta', 'rogue_gamma'. The digest contract is
> closed. Declare the field in .claude/skills/harness/bin/validate-digest.py: a lower-tier field
> carried by a lead belongs in PASSTHROUGH; a field in a persona's documented output block belongs
> in DOCUMENTED_OPTIONAL; a new required persona field belongs in SCHEMAS and must also be
> documented under DEC-216. A per-dispatch answer is not a digest key: put a PASS qualification in
> adequacy_notes or a per-step fact in the run state steps evidence container.

One message, all three keys, the **file** (`.claude/skills/harness/bin/validate-digest.py`) and the
**symbols** (`PASSTHROUGH`, `DOCUMENTED_OPTIONAL`, `SCHEMAS`) all named. SC-08's "by file and
symbol" bar is met. The fix is exactly the single added line the dispatch describes
(`git diff origin/main..168f875f` on this file: +89/-5 total, but `git diff 6126ac07..168f875f`
isolates the actual F3 fix to +3/-2 lines — `"Declare the field in "
".claude/skills/harness/bin/validate-digest.py: "` is new).

I also checked that the gap the c7 note raised against the *suite* — SC-08's own test not asserting
the filename substring — is closed too:
`tests/integration/test-validate-digest.py:_t04_three_key_failures` now asserts the literal token
`"validate-digest.py"` alongside `rogue_alpha/beta/gamma`, `"digest contract is closed"`,
`"PASSTHROUGH"`, `"DOCUMENTED_OPTIONAL"`, `"SCHEMAS"` as substrings of the single message. **F3 is
retired: no residual gap in either the message or its test.**

## F1 — schema_version downgrade — FALSIFIED (fixed, reproduced directly)

Ran `tests/integration/test-check-domain.py` at this pin: `12/12 T-06 check-domain cases passed`,
including `"schema_version floor refuses a version-2 checkpoint downgrade"`. Independently
reproduced the downgrade write outside the test file (own throwaway script against
`check_domain_support.fire`): an existing `schema_version: 2` checkpoint overwritten with
`schema_version: 1` exits 2 with stderr containing `"schema_version downgrade for a run
checkpoint."` and the remedy sentence `"Keep schema_version unchanged or increase it."` — actionable
on its own (G-13: names the concrete remedy, not just the fact). **F1 confirmed closed.**

## Cross-emitter message-consistency assessment

Three emitters carry the enforcement text an operator reads: `validate-digest.py` (digest-key
rejection), `check-domain.sh` (step-key rejection, schema_version floor, schema_version downgrade —
all via the file's existing `_head()` convention, confirmed against a dozen pre-existing call sites
in the same file, P-14), and `check-state.sh` (the at-rest `INV-16` sweep, same house style
`INV-16: {rel}: run {run_id} step {step_id}: undeclared step key or evidence shape {names} —
declare recovery fields in .claude/skills/harness/bin/run-state-schema.json; put per-dispatch facts
under evidence.`).

- **Route symbol for step keys is consistent across all three**: `check-domain.sh`'s write-time
  message and `check-state.sh`'s at-rest message both name the same file
  (`.claude/skills/harness/bin/run-state-schema.json`) and the same symbol (`evidence`), with
  near-identical remedy wording (only cosmetic phrasing differs — "A recovery field is declared in…"
  vs "declare recovery fields in…" — same content, not a defect).
- **`validate-digest.py`'s digest-key message correctly names a different file**
  (`validate-digest.py` itself) because that IS where a digest key is declared — this is not an
  inconsistency, it is each emitter naming its own true declaration route.
- **Agent-template guidance is byte-identical across the two lead files that carry it**:
  `.omp/agents/harness-eng-lead.md` and `.omp/agents/harness-product-lead.md` both add the exact
  same three-line paragraph — *"When a dispatch asks a specific question, put the answer in
  `adequacy_notes`…never a new digest key."* — and it matches the canonical text in
  `.claude/skills/harness-team/SKILL.md` and `.claude/skills/harness/SKILL.md` verbatim. No drift.
- **`harness-validator-lead.md`'s `severity_max` enum was corrected, not merely reworded**: `info` →
  `none`. Checked against `SEV = ["none", "low", "med", "high", "critical"]` in
  `validate-digest.py:36` — `"info"` was never a legal value; this diff fixes a real
  documented-block/contract mismatch (the class of defect REQ-09/SC-16 exists to catch), it does not
  introduce a new one.

## Agent-template dual-host pair consistency

`diff` on the post-frontmatter body of each `.claude/agents/<lead>.md` against its
`.omp/agents/<lead>.md` twin, for all three leads touched (`harness-eng-lead`,
`harness-product-lead`, `harness-validator-lead`): **bodies are byte-identical.** Frontmatter blocks
differ (tool-name casing, `model`/`skills` vs `spawns`/`autoloadSkills` keys) — that is the
pre-existing per-host frontmatter convention, unrelated to this diff's content, and not itself
touched by the FEAT-104 hunks (the added paragraphs land only in the shared body). No dual-host
drift introduced.

## New finding — F4 (mine), LOW, non-gating: `None` literal leaks into the downgrade message

Independently reproduced (own throwaway script, `check_domain_support.fire`, no source touched): an
existing `schema_version: 2` checkpoint updated with `schema_version` **omitted entirely** (not
lowered to a declared-but-smaller value — the case T-06's downgrade test does not cover; it only
constructs `2 → 1`) still correctly refuses at exit 2, but the message reads:

> schema_version downgrade for a run checkpoint.
> this existing checkpoint declares schema_version 2; the proposed write declares None. A strict
> checkpoint cannot opt out of its closed step schema. Keep schema_version unchanged or increase it.

`declares None` is a raw Python `repr(None)`, not prose. It is inconsistent with the sibling
schema_version-floor message in the **same file**, which handles the identical missing-value
condition with human phrasing: `"schema_version is absent"`. Concrete failure scenario: an agent's
Bash-authored update to an existing v2 run's `state.yaml` (e.g. a partial edit or a template that
drops the field) is correctly blocked, but the operator reading stderr sees an
implementation-detail token instead of "is absent" — a small, real actionability/consistency defect
inside the exact surface REQ-05 governs (does the message read as intended-for-a-human text, not as
a dump of the value it saw). The remedy sentence (`"Keep schema_version unchanged or increase it"`)
is still present and correct, so this does not block understanding or block the write's safety —
rating **LOW, non-gating**, in the DEC-174 read-only carve-out (I cannot patch the format string;
routing up as a finding, not a fix).

## F2 reassessment

F2's declined fix concerns whether `check-state.sh`'s at-rest sweep classifies historical digest
files through the generic `lead` CLI persona (`_vd_mod.validate("lead", _dtext)`,
`check-state.sh:1590`) versus the raw producing persona. **This does not touch operator-visible
text**: because the fix is declined, no new or changed message is emitted for historical digests
either way — they continue to pass the sweep silently, exactly as before this feature. This is a
coverage/enforcement-boundary decision (REQ-08/SC-12 stranding-avoidance, already argued in the
dispatch), not a wording or text-legibility question, so it sits outside this role's lens. No
independent UI finding to add.

## Accessibility / theme parity

Not applicable — no rendered surface, no colour-only state encoding, batch/CLI stderr text only
(repo Expertise G-02).

## Verdict rationale

Both prior findings (F1, F3) independently confirmed FIXED with direct execution against this pin,
not inherited claims. Cross-emitter and dual-host consistency checks pass. One new LOW,
non-gating finding (F4) on a narrow, untested edge case of the new downgrade message. No
`must_fix`. `severity_max: low`.

```yaml
VERDICT: PASS
DIGEST:
  headline: F1 and F3 independently confirmed fixed by direct execution at 168f875f; cross-emitter and dual-host message consistency hold; one new LOW non-gating finding (raw `None` literal in an untested downgrade-message edge case).
  mode: B
  in_scope: true
  severity_max: low
  findings: 1
  must_fix: []
  scope: "IN — extension census (62 files: md44/py6/html4/sh2/json2/yaml2/txt1/fixture1, zero rendered-UI extensions) plus direct `glob **/DESIGN.md` (0 hits) decided scope; the 4 html hits are the c7-confirmed generated ship-review artifacts, unchanged between 6126ac07 and 168f875f."
  contract_violations: []
  a11y: []
  f1_disposition: "FALSIFIED (i.e. the prior FIXED claim holds) — reproduced directly: T-06 12/12, and an independent repro of the 2->1 downgrade write exits 2 with 'schema_version downgrade for a run checkpoint.' plus an actionable remedy sentence."
  f3_disposition: "FALSIFIED (i.e. the prior FIXED claim holds) — captured the verbatim emitted message for a three-key rejection at this pin: names all 3 keys, the file (validate-digest.py), and the symbols (PASSTHROUGH/DOCUMENTED_OPTIONAL/SCHEMAS); the suite's own SC-08 case now asserts the 'validate-digest.py' substring too."
  f2_disposition: "Does not touch operator-visible text — the declined fix changes no message either way (historical digests keep passing the sweep silently); a coverage decision, not a text finding. No independent UI reassessment beyond this."
  f4_new_finding: "LOW, non-gating — schema_version-downgrade message renders Python `None` (not human prose) when an existing v2 checkpoint's update omits schema_version entirely, inconsistent with the sibling floor-creation message's 'schema_version is absent' phrasing for the identical condition; reproduced directly, untested by T-06 (whose downgrade case only covers a declared 2->1 value, not omission)."
  open_questions:
    - { id: Q1, question: "Should the schema_version-downgrade branch reuse the floor-check's existing missing-value/type-name phrasing (already computed a few lines above it in the same function) instead of Python repr, and should T-06 gain an omitted-on-update case to pin it? DEC-174 carve-out means I cannot apply this myself.", blocking: false }
  files_touched: []
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-104-strict-digest-schema/.harness/harness/features/FEAT-104-strict-digest-schema/notes/review-harness-ui-reviewer-c9.md
```
