# Code review — FEAT-01, `a606d7a..9b07cfc`

**FAIL.** The change under review exists to stop a lead masking a member `FAIL` (DEC-123). It does
that only for canonically-formatted digests. Four ordinary variations get a masked `FAIL` accepted
at `exit 0` in `--hook` mode. One blocking item; everything else is a note.

`human_commits_in_scope: []` — verified, `git log --grep='harness:human' a606d7a..9b07cfc` empty.
All repros run against `git show 9b07cfc:.../validate-digest.py`, not the working tree.

## Stage 1 — spec compliance: PASSES, with 4 recorded mismatches

Every change traces to DEC-121 / DEC-122 / DEC-123 or to DEC-120 propagation. No scope creep found.
None of the below invalidates the quality pass, so Stage 2 proceeded.

| Kind | Path | Ref | What |
|---|---|---|---|
| mismatch | `.claude/skills/harness-team/SKILL.md` §e | DEC-122 | See F2 — the claim replaced a real fallback |
| mismatch | `docs/harness/SPEC.md` §8.3 | DEC-122 | See F3 — "must fix it before it can finish" is one rejection deep |
| omission | `validate-digest.py` `ALIAS`/`SCHEMAS` | SPEC §8 | `harness-orchestrator` is the 16th agent, matched by the `harness-.*` `SubagentStop` matcher, has no schema → the "no schema — passing through" branch. Unenforced the moment BUILD task 14 lands. Pre-range; `info` |
| mismatch | `docs/harness/SPEC.md` §8.1 | DEC-121 | pm's bullet omits `sc_status`, which the validator requires and `.claude/agents/harness-pm.md:75` emits. §8.1 is the stale surface. `info`, doc fix. Also §8.1 names `expertise_full` as universal; no template carries it and the validator ignores it — leave it |

Verified clean, do not re-litigate: `ALIAS` covers all 15 roster agents (SPEC §3.4); all three
normative templates (SPEC §10.4, `harness-team` "Reporting up", `harness-handoff`) pass when
placeholders are filled; DEC-121's `harness-handoff` "only if" contradiction is closed at this SHA;
the four `settings.json` entries are present in `templates/settings.snippet.json`; the shipped suite
is 16/16 green; the validator reads no transcript, so "missing transcript path" is N/A.

## Stage 2 — findings, ranked

### F1 — `high`, **BLOCKING**. The roll-up never asserts that `members` is real
`validate-digest.py:263` — `if persona == "lead" and isinstance(seen.get("members"), list)`. When
the parse yields an empty or truncated list, `worst` stays `None` and the check emits **silence**,
not a violation. `steps_run` sits three lines away and could cross-check it; nothing does. Four
repros, all `VERDICT: PASS` over a member at `verdict: FAIL`, all `digest ok` / hook `exit 0`:

1. **Quote-blind, first-match verdict regex** (`:268`). No unusual formatting at all —
   `- { step: qa, persona: qa, headline: "verdict: PASS on retry", verdict: FAIL }` → reports PASS.
2. **Multi-line inline list.** `members: [` + indented entries + `]` → `parse_scalar` takes
   `v[1:-1]` of the string `"["` → `[]`. Confirmed through `--hook`: `exit 0`.
3. **Unbalanced apostrophe** in an unquoted inline value (`didn't`) — `split_items:105` opens a
   quote that never closes, so `depth` never returns to 0 and both entries fuse into one; the first
   `verdict:` wins.
4. **`members: []` with `steps_run: 3`.** SPEC §10.4 calls the block "NOT optional"; a team that
   ran 3 steps and reported zero members is never legitimate, and it passes.

Consequence in each case: the orchestrator routes on `VERDICT`, never opens member entries (SPEC
§8), so the `FAIL` ships. This is the exact defect DEC-123 was written to close.

### F2 — `med`. The runner now asserts a guarantee that does not hold, and deleted the layer that covered it
`.claude/skills/harness-team/SKILL.md` step e. The diff removes the host-side
`validate-digest.py <persona>` call *and* the "the orchestrator validates on receipt" fallback, and
replaces them with "a member that returned to you at all has already been held to the schema:
**every field present**". False for every F1 repro, and for `stop_hook_active` (F3), absent
`agent_type` (F6) and unknown personas. The fallback that would have caught the residue was removed
in the same commit that asserts there is no residue.

