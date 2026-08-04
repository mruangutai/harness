# Grilling — the team-definition layer and INV-6's truthy hole — 2026-08-04

## Destination

The team layer is machine-readable and complete — a `build` team exists, `review` runs the
blocking gate, both files parse — and INV-6 stops accepting a placeholder as a pinned SHA.
Issues **#8**, **#9** and **#16** close as a consequence.

## Settled

- **#16 — INV-6 accepts `review_sha: none` as pinned.** Reproduced: a fixture with a validator
  run and `review_sha: none` produces **no** INV-6 violation. `val()` returns `str(v)`, so the
  literal string `"none"` is truthy and only an ABSENT key trips the check. **Reuse the existing
  placeholder vocabulary** at `validate-digest.py:472` — `("none", "null", "n/a")` — rather than
  inventing a second one. Only two `val()` consumers exist; the other (`cycles_used`) is already
  guarded by `.isdigit()`.
- **#8 — add the qa step to `review.yaml`.** The user chose the direct fix over an invariant or a
  runner change. QA is the project's only blocking gate, and FEAT-03's lead added the step by hand
  at run 12 (`feature.yaml:62`, "panel + added qa step") — so the shape that works is on disk.
- **#9 — write `build.yaml` AND retire the hand-written step lists.** Derive it from what
  demonstrably shipped: FEAT-03's four build runs and FEAT-05's. Then update the orchestrator
  playbook so it dispatches the named team instead of composing steps inline. The user chose the
  larger scope deliberately; note it touches how builds are dispatched at all.
- **Both team files get their templates quoted, and the validity gate is widened to cover
  `.claude/skills/harness/teams/`.** Quoting means wrapping the path in `"` so YAML reads
  `{{feat}}` as text rather than the start of an inline object. The value is byte-identical; only
  the parser's reading of it changes.
- **Budget: $120**, the default, unraised. Much smaller than FEAT-05 — one invariant, two YAML
  files, one new team file, one gate widening. No new module, no hook conversion.

## Not yet specified

- **What `build.yaml`'s steps actually are.** Five real build runs are on disk as evidence, but
  whether they generalise — or whether FEAT-05's main-session build (DEC-174) is even a valid
  input, since it had no members — is pm's call from the run records, not mine to pre-decide.
- **Which playbook text changes when the hand-written lists retire.** `harness/SKILL.md` composes
  build dispatches today; the edit's shape depends on what `build.yaml` ends up declaring.
- **Whether `gate-probe.yaml` is still wanted at all.** It is invalid YAML and nothing references
  it outside its own directory. Fixing it and deleting it are both defensible; nobody has asked.

## Out of scope

- **#10** (`change_type` lacks `logic`) — ranked separately, one-line vocabulary fix, no shared
  cause with these three.
- **#7, #13, #14, #6** — unrelated to the team layer.
- **Making the runner parse team files.** They are read as prose by a lead agent today, and
  changing that is a design question this feature does not need to answer.
- **`bash-write-guard.sh`'s `FOO=bar python3 - <<'PY'` false positive** — real, found by a FEAT-05
  review pass, still unticketed. Different surface.

## Facts I verified (so pm does not re-derive them)

All at `61d5d44`, `main`, four gates green.

- **#16 REPRODUCED.** Fixture with `review_sha: none` + one `squad: validator` run → zero INV-6
  violations from `check-state.sh`. The defect is live, at `check-state.sh:156`.
- **#8 and #9 are ONE original finding, split into two tickets.** FEAT-03's ship review,
  `notes/ship-review-2026-07-31-16.md:198`, records them together as **B-7**: *"No `build` team
  definition exists… And the `review` team omits the QA step… I added the step by hand. Both reach
  every future feature."* Planning them together is returning them to their original shape.
- **`build.yaml` DOES NOT EXIST.** `.claude/skills/harness/teams/` contains exactly
  `review.yaml` and `gate-probe.yaml`.
- **BOTH team files fail `yaml.safe_load`** — unquoted `{{feat}}` inside a `[...]` flow sequence,
  the same shape that made `team-config.yaml` unreadable past line 23 for weeks.
- **BUT NO SCRIPT PARSES THEM.** `grep` over `bin/` returns nothing; `harness-team/SKILL.md:31`
  has a lead agent RESOLVE and read them as prose. An LLM handles `{{feat}}` fine. **So they work
  today** — this is a trap for whenever something machine-reads them, not a live outage. I told the
  user the opposite before checking, and corrected it.
- **The validity gate cannot see them.** `test-harness-yaml-corpus.py` scans `.harness/**` only;
  `.claude/skills/harness/teams/` is outside its glob.
- **The placeholder vocabulary #16 should reuse already exists** at `validate-digest.py:472`.

## The through-line worth stating in the BRIEF

All four defects are **a definition or check that appears to exist but does nothing**: an invariant
that passes on a placeholder, a team file missing its blocking step, a team that was never defined,
and two files whose extension promises a machine can read them when it cannot. That is the same
class FEAT-05 spent a day on, and DEC-174 exists because of it.
