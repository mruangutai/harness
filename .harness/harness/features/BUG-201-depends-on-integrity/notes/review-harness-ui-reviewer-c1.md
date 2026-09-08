# UI Review — BUG-201-depends-on-integrity — cycle 1 (Mode B)

**Verdict: PASS (measured decline on rendered UI; advisory-only note on in-remit CLI text).**

## What I measured

1. **DESIGN.md existence** — grepped the feature dir
   (`.harness/harness/features/BUG-201-depends-on-integrity`) for `DESIGN.md`, `prototype`,
   `mockup`: zero matches. `find … -iname "*design*"` in the feature dir: zero matches. No
   design contract exists for this feature, and none is warranted — see (2).
2. **Rendered-UI census** — `git diff --name-only af859ee8 6896ebe7c02df49df7b9d8c5f6e7a92a37dcd5e4`
   (34 files) grepped for `.html|.css|.scss|.tsx|.jsx|.vue|.svelte|.less`: zero matches.
   `git diff --stat` confirms the full changed set: 3 production `.py` files
   (`harness_yaml.py`, `factory_claim.py`, `gh-sync.py`), 6 test `.py` files, and the rest is
   plan/receipt/note markdown and `feature.json`/`STATE.md`. No file in this diff renders a
   user-facing surface. Mode B has no rendered UI to audit.

## In-remit surface: operator-facing CLI text (dispatch-named, per P-06/G-06)

Two new stderr lines surface the real cause of a dangling `depends_on` instead of the prior
silent-swallow-to-`{}`/`None`:
- `gh-sync.py:1174` (`_projected_for`, via `refuse(..., stream=sys.stderr)`) and
  `gh-sync.py:1289` (`_status_plan_doc`, direct `print(..., file=sys.stderr)`).
- `factory_claim.py:218-220` (`_blocker_reason_text`, `bad_plan` branch) — surfaces as
  `factory_claim.py`'s new `bad_plan` blocker text, consumed by the poller (never gates it,
  per dispatch and D-05 — confirmed by reading the call site, not re-litigated here).

**Executed, not just read** — I constructed a real dangling-`depends_on` plan.yaml and ran it
through the actual `harness_yaml.load_plan` raise site, then applied gh-sync.py's and
factory_claim.py's exact message-construction lines against the live exception:

```
gh-sync: REFUSED — the plan at <path> failed to load — failed to parse YAML in <path>: depends_on names task ids absent from this plan - T-01 to T-99

issue #4242 carries a feature: label that resolves, but its plan.yaml at <path> failed to
load - failed to parse YAML in <path>: depends_on names task ids absent from this plan - T-01 to T-99
```

Both: one line, no traceback, name the concrete offending value (the specific dangling
`task-id to task-id` pairs) — meets the project's CLI-message bar.

**One advisory (non-gating) finding.** Both lines repeat the plan path twice (once in the
wrapper's own "the plan at `<path>` failed to load" / "plan.yaml at `<path>` failed to load",
once again inside `str(exc)`, which already begins "failed to parse YAML in `<path>`:" —
`PlanSchemaError` inherits `YamlParseError.__init__`'s parse-error framing even though this is
a schema/referential error, not a parse error). This reads verbose and mildly misleading
("failed to parse YAML" for a file that DID parse). I checked whether this is new: it is not.
The identical shape — `f"{path} … : {e}"` wrapping a `str(exc)` that already embeds the path —
is the established, unchanged convention at `check-plan-routes.py:370`, `check-state.sh:145`,
`upgrade-config.py:247,254`, and the sibling `refuse()` shape at `gh-sync.py:364-367`, all of
which predate this diff. Per Expertise P-11/G-11-class precedent, an unchanged pre-existing
convention that a new call site correctly follows is a non-gating note, not a defect to file
against this diff.

**Comparison to the dispatch-cited sibling** (`gh-sync.py:1160-1168`, the `FleetError`
branch, unchanged by this diff): `refuse(f"the plan carries a station outside the
vocabulary, so no card can be placed from it — {exc}")` — states cause AND consequence in one
clause. The new lines state cause only ("failed to load — {error}") without an explicit
consequence clause ("so no station is recorded" / "so this candidate stays blocked").
Consequence is discoverable from context (the caller already prints "no station follows from
the plan" / "station ready refused" alongside), so this is a stylistic gap, not a missing-fact
gap — advisory only.

## Accessibility / theme parity / interaction

N/A — batch CLI stderr text, no colour-only state encoding, no rendered surface, no dark/light
theme to check. (Per repo-tier Expertise P-01/P-03: this repo is files-only, no build step;
confirmed again here via the extension census.)

## DIGEST
See below.
