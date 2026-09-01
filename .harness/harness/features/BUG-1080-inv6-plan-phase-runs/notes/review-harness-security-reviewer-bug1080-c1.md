# Security review — BUG-1080 cycle-1 remedy, a2fb6c0b..e9b11035, worktree-verified

## Verdict: PASS, severity_max LOW, no must_fix

The cycle-0 HIGH (dead exemption, no producer) is closed for security purposes: the self-assertion
grants the actor no capability they did not already have (unchanged from cycle 0's MED,
non-escalating). The exact-match tightening (Panel Q2) genuinely CLOSES the case-fold/whitespace
divergence cycle 0 rated LOW — it only narrows the exempt set, which cannot widen a fail-closed gate.
One residual LOW survives: exact-match closes the *value*-enum divergence but not a *document-format*
divergence between the two validators' loaders, which I reproduced live. It is pre-existing, not
introduced or worsened by this delta, and requires the identical raw-Bash-write precondition cycle 0
already priced in.

## 1. Did tightening to exact-match close, widen, or leave unchanged the LOW cycle 0 rated?

**Closed**, for the case it targeted. Old: `str(entry.get("code_grade","")).strip().lower() != "n_a"`
accepted `"N_A"`, `" n_a "`, etc. as exempt while the schema enum `["n_a"]` rejected them — the exact
divergence cycle 0 measured live (`review-harness-security-reviewer-bug1080.md` §3). New:
`entry.get("code_grade") != "n_a"` — exact identity. Live-tested with my own case-variant fixture via
`case_inv6_case_variant_is_not_exempt` (passes) and by direct reasoning: an exact-match predicate is a
**strict subset** of a case/whitespace-tolerant one, so the exempt set can only shrink. A narrower
exempt set cannot open new Tampering surface in a fail-closed gate — no widening is possible by
construction. Confirmed correct.

## 2. Is there an input that's schema-INVALID and gate-EXEMPT? Yes — via the LOADER, not the value.

The remedy's comment claims "a document must never be schema-invalid and gate-exempt at the same
time: any deviation fails BOTH." True for the VALUE only. False for the DOCUMENT: `check-state.sh`
reads every `feature.json` through `harness_yaml.load_file` (YAML-tolerant, regardless of the `.json`
extension — this is documented, deliberate corpus-migration behavior, see `feature_schema.py`'s own
docstring on the JSON/YAML migration window). `feature_schema.problems_for_file`'s `.json`-suffix path
uses strict stdlib `json.loads` instead. **Reproduced live**: a `feature.json` identical to the real
corpus format except `"code_grade": n_a` (bareword, unquoted) —
- `json.loads` on it: `JSONDecodeError: Expecting value` → `feature_schema.problems_for_text` reports
  `"not valid JSON"` → **schema-invalid**.
- `harness_yaml.load_file` on the identical bytes: parses the bareword as the plain string `"n_a"` →
  `entry.get("code_grade") != "n_a"` is `False` → **not** appended to `code_reviewing_runs`.
- Ran the actual `check-state.sh` against a full temp `.harness` tree carrying this file: **exit 0,
  no INV-6 violation printed** — confirmed gate-exempt end to end, not just in the parser unit.

**This is pre-existing, not introduced by the delta.** The pre-remedy comparison
(`.strip().lower()`) produces the identical `"n_a" == "n_a"` outcome for this exact bareword vector —
tightening the comparison operator changes nothing about which document-level parse a bareword
survives. It is also the same threat shape cycle 0 already priced at LOW in §1/§3 of its note: it
requires a raw Bash write that bypasses `feature_json_write.write_feature_json`'s schema gate (the
sanctioned writer refuses malformed JSON before it lands), the same actor already has a
schema-unconstrained, zero-effort route to an identical outcome (forge `review_sha` to any string —
no enum on it at all), and it leaves the same review_sha-forgery detectability gap cycle 0 already
assessed. Recording as **assessed-and-dismissed for must_fix**, not a silent drop: the new code
comment's wording overclaims (it reads as a whole-document guarantee when it only established
value-enum parity) — worth narrowing the comment to "the code_grade *value*" the next time this
region is touched; not gating.

Padded/quoted/case/non-string values through BOTH layers, checked individually: `"N_A"` (quoted, case
variant) — schema-invalid (enum), gate-liable (exact-match fails) — consistent, no divergence.
`"n_a "` (quoted, trailing space) — same, consistent. Numeric/boolean values — schema-invalid (wrong
type), gate-liable — consistent. Unicode look-alike (Cyrillic а, U+0430, in `"n_а"`) — schema-invalid
(enum is codepoint-exact) and gate-liable (Python `!=` is codepoint-exact) — consistent, no bypass.
The only surviving divergence is the document-parse-format one in this section.

## 3. Does `case_inv6_producer_is_documented` discriminate?

Built my own mutant (copied the real `bin/` dependency set + a copy of `SKILL.md` with the new
`code_grade: n_a` paragraph excised) and ran the case function against it standalone: **turns red**
(`FAIL - ... nothing instructs any writer to stamp the key ...`). It genuinely catches the primary
regression class (paragraph deleted/reverted). It is, as designed, a substring test — it cannot catch
content present-but-negated, present-in-the-wrong-section, present-for-the-wrong-squad, or a doc that
says the right thing but no orchestrator actually follows. Those are code-review-shaped
(dead-instruction / discoverability) concerns, not capability gaps — nothing about the string's mere
presence grants or withholds an actor any access.

**Anchoring is correct.** `CHECK_STATE_BIN`/`SCRIPT` is used in the test file *only* to point the
`check-state.sh` subprocess under test (grepped every use); it is never consulted when resolving the
`SKILL.md` path, which is always `__file__`-relative. No env-controlled path reaches the file this
assertion trusts.

**Anomaly, not reproduced, not a bypass**: one of 5 live full-suite runs printed `FAIL` for this case
with no other change; the file content was verified correct via direct read both immediately before
and immediately after that run, and 4/5 runs (including 3 in immediate succession afterward) passed
clean. Did not root-cause; direct reads never showed corrupted/mutated content. Given this worktree is
shared with sibling review agents per the dispatch's own note, a concurrent filesystem touch by
another process is the leading candidate. Recorded per O-04 rather than smoothed over — flagged as a
non-blocking open question for QA, not treated as a security finding: the failure mode observed is
fail-safe (spurious red), never a spurious green that would hide a real regression.

## 4. New SKILL.md text / new INV-6 message — leakage or gate-weakening?

No. Both are internal doctrine prose naming a decision (DEC-207) and a key (`code_grade: n_a`); no
credentials, no instruction to omit a check, no instruction that weakens any *other* gate. Standard
secrets/injection sweep across the full 4-file + 4-feature-note diff: no credential-shaped strings, no
new subprocess/shell call sites, nothing to report.

## Threat model

- feature.json `runs[].code_grade` self-assertion via unauthenticated write (T): **mitigated: false**
  — unchanged from cycle 0's MED, no new capability over the pre-existing `review_sha`-forgery route,
  not this delta's to fix.
- check-state.sh value-comparison vs schema enum, case/whitespace (T): **mitigated: true** — closed
  by this delta's exact-match change.
- check-state.sh YAML-tolerant document parse vs feature_schema.py's `.json`-suffix strict-JSON parse
  (T): **mitigated: false** — pre-existing, unaffected by this delta, requires the same raw-Bash-write
  precondition already priced at LOW in cycle 0, no new capability granted.
