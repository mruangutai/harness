# FEAT-45 plan revision c2 — model claim restored, persona repinned, absence handled

**BLUF.** The plan is revised and internally consistent. The independent-MODEL claim is restored
(REQ-02, REQ-05, D-04); the reader persona is repinned from `general-purpose` to `fable-advisor`
because only a self-pinning persona can keep that claim (D-14); absent-persona behaviour is now a
requirement (REQ-14), a criterion (SC-17) and five extended tasks. No new task, no new lane row.
Both approval fragments still read `pending`. `review_sha` untouched at `1d3e5db` (`feature.json`
field `review_sha`).

## The measurement that forced all of it

`general-purpose` is a platform built-in with **no agent-definition file anywhere**, therefore no
`model:` pin. A model claim resting on it would be false the moment it was written. The dispatch
guard blocks a lead from *passing* `model:` and does **not** strip the target's own frontmatter pin,
and it exits 0 recording no claim for any persona not prefixed `harness-`. So the claim is
deliverable — but only by a persona that self-pins. `~/.omp/agent/agents/fable-advisor.md` carries
`model: anthropic/claude-fable-5`, `tools: [read, glob, grep, bash]`, and a read-only
second-opinion description whose stated job is hunting work that should not be done at all
(verified 2026-08-30). `.omp/agents/` holds exactly 16 `harness-*.md` files and `fable-advisor` is
not among them, so SC-06's census and SC-14's non-harness requirement both survive.

## The consequence nobody had named

That definition lives in the operator's HOME. The team file ships as doctrine (D-09) to every
project the factory is pointed at, where it may not exist at all. So the panel must skip the reader
and record the skip — and a recorded skip must be distinguishable from a reader that ran and found
nothing, because **both contribute zero `findings` entries**. `findings` alone cannot tell them
apart, which is why the record needed a new key rather than a new comment.

Design: `panel.readers`, one entry per reader, `status: ran | skipped`, plus `persona` and `reason`
required on a skip. INV-32 gains **check 5**: a missing reader or a malformed status is `bad` with
the literal words `never ran`; a properly recorded skip is `warn` — visible at the signature, never
silent, and never a hard failure, because hard-failing an absent persona would break the gate in
every project that lacks it, the opposite of what REQ-14 asks.

## Where it landed — EXTENDED, five tasks, no new task

| Task | Slice of REQ-14 | File |
|---|---|---|
| T-02 | team file states the rule as shipped doctrine | `teams/plan-panel.yaml` |
| T-05 | `panel.readers` shape in the template + pm's transcription duty | `templates/plan.yaml`, `harness-spec-driven/SKILL.md` |
| T-06 | the lead's skip-and-record obligation (third refusal) | `.omp/agents/harness-validator-lead.md` |
| T-07 | INV-32 check 5, the falsifier | `check-state.sh` |
| T-08 | cases `reader-missing` / `reader-skipped`, and the existing mutant extended to the second fixture | `test-check-state.py` |

A T-12 was rejected deliberately: its `files:` would have overlapped four tasks that already own
those paths, and `depends_on` is this plan's only serializer (T-10's own comment records that trap).

## Persona propagation — every site

`plan.yaml` D-14 (choice + because), T-02 intent + verify, T-03 intent (**it carried the struck
"not of the model" claim — not on the dispatch list, found by sweep**), T-06 verify + intent, T-11
verify + intent; `BRIEF.md` SC-15 and `## Constraints`. T-10's verify token list **dropped** the
persona name instead of swapping it: case 8 reads the persona from the team file, so demanding a
hardcoded name contradicted the case. It now greps `spawns` and `SPAWNS` — the mechanism, not the
data.

Preserved as evidence about the HOST rather than about our pin: the `Cannot spawn 'general-purpose'.
Allowed: ...` refusal quote (D-14, T-02, T-06, BRIEF REQ-02, BRIEF SC-15) and the `## Constraints`
platform-built-ins bullet.

## Verification of this revision

- `yaml.safe_load` on `plan.yaml`: OK. 11 tasks, ids unchanged, `T-10` still last.
- REQ traceability both directions: 14 brief REQs, 14 traced, zero orphans either way.
- `bash -n` on all 11 `verify:` blocks: 0 failures. All embedded python one-liners and heredocs
  compile: 0 failures.
- `check-plan-routes.py <this plan>`: **exit 0, 0 violations**. The only two DEVIATION lines are
  T-07/T-08's DEC-174 carve-out, which Q4 confirmed — reported as deviations, not violations.
- `check-domain.sh --resolve` on all five extended surfaces: `teams/plan-panel.yaml`,
  `templates/plan.yaml`, `.omp/agents/harness-validator-lead.md` → `NOBODY`;
  `check-state.sh`, `test-check-state.py` → `harness-backend-dev harness-dev-ops`. Every one already
  has a `lanes.rows` entry with a matching reason. **No new surface, no new lane row.**
- `.omp/agents/` still 16 files; no advisor definition added anywhere.

## Confirmations (D)

- **REQ-01** stands byte-unchanged. It already states the re-plan scope flatly, not as a derivation,
  so ratification required no hardening.
- **D-09** reads `.claude/skills/harness/teams/plan-panel.yaml` — matches Q3 exactly.
- **T-07/T-08** `execution_reason` reads as a deliberate DEC-174 carve-out; the checker agrees.

## Open for the operator

One question, non-blocking, in the DIGEST: whether pinning a persona defined only in the operator's
HOME is acceptable as shipped doctrine, given the plan now handles its absence by recording a skip
rather than by failing. SC-16 remains the only thing that can settle live resolution.
