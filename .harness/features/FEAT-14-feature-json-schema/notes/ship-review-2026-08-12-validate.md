# FEAT-14 — feature.json with an enforced schema — ship review

**Recommendation: DO NOT SHIP YET.** Four fixes stand between here and shippable. Two are yours to
make directly; two are ordinary fix cycles. The feature works: all 17 execution-state files are
converted, every gate is green, and 12 of 18 success criteria are met. What is not yet true is that
the thing this feature exists to add — the write-time schema gate — is *protected*, and one defect
can reach outside the repo.

## What you would feel if this shipped as it stands

| | If it ships today | If the four fixes land first |
|---|---|---|
| Malformed `feature.json` | Blocked — **unless** `feature_schema.py` ever breaks, in which case it lands silently | Blocked, and blocked when the checker itself breaks |
| Someone deletes the schema check next month | Every gate stays green. Nothing notices | A test goes red |
| A `gh-sync` killed at the wrong instant | **Duplicate GitHub issues, milestone and parent — re-filed, manual cleanup** | Previous complete file survives |

None is theoretical-only: the middle row is how this feature's own defects reached review, the first
row already shipped in this branch, and I confirmed the third empirically below.

## The four things to fix

**1. The schema gate fails OPEN, and its own comment says it must not.** HIGH — **yours**
(`check-domain.sh` is a DEC-174 carve-out). `:891-897` catches only `except ImportError:`, but
`SyntaxError` is not one — so a syntax-broken `feature_schema.py` escapes uncaught, and `:14` records
that exit 1 is **non-blocking**, so the bad write proceeds. The block's own comment at `:873-877`
names three cases it must cover — "PYTHONPATH not exported, **a syntax error**, the file missing" —
and states this exact consequence. Two of the three raise `ModuleNotFoundError` and are caught; the
middle one is not. The same file already fixed this class at `:529-532` with `except Exception:`. The
call to `problems_for_text` sits inside the same `try`, so *any* exception escapes.

Widen to `except Exception:`, **and give the runtime-crash case its own message** — the current text
says "not importable", which would be wrong for a `problems_for_text` crash. *Two independent
code-review spawns found this same line*, and I confirmed every element including that
`issubclass(SyntaxError, ImportError)` is `False`.

**2. The gate has no standing test at all.** HIGH — **yours**, same carve-out. SC-04, SC-05 and
SC-16 declare `verify: automated`; `test-check-domain.py` carries **zero** schema-rejection fixtures.
True today only by one-off probes that left nothing re-runnable. **Fix 1 BEFORE 2**, or the new
fixtures pin the fail-open as expected behaviour.

**3. `gh-sync.py` can re-file GitHub issues that already exist.** HIGH, and the only defect here that
mutates state **outside** the repo. Ordinary fix cycle — not a carve-out. Two defects compose:

- `save_recorded:308` opens `feature.json` with `open(p, "w")`, which **truncates to zero bytes at
  open, before any data is written**. I measured it: a 28-byte file is 0 bytes immediately after the
  `open` call. So the zero-byte window is **guaranteed on every call**, not merely possible on a
  partial write. There are six call sites, and `:394` is *inside the per-issue create loop* — its own
  comment says the frequency is deliberate, "after EVERY create — a crash mid-loop must not orphan
  issues". The mitigation for one hazard is the mechanism of the other.
- `load_recorded:274-276` then routes a zero-byte file to the **empty** record. I measured that too:
  a zero-byte file loads as `None`, so the `isinstance(doc, dict)` guard fails and it returns "nothing
  is mirrored". The next sync re-creates the milestone, the parent issue and every task issue.
  `git restore` recovers the file; it does not un-file GitHub issues.

Two-part remedy: mirror `write_factory`'s same-directory `mkstemp` + `fsync` + `os.replace`; and make
an empty-or-non-mapping document an **error** in `load_recorded`, scoped so that a merely *missing*
`github` key still means legitimate first sync.

**4. Ordinary fix-cycle companions** — B-5 (the two writers read `feature.json` with different
parsers) and B-14, cheapest in the same `gh-sync.py` pass.

*Correction on the record:* an earlier draft of mine ranked fix 3 MED and argued it falsifies
`factory_decompose.py`'s docstring. I was wrong twice. The docstring at `:141-150` is
`write_factory`'s own function contract, not a global claim — the finding never needed it. And MED
rested on "a crash mid-write is real but not routine"; truncation-at-open defeats that, because the
window is every call. Promoted to HIGH on evidence I measured myself.

## Where the goal stands

**12 of 18 met · 3 unmet · 3 waiting on you.** Unmet are SC-04, SC-05, SC-16 — all fix 2; qa and pm
reached that independently. The three waiting on you are quick and the legwork is done:

- **SC-10** (5 min) — open `FEAT-11-graphql-field-resolve/notes/receipt-feature-key-drop.md`. pm swept
  all 17 pre/post: zero unrecorded drops, 17 receipts, none left over. *BRIEF's parenthetical is
  wrong twice — FEAT-11 lost 22 keys not 20, and FEAT-12/13 each lost 23.*
- **SC-11** (2 min) — pm recommends MET. Residual for your call: `factory.issues` and `factory.items`
  are bare `{type: object}` (`feature-schema.json:96-97`) where sibling `github.issues` constrains to
  integer, so they would accept a prose string today.
- **SC-15** (2 min) — script ready at `notes/uat-FEAT-14-sc15-readability.md`. *No corpus file carries
  eleven keys; `factory` is in zero of 17, so ten is the real maximum.*