### F3 — `med`. Enforcement is exactly one rejection deep
`validate-digest.py:340` returns 0 on `stop_hook_active`. An agent that ignores the stderr feedback
and re-emits the identical malformed digest is accepted on its second stop. SPEC §8.3 and DEC-122
both say "the agent must fix it before it can finish"; it does not have to. The pass-through itself
is correct (DEC-122 row 2) — the *claim* built on it is not. Residual: I verified the script's
branch, not that the platform sets the flag on the second `SubagentStop`.

### F4 — `med`. A trailing comment on the `DIGEST:` line reports every field missing
`parse_digest:161` requires `^\s*DIGEST:\s*$`, but the top-level presence check (`:222`) accepts
`DIGEST:` with anything after it. SPEC §8's own normative template is
`DIGEST:                             # routing — orchestrator reads THIS…`. An agent copying it gets
6 "missing field" errors naming fields that are visibly present. Same failure when an agent echoes
the contract template in a fenced block before its real return: the first `DIGEST:` wins, 11 bogus
errors. **This is not the stop-loop the brief assumes** — `stop_hook_active` caps it at one wasted
turn. The cost is that the feedback actively misdirects, so the agent cannot diagnose it.

### F5 — `med`. Standard YAML block-mapping member entries are rejected
`parse_digest:187` collects only lines starting `- `, discarding continuation lines. `- step: s1` /
`  verdict: PASS` on the next line → "a members entry has no verdict". Fails **closed**, which is
the right direction, so it costs a turn rather than correctness. SPEC §10.4's own `escalations`
example is written across three lines, so the shape is one agents will produce.

### F6 — `med`. Absent `agent_type` exits 0 **silently**
`validate-digest.py:333`. There is no way to distinguish "correctly declining to govern `Explore`"
from "the payload key was renamed and the hook is now a project-wide no-op". DEC-122 makes the
loudness of pass-throughs the property that matters, and this is the one that is mute. Same recorded
shape as DEC-110. One stderr line when a payload has no recognisable agent key would close it.

### The rest — `low` / `info`, non-blocking

| # | Sev | Where | Failure |
|---|---|---|---|
| F7 | low | `:225` | `headline` is matched anywhere in the text, at any depth. A lead digest with **no** top-level headline but a block-style member carrying `headline:` passes — verified. The orchestrator routes on headline |
| F8 | low | `test-validate-digest.py` | **Zero `--hook` coverage.** No case exercises `hook_mode`, its three pass-throughs, or `exit 2`. That is the only mode DEC-122 makes mandatory |
| F9 | low | same | DEC-123 says both templates are "extracted from the source files … run through the validator". No such test exists; the 16 cases are hand-copied lookalikes that will drift. Proof it already drifted: F10 |
| F10 | low | `harness-team/SKILL.md` "Reporting up" | `files_touched:` appears **twice** in the normative template. Passes the validator (last wins), so nothing catches it; a lead copying it emits a duplicate key |
| F11 | low | `test-validate-digest.py` enum case | `mentions="med"` is a substring of `"medium"`, which the error echoes from the input. The assertion passes even if the near-miss hint is deleted entirely — vacuous |
| F12 | low | `:191`+ | `str`-typed fields (`team`, `branch`, `blocked_on`) hit no type branch. `team: 7` passes; bare `branch:` parses to `[]` and passes, though DEC-121 requires the literal `none` |
| F13 | low | `:290` | The `open_questions`-is-a-count check still uses a whole-text regex, not `seen`. A nested `open_questions: 0` appearing *before* the top-level key produces a false positive on a valid digest — the same nesting bug `parse_digest` was written to fix, left in one place |
| F14 | low | `:373` | CLI mode crashes with `UnicodeEncodeError` under an ASCII locale (`LC_ALL=C`), truncating the reasons. Hook mode is safe (stderr is `backslashreplace`) |
| F15 | info | `:231` | The drift-spelling check iterates `schema` only, not `UNIVERSAL`, so `files-touched` is reported as merely missing rather than as drift. Fails closed |

## Open questions

- **Q1 (blocking):** F1 is a parser-robustness problem, and hardening a hand-rolled YAML subset is
  open-ended. Is taking a real YAML dependency for the digest block on the table, or is the
  files-only / no-dependency constraint (CLAUDE.md) binding here? That decides whether F1's fix is a
  patch or a rewrite. Not mine to decide.
