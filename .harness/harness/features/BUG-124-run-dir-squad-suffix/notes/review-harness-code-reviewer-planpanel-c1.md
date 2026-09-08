# Review — BUG-124 plan cycle 1 (scope / harness-code-reviewer)

**PASS with advisory notes.** All seven cycle-0 findings are genuinely closed, independently
re-derived — not accepted on pm's or the orchestrator's word. My own read of the revision surfaces
three new MED-level design-soundness gaps in D-05 itself (none block this plan's own build) and
confirms one already-disclosed LOW record-hygiene gap. Nothing here rises to `high`.

Read at HEAD `87205da9`. Nothing edited: `plan.yaml`/`BRIEF.md` untouched (see `git status` below).

## 1. The seven cycle-0 findings, re-derived independently

| id | sev | verdict | evidence |
|---|---|---|---|
| PF-d882b5400a23 (no escape hatch) | high | **closed** | D-05 adopted; T-02 intent's REFUSAL MESSAGE section requires every printed path go through `.replace` to `[.]harness/`, "NEVER print a raw anchored run-dir path"; case (h) PASTE-BACK is the producing case, with an explicit red proof ("delete the anchor rewrite... watch it fail at exit 2") |
| PF-018d8e2a2c8c (T-01 verify 2nd site) | high | **closed** | Read T-01's full verify line (785 bytes) programmatically: zero occurrences of the literal substring `.harness/` anywhere in it (`plan.yaml:174`). The only anchored-looking text is `[.]harness/harness/features/F/runs/eng-t01/digest.md`, restored to the real anchor only inside a runtime `.replace("[.]", ".")` call |
| PF-b126afaed82b (GOALCHECK-F1, T-02 verify) | high | **closed** | Same check on T-02's verify line (461 bytes, `plan.yaml:255`): zero literal `.harness/` occurrences |
| PF-05e45a58b54f (live-manifest `len(g)==3` pin) | med | **closed** | T-01 verify reads `assert g and all("/runs/" in x for x in g), g` — no count assertion; intent's TESTS section carries the "DO NOT PIN THE LIVE MANIFEST BY COUNT OR BY CONTENT" paragraph naming REQ-04 |
| PF-64c48fa9fb3d (unobservable derivation failure) | med | **closed at design level** | T-02 intent: `harness_yaml.load_str` now runs with NO try/except in the shell-side derivation, `HARNESS_RUN_DIR_DERIVED` crosses the isolation boundary, THE CHECK prints one of two non-interchangeable SKIPPED texts keyed on that flag, new case (i) exercises a garbage manifest, and the RED PROOF instructs collapsing the two lines to prove the pair discriminates |
| PF-4f1b6dc30897 (T-03 verify binds 4 words) | med | **closed** | Verified below (§3) — six required substrings, all present in the doer's prescribed prose, `case`/`tr` construct tested and discriminates correctly |
| PF-6e184d4c13c2 (mis-cited check-domain.sh:103) | low | **closed** | Read check-domain.sh directly: line 103 is `python3 -c 'import sys; sys.path.pop(0); exec(compile(sys.stdin.read(), "<stdin>", "exec"))' ... <<'PY'` (pop, feeds stdin); line 125 is `sys.path.insert(0, _bin_dir)` where `_bin_dir` comes from `_derived, argv_agent, _bin_dir = sys.argv[1:4]`, i.e. `sys.argv[3]`. T-02's intent now states exactly this and disclaims the old `sys.argv[1]` citation |

A remedy that changed text without closing the finding would be a finding in its own right; none of
the seven did that — each remedy's mechanism was independently re-derived from the file, not
inferred from the remedy note's own prose.

## 2. D-05 soundness — sound as stated, three real but bounded gaps

**False-refusal discoverability is handled well.** T-02's refusal message spec requires the final
line state the `[.]harness/` convention on *every* refusal, so a dispatcher who has never read
SKILL.md learns the escape at the point of failure, not only from documentation. REQ-02 also puts
the compliant form first in the message, which is the more natural repair path for the common case
(a genuinely inverted slug) — reducing, though not eliminating, the chance anyone reaches for the
escape reflexively.

**Gap 1 — grep/regex bracket-expression collision (demonstrated).** `[.]` is a POSIX bracket
expression matching a literal `.`, identically to an escaped `\.`, in `grep`'s BRE/ERE and in an
unescaped Python regex character class. Demonstrated live: `printf '.harness/...' | grep "[.]harness/"`
matches. So any future author who greps a receipt, a bug report, or a doc for the literal spelling
`[.]harness/` — to audit that the convention was applied, say — also matches every real, un-escaped
`.harness/` anchor in the same sweep, silently. SKILL.md's convention text gives no warning that the
escape is not grep-safe. **Severity: med** (maintainability/tooling cost; does not affect this
plan's own build, which never greps for the spelling).

**Gap 2 — YAML flow-sequence collision (demonstrated).** `path: [.]harness/harness/features/F/runs/…`
as a bare, unquoted YAML plain scalar fails to parse (`yaml.safe_load` raises `ParserError`: PyYAML
reads `[.]` as a one-item flow sequence and then chokes on the trailing unquoted text). T-01/T-02/T-03's
own `verify:`/`intent:` fields are safe today only because they are `|` block scalars, which this
plan does consistently — but D-05's own convention text (`.claude/skills/harness/SKILL.md`, via T-03)
never states that constraint, and the convention explicitly invites use in "a receipt, a bug report,"
neither of which is guaranteed to stay inside a block scalar if either ever becomes YAML-structured.
**Severity: med** (narrow — requires a future non-block-scalar YAML use — but a hard parse failure,
not silent corruption, so it fails loud rather than lying).

**Gap 3 — the escape is itself typable into a directive, which is the exact objection D-05 raises
against a NOSCAN token.** D-05's own `because` rejects a suppression marker on the ground that
"anything a dispatcher can type into a quote can also be typed into a directive." That argument
applies unchanged to `[.]harness/`: nothing mechanically distinguishes a correctly-applied escape
(a genuine quote) from the same spelling misapplied to a genuinely-bad directive to silence a real
refusal. If that happens, dispatch-guard.sh does not see the reference at all (confirmed: `run_dir_refs`
only fires on the literal `.harness/` anchor), so the dispatch proceeds. The eventual write is still
refused — independently verified in `check-domain.sh`: `classify()`/`domain_check()` emit the literal
token `NOBODY` and exit 2 whenever no grant's glob matches the actual write target, and no grant in
`.harness/team-config.yaml` starts with `[.]harness` — so this is not a security bypass. But detection
moves from dispatch time to write time, reproducing — self-inflicted, through the fix's own escape
hatch — the exact "mid-run, build spine already open" cost `BRIEF.md`'s Problem section names as the
harm being eliminated. **Severity: med** (bounded by check-domain.sh as an independent backstop, and
mitigated by REQ-02 surfacing the compliant form first, but a genuine, unaddressed gap in the design's
own stated non-goal).

*(Checked and dismissed: markdown-link collision — `[.]harness/` is never followed by `(url)`, so it
never parses as a link; shell **glob** collision — bash's default dotfile protection means a bracket
expression is not treated as an "explicit leading dot," so `[.]harness/...` left unquoted in a glob
does *not* expand to the real `.harness/...` path, tested live. Recorded so neither is re-raised.)*

## 3. Detector re-derivation — independently confirmed, not inherited

Built the regex from T-01's own spec (anchor on literal `.harness/`; slug class
`[A-Za-z0-9._-]+`, trailing dot/comma stripped) and ran it directly against `plan.yaml`, `BRIEF.md`
and `STATE.md` at HEAD, plus a positive control:

- `plan.yaml`: **0 matches.** `BRIEF.md`: **0 matches.**
- `STATE.md`: 1 match, `runs/planpanel-c1-validator` — compliant (`*-validator` grant).
- **Positive control fired**: the same regex against `runs/planpanel-validator/digest.md` (a cycle-0
  artifact) returns 4 matches, including the raw `eng-t01` anchor quoted in finding text — proving
  the search isn't vacuously empty.
- The three raw grant globs in T-01's intent WHY paragraph (`.harness/*/features/*/runs/*-eng/**`
  etc.) do not match: the slug class starts at the character right after `/runs/`, which is `*` for
  each of them — `*` is not in `[A-Za-z0-9._-]+`, so the match fails to anchor there. Confirmed by
  direct regex execution, not by trusting that the character class excludes it.