## The finding worth more than the feature

**Every one of the eight plan defects lived in a `verify:` clause, and every one was writable because
the clause was authored as prose and never executed against the tree before signature.** Two shapes:
*non-discriminating* — already satisfied before the change it existed to prove — and
*self-contradicting* — the `verify` forbids a literal the same task's own `intent` instructs the doer
to write.

The remedy lands in `check-plan-routes.py`, which already runs at plan time and is **not** a
carve-out: record `verify_red_at` per task and fail any verify already green at signature, plus grep
every literal a verify forbids against that task's own intent. **The second half needs no runner and
catches three of the eight on its own.**

## Proposed backlog

| ID | Finding | Nature |
|---|---|---|
| B-1 | **Promoted into fix 3 above** — `gh-sync.py` zero-byte window + empty-record read | bug |
| B-2 | Plan-time `verify:` clause checker — red-before-signature + intent cross-grep | enhancement |
| B-3 | SC-14's index check is blind to a corrupted **ruling clause**: prose round-trips verbatim, only structural fields regenerate. Proven live | bug |
| B-4 | `tests.yml`'s `Unit suite` step is the only runner for eight criteria and nothing asserts it — any PR can delete it. The `case 25` guard its comment claims does not exist (inherited, `eafc8ad`) | bug |
| B-5 | `gh-sync.py` reads `feature.json` with the YAML loader while `factory_decompose.py` uses `json.load` | chore |
| B-6 | `factory.issues` / `factory.items` unconstrained where `github.issues` is integer-typed | chore |
| B-7 | Three stale BRIEF lines: `:421` "exits 1 today" (exits 0), SC-13's "exactly two carve-outs" (five), SC-10's key counts | chore |
| B-8 | SC-02 has no failing fixture for the `factory` / `factory.edges` nesting levels | chore |
| B-9 | `harness.json`'s integration `detect` glob names 2 of the 12 scripts its `cmd` runs | chore |
| B-10 | Write guard denies paths containing an unexpanded shell variable — it does not expand `$VAR`. It bit me twice this session | bug |
| B-11 | Citation drift — two edits: `plan.yaml:158` D-04 → DEC-190, `:261` D-08 → DEC-191 | chore |
| B-12 | `check-plan-routes.py:558` says FEAT-08 "is `awaiting_user`"; it reads `Review` | chore |
| B-13 | Interrupting a lead does not stop its children (DEC-131). Fired **three times** this session; each digest honestly reported work that had in fact happened | bug |
| B-14 | No discriminating test confirmed for `check-plan-routes.py`'s `_is_shipped()` | chore |
| B-15 | `write_factory` starts from `doc = {}` and can write a document missing all eight required keys — the mirror of B-1: each writer holds the property the other lacks | bug |
| B-16 | Reviewers cannot falsify enforcement-path findings: the write guard denies them the fixture creation needed to break a checker on purpose. Both HIGHs were confirmed by reading, not by end-to-end execution | enhancement |

## How this briefing was assembled

**No report round was spawned** — digests read from disk (DEC-69): `runs/2026-08-10-01-plan-product/`,
`2026-08-10-02-eng/`, `2026-08-10-03-plan-product/`, `2026-08-11-04-revision-product/`,
`revision2-product/`, `t01t03-eng/`, `e1fix-eng/`, `qa-seg1-validator/`, `t11-eng/`, `t05-eng/`,
`t05b-eng/`, `t09-product/`, `t09b-product/`, `t10-product/`, `qa-final-validator/`,
`qa-final2-validator/`, `panel-validator/`, `panel2-validator/`, `goalcheck-product/` — each
`digest.md`.

**Every finding I re-verified at source**, because several findings on this feature rested on false
premises. Measured by me: the `ImportError` handler and the call's position; `issubclass(SyntaxError,
ImportError)` is `False`; **a 28-byte file at 0 bytes immediately after `open(p,"w")`**; a zero-byte
file loading as `None` and yielding the empty record; zero schema fixtures in `test-check-domain.py`
and exit 2 from a live invented-key probe; the citation drift being two edits; `factory` in zero of 17.

**One scope gap:** the code reviewer recorded its range as `1bdfe3f..3abaedd`, not `..HEAD`. Since
this feature's subject *is* execution-state files, "state-only commits" is not self-evidently out of
scope. Security covered the full range.

**Neither HIGH was falsified end-to-end (B-16).** Both are confirmed by reading both code paths and
by Python semantics, not by running a broken checker — the write guard denies reviewers the fixture
creation that would require. Worth one command from whoever fixes them.

**Three runs were interrupted and every one ran on anyway (B-13).** The first qa attempt left a live
`MUTANT-PROBE` in `DECISIONS-INDEX.md` while its digest reported nothing changed; I restored it and
verified byte-identity. The first panel reported both substantive reviewers "never started" — **both
had run**, and returned ~40 minutes after its own digest, with the stronger version of fix 3 that
this briefing now carries. Each lead reported honestly what it could see; the orphan is invisible
from that tier.

**Housekeeping done:** twelve task sub-issues `#264`–`#275` closed on the mirror (`rc 0` each,
verified `CLOSED`); two dead worktree registrations pruned. One probe worktree from the qa run
remains on disk in this session's scratchpad.

**Budget:** 4 of 10 cycles, **19 of an informational 20 runs**. Three runs went to interruptions
rather than rework, and the interrupted ones produced the two findings that make this briefing worth
reading. `cycles_used` is corrected: signed at 3, +1 for a traceable send-back, one untraceable
increment removed.
