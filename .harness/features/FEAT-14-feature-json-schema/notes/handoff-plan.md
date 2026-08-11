# Handoff — FEAT-14, plan → build — written at a29ad06, seq-3 (supersedes seq-2)

## Next

Do NOT dispatch T-01 on arrival. First confirm **FEAT-16 and FEAT-17 have both returned for
signature** — both were `in_progress` and writing `feature.yaml` live at `a29ad06` — plus any flow
started since. Then dispatch T-01 (schema artifact, `bin/feature_schema.py`, unit tests) to
eng-lead. **T-02, T-04, T-06, T-07, T-08, T-12 are `main-session-direct`**: written, never
dispatched. T-11 and T-12 are new in the 2026-08-11 revision; do not reorder T-12 behind the
migration it protects.

## Trust

- The plan was REVISED 2026-08-11 and is a different plan: `phase` deleted, one `status` on the
  board's six capitalized columns, 12 tasks / 13 decisions / 18 SCs, 8 required of ELEVEN keys —
  `notes/answers-2026-08-11-revision.md`, `safe_load` — verified-at a29ad06
- Deleting `phase` kills TWO required gates unless T-11 and T-12 land: `check-plan-routes.py:386`
  matches nothing and route-checks every finished feature forever; `check-state.sh:451`
  `if _phase not in PHASE_ORDER: continue` sees `""` for all 17 — verified-at a29ad06
- A dead INV-17 exits 0, so "check-state.sh passes" is NOT evidence T-12 worked. SC-18's two
  opposite-direction assertions are — `BRIEF.md` SC-18 — verified-at a29ad06
- Handoff stems stay lowercase literals, never derived from capitalized status values: a derived
  `handoff-Build.md` passes here and fails on Linux CI — `plan.yaml` D-12 — verified-at a29ad06
- The corpus is **17**, all carrying a feature.yaml, and it MUTATES mid-session — verified-at
  a29ad06. T-04/T-08 resolve the set by GLOB; their `files:` are glob + one literal anchor by
  NECESSITY, since 17 literals measure 54 machine-field lines against DEC-182's 50 cap and
  check-plan-routes REJECTS them — `notes/research-plan-revision-2026-08-11.md`
- Route-check baseline **0 violations across 12 plans**; with the skip tuple emptied — the state T-04
  leaves it in — 35 across 16. Keep that window inside one PR. Post-migration expected set is **11
  plans, 0 violations**; FEAT-09 (`shipping` → `Review`) STAYS checked — verified-at a29ad06
- `jsonschema` **4.26.0 IS installed** — verified-at a29ad06. The seq-2 note said otherwise; void.
- A validator that cannot LAUNCH and exits 1 fails OPEN; only exit 2 blocks — `check-domain.sh:14`
  — verified-at a29ad06
- gh-sync MUST NOT run between T-04 and T-08: it hardcodes feature.yaml and returns the EMPTY record
  on absence, re-filing existing issues — `bin/gh-sync.py:247,255-256` — verified-at 96d5d5c.
  External damage, NOT undone by `git reset`.
- T-05→T-08 is the dangerous window, not T-06→T-08 — `runs/2026-08-10-02-eng/digest.md` MF-4
- `.harness/team-config.yaml:15-16` is FALSE — `check-domain.sh:256` sets a flag — verified-at
  96d5d5c. It misled a lead once; do not reason from it.

## Dead ends

- Do not reopen YAML-vs-JSON, the enforcement point, or the key set — operator-settled —
  `notes/research-FEAT-14-reader-census.md` — verified-at 96d5d5c
- Do not resurrect `phase`, and build NO status mapping table in code, schema or fixture — the old
  values are migration INPUT only — `plan.yaml` D-09 — verified-at a29ad06
- Do not collapse `validate-digest.py:182`'s digest enum — out of scope by D-13; it carries
  `blocked` and the six columns have no `Blocked` — verified-at a29ad06
- Do not build a dual-read transition — the rot DEC-171 am.1 removed the fallback to avoid —
  `runs/2026-08-10-02-eng/digest.md`
- Do not import jsonschema at module level — +42.6 ms measured; deferred into the `feature.json`
  branch — `plan.yaml` D-03
- Do not plan board mutations — both boards carry the six columns — `notes/answers-2026-08-11-revision.md`

## Working set

- .harness/features/FEAT-14-feature-json-schema/plan.yaml
- .harness/features/FEAT-14-feature-json-schema/BRIEF.md
- .harness/features/FEAT-14-feature-json-schema/notes/answers-2026-08-11-revision.md
- .harness/features/FEAT-14-feature-json-schema/notes/research-plan-revision-2026-08-11.md

---

## Batch A execution notes — main session, 2026-08-11

**gh-sync ran BEFORE T-04, on the operator's ruling.** 12 sub-issues #264-#275 under #204,
`parent_origin: adopted`, milestone 8. The #252 defect — creating a parent instead of adopting one —
did NOT recur, but only because `--parent 204` was passed explicitly. The bug is dormant, not fixed.

**T-02 defect: its intent and its verify contradict each other.** The intent mandates the combined
command `python3 -m pip install pyyaml jsonschema`; the verify greps the literal substring
`install jsonschema`, which the combined form does not contain. **Written exactly as the signed
intent specifies, T-02 fails its own signed verify.**

Resolved without weakening the intent: the gate stays ONE gate, the combined command stays, and a
genuinely useful extra line was added (only one package missing -> install just that one) which
also carries the literal. This is eng-lead's G-04 shape — when a verify greps a literal string, the
work must carry that string even where the prose form reads better.

Backlog candidate, not this feature's to fix: a `verify:` whose literal cannot be produced by its
own `intent:` is undetectable at plan time. `check-plan-routes.py` checks routing and budget, not
whether a task's two halves agree.

**T-02 result:** verify exit 0. Two probe lines, ONE STOP gate covering both packages. CLAUDE.md at
75 lines against its 80 budget; the shape gate accepts it at exit 0.
