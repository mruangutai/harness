# Consolidated Advisor-consult note — BUG-1305 (plan phase)

## BLUF

The Advisor (`fable-advisor`) RAN and answered all five delegated design questions. Compressed to
one line each, all `[Advisor]`:

- **Q1** `[Advisor]` — Neither `<task-or-purpose>-<squad>` (DEC-145) nor `<YYYY-MM-DD>-<seq>-<squad>`
  (harness-team SKILL) is canonical; the Mode-A remedy must be grammar-independent, with one small
  doctrine-unification task routed to the operator's signature, defaulting to the date-seq form.
- **Q2** `[Advisor]` — Use a second identity signal (payload `session_id` and/or a hook-written
  write-once marker) alongside the existing human-legible `run_id`, not a machine-generated `run_id`;
  gate on one probe task confirming sibling lead spawns get distinct `session_id`s.
- **Q3** `[Advisor]` — Add post-hoc detection (a write-once per-run-dir marker plus a new
  `check-state.sh` invariant); detection does NOT subsume Q2's prevention for the identity-equal
  slug-reuse route, only for the already-forbidden `_no_parser` line-scan route.
- **Q4** `[Advisor]` — Do NOT wire `check-state.sh`/INV-15 to a hook; instead fix
  `validate-digest.py`'s `check_artifact_file` resolution and fail CLOSED when the digest is
  genuinely absent — `check-state.sh` already runs at every `/harness` entry per instruction, so the
  gap is latency, not absence.
- **Q5** `[Advisor]` — Close BOTH routes; the operator's own scope note forbids risk acceptance, so a
  plan that leaves either route open is not deliverable as written, and Q3's detection is therefore
  load-bearing, not optional.

The Advisor also disagrees with the diagnosis in two places (both material, see his preamble below).
My own independent re-verification of the four load-bearing claims his answers turn on is in the
"Reviewer's own" section — all four confirm.

---

## Advisor answers — fable-advisor, transcribed verbatim and unaltered

# Advisor answers — BUG-1305, five design questions

All citations are from the worktree at `.claude/worktrees/harness/BUG-1305-run-state-clobber/`, re-read today; line numbers are my own measurements, not the diagnosis's.

**Where I disagree with the diagnosis (two places, both material):**
1. **"No identity signal independent of run_id exists in the hook payload" is FALSE.** `check-domain.sh` itself reads `_session = d.get("session_id")` from the very same PreToolUse payload (check-domain.sh:1850, the FEAT-51 orphan-quarantine block) and `inflight_registry.py` already stores and compares that session id (`claim.get("session")`, inflight_registry.py:252-258, whose comment records "OMP child and parent sessions differ"). The signal exists and is already consumed two ways in this repo. What is genuinely unverified is its *discriminating power* — whether two lead spawns inside one compatibility-host session carry distinct session_ids — and that is a probe task, not an impossibility.
2. **"check-state.sh is never invoked automatically" is overstated.** It is registered in no settings.json hook (true — I read `.claude/settings.json` in full), but `.claude/commands/harness.md:11` mandates "Run `.claude/skills/harness/bin/check-state.sh`" at every `/harness` entry, and harness-init's SKILL (:291-293) records the operator's own premise that "that gate runs at every /harness door and before every commit." INV-15 therefore runs at a real, recurring cadence — instruction-enforced rather than hook-enforced. The Mode-B gap is latency and instruction-reliance, not absence. This changes the right answer to Q4.

