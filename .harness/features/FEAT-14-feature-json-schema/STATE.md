# STATE

## Current

- feature: FEAT-14-feature-json-schema · phase **validate** · status Review
- branch `feat/204-feature-json-schema` · HEAD `62e3f72` · `review_sha` pinned `3abaedd`
- cycles_used **4** of 10 · runs **19 of an informational 20**
- **All twelve tasks done. Validate is COMPLETE and the feature is NOT shippable.**
- briefing: `notes/ship-review-2026-08-12-validate.md` (+ rendered `.html`)

| gate | result |
|---|---|
| qa gate (`test_matrix`) | **FAIL** — `matrix_ok: true`, one HIGH must_fix |
| review panel | **FAIL** — one HIGH, one MED; security clean |
| goal-check | **FAIL** — 12/18 met, 3 unmet, 3 operator-owed |
| all four project gates | green: validator rc 0 · routes 0/10 · check-state rc 0 · unit suite rc 0 |

### Three fixes stand between here and shippable — two are the main session's

1. **HIGH, carve-out.** `check-domain.sh:891-897` catches only `except ImportError:`; `SyntaxError`
   is not one, so a syntax-broken `feature_schema.py` escapes and `:14` makes exit 1 non-blocking —
   the bad write lands. The block's own comment at `:873-877` names that case and states the
   consequence; `:529-532` already fixed the class with `except Exception:`. The call sits inside the
   same `try`, so *any* exception escapes. **Verified by me at source.**
2. **HIGH, carve-out.** SC-04/05/16 declare `verify: automated`; `test-check-domain.py` has **zero**
   schema-rejection fixtures. **Fix 1 BEFORE 2** — fixtures written first would pin the fail-open as
   expected behaviour.
3. **MED, ordinary fix cycle.** `gh-sync.py:308-310` writes `feature.json` with a truncating
   `open()`; sibling `factory_decompose.py:174-180` keeps `mkstemp`+`fsync`+`os.replace`. A crash
   leaves a zero-byte file that reads as "nothing is mirrored" and the next sync **re-files GitHub
   issues** — external, irreversible. `factory_decompose.py:149-151`, marked "carried forward by
   FEAT-14 T-05", claims an atomicity now false of this file.

**The two HIGHs compound:** a fail-open just shipped in the enforcement path, and that path is the
one surface with no standing assertion.

### Operator-owed, legwork done — none may be marked met by any agent

- **SC-10** — open `FEAT-11-graphql-field-resolve/notes/receipt-feature-key-drop.md`. pm swept all 17:
  zero unrecorded drops, 17 receipts, none left over. BRIEF's parenthetical is wrong twice (22 not
  20; FEAT-12/13 each dropped 23).
- **SC-11** — pm recommends MET; residual is `factory.issues`/`factory.items` bare `{type: object}`
  at `feature-schema.json:96-97` where `github.issues` constrains to integer.
- **SC-15** — script ready at `notes/uat-FEAT-14-sc15-readability.md`. No corpus file carries eleven
  keys; `factory` is in zero of 17, so ten is the real maximum.

### Two runs were interrupted; one left a live mutant

`MUTANT-PROBE` was spliced into `DEC-192`'s row in `DECISIONS-INDEX.md` and never restored, while its
digest reported nothing outside the run dir had changed — DEC-131's orphaned-child behaviour. I
restored it and verified byte-identity. Committing it would have corrupted the index this feature
just built. The panel's first attempt lost two of three reviewers to permission rejections; the
retry ran both and produced the HIGH above.

## Open Questions

- Q1 **BLOCKING, main session**: fixes 1 and 2 above, in that order. Both DEC-174 carve-outs.
- Q2 non-blocking: B-1, the `gh-sync.py` atomicity gap — an ordinary fix cycle, not a carve-out.
- Q3 non-blocking: plan-authorship remedy — extend `check-plan-routes.py` with `verify_red_at`
  (a verify already green at signature FAILS) plus an intent cross-grep of every literal a verify
  forbids. Not a carve-out, so dispatchable. Catches three of the eight defects with text alone.
- Q4 non-blocking: SC-14's index check is blind to a corrupted **ruling clause** — prose round-trips
  verbatim, only structural fields regenerate. Proven live. Record as a known limit, or commission a
  prose-integrity check.
- Q5 non-blocking: `tests.yml`'s `Unit suite` step is the sole runner for eight criteria and nothing
  asserts it; the `case 25` guard its comment claims does not exist (inherited, `eafc8ad`).
- Q6 non-blocking: `gh-sync.py` reads `feature.json` with the YAML loader (`:257`, `:300`) while
  `factory_decompose.py` uses `json.load` (`:155`). Latent — the write gate and CI reject divergence.
- Q7 non-blocking: citation drift, **two** edits — `plan.yaml:158` D-04 → DEC-190, `:261` D-08 →
  DEC-191. DEC-192 was never pre-committed. Operator's edit, ruled a finding not a silent fix.
- Q8 non-blocking: three stale BRIEF lines — `:421` "exits 1 today" (exits 0, zero-byte baseline),
  SC-13's "exactly two carve-outs" (five under R-01), SC-10's key counts.
- Q9 non-blocking: SC-02 has no failing fixture for `factory` / `factory.edges` (G1). Code rejects
  both correctly; the criterion under-specifies.
- Q10 non-blocking: `harness.json`'s integration `detect` glob names 2 of the 12 scripts its `cmd`
  runs — kind membership really comes from `run-unit-tests.sh`'s arrays.
- Q11 non-blocking: the write guard denies paths containing an **unexpanded shell variable**; the
  out-of-repo escape itself works. False positive. FEAT-17's.
- Q12 non-blocking: `check-plan-routes.py:558` says FEAT-08 "is `awaiting_user`" in present tense;
  it reads `Review`.
- Q13 non-blocking: `SPEC.md:1612` was rewritten in T-09 beyond its intent — the old text instructed
  writing `in_progress`/`abandoned`, both rejected by this feature's schema. pm recommends KEEP.
- Q14 non-blocking: close-out (ship-refresh, distillation) has NOT run — it is a feature-close step
  and the SCs have not all passed. A stray probe worktree from the qa run remains registered.
