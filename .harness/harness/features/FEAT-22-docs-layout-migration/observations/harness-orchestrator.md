# Observations — harness-orchestrator — FEAT-22

- 2026-08-15: **Resuming after an API cutoff spawns a DOUBLE unless you SendMessage.** Three
  instances this session. (1) A product-lead was cut off mid-run; I dispatched a fresh
  product-lead, and the original later completed with a stale FAIL naming a must_fix that the
  successor had already closed. (2) Two validator leads independently resolved
  `runs/2026-08-15-5-validator/` and one silently overwrote the other's in-flight `state.yaml`,
  deleting three dispatch checkpoints. (3) **My own error, same shape:** wanting to hand a
  measurement to an in-flight eng-lead, I used the Agent tool instead of SendMessage and spawned a
  second eng-lead on the same revision. The tool description says plainly that SendMessage
  continues an agent with its context intact while a new Agent call starts fresh; I read that and
  still reached for the wrong one under time pressure. The disk is what disambiguates: compare
  `state.yaml` mtimes and step lists, take the more complete sequence, and treat the earlier
  return as a pre-completion snapshot.

- 2026-08-15: **Verify the ORDER a relayed instruction implies, not just its content.** An operator
  ruling reached me as "correct T-01/T-05's expected-FAIL prose — two reds, not one." I passed it
  down verbatim. pm refused it and was right: the panel's "two reds" described the UNREMEDIED plan,
  and the remedy's own first half (T-04 adding the ninth fixture entry, which precedes T-05)
  removes the second red. Obeying me would have manufactured a mid-cluster halt on a red that no
  longer exists. The failure was conflating a DIAGNOSIS with a REMEDY as the finding travelled
  panel → operator → me → pm. When a fix and a count-assertion are in the same fold, ask which
  task lands first before restating the count.

- 2026-08-15: **A member refusing an instruction with a trace is the system working, not a defect.**
  pm declined two of my dispatch clauses — the count above, and a `.harness/notes/*` glob it
  narrowed to an exact path because that directory holds 29 files, 28 unrelated. Both refusals were
  improvements on what I dispatched. Cheap check before overruling: verify the member's trace at
  source. Both survived.

- 2026-08-15: **A gate value can be right while its stated derivation is unreproducible.** The
  29-file cluster floor is correct, but the reported terms `1+3+6+5+6+1+2+5` do not map to the
  per-task counts, and the sum-of-entries route only reaches 29 because two errors cancel: it
  triple-counts a note listed in three tasks, and counts a feature-dir file the same task's verify
  forbids from the commit. The reconstruction that works is 27 distinct − 1 forbidden + 3 moved
  docs no `files:` list names. Check a floor's DERIVATION, not just its value — a number nobody can
  re-derive drifts silently the next time a file is added.

- 2026-08-15: **Prove a new assertion reds the CURRENT tree before trusting it.** ui-reviewer set
  the pattern (`grep -cF` at the pin returning 0), and I reused it on both new pins: T-04's fixture
  string and T-02's mirrored grant both return 0 matches at `0f12f14`. An assertion that already
  passes on the unmodified tree gates nothing, and this costs one command.

- 2026-08-15: **Ending a turn with subagents in flight trips `validate-digest.py --hook`.** There is
  no idle-wait; the only way to hold is to keep making tool calls. Reported by product-lead earlier
  in this same feature and then hit by me directly. Useful filler is real work: verifying the
  folds I had only relayed, which is how I found the floor-derivation gap above.

- 2026-08-16: **I asserted a `change_type` distribution across 11 tasks from the 2 I had read, and
  the lead caught it.** My qa dispatch said "every one of the 11 tasks is `change_type: docs`, so
  `test_matrix.docs.always` is `[]` and the floor is empty", and I built the entire gate framing on
  that vacuous-PASS risk. Measured afterwards: 7 docs, **3 logic** (T-03/T-04/T-05), 1 config — and
  `logic.always` is `["unit"]`, so the floor was mandatory all along and the hole was never open. I
  had read T-10 and T-11 closely for their build cards and generalised from them. The tell I missed
  is that a per-task field is a DISTRIBUTION, never a constant, and one `yaml.safe_load` prints the
  whole of it. Outcome was unaffected — qa ran unit and integration regardless — but a dispatch
  whose central premise is false spends the lead's attention correcting me. Same class as the floor
  derivation above: I checked the values I was handed and not the ones I supplied.

- 2026-08-16: **The scratchpad is shared across sessions and its stale files impersonate current
  ones.** Extracting T-10's verify I wrote `verify-t-10.sh`, then catted `verify-t10.sh` — a file
  from FEAT-21's build, four days old, testing an entirely different task. It printed plausible,
  wrong content and I nearly reasoned from it. Compounding it, the filesystem is case-insensitive,
  so `verify-T-10.sh` and `verify-t-10.sh` are one file and my write clobbered a predecessor's.
  Extracting a verify by `yaml.safe_load` from the plan (never retyping it) and naming the output
  with a feature-scoped prefix fixed both. A file that exists is not a file that is yours.

- 2026-08-16: **A plan clause can be unsatisfiable-as-written without being wrong.** T-11 asks the
  note's last line to state the SHA of the commit that lands the note — which no commit can contain
  about itself. The resolution was in the plan's own word order: "commit, THEN state it" makes it a
  post-commit act, so it became a one-line follow-up commit rather than an amend. Also T-11's
  `POST-MOVE HEAD` parenthetical called HEAD "the cluster commit from T-09" when a logs commit had
  landed on top; recording the literal `git rev-parse HEAD` and naming the cluster commit on a
  separate line kept the capture true. Read a stale parenthetical as narration, not as the spec —
  the mechanical instruction beside it is the spec.

- 2026-08-17: **A killed subagent's WORK can be complete while its RECORD is not, and re-dispatch is
  the dangerous default.** A spend limit killed two of three distillation leads; one left a
  verdict-less digest, one left none. The kill notices claimed the deliverable was durable, which is
  exactly the sort of claim not to take on trust. Three checks settled it in one command each: entry
  counts per file against `git show HEAD:<path>` (a WIPE is the failure distillation is most exposed
  to and the format checker cannot see it — all ten files had GAINED entries, +25), duplicate entry
  IDs (zero, so nothing was double-applied), and `check-expertise.sh` (exit 0). Then the judgment:
  **do not re-dispatch when the members have already self-applied.** Re-running risks double-applying
  into files injected into every future spawn — a permanent tax — where the alternative is one gap in
  the run archive. Record the killed runs with an honest token rather than a flattering one, and say
  in the briefing that the token is coined, since nothing in the harness defines run verdicts.

- 2026-08-17: **Two crash resumes in one feature, and both times the waking relay carried stale
  state** — once describing three already-completed gates as still owed, once the cycle count. Had I
  acted on either I would have burned three runs re-running passed gates and reported a budget I had
  already spent. `feature.json` and the run dirs settled both in one command. The rule that saved it
  is the cheap one: re-derive from disk before believing any summary of your own prior work,
  including your own transcript.
