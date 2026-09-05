# Goal-check — BUG-1286 plan phase, cycle 9 (post-Advisor amendment)

**BLUF. YES — this plan delivers the operator's stated intent: all eleven ticket acceptance criteria
map to a falsifiable SC and to traced work, all four blocking questions are decided, both negatives
hold, and the fourth ruling is closed clause by clause; three residual imprecisions survive, all in
justification prose, none gating.**

Graded from the current text at worktree `a8532ce3`, working tree carrying only `BRIEF.md`,
`plan.yaml`, `observations/` and the c9 amend note (`git status --porcelain`) — no implementation,
test or config file touched.

## 1. Destination, both negatives

- Destination (grilling `:4`): "an approved BRIEF and plan that make every tracked Harness
  test-shaped file obey the `tests/**` tree". Met in plan form: `BRIEF.md:16-21` goal, REQ-01..09,
  T-01..T-05, all `status: ready`.
- Negative 1 — no change to product-checkout discovery: `D-03` (`plan.yaml:121-141`) scopes the clause
  to a root whose own index carries the predicate; `SC-16` (`BRIEF.md:152-157`) grades it via T-01
  case 9 (`plan.yaml:566-570`) plus the single-caller pin. Untouched this cycle.
- Negative 2 — implementation not begun: `approval.status: pending`, `status: plan`, and the working
  tree carries no source edit. Held.

## 2. The four blocking planning questions — all still settled decisively

| # | question | settled at |
|---|---|---|
| 1 | authoritative vocabulary, extensions, probe-Markdown scope | `D-01` `plan.yaml:34-47` — two groups, opposite extension policies; probe Markdown out of the repo-wide clause, agnostic pair in at any extension |
| 2 | exception contract; FEAT-44 classification | `D-02` `:111-120`, `D-05` `:150-162` (stays, not relocated, coupling cost stated); `layout_fixtures.py` not test-shaped (`SC-09`, T-05 `:1033-1034`) |
| 3 | tracked authority + failure semantics | `D-03` `:121-141` — Git index, staged add scanned/staged delete not, `LookupError` is a violation, no-index root inert |
| 4 | amend DEC-213 + regenerate index | `D-06` `:163-171`, `T-05` `:966-1046` |

## 3. Eleven acceptance criteria — 11 delivered, 0 partial, 0 not delivered

AC order is the ticket's. `BRIEF.md:235-255` carries the same table and is accurate.

| AC | SC | traced work |
|---|---|---|
| 01 rejected outside `tests/**` | SC-01, SC-02, SC-18, SC-19 | T-01 cases 1, 8, 10, 11 |
| 02 all paths, deterministic | SC-03 | T-01 case 3, T-02 case 3 |
| 03 runner refuses before sentinel | SC-04 | T-02 case 2 (`plan.yaml:809-814`) |
| 04 enumeration failure closed | SC-05, SC-17 | T-01 cases 4, 5; T-02 case 4 |
| 05 valid unit/integration/manual accepted | SC-06, SC-07 | T-01 case 1 exact-equality (`:523-543`) |
| 06 support modules incl. `bin/` | SC-08, SC-09, SC-18 | T-01 cases 7, 8 |
| 07 exact documented exceptions + positive coverage | SC-10 | T-01 cases 6, 7 |
| 08 tracked vs untracked | SC-11 | T-01 case 2, T-02 case 5 |
| 09 audit re-run at `review_sha` | SC-12 | T-03, T-04 |
| 10 DEC-213 + index | SC-13 | T-05 |
| 11 product discovery + mutation scope unchanged | SC-14, SC-15, SC-16 | T-01 case 9; SC-14/15 inspection over an unchanged surface |

Every SC carries exactly one `verify:`, and each `automated` one names its kind.

## 4. FEAT-44 classification — carried through, not weakened

`D-05` (`plan.yaml:150-162`) keeps the exception at its exact path with the archival consequence
stated; T-01 seeds it as the sole registry entry (`:444-449`); case 7 makes the live registry
load-bearing (`:558-562`); T-03/T-04 anchor their `verify:` on its `documented-exception` row
(`:835`, `:929`); T-05 names it (`:1031-1032`). Unchanged this cycle.

## 5. Out-of-scope entries and untouched surfaces

All four grilling entries (`grilling:15-18`) undrifted: no product-discovery redesign (D-03),
no mutation-snapshot widening (SC-15 pins the single `run_pool.py --mutation-check "$BIN_DIR"`),
no support-module rename (SC-09, T-05 `:1033-1034`), no implementation this run. `.harness/harness.json`
is byte-unchanged in the working tree and `SC-14` pins that at `review_sha`.

## 6. Delivered beyond the ask

One item, and it is operator-ratified rather than creep: REQ-09 / SC-19 / T-01 case 11 — the
guard-covers-discovery invariant — is not in the ticket. It arrived as a DEC-132 addition, has been
the subject of three consecutive operator rulings, and is now the largest single block of the plan
(`plan.yaml:579-783`). Recorded, not charged as scope creep.

