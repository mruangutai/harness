# FEAT-14 — feature.json with an enforced schema — ship review

**Recommendation: DO NOT SHIP YET.** Three small fixes stand between here and shippable, and two of
them are yours to make directly. The feature works: all 17 execution-state files are converted,
every gate is green, and 12 of 18 success criteria are met. What is not yet true is that the thing
this feature exists to add — the write-time schema gate — is *protected*.

## What you would feel if this shipped as it stands

| | If it ships today | If the three fixes land first |
|---|---|---|
| Malformed `feature.json` | Blocked — **unless** `feature_schema.py` ever breaks, in which case it lands silently | Blocked, and blocked when the checker itself breaks |
| Someone deletes the schema check next month | Every gate stays green. Nothing notices | A test goes red |
| A crash mid-`gh-sync` | Zero-byte state file → next sync **re-creates GitHub issues that already exist** | Previous complete file survives |

None of these is theoretical-only: the middle row is exactly how this feature's own defects reached
review, and the first row is a defect that already shipped in this branch.

## The three things to fix

**1. The schema gate fails OPEN, and its own comment says it must not.** HIGH.
`check-domain.sh:891-897` catches only `except ImportError:`, but `SyntaxError` is not an
`ImportError` — so a syntax-broken `feature_schema.py` escapes uncaught, and `check-domain.sh:14`
records that exit 1 is **non-blocking**, so the bad write proceeds. The block's own comment at
`:873-877` names "a syntax error" among the cases it must absorb and spells out this exact
consequence. The same file already fixed this class at `:529-532` with `except Exception:` under the
stated rule *"a shape question is never answered by a crash"*. The call to `problems_for_text` sits
inside the same `try`, so *any* exception escapes, not just the import.

**Yours — `check-domain.sh` is a DEC-174 carve-out.** Widen to `except Exception:`, **and give the
runtime-crash case its own message** — the current handler text says "feature_schema is not
importable", which would be wrong for a `problems_for_text` crash.

*Confidence is unusually high here:* **two independent code-review spawns found this same line
independently**, one falsification-backed live, and I confirmed every element myself — including that
`issubclass(SyntaxError, ImportError)` is `False`.

**2. The gate has no standing test at all.** HIGH. SC-04, SC-05 and SC-16 declare
`verify: automated`; `test-check-domain.py` carries **zero** schema-rejection fixtures. The three
criteria are true today only by one-off probes that left nothing anyone can re-run. **Yours — same
carve-out.** Order matters: **fix 1 first**, or the new fixtures will pin the fail-open as expected
behaviour.

**3. `gh-sync.py` writes the state file non-atomically.** MED, and the only one that is an ordinary
fix cycle. `gh-sync.py:308-310` uses a truncating `open()`; its sibling writer to the same file,
`factory_decompose.py:174-180`, keeps `mkstemp` + `fsync` + `os.replace`. A crash mid-write leaves a
zero-byte file that reads back as "nothing is mirrored", and the next sync re-files issues that
already exist — **external damage no `git reset` undoes**. FEAT-14 is the pass that had both writers
open and gave only one the contract. *Correction on the record: an earlier draft of mine claimed
this falsifies `factory_decompose.py`'s docstring. The lead withdrew that on re-reading and I agree —
`:141-150` is `write_factory`'s own function contract, not a global claim about the file. The finding
stands on irreversibility alone; the docstring argument does not support it.*

## Where the goal stands

**12 of 18 met · 3 unmet · 3 waiting on you.** Unmet are SC-04, SC-05, SC-16 — all fix 2 above; qa
and pm reached that independently. The three waiting on you are quick, and the legwork is done:

- **SC-10** (5 min) — open `FEAT-11-graphql-field-resolve/notes/receipt-feature-key-drop.md` and
  confirm it records what was dropped. pm swept all 17 features pre/post migration: zero unrecorded
  drops, 17 receipts, none left over. *Note: the BRIEF's parenthetical is wrong twice — FEAT-11 lost
  22 keys, not 20, and it is not the maximum; FEAT-12 and FEAT-13 each lost 23.*
- **SC-11** (2 min) — pm recommends MET. One residual for your call: `factory.issues` and
  `factory.items` are bare `{type: object}` (`feature-schema.json:96-97`) where the sibling
  `github.issues` constrains values to integer, so they would accept a prose string today.
- **SC-15** (2 min) — the UAT script is written: `notes/uat-FEAT-14-sc15-readability.md`. *Caveat: no
  file in the corpus carries eleven keys — `factory` appears in zero of 17, so ten is the real
  maximum.*

## The finding worth more than the feature

**Every one of the eight plan defects lived in a `verify:` clause, and every one was writable
because the clause was authored as prose and never executed against the tree before signature.**
pm identified two shapes: *non-discriminating* — the assertion was already satisfied before the
change it existed to prove — and *self-contradicting* — the `verify` forbids a literal the same
task's own `intent` instructs the doer to write. Three intent-vs-verify contradictions surfaced
inside one signed plan, plus three defects in T-08's verify and two dead assertions in T-09's.

