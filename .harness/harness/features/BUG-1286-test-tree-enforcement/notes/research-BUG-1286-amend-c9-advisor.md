# Cycle-9 amendment — all four cycle-8 findings closed in one edit

**BLUF.** The four findings are closed at `plan.yaml` T-01 case 11, `plan.yaml` D-01 `because`, and
`BRIEF.md` SC-19 + `## Verification gaps`. **The operator's literal wording in ruling 2 was MEASURED
first and is RED on today's own config** — it certifies none of the three `**/`-prefixed `unit`
patterns — so what is written is the faithful refinement the lead named, measured GREEN today and RED
on all four escape shapes. T-05 was grepped and carries neither the withdrawn sentence nor the
occupancy pin; it is unchanged.

## The certification rule as written (`plan.yaml:659-722`, `BRIEF.md:192-204`)

GUARD-COVERED requires all four: **(a)** core — the pattern minus one leading `**/` — contains no
`/`; **(b)** core is non-degenerate; **(c)** core carries FIXED wildcard-free literal text the
vocabulary keys on — the agnostic infix `_test.` / `.test.`, or a restricted prefix `test-` /
`test_` / `probe-` **together with** a fixed wildcard-free source extension; **(d)** the fixed
adversarial corpus, now carrying extension-poison basenames, leaves no basename matched-and-unrefused
by the imported `is_test_shaped`. The occupancy pin is gone with no replacement (`plan.yaml:725-735`).

## Divergence from the operator's literal wording — measured, not argued

`ruleA` = "every matched path ends in a fixed slash-free literal suffix the vocabulary refuses at that
suffix". Against the real `.harness/harness.json`:

| pattern | ruleA | why |
|---|---|---|
| `**/*.test.*`, `**/*_test.*` | UNCERTIFIED | end in `*` — no fixed suffix at all |
| `**/test_*.py` | UNCERTIFIED | suffix `.py`, but `gen.py`/`foo.py`/`conftest.py` are not refused |

Case 11 would be **RED on the unmutated config** — unbuildable, exactly the failure the false
impossibility sentence was covering for. The refinement moves the fixed-literal reasoning to the
**basename axis** on top of (a), which is decidable by inspection and green today.

## Six prototype results (heredoc prototype over the real config, worktree `a8532ce3`)

1 today → **GREEN**, 7/7 certified · 2 `tests/../evil/**` → **RED** ((a)) · 3 `**/test_*/**` → **RED**
((a)) · 4 `**/*.spec.*` → **RED** ((c) no key) · 5 `**/test_*.p?` → **RED** ((c) no fixed extension) ·
6 drop `**/test_*.py` → **GREEN**, 6 certified.

Independence measured: `**/test_*.p?` fails (c) **and** (d); `**/test_*.[ps]y` fails (c) only — no
poison basename matches it, so the corpus oracle alone would have passed it. Both conditions are
load-bearing; neither is redundant.

## Rationale sentence — every site

Greps on `prefixed fnmatch`, `satisfies that property`, `could never be green`, `bucket must be
non-empty`: the only surviving hits are inside the byte-identical `panel:` block (`plan.yaml:235,
249, 311, 337, 406` — the findings record) and the **new explicit withdrawal** at `plan.yaml:683`
("it is not true that no `**/`-prefixed fnmatch pattern can satisfy…"). Corrected at: T-01
(`plan.yaml:682-691`), D-01 `because` (`plan.yaml:62-115`, the sentence at 88-95), SC-19 (`BRIEF.md:204-209`). T-05: zero hits.

## Open items for the next reader

- The `panel:` block still shows all four findings `disposition: open`; the dispatch required it
  byte-identical, so the dispositions were not moved to `resolved` / `resolved_by: T-01`. Whoever
  next writes `panel:` should close them against T-01.
- `**/test-*.sh` is a legitimately covered shape that (d) currently reports as unseen (no corpus
  basename). That is why the remedy list gained "extend the CORPUS — add, never remove"
  (`plan.yaml:769-772`): fail-closed with a documented route, not a mystery red.
- The honest limit is stated where the operator signs (`BRIEF.md:299-309`) and in T-01
  (`plan.yaml:699-708`): sufficient over two hand-found axes, a third not excluded; what generalises
  is the fail-closed clause (`plan.yaml:709-713`, `BRIEF.md:200-203`).
