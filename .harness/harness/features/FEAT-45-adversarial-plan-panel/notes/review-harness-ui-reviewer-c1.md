# UI Reviewer — Mode B re-review, cycle 1 — FEAT-45-adversarial-plan-panel

**Pin note (provenance, checked before anything else):** the dispatch's 40-char pin
`c745d3a61f1049e5325854618511544b10f68753` does not resolve (`git cat-file -t` fails). The 7-char
prefix `c745d3a` DOES resolve uniquely, to `c745d3a07c2accd8395c9df7a25d911d40dc2c09`, message `fix:
fail closed on unrated panel findings`, one commit behind HEAD `401089a` (`chore: repin FEAT-45
review after fixes`) — exactly the shape the dispatch describes (message content, position). Treated
`c745d3a07c2accd8395c9df7a25d911d40dc2c09` as the real pin; the given 40-char string appears
mistyped past the 7th character. Flagging as an open question, not blocking — the object it names is
unambiguous.

## DESIGN.md / rendered-UI census — reconfirmed, unchanged

`git ls-tree -r c745d3a -- .harness/.../FEAT-45-adversarial-plan-panel | grep -i design` → no hits.
`git diff --name-only 1d3e5db c745d3a | grep -Ei '\.(html|css|scss|tsx|jsx|vue|svelte|less)$'` → no
hits (51 files touched by the full feature diff; the dispatch's ~41 undercounts because it's the
build-only slice — immaterial). Mode B against a DESIGN.md contract is unavailable, as cycle 0
established. Not re-derived, re-measured.

## Primary hunt — severity-vocabulary census against the new allow-list `{info, low, med}`

**The gate, read at the pin** (`check-state.sh:214-215`):
```
if severity not in {"info", "low", "med"} and disposition != "resolved" and fid not in overruled:
    bad.append(f"INV-32: {feat} finding {fid} is {severity or 'unrated'} and remains open ...")
```
`severity` is lowercased before comparison (`str(item.get("severity","")).strip().lower()`), so case
variants are not a separate risk.

**Files swept (10, beyond the seven doctrine files cycle 0 censused):**
1. `.claude/skills/harness/templates/plan.yaml:57` — `severity: unrated  # info | low | med | high | critical | unrated`
2. `.claude/skills/harness/teams/plan-panel.yaml:23-24` (should-not-exist reader) and `:46` (scope reader) — both: `severity (one of info, low, med, high, critical, unrated)`
3. `.harness/harness/features/FEAT-45-adversarial-plan-panel/plan.yaml:441-442,642,854-857` — same 6-token set, plus the explicit "treat unrated exactly as high" rule
4. `.harness/harness/docs/DECISIONS.md` DEC-206 (:7429-7443) — `unrated` sentinel, "self-emitted severity", "an omitted severity fails closed"
5. `.claude/skills/harness/SKILL.md:111` — "High, critical, or unrated findings return `awaiting_user`" (deny-language, consistent subset of the same 6 tokens, no new one)
6. `.claude/skills/harness-spec-driven/SKILL.md:108-112` — pm transcription contract; no full listing, no contradicting token
7. `.claude/skills/harness/bin/check-state.sh:214-215` — the gate itself
8. `.claude/agents/harness-validator-lead.md:129` and `.omp/agents/harness-validator-lead.md:135` — `severity_max: info|low|med|high|critical` — **a different field** (digest rollup, not per-finding severity); no `n/a`, no `unrated` here since the panel host is never scoped out
9. `.claude/skills/harness/bin/test-check-state.py` (fixtures) — tokens used: `"high"`, `"unrated"`, absent key, `None` (JSON-null). `panel_findings.py` carries no severity handling at all (identity/hashing only, confirmed by reading the file — 55 lines, `severity` never appears)
10. Every `plan.yaml` repo-wide (`git ls-tree -r c745d3a | grep 'features/.*/plan\.yaml$'`, grepped for a `severity:` field) — **zero real panel-finding severity values exist anywhere in the repo today.** FEAT-45 is the first feature to carry this mechanism; there is no historical drift to measure, only the doctrine's stated vocabulary.

**Tokens found and verdict against `{info, low, med}`:**

| token | source | verdict |
|---|---|---|
| `info` | all 4 doctrine listings | passes (in allow-list) |
| `low` | all 4 doctrine listings | passes |
| `med` | all 4 doctrine listings | passes |
| `high` | all 4 doctrine listings, test fixture | gates — correct, deny-list also caught this |
| `critical` | all 4 doctrine listings | gates — correct, deny-list also caught this |
| `unrated` | all 4 doctrine listings, DEC-206, test fixture | gates — correct, this is the exact case M1 fixed |
| absent key / `None` | test fixture (`PF-absent`, `PF-null`) | gates — displays as `unrated` in the message (`severity or 'unrated'`), correct, this is the exact case M1 fixed |

