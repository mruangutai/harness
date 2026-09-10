# Receipt — harness-ai-dev — planreview-eng — ALTITUDE angle

Flag-only pass over the DRAFTED plan (`plan.yaml` @ resolved lanes `abff2a84`) and `BRIEF.md`. No
edits made anywhere; findings below route to `harness-pm`. Contract items (lane assignments,
`.agents/` symlink, `plan-merge.py`'s missing verbs, the bedrock corpus rule) are NOT re-litigated.

## Item 1 — relocate-the-sweep vs repoint-every-reader (the one that carries the most weight)

Checked `.claude/settings.json`'s actual hook registrations, not assumption: **only**
`check-domain.sh` (PreToolUse/PostToolUse `Write|Edit`), `merge-gate.sh` (PreToolUse `Bash`), and
`dispatch-guard.sh` (PreToolUse `Task|Agent`) are registered hooks. `check-state.sh`,
`board_lifecycle.py`, `check-plan-routes.py`, `validate-feature-json.py`, `layout_migration.py`
appear nowhere in `.claude/settings.json` — nothing binds them to firing from inside the calling
session's cwd.

- **Genuinely must run in place** (a PreToolUse hook cannot relocate, and `check-domain.sh`'s
  `_hardlink_plan` additionally needs real on-disk inodes no history read can supply): **T-05**
  (`merge-gate.py`), **T-06** (`check-domain.sh`), **T-12** (`dispatch-guard.sh`).
- **Would have no problem left if the sweep simply ran where the corpus is complete**: **T-03**
  (`check-state.sh`) and the four in **T-04** (`board_lifecycle.py`, `check-plan-routes.py`,
  `validate-feature-json.py`, `layout_migration.py`). Nothing hook-binds them to the caller's cwd;
  invoking them with cwd (or an explicit root argument) pinned to `corpus_root()` up front would
  make every one of their sweep sites see a complete corpus by construction, with no
  materialised-vs-resolved comparison needed at all.

**Verdict: SILENT, and the silence is not acceptable in a plan going for signature.** None of
D-01–D-10 states why per-call-site repointing (T-03: 21 sites; T-04: one site per module across 4
files — ~25 sites total, each independently deciding "materialised? else `corpus_read`") was chosen
over relocating the five non-hook-bound scripts' invocation (5 sites) to the owner root. If SC-04's
literal "refuse with N of M when materialised < resolved" behaviour is genuinely required for these
five specifically — not just "never report clean on a partial view", which relocation would also
satisfy by construction — that is worth one sentence in a decision. As written, the plan pays for
~25 edited call sites in the tree's most-run gate script with no recorded reason the cheaper
alternative was insufficient.

- **T-03, T-04 / no `D-NN`** · plan.yaml T-03 intent (`check-state.sh`, 21 sites) and T-04 intent (4
  modules) vs. `.claude/settings.json`'s hook list · Five of the seven "sweep" readers are not
  hook-bound, so relocating their invocation to the owner root was structurally available and never
  addressed. · Cost: 25+ call sites edited in the highest-traffic gate script instead of 5 invocation
  points, and the next editor who touches 24 of the 25 correctly and misses one silently reopens a
  fail-open in exactly the file this feature exists to close. · Alternative: record (a `D-11`) either
  why the local-vs-corpus comparison shape is load-bearing for these five, or that relocation was
  considered and rejected and why. · severity: high · **briefing-row**

## Item 2 — is D-02's refusal predicate at the right altitude

T-01, verbatim: "compare the number of feature directories MATERIALISED under `os.getcwd()`'s own
checkout against `len(resolved)`." `corpus_root(cwd)` takes `cwd` as an explicit argument one call
earlier; `corpus_features(root, ref=None)` then reaches for a second, independent `os.getcwd()` call
instead of accepting the same value the caller already resolved and passed to `corpus_root`. The
thing being compared (the caller's local checkout) belongs to the caller's own accident of location,
and threading it explicitly — rather than re-deriving it from ambient process state inside the
shared authority function — is what keeps the two calls from silently diverging if a caller ever
chdirs between them (a wrapper, a test harness, a subprocess).

Predicate I would specify: `corpus_features(root, ref=None, local_root=None)`, `local_root`
defaulting to `os.getcwd()` for convenience but every real caller passing the same `cwd` value it
already threaded into `corpus_root(cwd)`.

- **T-01** · T-01 intent, `corpus_features` refusal clause · Refusal predicate re-derives the
  caller's location via a second `os.getcwd()` instead of accepting the value already resolved by
  `corpus_root(cwd)`. · Cost: a caller whose cwd differs between the two calls gets a refusal (or a
  pass) keyed to the wrong checkout, silently, and every test of the refusal path must monkeypatch
  global process state rather than pass a value. · Alternative: add an explicit (defaulted)
  parameter and thread the one `cwd` value through both calls. · severity: med · **fold-in**

## Item 3 — every accepted residual, and whether its named control can fire

- **D-05** (presence-not-correspondence) · D-05 "because" text, cites D-08's lint (T-13) as "the
  partial instrument." Checked: T-13's lint targets exactly the stated failure mode ("a stale glob
  against its own working tree"), so the named control does fire for that case. But D-05's own
  residual is broader than what "partial instrument" discloses — it says nothing about a caller that
  calls the real API (`corpus_read`/`corpus_features`, not a bypassing glob) with a ref/provider
  value that simply does not match the declared `HARNESS-CORPUS-REF`/`PROVIDER`; T-13 is a
  static-shape lint and cannot see a runtime argument value. Cost: a task can declare
  `corpus: {provider: history, ref: main}`, pass `dispatch-guard.sh`, pass T-13's lint (it's a real
  API call, not a glob), and still execute `corpus_read(path, ref="stale-branch")` — the exact
  fail-open, now behind two green checks instead of zero. Alternative: narrow D-05's own wording to
  name precisely what the lint covers (bypass-via-enumeration) versus what it does not
  (wrong-argument-to-the-real-API), so "partial instrument" isn't read as "closes most of the gap."
  severity: med · **briefing-row**

- **D-06** (blind `cmd_remove` dirty check) · D-06 "because" text, cites DEC-208/DEC-218. Checked:
  those decisions bind writes routed through the harness's own domain-guard hooks to the registered
  worktree — they say nothing about an out-of-band write (a direct filesystem edit, an external
  tool, a bug elsewhere) landing content in a SKIP_WORKTREE-hidden path without going through that
  routing, which is precisely the population this residual is about. Cost: citing DEC-208/218 as
  what makes the residual acceptable overstates the coverage — the real boundary is "no write path
  outside the harness's own routing is expected to exist," a narrower and different claim than "all
  legitimate writes are bound." Alternative: narrow D-06's wording to state which writes DEC-208/218
  governs and which it doesn't, so a later reader deciding whether to reopen this knows the actual
  boundary. severity: low · **briefing-row**

- **BRIEF SC-11 vs T-14** (the two authoritative statements disagree) · BRIEF.md SC-11 row states
  `verify: inspection` and "Prose has no gate at all... only the reviewer catches it." T-14 mandates
  `tests/integration/test-corpus-prose-anchor.py`, an automated test asserting the anchor token's
  presence and the absence of a live enumerate-instruction, paired with a positive control — that
  is an automated gate for the token-presence half of SC-11, contradicting BRIEF's own stated
  verification mode for the same criterion. Cost: a reviewer relying on BRIEF's "Verification gaps"
  section alone will believe SC-11 has zero automated coverage and may skip confirming T-14's test
  actually ran, since BRIEF told them no such test exists. Alternative: correct BRIEF's SC-11 row to
  `verify: automated  evidence: integration` (matching what T-14 delivers) and narrow the
  "Verification gaps" prose to state only the semantic-fidelity residual (correct prose can still be
  misread) is reviewer-only — not the token's mere presence. severity: med · **fold-in**

(SC-06/SC-07's "no runner exercises real host state" residual is not flagged: its compensating
control — the per-worktree record plus reviewer read, with the closing gap named as a dev-ops
backlog item — is honestly scoped and already states its own limit. **leave**.)

## Item 4 — a capability planned into ~25 callers that belongs in the module they call

T-03 and T-04 each instruct their call sites, independently, to implement: "is this path
materialised locally? if not, `corpus_read` at the resolved ref" — 21 sites in `check-state.sh`
(T-03) plus one per module across four files (T-04), all restating the identical branch that is
never itself given a name in `harness_boundary.py` alongside `corpus_root`/`corpus_features`/
`corpus_read`.

- **T-03, T-04** · T-03 intent ("read it through corpus_read at the resolved ref when the path is
  not materialised"); T-04 intent, same clause repeated per module · A materialised-or-corpus-read
  branch is specified once in prose but implemented independently at ~25 call sites in 5 files,
  never owned by the module it calls into. · Cost: a later change to this branch (handling a
  symlinked path, adding a content cache, changing what "materialised" means) needs coordinated
  edits across 25 sites in 5 files; an editor who updates 24 correctly and misses the 25th
  reintroduces a silent divergence — the same "several statements of one rule that can drift" shape
  this angle exists to catch, at a much larger blast radius than Item 5's four prose surfaces. ·
  Alternative: add a fourth function to `harness_boundary.py` alongside T-01's three (e.g.
  `corpus_open(local_path, root, ref)`) that owns the branch and returns content exactly as
  `corpus_read` does (`None` absent, `""` empty); every call site calls this one function instead of
  re-deriving the branch. · severity: high · **fold-in**

## Item 5 — the corpus-declaration mechanism, counted

The same mechanism — a task declares `corpus: {provider, ref}`; `dispatch-guard.sh` refuses at exit
2 without a matching declaration in the dispatch text; presence is checked, correspondence is not —
is stated in **four** places: **D-05**'s decision prose, **T-12**'s task intent, the one-sentence
code comment **T-12** itself mandates inside `dispatch-guard.sh`, and the paragraph **T-14** adds to
`harness-spec-driven/SKILL.md`. Nothing cross-references any of the four to the others, so nothing
forces the comment or the skill paragraph to track D-05's wording if the decision is later amended.

This repository's own recorded Expertise (repo-tier G-02) already names an identically-shaped
recurring gotcha — a decision's transcription duplicated into a code comment and a persona file with
no test cross-checking the two — observed drifting silently once already (`plan-panel.yaml`'s
closing comment vs. `harness-validator-lead.md`'s "Hosting plan-panel" section). This plan is about
to create a third instance of that shape, now across four surfaces instead of two.

- **T-12, T-14 / D-05** · D-05 (decision text); T-12 intent + mandated guard comment;
  `harness-spec-driven/SKILL.md` (T-14) · One mechanism restated in four places with no designated
  authority and no cross-check. · Cost: an edit to D-05's residual wording (e.g. if D-08's lint is
  later strengthened) has no forcing function to reach the guard's comment or the skill paragraph,
  so the two surfaces most likely to be read by a future dispatching agent go stale first, exactly
  as this repo's Expertise already records happening elsewhere. · Alternative: keep D-05 as the sole
  authoritative statement; have T-12's guard comment and T-14's spec-driven paragraph each cite
  "see D-05" rather than re-deriving the residual's wording independently. · severity: med ·
  **briefing-row**
