# Grilling — issue #262, the factory's station board — 2026-08-11

## Destination

A factory run against any declared repository reads **that repository's own board**, moves its
station, and the move is verified on the board. The fleet stops assuming one board serves every
member, so adding a third repo needs no rework.

## Settled

- **The board becomes per-repository in the fleet schema.** Each entry under `repos:` carries its
  own board — number and stations — rather than inheriting one `board:` block. The one-board
  assumption is the actual defect: retargeting `board.number` to 2 would fix kaya and re-open the
  same hole the moment a second product repo joins. The operator chose the schema change over the
  one-line retarget deliberately, knowing it costs more now.

- **Kaya's board keeps its meaning; the factory's vocabulary is added to it, not imposed on it.**
  Rename `Todo → Ready` and `In Progress → Building`. **Leave `Done` alone and ADD `Review` as a
  fourth option.** The board ends with four.

  This reverses the operator's first answer, which was to rename all three, and the reversal was
  driven by a measurement rather than an opinion: **118 of kaya's 211 issues are `Done`.** Renaming
  that option would relabel 118 finished issues as "Review" — false about every one of them — and
  leave kaya with no Done column at all. Renaming in Projects v2 does not move items: they keep
  their option id and the label changes, so the 118 would have silently acquired a wrong status.

- **The end state for those 118 is ASSERTED, not left implicit** (operator, 2026-08-11): kaya's
  board ends with a `Done` column, and **all 118 finished issues sit in it, none in `Review`**.

  Keeping the `Done` option rather than renaming it delivers this at **zero item writes** — the 118
  never move, they keep their option id and their label. The alternative reading of the same
  instruction, rename all three and then migrate 118 items back out of `Review` into a freshly
  created `Done`, reaches an identical end state through 118 board mutations and a window in which
  the board is wrong. Do not implement that. **What the operator asked for is the OUTCOME, and the
  cheap route to it is a criterion rather than a task.**

  So this becomes a success criterion with a real measurement: after the change, a read of board 2
  reports **118 in `Done` and 0 in `Review`**, and the count is taken off the board rather than
  inferred from the absence of a migration step. It is also the assertion that catches the wrong
  implementation: if someone does rename all three, this criterion fails and says so.

- **Done means a LIVE factory run against a real kaya-ai issue**, reaching the board and moving its
  station, with the move **read back off the board** rather than inferred from exit 0. A config
  assertion alone was offered and declined: it proves the config is self-consistent, which is not
  the thing that is broken. The smoke fixture (board 6, `factory-smoke-a1`) was also offered and
  declined — it proves the machinery, not kaya's specific board.

- **`harness.json`'s `github.repo` is NOT in scope.** It still names `mruangutai/harness` for the
  issue mirror. That is a different mechanism from the factory station board. Changing one does not
  settle the other, and this effort touches only the factory side.

## Not yet specified

- Whether the per-repo board block is required on every entry or falls back to a fleet-level default
  when absent. A default is friendlier and is also how the current bug got in.
- Whether `stations:` moves per-repo alongside the board number, or stays fleet-level. Kaya needs
  its own mapping, so probably per-repo — but that is pm's call against the readers.
- Which kaya issue the live run uses, and whether it is a throwaway created for the purpose or a
  real one with the station restored afterwards. Note it must NOT be one of the 118 — the live run
  moves a station, and moving a finished issue would break the criterion above.
- How the board/repo pairing is asserted so the two cannot drift apart silently again. The ticket
  suggests `test-no-distribution.py` or a sibling; the natural home may be `check-state.sh`.

## Out of scope

- Moving kaya's issues onto board 3, and moving harness's onto board 2. Both were offered and
  declined: one board for two products mixes the work and collides the priority schemes (board 3 is
  P0/P1/P2, board 2 is Urgent/High/Medium/Low).
- Board 6 and `mruangutai/harness-factory-smoke-a1`. They are retained fixtures, not cleanup owed.
- Re-adding `mruangutai/harness` to `repos:`. Its absence is DEC-174 am.1 and is asserted by
  `test-no-distribution.py`.

## Facts I verified (so pm does not re-derive them)

Measured 2026-08-11 at `e057525`.

- **The ticket's headline number is wrong; its direction is right.** Board 3 holds **204 items, all
  `mruangutai/harness`, zero kaya-ai** — not the 30 the ticket states. The claim that a factory run
  against kaya finds nothing on board 3 stands.
- Board 2 is `kaya-ai` and holds **211 items, all `mruangutai/kaya-ai`**.
- Three boards exist: `3 Harness`, `2 kaya-ai`, `6 factory-smoke-a1`.
- `.harness/factory/fleet.yaml` declares `board.number: 3` with `stations: ready→Ready,
  building→Building, review→Review`, and `repos:` holds `mruangutai/kaya-ai` alone.
- **Board 2's `Status` field offers `Todo`, `In Progress`, `Done` — none of the three stations.**
  This is the fact the ticket omits, and it is why "retarget to board 2" was never a one-line
  change.
- Status distribution on board 2: **118 Done, 82 Todo, 11 In Progress.**
- Board 2 also carries a `Priority` field with `Urgent / High / Medium / Low`, which does not match
  board 3's `P0 / P1 / P2`.
- **A mismatched retarget fails LOUDLY, not silently.** `factory_claim.py:214-220` reads the board's
  real field options via `factory_gh.project_field_options` and errors with "field 'Status' on
  mruangutai project 2 does not offer it". Verified at source. Nothing here can fail open.
- `factory_config.station(fleet, key)` (`:158`) reads `fleet["board"]["stations"]` — a single
  fleet-level block. This is the line the per-repo change has to move.
- `factory_config.load_fleet` validates `board.owner`, `board.number`, `board.station_field` and
  `board.stations` as required keys. A per-repo board needs its validation moved or duplicated
  there, and `load_fleet` is the one place fleet shape is enforced.