The proposed remedy lands in `check-plan-routes.py`, which already runs at plan time and is **not** a
carve-out, so it is dispatchable: record `verify_red_at` per task and fail any verify already green
at signature, plus grep every literal a verify forbids against that task's own intent. **The second
half needs no runner and catches three of the eight on its own.** Own feature or backlog — your call.

## Proposed backlog

| ID | Finding | Nature |
|---|---|---|
| B-1 | `gh-sync.py:308` non-atomic write of `feature.json` — re-files GitHub issues after a crash | bug |
| B-2 | Plan-time `verify:` clause checker — red-before-signature + intent cross-grep | enhancement |
| B-3 | SC-14's index check is blind to a corrupted **ruling clause**: prose round-trips verbatim, only structural fields regenerate. Proven live | bug |
| B-4 | `tests.yml`'s `Unit suite` step is the only runner for eight criteria and nothing asserts it — any PR can delete it. The `case 25` guard the comment claims does not exist (inherited, `eafc8ad`) | bug |
| B-5 | `gh-sync.py` reads `feature.json` with the YAML loader while `factory_decompose.py` uses `json.load` — latent divergence. Cheapest in the same pass as B-1 | chore |
| B-6 | `factory.issues` / `factory.items` unconstrained where `github.issues` is integer-typed | chore |
| B-7 | Three stale BRIEF lines: `:421` "exits 1 today" (exits 0), SC-13's "exactly two carve-outs" (five), SC-10's key counts | chore |
| B-8 | SC-02 has no failing fixture for the `factory` / `factory.edges` nesting levels (G1) | chore |
| B-9 | `harness.json`'s integration `detect` glob names 2 of the 12 scripts its `cmd` runs | chore |
| B-10 | Write guard denies paths containing an unexpanded shell variable — it does not expand `$VAR`. False positive | bug |
| B-11 | Citation drift — two edits: `plan.yaml:158` D-04 → DEC-190, `:261` D-08 → DEC-191 | chore |
| B-12 | `check-plan-routes.py:558` says FEAT-08 "is `awaiting_user`" in the present tense; it reads `Review` | chore |
| B-13 | Interrupting a lead does not stop its children (DEC-131). It fired **three times** this session and each digest honestly reported work that had in fact happened | bug |
| B-14 | No discriminating test confirmed for `check-plan-routes.py`'s `_is_shipped()` — the analogue of `test-check-state.py`'s `case_g`. One grep to settle | chore |

## How this briefing was assembled

**No report round was spawned** — the digests were read from disk (DEC-69). Assembled from:
`runs/2026-08-10-01-plan-product/`, `2026-08-10-02-eng/`, `2026-08-10-03-plan-product/`,
`2026-08-11-04-revision-product/`, `revision2-product/`, `t01t03-eng/`, `e1fix-eng/`,
`qa-seg1-validator/`, `t11-eng/`, `t05-eng/`, `t05b-eng/`, `t09-product/`, `t09b-product/`,
`t10-product/`, `qa-final-validator/`, `qa-final2-validator/`, `panel-validator/`,
`panel2-validator/`, `goalcheck-product/` — each `digest.md`.

**Every finding above I re-verified at source before writing it here**, because several findings on
this feature rested on false premises. Confirmed by my own commands: the `ImportError` handler and
the call's position inside the same `try`; `issubclass(SyntaxError, ImportError)` is `False`; the
truncating `open()` against its sibling's `os.replace`; zero schema fixtures in `test-check-domain.py`
and exit 2 from a live invented-key probe; the citation drift being two edits, not three; `factory`
in zero of 17 files.

**One scope gap, disclosed rather than absorbed:** the code reviewer recorded its range as
`1bdfe3f..3abaedd`, not `..HEAD` as dispatched. The difference is the state-only commits above the
pin — and since this feature's *subject* is execution-state files, "state-only" is not self-evidently
out of scope. Those commits were not code-reviewed. The security reviewer covered the full range.

**Three runs were interrupted, and every one of them ran on anyway (B-13).** The first qa attempt
left a live `MUTANT-PROBE` spliced into `DEC-192`'s row in `DECISIONS-INDEX.md` while its digest
reported nothing outside its run dir had changed; I restored it and verified byte-identity, and
committing it would have corrupted the index this feature just built. The first panel reported both
its substantive reviewers "rejected, never started" — **both had in fact run**, and their artifacts
arrived after the digest. That accident is why fix 1 has two independent confirmations. In every
case the lead reported honestly what it could see; the orphan is invisible from that tier.

**Budget:** 4 of 10 cycles, **19 of an informational 20 runs**. The run count is high and earned it —
three runs were consumed by interruptions rather than by rework, and the last three produced the two
findings that make this briefing worth reading. `cycles_used` is a corrected figure: signed at 3,
+1 for a traceable send-back, one untraceable increment removed.
