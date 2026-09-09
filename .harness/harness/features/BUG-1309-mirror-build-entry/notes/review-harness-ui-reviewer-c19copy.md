# UI review — c19 · BUG-1309 · operator-copy delta at 4857818b

**Mode B, narrow.** Surface is CLI/hook operator text (`permissionDecision: deny` reason strings),
not a rendered UI — no DESIGN.md, no theme/WCAG axis applies here (correctly out of scope per
dispatch). Read: `merge-gate.py:160-198` (full deny/print block), the delta diff, the rulings note,
BRIEF SC-04/SC-10, plan.yaml D-19, and `notes/uat-BUG-1309-mirror-build-entry.md` Steps 3, 3b, 6.

## 1. SC-10 — actionable without reading source?

**Satisfied.** Rendered: `merge-gate: FEAT-9001-uat-scratch needs its GitHub mirror recovery
completed before this merge can continue. Run: python3 .claude/skills/harness/bin/gh-sync.py open
/private/tmp/bug1309-uat/.harness/harness/features/FEAT-9001-uat-scratch`. The operator must already
know what "GitHub mirror" refers to as a harness concept (still true of the old copy too), but that
is the ceiling of what a one-line refusal can teach — the load-bearing improvement is that the
*fix* no longer requires understanding a config field. The old sentence required parsing
`github.build_entry=<value or "absent">` and inferring what value satisfies it; the new one gives a
complete, copy-pasteable remedy command and states the blocking condition in plain English with zero
internal field names. An operator who does not know what "GitHub mirror recovery" means can still
comply by running the printed command. This is a real improvement, not just a rewrap.

## 2. SC-04 — feature named, command given; is the double-naming noise?

**Satisfied, and the redundancy is not noise.** `{feat}` names the subject in the English clause;
`{command_line}` independently contains the feature slug because `os.path.realpath(feat_dir)` is
a directory path, and the path segment is a *required argument*, not a second naming for emphasis.
An operator reads them as two different things — "who" (prose) and "what to type" (code, visually
set off by `Run:`) — not as the same fact stated twice. No finding here.

## 3. Sibling-message consistency — the real finding

**Read:** `merge-gate.py:174` (ambiguity), `:180` (era-exempt stderr), `:188` (repo-unpinned),
`:194` (exception). Only `:192` changed.

- `:174` (ambiguity deny) — plain English already (“cannot be attributed to one feature… Correct
  the duplicated top-level branch field”). Reads consistently with the new `:192` tone. No finding.
- `:194` (exception deny) — plain, if slightly vague (“Repair the feature record”). Consistent tone.
  No finding.
- **`:188` (repo-unpinned deny) still opens with `{feat} records github.build_entry={value}, and
  this project has github.sync true with github.repo NOT pinned…`** — this is the *identical
  jargon pattern* (`records github.build_entry=<value>`) the operator explicitly rejected in
  ruling §2 for `:192`. It also splices a bare decision id, `(D-09)`, into operator-facing prose.
  Before this commit all four deny paths shared one voice; now `:192` reads like a different,
  more careful author than `:188`. This is a **finding, but not a defect introduced by this
  delta** — it is a pre-existing message the ruling's own scope table (§3) explicitly marks
  "untouched" and confines this authorization to `:192` only (§1: "Not… the unpinned-repo branch").
  Flagging for backlog, not gating this commit.
- **`:180` (era-exempt stderr)** carries `feature_schema.BUILD_ENTRY_ERA_EXEMPT` — a raw Python
  constant name — directly in operator-facing text, plus "terminal receipt" jargon. Lower stakes
  (informational allow-path stderr, not a blocking deny) but same category of leak. Pre-existing,
  untouched, backlog.

## 4. The `merge-gate: ` prefix — keep, endorsed

Right call. Every sibling message carries it, the UAT's observation steps key off it to attribute
the speaking gate, and stripping it would remove the one piece of "who is talking to me" context a
plain-English deny still needs. Ruling correctly logged it as reversible; nothing depends on
striking it, and nothing argues for striking it either.

## 5. UAT quote fidelity + Step 6 regression check

- Step 3 quoted block (`:159-164`) matches the actual rendered string character-for-character
  against the real `merge-gate.sh` invocation recorded in the dispatch's own measurement.
- Step 3b's inline quote (`:209-211`) uses `…` to elide the path, consistent with a paraphrase, not
  a literal-quote break.
- Step 6 (`:300`, "a `deny` naming `recover-terminal … --yes` — not `open`") **stays true.** The new
  sentence template is generic — `Run: {command_line}` — and never hardcodes the token `open`
  anywhere in the fixed English portion; which command name appears is entirely a function of
  `feature_schema.recovery_command_for(feat_dir)`. For a `recover-terminal` fixture the rendered
  command reads `...gh-sync.py recover-terminal <dir> --yes`, so Step 6's expectation is preserved
  by construction, not by luck.

## Verdict rationale

The delta itself (`:192` + the two re-anchored predicates) is correct, matches the operator's
verbatim-chosen sentence in D-19 and the rulings note byte-for-byte, and does not regress any
downstream UAT step. The one real defect found (`:188`'s surviving jargon, now thrown into relief
by its fixed sibling) is explicitly out of this commit's authorized scope and does not gate — it is
recorded as a backlog item, per ruling §1's own confinement.

## Findings

| id | severity | summary | file:line | status |
|---|---|---|---|---|
| F-01 | med | `:188` repo-unpinned deny still reads `{feat} records github.build_entry={value}` — the exact jargon phrase the operator rejected for `:192` in this same cycle — and inlines a bare decision id `(D-09)`; now tonally inconsistent with its just-fixed sibling. | `.claude/skills/harness/bin/merge-gate.py:188` | pre-existing, untouched by this delta, backlog (ruling §1/§3 scope it out) |
| F-02 | low | `:180` era-exempt stderr line leaks the raw Python constant name `feature_schema.BUILD_ENTRY_ERA_EXEMPT` into operator-facing text. | `.claude/skills/harness/bin/merge-gate.py:180` | pre-existing, untouched by this delta, backlog |

No must-fix findings against the reviewed delta itself.

## UI review answered

- fidelity: n/a (no DESIGN.md/rendered surface)
- states: n/a — CLI batch text, no loading/empty/overflow states
- interaction: n/a — no focus/keyboard surface
- accessibility: n/a — no colour-only state encoding; plain stdout/stderr text
- theme parity: n/a — no theming surface
- **usability/copy (this delta's actual axis):** PASS — SC-10 and SC-04 both satisfied by the new
  string; UAT quotes verified to match rendered output; Step 6 regression checked and holds.