## Fourth ruling — clause by clause

1. **All four c8 findings closed in T-01 case 11 and SC-19, incl. the `**/test_*.p?` escape.**
   CLOSED. Extension-position axis: `plan.yaml:665-676` (key (c)), worked counterexample `:690-698`,
   red case (iv) `:757-762`, poison corpus `:714-720`, SC-19 `BRIEF.md:194-202, 220-221`. Prototyped
   here against the real `harness.json`: today's 7 running-kind patterns all certify (GREEN); the
   four red shapes `tests/../evil/**`, `**/test_*/**`, `**/*.spec.*`, `**/test_*.p?` all certify as
   NEITHER; `.harness/test_evil.pw` is counted by `code_grade._is_test_path` once `**/test_*.p?` is
   added and by nothing today.
2. **False impossibility rationale corrected at EVERY site.** CLOSED. Grep
   `impossib|no \*\*/-prefixed|no "\*\*/"-prefixed|cannot satisfy the universal` over the feature
   directory: hits only in (a) the `panel:` findings record and `STATE.md`/`notes/` — the historical
   record, which must not be rewritten; (b) `plan.yaml:683`, which is the explicit WITHDRAWAL. The
   three live spec sites now state the sufficient-condition reason correctly: `plan.yaml:682-689`,
   D-01 `because` `:75-96`, `BRIEF.md:204-209`. **Zero surviving assertions of the false claim.**
3. **Occupancy pin deleted with no replacement.** CLOSED. `plan.yaml:725-735` forbids it by name
   including the `">= 1"` form; `BRIEF.md:203` mirrors. Grep for
   `non-empty|at least one|occupanc|bucket|>= 1` returns three survivors, none of them a bucket
   assertion: `:656` (the inside-tests prefix must be non-empty), `:664` condition (b)
   (`core.strip("*?[")` non-empty), `:677` condition (d) (core matches ≥1 corpus basename). The
   first two are per-pattern well-formedness. The third is per-pattern, not per-bucket — see
   divergence (d).
4. **Positive control's INAPPLICABLE branch survives.** CLOSED — `plan.yaml:639-643`, `BRIEF.md:188-191`.
   It is not exercised today: `.harness/tools/test_dir/gen.py` is counted live and is not
   `is_test_shaped`, so the control has a subject.
5. **Preserved, each verified individually.** REQ-09 breadth `BRIEF.md:40-50` (all running kinds,
   full-relative-path `fnmatch`, superset, probe rule); matcher semantics `plan.yaml:48-61` and
   case-11 shared setup `:583-595`; normalization + `..` rejection (the F-01 fix) `:652-658` with red
   case (i) `:741-747`, measured RED here; manual-probe source-name rule `:58-60`, `BRIEF.md:46-48`,
   `T-05:1001-1002`; D-05 `:150-162`; three-kind blast radius `BRIEF.md:263-277`, `plan.yaml:773-780`.
   Scope unchanged.
6. **Honest limit stated where the operator signs.** MOSTLY — `BRIEF.md:299-309` plus `plan.yaml:699-708`
   say sufficient-over-two-hand-found-axes, third not excluded, no exhaustive-proof claim. Two
   imprecisions remain, gaps 1 and 2 below.

## The divergence — adjudicated on my own evidence

**(a) Is the unbuildability claim TRUE? YES — per pattern, measured.** Ruling text: *every match ends
in a fixed slash-free literal SUFFIX the vocabulary refuses.*

| pattern | fixed suffix (text after last wildcard in core) | verdict |
|---|---|---|
| `**/*.test.*` | `''` | UNCERTIFIABLE — no fixed suffix at all |
| `**/*_test.*` | `''` | UNCERTIFIABLE — no fixed suffix at all |
| `**/test_*.py` | `.py` | UNCERTIFIABLE — the vocabulary refuses no basename merely for ending `.py`; `gen.py`, `foo.py`, `conftest.py` all pass `is_test_shaped` as False |

All three of `unit.detect`'s `**/`-prefixed patterns fail, so case 11 could never be green on the
unmutated config. pm's and the product lead's conclusion is confirmed independently.

**(b) FAITHFUL, not a weaker rule wearing the name.** The Advisor's insight (`plan.yaml:299-304`) is
that closure comes from *fixed slash-free literal text surviving into the basename*, not from the
absence of a wildcard after `**/`. Condition (a) forces core to be one basename-level segment;
condition (c) then requires fixed wildcard-free literal text the vocabulary keys on *inside that
segment* — agnostic infix `_test.`/`.test.`, or restricted prefix at position 0 **plus** a fixed
source extension at the tail. Both keys are exactly "fixed slash-free literal text", moved from the
suffix position (unusable, per (a)) to the basename axis. It is also demonstrably sufficient, not
merely plausible: over 363 machine-generated cores passing (a)+(b)+(c) cross-matched against 2 287
fuzzed basenames, **zero** matched-and-unrefused basenames.

