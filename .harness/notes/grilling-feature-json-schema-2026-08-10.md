# Grilling — issue #204, feature.yaml becomes feature.json with an enforced schema — 2026-08-10

## Destination

Execution state has a closed, machine-checked key set. An agent that invents a key fails
immediately, and the prose it wanted to write has a named destination it is redirected to rather
than a hard stop with nowhere to go.

## Settled

- **BUILD WAITS until FEAT-12 and FEAT-13 are idle.** Planning now is safe; building is not. The
  ticket blocked itself on FEAT-10 for exactly this reason — a running orchestrator writes
  `feature.yaml` live — and the same condition holds again: FEAT-12 is mid-build and FEAT-13 is
  mid-plan, both writing that file. Converting the format under a live writer produces a
  half-migrated file no reader understands. The build starts when both have reached a signature or a
  ship.

- **`jsonschema` becomes a real dependency, with its own decision entry.** Chosen over a hand-rolled
  stdlib checker and over the cheaper closed-key-set alternative. The precedent and the shape are
  DEC-171's for PyYAML: the schema stays a declarative artifact other tooling can consume, and a
  missing import is a LOUD failure, not a silent skip. The hand-rolled option was declined because a
  checker and a schema that can disagree is the two-copies drift this org keeps finding.

- **NO new `notes:` field. Prose goes to the homes that already exist, and the schema names the
  destination per class.** The point is redirection, not just refusal:

  | What an agent wants to record | Where it goes |
  |---|---|
  | An operator ruling | `plan.yaml` `approval.rulings` |
  | Run narrative, findings, corrections | that run's digest |
  | Current state, open questions | `STATE.md` |
  | Measurements, research, receipts | `notes/` |

  A typed `notes:` array was offered and declined: it becomes the drawer everything is swept into,
  and it would leave `feature.yaml` a narrative file with a schema blessing it.

- **The schema STARTS at SPEC §11.3's ten keys, `additionalProperties: false`, and the burden of
  proof is on KEEPING a field.** Every addition beyond the ten needs pm to name a real reader — file
  and line, a call site that actually consumes the value — not a name that happens to appear
  somewhere. **The 41 keys measured as unread (below) die without further argument.** This is the
  ruling that reverses ten features of growth: a field survives because something reads it, not
  because removing it feels lossy.

## Not yet specified

- **Which of the ~34 not-provably-unread keys have a REAL reader.** My measurement's negative half
  is sound; its positive half is not (see the caveat in `## Facts`). pm re-checks each survivor with
  a real call-site check and proposes only those that pass. Likely genuine, still to be proven:
  `github` (the mirror block), `tasks`, `mission`, `effort`, `briefing`, `phase`.
- The migration mechanism for in-flight features, and whether a one-shot converter is worth writing
  for twelve files.
- Whether `check-state.sh` INV-18 and `SKILL.md:23` are corrected by shipping the missing template,
  or by rewording, or both.

## Out of scope

- **`state.yaml`.** It already has a closed key set (`check-state.sh:548` `CHECKPOINT_KEYS`,
  reported at `:629`, DEC-154) and is not part of this change.
- **Re-opening YAML versus JSON.** The operator decided JSON on 2026-08-09 and reaffirmed it here.
  The ticket records the cheaper alternative and why it lost; do not rediscover it.
- **`check-docs.sh`, named in the ticket's step 7.** It no longer exists — struck under #202. That
  step is dead and must not be planned.

## Facts I verified (so pm does not re-derive them)

Measured 2026-08-10 at `3569a20`.

- **The growth did not stop, and the ticket's numbers are stale.** Top-level key counts today:
  FEAT-01 10, FEAT-02 12, FEAT-03 15, FEAT-04 18, FEAT-05 15, FEAT-06 19, FEAT-07 21, FEAT-08 20,
  FEAT-09 25, **FEAT-10 29** (the ticket says 34 — it was trimmed since), **FEAT-11 32**,
  **FEAT-12 26**.
- **FEAT-11 is the strongest evidence in the tree.** It carries all ten SPEC §11.3 keys **plus 22
  more**, on a ONE-TASK feature planned and shipped in a single day: `mission`, `effort`,
  `briefing`, `review_sha_note`, `review_sha_history`, `cycles_raise`, `cycles_note`, `counts`,
  `sc_result`, `tasks`, `tasks_note`, `route_resolution`, `peer_feature_collision`,
  `preflight_measurements`, `e1_ruling`, `sc01_ruling`, `mf1_correction`, `gate_status`,
  `runs_note`, `residuals`, `operator_rulings_2026_08_10`, `github`.
- **Three of those the MAIN SESSION added today**, including `operator_rulings_2026_08_10` — a
  date-stamped key, unrepeatable, that no schema could declare and no reader will look for. Its
  content was **already** in `plan.yaml`'s `approval.rulings`; it is a duplicate. Recorded because
  it makes the case better than the ticket's own list does: this is not an agent-only failure mode.
- `jsonschema` is **not installed** — `import jsonschema` raises at `3569a20`.
- `.claude/skills/harness/bin/check-docs.sh` **does not exist**.
- `.claude/skills/harness/templates/` contains **no** `feature.yaml` or `feature.json` template,
  while `check-state.sh` INV-18 and `.claude/skills/harness/SKILL.md:23` both instruct the reader to
  instantiate one from a template. Both instructions point at nothing.
- SPEC §11.3 (`docs/harness/SPEC.md:1742`) is normative prose declaring ten keys, enforced only by a
  human noticing.
- **There are 75 distinct top-level keys across the twelve features, not 34.** The ticket counted one
  feature's file; this is the union.
- **41 of the 75 appear NOWHERE outside a feature directory** — not in `.claude/`, `docs/`,
  `.github/`, `team-config.yaml` or `harness.json`. Nothing can read them. Among them are BOTH keys
  the ticket singled out as looking like real state — `gate_status` and `sc_tally` — plus
  `operator_rulings_2026_08_10`, `d06_reversal`, `kaya_measurements`, `verified_by_me`,
  `this_session`, `trigger_gap`, `skipped_segments`, `must_fix_open`, `must_fix_resolved`,
  `panel_result`, `pre_ship_steps`, `build_lanes`, `lane_split` and `approval_gate`.

  **CAVEAT, and pm must not skip it: the NEGATIVE half of that measurement is sound, the POSITIVE
  half is NOT.** It was a plain substring search on the key name, so a match proves only that the
  string occurs — `pr` matched 118 files, `shipped` 37, `approved` 30, all ordinary English words.
  A key that appears nowhere is certainly unread; a key that appears somewhere is NOT thereby read.
  Every survivor needs a real call-site check before it enters the schema.