The orchestrator's claim holds under independent re-derivation from the plan's own specification.
**No self-refusing reference survives in plan.yaml or BRIEF.md.**

## 4. What the revision added — first read

- **REQ-06 / SC-08 / T-02 case (h):** sound. Case (h) matches SC-08's text exactly, including the
  `HARNESS-FEATURE:` first-line requirement and the assertion that the second dispatch's own stderr
  carries no run-dir refusal. Red proof present: delete the anchor rewrite, watch (h) fail at exit 2.
- **SC-09 / T-02 cases (e)+(i):** sound, and mutually exclusive by construction — (e) exercises a
  grant-less-but-parseable manifest, (i) a garbage/unparseable one, each asserting its own text
  present and the other's absent. Red proof: collapse the two SKIPPED lines into one, watch one of
  the pair fail. **Not scope creep** — SC-09 directly closes cycle-0's PF-64c48fa9 (a documented panel
  finding), and adding an SC in a pre-signature plan-phase cycle in direct response to a panel finding
  is the intended plan-panel loop, not an unauthorized expansion of a signed plan. It does commit to
  behavior REQ-05's literal text didn't specify (two distinguished reasons, not merely "a" reason,
  plus a second team-config.yaml parse per governed dispatch) — already surfaced correctly as
  STATE.md's open question Q4 for the operator at signature; I concur with that framing and raise no
  separate objection.
- **T-03's six-string `verify:`:** checked the string itself against the exact sentence the intent
  tells the doer to write. All five plain-prose phrases appear intact in sentence one
  ("dispatch-guard.sh refuses a governed dispatch that names a run-dir path whose slug matches no
  run-dir write grant in .harness/team-config.yaml, at exit 2, naming the offending slug and a
  compliant form, and the check is on slug shape and is not on ownership by the dispatched persona"),
  and the literal `[.]harness/` is mandated verbatim in sentence two. Ran the `tr -s`/`case` construct
  against both a compliant fixture (all six present → `test "$ok" = 1` passes) and a mutated one
  (phrase changed, exit code changed → correctly reports `MISSING:` and fails) — the construct
  discriminates as designed. Confirmed independently that none of the six required substrings exists
  in `.claude/skills/harness/SKILL.md` today, so the verify is a genuine red-before-green gate, not a
  vacuous one.
- **D-05 itself:** covered in §2.

## `git status --porcelain` on the two reviewed paths (verbatim)

```
(no output — both plan.yaml and BRIEF.md are clean; this run modified neither)
```

## What I could not determine

- Whether a live Claude-Code hook's `python3` can `import yaml` (panel Q1) — already answered in
  D-03 by a dated orchestrator measurement; I did not re-measure it, per STATE.md's "Dead ends" list
  instructing not to.
- Everything about actual runtime correctness: nothing is built. Every severity above is a
  prediction about code that does not exist, except where explicitly marked "demonstrated" (the
  `grep`/YAML collisions, which I ran directly against real tools, and the detector re-derivation,
  which I ran directly against the real plan text).