**(c) Both known leak axes still closed; one survivor, and it is the disclosed one.** Extension-position
axis: closed by (c) — `**/test_*.p?`, `**/test_*.[ps]y`, `**/*.spec.*` all fail. Directory-component
axis: (a) closes only the non-final-segment form (`**/test_*/**` fails (a)). **The construction
attempt succeeds along the other form**: `**/test_*.py` certifies guard-covered under (a)–(d) and
`code_grade._is_test_path` counts `.harness/tools/test_dir/gen.py`, whose basename the vocabulary can
never refuse. That is exactly the residual the plan discloses at `plan.yaml:704-708`,
`BRIEF.md:211-213` and `BRIEF.md:292-298` and hands to the behavioural half — a known, stated
residual, not a new gap. No *undisclosed* survivor found on either axis.

**(d) YES, (d) creates a new failure mode; the remedy is adequate and is NOT the config pin returning.**
Measured: `**/test-*.sh`, `**/probe-*.ts`, `**/test_*.js` and `**/test_*.mjs` each satisfy (a)(b)(c)
— legitimately covered — and are reported UNCERTIFIED because no corpus basename matches them. The
corpus samples restricted shapes at `.py`/`.md`/`.pw` only, so **4 of the 7 source extensions are
unsampled**; the channel is wider than the single `**/test-*.sh` instance the amend note records
(`research-BUG-1286-amend-c9-advisor.md:56-58`). It is not the occupancy pin in a costume, for three
reasons: the red names the offending pattern rather than firing with nothing to fix; the remedy is
ADDITIVE and documented (`plan.yaml:769-772` — extend the corpus, never remove); and no property of
today's `detect` value is pinned, so a narrowing does not redden it (measured: dropping
`**/test_*.py` leaves the set certified). The failure direction is over-refusal — fail-closed. The
one asymmetry worth the operator's eye is gap 2 below.

## Stale-text check — clean

`D-01`'s `because` (`plan.yaml:62-109`) carries the withdrawal, the matcher contract and the empty
measured set at `cab6adb2`; `BRIEF.md ## Verification gaps` (`:257-317`) carries six bullets with no
withdrawn claim; `T-05`'s DEC-213 bullets (`:986-1032`) carry neither the withdrawn sentence nor any
occupancy pin (grep: zero hits in `:966-1046`); `SC-06`'s exact-equality assertion (`BRIEF.md:88-103`)
still matches T-01 case 1's one-element list and its `probe-*.py` manual shape (`plan.yaml:523-543`);
`T-03`/`T-04` `verify:` blocks (`:834-835`, `:928-929`) retain the `documented-exception` non-vacuity
anchor and the unconditional-output contract they depend on; the AC table is accurate against the
ticket's eleven bullets.

## Surviving gaps

1. **NON-GATING — "the directory-component axis, closed by (a)" is overstated at two sites.**
   `plan.yaml:700` and `BRIEF.md:300-301` say the hygiene rule *closes* the directory-component axis;
   `SC-19` (`BRIEF.md:211-213`) and `plan.yaml:704-707` say the opposite, correctly, four lines later,
   and `D-01` (`plan.yaml:103-106`) has the right formulation ("refuses a wildcard in any non-final
   segment, while the directory-component residual … stays with the behavioural half"). Non-gating:
   self-corrected in the same paragraph at both sites, zero operational effect, same class as the two
   c8 `low` findings. One edit: align `plan.yaml:700` and `BRIEF.md:301` to D-01's wording.
2. **NON-GATING — "(c) and (d) … both are load-bearing" is evidenced one way only, and (d)'s
   false-positive channel is not disclosed where the operator signs.** `plan.yaml:696-698` cites
   `**/test_*.[ps]y` as caught by (c) alone; nothing shows (d) catching what (c) misses, and the fuzz
   above found no basename escape under (a)+(b)+(c) alone. Meanwhile (d)'s "matches at least one
   corpus basename" conjunct reddens four legitimate shapes. The BRIEF's `## Verification gaps` says
   nothing about it. One edit, operator's choice of two: (i) add one clause to
   `BRIEF.md:299-309` naming the oracle's over-refusal channel and its add-a-corpus-entry remedy, or
   (ii) drop (d)'s first conjunct so the oracle is vacuously true when no corpus basename matches —
   verified safe here: all four red cases still fail on (a) or (c).
3. **NON-GATING — `panel:` bookkeeping.** All four c8 findings still read `disposition: open` with no
   `resolved_by: T-01`, and Q2 (the bucket clause) is now moot because ruling 3 deleted the pin. The
   c9 dispatch required the block byte-identical, so this is correctly not pm's edit; it belongs to
   the next `panel:` transcription or the main session. The panel gate is untripped either way
   (`must_fix: []`, `severity_max: med`).

No gating gap. The re-run is clean.
