# UI review (Mode A) — FEAT-17 guard boundaries — 2026-08-11

**Verdict: PASS.** The decline to write `DESIGN.md` is correct. One finding below (a text
assertion gap, not a design-contract gap) is worth carrying forward; none of this blocks.

## 1. The decline

Checked directly against `plan.yaml`, not accepted from the designer's note: every file in every
task's `files:` list is `.claude/skills/harness/bin/*.{sh,py}` or `docs/harness/*.md`. No markup, no
stylesheet, no component, no rendered surface — a file-extension census (this role's own P-01/P-04
pattern) turns up nothing to grade against a spacing/colour/type/theme contract. The designer's ruling
("nothing renders, nothing is operated") holds on inspection, not just on the designer's word for it.
`DESIGN.md` absent here is `n/a` under DEC-173, not a gap.

## 2. The contested surface — stderr/INV-25 verdict text — is NOT a design surface

Ruling on it myself, as directed, and correcting the designer's supporting claim on the way:

- **No applicable vocabulary.** Palette, type scale, spacing, light/dark, component direction — none
  of this role's contract fields resolve to anything on a stderr line. A `DESIGN.md` here would
  contain only wording rules, which is a content-design artifact, not this role's.
- **The wording is pinned, but the designer overstated how much of it is checkable.** The designer's
  note claims "SC-01, SC-04 and SC-08 already pin the text with literal-string and exit-code
  assertions." Verified against `BRIEF.md` directly, criterion by criterion, for each of the four new
  verdict surfaces:
  - Write-route target-side (SC-01): **text pinned** — `stderr contains .claude/worktrees`.
  - Bash-route target-side (SC-02): exit code only, no stderr text asserted.
  - Root-side, both routes (SC-03) — the surface carrying A-01's self-deleting instruction below:
    **exit code only, no stderr text asserted.**
  - Creation refusal, T-04 (SC-04): **exit codes only for every forbidden/allow pair, no stderr text
    asserted anywhere in the criterion.**
  - INV-25 (SC-08): text pinned — "prints an INV-25 line naming the sibling path" — but that covers
    only the detection line, not the remedy clause (`git worktree remove` / `prune`).
  So two of five new-verdict surfaces have a checkable text assertion; three, including the one
  carrying the actual defect this review found (A-01), do not. That does not reopen `DESIGN.md` — a
  markdown contract restating wording rules would still be a second authority for one string (the
  REQ-05 defect shape applied to prose) — but it does mean the wording is not yet checkable everywhere
  the designer implied it was. The remedy is a criterion, not a design contract.
- **Existing convention already governs the shape.** Confirmed by grep: `check-domain.sh` and
  `bash-write-guard.sh` both follow one actionable-rejection pattern (`check-domain.sh:641`,
  `ACTIONABLE REJECTION (DEC-100b)`) — name what's refused, name what may be written instead. The new
  verdicts extend an existing convention rather than inventing one that would need a fresh contract.

Agreement, independently reached and now better-supported than the designer's own framing: **PASS on
the decline.**

## 3. What the decline gives up — one real item, correctly kept advisory

**A-01 (root-side wording) is the substantive one and I reinforce it.** T-02's root-side verdict tells
an agent standing inside a misrooted worktree to remove that tree with `git worktree remove`. The
designer's own measurement (`git worktree remove .` from inside a linked worktree exits 0 and deletes
the directory the session occupies) is a real hazard, and — per section 2 above — SC-03, the criterion
covering exactly this surface, asserts only exit codes. A message telling an agent to delete its own
cwd would pass SC-03 as written with no test noticing. This is a coverage gap (P-08: a specified
message with no enforcing criterion), and the fix is a criterion plus a wording change to T-02's
intent, not a `DESIGN.md`. Kept advisory per this run's dispatch and because no REQ names message
content precision — but it is the one item I'd want the plan owner to see before signature.

A-02 (undeterminable-destination wording) and A-03 (em dash vs hyphen, confirmed at `plan.yaml:202,286`
against runtime convention at `check-domain.sh:219,268,660` and `bash-write-guard.sh:324,353,364`) are
minor, correctly non-blocking.

## 4. Explicitly out of scope for this feature

Accessibility and dark/light theme parity have no referent — there is no rendered surface, no colour,
no component tree, no dimension for either to apply to. No rendered dimension exists in this diff, so
nothing here is structurally invisible to a source-level audit (unlike a diagram-shrunk-to-thumbnail
case, where the unobservable dimension exists but this role can't see it) — there is simply no such
dimension in this feature at all.

## Open items

- SC-03 (root-side verdict, both routes) and SC-04 (creation refusal) assert exit codes only; neither
  requires stderr text. A-01's hazard — the root-side line telling an agent to delete the tree it is
  standing in — could be introduced or reintroduced without any criterion catching it. Recommend the
  plan owner add a text assertion to SC-03 before signature, or explicitly accept the gap.
  Non-blocking for this review.
