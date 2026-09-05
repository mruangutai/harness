# Plan-panel c10 — scope reader (code side) — BUG-1286-test-tree-enforcement

**BLUF: PASS with notes.** The divergence from the operator's literal wording is CORRECT (per-pattern
verified: none of today's 3 `**/`-prefixed unit patterns certify under the literal universal reading),
and the replacement (a)-(d) rule is SOUND for today's live config and for every constructed adversarial
shape I could find — with one genuine MED faithfulness gap: condition (b)'s wildcard-presence
requirement rejects the *safest possible* case, a fully-literal wildcard-free core, which is exactly the
Advisor's own cited proof-witness pattern (`**/test_foo.py`). No must_fix; severity_max is `med`.

## (a) Literal-ruling verification, per pattern (fnmatch semantics, `code_grade._is_test_path` at
`code_grade.py:458-473`; live `.harness/harness.json` `unit.detect`)

Simulated `_is_test_path`-equivalent matching plus the literal ruling ("every matched path ends in a
fixed slash-free literal SUFFIX the vocabulary refuses at that suffix") against all 3 live `**/`-prefixed
`unit` patterns:

| pattern | literal suffix | literal ruling certifies? |
|---|---|---|
| `**/*.test.*` | none (ends in `*`) | **NO** |
| `**/*_test.*` | none (ends in `*`) | **NO** |
| `**/test_*.py` | `.py` | **NO** — `is_test_shaped(<arbitrary-prefix>.py)` is False for a plain prefix; `.py` alone is refused nowhere |

Matches plan.yaml:298 exactly. The divergence's premise is confirmed true: literally read, **none of
today's patterns certify**, so a hygiene half asserting the operator's universal wording directly
could never be green on the unmutated config. No finding here.

## (b) Faithfulness of the (a)-(d) rule (plan.yaml:659-722)

(a) NO DIRECTORY ESCAPE and (c) FIXED-LITERAL KEY carry the real force: (a) is what refuses a wildcard
in a non-final pattern segment (kills `**/test_*/**`-shaped patterns); (c) is what refuses a core with
no fixed literal text at all (kills `**/*.spec.*`, `**/test_*.p?`). (d) is currently vacuous on every
live pattern (no corpus basename matches any of today's 3 cores) — it is dormant defense-in-depth, not
decoration: it still fires for `**/test_*.p?`'s `test_x.pw` and `**/*.spec.*`'s `x.spec.y`/`x.spec.tsx`.

**(b) NON-DEGENERATE is where faithfulness breaks.** `core.strip("*?[") != ""` is fine, but the
preceding conjunct — `core contains a wildcard` — is NOT implied by (c) and is not motivated by the
"fixed slash-free literal text" insight at all. A core with **zero wildcard characters** (a pure
literal string) trivially satisfies "fixed literal text" more completely than any wildcarded core, and
has **zero directory-crossing exposure** (no `*`/`?`/`[` to span a `/`). Yet (b) rejects it outright:

```
pattern = "**/test_foo.py"   (core = "test_foo.py", no wildcard at all)
  inside_tests   -> False  (prefix computation finds no non-wildcard-terminated segment before "**")
  guard_covered  -> False, reason "(b) NO WILDCARD AT ALL -> degenerate"
  real fnmatch match against .harness/tools/test_foo.py -> True
  is_test_shaped(that match)                             -> True  (genuinely, always, safe)
```

`**/test_foo.py` is the **Advisor's own cited witness** for the "buildability conclusion survives"
answer (`plan.yaml:297-298`, `advisor_consultation.a_impossibility_claim.method_scope`: "a
`**/`-prefixed pattern whose every match has the fixed literal basename `test_foo.py`, which
`is_test_shaped` always accepts — so there is no escaping path at all"). Under the current (a)-(d)
rule as written, that exact pattern is classified as **neither** inside-tests nor guard-covered, which
trips FAIL-CLOSED (plan.yaml:717-721) if it ever appeared as a real `detect` entry — even though
nothing about it is unsafe, and none of the three stated remedies ("widen the vocabulary" / "fix the
pattern" / "record a DEC-213 exception") actually fits, because there is nothing wrong with the pattern.

No live pattern hits this today (all 3 wildcarded unit cores have a `*`), so there is **no operational
impact now**, and the failure mode is conservative (fail-closed, not an escape) — hence `med`, not
`high`. But it is a genuine gap between the rule's stated justification and its implementation, worth
a one-line fix (drop the wildcard-presence conjunct from (b), keep only non-degeneracy) before this
axis space is extended further. Given cycle 10 is the operator's declared last cycle and there is no
review capacity left to re-verify a plan.yaml edit, I am **not** proposing this as a must_fix; recording
it for the operator's signature decision.

## (c) Attack — search for an undisclosed certifying-but-unrefused pattern

**NONE FOUND**, wider than cycle 8's search. Shapes tried:

1. Generative sweep: 220 candidate cores — 3 restricted prefixes (`test-`,`test_`,`probe-`) ×
   7 wildcard-shape templates (`*`, `*/*`, `[a-z]*`, `?*`, `*?`, `*.*`, `*x*`) × 10 extension
   variants (7 real `SOURCE_EXTENSIONS`, `..py`, and case-poisoned `.PY`/`.Py`), plus 10 agnostic-key
   wraps (`_test.`/`.test.` embedded 5 ways). For every core that certified (a)-(d) I tried 5 innocuous
   basenames (`gen.py`, `util.sh`, `index.ts`, `app.js`, `innocent.txt`, `config.json`) under 5
   directory-crossing prefixes. Zero survivors distinct from the known axis.
2. Targeted algebraic argument, then confirmed by execution: for a core that certifies via the
   AGNOSTIC key, any string matching it *as a basename* must contain `_test.` or `.test.` literally —
   and `is_test_shaped` accepts **any** basename containing that literal, at any extension, by
   construction. So no basename-level escape is possible for the agnostic key. For the RESTRICTED key,
   any basename-level match necessarily starts with the literal prefix and ends with the literal
   extension the trailing-region check pins, so `os.path.splitext` cannot diverge from it. **The only
   escape possible is the already-disclosed directory-component one** (a wildcard's `*`/`?`/`[...]`
   spans a `/`, so the literal text lands in a directory-name segment, leaving the final basename free).
   Verified this fires identically for **all three** live `**/`-prefixed patterns, not just
   `**/test_*.py`: `.harness/tools/a_test.d/gen.py` escapes `**/*_test.*`, and
   `.harness/tools/a.test.d/gen.py` escapes `**/*.test.*`, exactly as `.harness/tools/test_dir/gen.py`
   escapes `**/test_*.py`.
3. Char-class/edge probing: literal `]` without a matching `[` in the trailing-region scan, double
   dots (`test_*..py`), extension case variants — none produced a false certify; each either correctly
   fails (c) or remains internally consistent with `is_test_shaped`.

The disclosure at BRIEF's "## Verification gaps" names only `test_dir/gen.py` ("a path such as") as
the directory-component example, but SC-19's own corpus-spanning language (BRIEF:~this criterion) and
plan.yaml's T-01 intent (plan.yaml:~226-230, "the `*.test.*` and `*_test.*` directory-component
shapes") already name and measure all three instances — so the mechanism disclosure is complete even
though one prose bullet gives a single example. `info`, not a gate.

## (d) Re-measurement of the struck corpus-match conjunct (independent, not read from the c9 note
first)

| check | my result | c9 note's claim |
|---|---|---|
| 4/4 red cases fail | ✓ — `tests/../evil/**` and `**/test_*/**` fail (a); `**/*.spec.*` and `**/test_*.p?` fail (c) | same |
| 7/7 running-kind patterns certify | ✓ — 4 inside-tests (`tests/unit/**`, `tests/integration/**`, both `locally_run` probes) + 3 guard-covered (`**/*.test.*`, `**/*_test.*`, `**/test_*.py`) | same |
| 4 previously over-refused shapes now certify | ✓ — `**/test-*.sh`, `**/probe-*.ts`, `**/test_*.js`, `**/test_*.mjs` all certify vacuously under the struck rule; all 4 fail under the old occupancy-conjunct rule | same |

Independently reproduced before opening `notes/research-BUG-1286-test-tree-enforcement-honest-limit-c9.md`
— numbers match exactly. The struck conjunct's removal is measured-safe. `adequacy_notes` in the
historical `panel:` block already flags the deeper limitation correctly: (d) is corpus-sampled and can
never independently prove absence of a third axis; that limitation is accurately stated as a limitation,
not oversold as a proof.

## Fail-closed clause (plan.yaml:717-721) — general rule, not a shape list

Traced 7 edge cases through both `inside_tests`/`guard_covered` reconstructions: no `**/` prefix
(classifies correctly via `core = pattern`), empty core (`**/`, fails (b)), pure-wildcard core (`**/*`,
`**/**`, fails (b)), a sub-pattern containing `|` (moot — `_patterns()` splits on `|` before this stage
runs, so no sub-pattern can ever carry one), a leading `/` (fails both — rejected by the absolute-prefix
check in inside-tests and by (a) in guard-covered), and the `..`-substitution case. Every one lands in
FAIL-CLOSED or CLASSIFIED, never a silent fall-through or crash. This is a genuine general algorithm,
not banned-shape enumeration.

## Recurrence watch — no fourth live-config cardinality/occupancy pin

Grepped T-01, D-01, SC-19 and BRIEF's "## Verification gaps" for `== 1`, `>= 1`, `exactly one`,
`occupancy`, `cardinality`, `non-empty`. All hits are either (i) fixture/synthetic-set assertions
(`exactly one finding` in a constructed test case — fine), (ii) code-structure invariants (`violations()`
has exactly one caller; `is_test_shaped` has exactly one implementation — fine, not about `test_kinds`),
(iii) the T-03/T-04 one-fence-block contract (a note-format rule, unrelated to `test_kinds`), or (iv) the
explicit anti-occupancy language at plan.yaml:733-743 ("Make NO assertion... NO assertion that either
bucket is occupied"), which is the DELETION, not a new pin. The historical `panel:` block's `contested`
item about the old "bucket must be non-empty" clause is a preserved cycle-8 audit record, correctly
inert — the live T-01 text no longer contains that clause. No fourth pin found.

## Breakage sweep — amendment-era text

SC-06's exact-equality assertion (plan.yaml:523-527, BRIEF SC-06) still names the single fixture file
`.harness/tools/test_rogue.py` and the DOCUMENTED_EXCEPTIONS-rebind mechanism consistently at both
sites. T-03's fence-count contract and exit-code table (plan.yaml:892-912) is echoed verbatim by T-04's
intent and by SC-12 — all three describe the same two SEPARATE failure messages with no drift. SC-to-AC
traceability table: 19 SC rows, 9 REQ ids (REQ-01..09), all referenced by at least one task
(T-01 traces REQ-01-05,08,09; T-03/T-04 trace REQ-06; T-05 traces REQ-07) — no orphan REQ, no task
citing a REQ that doesn't exist. `depends_on` DAG (T-01←none, T-02/T-03←T-01, T-04←T-03, T-05←T-01,T-02)
is a valid topological order matching list order. No `verify:` clause found asserting a phrase a
sibling task deletes.

## Honest limit — accuracy in both directions

Reads correctly in both directions: it does NOT overstate (states "sufficient... not a proof",
explicitly names the un-enumerated axis space, explicitly says a third axis is not excluded) and does
NOT understate now that the corpus conjunct is gone (still names the directory-component residual as
the concrete open item and defers it explicitly to the behavioural half, consistent with my (c) finding
that this is the only real remaining axis).

## Overall

**KEEP.** Nothing here argues for not building this. My one MED finding ((b)'s wildcard-presence
over-refusal of the Advisor's own witness pattern) is a specification precision gap, safely fail-closed,
zero operational impact today, and cheap to fix later — not a reason to hold the ship.
