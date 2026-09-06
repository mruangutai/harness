# UI review — BUG-1305-run-state-clobber — review-c1 — pin `dc0e0313`

## Measured census

`git -C <worktree> diff --name-status origin/main...dc0e0313` → **48 files.** By kind: 4 shell
(`.sh`), 8 Python (1 new `run_identity.py` + 7 modified, incl. 10 test files under `tests/`),
1 `.json` (`feature.json`), 1 `.yaml` (`plan.yaml`), 30 `.md` (BRIEF/STATE/DECISIONS/SKILL.md +
every `notes/`/`observations/` file). **Zero** rendered-UI extensions (html/css/scss/tsx/jsx/vue/
svelte/less) — 0 hits, all counted. **No `DESIGN.md` exists for this feature**
(`glob **/DESIGN.md` under the feature dir → no matches). Every `.md` file present is either the
spec of record, a plan/decisions log, or a per-agent note/receipt — none is a rendered-surface
design contract. **Conclusion: no rendered UI surface in this diff.** This is Mode B territory with
`in_scope: false` for the rendered-UI half of my remit.

## What I reviewed instead — operator-facing guard text

Per dispatch, the one surface arguably in my lens on a pure-guard diff is the **text a human
operator or a blocked writer actually reads** — the SC-01(c)/SC-03-graded refusal and detection
messages. I read them at the pin (`git show dc0e0313:<path>`, confirmed byte-identical to the clean
working tree — `git status --short` and `git diff --stat dc0e0313 -- <these 4 files>` both empty).
**Not applicable / no finding:** colour-only state encoding, contrast, theme parity — this is
stderr/stdout text with no colour channel at all.

**SC-01(c) message** (`check-domain.sh:~1697-1704`, `uid_conflict()` body in `run_identity.py:130-141`):
for an incoming checkpoint carrying no `run_uid` against a present prior carrying U1, the emitted
text is: *"the existing checkpoint belongs to run_uid 'U1'; this write cannot be shown to update
that run. A run that owns the record must carry its run_uid line forward verbatim from the
checkpoint it is updating; the same value is recorded in the witness beside it; if this write does
not belong to that run, write this cycle's state into a run directory of its own."* This **meets**
the BRIEF's SC-01(c) falsifiable text (names U1 ✓, says where it is recorded — "in the witness
beside it" ✓, tells a non-owning writer to use its own directory ✓) and **also** discharges REQ-01's
"cost of the identity refusal" bound for the legitimate-owner-who-dropped-`run_uid` case, which
reads the *same* code path: it names the exact value to carry forward and where to read it. One
message correctly serves two different readers (foreign writer / owner who dropped the field) with
distinct, sequenced instructions. No finding.

**SC-03 detection wording** (`check-state.sh` INV-36, lines ~1493-1514): both the field-disagreement
and `run_uid`-disagreement branches emit `"INV-36: {rel}: the checkpoint occupying this run
directory records an identity that disagrees with the identity recorded when the directory was
first written: {reason}. The checkpoint the witness describes is the record that was lost; the
occupying file belongs to a different run."` — names the run directory, embeds both disagreeing
values via `conflict()`/`uid_conflict()`, and never touches INV-16's `"non-checkpoint top-level
key(s)"` string (confirmed by direct grep of both literals). Malformed-shape and clobber are also
**structurally** unconfusable at the control-flow level: a parse failure or non-mapping `sdoc`
`continue`s at lines ~1435/1439, before the INV-36 block is ever reached — a malformed file can
never carry both findings in the same pass. No finding; SC-03 is met as written.

## Finding — low, advisory

**UI-01 (low).** Two sibling "witness unreadable" messages, both new in this diff, state the fact
with no remedy, unlike their SC-13 sibling which does:

- `check-domain.sh:1641-1643` (PRE, Write/Edit route, `MarkerUnreadable` on the *prior's* witness):
  `"this run directory's recorded identity cannot be read, so a Write that could silently replace
  another run checkpoint is refused."`
- `check-state.sh:1487-1491` (INV-36 detection, same exception): `"INV-36: {rel}: its recorded run
  identity cannot be read, so whether the checkpoint occupying this directory belongs to it cannot
  be determined."`

Compare the write-once-witness refusal a few lines above in the same file
(`check-domain.sh:~1697-1704`'s `RE_RUN_IDENTITY` block, graded by SC-13), which for the *analogous*
human-repair case explicitly says *"a witness a human genuinely must repair is repaired outside the
guards."* The two MarkerUnreadable messages above give an operator no such pointer: a human hitting
either message knows a write was refused or an invariant is undecidable, but not that the file in
question is `.run-identity.json`, nor that hand-repair (outside the guards) is the expected recovery
path. **Concrete scenario:** an operator sees `INV-36: runs/2026-09-05-02-lead: its recorded run
identity cannot be read...` in a `check-state.sh` sweep with dozens of other findings, and — with
no filename and no remedy — has no way to distinguish "go read `.run-identity.json`'s permissions/
encoding" from "this run is now permanently unrecoverable." **Remedy:** name the file
(`.run-identity.json`) and add the same "repaired outside the guards" pointer the SC-13 message
already carries, in both locations. **Ship ruling:** this is **not gated** — it isn't part of
SC-01(c)'s, SC-03's, or SC-13's falsifiable text (all three are satisfied as written; this is a
*different*, ungraded branch), the scenario it covers is a witness file the harness itself creates
and no governed route can corrupt, and it can be **ruled on at ship with the finding in front of the
operator** — accept the terser wording as-is, or file it as a small follow-up wording tweak. It does
not require rework to land this feature.

## Declined

- Fidelity/spacing/contrast/theme-parity/interaction-state dimensions of the standard Mode B table:
  **n/a** — no rendered surface exists to hold any of them.
- REQ-06/SC-06's corrected `check-domain.sh` inline comment (the "intentionally Write/PRE-only"
  fix, `check-domain.sh:~110-114` in the diff): a developer-facing code comment, not an emitted
  operator message — code-reviewer's lens, not mine. Declined.
