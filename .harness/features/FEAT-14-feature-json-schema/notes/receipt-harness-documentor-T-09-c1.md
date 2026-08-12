# Receipt — harness-documentor — T-09 — c1

**T-09 is done and its amended verify clause is green at exit 0, with all three of its
discriminating assertions proven able to fail.** Three decision entries written, SPEC §11.3 rewritten
around one lifecycle field, the tense-scoped rename applied. No commits — the operator holds the pen.

## DEC numbers actually taken

**DEC-190, DEC-191, DEC-192.** Re-confirmed at write time: highest entry was `## DEC-189`, gaps at 12
and 161 are isolated singles and not a run of three.

- **DEC-190** — `jsonschema` is a required dependency, and a missing import is a loud error.
  Declared where PyYAML is: `.claude/skills/harness-init/SKILL.md:47` (8th prerequisite, installs at
  `:61-65`) and `.github/workflows/tests.yml:59-60`. Verified on disk that this repo has **no**
  `requirements.txt` and **no** `pyproject.toml`, as the intent asserts.
- **DEC-191** — the closed key set: eleven keys, eight required, `additionalProperties: false` at the
  top level and inside `runs` items, `github`, `factory`.
- **DEC-192** — `phase` and `status` collapse into one field with the board's six column names.

## Citation drift — reported, deliberately NOT fixed (R-01/operator ruling)

`plan.yaml`'s `decisions:` both point at the wrong entries, each off by one:
`D-04 → dec: DEC-189` (now the write-guard entry) and `D-08 → dec: DEC-190` (now the jsonschema
entry). This is a finding for the goal-check, not a silent edit.

## SPEC §11.3 (`SPEC.md:1763`)

Eleven-key JSON sample, the eight required named, `.claude/skills/harness/bin/feature-schema.json`
named as the authority, one `status` field with the six board columns in a meaning table, both
collapses stated as costs, an explicit "there is NO `phase` field" sentence, case sensitivity with no
lowercase alias. No mapping table of the old values. **The sample was validated against the real
schema with `jsonschema.validate` before it went into the file** — it passes, 11 keys. ORCHESTRATOR
MISSION language (`SPEC.md:1446-1454`) and the DEC-157 cycle-budget paragraph are intact, the latter
changed only in filename.

## Stale prose found and fixed — `SPEC.md:1612`

The retry-exhaustion step said the feature's `status` stays `in_progress` and is **not** set to
`abandoned`. **Both values are rejected by the schema's enum**, so the sentence instructed a reader
to write an illegal file. Rewritten to preserve its actual point — the orchestrator does not close a
feature out — as "stays where it is … not advanced to `Done`". Same file, same field, inside T-09's
declared `files:`; flagged here rather than left standing.

## Rename — tense-scoped per R-01

Verified line by line; my reading matched the dispatch table exactly, including the three occurrences
on `BUILD.md:335`.

| file | before | after | note |
|---|---|---|---|
| `docs/harness/BUILD.md` | 11 occ / 8 lines | **3 occ / 3 lines** | 8 renamed; the `acb8db4` marker, the 2026-07-28 D3 marker and D7's "second feature's" all stay |
| `docs/harness/SPEC.md` | 14 | **0** | |
| `docs/harness/org.html` | 2 (`:166`, `:288`) | **0** | |
| `docs/harness/DECISIONS.md` | 52 occ / 50 lines | **52 occ / 50 lines** | unchanged; the three new entries introduce none |

Each of the three exempt anchors confirmed at **exactly 1** after the edit. `DECISIONS.md` is purely
additive (`+113 / -0`).

## Mutation proof — the assertions can fail

| # | Mutation | Assertion that fired | exit |
|---|---|---|---|
| M1 | `"phase": null,` into §11.3's JSON block | `SPEC 11.3 still declares a phase field` | 1 |
| M2 | `Backlog` removed from DEC-192's enum | `no single DEC- entry records all six board-column status values` | 1 |
| M3 | new `feature.yaml` line appended to BUILD.md | `BUILD.md names feature.yaml outside the three exempt dated records` | 1 |

M2 also proves no *other* single entry accidentally carries all six board words. M3 is the empirical
answer to R-01's design question: **the clause exempts three anchors by their literal text and then
scans the remainder, so a newly added reference is still caught** — a file-level exemption or an
occurrence-count check would have passed this mutant.

Restore after each was verified **byte-identical by SHA-256**, not by inspection. Green re-run after
all three: `OK`, exit 0.

## Not mine, seen and not chased

`check-plan-routes.py` / `check-state.sh` red closes at T-08. I did not run them and did not touch
`check-plan-routes.py`, `.harness/features/**` state files, or `DECISIONS-INDEX.md` (generated,
T-10's).