Everything else in the diagnosis I checked held up: the `str(prior_run_id) != str(new_run_id)` compare is the only identity test (check-domain.sh, Issue #1124 block, ~:1560-1575 in my read); the `_no_parser` bare `return out` precedes it (~:1476) and its comment records the line-scan fallback was "REMOVED at the user's ruling" under a signed BRIEF; `validate-digest.py`'s `check_artifact_file` fails open on unresolvable paths and names INV-15 as backstop (validate-digest.py:1493-1503 docstring and the :1546-1549 stderr message); the stale comment at check-domain.sh:1237-1238 ("intentionally Write/PRE-only") does contradict the Edit-reconstruction runtime directly below it (~:1876+). I did not re-run the diagnosis's probes; where I rely on a probe result (Edit pure-append allowed) I say so.

---

## Q1 — Which slug grammar is canonical?

**(a) Recommendation:** Neither is canonical — DEC-145's body prescribes `<task-or-purpose>-<squad>` in one incidental sentence ("Run directories are slugged `<task-or-purpose>-<squad>`, with no feature infix", DECISIONS.md, DEC-145) while harness-team SKILL §2 prescribes `runs/<YYYY-MM-DD>-<seq>-<squad>/` (harness-team/SKILL.md:45) and a later DECISIONS entry treats date-seq ids (`2026-07-31-01-product`, DECISIONS.md ~:4172) as live — so this plan must make its Mode-A remedy **grammar-independent** (acceptance pinned on run identity, never on slug shape, per rule 6), and carry ONE small doctrine task that unifies the two files, put to the operator at plan signature with a stated default of the harness-team date-seq form.

Why that default: date-seq is the only grammar of the two with a built-in per-cycle discriminator (`<seq>`); the purpose-squad grammar structurally invites the exact collision under diagnosis (two cycles sharing a purpose share a slug, and SKILL.md:272-274 offers no cycle suffix). DEC-145's contrary sentence argues only "no feature infix," which date-seq also satisfies; both grammars end `-<squad>`, so the lead-domain glob keying (SKILL.md:272-273) is unaffected either way. The plan may not resolve doctrine by itself — DEC-145 is a recorded decision — which is exactly why the unification rides to the operator's signature rather than being decided by remedy shape.

**(b) Cost:** two one-line skill edits plus one DECISIONS entry superseding DEC-145's sentence; zero mechanism changes (verified: no script parses slug internals — the identity guard reads `run_id` from file content, and domain globs are `*-<squad>`-suffix keyed). The mixed legacy corpus (~600 gitignored run dirs, both grammars) needs no migration because a grammar-independent remedy never inspects it.

**(c) How this could be wrong:** if some live tooling I did not find *parses* the slug — e.g. sorts runs chronologically by the date prefix, or derives `<seq>` for the next run dir by globbing — then "grammar-independent remedy" underestimates coupling, and canonicalizing date-seq becomes load-bearing rather than cosmetic, requiring the plan to also specify the seq-derivation rule it currently leaves free. [unverified: I searched bin/ for slug parsing and found none, but not exhaustively.]

## Q2 — Machine-generated run_id vs. a second identity signal

**(a) Recommendation:** Second identity signal; `run_id` stays human-legible — and reject the diagnosis's premise that this is unimplementable: `session_id` is present in the PreToolUse payload and already consumed by this very script (check-domain.sh:1850), with a hook-recorded seed-time marker as the runtime-independent fallback if a probe shows compatibility-host session_ids don't discriminate between sibling lead spawns.

Concretely (implementation freedom preserved, this is the acceptance shape): the first accepted write to a run dir's `state.yaml` fixes that directory's identity in a signal the *author does not type* — payload `session_id`, a hook-written write-once marker, or both — and a later write whose run_id matches but whose fixed signal does not is denied as a different run, with the same "write this cycle's state into a run directory of its own" message the guard already emits. The plan must include one probe task: verify whether two lead spawns under one compatibility-host session carry distinct `session_id`s (inflight_registry.py:255 proves child/parent differ under OMP; sibling-vs-sibling under claude runtime is unverified).

Why not machine-generated run_id: it violates rule 6 (a new global property — collision-resistance — bought by changing every surface where run_id is display text) and the repo has already ruled on this shape of trade: DEC-133 made the *id carry the slug* precisely because a bare opaque id "says nothing useful in a directory listing, a log line, or a briefing," and run ids appear in operator-read filenames (`notes/answers-<runid>.md`, DEC-40; `notes/review-<persona>-<runid>-c<cycle>.md`, DECISIONS ~:2119). A UUID-ish run_id pollutes all of those or forces a display-name/identity-id split — two names for one thing, the exact failure DEC-133 closed.

**(b) Cost:** bounded to the enforcement layer plus one skill line: the Issue-#1124 block in check-domain.sh gains one compare; the state.yaml key whitelist (check-domain.sh ALLOWED set, ~:1450) and CHECKPOINT_KEYS in check-state.sh gain at most one key (the two are documented as vocabulary-synced, mechanism-separate, check-domain.sh:1444-1449); harness-team §2's seed sentence gains one field; plus the probe task and fixture tests. Zero downstream display surfaces change because run_id's value is untouched. Legacy priors lacking the new signal: at most a warn-not-deny compatibility branch, since old run dirs are archives that should not be receiving new seeds anyway.

**(c) How this could be wrong:** if the host populates `session_id` identically for every subagent in a session AND the fallback marker is judged unacceptable because it makes a read-only guard into a writer (a genuinely new class of hook behavior with its own failure modes — partial writes, marker/state divergence), then the second-signal option collapses and machine-generated run_id becomes the honest remedy despite its display cost.

## Q3 — Post-hoc detection, and does it subsume prevention?

**(a) Recommendation:** Yes, add detection (a write-once, hook-recorded seed identity per run dir + one new check-state.sh invariant comparing the occupying state.yaml against it) — but detection does NOT subsume prevention: it subsumes it only for the `_no_parser` route, where prevention is already forbidden by the operator's recorded ruling; the identity-equal slug-reuse route must ALSO get Q2's strengthened prevention, because detection is post-loss and the destroyed checkpoint is the harm.

Sufficient closure of Mode A = Q2 prevention (identity-equal route, parser present — the common case) + this detection (every route, including PyYAML fail-open and any future unguarded route). Detection alone is not closure: check-state.sh fires at the next `/harness` entry (command doc :11), by which time the clobber has destroyed the prior checkpoint and a successor context may already have re-entered the loop against forged state (harness-team:85-87 — state.yaml IS the loop position). The cheapest sufficient side-channel: one tiny hook-written, write-once file per run dir recording `{run_id, session_id, sha256(seed), ts}` at first accepted state.yaml write — recorded by the PostToolUse sweep that already fires on Write|Edit|Bash (settings.json registers `check-domain.sh --post`), needing only stdlib json/hashlib so it works in `_no_parser` sessions too (run_id recorded null there; ts/session/hash still land). Git is not available as the side-channel: run dirs are gitignored (DECISIONS ~:5749 records this explicitly). The detection INV: state.yaml's run_id (or seed hash lineage) disagrees with the marker → clobber flag; marker absent for a post-remedy run dir → warn.

**(b) Cost:** one marker file (~100 bytes) per new run dir; one stdlib-only append in the already-running post sweep (no new interpreter — the sweep is already a registered PostToolUse hook); one INV in check-state.sh's existing per-run-dir loop, amortized over the corpus exactly like INV-15/16 (measured pattern already in file: the module-load fix took the sweep from 3.45s to sub-second, check-state.sh:1407-1410). Legacy dirs without markers are ungraded — acceptable, they predate the invariant.

**(c) How this could be wrong:** the diagnosis's own caveat is real — the side-channel is a second artifact that can diverge from the state it witnesses (e.g., a run dir copied/renamed by hand carries a stale marker), so the new INV could produce false clobber findings on legitimately-moved dirs; if the operator's workflow ever moves run dirs, the invariant needs a documented reconcile path or it becomes a recurring red gate that trains people to ignore check-state output.

## Q4 — Wire INV-15 to a hook?

**(a) Recommendation:** No — do not wire check-state.sh (or an extracted INV-15) to SubagentStop; instead fix the fail-open at its source inside the hook that ALREADY runs per spawn: give `validate-digest.py`'s `check_artifact_file` deterministic root resolution (self-path walk, the same cwd-independence fix check-domain.sh documents at :82-85), then fail CLOSED when the resolved digest.md is genuinely absent, and keep INV-15 at its existing `/harness`-entry-and-pre-commit cadence — which, contra the diagnosis's framing, already runs (`.claude/commands/harness.md:11`), just instruction-enforced.

The key observation: "wire INV-15 to a hook" is answering the wrong question. The SubagentStop hook already pays a Python interpreter per harness-agent stop (settings.json registers `validate-digest.py --hook` for matcher `harness-.*`) and already validates the exact file INV-15 would validate — it fails open only when it cannot *find* the file (validate-digest.py:1493-1503). Closing the resolution gap adds a few `os.path` calls to an interpreter already running: marginal cost ≈ zero per spawn, paid by every harness-agent stop (bounded by the recorded caps: 20 concurrent / 200 spawns per session, harness-team:107). By contrast, wiring full check-state.sh per stop is measurably wrong on the repo's own numbers: the sweep grows with run history forever (check-state.sh:1407-1410, 103 digest validations = 3.02s of a 3.45s run before amortization), its git subprocess is justified in-file ONLY by "check-state runs once per session" (check-state.sh:1689-1691), and the operator has already ruled against per-door recurring costs of this shape (harness-init SKILL:291-293; the INV-26 GraphQL burn of 506 points is the recorded cautionary incident, gh_cost_log.py:9-11). Wiring it per-spawn contradicts two recorded premises at once. Secondary, cheap, and in-scope: correct the stale comment at check-domain.sh:1237-1238 — the diagnosis proved the runtime right and the comment wrong, and a comment that misdescribes an enforcement boundary is how the next FEAT-50-shaped regression gets argued into existence.

**(b) Cost:** resolution fix = a few path operations inside an already-running per-spawn interpreter (tens of microseconds against an already-paid ~30ms+ interpreter start); fail-closed on absent digest = zero new spawns, but converts today's silent pass into an exit-2 re-prompt for leads whose artifact truly is missing — which is the intended behavior, since the durable digest IS the deliverable a successor reads (DEC-156 rationale in the same docstring). No change to check-state.sh cadence, so /harness entry cost is unchanged.

**(c) How this could be wrong:** if there is a legitimate lead workflow where the digest genuinely cannot exist at SubagentStop from any root — e.g. a feature worktree removed between the lead's write and its stop event — then fail-closed blocks an innocent lead on an environment race, exactly what the original fail-open comment feared; the mitigation (fail closed only when the run dir resolves but digest.md is absent, fail open when nothing resolves) narrows but does not provably eliminate that race. [unverified: I did not enumerate all worktree-teardown orderings.]

## Q5 — Close both routes, or accept risk on one? (report, not resolve)

**(a) Recommendation:** Close BOTH routes, and note that doing so requires NO new risk acceptance — which matters because the operator's scope note rules risk acceptance out for this batch, so a plan shape that leaves either route open is not deliverable as written.

The shape that closes both without a signature event: route 1 (slug reuse, parser present) is closed by prevention (Q2's second signal) plus detection; route 2 (`_no_parser` fail-open) cannot be closed by prevention — the line-scan fallback was "REMOVED at the user's ruling" under a signed BRIEF (recorded verbatim in check-domain.sh's own comment block above the `_no_parser` return, ~:1456-1465), and that is an EXISTING, already-signed operator ruling, not a new acceptance — but it IS closed by Q3's detection, whose side-channel needs no YAML parser. So the residual on route 2 shrinks from "silent clobber" to "clobber detected at next /harness entry," inside the bounds of a ruling the operator already signed. The plan should also state plainly that with the original evidence destroyed (gitignored run dirs, removed worktree — confirmed by the diagnosis and by DECISIONS' own record that run dirs are not durable), forensic discrimination between the two candidates is permanently unavailable and no task should be spent attempting it; both routes are real independent of which one fired in BUG-1286.

The tension, named: if planning later cuts the detection work (Q3) for budget, route 2 reverts to an open gap, and recording it as ACCEPTED RISK is something neither the validation squad nor the orchestrator may do — only the operator's signature can, and the operator has pre-declared that out of scope for this batch. So detection is not a nice-to-have in this plan; it is the load-bearing element that keeps the plan inside its own scope note. Cutting it means going back to the operator, not shipping around it.

**(b) Cost:** the cost of closing both is exactly the sum already bounded in Q2 (one compare + one key + one skill line + one probe) and Q3 (one marker write in an existing hook + one INV) — no third mechanism; route 2's closure reuses route 1's detection artifact entirely.

**(c) How this could be wrong:** if the `_no_parser` condition also degrades the recording path in a way I did not anticipate (the hook's own Python is what runs the heredoc, so a session with no working python3 at all — as opposed to no PyYAML — runs neither guard nor recorder), then detection quietly fails to cover route 2's outermost variant and "both routes closed, no risk acceptance needed" overstates the closure; the plan's acceptance criteria should pin the marker write to the no-PyYAML case explicitly (a fixture test with PyYAML absent) so this is measured rather than assumed.

---

## Reviewer's own — harness-code-reviewer, NOT the Advisor

Independent re-measurement of the four load-bearing claims, against the worktree at HEAD `c369fb1f`
(not the Advisor's or diagnosis's line numbers — mine, re-read just now).

**V1 — CONFIRMED.** `.claude/commands/harness.md:11` reads verbatim: "Run
`.claude/skills/harness/bin/check-state.sh`. Violations are surfaced to the user before / anything
spawns — except..." — under the file's `## 0. Gate` heading, the first instruction of every `/harness`
entry. The Advisor's Q4 turn on this (downgrading Mode-B from "INV-15 never runs" to "runs on
instruction, not on a hook") is textually correct: this is a mandatory step in the door's own
instructions, not an aside. I did not independently verify that the main-session persona reliably
*executes* every instruction line in its own command file — that reliability is instruction-based by
construction and outside what a line citation can prove — but the text itself unambiguously mandates
the run, which is exactly what V1 asked me to confirm or refute.

**V2 — CONFIRMED, both halves.** `check-domain.sh:1850` reads verbatim `_session = d.get("session_id")`
inside the FEAT-51 orphan-quarantine block (lines 1839–1873 as I read them), consuming `session_id`
straight off the same PreToolUse payload dict used for domain checks. Separately,
`harness_yaml.py:511-533` defines `_resolve_identity(payload)` with the documented fallback chain
`session_id -> transcript_path stem -> CLAUDE_CODE_SESSION_ID -> CLAUDE_CODE_BRIDGE_SESSION_ID`,
called at `harness_yaml.py:572` — but only from `require_or_die()`'s PyYAML-bootstrap-escape marker
path, NOT from the run-identity guard. I traced the Issue #1106/#1124 identity compare itself
(`check-domain.sh:1508-1574`, the `str(prior_run_id) != str(new_run_id)` test lands at `:1567` in my
read) and confirmed it reads only `run_id` from file content — no `session_id`, no
`_resolve_identity` call, anywhere in that function. So: the diagnosis's premise that "no independent
identity signal exists in the payload" is falsified — session_id is present, is already read once in
this file, and a shared resolver with a documented fallback chain already exists — but neither is
currently *wired into* the run-identity check Q2 proposes strengthening. That is consistent with,
not contradicted by, the Advisor's framing: he correctly recommends *adding* the wiring, not
claiming it already exists. **This does lower Q2's cost estimate below the diagnosis's implicit
"unimplementable" framing** — a shared resolver already exists and needs a caller added, not a new
concept built from nothing.

**V3 — CONFIRMED.** `inflight_registry.py:257-258` reads verbatim: `if session is not None and
claim.get("runtime") != "omp": return claim.get("session") in (None, session)`, immediately preceded
by the comment (lines 255-256) "OMP child and parent sessions differ. Process ownership + feature
identity is its liveness boundary; the compatibility host retains FEAT-42's session filter." This
confirms the registry both stores (`claim.get("session")`) and compares a claim's session, and
confirms the comment recording that OMP child/parent sessions differ — but note the code's own
carve-out: the session filter applies only when `claim.get("runtime") != "omp"`, i.e. it is
explicitly bypassed for OMP-runtime claims. This bears directly on Q2's probe task: under OMP, this
registry does NOT discriminate siblings by session today (the filter is skipped for that runtime),
so the Advisor's proposed probe ("do sibling lead spawns carry distinct session_ids") needs to
additionally state which runtime it is testing under — the answer plausibly differs between the
compatibility host and OMP, and the current code already treats them differently by design.

**V4 — CONFIRMED, DEC-145 is the only entry that rules on this.** `DECISIONS.md:3242-3243` (inside
`## DEC-145 — Expertise v2...`) reads verbatim: "Run directories are slugged
`<task-or-purpose>-<squad>`, with no feature infix." — an exact match to the Advisor's quote. I
grepped every DECISIONS heading plus every line mentioning `slug`/`run_id`/`run dir` across the whole
file and found no other entry that *rules* on run-dir slug grammar: DEC-133 rules on the *feature*
id's slug (`FEAT-NN-<kebab-slug>`), DEC-139 on the *bug* id's slug (`BUG-NN-<kebab-slug>`), DEC-144
on the *branch*-name grammar — none governs `runs/*` directory names. `DECISIONS.md:4172` (inside
DEC-171) does contain the Advisor's cited `2026-07-31-01-product` string, but only as an incidental
YAML-parsing-hazard example ("Run ids like `2026-07-31-01-product` carry trailing text and stay
strings…") — it is evidence that the date-seq form was in live use after DEC-145 landed, not itself
a decision that rules on the grammar. The Advisor's own wording ("a later DECISIONS entry *treats*
date-seq ids... as live") is accurate to this — he does not claim DEC-171 is a ruling, only that it
uses the form. `harness-team/SKILL.md:45` independently confirms the competing prescription:
`<HARNESS_FEATURE_TREE_ROOT>/.harness/harness/features/<feat>/runs/<YYYY-MM-DD>-<seq>-<squad>/`,
verbatim. Q1's "neither grammar is canonical" holds on my own read.

**Nothing else material left unaddressed.** The Advisor flagged his own unverified items honestly
([unverified] tags in Q1c, Q4c) and I did not attempt to close those — they are genuinely
research/probe-shaped, not verifiable from a static read, and the plan should carry them as tasks
rather than treat them as settled.

## Open for the operator

- Q1's doctrine unification (DEC-145 vs. harness-team SKILL.md run-dir grammar) needs the operator's
  signature per the Advisor's own framing — not decidable by plan shape alone.
- Whether the compatibility-host runtime (non-OMP) actually assigns distinct `session_id`s to sibling
  lead spawns is unverified by static read (V3 above); Q2's probe task must specify it is testing
  the non-OMP path, since OMP-runtime claims already bypass the session filter by design.
- Whether any `run_id` seeding call site in the live team-orchestration code path derives `run_id`
  from the directory slug (diagnosis's Q2, non-blocking) — neither the Advisor nor I found the exact
  seeding call site; still open.