**Result: the allow-list is closed.** Every token the doctrine actually instructs a reader to emit
for a panel finding's `severity` field is one of exactly six: `info, low, med, high, critical,
unrated`. Three pass, three (plus absent/null) gate — mathematically identical membership to the old
deny-list `{high, critical, unrated}` for this closed vocabulary. **No legitimately-emitted token
gates spuriously.** No `medium`/`severe`/`urgent`/`blocker`/`priority`/`n/a` appears anywhere as an
instructed value for this field; the one `medium` hit in the whole sweep is
`harness-handoff/SKILL.md:42`, which names it explicitly as the WRONG spelling in a misrouting
example, not a doctrine token.

**One adjacent risk, checked and found not to apply:** the "scope" reader is dispatched as the
`code-reviewer` persona (`teams/plan-panel.yaml:33`), whose *native* digest format
(`harness-code-reviewer.md:83`) uses `severity_max: info|low|med|high|critical|n/a` — a sibling field
with a 6th token, `n/a`, that the panel-finding vocabulary does not have. The wrapping prompt
overrides this for panel findings but does not explicitly warn the persona off its home habit. If
that cross-contamination ever happened — an LLM writing `severity: n/a` on an individual panel
finding — the OLD deny-list would have silently passed it (exactly the fail-open class M1 exists to
close); the NEW allow-list correctly gates it. This is the fix working as intended for this
scenario, not a new defect, and it is not proven to occur (no such value found in any fixture or
corpus file) — recorded as a decline that measured, not a finding.

## M7 (low, ui, carried forward) — reconfirmed open, unchanged

`check-state.sh:215`'s withhold message still states only the fact: `"finding {fid} is {severity or
'unrated'} and remains open without an operator overrule."` — no mention that resolving means a task
sets `disposition: resolved`, no mention of the stale-override rename mechanic in the doctrine prose
itself (that explanation lives only in the *stale-override* branch's own message, `check-state.sh
:203-205`, unchanged since c0). `git grep -n "disposition" .claude/commands/harness-plan.md
.claude/skills/harness/SKILL.md` still returns zero hits in either file. Confirmed via `git diff
d0ebbe6 c745d3a -- .claude/skills/harness/bin/check-state.sh`: the fix touched exactly two lines (the
allow-list flip and the message's severity-display fallback); the message's remedy content is
untouched. Non-gating (`low`), as at c0.

**One incidental improvement, worth recording though not requested:** the message's
`{severity or 'unrated'}` fallback is new in this fix and means an absent/null severity now prints
"is unrated" instead of the blank "is  and remains open" the old code would have rendered had it ever
reached this branch (it couldn't, on the old deny-list, which is exactly the bug). Not a fix for M7 —
still no remedy stated — but a small legibility gain on the fact half of the message.

## M4/M5/M6 — status confirmed via diff, not re-derived

`git diff --name-only d0ebbe6 c745d3a` (c0 pin → c1 pin) touches only `check-state.sh`,
`test-check-state.py`, and bookkeeping/notes files. **`panel_findings.py` (M4's site) and
`test-plan-panel.py` (M5's site) are absent from that list — untouched, unchanged.** `check-state.sh`
was touched, but only at the two lines shown above; the `expected_readers = {"should-not-exist",
"scope", "goalcheck"}` line (M6's site, now at `:216`) is outside the diff hunk, unchanged. All three
remain open exactly as cycle 0 left them; none is this role's to re-litigate.

## Suite check (supporting evidence, not the primary claim)

`python3 .claude/skills/harness/bin/test-check-state.py` at the pin: exit 0, tail shows `ok - INV-32
plan panel fixtures, including inv32-red` and `ok - INV-32 unrated severities fail closed` — no
`FAIL` lines. Corroborates the orchestrator's RED-capability claim without restating its own
measurement.

## Accessibility / theme parity

Not applicable — unchanged from c0: every touched surface is plain text/YAML/shell stdout, no colour
encoding, no ANSI, no rendered surface for a human to misread differently than the source shows.

## Verdict basis

`must_fix: []`. `severity_max: low` (M7, carried forward, non-gating) — below the `>= high` gate. The
primary hunt returned a closed, safe allow-list: no spurious-gate finding to file. `VERDICT: PASS`.
