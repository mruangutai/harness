# UI review — BUG-124-run-dir-squad-suffix — Mode B — cycle c4 (review_sha 6c037de4)

## Verdict: PASS (advisory notes only, none gating)

## Census (measured, not predicted)

- `DESIGN.md` for this feature: **absent**. `git cat-file -e 6c037de4:.harness/harness/features/BUG-124-run-dir-squad-suffix/DESIGN.md`
  exits 128 ("does not exist in 6c037de4..."). No per-feature contract to audit in Mode B's usual sense.
- File-extension census of the four-file diff: 1 `.sh`, 1 `.py` (source), 2 `.py` (tests). Zero
  html/css/scss/tsx/jsx/vue/svelte/less. Confirms repo-tier P-01 (no rendered UI in this repo by
  default) — nothing here is a rendered surface.
- Read in full: the `dispatch-guard.sh` diff (both hunks, `artifact://1840`), `harness_boundary.py`
  lines 816–915 (all four new helpers' bodies, not just signatures), and grepped
  `tests/integration/test-dispatch-guard.py` case 18/20/22 for what wording the suite actually pins.
- Per dispatch: judged the one adjacent non-rendered surface named — the refusal string
  `dispatch-guard.sh` emits on stderr for an inverted run-dir slug (REQ-02/SC-02/SC-08). Accessibility
  and dark/light theme parity have no purchase on a stderr string — stated explicitly, not silently
  omitted (repo-tier P-03 applies analogously to a stderr string as it does to a print-only test
  suite; both are one-channel text with no colour-only state encoding).

## The refusal message, read in full (`dispatch-guard.sh:172-182`)

```
dispatch-guard: BLOCKED -- run-dir slug 'eng-t01' cannot be written by any squad lead.
  [.]harness/<repo>/features/<feature>/runs/eng-t01
  compliant forms: <task-or-purpose>-eng, <task-or-purpose>-product, <task-or-purpose>-validator
  the squad suffix trails the purpose -- the parent directory already carries the feature id.
  a run-dir path being quoted rather than directed is spelled with [.]harness/ in place of
  .harness/; the paths above are already in that form.
```

**Legibility / actionability (REQ-02, SC-02):** the two load-bearing facts — the offending slug
(`'eng-t01'`, plain quoting via `%r`, matches house convention already used at
`dispatch-guard.sh:101`/`245` for persona/path values) and the compliant forms
(`<task-or-purpose>-eng` etc., derived from `run_dir_forms()`, `harness_boundary.py:892-915`) — are
both printed **unescaped and in plain text**. A dispatcher does not need to parse the escaped tail
line to fix the dispatch; the fix ingredients are legible without it. `test-dispatch-guard.py:556-560`
pins exactly this pair as the contract, which is the right thing to pin.

## Finding 1 — LOW — SC-08 anchor rewrite orders the explanation after the confusing artifact

The escaped path (`[.]harness/...`) is printed on the line immediately under the BLOCKED headline;
the sentence explaining *why* it is spelled that way is the LAST line of the block, three lines
later. Concrete scenario: a dispatcher skimming stderr for "what path is broken" reads line 2
(`[.]harness/myrepo/features/BUG-124/runs/eng-t01`), sees a path that does not exist on disk with
literal brackets in it, and may paste or `cat` it verbatim before reaching the explanatory footer —
producing a "no such file" confusion the guard itself never has a reason to cause, since the
underlying real path (with a literal `.`) is never printed anywhere in this message. This does not
block REQ-02/SC-02 (the slug and the compliant forms are both stated plainly, independent of this
line) and does not touch SC-08's own correctness (paste-back safety is a behavioural property,
verified by `case_18_...` at `test-dispatch-guard.py:541-574`, and holds regardless of line order).
Advisory: leading with the one-line "why" before the mangled path would remove the moment of
confusion; not required to ship.

## Finding 2 — informational, non-gating — separator-style split predates this diff

New print lines use ASCII `--` (`"BLOCKED -- run-dir slug..."`, `"SKIPPED -- the manifest..."`);
sibling lines elsewhere in the same file use an em dash (`"BLOCKED — this governed dispatch..."` at
line 131, `"... — no claim recorded."` at line 101). Measured: the *pre-existing* file at `80ce35d1`
already mixes both (`git show 80ce35d1:.../dispatch-guard.sh` — 18 em dashes, 9 ASCII `--`, the T-09
block already using `--`). The new BUG-124 lines are internally consistent with themselves and with
the T-09 half of the existing split; they do not introduce a new inconsistency, only continue an
existing one. Per house precedent (P-11 in Expertise: don't file a fix against an untouched
pre-existing pattern), noting only — not a finding to remedy in this diff.

## Not applicable, stated rather than omitted

- **Accessibility** (contrast, colour-only state, labels): N/A. Stderr text carries no colour, no
  ARIA, no visual channel of any kind.
- **Theme parity** (light/dark): N/A. There is no theme; there is one terminal stream.
- **Interaction** (focus, keyboard, hit targets): N/A. There is no interactive surface — the message
  is read once, by a human, and the "interaction" is the dispatcher rewriting their own next
  dispatch prompt, which this note already judges under legibility/actionability above.

## Open questions

None blocking.

## expertise_update

`[]` — not a distillation dispatch.
